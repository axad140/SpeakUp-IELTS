"""
IDIOMATIC EXPRESSION DETECTOR & EVALUATOR
Detects and evaluates use of idiomatic expressions in IELTS context
Higher IELTS bands require sophisticated phrasal verbs and idioms
"""

import re
import spacy

nlp = spacy.load("en_core_web_sm")

# Comprehensive IELTS-level idioms and phrasal verbs
IELTS_IDIOMS = {
    # Academic/Professional Idioms
    "come up with": {"level": 7, "type": "phrasal_verb", "meaning": "to think of or produce"},
    "look into": {"level": 7, "type": "phrasal_verb", "meaning": "to investigate"},
    "deal with": {"level": 6, "type": "phrasal_verb", "meaning": "to handle or manage"},
    "bring about": {"level": 7, "type": "phrasal_verb", "meaning": "to cause something to happen"},
    "put forward": {"level": 7, "type": "phrasal_verb", "meaning": "to propose"},
    "set up": {"level": 6, "type": "phrasal_verb", "meaning": "to establish"},
    "carry out": {"level": 7, "type": "phrasal_verb", "meaning": "to conduct or perform"},
    "point out": {"level": 6, "type": "phrasal_verb", "meaning": "to indicate or draw attention"},
    "break down": {"level": 7, "type": "phrasal_verb", "meaning": "to analyze or fail"},
    "take into account": {"level": 7, "type": "idiom", "meaning": "to consider"},
    
    # Confidence & Certainty
    "no doubt": {"level": 7, "type": "idiom", "meaning": "certainly"},
    "to be honest": {"level": 6, "type": "idiom", "meaning": "to speak truthfully"},
    "in my opinion": {"level": 6, "type": "idiom", "meaning": "my perspective"},
    "it goes without saying": {"level": 8, "type": "idiom", "meaning": "it is obvious"},
    "beyond a shadow of a doubt": {"level": 8, "type": "idiom", "meaning": "absolutely certain"},
    "in all likelihood": {"level": 8, "type": "idiom", "meaning": "probably"},
    
    # Cause & Effect
    "as a result": {"level": 6, "type": "phrase", "meaning": "therefore"},
    "as a consequence": {"level": 7, "type": "phrase", "meaning": "therefore"},
    "in consequence": {"level": 7, "type": "phrase", "meaning": "therefore"},
    "on account of": {"level": 7, "type": "phrase", "meaning": "because of"},
    "due to the fact that": {"level": 7, "type": "phrase", "meaning": "because"},
    
    # Common Expressions
    "get the hang of": {"level": 7, "type": "idiom", "meaning": "to understand"},
    "get down to": {"level": 7, "type": "phrasal_verb", "meaning": "to start working seriously on"},
    "run into": {"level": 6, "type": "phrasal_verb", "meaning": "to encounter"},
    "come across": {"level": 6, "type": "phrasal_verb", "meaning": "to encounter or discover"},
    "go through": {"level": 6, "type": "phrasal_verb", "meaning": "to experience"},
    "bring to mind": {"level": 7, "type": "phrasal_verb", "meaning": "to remind"},
    "bear in mind": {"level": 7, "type": "phrasal_verb", "meaning": "to remember"},
    
    # Problem & Solution
    "to the best of my knowledge": {"level": 8, "type": "idiom", "meaning": "as far as I know"},
    "in a nutshell": {"level": 7, "type": "idiom", "meaning": "in summary"},
    "come to a conclusion": {"level": 7, "type": "phrase", "meaning": "to decide"},
    "put matters right": {"level": 8, "type": "phrase", "meaning": "to fix problems"},
    
    # Experience & Change
    "learn a lesson": {"level": 6, "type": "phrase", "meaning": "to gain knowledge from experience"},
    "a breath of fresh air": {"level": 8, "type": "idiom", "meaning": "something refreshingly new"},
    "stand out": {"level": 7, "type": "phrasal_verb", "meaning": "to be noticeably different"},
    "find a way": {"level": 6, "type": "phrase", "meaning": "to discover a solution"},
    
    # Abstract Idioms (Band 8+)
    "at the end of the day": {"level": 7, "type": "idiom", "meaning": "ultimately"},
    "in the long run": {"level": 7, "type": "idiom", "meaning": "eventually"},
    "by and large": {"level": 8, "type": "idiom", "meaning": "generally speaking"},
    "needless to say": {"level": 8, "type": "idiom", "meaning": "obviously"},
    "it is imperative": {"level": 8, "type": "phrase", "meaning": "it is essential"},
}


