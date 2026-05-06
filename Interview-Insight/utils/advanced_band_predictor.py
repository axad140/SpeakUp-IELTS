"""
ENHANCED IELTS BAND PREDICTOR - v2.0 with Advanced Metrics
Incorporates coherence, idioms, pronunciation, and multiple factors
Provides accurate IELTS band 0-9 with 0.5 increments
"""

def predict_ielts_band_advanced(
    grammar_score: float,
    vocabulary_score: float,
    fluency_score: float,
    pronunciation_score: float,
    coherence_score: float,
    cohesion_score: float,
    complexity_score: float,
    accuracy_score: float,
    idiom_count: int = 0,
    filler_count: int = 0,
    total_words: int = 100,
    response_length: int = 0,
) -> dict:
    """
    Advanced IELTS Band Prediction using comprehensive metrics
    
    IELTS Speaking evaluation criteria:
    1. Fluency & Coherence (25%)
    2. Lexical Resource (25%)
    3. Grammatical Range & Accuracy (25%)
    4. Pronunciation (25%)
    
    Args:
        - grammar_score: 0-10 (from LanguageTool)
        - vocabulary_score: 0-10 (from vocabulary analyzer)
        - fluency_score: 0-10 (from fluency detector)
        - pronunciation_score: 0-10 (from delivery analysis)
        - coherence_score: 0-10 (from coherence analyzer)
        - cohesion_score: 0-10 (from cohesion analyzer)
        - complexity_score: 0-10 (from syntax analyzer)
        - accuracy_score: 0-100 (grammar accuracy percentage)
        - idiom_count: count of idioms used
        - filler_count: count of filler words
        - total_words: total words in response
        - response_length: length in seconds or words
    
    Returns:
        dict with band, sub-scores, descriptors, feedback
    """
    
    # ============ NORMALIZE SCORES TO 0-10 RANGE ============
    grammar_score = min(10, max(0, grammar_score))
    vocabulary_score = min(10, max(0, vocabulary_score))
    fluency_score = min(10, max(0, fluency_score))
    pronunciation_score = min(10, max(0, pronunciation_score))
    coherence_score = min(10, max(0, coherence_score))
    cohesion_score = min(10, max(0, cohesion_score))
    complexity_score = min(10, max(0, complexity_score))
    accuracy_score = min(100, max(0, accuracy_score))
    
    # ============ CALCULATE COMPOSITE SCORES ============
    
    # 1. FLUENCY & COHERENCE (25% of total score)
    # Combination of: fluency, coherence, cohesion, delivery
    fluency_coherence_score = (
        fluency_score * 0.35 +        # Speech smoothness
        coherence_score * 0.35 +       # Logical flow
        cohesion_score * 0.20 +        # Connection between ideas
        pronunciation_score * 0.10     # Delivery clarity
    )
    
    # Penalize excessive fillers
    filler_penalty = min(2, (filler_count / max(1, total_words)) * 20)
    fluency_coherence_score = max(0, fluency_coherence_score - filler_penalty)
    
    # 2. LEXICAL RESOURCE (Vocabulary) - 25% of total score
    # Combination of: vocabulary richness, idiom use, word variety
    lexical_score = vocabulary_score * 0.7
    
    # Bonus for idiom use (indicates higher sophistication)
    if idiom_count >= 3:
        idiom_bonus = 1.0
    elif idiom_count == 2:
        idiom_bonus = 0.5
    elif idiom_count == 1:
        idiom_bonus = 0.25
    else:
        idiom_bonus = 0
    
    lexical_score = min(10, lexical_score + idiom_bonus)
    
    # 3. GRAMMATICAL RANGE & ACCURACY - 25% of total score
    # Combination of: grammar accuracy, sentence complexity, range
    grammatical_score = (
        accuracy_score / 10 * 0.5 +        # Raw accuracy
        grammar_score * 0.3 +               # Grammar quality
        complexity_score * 0.2              # Sentence variety and complexity
    )
    grammatical_score = min(10, max(0, grammatical_score))
    
    # 4. PRONUNCIATION - 25% of total score
    # Use pronunciation_score directly (from delivery/confidence analysis)
    pronunciation_final = pronunciation_score
    
    # ============ IELTS OFFICIAL WEIGHTING ============
    # All four criteria weighted equally at 25% each
    
    overall_score_0_10 = (
        fluency_coherence_score * 0.25 +
        lexical_score * 0.25 +
        grammatical_score * 0.25 +
        pronunciation_final * 0.25
    )
    
    overall_score_0_10 = min(10, max(0, overall_score_0_10))
    
    # ============ CONVERT 0-10 SCALE TO IELTS BAND 0-9 ============
    # Formula: IELTS Band = (score / 10) * 9
    
    ielts_band_float = (overall_score_0_10 / 10) * 9
    
    # Round to nearest 0.5
    ielts_band = round(ielts_band_float * 2) / 2
    ielts_band = max(0, min(9, ielts_band))
    
    # ============ BAND DESCRIPTORS (Official IELTS Bands) ============
    
    band_descriptors = {
        9.0: {
            "label": "Expert User",
            "description": "Fully realizes the linguistic potential of the task. Demonstrates sustained, effortless, fluent use of the language with only rare minor inaccuracies.",
            "fluency": "Speaks fluently with complete coherence and perfect flow",
            "lexical": "Uses sophisticated vocabulary with precision",
            "grammar": "Uses a wide range of structures accurately and flexibly",
            "pronunciation": "Has clear, natural pronunciation with appropriate stress and intonation",
            "examples": [
                "✓ Maintains consistent accuracy with complex structures",
                "✓ Sophisticated lexical choice throughout",
                "✓ Effortless fluency with excellent coherence"
            ]
        },
        8.5: {
            "label": "Very Good User",
            "description": "Demonstrates robust, sustained ability with consistent accuracy. Occasional minor errors or inappropriateness.",
            "fluency": "Speaks fluently with occasional repetition or self-correction",
            "lexical": "Uses a good range of vocabulary with appropriate choice",
            "grammar": "Uses a range of complex structures mostly accurately",
            "pronunciation": "Clear pronunciation with mainly appropriate stress and intonation",
            "examples": [
                "✓ Strong command of complex structures",
                "✓ Natural flow with minor hesitations",
                "✓ Good vocabulary range with sophistication"
            ]
        },
        8.0: {
            "label": "Very Good User",
            "description": "Handles complex language well, but some inaccuracies and inappropriateness occur.",
            "fluency": "Generally fluent with some repetition but maintains flow",
            "lexical": "Good range of vocabulary with effective expression",
            "grammar": "Uses a range of complex structures with occasional errors",
            "pronunciation": "Clear pronunciation with appropriate stress patterns",
            "examples": [
                "✓ Generally good use of complex structures",
                "✓ Minor grammatical errors don't impede communication",
                "✓ Generally fluent with clear expression"
            ]
        },
        7.5: {
            "label": "Good User",
            "description": "Shows good control but some inaccuracies and occasionally inappropriate expression.",
            "fluency": "Generally fluent with some repetition or hesitation",
            "lexical": "Good vocabulary range with some less common words",
            "grammar": "Good grammatical accuracy with some errors in complex structures",
            "pronunciation": "Clear pronunciation with generally appropriate stress",
            "examples": [
                "✓ Good use of both simple and complex structures",
                "✓ Some vocabulary sophistication",
                "✓ Speaks with reasonable fluency"
            ]
        },
        7.0: {
            "label": "Good User",
            "description": "Shows operational command with some inaccuracies and inappropriate usage.",
            "fluency": "Speaks at a reasonable pace with only occasional hesitation",
            "lexical": "Adequate vocabulary range for the task",
            "grammar": "Mostly accurate with some errors in complex structures",
            "pronunciation": "Clear enough to be generally understood",
            "examples": [
                "✓ Can handle both simple and complex grammar",
                "✓ Generally clear communication",
                "✓ Adequate vocabulary for most topics"
            ]
        },
        6.5: {
            "label": "Competent User",
            "description": "Shows generally effective operation despite inaccuracies and inappropriateness.",
            "fluency": "Speaks with some hesitation but generally communicates ideas",
            "lexical": "Vocabulary range adequate for the task",
            "grammar": "Generally accurate with noticeable errors in complex structures",
            "pronunciation": "Generally clear with occasional difficulty",
            "examples": [
                "✓ Can produce simple and some complex sentences",
                "✓ Communicates main ideas effectively",
                "✓ Minor pronunciation issues don't impede understanding"
            ]
        },
        6.0: {
            "label": "Competent User",
            "description": "Shows some effective operation but with noticeable problems.",
            "fluency": "Speaks with noticeable hesitation and sometimes inappropriate pausing",
            "lexical": "Limited vocabulary range but adequate for basic topics",
            "grammar": "Frequent errors especially in complex structures",
            "pronunciation": "Pronunciation generally clear but with some problems",
            "examples": [
                "⚠ Limited range of complex structures",
                "⚠ Hesitation affects fluency",
                "⚠ Vocabulary limitations evident"
            ]
        },
        5.5: {
            "label": "Modest User",
            "description": "Shows some limited effective operation with frequent problems.",
            "fluency": "Speaks haltingly with frequent hesitation",
            "lexical": "Limited vocabulary range with repetition",
            "grammar": "Errors in simple and complex structures are frequent",
            "pronunciation": "Pronunciation problems cause some difficulty",
            "examples": [
                "⚠ Many pauses and repetitions",
                "⚠ Simple vocabulary with frequent repetition",
                "⚠ Grammatical errors are noticeable"
            ]
        },
        5.0: {
            "label": "Modest User",
            "description": "Shows limited operation of the language.",
            "fluency": "Speech is slow with frequent pausing and hesitation",
            "lexical": "Limited vocabulary restricts expression",
            "grammar": "Frequent errors affect communication",
            "pronunciation": "Pronunciation difficulty hampers understanding",
            "examples": [
                "⚠ Very limited fluency",
                "⚠ Cannot express complex ideas",
                "⚠ Many grammatical errors"
            ]
        },
        4.0: {
            "label": "Limited User",
            "description": "Shows limited ability with fundamental problems.",
            "fluency": "Speech is very slow and hesitant",
            "lexical": "Very limited vocabulary",
            "grammar": "Very frequent errors",
            "pronunciation": "Significant pronunciation problems",
            "examples": [
                "✗ Severe hesitation and pausing",
                "✗ Cannot form complex sentences",
                "✗ Basic vocabulary only"
            ]
        }
    }
    
    # ============ GET BAND DESCRIPTOR ============
    descriptor = band_descriptors.get(ielts_band, band_descriptors[4.0])
    
    # ============ DETERMINE STRENGTHS & WEAKNESSES ============
    
    criteria_scores = {
        "Fluency & Coherence": fluency_coherence_score,
        "Lexical Resource": lexical_score,
        "Grammatical Range": grammatical_score,
        "Pronunciation": pronunciation_final
    }
    
    # Sort by score
    sorted_criteria = sorted(criteria_scores.items(), key=lambda x: x[1], reverse=True)
    
    strengths = [criterion for criterion, score in sorted_criteria[:2] if score >= 6.5]
    weaknesses = [criterion for criterion, score in sorted_criteria[-2:] if score < 6.5]
    
    # ============ RETURN COMPREHENSIVE RESULT ============
    
    return {
        "ielts_band": ielts_band,
        "score_0_10": round(overall_score_0_10, 2),
        "band_label": descriptor["label"],
        "band_description": descriptor["description"],
        
        "criteria_breakdown": {
            "fluency_coherence": round(fluency_coherence_score, 2),
            "lexical_resource": round(lexical_score, 2),
            "grammatical_range": round(grammatical_score, 2),
            "pronunciation": round(pronunciation_final, 2)
        },
        
        "component_scores": {
            "grammar": round(grammar_score, 2),
            "vocabulary": round(vocabulary_score, 2),
            "fluency": round(fluency_score, 2),
            "coherence": round(coherence_score, 2),
            "cohesion": round(cohesion_score, 2),
            "complexity": round(complexity_score, 2),
            "pronunciation": round(pronunciation_score, 2),
            "accuracy_percentage": round(accuracy_score, 2)
        },
        
        "bonus_factors": {
            "idioms_used": idiom_count,
            "filler_words": filler_count,
            "idiom_bonus_applied": idiom_bonus > 0
        },
        
        "band_details": {
            "fluency": descriptor["fluency"],
            "lexical": descriptor["lexical"],
            "grammar": descriptor["grammar"],
            "pronunciation": descriptor["pronunciation"],
            "examples": descriptor["examples"]
        },
        
        "strengths": strengths if strengths else ["Continue building on your current level"],
        "weaknesses": weaknesses if weaknesses else ["No significant weaknesses identified"],
        
        "confidence_interval": {
            "lower_bound": round(max(0, ielts_band - 0.5), 1),
            "upper_bound": round(min(9, ielts_band + 0.5), 1),
            "note": f"Your band is likely between {round(max(0, ielts_band - 0.5), 1)} and {round(min(9, ielts_band + 0.5), 1)}"
        },
        
        "next_steps": _get_next_steps(ielts_band, criteria_scores),
        "detailed_feedback": _get_detailed_feedback(ielts_band, descriptor)
    }


