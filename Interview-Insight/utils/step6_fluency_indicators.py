"""
STEP 6 — Fluency Indicators (from text)
Detect fillers & repetitions - more fillers = lower fluency
"""


def analyze_fluency_indicators(text: str) -> dict:
    """
    Detect fluency indicators from text:
    - Filler words (um, uh, like, you know, etc.)
    - Repeated words/phrases
    - Hesitation markers
    - Speech flow issues
    
    Returns:
        dict with:
        - filler_words: count and list
        - filler_percentage: percentage of text
        - fluency_score: calculated score
        - fluency_level: assessed level
        - issues: identified fluency problems
    """
    text_lower = text.lower()
    
    # Define filler words
    fillers = {
        'um': 'filler',
        'uh': 'filler',
        'like': 'filler',
        'you know': 'phrase',
        'basically': 'filler',
        'actually': 'filler',
        'i mean': 'phrase',
        'sort of': 'phrase',
        'kind of': 'phrase',
        'really': 'intensifier',
        'very': 'intensifier',
        'just': 'filler',
        'okay': 'filler',
        'well': 'filler',
        'so': 'filler',
        'hmm': 'hesitation',
        'err': 'hesitation',
        'erm': 'hesitation',
        'ah': 'hesitation',
    }
    
    # Count fillers
    filler_count = 0
    filler_found = {}
    
    for filler, filler_type in fillers.items():
        count = text_lower.count(filler)
        if count > 0:
            filler_count += count
            filler_found[filler] = {
                "count": count,
                "type": filler_type
            }
    
    # Count words
    words = text.split()
    word_count = len(words)
    
    # Calculate filler percentage
    filler_percentage = (filler_count / word_count * 100) if word_count > 0 else 0
    
    # Detect repetition (words used more than 3 times unnecessarily)
    word_freq = {}
    for word in words:
        word_clean = word.lower().strip('.,!?;:')
        if len(word_clean) > 3:  # Ignore short words
            word_freq[word_clean] = word_freq.get(word_clean, 0) + 1
    
    repetitions = {word: count for word, count in word_freq.items() if count > 3}
    repetition_score = len(repetitions)
    
    # Detect hesitations & stuttering patterns
    hesitation_patterns = ['...', '- -', 'th-th', 'l-l']
    hesitation_count = sum(text.lower().count(pattern) for pattern in hesitation_patterns)
    
    # Sentence length consistency (more consistent = more fluent)
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    if len(sentences) > 1:
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_length = sum(sentence_lengths) / len(sentence_lengths)
        variance = sum((length - avg_length)**2 for length in sentence_lengths) / len(sentence_lengths)
        consistency_score = max(0, 10 - (variance / 10))  # Lower variance = higher score
    else:
        consistency_score = 5
    
    # Calculate fluency score (0-10)
    # Factors:
    # - Filler percentage (lower is better): -filler_percentage
    # - Repetitions (lower is better): -repetition_score
    # - Hesitations (lower is better): -hesitation_count
    # - Sentence consistency (higher is better): +consistency_score
    
    fluency_score = max(0, min(10, 10 - (filler_percentage / 10) - (repetition_score / 2) - (hesitation_count * 0.5) + (consistency_score / 10) * 3))
    
    # Assess fluency level
    if fluency_score >= 8:
        fluency_level = "Very Fluent (Band 8-9)"
    elif fluency_score >= 6.5:
        fluency_level = "Fluent (Band 7-7.5)"
    elif fluency_score >= 5:
        fluency_level = "Moderately Fluent (Band 6-6.5)"
    elif fluency_score >= 3:
        fluency_level = "Less Fluent (Band 5-5.5)"
    else:
        fluency_level = "Not Fluent (Band 4 or below)"
    
    # Identify issues
    issues = []
    if filler_percentage > 5:
        issues.append(f"❌ High filler usage ({filler_percentage:.1f}%) - reduces fluency")
    
    if repetition_score > 3:
        issues.append(f"⚠️  Word repetition detected - use synonyms instead")
    
    if hesitation_count > 2:
        issues.append(f"⚠️  Stuttering/hesitation patterns - practice smooth delivery")
    
    if consistency_score < 3:
        issues.append(f"⚠️  Inconsistent sentence length - practice rhythm")
    
    if not issues:
        issues.append("✅ Good fluency indicators detected")
    
    return {
        "filler_count": filler_count,
        "filler_percentage": round(filler_percentage, 2),
        "filler_found": filler_found,
        "repetition_score": repetition_score,
        "repetitions_found": repetitions,
        "hesitation_count": hesitation_count,
        "sentence_consistency": round(consistency_score, 2),
        "fluency_score": round(fluency_score, 2),
        "fluency_level": fluency_level,
        "word_count": word_count,
        "sentence_count": len(sentences),
        "issues": issues,
        "recommendation": _get_fluency_recommendation(fluency_score)
    }


