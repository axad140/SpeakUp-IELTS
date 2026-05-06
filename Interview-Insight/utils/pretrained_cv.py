import cv2
import numpy as np
import base64
from .body_language_analysis import body_language_analyzer

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DeepFace = None
    DEEPFACE_AVAILABLE = False
    print("[WARNING] deepface not installed. Emotion analysis will use neutral fallback.")

class PretrainedVisionAnalyzer:
    def __init__(self):
        print("[SETUP] Loading pre-trained Computer Vision models for facial analysis...")
        # DeepFace auto-downloads weights for emotion if not present
        # Haar Cascades for extremely fast robust eye detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    def decode_base64_frame(self, b64_string):
        if "," in b64_string:
            b64_string = b64_string.split(",")[1]
        img_data = base64.b64decode(b64_string)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img

    def analyze_frame(self, frame_b64):
        try:
            img = self.decode_base64_frame(frame_b64)
            if img is None:
                return {"emotion": "neutral", "eye_contact": False}

            # 1. EMOTION: using DeepFace pre-trained network
            dominant_emotion = "neutral"
            if DEEPFACE_AVAILABLE:
                try:
                    # enforce_detection=False prevents crash if face briefly disappears
                    emotions = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
                    dominant_emotion = emotions[0]['dominant_emotion'] if isinstance(emotions, list) else emotions['dominant_emotion']
                except Exception as e:
                    print("DeepFace minimal error:", e)

            # 2. EYE CONTACT: utilizing Haar Cascades
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            eye_contact = False

            for (x, y, w, h) in faces:
                roi_gray = gray[y:y+h, x:x+w]
                eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 3)
                if len(eyes) >= 1:
                    eye_contact = True
                    break

            # 3. BODY LANGUAGE ANALYSIS: Full comprehensive analysis
            body_language_result = body_language_analyzer.analyze_frame(
                frame_b64, 
                emotion=dominant_emotion, 
                eye_contact=eye_contact
            )

            return {
                "emotion": dominant_emotion,
                "eye_contact": body_language_result.get("gaze", {}).get("eye_contact", eye_contact),
                "face_detected": body_language_result.get("face_detected", bool(len(faces))),
                "body_language": body_language_result,
                "confidence_score": body_language_result.get('confidence', {}).get('confidence_score', 70),
                "guidance": body_language_result.get('guidance', ''),
                "overall_score": body_language_result.get('overall_score', 70),
                "posture": body_language_result.get('posture', {}),
                "head_position": body_language_result.get('head_position', {}),
                "engagement": body_language_result.get('engagement', {}),
                "gaze": body_language_result.get("gaze", {}),
                "movement": body_language_result.get("movement", {}),
                "frame_quality": body_language_result.get("frame_quality", {}),
                "presentation": body_language_result.get("presentation", {}),
                "interviewer_signals": body_language_result.get("interviewer_signals", [])
            }
        except Exception as e:
            print("[CV ERROR]", e)
            return {
                "emotion": "neutral", 
                "eye_contact": False,
                "face_detected": False,
                "body_language": {},
                "confidence_score": 70,
                "guidance": "Position yourself in front of the camera.",
                "overall_score": 70,
                "gaze": {},
                "movement": {},
                "frame_quality": {},
                "presentation": {},
                "interviewer_signals": []
            }

cv_analyzer = PretrainedVisionAnalyzer()