def _get_next_steps(band: float, criteria_scores: dict) -> list:
    """
    Generate personalized next steps based on band and scores
    """
    steps = []
    
    if band < 6:
        steps = [
            "1. Focus on fundamental English grammar and sentence structure",
            "2. Build daily vocabulary (learn 20-30 words daily)",
            "3. Practice speaking slowly and deliberately",
            "4. Record yourself and identify pronunciation issues",
            "5. Listen to English media daily (podcasts, movies, songs)"
        ]
    elif band < 7:
        steps = [
            "1. Practice using complex sentence structures naturally",
            "2. Learn and use topic-specific vocabulary",
            "3. Work on reducing hesitation and pauses",
            "4. Use linking words to connect ideas",
            "5. Practice past and future tenses extensively"
        ]
    elif band < 8:
        steps = [
            "1. Focus on sophisticated vocabulary and idiomatic expressions",
            "2. Practice maintaining fluency under pressure",
            "3. Work on consistent accuracy with complex structures",
            "4. Use pronunciation recordings to fine-tune intonation",
            "5. Practice on varied topics to build confidence"
        ]
    else:
        steps = [
            "1. Maintain current level through regular practice",
            "2. Aim for even more sophisticated vocabulary and expressions",
            "3. Perfect your pronunciation and stress patterns",
            "4. Practice varied topic areas to maintain fluency",
            "5. Consider advanced preparation for real IELTS exam"
        ]
    
    return steps


