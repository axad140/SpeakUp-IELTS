"""
STEP 7 — Convert These Metrics → Scores (0-10)
Take all metrics and convert to IELTS-compatible scores
"""


def convert_metrics_to_scores(grammar_error_count: int = 0,
                               vocab_richness: float = 0.5,
                               complex_count: int = 0,
                               filler_count: int = 0,
                               total_words: int = 100,
                               accuracy_score: float = 75.0,
                               complexity_score: float = 5.0,
                               fluency_score: float = 5.0,
                               vocabulary_score: float = 5.0) -> dict:
    """
    Convert various metrics into standardized 0-10 IELTS scores
    
    Args:
        grammar_error_count: Number of grammar errors (from LanguageTool)
        vocab_richness: Vocabulary richness ratio (0-1, from spaCy)
        complex_count: Number of complex structures (from spaCy)
        filler_count: Number of filler words (from fluency analysis)
        total_words: Total words in text
        accuracy_score: Grammar accuracy percentage (0-100)
        complexity_score: Sentence complexity score (0-10)
        fluency_score: Fluency score (0-10)
        vocabulary_score: Vocabulary score (0-10)
    
    Returns:
        dict with converted scores and explanations
    """
    
    # ==================== GRAMMAR SCORE ====================
    # Based on: error count and accuracy score
    # Formula: accuracy_score / 10 (converts 0-100 to 0-10)
    grammar_score = accuracy_score / 10
    grammar_score = max(0, min(10, grammar_score))
    
    # ==================== VOCABULARY SCORE ====================
    # Based on: vocabulary richness (type-token ratio)
    # Formula: richness * 10 (converts 0-1 to 0-10)
    vocab_score = vocab_richness * 10
    vocab_score = max(0, min(10, vocab_score))
    
    # Alternative formula if using explicit vocabulary_score:
    # vocab_score = vocabulary_score
    
    # ==================== COMPLEXITY SCORE ====================
    # Based on: complex structures and sentence length
    # Already typically 0-10
    complexity_score = max(0, min(10, complexity_score))
    
    # ==================== FLUENCY SCORE ====================
    # Based on: filler words, hesitation, repetition
    # Already typically 0-10
    fluency_score = max(0, min(10, fluency_score))
    
    # ==================== PRONUNCIATION SCORE ====================
    # In this simplified version, use confidence/delivery as proxy
    # For real system: use actual pronunciation analysis
    # Estimate from fluency: better fluency = better pronunciation likely
    pronunciation_score = fluency_score * 0.9  # Slightly lower than fluency
    pronunciation_score = max(0, min(10, pronunciation_score))
    
    # ==================== COHERENCE SCORE ====================
    # Based on: complexity (complex structures indicate good coherence)
    coherence_score = complexity_score * 0.95
    coherence_score = max(0, min(10, coherence_score))
    
    # ==================== CALCULATE OVERALL SCORES ====================
    
    # IELTS weighs all 4 criteria equally:
    # 1. Grammatical Range & Accuracy
    # 2. Fluency & Coherence
    # 3. Lexical Resource (Vocabulary)
    # 4. Pronunciation
    
    overall_score_four_criteria = (grammar_score + fluency_score + vocab_score + pronunciation_score) / 4
    
    # Alternative: IELTS official weighting (all equal weight)
    overall_score_with_coherence = (grammar_score + fluency_score + vocab_score + pronunciation_score + coherence_score) / 5
    
    # Use the 4-criteria version (official IELTS)
    overall_score = overall_score_four_criteria
    overall_score = round(overall_score, 2)
    
    return {
        "grammar_score": round(grammar_score, 2),
        "vocabulary_score": round(vocab_score, 2),
        "complexity_score": round(complexity_score, 2),
        "fluency_score": round(fluency_score, 2),
        "pronunciation_score": round(pronunciation_score, 2),
        "coherence_score": round(coherence_score, 2),
        "overall_score": overall_score,
        "scores_breakdown": {
            "Grammatical Range & Accuracy": round(grammar_score, 2),
            "Fluency & Coherence": round((fluency_score + coherence_score) / 2, 2),
            "Lexical Resource": round(vocab_score, 2),
            "Pronunciation": round(pronunciation_score, 2)
        },
        "metrics": {
            "grammar_error_count": grammar_error_count,
            "vocabulary_richness": vocab_richness,
            "complex_structures": complex_count,
            "filler_words": filler_count,
            "total_words": total_words
        }
    }


def print_score_conversion(grammar_error_count: int = 0,
                          vocab_richness: float = 0.5,
                          complex_count: int = 0,
                          filler_count: int = 0,
                          total_words: int = 100,
                          accuracy_score: float = 75.0,
                          complexity_score: float = 5.0,
                          fluency_score: float = 5.0,
                          vocabulary_score: float = 5.0) -> dict:
    """
    Print detailed score conversion report
    """
    result = convert_metrics_to_scores(
        grammar_error_count=grammar_error_count,
        vocab_richness=vocab_richness,
        complex_count=complex_count,
        filler_count=filler_count,
        total_words=total_words,
        accuracy_score=accuracy_score,
        complexity_score=complexity_score,
        fluency_score=fluency_score,
        vocabulary_score=vocabulary_score
    )
    
    print("\n" + "="*60)
    print("METRICS → SCORES CONVERSION (IELTS 0-10)")
    print("="*60)
    
    print(f"\n📊 Input Metrics:")
    print(f"   Grammar Errors: {grammar_error_count}")
    print(f"   Accuracy Score: {accuracy_score}%")
    print(f"   Vocabulary Richness: {vocab_richness}")
    print(f"   Complex Structures: {complex_count}")
    print(f"   Filler Words: {filler_count}")
    print(f"   Total Words: {total_words}")
    
    print(f"\n🎯 Converted Scores (0-10):")
    print(f"   Grammar Score: {result['grammar_score']}/10")
    print(f"   Vocabulary Score: {result['vocabulary_score']}/10")
    print(f"   Complexity Score: {result['complexity_score']}/10")
    print(f"   Fluency Score: {result['fluency_score']}/10")
    print(f"   Pronunciation Score: {result['pronunciation_score']}/10")
    print(f"   Coherence Score: {result['coherence_score']}/10")
    
    print(f"\n⭐ OVERALL SCORE: {result['overall_score']}/10")
    
    print(f"\n📈 IELTS 4 Criteria Breakdown:")
    for criterion, score in result['scores_breakdown'].items():
        print(f"   - {criterion}: {score}/10")
    
    print("\n" + "="*60 + "\n")
    
    return result


# Example usage
if __name__ == "__main__":
    # Example metrics from analysis steps
    result = print_score_conversion(
        grammar_error_count=2,
        vocab_richness=0.65,
        complex_count=3,
        filler_count=1,
        total_words=80,
        accuracy_score=80.0,
        complexity_score=6.5,
        fluency_score=7.0,
        vocabulary_score=6.5
    )
    
    print(f"\nStored Overall Score:")
    print(f"  overall_score = {result['overall_score']}")
