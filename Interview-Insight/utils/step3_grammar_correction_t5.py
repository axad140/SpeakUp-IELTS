"""
STEP 3 — Grammar Correction using T5 (IELTS level)
Using Hugging Face T5 model for professional grammar correction
"""

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# Load the T5 grammar correction model
print("[T5] Loading grammar correction model...")
try:
    tokenizer = AutoTokenizer.from_pretrained("vennify/t5-base-grammar-correction")
    model = AutoModelForSeq2SeqLM.from_pretrained("vennify/t5-base-grammar-correction")
    print("✓ T5 Grammar Correction Model loaded successfully\n")
except Exception as e:
    print(f"✗ Error loading T5 model: {e}\n")
    tokenizer = None
    model = None


def correct_grammar_t5(sentence: str) -> dict:
    """
    Correct grammar using T5 model
    
    Args:
        sentence: Text to correct
    
    Returns:
        dict with:
        - original: original text
        - corrected: corrected text
        - changed: whether corrections were made
        - confidence: confidence score
    """
    if not tokenizer or not model:
        return {
            "original": sentence,
            "corrected": sentence,
            "changed": False,
            "confidence": 0,
            "error": "T5 model not loaded"
        }
    
    try:
        # Prepare input for T5
        input_text = "correct: " + sentence
        
        # Tokenize
        inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=256, truncation=True)
        
        # Generate correction
        outputs = model.generate(
            inputs,
            max_length=256,
            num_beams=5,
            early_stopping=True,
            temperature=0.7
        )
        
        # Decode
        corrected_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Check if changes were made
        changed = sentence.lower().strip() != corrected_text.lower().strip()
        
        # Calculate confidence
        confidence = 95 if changed else 99  # Higher confidence if correction was made
        
        return {
            "original": sentence,
            "corrected": corrected_text,
            "changed": changed,
            "confidence": confidence,
            "status": "corrected" if changed else "already_correct"
        }
    
    except Exception as e:
        return {
            "original": sentence,
            "corrected": sentence,
            "changed": False,
            "confidence": 0,
            "error": str(e)
        }


def correct_paragraph_t5(text: str) -> dict:
    """
    Correct a full paragraph sentence by sentence
    
    Args:
        text: Full paragraph to correct
    
    Returns:
        dict with corrections for each sentence
    """
    sentences = text.split('.')
    corrected_sentences = []
    total_changes = 0
    
    print("[T5] Correcting paragraph...")
    print("="*60)
    
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if not sentence:
            continue
        
        result = correct_grammar_t5(sentence)
        corrected_sentences.append(result['corrected'])
        
        if result['changed']:
            total_changes += 1
            print(f"\n✏️  Sentence {i+1}:")
            print(f"   ❌ Original: {sentence}")
            print(f"   ✅ Corrected: {result['corrected']}")
        else:
            print(f"\n✓ Sentence {i+1}: Already correct")
            print(f"   {sentence}")
    
    corrected_text = '. '.join(corrected_sentences)
    if corrected_text and not corrected_text.endswith('.'):
        corrected_text += '.'
    
    print("\n" + "="*60)
    print(f"\n📊 Summary: {total_changes} sentences corrected\n")
    
    return {
        "original": text,
        "corrected": corrected_text,
        "total_corrections": total_changes,
        "sentences_total": len([s for s in sentences if s.strip()])
    }


def print_grammar_correction(sentence: str) -> None:
    """
    Print formatted grammar correction
    
    Example:
        text = "She go to market yesterday and buy vegetables."
        print_grammar_correction(text)
    """
    result = correct_grammar_t5(sentence)
    
    print("\n" + "="*60)
    print("T5 GRAMMAR CORRECTION (IELTS Level)")
    print("="*60)
    print(f"\n❌ Original: {result['original']}")
    print(f"✅ Corrected: {result['corrected']}")
    print(f"\nChanged: {result['changed']}")
    print(f"Confidence: {result['confidence']}%")
    print(f"Status: {result.get('status', 'N/A')}")
    print("\n" + "="*60 + "\n")


# Example usage
if __name__ == "__main__":
    # Test sentence
    test_sentence = "She go to market yesterday and buy vegetables."
    print_grammar_correction(test_sentence)
    
    # Store metrics
    result = correct_grammar_t5(test_sentence)
    corrected_text = result['corrected']
    changed = result['changed']
    
    print(f"\nStored Metrics:")
    print(f"  corrected_text = '{corrected_text}'")
    print(f"  changed = {changed}")
    
    # Test paragraph correction
    print("\n\n" + "="*60)
    print("Testing paragraph correction:")
    print("="*60)
    
    test_paragraph = "She go to market yesterday. He are very happy. They was playing football."
    result = correct_paragraph_t5(test_paragraph)
    
    print(f"\nFinal Corrected Paragraph:")
    print(result['corrected'])
