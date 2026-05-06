"""
IELTS Evaluator Pipeline - Professional Version
Powered by Unified Professional NLP Engine (Offline)
"""

from utils.professional_nlp_engine import get_professional_judgment
from utils.speech_transcription import transcribe_audio_local

def evaluate_ielts_full_response(question: str, answer: str) -> dict:
    """
    Main entry point for professional IELTS response evaluation.
    This function replaces the fragmented step-by-step pipeline with a 
    unified, high-accuracy model-based engine.
    """
    print(f"\n[PIPELINE] Evaluating Response for Question: '{question}'...")
    
    # Run unified evaluation
    result = get_professional_judgment(question, answer)
    
    if result.get("status") == "success":
        print(f"✓ Evaluation complete. Predicted Band: {result['overall_band']['band']}")
        print(f"✓ Judgment Summary: {result['interviewer_report']}")
    else:
        print(f"✗ Evaluation failed: {result.get('error')}")
        
    return result

def evaluate_audio_response(question: str, audio_path: str) -> dict:
    """
    End-to-end evaluation from audio file to full IELTS report
    """
    print(f"\n[PIPELINE] Processing audio response...")
    
    # 1. Transcribe locally using Whisper
    transcription_result = transcribe_audio_local(audio_path)
    
    if transcription_result.get("error"):
        return {"error": transcription_result["error"]}
        
    text = transcription_result["text"]
    
    # 2. Evaluate using Professional NLP Engine
    return evaluate_ielts_full_response(question, text)

if __name__ == "__main__":
    # Test example
    q = "Describe a beautiful place you have visited."
    a = "Well, like, I visited Switzerland last year, you know, and it was a piece of cake to travel there because she go to market yesterday... I mean, the views were absolutely breathtaking and I definitely loved the mountains."
    
    report = evaluate_ielts_full_response(q, a)
    
    import json
    print("\nFINAL PROFESSIONAL REPORT (JSON):")
    print(json.dumps(report, indent=2))
