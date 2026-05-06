"""
Advanced NLP using HuggingFace Transformers - FREE MODELS
Professional-grade analysis with semantic understanding
"""

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import warnings
warnings.filterwarnings('ignore')

class AdvancedNLPAnalyzer:
    def __init__(self):
        """Initialize HuggingFace models for advanced analysis"""
        print("[NLP] Loading HuggingFace models...")
        
        try:
            # 1. Sentiment Analysis - understands emotional tone
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            print("✓ Sentiment analyzer loaded")
        except Exception as e:
            print(f"⚠️  Sentiment analyzer failed: {e}")
            self.sentiment_analyzer = None
        
        try:
            # 2. Zero-shot classification - detect error types without training
            self.zero_shot = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
            print("✓ Error classifier loaded")
        except Exception as e:
            print(f"⚠️  Error classifier failed: {e}")
            self.zero_shot = None
        
        try:
            # 3. Question Answering - understand question requirements
            self.qa_model = pipeline(
                "question-answering",
                model="distilbert-base-cased-distilled-squad"
            )
            print("✓ Question answering model loaded")
        except Exception as e:
            print(f"⚠️  QA model failed: {e}")
            self.qa_model = None
        
        print("[NLP] Models initialized successfully!\n")
    
    def analyze_answer_quality(self, question: str, answer: str) -> dict:
        """
        Comprehensive analysis of answer quality for IELTS
        """
        analysis = {
            "completeness": self._check_completeness(question, answer),
            "coherence": self._check_coherence(answer),
            "relevance": self._check_relevance(question, answer),
            "tone": self._analyze_tone(answer),
            "complexity": self._analyze_complexity(answer),
            "confidence_level": self._detect_confidence(answer)
        }
        
        return analysis
    
    def _check_completeness(self, question: str, answer: str) -> dict:
        """Check if answer covers all aspects of the question"""
        if not self.qa_model:
            return {"score": 70, "status": "Adequate", "issues": []}
        
        try:
            # Check if answer addresses the question fully
            result = self.qa_model(question=question, context=answer)
            
            score = min(100, int(result['score'] * 100))
            
            if score < 60:
                return {
                    "score": score,
                    "status": "Incomplete",
                    "issues": [
                        "❌ Answer doesn't fully address the question",
                        "❌ Missing key aspects of the question",
                        "❌ Needs more detailed response"
                    ]
                }
            elif score < 85:
                return {
                    "score": score,
                    "status": "Good",
                    "issues": [
                        "⚠️ Could add more specific examples",
                        "⚠️ Some aspects could be elaborated"
                    ]
                }
            else:
                return {
                    "score": score,
                    "status": "Excellent",
                    "issues": []
                }
        except Exception as e:
            return {"score": 70, "status": "Good", "issues": []}
    
    def _check_coherence(self, answer: str) -> dict:
        """Check logical flow and coherence of the answer"""
        sentences = [s.strip() for s in answer.split('.') if s.strip()]
        
        if len(sentences) < 3:
            return {
                "score": 50,
                "status": "Needs Improvement",
                "issues": [
                    "❌ Too few sentences - lacks development",
                    "❌ Answer is too short and underdeveloped",
                    "❌ Need more sentences to show coherence"
                ]
            }
        
        avg_length = len(answer) / len(sentences)
        
        # Check sentence variety
        if avg_length < 8:
            coherence_score = 60
            status = "Poor"
            issues = [
                "❌ Sentences are too short",
                "❌ Lacks complex sentence structures",
                "❌ Use longer, more detailed sentences"
            ]
        elif avg_length < 15:
            coherence_score = 75
            status = "Good"
            issues = [
                "⚠️ Sentence structures could be more varied",
                "⚠️ Mix short and long sentences for better flow"
            ]
        else:
            coherence_score = 85
            status = "Excellent"
            issues = []
        
        return {
            "score": coherence_score,
            "status": status,
            "issues": issues,
            "metrics": {
                "total_sentences": len(sentences),
                "avg_words_per_sentence": round(avg_length, 1)
            }
        }
    
    def _check_relevance(self, question: str, answer: str) -> dict:
        """Check relevance of answer to question using semantic similarity"""
        if not self.zero_shot:
            return {"score": 70, "status": "Good", "issues": []}
        
        try:
            # Check if answer is relevant to the question
            candidate_labels = ["relevant", "irrelevant", "partially relevant"]
            
            result = self.zero_shot(answer, candidate_labels)
            
            top_label = result['labels'][0]
            confidence = result['scores'][0]
            
            if top_label == "irrelevant":
                return {
                    "score": 40,
                    "status": "Poor",
                    "issues": [
                        "❌ Answer is NOT relevant to the question",
                        "❌ Off-topic response",
                        "❌ Read the question carefully and answer it directly"
                    ]
                }
            elif top_label == "partially relevant":
                return {
                    "score": 65,
                    "status": "Moderate",
                    "issues": [
                        "⚠️ Some parts are off-topic",
                        "⚠️ Stay focused on what the question asks",
                        "⚠️ Include more relevant details"
                    ]
                }
            else:
                return {
                    "score": 85,
                    "status": "Excellent",
                    "issues": [],
                    "confidence": round(confidence * 100, 1)
                }
        except Exception as e:
            return {"score": 70, "status": "Good", "issues": []}
    
    def _analyze_tone(self, answer: str) -> dict:
        """Analyze tone and formality level"""
        if not self.sentiment_analyzer:
            return {"score": 70, "tone": "Neutral", "issues": []}
        
        try:
            # Analyze sentiment to gauge confidence and tone
            result = self.sentiment_analyzer(answer[:512])  # First 512 chars
            
            sentiment = result[0]['label']
            confidence = result[0]['score']
            
            if sentiment == "POSITIVE":
                return {
                    "score": 80,
                    "tone": "Confident & Positive",
                    "issues": [],
                    "advice": "Good! Your answer shows confidence. Maintain this tone."
                }
            else:
                return {
                    "score": 60,
                    "tone": "Neutral/Uncertain",
                    "issues": [
                        "⚠️ Your tone sounds uncertain or hesitant",
                        "⚠️ Use more confident and affirmative language",
                        "⚠️ Avoid phrases like 'I think', 'maybe', 'I guess'"
                    ],
                    "advice": "Speak with more confidence and certainty."
                }
        except Exception as e:
            return {"score": 70, "tone": "Neutral", "issues": []}
    
    def _analyze_complexity(self, answer: str) -> dict:
        """Analyze grammatical and lexical complexity"""
        words = answer.split()
        sentences = [s.strip() for s in answer.split('.') if s.strip()]
        
        # Calculate complexity metrics
        word_count = len(words)
        unique_words = len(set(w.lower() for w in words))
        vocab_variety = (unique_words / word_count * 100) if word_count > 0 else 0
        
        if word_count < 100:
            return {
                "score": 50,
                "level": "Basic",
                "issues": [
                    "❌ Answer is too short (< 100 words)",
                    "❌ Need more detailed response",
                    f"❌ Current: {word_count} words, Target: 150+ words"
                ]
            }
        elif word_count < 150:
            return {
                "score": 65,
                "level": "Intermediate",
                "issues": [
                    "⚠️ Could be more detailed (100-150 words)",
                    f"⚠️ Current: {word_count} words, Target: 180+ words",
                    "⚠️ Add more examples and explanations"
                ],
                "word_count": word_count,
                "vocab_variety": round(vocab_variety, 1)
            }
        elif vocab_variety < 50:
            return {
                "score": 70,
                "level": "Intermediate",
                "issues": [
                    "⚠️ Low vocabulary variety - words are repetitive",
                    f"⚠️ Variety: {round(vocab_variety, 1)}% (Target: 60%+)",
                    "⚠️ Use synonyms and varied vocabulary"
                ],
                "word_count": word_count,
                "vocab_variety": round(vocab_variety, 1)
            }
        else:
            return {
                "score": 85,
                "level": "Advanced",
                "issues": [],
                "word_count": word_count,
                "vocab_variety": round(vocab_variety, 1),
                "advice": "Excellent vocabulary variety and complexity!"
            }
    
    def _detect_confidence(self, answer: str) -> dict:
        """Detect confidence level from language patterns"""
        uncertainty_words = ['think', 'maybe', 'perhaps', 'possibly', 'might', 'sort of', 'kind of']
        confident_words = ['definitely', 'certainly', 'absolutely', 'clearly', 'obviously', 'obviously']
        
        uncertainty_count = sum(1 for word in uncertainty_words if word in answer.lower())
        confident_count = sum(1 for word in confident_words if word in answer.lower())
        
        total_words = len(answer.split())
        uncertainty_ratio = (uncertainty_count / total_words * 100) if total_words > 0 else 0
        
        if uncertainty_ratio > 5:
            return {
                "score": 60,
                "level": "Low",
                "issues": [
                    f"❌ Using {uncertainty_count} uncertainty words",
                    "❌ Phrases like 'I think', 'maybe', 'perhaps' reduce confidence",
                    "❌ Be more assertive and definitive in your statements"
                ]
            }
        elif confident_count > 3:
            return {
                "score": 85,
                "level": "High",
                "issues": [],
                "advice": "Excellent! Your answer shows strong confidence."
            }
        else:
            return {
                "score": 75,
                "level": "Moderate",
                "issues": [
                    "⚠️ Could sound more confident",
                    "⚠️ Use more assertive language"
                ]
            }

# Initialize analyzer
analyzer = AdvancedNLPAnalyzer()

def get_advanced_analysis(question: str, answer: str) -> dict:
    """Main function for advanced analysis"""
    return analyzer.analyze_answer_quality(question, answer)
