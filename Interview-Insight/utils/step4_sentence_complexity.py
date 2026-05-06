"""
STEP 4 — Sentence Complexity & Structure (spaCy)
IELTS checks for complex sentences - more complex = higher band
"""

import subprocess
import sys
import spacy

# Load spaCy model
print("[spaCy] Loading English model...")
try:
    nlp = spacy.load("en_core_web_sm")
    print("✓ spaCy model loaded successfully\n")
except OSError:
    print("⚠️  spaCy model not found. Installing...")
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
    nlp = spacy.load("en_core_web_sm")
    print("✓ spaCy model installed and loaded\n")


def analyze_sentence_complexity(text: str) -> dict:
    """
    Analyze sentence complexity and structure using spaCy
    
    Returns:
        dict with:
        - sentences: count of sentences
        - words: total word count
        - complex_structures: count of conjunctions/complex markers
        - complexity_score: calculated complexity (0-10)
    """
    doc = nlp(text)
    
    # 1. Count sentences
    sentences = list(doc.sents)
    sentence_count = len(sentences)
    
    # 2. Count total words (alpha tokens only)
    words = [token for token in doc if token.is_alpha]
    word_count = len(words)
    
    # 3. Count complex structural markers
    complex_markers = {
        "because": 0,
        "although": 0,
        "however": 0,
        "which": 0,
        "who": 0,
        "that": 0,
        "since": 0,
        "if": 0,
        "while": 0,
        "unless": 0,
        "moreover": 0,
        "furthermore": 0,
    }
    
    for token in doc:
        if token.text.lower() in complex_markers:
            complex_markers[token.text.lower()] += 1
    
    complex_count = sum(complex_markers.values())
    
    # 4. POS Tag analysis (Parts of Speech)
    pos_tags = {}
    for token in doc:
        pos = token.pos_
        pos_tags[pos] = pos_tags.get(pos, 0) + 1
    
    # 5. Calculate complexity score
    # Factors: 
    # - Average sentence length (longer = more complex)
    # - Presence of conjunctions/complex markers
    # - POS variety (more variety = more complex)
    
    avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
    pos_variety = len(pos_tags) / 10  # Normalize by typical POS count
    
    # Complexity formula (scaled to 0-10)
    complexity_score = min(10, (avg_sentence_length / 15 * 5) + (complex_count / (sentence_count + 1) * 3) + (pos_variety * 2))
    
    # 6. Root verbs (indicates main clauses)
    root_verbs = [token.text for token in doc if token.dep_ == "ROOT" and token.pos_ == "VERB"]
    
    return {
        "sentence_count": sentence_count,
        "word_count": word_count,
        "average_sentence_length": round(avg_sentence_length, 2),
        "complex_structures": complex_count,
        "complex_markers_found": {k: v for k, v in complex_markers.items() if v > 0},
        "pos_distribution": pos_tags,
        "pos_variety": round(pos_variety, 2),
        "root_verbs": root_verbs,
        "complexity_score": round(complexity_score, 2),
        "complexity_level": _rate_complexity(complexity_score)
    }


def _rate_complexity(score: float) -> str:
    """Rate linguistic complexity level"""
    if score >= 8:
        return "Very High (Band 8-9)"
    elif score >= 6.5:
        return "High (Band 7-7.5)"
    elif score >= 5:
        return "Moderate (Band 6-6.5)"
    elif score >= 3:
        return "Low (Band 5-5.5)"
    else:
        return "Very Low (Band 4 or below)"


def print_complexity_analysis(text: str) -> None:
    """
    Print detailed sentence complexity analysis
    
    Example:
        text = "She go to market yesterday and buy vegetables because she need cooking ingredients."
        print_complexity_analysis(text)
    """
    result = analyze_sentence_complexity(text)
    
    print("\n" + "="*60)
    print("SENTENCE COMPLEXITY & STRUCTURE (spaCy)")
    print("="*60)
    print(f"\nText: {text}")
    
    print(f"\n📊 Structural Analysis:")
    print(f"   Sentences: {result['sentence_count']}")
    print(f"   Total Words: {result['word_count']}")
    print(f"   Avg Sentence Length: {result['average_sentence_length']} words")
    print(f"   Complex Structures Found: {result['complex_structures']}")
    
    if result['complex_markers_found']:
        print(f"\n🔗 Complex Markers:")
        for marker, count in result['complex_markers_found'].items():
            print(f"   - {marker}: {count}")
    
    print(f"\n🎯 POS Distribution (Parts of Speech):")
    for pos, count in sorted(result['pos_distribution'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   - {pos}: {count}")
    
    if result['root_verbs']:
        print(f"\n📌 Root Verbs (Main Clauses):")
        for verb in result['root_verbs']:
            print(f"   - {verb}")
    
    print(f"\n⭐ Complexity Score: {result['complexity_score']}/10")
    print(f"   Level: {result['complexity_level']}")
    
    print("\n" + "="*60 + "\n")


# Example usage
if __name__ == "__main__":
    # Test sentence
    test_text = "She go to market yesterday and buy vegetables because she need cooking ingredients."
    print_complexity_analysis(test_text)
    
    # Store metrics
    result = analyze_sentence_complexity(test_text)
    complexity_score = result['complexity_score']
    
    print(f"Stored Metrics:")
    print(f"  complexity_score = {complexity_score}")
    print(f"  complexity_level = {result['complexity_level']}")
