"""
CONFIDENCE & HESITATION DETECTOR
Analyzes text for confidence indicators, hesitations, and delivery patterns
Provides insight into speaker confidence level and anxiety indicators
"""

import re
import spacy
from collections import Counter

nlp = spacy.load("en_core_web_sm")


class ConfidenceAnalyzer:
    """
    Analyzes speaker confidence from transcribed text
    """
    
    def __init__(self):
        # Confidence indicators
        self.confidence_phrases = {
            # High confidence markers
            "I'm sure": {"score": 8, "type": "assertion"},
            "definitely": {"score": 8, "type": "emphasis"},
            "certainly": {"score": 8, "type": "assertion"},
            "absolutely": {"score": 8, "type": "emphasis"},
            "without doubt": {"score": 9, "type": "assertion"},
            "no question": {"score": 8, "type": "assertion"},
            "clearly": {"score": 7, "type": "emphasis"},
            "obviously": {"score": 7, "type": "emphasis"},
            "undoubtedly": {"score": 8, "type": "assertion"},
            "unquestionably": {"score": 9, "type": "assertion"},
            "i know": {"score": 7, "type": "assertion"},
            "i believe": {"score": 6, "type": "opinion"},
            
            # Moderate confidence
            "i think": {"score": 5, "type": "opinion"},
            "in my opinion": {"score": 5, "type": "opinion"},
            "probably": {"score": 4, "type": "hedge"},
            "likely": {"score": 4, "type": "hedge"},
            "perhaps": {"score": 3, "type": "hedge"},
            "maybe": {"score": 2, "type": "hedge"},
            "seems": {"score": 3, "type": "hedge"},
            "appears": {"score": 3, "type": "hedge"},
            
            # Low confidence markers
            "i might": {"score": 2, "type": "uncertainty"},
            "could be": {"score": 2, "type": "uncertainty"},
            "sort of": {"score": 2, "type": "hedging"},
            "kind of": {"score": 2, "type": "hedging"},
            "a bit": {"score": 2, "type": "minimization"},
            "somewhat": {"score": 2, "type": "minimization"},
            "i guess": {"score": 1, "type": "uncertainty"},
            "i suppose": {"score": 1, "type": "uncertainty"},
            "i'm not sure": {"score": 0, "type": "uncertainty"},
            "i don't know": {"score": 0, "type": "ignorance"},
        }
        
        # Hesitation markers
        self.hesitation_patterns = {
            "um": {"frequency": 1, "type": "filled_pause"},
            "uh": {"frequency": 1, "type": "filled_pause"},
            "er": {"frequency": 1, "type": "filled_pause"},
            "erm": {"frequency": 1, "type": "filled_pause"},
            "hmm": {"frequency": 1, "type": "thinking"},
            "ah": {"frequency": 1, "type": "realization"},
            "oh": {"frequency": 1, "type": "realization"},
            "well": {"frequency": 1, "type": "delay"},
            "you know": {"frequency": 2, "type": "filler"},
            "like": {"frequency": 2, "type": "filler"},
            "actually": {"frequency": 1, "type": "correction"},
        }
        
        # Anxiety/nervousness indicators
        self.anxiety_indicators = {
            "i'm nervous": 9,
            "i'm anxious": 8,
            "i'm scared": 8,
            "i'm worried": 7,
            "i'm uncomfortable": 7,
            "embarrassed": 8,
            "stressed": 7,
            "overwhelmed": 8,
        }
    
    def analyze_confidence(self, text: str) -> dict:
        """
        Analyze confidence level from text
        
        Returns:
            dict with confidence score, patterns found, assessment
        """
        
        text_lower = text.lower()
        
        # ============ CONFIDENCE MARKERS ANALYSIS ============
        
        confidence_markers_found = []
        total_confidence_score = 0
        
        # Search for confidence phrases (longest first to avoid partial matches)
        sorted_phrases = sorted(self.confidence_phrases.keys(), key=len, reverse=True)
        
        for phrase in sorted_phrases:
            pattern = r'\b' + re.escape(phrase) + r'\b'
            matches = re.finditer(pattern, text_lower)
            count = len(list(matches))
            
            if count > 0:
                phrase_info = self.confidence_phrases[phrase]
                confidence_markers_found.append({
                    "phrase": phrase,
                    "score": phrase_info["score"],
                    "type": phrase_info["type"],
                    "count": count
                })
                total_confidence_score += phrase_info["score"] * count
        
        # Calculate average confidence from phrases
        if confidence_markers_found:
            phrase_confidence_score = total_confidence_score / sum(m["count"] for m in confidence_markers_found)
        else:
            phrase_confidence_score = 5  # Neutral if no markers
        
        # ============ HESITATION ANALYSIS ============
        
        hesitation_markers_found = []
        total_hesitations = 0
        
        for hesitation, info in self.hesitation_patterns.items():
            pattern = r'\b' + re.escape(hesitation) + r'\b'
            matches = re.finditer(pattern, text_lower)
            count = len(list(matches))
            
            if count > 0:
                hesitation_markers_found.append({
                    "marker": hesitation,
                    "count": count,
                    "type": info["type"]
                })
                total_hesitations += count * info["frequency"]
        
        # Calculate hesitation penalty (more hesitations = lower confidence)
        word_count = len(text.split())
        hesitation_rate = (total_hesitations / word_count * 100) if word_count > 0 else 0
        
        # Hesitation impact on confidence (0-10, inverted)
        hesitation_confidence = max(0, 10 - (hesitation_rate / 2))
        
        # ============ ANXIETY INDICATORS ============
        
        anxiety_found = []
        anxiety_score = 0
        
        for anxiety_phrase, severity in self.anxiety_indicators.items():
            if anxiety_phrase in text_lower:
                anxiety_found.append({
                    "phrase": anxiety_phrase,
                    "severity": severity
                })
                anxiety_score = max(anxiety_score, severity)
        
        # ============ SENTENCE STRUCTURE CONFIDENCE ============
        # Complete sentences = more confidence
        # Fragments = less confidence
        
        doc = nlp(text)
        sentences = list(doc.sents)
        
        complete_sentences = 0
        for sent in sentences:
            verbs = [token for token in sent if token.pos_ == "VERB"]
            if verbs:  # Has a verb = likely complete
                complete_sentences += 1
        
        sentence_confidence = (complete_sentences / len(sentences) * 10) if sentences else 5
        
        # ============ FINAL CONFIDENCE CALCULATION ============
        
        # Combine all factors
        overall_confidence = (
            phrase_confidence_score * 0.4 +      # Explicit confidence markers
            hesitation_confidence * 0.3 +         # Hesitation analysis
            sentence_confidence * 0.2 +           # Sentence completeness
            (10 - anxiety_score * 1.5) * 0.1      # Anxiety indicators (inverted)
        )
        
        overall_confidence = min(10, max(0, overall_confidence))
        
        # ============ CONFIDENCE LEVEL ASSESSMENT ============
        
        if overall_confidence >= 8:
            confidence_level = "Very High"
            assessment = "Speaks with strong conviction and authority"
        elif overall_confidence >= 6.5:
            confidence_level = "High"
            assessment = "Generally confident with occasional hesitation"
        elif overall_confidence >= 5:
            confidence_level = "Moderate"
            assessment = "Shows reasonable confidence with some uncertainty"
        elif overall_confidence >= 3:
            confidence_level = "Low"
            assessment = "Displays noticeable hesitation and uncertainty"
        else:
            confidence_level = "Very Low"
            assessment = "Appears anxious or unsure throughout"
        
        # ============ RECOMMENDATIONS ============
        
        recommendations = []
        
        if hesitation_rate > 5:
            recommendations.append(f"⚠️ High hesitation rate ({hesitation_rate:.1f}%) - practice speaking more fluently")
        
        if len(sentences) > 0 and complete_sentences / len(sentences) < 0.7:
            recommendations.append("⚠️ Many sentence fragments - focus on completing thoughts")
        
        if anxiety_score > 5:
            recommendations.append("⚠️ Signs of anxiety detected - practice relaxation techniques before speaking")
        
        if overall_confidence < 5:
            recommendations.append("💡 Build confidence by practicing regularly and focusing on prepared topics")
        
        if not recommendations:
            recommendations.append("✅ Good confidence level - maintain this approach")
        
        return {
            "overall_confidence": round(overall_confidence, 2),
            "confidence_level": confidence_level,
            "assessment": assessment,
            
            "components": {
                "phrase_confidence": round(phrase_confidence_score, 2),
                "hesitation_confidence": round(hesitation_confidence, 2),
                "sentence_confidence": round(sentence_confidence, 2),
                "anxiety_penalty": round((10 - anxiety_score * 1.5), 2) if anxiety_found else 10
            },
            
            "hesitation_analysis": {
                "total_hesitations": total_hesitations,
                "hesitation_rate_percent": round(hesitation_rate, 2),
                "markers_found": hesitation_markers_found,
                "assessment": "High hesitation" if hesitation_rate > 5 else (
                    "Moderate hesitation" if hesitation_rate > 2 else "Low hesitation"
                )
            },
            
            "confidence_markers": confidence_markers_found,
            "marker_count": len(confidence_markers_found),
            
            "anxiety_indicators_found": anxiety_found,
            "anxiety_score": round(anxiety_score, 2) if anxiety_found else 0,
            
            "recommendations": recommendations
        }


