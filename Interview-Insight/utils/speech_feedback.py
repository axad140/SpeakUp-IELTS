import pyttsx3
from config import TTS_ENGINE_RATE, TTS_ENGINE_VOLUME

def provide_feedback(text):
    """Speak out feedback using text-to-speech"""
    engine = pyttsx3.init()
    engine.setProperty('rate', TTS_ENGINE_RATE)
    engine.setProperty('volume', TTS_ENGINE_VOLUME)
    engine.say(text)
    engine.runAndWait()

def get_fluency_feedback(answer):
    """Analyze fluency and provide feedback"""
    words = answer.split()
    sentences = answer.split('.')
    
    # Calculate metrics
    word_count = len(words)
    avg_words_per_sentence = word_count / len([s for s in sentences if s.strip()]) if sentences else 0
    
    issues = []
    score = 85
    
    # Check for fragments and very short sentences
    short_sentences = [s.strip() for s in sentences if len(s.strip().split()) < 3 and s.strip()]
    if len(short_sentences) > 2:
        issues.append("Avoid using too many short sentences. Combine simple ideas.")
        score -= 10
    
    # Check for word repetition (basic check)
    word_freq = {}
    for word in words:
        w = word.lower().strip('.,!?;:')
        if len(w) > 4:
            word_freq[w] = word_freq.get(w, 0) + 1
    
    repeated_words = [w for w, count in word_freq.items() if count > 3]
    if repeated_words:
        issues.append(f"Try to avoid repeating '{repeated_words[0]}' too many times. Use synonyms.")
        score -= 5
    
    # Check sentence variety
    if avg_words_per_sentence < 8:
        issues.append("Use more complex sentence structures. Combine thoughts with connectors.")
        score -= 5
    
    # Check for filler words (basic)
    fillers = answer.lower().count('um') + answer.lower().count('uh') + answer.lower().count('like')
    if fillers > 2:
        issues.append("Reduce filler words (um, uh, like). Take a breath before speaking.")
        score -= 5
    
    return {
        "score": max(0, score),
        "word_count": word_count,
        "sentence_count": len([s for s in sentences if s.strip()]),
        "avg_words_per_sentence": round(avg_words_per_sentence, 1),
        "issues": issues
    }
