from typing import List, Dict
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider


class GradeResult(BaseModel):
    is_correct: bool

ollama_model = OpenAIChatModel(
    model_name="llama3.1:latest",  # or deepseek-r1:7b, llama3.2:1b
    provider=OllamaProvider(base_url="http://localhost:11434/v1"),
)

grader_agent = Agent(
    ollama_model,
    output_type=GradeResult,
        instructions="""
You are a strict quiz grader.
Always respond with valid JSON ONLY in the following format:

{"is_correct": true} OR {"is_correct": false}

Never include explanations or extra text.
"""
)

async def grade_quiz(answers: List[Dict]) -> Dict:
    graded = []
    score = 0

    for ans in answers:
        question = ans["question_text"]
        chosen = ans["chosen_answer"]
        correct = ans.get("correct_answer")
        
        result = None

        if correct:  # deterministic question
            is_correct = str(chosen).strip().lower() == str(correct).strip().lower()
        else:
            prompt = (
                f"Question: {question}\n"
                f"Correct Answer: {correct if correct else '[open-ended]'}\n"
                f"Student Answer: {chosen}\n\n"
                f"Reply only with JSON {{'is_correct': true/false}}."
            )

            result = await grader_agent.run(prompt)
            is_correct = result.output.is_correct

        print("─────────────────────────────")
        print(f"[DEBUG] Q: {question}")
        print(f"[DEBUG] Student Answer: {chosen}")
        print(f"[DEBUG] Parsed: {is_correct}")
        if result:
            print(f"[DEBUG] Parsed Object: {result.output}")
        print("─────────────────────────────")

        graded.append({
            "question_id": ans["question_id"],
            "is_correct": is_correct
        })
        if is_correct:
            score += 1

    return {
        "score": score,
        "passed": score >= 3,
        "answers": graded
    }
