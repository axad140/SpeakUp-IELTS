"""
Professional Weakness Detection - IELTS Standards Compliance
Identifies specific weak points in speaking performance
"""

import re
from typing import List, Dict

class WeaknessDetector:
    def __init__(self):
        # IELTS Band Criteria for weighting weaknesses
        self.band_criteria = {
            "grammar": {
                "Band 7-9": "Uses a wide range of structures with high accuracy",
                "Band 6-7": "Uses a mix of simple and complex sentences",
                "Band 5-6": "Primarily simple sentences with some errors",
                "Band 4-5": "Limited structures with frequent errors",
                "Band 0-4": "Very limited range with many errors"
            },
            "fluency": {
                "Band 7-9": "Speaks fluently with minimal pauses",
                "Band 6-7": "Generally fluent with occasional pauses",
                "Band 5-6": "Some pauses and hesitations",
                "Band 4-5": "Frequently pauses and hesitates",
                "Band 0-4": "Unable to sustain fluency"
            },
            "vocabulary": {
                "Band 7-9": "Uses sophisticated vocabulary accurately",
                "Band 6-7": "Uses varied vocabulary appropriately",
                "Band 5-6": "Uses some varied vocabulary but limited range",
                "Band 4-5": "Limited vocabulary with repetition",
                "Band 0-4": "Very limited vocabulary"
            },
            "pronunciation": {
                "Band 7-9": "Intelligible with sophisticated intonation",
                "Band 6-7": "Clear with appropriate intonation",
                "Band 5-6": "Generally clear but some errors",
                "Band 4-5": "Difficult to understand in places",
                "Band 0-4": "Frequently unintelligible"
            }
        }
        
        self.weakness_severity_levels = {
            "critical": {"min": 0, "max": 40, "label": "Critical - Needs immediate improvement"},
            "high": {"min": 40, "max": 60, "label": "High - Major improvement needed"},
            "medium": {"min": 60, "max": 75, "label": "Medium - Some improvement needed"},
            "low": {"min": 75, "max": 85, "label": "Low - Minor improvement"},
            "excellent": {"min": 85, "max": 100, "label": "Excellent - No improvement needed"}
        }
    
    def detect_all_weaknesses(self, question: str, answer: str, 
                             grammar_score: float, fluency_score: float,
                             vocabulary_score: float, pronunciation_score: float) -> Dict:
        """
        Comprehensive weakness detection across all IELTS criteria
        """
        weaknesses = {
            "grammar": self._detect_grammar_weaknesses(answer, grammar_score),
            "fluency": self._detect_fluency_weaknesses(answer, fluency_score),
            "vocabulary": self._detect_vocabulary_weaknesses(answer, vocabulary_score),
            "pronunciation": self._detect_pronunciation_weaknesses(answer, pronunciation_score),
            "question_coverage": self._detect_question_coverage_issues(question, answer)
        }
        
        # Overall weakness summary
        total_score = (grammar_score + fluency_score + vocabulary_score + pronunciation_score) / 4
        weaknesses["overall_severity"] = self._get_severity_level(total_score)
        weaknesses["critical_areas"] = self._identify_critical_areas(weaknesses)
        
        return weaknesses
    
    def _detect_grammar_weaknesses(self, answer: str, score: float) -> Dict:
        """Identify specific grammar weaknesses"""
        issues = []
        
        # 1. Subject-Verb Agreement
        sv_errors = self._check_subject_verb_agreement(answer)
        if sv_errors:
            issues.extend(sv_errors)
        
        # 2. Tense Consistency
        tense_errors = self._check_tense_consistency(answer)
        if tense_errors:
            issues.extend(tense_errors)
        
        # 3. Article Usage
        article_errors = self._check_article_usage(answer)
        if article_errors:
            issues.extend(article_errors)
        
        # 4. Preposition Errors
        prep_errors = self._check_preposition_errors(answer)
        if prep_errors:
            issues.extend(prep_errors)
        
        # 5. Sentence Fragments
        fragment_errors = self._check_sentence_fragments(answer)
        if fragment_errors:
            issues.extend(fragment_errors)
        
        return {
            "score": score,
            "severity": self._get_severity_level(score),
            "issues": issues[:5],  # Top 5 issues
            "total_issues": len(issues),
            "band_target": self._get_band_target(score, "grammar")
        }
    
    def _detect_fluency_weaknesses(self, answer: str, score: float) -> Dict:
        """Identify specific fluency weaknesses"""
        issues = []
        
        sentences = [s.strip() for s in answer.split('.') if s.strip()]
        
        if len(sentences) < 2:
            issues.append({
                "issue": "❌ CRITICAL: Too few sentences for fluent speech",
                "advice": f"You used only {len(sentences)} sentence(s). IELTS requires 4+ sentences.",
                "impact": "HIGH"
            })
        
        # 1. Sentence Variety
        if self._low_sentence_variety(sentences):
            issues.append({
                "issue": "❌ Low sentence variety",
                "advice": "Mix simple and complex sentences for better fluency",
                "impact": "HIGH"
            })
        
        # 2. Filler Words
        filler_count = self._count_filler_words(answer)
        if filler_count > 2:
            issues.append({
                "issue": f"❌ Too many filler words ({filler_count} found)",
                "advice": "Reduce 'um', 'like', 'basically', 'actually' - these break fluency",
                "impact": "HIGH"
            })
        
        # 3. Repetition of Words
        repeated_words = self._find_word_repetition(answer)
        if repeated_words:
            issues.append({
                "issue": f"❌ Excessive word repetition",
                "advice": f"Repeated words: {', '.join(repeated_words)}. Use synonyms instead.",
                "impact": "MEDIUM"
            })
        
        # 4. Connector Usage
        if not self._has_good_connectors(answer):
            issues.append({
                "issue": "❌ Missing linking words",
                "advice": "Use: however, therefore, moreover, furthermore, meanwhile, etc.",
                "impact": "MEDIUM"
            })
        
        return {
            "score": score,
            "severity": self._get_severity_level(score),
            "issues": issues[:5],
            "total_issues": len(issues),
            "band_target": self._get_band_target(score, "fluency"),
            "metrics": {
                "sentence_count": len(sentences),
                "filler_words": filler_count,
                "connector_usage": self._count_connectors(answer)
            }
        }
    
    def _detect_vocabulary_weaknesses(self, answer: str, score: float) -> Dict:
        """Identify specific vocabulary weaknesses"""
        issues = []
        
        words = answer.lower().split()
        unique_words = set(words)
        
        # 1. Limited Vocabulary Range
        if len(unique_words) / len(words) < 0.5:
            issues.append({
                "issue": "❌ Vocabulary repetition - limited range",
                "advice": f"Only {len(unique_words)} unique words out of {len(words)}. Use more synonyms.",
                "impact": "HIGH"
            })
        
        # 2. Weak Vocabulary Choices
        weak_words = ['good', 'bad', 'nice', 'thing', 'very', 'a lot', 'get', 'put']
        found_weak = [w for w in weak_words if w in answer.lower()]
        if found_weak:
            issues.append({
                "issue": f"❌ Using basic/weak vocabulary: {', '.join(found_weak)}",
                "advice": "Replace with: excellent, poor, pleasant, aspect, extremely, numerous, obtain, place",
                "impact": "MEDIUM"
            })
        
        # 3. Lack of Advanced Vocabulary
        advanced_words = ['nevertheless', 'consequently', 'subsequently', 'particularly', 'significantly']
        found_advanced = sum(1 for w in advanced_words if w in answer.lower())
        if found_advanced == 0 and len(words) > 100:
            issues.append({
                "issue": "❌ No advanced vocabulary detected",
                "advice": "For higher bands, use sophisticated words: nevertheless, consequently, particularly, etc.",
                "impact": "MEDIUM"
            })
        
        # 4. Topic-Specific Vocabulary
        if score < 70:
            issues.append({
                "issue": "❌ Lack of topic-specific vocabulary",
                "advice": "Use words directly related to the topic for better relevance",
                "impact": "MEDIUM"
            })
        
        return {
            "score": score,
            "severity": self._get_severity_level(score),
            "issues": issues[:5],
            "total_issues": len(issues),
            "word_count": len(words),
            "unique_words": len(unique_words),
            "vocabulary_ratio": round(len(unique_words) / len(words) * 100, 1),
            "band_target": self._get_band_target(score, "vocabulary")
        }
    
    def _detect_pronunciation_weaknesses(self, answer: str, score: float) -> Dict:
        """Identify pronunciation/delivery weaknesses"""
        issues = []
        
        # Since we can't test actual pronunciation, we use proxy indicators
        
        # 1. No contractions (indicates unnatural speech)
        contractions = ["can't", "won't", "don't", "isn't", "aren't", "doesn't"]
        contraction_count = sum(1 for c in contractions if c in answer.lower())
        
        if contraction_count == 0 and len(answer) > 100:
            issues.append({
                "issue": "❌ No contractions used - speech sounds unnatural",
                "advice": "Use natural contractions: can't, won't, don't, isn't, etc.",
                "impact": "MEDIUM"
            })
        
        # 2. Overly complex words
        if score < 65:
            issues.append({
                "issue": "❌ Pronunciation may be difficult",
                "advice": "Use clearer, simpler words. Test pronunciation of complex words.",
                "impact": "MEDIUM"
            })
        
        # 3. Speech clarity indicators
        unclear_patterns = ['idk', 'u ', 'ur ', 'gonna', 'wanna', 'innit']
        unclear_count = sum(1 for p in unclear_patterns if p in answer.lower())
        
        if unclear_count > 0:
            issues.append({
                "issue": f"❌ Informal/unclear speech patterns detected",
                "advice": "Use formal English: 'I don't know', 'your', 'going to', 'want to', etc.",
                "impact": "HIGH"
            })
        
        return {
            "score": score,
            "severity": self._get_severity_level(score),
            "issues": issues[:5],
            "total_issues": len(issues),
            "band_target": self._get_band_target(score, "pronunciation")
        }
    
    def _detect_question_coverage_issues(self, question: str, answer: str) -> Dict:
        """Check if answer properly addresses the question"""
        issues = []
        
        question_words = set(question.lower().split())
        answer_words = set(answer.lower().split())
        
        coverage = len(question_words & answer_words) / len(question_words)
        
        if coverage < 0.4:
            issues.append({
                "issue": "❌ CRITICAL: Answer doesn't address the question properly",
                "advice": "Read the question again. Your answer must directly answer what is asked.",
                "impact": "CRITICAL"
            })
        
        return {
            "coverage_score": round(coverage * 100, 1),
            "issues": issues,
            "severity": "critical" if coverage < 0.4 else "low"
        }
    
    # Helper Methods
    
    def _check_subject_verb_agreement(self, answer: str) -> List[Dict]:
        errors = []
        # Simplified check - look for patterns like "he are", "she have"
        patterns = [
            (r'\b(he|she|it)\s+(are|have|were|do)\b', "Subject-Verb Agreement"),
            (r'\b(I|you|we|they)\s+(is|has|was)\b', "Subject-Verb Agreement"),
        ]
        
        for pattern, error_type in patterns:
            if re.search(pattern, answer, re.IGNORECASE):
                errors.append({
                    "issue": f"❌ {error_type} error detected",
                    "advice": "Singular subjects need singular verbs, plural subjects need plural verbs",
                    "impact": "HIGH"
                })
        
        return errors
    
    def _check_tense_consistency(self, answer: str) -> List[Dict]:
        errors = []
        
        past_tense_words = ['was', 'were', 'had', 'went', 'studied', 'did']
        present_tense_words = ['is', 'are', 'have', 'go', 'study', 'do']
        
        past_count = sum(1 for word in past_tense_words if word in answer.lower())
        present_count = sum(1 for word in present_tense_words if word in answer.lower())
        
        if past_count > 0 and present_count > 3:
            errors.append({
                "issue": "❌ Tense inconsistency - mixing past and present",
                "advice": "Keep a consistent tense throughout your answer (usually present or past)",
                "impact": "HIGH"
            })
        
        return errors
    
    def _check_article_usage(self, answer: str) -> List[Dict]:
        errors = []
        
        # Check for missing articles
        if re.search(r'\b[aeiou]\w+\b(?!\s+[aeiou])', answer):
            if answer.count('a ') + answer.count('an ') + answer.count('the ') < len(answer.split()) * 0.1:
                errors.append({
                    "issue": "❌ Article usage errors - missing 'a', 'an', or 'the'",
                    "advice": "Use articles correctly: 'a/an' before consonants/vowels, 'the' for specific nouns",
                    "impact": "MEDIUM"
                })
        
        return errors
    
    def _check_preposition_errors(self, answer: str) -> List[Dict]:
        errors = []
        
        wrong_prepositions = [
            (r'in morning', 'in the morning'),
            (r'on evening', 'in the evening'),
            (r'at day', 'during the day'),
            (r'at night', 'at night'),  # This is correct
        ]
        
        for wrong, correct in wrong_prepositions:
            if re.search(wrong, answer, re.IGNORECASE):
                errors.append({
                    "issue": f"❌ Preposition error: '{wrong}' should be '{correct}'",
                    "advice": f"Use '{correct}' instead of '{wrong}'",
                    "impact": "MEDIUM"
                })
        
        return errors
    
    def _check_sentence_fragments(self, answer: str) -> List[Dict]:
        errors = []
        
        sentences = [s.strip() for s in answer.split('.') if s.strip()]
        
        for sent in sentences:
            if len(sent.split()) < 3:
                errors.append({
                    "issue": f"❌ Sentence fragment: '{sent}'",
                    "advice": "All sentences need a subject and verb (complete sentences)",
                    "impact": "MEDIUM"
                })
        
        return errors
    
    def _low_sentence_variety(self, sentences: List) -> bool:
        if len(sentences) < 3:
            return True
        
        lengths = [len(s.split()) for s in sentences]
        return max(lengths) - min(lengths) < 3
    
    def _count_filler_words(self, answer: str) -> int:
        fillers = ['um', 'uh', 'like', 'you know', 'basically', 'actually', 'sort of', 'kind of']
        count = 0
        for filler in fillers:
            count += len(re.findall(r'\b' + filler + r'\b', answer, re.IGNORECASE))
        return count
    
    def _find_word_repetition(self, answer: str) -> List[str]:
        words = answer.lower().split()
        repeated = []
        for word in set(words):
            count = words.count(word)
            if count > 3 and len(word) > 4:  # Only count significant words
                repeated.append(f"{word}({count}x)")
        
        return repeated[:5]
    
    def _has_good_connectors(self, answer: str) -> bool:
        connectors = ['however', 'therefore', 'moreover', 'furthermore', 'meanwhile', 'also', 'besides']
        return any(conn in answer.lower() for conn in connectors)
    
    def _count_connectors(self, answer: str) -> int:
        connectors = ['however', 'therefore', 'moreover', 'furthermore', 'meanwhile', 'also', 'besides']
        count = 0
        for conn in connectors:
            count += len(re.findall(r'\b' + conn + r'\b', answer, re.IGNORECASE))
        return count
    
    def _get_severity_level(self, score: float) -> str:
        for level, range_dict in self.weakness_severity_levels.items():
            if range_dict['min'] <= score < range_dict['max']:
                return level
        return "excellent"
    
    def _get_band_target(self, score: float, criterion: str) -> str:
        if score < 40:
            return "Band 4-5"
        elif score < 60:
            return "Band 5-6"
        elif score < 75:
            return "Band 6-7"
        elif score < 85:
            return "Band 7-8"
        else:
            return "Band 8-9"
    
    def _identify_critical_areas(self, weaknesses: Dict) -> List[str]:
        """Identify which areas need immediate attention"""
        critical = []
        
        for category, data in weaknesses.items():
            if isinstance(data, dict) and 'severity' in data:
                if data['severity'] == 'critical':
                    critical.append(f"🔴 {category}: {data['severity'].upper()}")
                elif data['severity'] == 'high':
                    critical.append(f"🟠 {category}: {data['severity'].upper()}")
        
        return critical

# Initialize detector
detector = WeaknessDetector()

def get_detailed_weaknesses(question: str, answer: str, scores: Dict) -> Dict:
    """Main function to get detailed weakness analysis"""
    return detector.detect_all_weaknesses(
        question,
        answer,
        scores.get('grammar', 70),
        scores.get('fluency', 70),
        scores.get('vocabulary', 70),
        scores.get('pronunciation', 70)
    )
