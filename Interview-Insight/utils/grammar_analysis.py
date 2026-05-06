import language_tool_python
from config import LANGUAGE_TOOL_LANGUAGE, GRAMMAR_CHECK_THRESHOLD

def grammar_check(answer):
    """Simple grammar check returning accuracy score"""
    tool = language_tool_python.LanguageTool(LANGUAGE_TOOL_LANGUAGE)
    matches = tool.check(answer)
    errors = len(matches)
    total_words = len(answer.split())
    accuracy = max(0, (total_words - errors) / total_words * 100)
    return accuracy

def grammar_check_detailed(answer):
    """Detailed grammar check with error information and corrections"""
    tool = language_tool_python.LanguageTool(LANGUAGE_TOOL_LANGUAGE)
    matches = tool.check(answer)
    
    errors = []
    for match in matches[:10]:  # Limit to top 10 errors
        error_info = {
            "issue": match.message,
            "original": answer[match.offset:match.offset + match.length],
            "suggestion": match.replacements[0] if match.replacements else "See suggestion above",
            "position": f"Word {len(answer[:match.offset].split())}"
        }
        errors.append(error_info)
    
    # Calculate accuracy score
    total_words = len(answer.split())
    error_count = len(matches)
    accuracy_score = max(0, (total_words - error_count) / total_words * 100)
    
    return {
        "score": accuracy_score,
        "total_errors": len(matches),
        "errors": errors
    }