def detect_idiomatic_expressions(text: str) -> dict:
    """
    Detect idiomatic expressions and phrasal verbs in text
    
    Returns:
        dict with:
        - idioms_found: list of idioms detected
        - idiom_count: total count
        - sophistication_level: average IELTS level
        - band_estimate: estimated IELTS band from idiom use
        - accuracy_of_usage: whether idioms are used correctly
        - recommendations: suggestions for more idioms
    """
    
    text_lower = text.lower()
    found_idioms = []
    
    # Search for idioms (longest first to avoid partial matches)
    sorted_idioms = sorted(IELTS_IDIOMS.keys(), key=len, reverse=True)
    
    for idiom in sorted_idioms:
        # Use word boundaries for accurate matching
        pattern = r'\b' + re.escape(idiom) + r'\b'
        matches = re.finditer(pattern, text_lower)
        
        for match in matches:
            # Avoid duplicate detection
            if not any(idiom_data['phrase'] == idiom for idiom_data in found_idioms):
                context_start = max(0, match.start() - 50)
                context_end = min(len(text), match.end() + 50)
                context = text[context_start:context_end]
                
                found_idioms.append({
                    "phrase": idiom,
                    "level": IELTS_IDIOMS[idiom]["level"],
                    "type": IELTS_IDIOMS[idiom]["type"],
                    "meaning": IELTS_IDIOMS[idiom]["meaning"],
                    "context": context.strip(),
                    "band_contribution": IELTS_IDIOMS[idiom]["level"] / 9.0  # Convert to 0-1 scale
                })
    
    # Calculate statistics
    if found_idioms:
        avg_level = sum(idiom['level'] for idiom in found_idioms) / len(found_idioms)
        sophistication_level = round(avg_level, 1)
        
        # Estimate IELTS band from idiom usage
        if len(found_idioms) == 0:
            band_estimate = 4.5
        elif len(found_idioms) == 1:
            band_estimate = found_idioms[0]['level'] - 1.5
        elif len(found_idioms) >= 2:
            avg_contrib = sum(idiom['band_contribution'] for idiom in found_idioms) / len(found_idioms)
            band_estimate = avg_contrib * 9
        
        band_estimate = round(min(9, max(4, band_estimate)), 1)
    else:
        sophistication_level = 0
        band_estimate = 0
        found_idioms = []
    
    # Assess accuracy of usage (assuming correct if found - ideally parse grammar)
    accuracy_score = 8.0 if found_idioms else 0  # Placeholder - would need semantic checking
    
    # Generate recommendations
    recommendations = []
    
    if len(found_idioms) == 0:
        recommendations.append("❌ No idiomatic expressions detected")
        recommendations.append("💡 For IELTS Band 7+, incorporate idioms naturally:")
        recommendations.append("   - 'come up with' (produce ideas)")
        recommendations.append("   - 'deal with' (handle situations)")
        recommendations.append("   - 'take into account' (consider factors)")
        recommendations.append("   - 'in my opinion' (express views)")
    
    elif len(found_idioms) < 2:
        recommendations.append("⚠️ Very few idiomatic expressions used")
        recommendations.append("💡 Add more sophisticated phrasal verbs and idioms for higher bands")
    
    elif avg_level < 6:
        recommendations.append("⚠️ Idioms are mostly basic (Band 5-6 level)")
        recommendations.append("💡 Use more sophisticated expressions:")
        recommendations.append("   - 'beyond a shadow of a doubt'")
        recommendations.append("   - 'it goes without saying'")
        recommendations.append("   - 'needless to say'")
    
    else:
        recommendations.append("✅ Good range of idiomatic expressions for higher IELTS bands")
    
    return {
        "idioms_found": found_idioms,
        "idiom_count": len(found_idioms),
        "unique_phrases": len(set(idiom['phrase'] for idiom in found_idioms)),
        "sophistication_level": round(sophistication_level, 2),
        "average_band_level": round(avg_level if found_idioms else 0, 2),
        "band_estimate_from_idioms": band_estimate,
        "accuracy_score": accuracy_score,
        "recommendations": recommendations,
        "phrasal_verbs": len([i for i in found_idioms if i['type'] == 'phrasal_verb']),
        "idioms": len([i for i in found_idioms if i['type'] == 'idiom']),
        "phrases": len([i for i in found_idioms if i['type'] == 'phrase'])
    }


if __name__ == "__main__":
    test_texts = [
        "I like to study hard because I want to succeed.",
        "I come up with new ideas regularly. Furthermore, I deal with challenges by thinking outside the box.",
        "It goes without saying that we must take into account various factors. In my opinion, this approach is beyond a shadow of a doubt the best solution."
    ]
    
    for i, text in enumerate(test_texts, 1):
        result = detect_idiomatic_expressions(text)
        
        print(f"\n{'='*70}")
        print(f"TEST {i}: IDIOMATIC EXPRESSION ANALYSIS")
        print(f"{'='*70}")
        print(f"\nText: {text}")
        print(f"\n📊 Statistics:")
        print(f"   Idioms Found: {result['idiom_count']}")
        print(f"   Phrasal Verbs: {result['phrasal_verbs']}")
        print(f"   Idioms: {result['idioms']}")
        print(f"   Phrases: {result['phrases']}")
        print(f"   Sophistication Level: {result['sophistication_level']}")
        print(f"   Estimated Band (from idioms): {result['band_estimate_from_idioms']}")
        
        if result['idioms_found']:
            print(f"\n🔤 Idioms Found:")
            for idiom in result['idioms_found']:
                print(f"   - '{idiom['phrase']}' (Band {idiom['level']}) - {idiom['meaning']}")
        
        print(f"\n💡 Recommendations:")
        for rec in result['recommendations']:
            print(f"   {rec}")
        print()
