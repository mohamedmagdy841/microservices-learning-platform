from typing import List, Dict
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import re

MODEL_NAME = "google/gemma-2-2b-it"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
    dtype=torch.float16 if torch.cuda.is_available() else torch.float32
)

generator = pipeline("text-generation", model=model, tokenizer=tokenizer)


def clean_output(text: str) -> str:
    """
    Extract 'true' or 'false' from model output reliably.
    """
    # Remove special tokens like <bos>, <start_of_turn>, etc.
    cleaned = re.sub(r"<.*?>", "", text)
    cleaned = cleaned.strip().lower()

    if "true" in cleaned and not "false" in cleaned:
        return "true"
    if "false" in cleaned and not "true" in cleaned:
        return "false"

    if "true" in cleaned and "false" in cleaned:
        return "true" if cleaned.rfind("true") > cleaned.rfind("false") else "false"

    return "false"


def grade_quiz(answers: List[Dict]) -> Dict:
    graded = []
    score = 0

    for ans in answers:
        question = ans["question_text"]
        chosen = ans["chosen_answer"]
        correct = ans.get("correct_answer")

        user_prompt = (
            f"Grade this answer.\n"
            f"Question: {question}\n"
            f"Correct Answer: {correct if correct else '[open-ended]'}\n"
            f"Student Answer: {chosen}\n\n"
            f"Reply with ONLY one word: true or false."
        )

        chat_input = tokenizer.apply_chat_template(
            [{"role": "user", "content": user_prompt}],
            tokenize=False,
            add_generation_prompt=True
        )

        raw = generator(
            chat_input,
            max_new_tokens=3,
            do_sample=False,
            eos_token_id=tokenizer.eos_token_id
        )[0]["generated_text"]

        result = clean_output(raw)
        is_correct = (result == "true")

        print(f"[DEBUG] Q: {question} | A: {chosen} | Raw: {raw} | Parsed: {result}")

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