def _get_detailed_feedback(band: float, descriptor: dict) -> str:
    """
    Generate detailed feedback message
    """
    feedback = f"""
    Your IELTS Speaking Band: {descriptor['label']}
    
    {descriptor['description']}
    
    Fluency & Coherence: {descriptor['fluency']}
    Lexical Resource: {descriptor['lexical']}
    Grammatical Range: {descriptor['grammar']}
    Pronunciation: {descriptor['pronunciation']}
    """
    
    return feedback.strip()


if __name__ == "__main__":
    # Example usage
    result = predict_ielts_band_advanced(
        grammar_score=7.5,
        vocabulary_score=7.0,
        fluency_score=6.8,
        pronunciation_score=7.2,
        coherence_score=7.1,
        cohesion_score=6.9,
        complexity_score=7.0,
        accuracy_score=75.0,
        idiom_count=3,
        filler_count=2,
        total_words=200,
        response_length=120
    )
    
    print("\n" + "="*70)
    print("IELTS BAND PREDICTION (ADVANCED)")
    print("="*70)
    print(f"\n🎯 PREDICTED BAND: {result['ielts_band']}")
    print(f"📊 Score (0-10): {result['score_0_10']}")
    print(f"🏆 Level: {result['band_label']}")
    print(f"\n📝 Description:")
    print(f"   {result['band_description']}")
    print(f"\n🔍 Criteria Breakdown:")
    for criterion, score in result['criteria_breakdown'].items():
        print(f"   {criterion.replace('_', ' ').title()}: {score}/10")
    print(f"\n✨ Strengths:")
    for strength in result['strengths']:
        print(f"   ✓ {strength}")
    print(f"\n⚠️ Areas to Improve:")
    for weakness in result['weaknesses']:
        print(f"   • {weakness}")
    print(f"\n🎯 Band Confidence Range: {result['confidence_interval']['lower_bound']}-{result['confidence_interval']['upper_bound']}")
    print(f"\n📈 Next Steps:")
    for step in result['next_steps']:
        print(f"   {step}")
    print("\n" + "="*70 + "\n")