def _get_fluency_recommendation(fluency_score: float) -> str:
    """Get recommendation based on fluency score"""
    if fluency_score >= 8:
        return "✅ Excellent fluency. Maintain this smooth delivery!"
    elif fluency_score >= 6.5:
        return "✓ Good fluency. Minor improvements possible."
    elif fluency_score >= 5:
        return "⚠️  Moderate fluency. Reduce fillers and practice smooth delivery."
    elif fluency_score >= 3:
        return "⚠️  Lower fluency. Focus on reducing fillers and speaking more naturally."
    else:
        return "❌ Poor fluency. Practice speaking more smoothly and reducing hesitations."


def print_fluency_analysis(text: str) -> None:
    """
    Print detailed fluency analysis
    
    Example:
        text = "Well, like, she go to market yesterday, you know, and buy vegetables because she like needed cooking ingredients."
        print_fluency_analysis(text)
    """
    result = analyze_fluency_indicators(text)
    
    print("\n" + "="*60)
    print("FLUENCY INDICATORS DETECTION")
    print("="*60)
    print(f"\nText: {text}")
    
    print(f"\n📊 Fluency Statistics:")
    print(f"   Total Words: {result['word_count']}")
    print(f"   Sentences: {result['sentence_count']}")
    
    print(f"\n🎙️  Filler Words Analysis:")
    print(f"   Total Fillers: {result['filler_count']}")
    print(f"   Filler Percentage: {result['filler_percentage']}%")
    if result['filler_found']:
        for filler, data in result['filler_found'].items():
            print(f"   - '{filler}': {data['count']} times ({data['type']})")
    else:
        print(f"   ✅ No filler words detected")
    
    print(f"\n🔄 Repetition Analysis:")
    print(f"   Repetition Score: {result['repetition_score']}")
    if result['repetitions_found']:
        for word, count in sorted(result['repetitions_found'].items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   - '{word}': repeated {count} times")
    else:
        print(f"   ✅ Good word variety - no excessive repetition")
    
    print(f"\n⏸️  Hesitation Markers:")
    print(f"   Hesitations: {result['hesitation_count']}")
    
    print(f"\n🎯 Sentence Consistency:")
    print(f"   Score: {result['sentence_consistency']}/10")
    
    print(f"\n⭐ Fluency Score: {result['fluency_score']}/10")
    print(f"   Level: {result['fluency_level']}")
    
    print(f"\n❗ Issues Found:")
    for issue in result['issues']:
        print(f"   {issue}")
    
    print(f"\n💡 Recommendation:")
    print(f"   {result['recommendation']}")
    
    print("\n" + "="*60 + "\n")


# Example usage
if __name__ == "__main__":
    # Test sentence with fillers
    test_text = "Well, like, she go to market yesterday, you know, and buy vegetables because she, um, needed cooking ingredients."
    print_fluency_analysis(test_text)
    
    # Store metrics
    result = analyze_fluency_indicators(test_text)
    fluency_score = result['fluency_score']
    
    print(f"Stored Metrics:")
    print(f"  fluency_score = {fluency_score}")
    print(f"  fluency_level = {result['fluency_level']}")
