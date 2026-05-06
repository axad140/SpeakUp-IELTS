"""
Runtime NLP engine for IELTS/interview assessment.

The engine uses local models when they are available and falls back to
transparent text analytics when model weights are not cached locally. No API key
or external service is required.
"""
import math
import re
from collections import Counter
from datetime import datetime

import numpy as np

try:
    import language_tool_python
    from language_tool_python.utils import correct as lt_correct
except Exception:
    language_tool_python = None
    lt_correct = None

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
except Exception:
    TfidfVectorizer = None

try:
    from config import LANGUAGE_TOOL_LANGUAGE, NLP_COHERENCE_MODEL
except Exception:
    LANGUAGE_TOOL_LANGUAGE = "en-US"
    NLP_COHERENCE_MODEL = "all-MiniLM-L6-v2"


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "because", "been", "but",
    "by", "can", "could", "did", "do", "does", "for", "from", "had",
    "has", "have", "he", "her", "his", "how", "i", "if", "in", "is",
    "it", "its", "me", "my", "of", "on", "or", "our", "she", "so",
    "that", "the", "their", "them", "then", "there", "they", "this",
    "to", "was", "we", "were", "what", "when", "where", "which", "who",
    "why", "will", "with", "would", "you", "your",
}

FILLERS = {
    "um", "uh", "erm", "hmm", "like", "basically", "actually", "literally",
    "you know", "i mean", "kind of", "sort of", "well",
}

DISCOURSE_MARKERS = {
    "however", "therefore", "moreover", "furthermore", "although",
    "because", "meanwhile", "consequently", "nevertheless", "additionally",
    "firstly", "secondly", "finally", "for example", "in contrast",
    "as a result", "on the other hand", "in my opinion",
}

COMMON_WORDS = {
    "good", "bad", "big", "small", "thing", "things", "people", "work",
    "make", "made", "get", "got", "go", "went", "nice", "very", "really",
    "much", "many", "some", "lot", "also", "use", "used", "want", "need",
}


def _clip(value, low=0.0, high=9.0):
    return max(low, min(high, value))


def _round_band(value):
    return _clip(round(value * 2) / 2)


def _words(text):
    return re.findall(r"[A-Za-z][A-Za-z']*", text.lower())


def _sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def _cosine(a, b):
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def _level(score):
    if score >= 8:
        return "Excellent"
    if score >= 7:
        return "Strong"
    if score >= 6:
        return "Developing"
    if score >= 5:
        return "Limited"
    return "Needs work"


class ProfessionalNLPEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        print("[NLP ENGINE] Initializing dynamic local NLP engine...")
        self.grammar_tool = None
        self.embedding_model = None
        self.semantic_backend = None
        self.model_status = {
            "grammar": "fallback",
            "semantic": "fallback",
        }

        if language_tool_python is not None:
            try:
                self.grammar_tool = language_tool_python.LanguageTool(LANGUAGE_TOOL_LANGUAGE)
                self.model_status["grammar"] = "language_tool"
            except Exception as exc:
                print("[NLP WARNING] LanguageTool unavailable:", exc)

        if SentenceTransformer is not None:
            try:
                self.embedding_model = SentenceTransformer(NLP_COHERENCE_MODEL)
                self.semantic_backend = "sentence_transformer"
                self.model_status["semantic"] = NLP_COHERENCE_MODEL
            except Exception as exc:
                print("[NLP WARNING] Semantic model unavailable:", exc)
        if self.semantic_backend is None and TfidfVectorizer is not None:
            self.semantic_backend = "tfidf_runtime_model"
            self.model_status["semantic"] = "tfidf_runtime_model"

        self._initialized = True
        print("[NLP ENGINE] Ready:", self.model_status)

    def evaluate_response(self, question, answer, context=None):
        context = context or {}
        question = (question or "").strip()
        answer = (answer or "").strip()

        tokens = _words(answer)
        if len(tokens) < 3:
            return {"error": "Response is too short for reliable analysis."}

        grammar = self._analyze_grammar(answer, tokens)
        lexical = self._analyze_lexical(answer, tokens)
        fluency = self._analyze_fluency(answer, tokens)
        coherence = self._analyze_coherence(question, answer)
        judgment = self._judge_content(question, answer, context, coherence)

        scores = {
            "fluency": fluency["score"],
            "coherence": coherence["score"],
            "vocabulary": lexical["score"],
            "grammar": grammar["score"],
            "relevance": judgment["relevance_score"],
        }
        band_result = self._calculate_band(scores, judgment["confidence"])
        strengths, improvements = self._feedback_points(scores, grammar, lexical, fluency, coherence, judgment)

        if judgment.get("is_off_topic"):
            improvements.insert(0, judgment["refutation"])

        return {
            "status": "success",
            "question": question,
            "answer": answer,
            "model_status": self.model_status,
            "analysis_confidence": judgment["confidence"],
            "grammar": grammar,
            "lexical": lexical,
            "coherence": coherence,
            "judgment": judgment,
            "fluency": fluency,
            "overall_band": band_result,
            "strengths": strengths,
            "improvements": improvements,
            "feedback": self._criterion_feedback(scores, grammar, lexical, fluency, coherence, judgment),
            "interviewer_report": self._generate_report(band_result, scores, strengths, improvements, judgment),
        }

    def _analyze_grammar(self, text, tokens):
        if self.grammar_tool is not None:
            try:
                matches = self.grammar_tool.check(text)
                filtered = [m for m in matches if getattr(m, "ruleId", "") != "WHITESPACE_RULE"]
                corrected = lt_correct(text, filtered) if lt_correct else text
                error_density = len(filtered) / max(1, len(tokens))
                score = _clip(9.0 - (error_density * 32))
                accuracy = _clip(100 - (error_density * 100), 0, 100)
                errors = []
                for match in filtered[:8]:
                    replacement = match.replacements[0] if match.replacements else ""
                    errors.append({
                        "error": text[match.offset:match.offset + match.errorLength],
                        "correction": replacement,
                        "rule": match.ruleId,
                        "message": match.message,
                    })
                return {
                    "score": round(score, 1),
                    "accuracy_percentage": round(accuracy, 1),
                    "corrected_text": corrected,
                    "has_errors": bool(errors),
                    "estimated_errors": len(filtered),
                    "errors": errors,
                    "engine": "language_tool",
                }
            except Exception as exc:
                print("[NLP WARNING] Grammar analysis fallback:", exc)

        repeated = sum(1 for a, b in zip(tokens, tokens[1:]) if a == b)
        lower_text = text.lower()
        agreement_flags = len(re.findall(r"\b(he|she|it)\s+(are|were|have)\b|\b(they|we|you)\s+(is|was|has)\b", lower_text))
        sentence_start_flags = sum(1 for s in _sentences(text) if s and not s[0].isupper())
        estimated_errors = repeated + agreement_flags + sentence_start_flags
        error_density = estimated_errors / max(1, len(tokens))
        score = _clip(8.2 - (error_density * 28))
        corrected = re.sub(r"\s+", " ", text).strip()
        return {
            "score": round(score, 1),
            "accuracy_percentage": round(_clip(score / 9 * 100, 0, 100), 1),
            "corrected_text": corrected,
            "has_errors": estimated_errors > 0,
            "estimated_errors": estimated_errors,
            "errors": [],
            "engine": "rule_fallback",
        }

    def _analyze_lexical(self, text, tokens):
        content_words = [w for w in tokens if w not in STOPWORDS]
        unique = set(content_words)
        word_count = len(tokens)
        diversity = len(unique) / max(1, len(content_words))
        sophistication_words = [
            w for w in unique
            if len(w) >= 8 or (w not in COMMON_WORDS and len(w) >= 6)
        ]
        long_word_ratio = sum(1 for w in content_words if len(w) >= 7) / max(1, len(content_words))
        repeated_content = sum(count - 1 for count in Counter(content_words).values() if count > 1)
        repetition_penalty = repeated_content / max(1, len(content_words))
        score = _clip((diversity * 4.2) + (long_word_ratio * 3.2) + min(1.8, len(sophistication_words) / 6) + 1.0 - repetition_penalty)

        phrases = self._key_phrases(text, limit=8)
        return {
            "score": round(score, 1),
            "variety_ratio": round(diversity, 2),
            "idioms_count": len([p for p in phrases if len(p.split()) > 1]),
            "idioms_found": phrases,
            "advanced_vocab_count": len(sophistication_words),
            "advanced_words": sorted(sophistication_words, key=lambda w: (-len(w), w))[:12],
            "word_count": word_count,
            "unique_words": len(unique),
            "repetition_ratio": round(repetition_penalty, 3),
        }

    def _analyze_fluency(self, text, tokens):
        lower_text = text.lower()
        filler_count = sum(len(re.findall(r"\b" + re.escape(f) + r"\b", lower_text)) for f in FILLERS)
        filler_ratio = filler_count / max(1, len(tokens))
        repeated_count = sum(1 for a, b in zip(tokens, tokens[1:]) if a == b)
        sentence_list = _sentences(text)
        avg_sentence_length = len(tokens) / max(1, len(sentence_list))
        length_balance = 1 - min(1, abs(avg_sentence_length - 16) / 18)
        score = _clip(5.0 + (length_balance * 2.2) + min(1.8, len(tokens) / 80) - (filler_ratio * 18) - (repeated_count * 0.25))
        return {
            "score": round(score, 1),
            "filler_count": filler_count,
            "filler_ratio": round(filler_ratio, 3),
            "avg_sentence_length": round(avg_sentence_length, 1),
            "repetition_count": repeated_count,
        }

    def _analyze_coherence(self, question, answer):
        sentence_list = _sentences(answer)
        marker_count = sum(len(re.findall(r"\b" + re.escape(marker) + r"\b", answer.lower())) for marker in DISCOURSE_MARKERS)
        semantic_flow = None
        relevance_similarity = None

        if self.embedding_model is not None:
            try:
                if len(sentence_list) > 1:
                    vectors = self.embedding_model.encode(sentence_list)
                    adjacent = [_cosine(vectors[i], vectors[i + 1]) for i in range(len(vectors) - 1)]
                    semantic_flow = float(np.mean(adjacent))
                if question:
                    q_vec, a_vec = self.embedding_model.encode([question, answer])
                    relevance_similarity = _cosine(q_vec, a_vec)
            except Exception as exc:
                print("[NLP WARNING] Embedding analysis fallback:", exc)

        if semantic_flow is None and self.semantic_backend == "tfidf_runtime_model":
            try:
                docs = sentence_list[:]
                if question:
                    docs = [question, answer] + docs
                matrix = TfidfVectorizer(stop_words="english", ngram_range=(1, 2)).fit_transform(docs)
                offset = 2 if question else 0
                if question:
                    relevance_similarity = float((matrix[0] @ matrix[1].T).toarray()[0][0])
                if len(sentence_list) > 1:
                    adjacent = []
                    for i in range(offset, offset + len(sentence_list) - 1):
                        adjacent.append(float((matrix[i] @ matrix[i + 1].T).toarray()[0][0]))
                    semantic_flow = float(np.mean(adjacent)) if adjacent else None
            except Exception as exc:
                print("[NLP WARNING] TF-IDF semantic fallback:", exc)

        if semantic_flow is None:
            sentence_sets = [set(_words(s)) - STOPWORDS for s in sentence_list]
            overlaps = []
            for left, right in zip(sentence_sets, sentence_sets[1:]):
                denom = max(1, len(left | right))
                overlaps.append(len(left & right) / denom)
            semantic_flow = float(np.mean(overlaps)) if overlaps else 0.35

        structure = min(1.0, len(sentence_list) / 4)
        marker_score = min(1.0, marker_count / max(1, len(sentence_list)))
        flow_score = _clip(semantic_flow * 9)
        score = _clip((structure * 2.0) + (marker_score * 2.0) + (flow_score * 0.55) + 2.0)

        return {
            "score": round(score, 1),
            "sentence_count": len(sentence_list),
            "discourse_markers_found": marker_count,
            "semantic_flow": round(float(semantic_flow), 3),
            "question_similarity": None if relevance_similarity is None else round(float(relevance_similarity), 3),
            "logical_flow": _level(score),
        }

    def _judge_content(self, question, answer, context, coherence):
        q_terms = set(w for w in _words(question) if w not in STOPWORDS and len(w) > 2)
        a_terms = set(w for w in _words(answer) if w not in STOPWORDS and len(w) > 2)
        lexical_overlap = len(q_terms & a_terms) / max(1, len(q_terms))

        if coherence.get("question_similarity") is not None:
            semantic_relevance = max(0.0, min(1.0, (coherence["question_similarity"] + 1) / 2))
            relevance_score = _clip((semantic_relevance * 7.0) + (lexical_overlap * 2.0))
            evidence = "semantic_model"
        else:
            relevance_score = _clip((lexical_overlap * 7.0) + min(2.0, len(a_terms) / 20))
            semantic_relevance = None
            evidence = "keyword_overlap"

        is_off_topic = relevance_score <= 4.5
        refutation = None
        if is_off_topic:
            q_k = [word for word, _ in Counter([w for w in _words(question) if w not in STOPWORDS and len(w) > 2]).most_common(3)]
            a_k = [word for word, _ in Counter([w for w in _words(answer) if w not in STOPWORDS and len(w) > 2]).most_common(3)]
            q_topic = ", ".join(q_k) if q_k else "the expected topic"
            a_topic = ", ".join(a_k) if a_k else "unrelated subjects"
            refutation = f"Issue Detected: Out of Context. The question asked about '{q_topic}', but your answer discussed '{a_topic}'. You need to properly relate your answer to the exact question asked."
            relevance_score = min(relevance_score, 3.0)

        answer_words = len(_words(answer))
        evidence_strength = min(1.0, answer_words / 80)
        model_bonus = 0.15 if self.semantic_backend in {"sentence_transformer", "tfidf_runtime_model"} else 0
        confidence = _clip(45 + evidence_strength * 30 + relevance_score * 2.2 + model_bonus * 100, 0, 96)

        return {
            "relevance_score": round(relevance_score, 1),
            "professionalism_score": round(self._professionalism(answer), 1),
            "status": _level(relevance_score),
            "matched_keywords": len(q_terms & a_terms),
            "total_keywords": len(q_terms),
            "semantic_relevance": None if semantic_relevance is None else round(semantic_relevance, 3),
            "confidence": round(confidence, 1),
            "evidence": evidence,
            "is_off_topic": is_off_topic,
            "refutation": refutation,
            "context": {
                "field": context.get("field", ""),
                "category": context.get("category", ""),
                "part": context.get("part", ""),
            },
        }

    def _professionalism(self, text):
        tokens = _words(text)
        first_person = sum(1 for w in tokens if w in {"i", "me", "my", "we", "our"})
        directness = min(1.0, len(tokens) / 70)
        slang = sum(1 for w in tokens if w in {"gonna", "wanna", "kinda", "yeah", "nah"})
        return _clip(5.0 + directness * 3.0 - slang * 0.7 + min(1.0, first_person / 8))

    def _calculate_band(self, scores, confidence):
        weighted = (
            scores["fluency"] * 0.25
            + scores["coherence"] * 0.20
            + scores["vocabulary"] * 0.20
            + scores["grammar"] * 0.25
            + scores["relevance"] * 0.10
        )
        confidence_adjustment = 0.92 + (confidence / 100 * 0.08)
        band = _round_band(weighted * confidence_adjustment)
        return {
            "band": band,
            "label": self._band_label(band),
            "description": self._band_description(band),
            "confidence": round(confidence, 1),
            "breakdown": {
                "fluency_coherence": round((scores["fluency"] + scores["coherence"]) / 2, 1),
                "lexical_resource": round(scores["vocabulary"], 1),
                "grammatical_range": round(scores["grammar"], 1),
                "task_achievement": round(scores["relevance"], 1),
            },
        }

    def _criterion_feedback(self, scores, grammar, lexical, fluency, coherence, judgment):
        return {
            "fc": self._sentence_feedback("Fluency and coherence", scores["fluency"], [
                f"{fluency['filler_count']} hesitation markers",
                f"{coherence['sentence_count']} sentence units",
                f"{coherence['discourse_markers_found']} linking markers",
            ]),
            "lr": self._sentence_feedback("Lexical resource", scores["vocabulary"], [
                f"{lexical['unique_words']} unique content words",
                f"{lexical['advanced_vocab_count']} stronger vocabulary choices",
                f"diversity ratio {lexical['variety_ratio']}",
            ]),
            "gra": self._sentence_feedback("Grammar accuracy", scores["grammar"], [
                f"{grammar['estimated_errors']} detected issues",
                f"{grammar['accuracy_percentage']}% estimated accuracy",
                f"engine: {grammar['engine']}",
            ]),
            "ta": self._sentence_feedback("Task relevance", scores["relevance"], [
                f"{judgment['matched_keywords']}/{judgment['total_keywords']} question signals matched",
                f"confidence {judgment['confidence']}%",
                f"evidence: {judgment['evidence']}",
            ]),
        }

    def _sentence_feedback(self, title, score, evidence):
        evidence_text = "; ".join(str(item) for item in evidence if item is not None)
        return f"{title}: {_level(score)} ({round(score, 1)}/9). Evidence: {evidence_text}."

    def _feedback_points(self, scores, grammar, lexical, fluency, coherence, judgment):
        labels = {
            "fluency": "Your fluency is supported by steady sentence length and limited hesitation.",
            "coherence": "Your ideas connect clearly across the answer.",
            "vocabulary": "Your vocabulary shows range and topic-specific wording.",
            "grammar": "Your grammar is accurate enough for clear communication.",
            "relevance": "Your answer addresses the question directly.",
        }
        improve = {
            "fluency": f"Reduce hesitation markers and avoid repeated words; detected fillers: {fluency['filler_count']}.",
            "coherence": f"Add clearer linking language between ideas; linking markers found: {coherence['discourse_markers_found']}.",
            "vocabulary": "Use more precise topic vocabulary and avoid repeating the same content words.",
            "grammar": f"Review the detected grammar issues; estimated issues: {grammar['estimated_errors']}.",
            "relevance": "Answer the exact question more directly before adding extra details.",
        }

        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        strengths = [labels[key] for key, score in ranked if score >= 6][:3]
        if not strengths:
            strengths = [labels[ranked[0][0]]]

        weak_ranked = sorted(scores.items(), key=lambda item: item[1])
        improvements = [improve[key] for key, score in weak_ranked if score < 7][:4]
        if not improvements:
            improvements = [f"Push from {_level(ranked[0][1]).lower()} to excellent by adding richer examples and more precise language."]

        if lexical.get("advanced_words"):
            strengths.append("Strong words detected: " + ", ".join(lexical["advanced_words"][:5]) + ".")

        return strengths[:4], improvements[:4]

    def _generate_report(self, band_result, scores, strengths, improvements, judgment):
        score_bits = ", ".join(f"{name} {round(score, 1)}/9" for name, score in scores.items())
        report_text = (
            f"Overall Band {band_result['band']} ({band_result['label']}) with "
            f"{band_result['confidence']}% analysis confidence. Scores: {score_bits}. "
            f"Main strengths: {' '.join(strengths[:2])} "
            f"Priority work: {' '.join(improvements[:2])} "
            f"Relevance evidence: {judgment['evidence']}."
        )
        if judgment.get("is_off_topic"):
            report_text = judgment["refutation"] + " " + report_text
        return report_text

    def _key_phrases(self, text, limit=8):
        tokens = [w for w in _words(text) if w not in STOPWORDS and len(w) > 2]
        phrases = Counter()
        for n in (2, 3):
            for i in range(0, max(0, len(tokens) - n + 1)):
                phrase = " ".join(tokens[i:i + n])
                if len(set(phrase.split())) == n:
                    phrases[phrase] += 1
        ranked_phrases = [p for p, _ in phrases.most_common(limit)]
        singles = sorted(set(tokens), key=lambda w: (-len(w), w))[: max(0, limit - len(ranked_phrases))]
        return ranked_phrases + singles

    def _band_label(self, band):
        if band >= 8.5:
            return "Expert User"
        if band >= 7:
            return "Good User"
        if band >= 6:
            return "Competent User"
        if band >= 5:
            return "Modest User"
        if band >= 4:
            return "Limited User"
        return "Developing User"

    def _band_description(self, band):
        if band >= 8:
            return "Clear, flexible and detailed speaking performance."
        if band >= 7:
            return "Strong communication with some areas to refine."
        if band >= 6:
            return "Generally effective response with noticeable limitations."
        if band >= 5:
            return "Meaning is understandable but language range needs work."
        return "Basic response; focus on clarity, structure and accuracy."


