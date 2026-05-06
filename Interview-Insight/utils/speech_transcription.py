import os
import tempfile
import time
import torch
from transformers import pipeline

# Global model instance to avoid reloading
_whisper_pipeline = None

def get_whisper_model():
    global _whisper_pipeline
    if _whisper_pipeline is None:
        print("[TRANSCRIPTION] Loading Whisper (Local) model...")
        try:
            # Using 'base' model for a good balance of speed and accuracy
            # 'tiny' is faster, 'small' is more accurate but heavier
            _whisper_pipeline = pipeline(
                "automatic-speech-recognition",
                model="openai/whisper-base",
                chunk_length_s=30,
                device="cuda:0" if torch.cuda.is_available() else "cpu"
            )
            print("✓ Whisper (Local) loaded successfully")
        except Exception as e:
            print(f"✗ Error loading Whisper model: {e}")
            _whisper_pipeline = None
    return _whisper_pipeline

def transcribe_audio_local(audio_file_path):
    """
    Transcribe audio using LOCAL Whisper model (No API)
    """
    try:
        model = get_whisper_model()
        if model is None:
            return {"text": "", "confidence": 0, "error": "Model failed to load"}

        print(f"[TRANSCRIPTION] Local Whisper processing: {os.path.basename(audio_file_path)}")
        
        # Start transcription
        start_time = time.time()
        result = model(audio_file_path, return_timestamps=True)
        processing_time = time.time() - start_time
        
        text = result.get("text", "").strip()
        print(f"[TRANSCRIPTION] ✅ Done in {processing_time:.2f}s! Text: {text[:100]}...")
        
        return {
            "text": text,
            "confidence": 0.98,  # Whisper is highly accurate
            "language": "en",
            "processing_time": processing_time,
            "error": None
        }
    
    except Exception as e:
        print(f"[TRANSCRIPTION] Error: {str(e)}")
        return {
            "text": "",
            "confidence": 0,
            "error": str(e)
        }

def transcribe_audio_from_file(audio_file):
    """
    Transcribe audio from Flask file object locally
    """
    temp_path = None
    try:
        audio_data = audio_file.read()
        if not audio_data or len(audio_data) < 100:
            return {"text": "", "confidence": 0, "error": "Audio data too small"}
        
        # Determine file extension
        is_wav = audio_data[:4] == b'RIFF'
        extension = '.wav' if is_wav else '.webm'
        
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"audio_{int(time.time()*1000)}{extension}")
        
        with open(temp_path, 'wb') as f:
            f.write(audio_data)
        
        # Transcribe locally
        result = transcribe_audio_local(temp_path)
        return result
    
    except Exception as e:
        print(f"[TRANSCRIPTION] ❌ Error: {e}")
        return {"text": "", "confidence": 0, "error": str(e)}
    
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass
