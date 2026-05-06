"""
ADVANCED PROFESSIONAL FEEDBACK GENERATOR
Generates detailed, professional IELTS feedback without APIs
Uses pre-trained language models and rule-based approaches
"""

from transformers import pipeline
import spacy

nlp = spacy.load("en_core_web_sm")

# Initialize summarizer for feedback generation
print("[FEEDBACK] Loading feedback generation model...")
try:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=-1)  # CPU mode
    print("✓ Feedback model loaded\n")
except Exception as e:
    print(f"⚠️  Warning: Could not load summarizer: {e}")
    print("   Install with: pip install transformers torch")
    summarizer = None


class ProfessionalFeedbackGenerator:
    """
    Generates professional IELTS feedback based on multiple metrics
    """
    
    def __init__(self):
        self.feedback_templates = {
            "grammar": {
                9: "Your grammar is exceptional with sophisticated structures used accurately throughout.",
                8: "Strong grammatical range with mostly accurate complex structures. Occasional minor errors.",
                7: "Generally good grammar with accurate use of complex structures, though some errors appear.",
                6: "Adequate grammar with some inaccuracies in complex structures.",
                5: "Grammar is basic with frequent errors in complex sentences.",
                4: "Significant grammar errors that sometimes impede communication."
            },
            "vocabulary": {
                9: "Lexical range is very sophisticated with precise and natural use of less common words.",
                8: "Good vocabulary range with appropriate use of less common words.",
                7: "Adequate vocabulary range with some less common words used appropriately.",
                6: "Sufficient vocabulary for the task with occasional inappropriateness.",
                5: "Limited vocabulary range affecting expression of ideas.",
                4: "Very limited vocabulary range restricting communication."
            },
            "fluency": {
                9: "Speech is effortlessly fluent with minimal hesitation and natural pausing.",
                8: "Fluent speech with only occasional hesitation or self-correction.",
                7: "Generally fluent with some repetition and hesitation.",
                6: "Fluent enough to communicate despite some hesitation.",
                5: "Speech is slow and repetitive with noticeable hesitation.",
                4: "Frequent hesitation and repetition affecting communication."
            },
            "coherence": {
                9: "Ideas are organized with complete clarity and logical progression.",
                8: "Well-organized and logical with clear connections between ideas.",
                7: "Generally well-organized with mostly clear progression.",
                6: "Adequately organized with some logical progression.",
                5: "Some organization but connections between ideas are unclear.",
                4: "Ideas are poorly organized and difficult to follow."
            }
        }
    
    def generate_strengths(self, scores: dict) -> list:
        """
        Generate list of strengths based on scores
        """
        strengths = []
        
        if scores.get('grammar_score', 0) >= 7:
            strengths.append("✅ Strong grammatical accuracy")
        
        if scores.get('vocabulary_score', 0) >= 7:
            strengths.append("✅ Good vocabulary range and selection")
        
        if scores.get('fluency_score', 0) >= 7:
            strengths.append("✅ Fluent and confident delivery")
        
        if scores.get('coherence_score', 0) >= 7:
            strengths.append("✅ Well-organized and coherent response")
        
        if scores.get('complexity_score', 0) >= 7:
            strengths.append("✅ Good sentence complexity and variation")
        
        if scores.get('idiom_count', 0) >= 2:
            strengths.append("✅ Appropriate use of idiomatic expressions")
        
        if not strengths:
            strengths.append("💡 Continue working on your English skills")
        
        return strengths
    
    def generate_areas_for_improvement(self, scores: dict, errors: dict) -> list:
        """
        Generate list of areas needing improvement
        """
        improvements = []
        
        if scores.get('grammar_score', 0) < 7:
            grammar_errors = errors.get('total_errors', 0)
            if grammar_errors > 5:
                improvements.append(f"⚠️ Grammar accuracy: {grammar_errors} errors detected - focus on subject-verb agreement and tenses")
            else:
                improvements.append("⚠️ Grammar accuracy: Work on complex sentence structures")
        
        if scores.get('vocabulary_score', 0) < 7:
            vocab_richness = scores.get('vocabulary_richness', 0)
            if vocab_richness < 0.4:
                improvements.append("⚠️ Vocabulary range: Use more varied and sophisticated vocabulary")
            else:
                improvements.append("⚠️ Vocabulary: Try to use less common but appropriate words")
        
        if scores.get('fluency_score', 0) < 7:
            filler_count = errors.get('filler_count', 0)
            if filler_count > 3:
                improvements.append(f"⚠️ Fluency: Reduce filler words (um, like, you know) - detected {filler_count}")
            else:
                improvements.append("⚠️ Fluency: Try to speak more smoothly with fewer pauses")
        
        if scores.get('coherence_score', 0) < 7:
            improvements.append("⚠️ Coherence: Use more linking words to connect ideas (however, furthermore, therefore)")
        
        if scores.get('complexity_score', 0) < 6:
            improvements.append("⚠️ Sentence complexity: Vary sentence structures more - combine ideas with conjunctions")
        
        if scores.get('band_estimate_from_idioms', 0) < 5:
            improvements.append("⚠️ Expression: Incorporate more phrasal verbs and idioms naturally")
        
        return improvements
    
    def generate_specific_feedback(self, scores: dict, errors: dict, text: str) -> dict:
        """
        Generate specific, actionable feedback
        """
        feedback_sections = {}
        
        # Grammar feedback
        grammar_level = min(9, max(1, int(scores.get('grammar_score', 5))))
        feedback_sections['grammar'] = {
            "score": scores.get('grammar_score', 0),
            "feedback": self.feedback_templates['grammar'].get(grammar_level, "Keep practicing grammar."),
            "issues": errors.get('error_summary', [])[:3]  # Top 3 errors
        }
        
        # Vocabulary feedback
        vocab_level = min(9, max(1, int(scores.get('vocabulary_score', 5))))
        feedback_sections['vocabulary'] = {
            "score": scores.get('vocabulary_score', 0),
            "feedback": self.feedback_templates['vocabulary'].get(vocab_level, "Expand your vocabulary."),
            "richness": scores.get('vocabulary_richness', 0)
        }
        
        # Fluency feedback
        fluency_level = min(9, max(1, int(scores.get('fluency_score', 5))))
        feedback_sections['fluency'] = {
            "score": scores.get('fluency_score', 0),
            "feedback": self.feedback_templates['fluency'].get(fluency_level, "Work on fluency."),
            "filler_words": errors.get('filler_count', 0)
        }
        
        # Coherence feedback
        coherence_level = min(9, max(1, int(scores.get('coherence_score', 5))))
        feedback_sections['coherence'] = {
            "score": scores.get('coherence_score', 0),
            "feedback": self.feedback_templates['coherence'].get(coherence_level, "Improve coherence."),
            "transitions": errors.get('discourse_markers', 0)
        }
        
        return feedback_sections
    
    def generate_band_breakdown(self, band: float) -> dict:
        """
        Generate detailed band score breakdown and achievement
        """
        if band >= 8.5:
            level = "Expert"
            description = "Demonstrates complete control with sophisticated use of language"
            tips = [
                "Maintain your excellent level",
                "Focus on even more sophisticated vocabulary and complex structures",
                "Record yourself and listen for any areas of improvement"
            ]
        elif band >= 8:
            level = "Very Good"
            description = "Demonstrates strong control with effective use of complex structures"
            tips = [
                "Continue using sophisticated vocabulary and structures",
                "Work on consistency - avoid occasional lapses",
                "Add more varied sentence patterns"
            ]
        elif band >= 7:
            level = "Good"
            description = "Demonstrates good command of English with mostly accurate use"
            tips = [
                "Work on using more complex grammatical structures",
                "Expand vocabulary with synonyms and less common words",
                "Reduce filler words and hesitations"
            ]
        elif band >= 6:
            level = "Competent"
            description = "Demonstrates adequate command of English"
            tips = [
                "Practice using complex sentence structures",
                "Learn and use more academic vocabulary",
                "Focus on speaking fluently with fewer pauses"
            ]
        else:
            level = "Modest/Limited"
            description = "Demonstrates basic command of English with noticeable errors"
            tips = [
                "Focus on fundamental grammar rules (tenses, agreement, word order)",
                "Build vocabulary with common phrases and expressions",
                "Practice speaking clearly and confidently"
            ]
        
        return {
            "band": band,
            "level": level,
            "description": description,
            "tips": tips
        }
    
    def generate_full_report(self, scores: dict, errors: dict, text: str) -> dict:
        """
        Generate comprehensive feedback report
        """
        overall_band = scores.get('overall_score', 0) * 0.9 + 0.5  # Approximate conversion
        
        report = {
            "overall_band": round(min(9, max(0, overall_band)), 1),
            "overall_score": scores.get('overall_score', 0),
            "strengths": self.generate_strengths(scores),
            "areas_for_improvement": self.generate_areas_for_improvement(scores, errors),
            "detailed_feedback": self.generate_specific_feedback(scores, errors, text),
            "band_breakdown": self.generate_band_breakdown(overall_band),
            "action_plan": self._generate_action_plan(overall_band, scores),
            "sample_corrections": self._generate_corrections(errors)
        }
        
        return report
    
    def _generate_action_plan(self, band: float, scores: dict) -> list:
        """
        Generate personalized action plan for improvement
        """
        plan = []
        
        if band < 6:
            plan = [
                "1. Focus on basic grammar and sentence structure",
                "2. Build everyday vocabulary (300-500 words)",
                "3. Practice speaking at normal pace",
                "4. Listen to English content (podcasts, videos)",
                "5. Record yourself speaking and identify errors"
            ]
        elif band < 7:
            plan = [
                "1. Practice using complex sentence structures",
                "2. Learn academic and less common vocabulary",
                "3. Work on fluency - reduce hesitation",
                "4. Use linking words to connect ideas",
                "5. Practice with different question types"
            ]
        else:
            plan = [
                "1. Maintain current level while targeting Band 8",
                "2. Use sophisticated vocabulary and expressions",
                "3. Practice varied sentence structures",
                "4. Reduce any remaining errors",
                "5. Work on natural, confident delivery"
            ]
        
        return plan
    
    def _generate_corrections(self, errors: dict) -> list:
        """
        Generate sample corrections for common errors
        """
        corrections = []
        
        grammar_errors = errors.get('errors', [])[:2]  # Top 2 errors
        
        for error in grammar_errors:
            original = error.get('original', '')
            suggestions = error.get('suggestions', [])
            if suggestions:
                corrections.append({
                    "error": original,
                    "correction": suggestions[0],
                    "reason": error.get('message', 'Grammar correction')
                })
        
        return corrections


