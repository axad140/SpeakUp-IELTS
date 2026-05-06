"""
Comprehensive IELTS Speaking Score Calculation
IELTS Bands: 0-9 (with 0.5 increments)
"""
from typing import Dict, List
import re

class IELTSScorer:
    def __init__(self):
        # IELTS Band Descriptors (simplified)
        self.band_descriptors = {
            9: {"range": [90, 100], "label": "Expert", "description": "Fully realizes the linguistic potential of the task"},
            8.5: {"range": [85, 89], "label": "Very Good", "description": "Demonstrates robust and sustained ability"},
            8: {"range": [80, 84], "label": "Very Good", "description": "Handles complex language with ease"},
            7.5: {"range": [75, 79], "label": "Good", "description": "Shows good control with minor lapses"},
            7: {"range": [70, 74], "label": "Good", "description": "Shows flexibility and appropriate use"},
            6.5: {"range": [65, 69], "label": "Competent", "description": "Generally accurate with some errors"},
            6: {"range": [60, 64], "label": "Competent", "description": "Generally effective communication"},
            5.5: {"range": [55, 59], "label": "Modest", "description": "Generally makes simple statements"},
            5: {"range": [50, 54], "label": "Modest", "description": "Handles simple communication"},
            4.5: {"range": [45, 49], "label": "Limited", "description": "Basic communication attempts"},
            4: {"range": [40, 44], "label": "Limited", "description": "Produces basic language"},
            0: {"range": [0, 39], "label": "Extremely Limited", "description": "Fails to use language"}
        }
    
    def calculate_ielts_band(self, 
                            grammar_score: float,
                            fluency_score: float,
                            vocabulary_score: float,
                            pronunciation_score: float = 70,
                            coherence_score: float = None) -> Dict:
        """
        Calculate IELTS band based on four criteria:
        1. Grammatical Range & Accuracy
        2. Fluency & Coherence
        3. Lexical Resource (Vocabulary)
        4. Pronunciation
        """
        
        # Weighted average (IELTS uses equal weighting)
        if coherence_score is None:
            coherence_score = fluency_score
        
        overall_score = (grammar_score + fluency_score + vocabulary_score + pronunciation_score) / 4
        
        # Find matching band
        band = self._get_band_from_score(overall_score)
        
        return {
            "overall_score": round(overall_score, 1),
            "ielts_band": band["label"],
            "band_number": band["number"],
            "band_description": band["description"],
            "breakdown": {
                "grammar": round(grammar_score, 1),
                "fluency": round(fluency_score, 1),
                "vocabulary": round(vocabulary_score, 1),
                "pronunciation": round(pronunciation_score, 1),
                "coherence": round(coherence_score, 1)
            },
            "next_band_gap": band.get("gap_to_next", 0),
            "recommendation": self._get_band_recommendation(band["number"]),
            "strengths": self._identify_strengths(grammar_score, fluency_score, vocabulary_score, pronunciation_score),
            "weaknesses": self._identify_weaknesses(grammar_score, fluency_score, vocabulary_score, pronunciation_score)
        }
    
    def _get_band_from_score(self, score: float) -> Dict:
        """
        Convert numeric score to IELTS band
        """
        bands = [
            (90, 100, 9.0, "Expert"),
            (85, 89, 8.5, "Very Good"),
            (80, 84, 8.0, "Very Good"),
            (75, 79, 7.5, "Good"),
            (70, 74, 7.0, "Good"),
            (65, 69, 6.5, "Competent"),
            (60, 64, 6.0, "Competent"),
            (55, 59, 5.5, "Modest"),
            (50, 54, 5.0, "Modest"),
            (45, 49, 4.5, "Limited"),
            (40, 44, 4.0, "Limited"),
            (0, 39, 0.0, "Extremely Limited")
        ]
        
        for min_score, max_score, band_num, label in bands:
            if min_score <= score <= max_score:
                gap = 80 - score if score < 80 else 0
                return {
                    "number": band_num,
                    "label": label,
                    "description": self.band_descriptors.get(band_num, {}).get("description", ""),
                    "gap_to_next": gap
                }
        
        return {
            "number": 0.0,
            "label": "Extremely Limited",
            "description": "Fails to use language",
            "gap_to_next": 100
        }
    
    def _identify_strengths(self, grammar: float, fluency: float, vocabulary: float, pronunciation: float) -> List[str]:
        """
        Identify strongest areas
        """
        strengths = []
        
        if grammar > 75:
            strengths.append("✅ Strong grammar and sentence accuracy")
        if fluency > 75:
            strengths.append("✅ Good fluency and natural speech flow")
        if vocabulary > 75:
            strengths.append("✅ Excellent vocabulary and word choice")
        if pronunciation > 75:
            strengths.append("✅ Clear pronunciation and stress patterns")
        
        if not strengths:
            strengths.append("💡 Keep practicing - all areas need improvement")
        
        return strengths
    
    def _identify_weaknesses(self, grammar: float, fluency: float, vocabulary: float, pronunciation: float) -> List[str]:
        """
        Identify weakest areas
        """
        weaknesses = []
        
        if grammar < 65:
            weaknesses.append("⚠️ Grammar - Focus on tense consistency and complex sentences")
        if fluency < 65:
            weaknesses.append("⚠️ Fluency - Practice speaking smoothly without filler words")
        if vocabulary < 65:
            weaknesses.append("⚠️ Vocabulary - Learn and use more sophisticated words")
        if pronunciation < 65:
            weaknesses.append("⚠️ Pronunciation - Work on accent and word stress")
        
        return weaknesses
    
    def _get_band_recommendation(self, band: float) -> str:
        """
        Get recommendation based on band score
        """
        recommendations = {
            9.0: "🌟 Excellent! You've achieved near-perfect IELTS Speaking.",
            8.5: "🎯 Outstanding! You're at a very competitive level.",
            8.0: "💪 Excellent! You can apply to top universities worldwide.",
            7.5: "✨ Very good! Most programs worldwide accept this score.",
            7.0: "👍 Good! You meet requirements for most Canadian/Australian universities.",
            6.5: "💼 Acceptable for many programs, but not top tier.",
            6.0: "📚 Basic competency - Keep improving for better opportunities.",
            5.5: "🔄 Needs improvement - Focus on grammar and fluency.",
            5.0: "⚡ Significant improvement needed - Consider intensive practice.",
            4.5: "🚀 Major work required - Start with fundamentals.",
            4.0: "🎓 Please practice basic English skills.",
            0.0: "💬 Need to restart learning process."
        }
        
        return recommendations.get(float(int(band * 2) / 2), "Keep practicing!")

# Initialize scorer
scorer = IELTSScorer()

def get_ielts_band_score(grammar_score: float, 
                         fluency_score: float, 
                         vocabulary_score: float,
                         pronunciation_score: float = 70) -> Dict:
    """
    Main function to calculate IELTS band
    """
    return scorer.calculate_ielts_band(grammar_score, fluency_score, vocabulary_score, pronunciation_score)