def analyze_confidence_level(text: str) -> dict:
    """
    Main function to analyze confidence level
    """
    analyzer = ConfidenceAnalyzer()
    result = analyzer.analyze_confidence(text)
    return result


if __name__ == "__main__":
    test_texts = [
        "I think... well, um, maybe traveling is good? Sort of? I mean, it could help, I guess.",
        "Traveling is definitely beneficial. It clearly enhances personal development and certainly broadens one's perspective.",
        "I believe that traveling has advantages. It probably helps with learning about different cultures, and it might improve communication skills."
    ]
    
    for i, text in enumerate(test_texts, 1):
        result = analyze_confidence_level(text)
        
        print(f"\n{'='*70}")
        print(f"TEST {i}: CONFIDENCE ANALYSIS")
        print(f"{'='*70}")
        print(f"\nText: {text}")
        print(f"\n🎯 Confidence Level: {result['confidence_level']} ({result['overall_confidence']}/10)")
        print(f"📝 Assessment: {result['assessment']}")
        print(f"\n🔍 Component Breakdown:")
        for component, score in result['components'].items():
            print(f"   {component.title()}: {score}/10")
        print(f"\n⏸️ Hesitation Analysis:")
        hesitation = result['hesitation_analysis']
        print(f"   Total Hesitations: {hesitation['total_hesitations']}")
        print(f"   Hesitation Rate: {hesitation['hesitation_rate_percent']}%")
        if hesitation['markers_found']:
            print(f"   Markers Found: {', '.join(m['marker'] for m in hesitation['markers_found'])}")
        print(f"\n💡 Recommendations:")
        for rec in result['recommendations']:
            print(f"   {rec}")
        print()
