import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

class PretrainedLocalExaminer:
    def __init__(self):
        # We use a completely offline pre-trained conversational generation model
        # that doesn't rely on Gemini/OpenAI API keys.
        # Using Flan-T5-base for fast local generation
        print("[SETUP] Loading completely offline pre-trained response generation model...")
        self.model_name = "google/flan-t5-base"
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self.is_ready = True
            print("[SETUP] Pre-trained model loaded successfully.")
        except Exception as e:
            print("[SETUP Error] Could not load offline model:", e)
            self.is_ready = False
            self.tokenizer = None
            self.model = None

    def _fallback_question(self, context: str) -> str:
        context = context or "general communication"
        field = "your field"
        category = "communication"
        part = "1"
        number = 1
        for chunk in context.split("."):
            lower = chunk.strip().lower()
            if lower.startswith("field:"):
                field = chunk.split(":", 1)[1].strip() or field
            elif lower.startswith("category:"):
                category = chunk.split(":", 1)[1].strip() or category
            elif lower.startswith("question:"):
                digits = "".join(ch for ch in lower if ch.isdigit())
                if digits:
                    number = int(digits)
            elif "part" in lower:
                digits = "".join(ch for ch in lower if ch.isdigit())
                if digits:
                    part = digits[0]

        part_one = [
            f"What do you usually do to improve your communication in {field}?",
            f"Which skill is most useful for someone working in {field}, and why?",
            f"How often do you use {category} in your daily work or study?",
        ]
        part_two = [
            f"Describe a recent experience in {field} where {category} was important.",
            f"Talk about a project or task in {field} that helped you learn something new.",
            f"Describe a person in {field} whose communication style you respect.",
        ]
        part_three = [
            f"How do you think {category} will change the future of {field}?",
            f"What challenges do people in {field} face when they communicate complex ideas?",
            f"Should students preparing for {field} focus more on technical knowledge or communication?",
        ]
        index = max(0, number - 1)
        if part == "1":
            return part_one[index % len(part_one)]
        if part == "2":
            return part_two[index % len(part_two)]
        return part_three[index % len(part_three)]

    def _generate(self, prompt: str, max_new_tokens: int = 64) -> str:
        if not self.is_ready or self.tokenizer is None or self.model is None:
            return ""

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=256
        )

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                top_p=0.92,
                temperature=0.7,
                repetition_penalty=1.05
            )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
            
    def generate_question(self, context="Start the interview"):
        if not self.is_ready:
            return self._fallback_question(context)
            
        prompt = (
            "Generate one IELTS speaking question only. "
            f"Context: {context}. Keep it natural and concise."
        )
        try:
            generated = self._generate(prompt, max_new_tokens=40)
            return generated if generated else self._fallback_question(context)
        except:
            return self._fallback_question(context)

    def generate_feedback(self, text, grammar_errors, vocab_score):
        if not self.is_ready:
            return (
                f"Your answer contains {len(text.split())} words, "
                f"{grammar_errors} grammar signals, and vocabulary score {vocab_score}/10."
            )
            
        prompt = (
            "Provide brief IELTS speaking feedback in 2 short sentences. "
            f"Student response: '{text}'. "
            f"Grammar errors: {grammar_errors}. Vocabulary score: {vocab_score} out of 10."
        )
        try:
            generated = self._generate(prompt, max_new_tokens=80)
            return generated if generated else "Please focus on speaking more clearly and expanding your vocabulary."
        except:
            return (
                f"Use the detected evidence to improve: grammar signals {grammar_errors}, "
                f"vocabulary score {vocab_score}/10."
            )

    def generate_model_answer(self, question: str, candidate_answer: str = "") -> str:
        if not self.is_ready:
            return ""

        prompt = (
            "Write a concise IELTS Band 8+ sample spoken answer in 4-6 sentences. "
            f"Question: {question}. "
            f"Candidate answer context: {candidate_answer}."
        )
        try:
            return self._generate(prompt, max_new_tokens=120)
        except Exception:
            return ""

local_examiner = PretrainedLocalExaminer()
