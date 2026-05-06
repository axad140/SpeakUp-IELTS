"""
STEP 2 — Grammar Error Detection (Most Important)
Using LanguageTool to count and identify grammar mistakes
"""

import language_tool_python
from config import LANGUAGE_TOOL_LANGUAGE

# Initialize LanguageTool (with Java check)
tool = None
tool_init_error = None
try:
    tool = language_tool_python.LanguageTool(LANGUAGE_TOOL_LANGUAGE)
except Exception as exc:
    tool_init_error = str(exc)
    print("Warning: LanguageTool unavailable. Java is required for grammar detection.")
    print("Please install Java from: https://java.com")
    print("Or run: winget install Oracle.JDK.21")

def detect_grammar_errors(text: str) -> dict:
    """
    Detect grammar errors using LanguageTool
    
    Returns:
        dict with:
        - total_errors: count of grammar mistakes
        - errors: list of detailed error information
        - accuracy_score: percentage of correct words
    """
    # If Java is not installed, return default response
    if tool is None:
        return {
            "total_errors": 0,
            "errors": [],
            "accuracy_score": 100,
            "total_words": len(text.split()),
            "error_percentage": 0,
            "warning": f"Grammar detection unavailable ({tool_init_error or 'Java required'})"
        }
    
    try:
        matches = tool.check(text)
        
        errors = []
        for match in matches:
            error_info = {
                "message": match.message,
                "original": text[match.offset:match.offset + match.length],
                "suggestions": match.replacements[:3],  # Top 3 suggestions
                "position": match.offset,
                "error_type": match.category,
                "context": text[max(0, match.offset-30):min(len(text), match.offset+match.length+30)]
            }
            errors.append(error_info)
        
        # Calculate accuracy score
        total_words = len(text.split())
        error_count = len(matches)
        accuracy_score = max(0, ((total_words - error_count) / total_words * 100)) if total_words > 0 else 0
        
        return {
            "total_errors": error_count,
            "errors": errors,
            "accuracy_score": round(accuracy_score, 2),
            "total_words": total_words,
            "error_percentage": round((error_count / total_words * 100), 2) if total_words > 0 else 0
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "total_errors": 0,
            "errors": [],
            "accuracy_score": 0
        }


def print_grammar_analysis(text: str) -> None:
    """
    Print detailed grammar analysis for a text
    
    Example:
        text = "She go to market yesterday and buy vegetables."
        print_grammar_analysis(text)
    """
    result = detect_grammar_errors(text)
    
    print("\n" + "="*60)
    print("GRAMMAR ERROR DETECTION (LanguageTool)")
    print("="*60)
    print(f"\nText: {text}")
    print(f"\n📊 Summary:")
    print(f"   Total Errors: {result['total_errors']}")
    print(f"   Total Words: {result['total_words']}")
    print(f"   Error Percentage: {result['error_percentage']}%")
    print(f"   Accuracy Score: {result['accuracy_score']}%")
    
    if result['errors']:
        print(f"\n❌ Errors Found:")
        for i, error in enumerate(result['errors'], 1):
            print(f"\n   {i}. Error Type: {error['error_type']}")
            print(f"      Message: {error['message']}")
            print(f"      Original: '{error['original']}'")
            print(f"      Suggestions: {', '.join(error['suggestions'])}")
            print(f"      Context: ...{error['context']}...")
    else:
        print(f"\n✅ No grammar errors found!")
    
    print("\n" + "="*60 + "\n")


# Example usage
if __name__ == "__main__":
    # Test example
    test_text = "She go to market yesterday and buy vegetables."
    print_grammar_analysis(test_text)
    
    # Store metrics
    result = detect_grammar_errors(test_text)
    grammar_error_count = result['total_errors']
    accuracy_score = result['accuracy_score']
    
    print(f"\nStored Metrics:")
    print(f"  grammar_error_count = {grammar_error_count}")
    print(f"  accuracy_score = {accuracy_score}")
