"""
Response Suggestions - Help candidates give better answers
"""
from typing import Dict, List
import re

class ResponseSuggestions:
    def __init__(self):
        # Question-specific response templates for IELTS
        self.response_templates = {
            "Tell me about yourself": {
                "structure": [
                    "1. Name & Origin: 'My name is... I'm from...'",
                    "2. Education: 'I studied... at...'",
                    "3. Current Job: 'Currently, I work as...'",
                    "4. Interests: 'I'm interested in...'",
                    "5. Future: 'I hope to...'"
                ],
                "example": "My name is Ahmed and I'm from Pakistan. I studied computer science at COMSATS. Currently, I work as a software developer. I'm very interested in AI and machine learning. In the future, I hope to lead a tech team.",
                "keywords": ["name", "from", "studied", "work", "interested", "future"],
                "tips": [
                    "Speak naturally and conversationally",
                    "Give specific details, not just general statements",
                    "Use present and past tenses appropriately",
                    "Keep it to 1-1.5 minutes",
                    "Maintain good eye contact (if on video)"
                ]
            },
            "What do you like to do in your free time": {
                "structure": [
                    "1. Main hobby: 'I really enjoy... because...'",
                    "2. Frequency: 'I do this... times per week/month'",
                    "3. Why you like it: 'It helps me to... / It makes me feel...'",
                    "4. With whom: 'I usually do it... (alone/with friends/family)'",
                    "5. Duration: 'I've been doing this for... years/months'"
                ],
                "example": "I really enjoy playing badminton because it keeps me fit and active. I play about 3 times a week at a local club. It helps me relieve stress after work. I usually do it with my colleagues, and we've been playing together for the past 2 years.",
                "keywords": ["hobby", "enjoy", "enjoy", "spend", "time", "interested"],
                "tips": [
                    "Use specific examples, not vague hobbies",
                    "Explain why you like it",
                    "Use present simple tense",
                    "Mention frequency specific dates/times",
                    "Show enthusiasm in your voice"
                ]
            },
            "Describe a book you have read": {
                "structure": [
                    "1. Title & Author: 'The book is... by...'",
                    "2. What it's about: 'It's about... The main character is...'",
                    "3. Plot highlights: 'The story follows... and then...'",
                    "4. Why you liked it: 'I enjoyed it because...'",
                    "5. Recommendation: 'I would recommend it to... because...'"
                ],
                "example": "The book is '1984' by George Orwell. It's about a dystopian society where the government controls everything. The main character is Winston Smith, who works for the government. The story follows his attempt to rebel, though it ends tragically. I enjoyed it because it explores important themes about freedom and identity. I would recommend it to anyone interested in political fiction.",
                "keywords": ["book", "read", "author", "story", "character", "enjoyed"],
                "tips": [
                    "Structure: Title → Author → Plot → Why you liked it",
                    "Use past tense for the story",
                    "Mention specific character names and events",
                    "Speak for 1.5-2 minutes",
                    "Explain the significance of the book"
                ]
            }
        }
        
        # Common mistakes and corrections
        self.common_mistakes = {
            "lack_of_structure": "Your answer needs better organization. Follow: Introduction → Details → Conclusion",
            "too_vague": "Your answer is too general. Add specific examples, dates, names, or numbers.",
            "short_answer": "Your answer is too short. Aim for at least 1 minute (150+ words).",
            "no_examples": "You didn't provide any examples. IELTS examiners want to hear specific stories.",
            "poor_grammar": "Your answer has grammar issues. Use correct tenses and sentence structures.",
            "no_enthusiasm": "Your answer sounds monotone. Show enthusiasm through vocabulary and tone of voice.",
        }
    
    def get_suggestions_for_question(self, question: str, user_answer: str) -> Dict:
        """
        Get suggestions based on the question and user's answer
        """
        # Find matching question template
        best_match = None
        best_score = 0
        
        for template_q in self.response_templates.keys():
            score = self._similarity_score(question, template_q)
            if score > best_score:
                best_score = score
                best_match = template_q
        
        if best_match and best_score > 0.3:
            template = self.response_templates[best_match]
            return {
                "suggested_structure": template["structure"],
                "example_answer": template["example"],
                "example_keywords": template["keywords"],
                "tips": template["tips"],
                "analysis": self._analyze_user_answer(user_answer, template)
            }
        
        return {"tips": ["Follow IELTS speaking guidelines: be specific, use examples, vary your vocabulary"]}
    
    def _similarity_score(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union if union > 0 else 0
    
    def _analyze_user_answer(self, answer: str, template: Dict) -> Dict:
        """
        Analyze user's answer against the template structure
        """
        issues = []
        word_count = len(answer.split())
        
        if word_count < 50:
            issues.append("❌ Too short - Aim for at least 150+ words")
        
        # Check if answer contains keywords from template
        keywords = template.get('keywords', [])
        found_keywords = sum(1 for kw in keywords if kw.lower() in answer.lower())
        
        if found_keywords < len(keywords) * 0.5:
            issues.append(f"⚠️ Missing important keywords: {', '.join([kw for kw in keywords if kw.lower() not in answer.lower()])}")
        
        # Check for specific details
        if not re.search(r'\d+', answer):  # No numbers/dates
            issues.append("📊 Add specific numbers, dates, or statistics")
        
        # Check for examples
        if 'example' not in answer.lower() and 'such as' not in answer.lower() and 'like' not in answer.lower():
            issues.append("📚 Add specific examples to support your points")
        
        # Check sentence length
        sentences = re.split(r'[.!?]+', answer)
        avg_len = sum(len(s.split()) for s in sentences) / max(1, len(sentences))
        if avg_len < 8:
            issues.append("📝 Use longer sentences with complex structures")
        
        positive = []
        if word_count > 150:
            positive.append("✅ Good length - Covers sufficient content")
        if found_keywords >= len(keywords) * 0.7:
            positive.append("✅ Covers key aspects of the question")
        if len(sentences) > 3:
            positive.append("✅ Good variety in sentence structures")
        
        return {
            "word_count": word_count,
            "strengths": positive,
            "improvements": issues
        }
    
    def get_score_tips(self, current_score: float) -> List[str]:
        """
        Tips to improve score based on current performance
        """
        tips = []
        
        if current_score < 40:
            tips = [
                "❌ VERY LOW - Your answer needs major improvements",
                "1️⃣ Start with a clear introduction",
                "2️⃣ Add specific examples with details",
                "3️⃣ Use a variety of sentence structures",
                "4️⃣ Practice speaking for 1-2 minutes continuously",
                "💡 Tip: Record yourself and listen for filler words and pronunciation issues"
            ]
        elif current_score < 60:
            tips = [
                "⚠️ BELOW AVERAGE - Good start, but needs improvement",
                "1️⃣ Organize your answer better - Introduction, Details, Conclusion",
                "2️⃣ Use more specific examples and details",
                "3️⃣ Expand on why/how, not just what",
                "4️⃣ Vary your vocabulary - avoid repetition",
                "💡 Tip: Use transitional phrases like 'Moreover', 'Therefore', 'In addition'"
            ]
        elif current_score < 75:
            tips = [
                "✓ GOOD - Continue improving for excellence",
                "1️⃣ Add more complex sentence structures",
                "2️⃣ Include more specific dates, numbers, or proper nouns",
                "3️⃣ Show more enthusiasm and personality",
                "4️⃣ Use phrasal verbs and idioms appropriately",
                "5️⃣ Ensure perfect pronunciation and intonation",
                "💡 Tip: Native-like fluency requires practice - aim for 2+ minutes per answer"
            ]
        else:
            tips = [
                "🌟 EXCELLENT - You're on the right track!",
                "1️⃣ Maintain this consistent level across all questions",
                "2️⃣ Focus on minor pronunciation refinements",
                "3️⃣ Continue using sophisticated vocabulary",
                "4️⃣ Practice to achieve IELTS Band 7.5-8.0",
                "💡 Tip: Record all your practice sessions and analyze them"
            ]
        
        return tips

# Initialize suggestions
suggester = ResponseSuggestions()

def get_better_response_suggestions(question: str, user_answer: str) -> Dict:
    """
    Main function to get response suggestions
    """
    suggestions = suggester.get_suggestions_for_question(question, user_answer)
    return suggestions

def get_score_improvement_tips(score: float) -> List[str]:
    """
    Get tips to improve score
    """
    return suggester.get_score_tips(score)
