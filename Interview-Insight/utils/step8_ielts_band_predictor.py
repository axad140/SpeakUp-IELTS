"""
STEP 8 — IELTS Band Predictor Logic
Convert overall score (0-10) to IELTS band (0-9 with 0.5 increments)
"""


def predict_ielts_band(overall_score: float) -> dict:
    """
    Predict IELTS band from overall score (0-10)
    
    IELTS bands:
    9: Expert (90-100)
    8.5: Very Good (85-89)
    8: Very Good (80-84)
    7.5: Good (75-79)
    7: Good (70-74)
    6.5: Competent (65-69)
    6: Competent (60-64)
    5.5: Modest (55-59)
    5: Modest (50-54)
    4.5: Limited (45-49)
    4: Limited (40-44)
    0-3.9: Extremely Limited
    
    Args:
        overall_score: Score on 0-10 scale
    
    Returns:
        dict with band, description, strengths, weaknesses
    """
    
    # Convert 0-10 scale to 0-100 scale for IELTS
    score_100 = overall_score * 10
    
    # Determine band
    band_descriptors = {
        9.0: {
            "range": [90, 100],
            "label": "Expert User",
            "description": "Fully realizes the linguistic potential of the task. Demonstrates sustained, effortless, fluent use of the language.",
            "strengths": [
                "✅ Excellent command of English",
                "✅ Complex structures used accurately",
                "✅ Sophisticated vocabulary with precision",
                "✅ Native-like fluency and ease",
                "✅ Minimal or no errors"
            ],
            "areas_for_improvement": []
        },
        8.5: {
            "range": [85, 89],
            "label": "Very Good User",
            "description": "Demonstrates robust, sustained ability with consistent accuracy. Occasional minor errors.",
            "strengths": [
                "✅ Strong command of English",
                "✅ Good range of complex structures",
                "✅ Effective use of vocabulary",
                "✅ Good fluency",
                "✅ Few significant errors"
            ],
            "areas_for_improvement": ["Minor: occasional grammatical slips", "Minor: occasional pronunciation issues"]
        },
        8.0: {
            "range": [80, 84],
            "label": "Very Good User",
            "description": "Handles complex language well, but some inaccuracies and inappropriateness in places.",
            "strengths": [
                "✅ Very good command of English",
                "✅ Uses complex structures effectively",
                "✅ Demonstrates good vocabulary range",
                "✅ Generally fluent"
            ],
            "areas_for_improvement": [
                "Minor: some grammatical errors",
                "Minor: occasional vocabulary slip",
                "Minor: occasional repetition"
            ]
        },
        7.5: {
            "range": [75, 79],
            "label": "Good User",
            "description": "Generally shows good control with only occasional lapses. Some misuse of complex structures.",
            "strengths": [
                "✓ Good command of English",
                "✓ Handles complex structures (with some errors)",
                "✓ Good vocabulary range",
                "✓ Clear communication"
            ],
            "areas_for_improvement": [
                "Occasional: subject-verb agreement errors",
                "Occasional: tense inconsistency",
                "Occasional: word choice errors",
                "Some: filler words"
            ]
        },
        7.0: {
            "range": [70, 74],
            "label": "Good User",
            "description": "Shows operational command of the language despite some inaccuracies and inappropriate usage.",
            "strengths": [
                "✓ Operational command of English",
                "✓ Uses complex structures (with errors)",
                "✓ Adequate vocabulary",
                "✓ Generally understandable"
            ],
            "areas_for_improvement": [
                "Frequent: grammatical errors",
                "Regular: repetitive vocabulary",
                "Occasional: unclear expression",
                "Some: filler words affecting fluency"
            ]
        },
        6.5: {
            "range": [65, 69],
            "label": "Competent User",
            "description": "Generally accurate with some errors and inappropriate usage. Usually manages to communicate.",
            "strengths": [
                "⚠️  Generally accurate English",
                "⚠️  Attempts complex structures",
                "⚠️  Basic vocabulary adequate",
                "⚠️  Usually understandable"
            ],
            "areas_for_improvement": [
                "Regular: grammatical errors",
                "Regular: limited vocabulary",
                "Frequent: repetition",
                "Regular: hesitation and fillers",
                "Some: unclear expression"
            ]
        },
        6.0: {
            "range": [60, 64],
            "label": "Competent User",
            "description": "Generally makes an effective attempt at communication but with less consistent control of structure and vocabulary.",
            "strengths": [
                "⚠️  Basic accurate English",
                "⚠️  Simple structures mostly correct",
                "⚠️  Basic vocabulary",
                "⚠️  Main ideas communicated"
            ],
            "areas_for_improvement": [
                "Frequent: grammatical errors",
                "Frequent: basic vocabulary only",
                "Frequent: repetition of words",
                "Regular: filler words",
                "Regular: hesitation and pausing",
                "Some: mispronunciation"
            ]
        },
        5.5: {
            "range": [55, 59],
            "label": "Modest User",
            "description": "Generally makes himself understood, though accuracy is inconsistent. Ideas are expressed but often lack clarity.",
            "strengths": [
                "⚠️  Can express basic ideas",
                "⚠️  Simple structures attempted",
                "⚠️  Basic vocabulary used",
                "⚠️  Partially understandable"
            ],
            "areas_for_improvement": [
                "Many: grammatical errors",
                "Many: vocabulary limitations",
                "Frequent: word repetition",
                "Frequent: fillers and hesitations",
                "Frequent: unclear ideas",
                "Some: significant pronunciation issues"
            ]
        },
        5.0: {
            "range": [50, 54],
            "label": "Modest User",
            "description": "Can sometimes deal with communication tasks involving familiar contexts, but with limited accuracy.",
            "strengths": [
                "⚠️  Sometimes communicates ideas",
                "⚠️  Simple familiar topics",
                "⚠️  Very basic vocabulary",
                "⚠️  Partially understandable"
            ],
            "areas_for_improvement": [
                "Frequent: grammatical errors",
                "Significant: vocabulary limitations",
                "Frequent: word/phrase repetition",
                "Very frequent: fillers",
                "Frequent: hesitation and pausing",
                "Regular: pronunciation issues",
                "Ideas: often unclear or incomplete"
            ]
        },
        4.5: {
            "range": [45, 49],
            "label": "Limited User",
            "description": "Generally fails to communicate with clarity. Frequent errors and extensive pauses.",
            "strengths": [
                "❌ Limited communication ability",
                "❌ Familiar topics only",
                "❌ Very basic vocabulary",
                "❌ Difficult to understand"
            ],
            "areas_for_improvement": [
                "Many: grammatical errors",
                "Severe: vocabulary limitations",
                "Very frequent: repetition",
                "Very frequent: fillers",
                "Very frequent: long pauses",
                "Regular: significant pronunciation issues",
                "Ideas: usually unclear",
                "Grammar: basic structures only"
            ]
        },
        4.0: {
            "range": [40, 44],
            "label": "Limited User",
            "description": "Can express simple meanings in isolated familiar contexts. Frequent pauses and errors.",
            "strengths": [
                "❌ Very limited communication",
                "❌ Only simple ideas",
                "❌ Minimal vocabulary",
                "❌ Hard to understand"
            ],
            "areas_for_improvement": [
                "Frequent: significant errors",
                "Severe: grammar issues",
                "Severe: vocabulary limitations",
                "Very frequent: fillers",
                "Very frequent: pauses",
                "Regular: pronunciation problems",
                "Ideas: unclear",
                "No complex structures"
            ]
        },
    }
    
    # Find the appropriate band
    for band, descriptor in sorted(band_descriptors.items(), reverse=True):
        if score_100 >= descriptor['range'][0]:
            band_info = {
                "band": band,
                "label": descriptor["label"],
                "description": descriptor["description"],
                "score_range": f"{descriptor['range'][0]}-{descriptor['range'][1]}",
                "overall_score": overall_score,
                "score_100": score_100,
                "strengths": descriptor["strengths"],
                "areas_for_improvement": descriptor["areas_for_improvement"]
            }
            return band_info
    
    # If below 4.0
    return {
        "band": "Below 4",
        "label": "Extremely Limited User",
        "description": "Fails to communicate effectively in English. Severe language errors throughout.",
        "score_range": "0-39",
        "overall_score": overall_score,
        "score_100": score_100,
        "strengths": [],
        "areas_for_improvement": [
            "❌ Major: very limited English knowledge",
            "❌ Major: frequent and severe errors",
            "❌ Major: minimal vocabulary",
            "❌ Major: pronunciation issues",
            "❌ Major: very difficult to understand",
            "Recommendation: Significant improvement needed in all areas"
        ]
    }


