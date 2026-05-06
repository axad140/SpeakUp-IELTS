"""
Professional real-time computer-vision analysis for interview performance.

Focus areas:
- face presence and framing
- eye contact / gaze proxy
- head pose and posture
- movement stability and fidgeting
- lighting / sharpness
- presentation and dress-formality cues

The module intentionally uses local CV signals only. It does not touch the NLP
pipeline.
"""
import base64
import math
import time
from collections import Counter, deque
from typing import Dict, Optional, Tuple

import cv2
import numpy as np

try:
    import mediapipe as mp
    from mediapipe.python.solutions import face_mesh, pose
    MEDIAPIPE_AVAILABLE = True
except (ImportError, AttributeError):
    MEDIAPIPE_AVAILABLE = False
    print("[WARNING] MediaPipe not properly installed. Install: pip install --upgrade mediapipe")


def _clip(value, low=0, high=100):
    return max(low, min(high, value))


def _quality(score):
    if score >= 85:
        return "excellent"
    if score >= 72:
        return "strong"
    if score >= 58:
        return "acceptable"
    if score >= 42:
        return "needs_attention"
    return "poor"


def _distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


class BodyLanguageAnalyzer:
    def __init__(self):
        print("[SETUP] Initializing advanced CV interview analyzer...")
        self.pose = None
        self.face_mesh = None
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        if MEDIAPIPE_AVAILABLE:
            try:
                self.pose = pose.Pose(
                    static_image_mode=False,
                    model_complexity=1,
                    smooth_landmarks=True,
                    min_detection_confidence=0.55,
                    min_tracking_confidence=0.55,
                )
                self.face_mesh = face_mesh.FaceMesh(
                    static_image_mode=False,
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.55,
                    min_tracking_confidence=0.55,
                )
            except Exception as exc:
                print(f"[WARNING] MediaPipe initialization error: {exc}")

        self.history = deque(maxlen=45)
        self.metrics = {
            "posture_scores": [],
            "head_position_scores": [],
            "engagement_scores": [],
            "confidence_scores": [],
            "framing_scores": [],
            "lighting_scores": [],
            "movement_scores": [],
            "presentation_scores": [],
            "eye_contact": [],
            "emotions": [],
            "guidance": [],
        }

    def decode_base64_frame(self, b64_string: str) -> Optional[np.ndarray]:
        if not b64_string:
            return None
        if "," in b64_string:
            b64_string = b64_string.split(",", 1)[1]
        img_data = base64.b64decode(b64_string)
        nparr = np.frombuffer(img_data, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    def analyze_frame(self, frame_b64: str, emotion: str = "neutral", eye_contact: bool = False) -> Dict:
        try:
            img = self.decode_base64_frame(frame_b64)
            if img is None:
                return self._default_response("No camera frame was received.")

            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            pose_landmarks = self._get_pose_landmarks(img_rgb)
            face_landmarks = self._get_face_landmarks(img_rgb)
            face_box = self._face_box(face_landmarks, img.shape) if face_landmarks else None
            if face_box is None:
                face_box = self._haar_face_box(img)

            frame_quality = self.analyze_frame_quality(img, face_box)
            posture = self.analyze_posture(pose_landmarks, face_box, img.shape)
            head_position = self.analyze_head_position(face_landmarks, face_box, img.shape)
            gaze = self.analyze_eye_contact(face_landmarks, face_box, img.shape, eye_contact)
            engagement = self.analyze_engagement(face_landmarks, emotion, gaze)
            movement = self.analyze_movement(face_box, head_position, posture)
            presentation = self.analyze_presentation(img, face_box, pose_landmarks)
            confidence = self.analyze_confidence(posture, head_position, gaze, engagement, movement, presentation, frame_quality, emotion)

            guidance = self._generate_guidance(
                frame_quality, posture, head_position, gaze, engagement, movement, presentation, confidence
            )

            overall_score = round(
                confidence["confidence_score"] * 0.30
                + posture["posture_score"] * 0.15
                + head_position["head_score"] * 0.15
                + gaze["eye_contact_score"] * 0.15
                + movement["stability_score"] * 0.10
                + frame_quality["framing_score"] * 0.08
                + presentation["presentation_score"] * 0.07
            )

            result = {
                "success": True,
                "emotion": emotion,
                "eye_contact": gaze["eye_contact"],
                "face_detected": face_box is not None,
                "posture": posture,
                "head_position": head_position,
                "engagement": engagement,
                "gaze": gaze,
                "movement": movement,
                "frame_quality": frame_quality,
                "presentation": presentation,
                "confidence": confidence,
                "guidance": guidance,
                "overall_score": overall_score,
                "interviewer_signals": self._interviewer_signals(
                    frame_quality, posture, head_position, gaze, engagement, movement, presentation
                ),
            }

            self._record_metrics(result)
            return result
        except Exception as exc:
            print(f"[Frame Analysis Error] {exc}")
            return self._default_response("Position yourself clearly in front of the camera.")

    def _get_pose_landmarks(self, img_rgb):
        if not self.pose:
            return None
        try:
            results = self.pose.process(img_rgb)
            return results.pose_landmarks.landmark if results.pose_landmarks else None
        except Exception as exc:
            print(f"[Pose Detection Error] {exc}")
            return None

    def _get_face_landmarks(self, img_rgb):
        if not self.face_mesh:
            return None
        try:
            results = self.face_mesh.process(img_rgb)
            if results.multi_face_landmarks:
                return results.multi_face_landmarks[0].landmark
        except Exception as exc:
            print(f"[Face Mesh Error] {exc}")
        return None

    def _haar_face_box(self, img) -> Optional[Tuple[int, int, int, int]]:
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.2, 5, minSize=(70, 70))
            if len(faces) == 0:
                return None
            x, y, w, h = max(faces, key=lambda box: box[2] * box[3])
            return int(x), int(y), int(x + w), int(y + h)
        except Exception:
            return None

    def _face_box(self, face_landmarks, shape) -> Optional[Tuple[int, int, int, int]]:
        if not face_landmarks:
            return None
        h, w = shape[:2]
        xs = [lm.x for lm in face_landmarks]
        ys = [lm.y for lm in face_landmarks]
        x1 = int(_clip(min(xs) * w, 0, w - 1))
        y1 = int(_clip(min(ys) * h, 0, h - 1))
        x2 = int(_clip(max(xs) * w, 0, w - 1))
        y2 = int(_clip(max(ys) * h, 0, h - 1))
        if x2 <= x1 or y2 <= y1:
            return None
        return x1, y1, x2, y2

    def analyze_frame_quality(self, img, face_box) -> Dict:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        brightness = float(np.mean(gray))
        contrast = float(np.std(gray))
        sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        brightness_score = _clip(100 - abs(brightness - 135) * 0.9)
        contrast_score = _clip(contrast * 2.4)
        sharpness_score = _clip(sharpness / 3.2)
        lighting_score = round(brightness_score * 0.45 + contrast_score * 0.25 + sharpness_score * 0.30)

        if face_box:
            h, w = img.shape[:2]
            x1, y1, x2, y2 = face_box
            face_cx = (x1 + x2) / 2 / w
            face_cy = (y1 + y2) / 2 / h
            face_area = ((x2 - x1) * (y2 - y1)) / max(1, w * h)
            center_score = _clip(100 - (abs(face_cx - 0.5) + abs(face_cy - 0.38)) * 170)
            size_score = _clip(100 - abs(face_area - 0.16) * 260)
            framing_score = round(center_score * 0.65 + size_score * 0.35)
        else:
            face_cx = face_cy = face_area = 0
            framing_score = 25

        return {
            "lighting_score": lighting_score,
            "framing_score": framing_score,
            "brightness": round(brightness, 1),
            "contrast": round(contrast, 1),
            "sharpness": round(sharpness, 1),
            "face_center": {"x": round(face_cx, 3), "y": round(face_cy, 3)},
            "face_area_ratio": round(face_area, 3),
            "quality": _quality(round((lighting_score + framing_score) / 2)),
        }

    def analyze_posture(self, landmarks, face_box=None, shape=None) -> Dict:
        if landmarks is None:
            if face_box and shape is not None:
                h, w = shape[:2]
                x1, y1, x2, y2 = face_box
                face_cx = (x1 + x2) / 2 / w
                face_area = ((x2 - x1) * (y2 - y1)) / max(1, w * h)
                centered_score = _clip(100 - abs(face_cx - 0.5) * 180)
                distance_score = _clip(100 - abs(face_area - 0.15) * 260)
                shoulder_visibility_proxy = _clip(100 - max(0, y2 - h * 0.42) * 0.20)
                score = round(centered_score * 0.45 + distance_score * 0.35 + shoulder_visibility_proxy * 0.20)
                return {
                    "posture_score": score,
                    "posture_quality": _quality(score),
                    "shoulder_alignment": round(centered_score),
                    "spine_alignment": round(distance_score),
                    "visibility": "estimated_from_face_and_framing",
                }
            return {
                "posture_score": 55,
                "posture_quality": "not_visible",
                "shoulder_alignment": 0,
                "spine_alignment": 0,
                "visibility": "upper_body_not_detected",
            }
        try:
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            left_hip = landmarks[23]
            right_hip = landmarks[24]
            nose = landmarks[0]

            shoulder_visibility = min(left_shoulder.visibility, right_shoulder.visibility)
            hip_visibility = min(left_hip.visibility, right_hip.visibility)
            shoulder_diff = abs(left_shoulder.y - right_shoulder.y)
            shoulder_width = abs(left_shoulder.x - right_shoulder.x)
            shoulder_score = _clip(100 - shoulder_diff * 260)

            hip_mid_x = (left_hip.x + right_hip.x) / 2
            shoulder_mid_x = (left_shoulder.x + right_shoulder.x) / 2
            torso_lean = abs(shoulder_mid_x - hip_mid_x)
            spine_score = _clip(100 - torso_lean * 260)

            body_center = (shoulder_mid_x + nose.x) / 2
            centered_score = _clip(100 - abs(body_center - 0.5) * 180)
            visibility_score = _clip((shoulder_visibility + hip_visibility) * 50)
            posture_score = round(
                shoulder_score * 0.35 + spine_score * 0.30 + centered_score * 0.20 + visibility_score * 0.15
            )

            if shoulder_width < 0.12:
                posture_quality = "too_far_or_shoulders_not_visible"
            else:
                posture_quality = _quality(posture_score)

            return {
                "posture_score": posture_score,
                "posture_quality": posture_quality,
                "shoulder_alignment": round(shoulder_score),
                "spine_alignment": round(spine_score),
                "centered_score": round(centered_score),
                "visibility": round(visibility_score),
                "torso_lean": round(torso_lean, 3),
            }
        except Exception as exc:
            print(f"[Posture Analysis Error] {exc}")
            return {"posture_score": 55, "posture_quality": "not_visible"}

    def analyze_head_position(self, face_landmarks, face_box, shape) -> Dict:
        if face_landmarks is None:
            if face_box is not None:
                h, w = shape[:2]
                x1, y1, x2, y2 = face_box
                cx = (x1 + x2) / 2 / w
                cy = (y1 + y2) / 2 / h
                face_ratio = (x2 - x1) / max(1, y2 - y1)
                center_score = _clip(100 - (abs(cx - 0.5) + abs(cy - 0.38)) * 165)
                ratio_score = _clip(100 - abs(face_ratio - 0.78) * 120)
                score = round(center_score * 0.70 + ratio_score * 0.30)
                if cx > 0.62:
                    position = "off_center_right"
                elif cx < 0.38:
                    position = "off_center_left"
                elif cy > 0.55:
                    position = "too_low_in_frame"
                elif cy < 0.22:
                    position = "too_high_in_frame"
                else:
                    position = "neutral_estimated"
                return {
                    "head_position": position,
                    "head_score": score,
                    "yaw": round(cx - 0.5, 3),
                    "tilt": 0,
                    "pitch": round(cy - 0.38, 3),
                    "head_guidance": self._get_head_guidance(position),
                }
            return {
                "head_position": "face_not_detected",
                "head_score": 35,
                "yaw": 0,
                "tilt": 0,
                "pitch": 0,
                "head_guidance": "Keep your face visible and centered in the camera.",
            }
        try:
            left_eye = face_landmarks[33]
            right_eye = face_landmarks[263]
            nose = face_landmarks[1]
            chin = face_landmarks[152]
            mouth = face_landmarks[13]

            eye_mid_x = (left_eye.x + right_eye.x) / 2
            eye_mid_y = (left_eye.y + right_eye.y) / 2
            eye_width = max(0.001, abs(right_eye.x - left_eye.x))
            yaw = (nose.x - eye_mid_x) / eye_width
            tilt = (right_eye.y - left_eye.y) / eye_width
            pitch = ((mouth.y - eye_mid_y) / max(0.001, chin.y - eye_mid_y)) - 0.42

            yaw_score = _clip(100 - abs(yaw) * 135)
            tilt_score = _clip(100 - abs(tilt) * 170)
            pitch_score = _clip(100 - abs(pitch) * 180)
            head_score = round(yaw_score * 0.45 + tilt_score * 0.35 + pitch_score * 0.20)

            if abs(yaw) > 0.27:
                position = "turned_right" if yaw > 0 else "turned_left"
            elif abs(tilt) > 0.18:
                position = "tilted_right" if tilt > 0 else "tilted_left"
            elif pitch > 0.18:
                position = "looking_down"
            elif pitch < -0.18:
                position = "chin_too_high"
            else:
                position = "neutral"

            return {
                "head_position": position,
                "head_score": head_score,
                "yaw": round(yaw, 3),
                "tilt": round(tilt, 3),
                "pitch": round(pitch, 3),
                "head_guidance": self._get_head_guidance(position),
            }
        except Exception as exc:
            print(f"[Head Position Error] {exc}")
            return {"head_position": "neutral", "head_score": 60, "head_guidance": "Keep your face level."}

    def analyze_eye_contact(self, face_landmarks, face_box, shape, fallback_eye_contact: bool) -> Dict:
        if face_landmarks is None:
            return {
                "eye_contact": bool(fallback_eye_contact),
                "eye_contact_score": 40 if not fallback_eye_contact else 65,
                "gaze_direction": "unknown",
                "eye_openness": 0,
            }
        try:
            left_eye_outer, left_eye_inner = face_landmarks[33], face_landmarks[133]
            right_eye_inner, right_eye_outer = face_landmarks[362], face_landmarks[263]
            left_eye_top, left_eye_bottom = face_landmarks[159], face_landmarks[145]
            right_eye_top, right_eye_bottom = face_landmarks[386], face_landmarks[374]
            nose = face_landmarks[1]

            eye_center_x = (left_eye_outer.x + right_eye_outer.x) / 2
            eye_width = max(0.001, right_eye_outer.x - left_eye_outer.x)
            gaze_offset = (nose.x - eye_center_x) / eye_width
            left_open = _distance(left_eye_top, left_eye_bottom) / max(0.001, _distance(left_eye_outer, left_eye_inner))
            right_open = _distance(right_eye_top, right_eye_bottom) / max(0.001, _distance(right_eye_inner, right_eye_outer))
            eye_openness = _clip((left_open + right_open) * 220)

            gaze_center_score = _clip(100 - abs(gaze_offset) * 170)
            openness_score = _clip(eye_openness)
            eye_contact_score = round(gaze_center_score * 0.70 + openness_score * 0.30)
            eye_contact = eye_contact_score >= 58 or bool(fallback_eye_contact)

            if gaze_offset > 0.22:
                direction = "looking_right"
            elif gaze_offset < -0.22:
                direction = "looking_left"
            elif eye_openness < 35:
                direction = "eyes_partly_closed"
            else:
                direction = "towards_camera"

            return {
                "eye_contact": eye_contact,
                "eye_contact_score": eye_contact_score,
                "gaze_direction": direction,
                "gaze_offset": round(gaze_offset, 3),
                "eye_openness": round(eye_openness),
            }
        except Exception as exc:
            print(f"[Eye Contact Error] {exc}")
            return {"eye_contact": bool(fallback_eye_contact), "eye_contact_score": 60, "gaze_direction": "estimated"}

    def analyze_engagement(self, face_landmarks, emotion: str, gaze: Dict) -> Dict:
        emotion_score = {
            "happy": 88,
            "calm": 82,
            "neutral": 74,
            "surprised": 62,
            "sad": 45,
            "angry": 38,
            "fear": 35,
            "disgust": 35,
        }.get((emotion or "neutral").lower(), 68)

        if face_landmarks is None:
            score = round(emotion_score * 0.45 + gaze.get("eye_contact_score", 50) * 0.55)
            return {"engagement_score": score, "engagement_level": _quality(score), "emotion_state": emotion}

        try:
            mouth_left, mouth_right = face_landmarks[61], face_landmarks[291]
            mouth_top, mouth_bottom = face_landmarks[13], face_landmarks[14]
            mouth_width = _distance(mouth_left, mouth_right)
            mouth_open = _distance(mouth_top, mouth_bottom) / max(0.001, mouth_width)
            speaking_expression = _clip(mouth_open * 260)
            score = round(
                gaze.get("eye_contact_score", 60) * 0.45
                + emotion_score * 0.35
                + speaking_expression * 0.20
            )
            return {
                "engagement_score": score,
                "engagement_level": _quality(score),
                "eye_opening": gaze.get("eye_openness", 0),
                "mouth_activity": round(speaking_expression),
                "emotion_state": emotion,
            }
        except Exception as exc:
            print(f"[Engagement Analysis Error] {exc}")
            score = round(emotion_score * 0.5 + gaze.get("eye_contact_score", 60) * 0.5)
            return {"engagement_score": score, "engagement_level": _quality(score), "emotion_state": emotion}

    def analyze_movement(self, face_box, head_position: Dict, posture: Dict) -> Dict:
        now = time.time()
        center = None
        if face_box:
            x1, y1, x2, y2 = face_box
            center = ((x1 + x2) / 2, (y1 + y2) / 2)

        previous = self.history[-1] if self.history else None
        frame_movement = 0
        if previous and center and previous.get("center"):
            px, py = previous["center"]
            frame_movement = math.hypot(center[0] - px, center[1] - py)

        self.history.append({
            "time": now,
            "center": center,
            "yaw": head_position.get("yaw", 0),
            "tilt": head_position.get("tilt", 0),
            "posture": posture.get("posture_score", 55),
        })

        recent = list(self.history)[-12:]
        centers = [item["center"] for item in recent if item.get("center")]
        if len(centers) >= 3:
            xs = [c[0] for c in centers]
            ys = [c[1] for c in centers]
            movement_variance = float(np.std(xs) + np.std(ys))
        else:
            movement_variance = frame_movement

        head_changes = [abs(recent[i]["yaw"] - recent[i - 1]["yaw"]) + abs(recent[i]["tilt"] - recent[i - 1]["tilt"]) for i in range(1, len(recent))]
        head_motion = float(np.mean(head_changes)) if head_changes else 0
        fidget_index = movement_variance * 0.18 + head_motion * 95
        stability_score = round(_clip(100 - fidget_index))

        if stability_score >= 78:
            movement_level = "steady"
        elif stability_score >= 58:
            movement_level = "natural"
        elif stability_score >= 40:
            movement_level = "restless"
        else:
            movement_level = "distracting"

        return {
            "stability_score": stability_score,
            "movement_level": movement_level,
            "frame_movement": round(frame_movement, 1),
            "movement_variance": round(movement_variance, 1),
            "head_motion": round(head_motion, 3),
            "fidget_index": round(fidget_index, 1),
        }

    def analyze_presentation(self, img, face_box, pose_landmarks) -> Dict:
        h, w = img.shape[:2]
        if face_box:
            x1, y1, x2, y2 = face_box
            torso_top = min(h - 1, y2 + int((y2 - y1) * 0.15))
            torso_bottom = min(h, torso_top + int((y2 - y1) * 1.6))
            torso_left = max(0, x1 - int((x2 - x1) * 0.9))
            torso_right = min(w, x2 + int((x2 - x1) * 0.9))
        else:
            torso_top, torso_bottom = int(h * 0.42), int(h * 0.88)
            torso_left, torso_right = int(w * 0.25), int(w * 0.75)

        torso = img[torso_top:torso_bottom, torso_left:torso_right]
        if torso.size == 0:
            return {
                "presentation_score": 50,
                "dress_assessment": "not_visible",
                "dress_confidence": 0,
                "professional_palette": "unknown",
            }

        hsv = cv2.cvtColor(torso, cv2.COLOR_BGR2HSV)
        saturation = float(np.mean(hsv[:, :, 1]))
        value = float(np.mean(hsv[:, :, 2]))
        edges = cv2.Canny(cv2.cvtColor(torso, cv2.COLOR_BGR2GRAY), 80, 160)
        texture = float(np.mean(edges > 0))

        neutral_mask = (hsv[:, :, 1] < 80) & (hsv[:, :, 2] > 35)
        dark_mask = hsv[:, :, 2] < 95
        formal_ratio = float(np.mean(neutral_mask | dark_mask))
        overly_bright_ratio = float(np.mean((hsv[:, :, 1] > 145) & (hsv[:, :, 2] > 170)))

        presentation_score = round(_clip(48 + formal_ratio * 42 + min(texture, 0.14) * 80 - overly_bright_ratio * 20))
        if presentation_score >= 78:
            assessment = "professional"
        elif presentation_score >= 62:
            assessment = "presentable"
        elif presentation_score >= 48:
            assessment = "casual"
        else:
            assessment = "distracting_or_unclear"

        return {
            "presentation_score": presentation_score,
            "dress_assessment": assessment,
            "dress_confidence": round(_clip(formal_ratio * 100)),
            "professional_palette": "neutral_or_formal" if formal_ratio >= 0.45 else "bright_or_patterned",
            "torso_visibility": round((torso.shape[0] * torso.shape[1]) / max(1, h * w), 3),
            "saturation": round(saturation, 1),
            "brightness": round(value, 1),
            "texture_density": round(texture, 3),
            "note": "Dress sense is estimated from visible color/contrast cues, not identity or personal attributes.",
        }

    def analyze_confidence(self, posture, head_position, gaze, engagement, movement, presentation, frame_quality, emotion) -> Dict:
        emotion_adjustment = {
            "happy": 5,
            "calm": 4,
            "neutral": 0,
            "surprised": -2,
            "sad": -7,
            "angry": -10,
            "fear": -12,
            "disgust": -10,
        }.get((emotion or "neutral").lower(), 0)
        score = round(_clip(
            posture["posture_score"] * 0.18
            + head_position["head_score"] * 0.18
            + gaze["eye_contact_score"] * 0.22
            + engagement["engagement_score"] * 0.16
            + movement["stability_score"] * 0.12
            + presentation["presentation_score"] * 0.07
            + frame_quality["framing_score"] * 0.07
            + emotion_adjustment
        ))
        return {
            "confidence_score": score,
            "confidence_level": _quality(score),
            "components": {
                "posture": posture["posture_score"],
                "head_position": head_position["head_score"],
                "eye_contact": gaze["eye_contact_score"],
                "engagement": engagement["engagement_score"],
                "movement_stability": movement["stability_score"],
                "presentation": presentation["presentation_score"],
                "framing": frame_quality["framing_score"],
                "emotion": emotion,
            },
        }

    def _record_metrics(self, result: Dict) -> None:
        self.metrics["posture_scores"].append(result["posture"].get("posture_score", 55))
        self.metrics["head_position_scores"].append(result["head_position"].get("head_score", 55))
        self.metrics["engagement_scores"].append(result["engagement"].get("engagement_score", 55))
        self.metrics["confidence_scores"].append(result["confidence"].get("confidence_score", 55))
        self.metrics["framing_scores"].append(result["frame_quality"].get("framing_score", 55))
        self.metrics["lighting_scores"].append(result["frame_quality"].get("lighting_score", 55))
        self.metrics["movement_scores"].append(result["movement"].get("stability_score", 55))
        self.metrics["presentation_scores"].append(result["presentation"].get("presentation_score", 55))
        self.metrics["eye_contact"].append(bool(result["gaze"].get("eye_contact", False)))
        self.metrics["emotions"].append(result.get("emotion", "neutral"))
        self.metrics["guidance"].append(result.get("guidance", ""))

    def _interviewer_signals(self, frame_quality, posture, head_position, gaze, engagement, movement, presentation):
        return [
            {"label": "Camera framing", "score": frame_quality["framing_score"], "level": frame_quality["quality"]},
            {"label": "Eye contact", "score": gaze["eye_contact_score"], "level": gaze["gaze_direction"]},
            {"label": "Posture", "score": posture["posture_score"], "level": posture["posture_quality"]},
            {"label": "Head position", "score": head_position["head_score"], "level": head_position["head_position"]},
            {"label": "Movement control", "score": movement["stability_score"], "level": movement["movement_level"]},
            {"label": "Presentation", "score": presentation["presentation_score"], "level": presentation["dress_assessment"]},
            {"label": "Engagement", "score": engagement["engagement_score"], "level": engagement["engagement_level"]},
        ]

    def _generate_guidance(self, frame_quality, posture, head_pos, gaze, engagement, movement, presentation, confidence) -> str:
        tips = []
        if frame_quality["framing_score"] < 58:
            tips.append("Center your face and keep your head and shoulders visible.")
        if frame_quality["lighting_score"] < 55:
            tips.append("Improve lighting so your face is clear.")
        if posture["posture_score"] < 62:
            tips.append("Sit upright with balanced shoulders.")
        if head_pos["head_score"] < 62:
            tips.append(head_pos.get("head_guidance", "Keep your head level and face the camera."))
        if gaze["eye_contact_score"] < 58:
            tips.append("Look closer to the camera to show interviewer-level eye contact.")
        if movement["stability_score"] < 55:
            tips.append("Reduce side-to-side movement and keep gestures controlled.")
        if presentation["presentation_score"] < 55:
            tips.append("Keep clothing/background simple and professional on camera.")
        if engagement["engagement_score"] < 55:
            tips.append("Use a more attentive facial expression while speaking.")

        if not tips:
            return "Professional presence detected: posture, eye contact, framing, and movement look strong."
        return " | ".join(tips[:2])

    def _get_head_guidance(self, position: str) -> str:
        guidance_map = {
            "turned_right": "Face the camera directly; avoid turning to the right.",
            "turned_left": "Face the camera directly; avoid turning to the left.",
            "tilted_right": "Keep your head level; avoid tilting right.",
            "tilted_left": "Keep your head level; avoid tilting left.",
            "looking_down": "Raise your gaze; avoid looking down while answering.",
            "chin_too_high": "Lower your chin slightly for a natural interview posture.",
            "neutral": "Head position is balanced.",
            "neutral_estimated": "Head position appears balanced.",
            "off_center_right": "Move slightly left so your face is centered.",
            "off_center_left": "Move slightly right so your face is centered.",
            "too_low_in_frame": "Raise the camera or sit higher so your face is centered.",
            "too_high_in_frame": "Lower the camera slightly so your shoulders remain visible.",
        }
        return guidance_map.get(position, "Keep your face level and centered.")

    def _default_response(self, guidance: str) -> Dict:
        return {
            "success": True,
            "emotion": "neutral",
            "eye_contact": False,
            "face_detected": False,
            "posture": {"posture_score": 45, "posture_quality": "not_visible"},
            "head_position": {"head_position": "face_not_detected", "head_score": 35},
            "engagement": {"engagement_score": 45, "engagement_level": "poor"},
            "gaze": {"eye_contact": False, "eye_contact_score": 35, "gaze_direction": "unknown"},
            "movement": {"stability_score": 50, "movement_level": "unknown"},
            "frame_quality": {"lighting_score": 50, "framing_score": 30, "quality": "poor"},
            "presentation": {"presentation_score": 45, "dress_assessment": "not_visible"},
            "confidence": {"confidence_score": 42, "confidence_level": "needs_attention"},
            "guidance": guidance,
            "overall_score": 42,
            "interviewer_signals": [],
        }

    def get_session_summary(self) -> Dict:
        def avg(values, default=0):
            return sum(values) / len(values) if values else default

        emotion_counts = Counter(self.metrics["emotions"])
        total_emotions = sum(emotion_counts.values()) or 1
        emotion_percentages = {
            emotion: round(count / total_emotions * 100, 1)
            for emotion, count in emotion_counts.most_common()
        }
        frames = len(self.metrics["confidence_scores"])
        eye_rate = round(sum(self.metrics["eye_contact"]) / frames * 100) if frames else 0
        avg_confidence = round(avg(self.metrics["confidence_scores"], 55))

        feedback = []
        signal_map = [
            ("posture", avg(self.metrics["posture_scores"], 55)),
            ("head position", avg(self.metrics["head_position_scores"], 55)),
            ("engagement", avg(self.metrics["engagement_scores"], 55)),
            ("movement stability", avg(self.metrics["movement_scores"], 55)),
            ("framing", avg(self.metrics["framing_scores"], 55)),
            ("lighting", avg(self.metrics["lighting_scores"], 55)),
            ("presentation", avg(self.metrics["presentation_scores"], 55)),
        ]
        for label, score in signal_map:
            feedback.append({
                "cat": label.title(),
                "type": "positive" if score >= 72 else "improve" if score < 58 else "neutral",
                "msg": f"{label.title()} averaged {round(score)}/100 ({_quality(score)}).",
            })

        return {
            "average_posture": round(avg(self.metrics["posture_scores"], 55)),
            "average_head_position": round(avg(self.metrics["head_position_scores"], 55)),
            "average_engagement": round(avg(self.metrics["engagement_scores"], 55)),
            "average_confidence": avg_confidence,
            "average_framing": round(avg(self.metrics["framing_scores"], 55)),
            "average_lighting": round(avg(self.metrics["lighting_scores"], 55)),
            "average_movement_stability": round(avg(self.metrics["movement_scores"], 55)),
            "average_presentation": round(avg(self.metrics["presentation_scores"], 55)),
            "eye_contact_rate": eye_rate,
            "dominant_emotion": emotion_counts.most_common(1)[0][0] if emotion_counts else "neutral",
            "emotion_percentages": emotion_percentages,
            "presentation_score": round(avg(self.metrics["presentation_scores"], 55)),
            "feedback": feedback,
            "total_frames_analyzed": frames,
            "body_language_band": self._calculate_band(avg_confidence),
        }

    def _calculate_band(self, avg_score: float) -> float:
        if avg_score >= 90:
            return 9.0
        if avg_score >= 85:
            return 8.5
        if avg_score >= 80:
            return 8.0
        if avg_score >= 70:
            return 7.0
        if avg_score >= 60:
            return 6.0
        if avg_score >= 50:
            return 5.0
        return 4.0


body_language_analyzer = BodyLanguageAnalyzer()
