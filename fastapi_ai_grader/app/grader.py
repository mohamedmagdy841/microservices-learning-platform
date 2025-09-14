import random
from typing import List, Dict

def grade_quiz(answers: List[Dict]) -> Dict:
    graded = []
    score = 0

    for ans in answers:
        # Randomly decide correctness
        is_correct = random.choice([True, False])

        graded.append({
            "question_id": ans["question_id"],
            "is_correct": is_correct
        })

        if is_correct:
            score += 1

    return {
        "score": score,
        "passed": score >= 3,  # arbitrary pass condition
        "answers": graded
    }