def print_band_prediction(overall_score: float) -> dict:
    """
    Print detailed IELTS band prediction
    
    Example:
        print_band_prediction(6.8)
    """
    band_info = predict_ielts_band(overall_score)
    
    print("\n" + "="*60)
    print("IELTS BAND PREDICTION")
    print("="*60)
    
    print(f"\n📊 Overall Score: {band_info['overall_score']}/10 ({band_info['score_100']:.0f}/100)")
    
    print(f"\n🎯 PREDICTED IELTS BAND: {band_info['band']}")
    print(f"   Category: {band_info['label']}")
    print(f"   Range: {band_info['score_range']}")
    
    print(f"\n📖 Description:")
    print(f"   {band_info['description']}")
    
    if band_info['strengths']:
        print(f"\n✅ Strengths:")
        for strength in band_info['strengths']:
            print(f"   {strength}")
    
    if band_info['areas_for_improvement']:
        print(f"\n⚠️  Areas for Improvement:")
        for area in band_info['areas_for_improvement']:
            print(f"   {area}")
    
    print("\n" + "="*60 + "\n")
    
    return band_info


# Example usage
if __name__ == "__main__":
    # Example: score of 6.8/10 should predict band 7.0
    result = print_band_prediction(6.8)
    
    print(f"Stored Band:")
    print(f"  band = {result['band']}")
    print(f"  score_100 = {result['score_100']}")
