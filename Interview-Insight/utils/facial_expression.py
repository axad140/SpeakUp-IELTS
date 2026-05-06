import cv2
import threading
from config import VIDEO_CAPTURE_INDEX, CAMERA_FRAME_WIDTH, CAMERA_FRAME_HEIGHT, EMOTION_ANALYSIS_INTERVAL
import random

# Global variables
emotion_count = {
    'happy': 0,
    'sad': 0,
    'neutral': 0,
    'angry': 0,
    'surprised': 0,
    'fear': 0,
    'calm': 0
}
camera_active = True

def capture_facial_expressions():
    global camera_active
    try:
        cap = cv2.VideoCapture(VIDEO_CAPTURE_INDEX)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_FRAME_HEIGHT)
        frame_count = 0
        
        while cap.isOpened() and camera_active:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Simulate emotion detection with weighted distribution
            # Positive emotions (happy, calm) should be more frequent for confident speech
            frame_count += 1
            if frame_count % 3 == 0:  # Analyze every 3rd frame
                rand_val = random.random()
                if rand_val < 0.4:
                    emotion = 'neutral'
                elif rand_val < 0.6:
                    emotion = 'happy'
                elif rand_val < 0.8:
                    emotion = 'calm'
                else:
                    emotion = 'surprised'
                
                emotion_count[emotion] += 1

        cap.release()
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Warning: Camera access issue: {str(e)}")

def start_facial_expression_thread():
    global camera_active
    camera_active = True
    facial_thread = threading.Thread(target=capture_facial_expressions, daemon=True)
    facial_thread.start()

def stop_camera():
    global camera_active
    camera_active = False

def get_emotion_stats():
    """Calculate emotion statistics and confidence score"""
    total = sum(emotion_count.values())
    
    if total == 0:
        return {
            "emotions": emotion_count,
            "confidence_score": 70,
            "dominant_emotion": "neutral"
        }
    
    # Calculate percentages
    emotion_percentages = {k: (v / total * 100) for k, v in emotion_count.items()}
    
    # Find dominant emotion
    dominant = max(emotion_count, key=emotion_count.get)
    
    # Calculate confidence score based on positive emotions
    positive_emotions = emotion_count.get('happy', 0) + emotion_count.get('calm', 0)
    confidence_score = min(100, 40 + (positive_emotions / total * 60)) if total > 0 else 70
    
    return {
        "emotions": emotion_count,
        "emotion_percentages": emotion_percentages,
        "dominant_emotion": dominant,
        "confidence_score": round(confidence_score, 1),
        "total_frames_analyzed": total
    }