def generate_professional_feedback(scores: dict, errors: dict, text: str) -> dict:
    """
    Main function to generate professional feedback
    """
    generator = ProfessionalFeedbackGenerator()
    report = generator.generate_full_report(scores, errors, text)
    
    return report


if __name__ == "__main__":
    # Example usage
    test_scores = {
        'overall_score': 7.2,
        'grammar_score': 7.0,
        'vocabulary_score': 7.5,
        'fluency_score': 6.8,
        'coherence_score': 7.3,
        'complexity_score': 6.9,
        'band_estimate_from_idioms': 7.0,
        'vocabulary_richness': 0.55
    }
    
    test_errors = {
        'total_errors': 3,
        'filler_count': 2,
        'discourse_markers': 4,
        'error_summary': ["Subject-verb agreement", "Tense inconsistency"],
        'errors': [
            {
                'original': 'She go',
                'suggestions': ['She goes'],
                'message': 'Third person singular'
            }
        ]
    }
    
    test_text = "She go to school every day. I think traveling is very important because you learn about different cultures."
    
    feedback = generate_professional_feedback(test_scores, test_errors, test_text)
    
    print("\n" + "="*70)
    print("PROFESSIONAL IELTS FEEDBACK REPORT")
    print("="*70)
    print(f"\n🎯 Overall Band: {feedback['overall_band']}")
    print(f"📊 Overall Score: {feedback['overall_score']}/10")
    print(f"\n✨ Strengths:")
    for strength in feedback['strengths']:
        print(f"   {strength}")
    print(f"\n⚠️ Areas for Improvement:")
    for improvement in feedback['areas_for_improvement']:
        print(f"   {improvement}")
    print(f"\n📋 Band Description:")
    band_info = feedback['band_breakdown']
    print(f"   Level: {band_info['level']}")
    print(f"   Description: {band_info['description']}")
    print(f"\n💡 Tips for Next Level:")
    for tip in band_info['tips']:
        print(f"   - {tip}")
    print(f"\n📝 Action Plan:")
    for action in feedback['action_plan']:
        print(f"   {action}")
    print("\n" + "="*70 + "\n")
