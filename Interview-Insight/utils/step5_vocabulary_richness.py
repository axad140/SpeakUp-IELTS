"""
STEP 5 — Vocabulary Richness (Lexical Resource)
IELTS checks vocabulary variety - higher ratio = better band
"""

import spacy
from collections import Counter

# Load spaCy model
nlp = spacy.load("en_core_web_sm")


def analyze_vocabulary_richness(text: str) -> dict:
    """
    Analyze vocabulary richness and variety
    
    Returns:
        dict with:
        - total_words: total word count
        - unique_words: count of unique words
        - vocabulary_richness: type-token ratio (0-1)
        - vocabulary_richness_percentage: as percentage
        - vocabulary_level: assessed level
        - word_frequency: most common words
        - rare_words: less common/sophisticated words
    """
    doc = nlp(text)
    
    # Get all alphabetic tokens (words)
    tokens = [token.text.lower() for token in doc if token.is_alpha]
    word_count = len(tokens)
    
    # Calculate unique words
    unique_words = set(tokens)
    unique_count = len(unique_words)
    
    # Type-Token Ratio (TTR) - standard metric for lexical diversity
    # TTR = unique_words / total_words
    # Higher ratio = more diverse vocabulary
    if word_count > 0:
        vocabulary_richness = unique_count / word_count
    else:
        vocabulary_richness = 0
    
    vocabulary_richness_percentage = round(vocabulary_richness * 100, 2)
    
    # Assess vocabulary level based on TTR
    if vocabulary_richness >= 0.75:
        vocab_level = "Excellent (Band 8-9)"
        vocab_score = 9
    elif vocabulary_richness >= 0.60:
        vocab_level = "Very Good (Band 7-7.5)"
        vocab_score = 7.5
    elif vocabulary_richness >= 0.45:
        vocab_level = "Good (Band 6-6.5)"
        vocab_score = 6.5
    elif vocabulary_richness >= 0.35:
        vocab_level = "Adequate (Band 5-5.5)"
        vocab_score = 5.5
    else:
        vocab_level = "Limited (Band 4 or below)"
        vocab_score = 4
    
    # Word frequency distribution
    word_freq = Counter(tokens)
    most_common = word_freq.most_common(10)
    
    # Identify rare/sophisticated words (appear only once)
    rare_words = [word for word, count in word_freq.items() if count == 1][:10]
    
    # Stopwords (common, less meaningful words)
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
                 'have', 'has', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
                 'may', 'might', 'must', 'can', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}
    
    # Content words (meaningful words)
    content_words = [word for word in tokens if word not in stopwords]
    content_word_count = len(content_words)
    unique_content_words = len(set(content_words))
    
    # Content word diversity
    content_word_diversity = (unique_content_words / content_word_count * 100) if content_word_count > 0 else 0
    
    return {
        "total_words": word_count,
        "unique_words": unique_count,
        "vocabulary_richness": round(vocabulary_richness, 4),
        "vocabulary_richness_percentage": vocabulary_richness_percentage,
        "vocabulary_level": vocab_level,
        "vocabulary_score": vocab_score,
        "content_words": content_word_count,
        "unique_content_words": unique_content_words,
        "content_word_diversity": round(content_word_diversity, 2),
        "most_common_words": most_common,
        "rare_words": rare_words,
        "recommendation": _get_vocabulary_recommendation(vocabulary_richness)
    }


def _get_vocabulary_recommendation(vocabulary_richness: float) -> str:
    """Get recommendation based on vocabulary richness"""
    if vocabulary_richness >= 0.75:
        return "✅ Excellent vocabulary variety. Maintain this level!"
    elif vocabulary_richness >= 0.60:
        return "✓ Very good vocabulary. Could use a few more synonyms."
    elif vocabulary_richness >= 0.45:
        return "⚠️  Good vocabulary. Try to use more varied words instead of repetition."
    elif vocabulary_richness >= 0.35:
        return "⚠️  Adequate vocabulary. Avoid repeating the same words - use synonyms."
    else:
        return "❌ Limited vocabulary. Expand your word range significantly."


def print_vocabulary_analysis(text: str) -> None:
    """
    Print detailed vocabulary richness analysis
    
    Example:
        text = "She go to market yesterday and buy vegetables because she need cooking ingredients."
        print_vocabulary_analysis(text)
    """
    result = analyze_vocabulary_richness(text)
    
    print("\n" + "="*60)
    print("VOCABULARY RICHNESS (Lexical Resource)")
    print("="*60)
    print(f"\nText: {text}")
    
    print(f"\n📊 Vocabulary Statistics:")
    print(f"   Total Words: {result['total_words']}")
    print(f"   Unique Words: {result['unique_words']}")
    print(f"   Vocabulary Richness Ratio: {result['vocabulary_richness']}")
    print(f"   Vocabulary Richness %: {result['vocabulary_richness_percentage']}%")
    
    print(f"\n📈 Assessment:")
    print(f"   Level: {result['vocabulary_level']}")
    print(f"   Score: {result['vocabulary_score']}/10")
    
    print(f"\n📝 Content Words Analysis:")
    print(f"   Content Words: {result['content_words']}")
    print(f"   Unique Content Words: {result['unique_content_words']}")
    print(f"   Content Word Diversity: {result['content_word_diversity']}%")
    
    print(f"\n🔝 Most Common Words:")
    for word, count in result['most_common_words'][:5]:
        print(f"   - '{word}': {count} times")
    
    if result['rare_words']:
        print(f"\n💎 Rare/Sophisticated Words (used once):")
        for word in result['rare_words'][:5]:
            print(f"   - {word}")
    
    print(f"\n💡 Recommendation:")
    print(f"   {result['recommendation']}")
    
    print("\n" + "="*60 + "\n")


# Example usage
if __name__ == "__main__":
    # Test sentence
    test_text = "She go to market yesterday and buy vegetables because she need cooking ingredients."
    print_vocabulary_analysis(test_text)
    
    # Store metrics
    result = analyze_vocabulary_richness(test_text)
    vocab_richness = result['vocabulary_richness']
    vocab_score = result['vocabulary_score']
    
    print(f"Stored Metrics:")
    print(f"  vocab_richness = {vocab_richness}")
    print(f"  vocab_score = {vocab_score}")