def extract_question_keywords(text, limit=5):
    tokens = [w for w in _words(text) if w not in STOPWORDS and len(w) > 2]
    counts = Counter(tokens)
    return [word for word, _ in counts.most_common(limit)]


def build_question_metadata(question, part=1, field="", category=""):
    keywords = extract_question_keywords(f"{question} {field} {category}", limit=6)
    if part == 1:
        duration = "30-45 seconds"
    elif part == 2:
        duration = "1-2 minutes"
    else:
        duration = "2-3 minutes"

    focus = ", ".join(keywords[:3]) if keywords else "the question"
    return {
        "keywords": keywords,
        "tips": f"Answer directly, support your point with one example, and connect back to {focus}.",
        "duration": duration,
    }


def build_dynamic_report(responses, cv=None, name="Candidate", field="General", category="general"):
    cv = cv or {}
    bands = [r.get("bands", {}) for r in responses]

    def avg(key):
        values = [b.get(key) for b in bands if isinstance(b.get(key), (int, float))]
        return round(sum(values) / len(values), 1) if values else 0

    fc, lr, gra, p = avg("fc"), avg("lr"), avg("gra"), avg("p")
    available = [value for value in [fc, lr, gra, p] if value]
    overall_band = _round_band(sum(available) / len(available)) if available else 0

    all_strengths = []
    all_improvements = []
    for response in responses:
        all_strengths.extend(response.get("ai", {}).get("strengths", []))
        all_improvements.extend(response.get("ai", {}).get("improvements", []))

    strength_counts = Counter(all_strengths)
    improvement_counts = Counter(all_improvements)
    top_strengths = [item for item, _ in strength_counts.most_common(5)]
    critical_improvements = [item for item, _ in improvement_counts.most_common(5)]

    weakest = sorted(
        [("Fluency", fc), ("Vocabulary", lr), ("Grammar", gra), ("Pronunciation", p)],
        key=lambda item: item[1] or 0,
    )
    study_plan = []
    for week, (theme, score) in enumerate(weakest, start=1):
        study_plan.append({
            "week": week,
            "theme": theme,
            "daily_tasks": [
                f"Record one answer focused on {theme.lower()} and compare it with yesterday.",
                "Rewrite one weak answer using clearer structure and stronger examples.",
                "Review your score evidence and repeat the lowest-scoring criterion.",
            ],
            "resources": [f"Personal practice set: {theme}"],
            "current_score": score,
        })

    question_rows = []
    for index, response in enumerate(responses, start=1):
        question_rows.append({
            "num": index,
            "question": response.get("question", ""),
            "answer": response.get("answer", ""),
            "band": response.get("overall_band") or response.get("bands", {}).get("overall", 0),
            "bands": response.get("bands", {}),
            "strengths": response.get("ai", {}).get("strengths", []),
            "improvements": response.get("ai", {}).get("improvements", []),
            "corrected": response.get("ai", {}).get("corrected_answer", ""),
            "model": response.get("ai", {}).get("model_answer", ""),
            "word_count": response.get("nlp", {}).get("word_count", 0),
        })

    summary = (
        f"{name} completed {len(responses)} responses in {field}. "
        f"The runtime analysis produced Band {overall_band}, with the strongest criterion "
        f"at {max([fc, lr, gra, p] or [0])}/9 and the main improvement area in {weakest[0][0]}."
    )

    return {
        "meta": {
            "name": name,
            "field": field,
            "category": category,
            "date": datetime.now().strftime("%B %d, %Y"),
            "time": datetime.now().strftime("%I:%M %p"),
            "total_questions": len(responses),
        },
        "overall": {
            "band": overall_band,
            "label": ProfessionalNLPEngine()._band_label(overall_band),
            "description": ProfessionalNLPEngine()._band_description(overall_band),
            "color": "#00b894" if overall_band >= 7 else "#f0a500" if overall_band >= 6 else "#e17055",
            "fc": fc,
            "lr": lr,
            "gra": gra,
            "p": p,
        },
        "cv": cv,
        "ai_report": {
            "summary": summary,
            "top_strengths": top_strengths or ["You completed the speaking task and produced analyzable responses."],
            "critical_improvements": critical_improvements or ["Give fuller answers with clearer examples."],
            "study_plan": study_plan,
            "target_timeline": "2-4 weeks, adjusted by your weakest criterion trend.",
            "field_specific_advice": f"For {field}, keep examples specific and use the vocabulary that naturally belongs to your topic.",
            "motivational_message": f"{name}, your next gain will come from improving the lowest-scoring criterion first.",
        },
        "questions": question_rows,
    }


_engine = None


def get_professional_judgment(question, answer, context=None):
    global _engine
    if _engine is None:
        _engine = ProfessionalNLPEngine()
    return _engine.evaluate_response(question, answer, context=context)
