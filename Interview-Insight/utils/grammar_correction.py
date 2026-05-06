"""
Advanced Grammar Correction - Lightweight version without Java dependency
"""
import re
from typing import Dict, List, Tuple

class GrammarCorrector:
    def __init__(self):
        # Common grammar patterns and corrections
        self.grammar_rules = [
            # Tense consistency
            {
                "pattern": r"\b(was|were)\s+(\w+ing)\b(?!.*\b(was|were|is|are|am)\b)",
                "error_type": "Tense Consistency",
                "suggestion": "Ensure consistent tense usage"
            },
            # Subject-verb agreement
            {
                "pattern": r"\b(he|she|it|person|student)\s+(are|were|have|do)\b",
                "error_type": "Subject-Verb Agreement",
                "suggestion": "Use singular verb with singular subject"
            },
            # Article usage common errors
            {
                "pattern": r"\b(a)\s+([aeiou])",
                "error_type": "Article Usage",
                "suggestion": "Use 'an' before vowel sounds"
            },
            # Preposition errors
            {
                "pattern": r"\b(in|at|on)\s+(morning|evening|night)\b",
                "error_type": "Preposition",
                "suggestion": "Use 'in the morning/evening', 'at night'"
            },
            # Common word confusions
            {
                "pattern": r"\b(there|their|they're)\b",
                "error_type": "Word Confusion",
                "suggestion": "Ensure correct there/their/they're usage"
            },
        ]
        
        # Filler words to avoid
        self.filler_words = {
            'um': 'Remove filler word',
            'uh': 'Remove filler word',
            'like': 'Reduce usage in formal speech',
            'you know': 'Avoid filler phrase',
            'basically': 'Use more specific language',
            'actually': 'Reduce redundant word',
            'sort of': 'Be more direct',
            'kind of': 'Be more direct'
        }
        
        # Weak words to replace
        self.weak_words = {
            'good': ['excellent', 'outstanding', 'exceptional'],
            'bad': ['poor', 'inadequate', 'inadequate'],
            'thing': ['matter', 'issue', 'aspect'],
            'nice': ['pleasant', 'agreeable', 'delightful'],
            'very': ['extremely', 'remarkably', 'particularly'],
            'a lot': ['many', 'numerous', 'considerable'],
            'get': ['obtain', 'acquire', 'receive'],
            'put': ['place', 'position', 'arrange']
        }
    
    def correct_with_suggestions(self, text: str) -> Dict:
        """
        Detect grammar issues and provide corrections with suggestions
        """
        corrections = []
        words = text.split()
        
        # Check for filler words
        for filler, description in self.filler_words.items():
            pattern = r'\b' + re.escape(filler) + r'\b'
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for match in matches:
                corrections.append({
                    "error_type": "Filler Word",
                    "original": match.group(),
                    "position": match.start(),
                    "suggestions": ["Remove or replace with silence/pause"],
                    "explanation": "Filler words reduce clarity and fluency",
                    "context": text[max(0, match.start()-20):min(len(text), match.end()+20)]
                })
        
        # Check for weak words
        for weak, strong_options in self.weak_words.items():
            pattern = r'\b' + re.escape(weak) + r'\b'
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for match in matches:
                corrections.append({
                    "error_type": "Weak Word Choice",
                    "original": match.group(),
                    "position": match.start(),
                    "suggestions": strong_options,
                    "explanation": f"Use stronger vocabulary instead of '{weak}'",
                    "context": text[max(0, match.start()-20):min(len(text), match.end()+20)]
                })
        
        # Check for common tense errors
        tense_issues = self._check_tense_consistency(text)
        corrections.extend(tense_issues)
        
        # Check for subject-verb agreement
        sv_issues = self._check_subject_verb_agreement(text)
        corrections.extend(sv_issues)
        
        return {
            "total_errors": len(corrections),
            "corrections": corrections[:15],  # Top 15 errors
            "corrected_text": self._apply_corrections_auto(text, corrections),
            "error_summary": self._summarize_errors(corrections)
        }
    
    def _check_tense_consistency(self, text: str) -> List[Dict]:
        """Check for tense inconsistency"""
        issues = []
        
        past_tenses = ['was', 'were', 'had', 'did']
        present_tenses = ['is', 'are', 'am', 'have', 'do']
        
        past_count = sum(1 for word in past_tenses if re.search(r'\b' + word + r'\b', text, re.IGNORECASE))
        present_count = sum(1 for word in present_tenses if re.search(r'\b' + word + r'\b', text, re.IGNORECASE))
        
        if past_count > 0 and present_count > 3:
            issues.append({
                "error_type": "Tense Consistency",
                "original": "Mixed tenses",
                "position": 0,
                "suggestions": ["Maintain consistent past or present tense"],
                "explanation": "Your answer mixes past and present tenses inconsistently",
                "context": text[:100]
            })
        
        return issues
    
    def _check_subject_verb_agreement(self, text: str) -> List[Dict]:
        """Check for subject-verb agreement errors"""
        issues = []
        
        # Pattern: singular subject + plural verb (simplified)
        singular_subjects = ['he', 'she', 'it', 'person', 'student', 'the man', 'the woman']
        plural_verbs = ['are', 'were', 'have', 'do']
        
        for subject in singular_subjects:
            for verb in plural_verbs:
                pattern = r'\b' + re.escape(subject) + r'\s+' + re.escape(verb) + r'\b'
                if re.search(pattern, text, re.IGNORECASE):
                    issues.append({
                        "error_type": "Subject-Verb Agreement",
                        "original": f"{subject} {verb}",
                        "position": 0,
                        "suggestions": [f"Use singular verb form with '{subject}'"],
                        "explanation": f"'{subject}' is singular and needs singular verb",
                        "context": text[:100]
                    })
        
        return issues
    
    def _apply_corrections_auto(self, text: str, corrections: List[Dict]) -> str:
        """
        Apply best corrections automatically (conservative approach)
        """
        corrected = text
        
        # Apply only the most certain corrections
        for correction in corrections[:3]:
            if correction['suggestions'] and correction['suggestions'][0]:
                original = correction['original']
                best_suggestion = correction['suggestions'][0]
                
                # Only replace exact matches
                pattern = r'\b' + re.escape(original) + r'\b'
                corrected = re.sub(pattern, best_suggestion, corrected, flags=re.IGNORECASE, count=1)
        
        return corrected
    
    def _summarize_errors(self, corrections: List[Dict]) -> Dict:
        """
        Summarize error types and frequency
        """
        error_counts = {}
        for correction in corrections:
            error_type = correction['error_type']
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        return error_counts
    
    def get_improvement_tips(self, text: str) -> List[str]:
        """
        Provide improvement tips based on analysis
        """
        tips = []
        
        # Check for filler words
        filler_pattern = r'\b(um|uh|like|you know|basically|actually)\b'
        filler_count = len(re.findall(filler_pattern, text, re.IGNORECASE))
        if filler_count > 2:
            tips.append(f"⚠️ Reduce filler words ({filler_count} found). Pause instead of using 'um', 'like', etc.")
        
        # Check sentence length
        sentences = re.split(r'[.!?]+', text)
        avg_words_per_sentence = sum(len(s.split()) for s in sentences) / max(1, len(sentences))
        if avg_words_per_sentence < 8:
            tips.append("📝 Use longer, more complex sentences. Aim for 10-15 words per sentence.")
        
        # Check for passive voice
        passive_pattern = r'\b(is|are|was|were)\s+\w+ed\b'
        passive_count = len(re.findall(passive_pattern, text))
        if passive_count > 2:
            tips.append("💪 Use more active voice. Convert passive to active constructions.")
        
        # Check for variety
        words = text.lower().split()
        unique_words = len(set(words))
        variety_ratio = unique_words / len(words) if words else 0
        if variety_ratio < 0.5:
            tips.append("🎯 Increase vocabulary variety. Avoid repeating the same words.")
        
        # Check for connectors
        connectors = ['however', 'therefore', 'moreover', 'furthermore', 'nevertheless', 'meanwhile']
        connector_count = sum(1 for conn in connectors if conn.lower() in text.lower())
        if connector_count == 0 and len(text) > 100:
            tips.append("🔗 Use linking words to connect ideas (however, therefore, moreover, etc.)")
        
        # Check for example usage
        if 'for example' not in text.lower() and 'such as' not in text.lower():
            tips.append("📚 Add specific examples to support your points.")
        
        return tips[:5]

# Initialize corrector
corrector = GrammarCorrector()

def correct_grammar_smart(text: str) -> Dict:
    """
    Main function for grammar correction
    """
    result = corrector.correct_with_suggestions(text)
    result['tips'] = corrector.get_improvement_tips(text)
    return result

