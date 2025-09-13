from typing import List, Dict
import random

def grade_quiz(answers: List[Dict]) -> Dict:
    """
    Fake AI grader: randomly marks answers correct/incorrect.
    Later, integrate with LLM API (OpenAI, etc).
    """
    graded = []
    score = 0

    for ans in answers:
        is_correct = random.choice([True, False])  # mock AI grading
        graded.append({
            "question_id": ans["question_id"],
            "is_correct": is_correct
        })
        if is_correct:
            score += 1

    return {
        "score": score,
        "passed": score >= 3,  # rule: pass if >= 3/5
        "answers": graded
    }
