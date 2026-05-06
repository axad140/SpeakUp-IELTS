"""
ADVANCED COHERENCE & COHESION ANALYZER
Analyzes logical flow, sentence connections, and discourse coherence
Using sentence embeddings and syntactic analysis
"""

import spacy
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load models
nlp = spacy.load("en_core_web_sm")

print("[COHERENCE] Loading Sentence Transformer model...")
try:
    coherence_model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✓ Sentence Transformer loaded successfully\n")
except Exception as e:
    print(f"⚠️  Warning: Could not load Sentence Transformer: {e}")
    print("   Install with: pip install sentence-transformers scikit-learn")
    coherence_model = None


def analyze_coherence_cohesion(text: str) -> dict:
    """
    Analyze coherence and cohesion of a response
    
    Returns:
        dict with:
        - coherence_score: 0-10 (how well ideas flow)
        - cohesion_score: 0-10 (how well sentences connect)
        - discourse_markers: list of connecting words found
        - sentence_transitions: quality of transitions
        - logical_flow: assessment of logical progression
        - reference_chains: pronoun/reference tracking
        - recommendations: list of improvement suggestions
    """
    doc = nlp(text)
    sentences = list(doc.sents)
    
    if len(sentences) < 2:
        return {
            "coherence_score": 5.0,
            "cohesion_score": 5.0,
            "discourse_markers": [],
            "sentence_transitions": [],
            "logical_flow": "Single or no sentences",
            "reference_chains": [],
            "recommendations": ["Provide more sentences for coherence analysis"]
        }
    
    # ============ DISCOURSE MARKERS ANALYSIS ============
    discourse_markers = {
        'however': 'contrast',
        'but': 'contrast',
        'although': 'contrast',
        'yet': 'contrast',
        'nevertheless': 'contrast',
        'furthermore': 'addition',
        'moreover': 'addition',
        'besides': 'addition',
        'also': 'addition',
        'additionally': 'addition',
        'therefore': 'consequence',
        'hence': 'consequence',
        'so': 'consequence',
        'thus': 'consequence',
        'consequently': 'consequence',
        'as a result': 'consequence',
        'for example': 'exemplification',
        'for instance': 'exemplification',
        'such as': 'exemplification',
        'in other words': 'reformulation',
        'that is': 'reformulation',
        'i.e.': 'reformulation',
    }
    
    found_markers = []
    text_lower = text.lower()
    
    for marker, marker_type in discourse_markers.items():
        if marker in text_lower:
            found_markers.append({
                "marker": marker,
                "type": marker_type,
                "count": text_lower.count(marker)
            })
    
    marker_score = min(10, len(found_markers) * 1.5)  # More markers = better cohesion
    
    # ============ REFERENCE CHAIN ANALYSIS ============
    pronouns = {'he', 'she', 'it', 'they', 'this', 'that', 'these', 'those', 'which', 'who'}
    reference_chains = []
    
    for sent_idx, sent in enumerate(sentences):
        sent_pronouns = [token.text.lower() for token in sent if token.text.lower() in pronouns]
        if sent_pronouns:
            reference_chains.append({
                "sentence": str(sent),
                "pronouns": sent_pronouns,
                "sentence_index": sent_idx
            })
    
    reference_score = min(10, len(reference_chains) * 2)  # More references = better cohesion
    
    # ============ SENTENCE EMBEDDINGS COHERENCE ============
    if coherence_model:
        try:
            sentence_texts = [str(sent).strip() for sent in sentences]
            embeddings = coherence_model.encode(sentence_texts)
            
            # Calculate similarity between consecutive sentences
            transitions = []
            similarities = []
            
            for i in range(len(embeddings) - 1):
                similarity = cosine_similarity(
                    embeddings[i].reshape(1, -1),
                    embeddings[i + 1].reshape(1, -1)
                )[0][0]
                similarities.append(similarity)
                
                quality = "Excellent" if similarity > 0.7 else (
                    "Good" if similarity > 0.5 else (
                    "Fair" if similarity > 0.3 else "Weak"
                ))
                
                transitions.append({
                    "from_sentence": str(sentences[i])[:50] + "...",
                    "to_sentence": str(sentences[i + 1])[:50] + "...",
                    "similarity": round(float(similarity), 3),
                    "quality": quality
                })
            
            # Average similarity = coherence
            avg_similarity = np.mean(similarities) if similarities else 0.5
            coherence_score_semantic = avg_similarity * 10  # Convert 0-1 to 0-10
            
        except Exception as e:
            print(f"Error in semantic coherence: {e}")
            coherence_score_semantic = 5.0
            transitions = []
    else:
        coherence_score_semantic = 5.0
        transitions = []
    
    # ============ SYNTACTIC COHERENCE ============
    # Check for consistent verb tenses
    verb_tenses = {}
    for token in doc:
        if token.pos_ == "VERB":
            tense = token.tag_  # Verb tag includes tense info
            verb_tenses[tense] = verb_tenses.get(tense, 0) + 1
    
    # If too many different tenses, it's less coherent
    num_tenses = len(verb_tenses)
    tense_consistency = max(0, 10 - (num_tenses - 1) * 2)  # Penalize multiple tenses
    
    # ============ FINAL SCORES ============
    coherence_score = min(10, coherence_score_semantic * 0.6 + tense_consistency * 0.4)
    cohesion_score = min(10, (marker_score + reference_score) / 2)
    
    # ============ RECOMMENDATIONS ============
    recommendations = []
    
    if marker_score < 5:
        recommendations.append("⚠️ Use more linking words (however, furthermore, therefore) to connect ideas")
    
    if coherence_score < 6:
        recommendations.append("⚠️ Improve topic clarity - ensure sentences relate to each other logically")
    
    if tense_consistency < 6:
        recommendations.append("⚠️ Keep verb tenses consistent throughout your response")
    
    if len(reference_chains) == 0:
        recommendations.append("💡 Use pronouns (he, she, it, this) to refer back to previously mentioned ideas")
    
    if not found_markers:
        recommendations.append("💡 Add transitional phrases between sentences for better flow")
    
    if not recommendations:
        recommendations.append("✅ Good coherence and cohesion!")
    
    # Determine logical flow assessment
    if coherence_score > 7 and cohesion_score > 7:
        logical_flow = "Excellent - Ideas flow logically with clear connections"
    elif coherence_score > 6 and cohesion_score > 6:
        logical_flow = "Good - Generally coherent with some connecting elements"
    elif coherence_score > 5 or cohesion_score > 5:
        logical_flow = "Fair - Some logical progression but needs improvement"
    else:
        logical_flow = "Weak - Ideas don't connect well"
    
    return {
        "coherence_score": round(min(10, coherence_score), 2),
        "cohesion_score": round(min(10, cohesion_score), 2),
        "discourse_markers_found": len(found_markers),
        "discourse_markers": found_markers,
        "sentence_transitions": transitions,
        "reference_chains_found": len(reference_chains),
        "reference_chains": reference_chains,
        "verb_tense_consistency": round(tense_consistency, 2),
        "logical_flow": logical_flow,
        "recommendations": recommendations,
        "combined_score": round((coherence_score + cohesion_score) / 2, 2)
    }


if __name__ == "__main__":
    test_text = """
    Traveling has many benefits for personal development. First, it allows you to experience 
    different cultures and traditions. Moreover, you can meet new people and build international 
    relationships. Furthermore, traveling improves your problem-solving skills when facing 
    unexpected situations. Therefore, I believe that everyone should travel at least once a year.
    """
    
    result = analyze_coherence_cohesion(test_text)
    
    print("\n" + "="*60)
    print("COHERENCE & COHESION ANALYSIS")
    print("="*60)
    print(f"\n📊 Scores:")
    print(f"   Coherence: {result['coherence_score']}/10")
    print(f"   Cohesion: {result['cohesion_score']}/10")
    print(f"   Combined: {result['combined_score']}/10")
    print(f"\n🔗 Discourse Markers Found: {result['discourse_markers_found']}")
    if result['discourse_markers']:
        for marker in result['discourse_markers']:
            print(f"   - {marker['marker']} ({marker['type']}): {marker['count']}x")
    print(f"\n💭 Logical Flow: {result['logical_flow']}")
    print(f"\n✨ Recommendations:")
    for rec in result['recommendations']:
        print(f"   {rec}")
    print("\n" + "="*60 + "\n")
