from config import KEYWORD_MATCH_THRESHOLD

def evaluate_keywords(answer, keywords):
    keyword_count = sum(1 for keyword in keywords if keyword.lower() in answer.lower())
    return (keyword_count / len(keywords)) * 100
