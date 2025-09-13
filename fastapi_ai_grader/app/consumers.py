import json
import pika
import httpx
from app.config import settings
from app.grader import grade_quiz

def callback(ch, method, properties, body):
    data = json.loads(body)

    attempt_id = data["attempt_id"]
    answers = data["answers"]

    result = grade_quiz(answers)

    payload = {
        "attempt_id": attempt_id,
        "score": result["score"],
        "passed": result["passed"],
        "answers": result["answers"],
    }

    url = f"{settings.DJANGO_API_URL}/quiz/grading-callback/"
    headers = {"Authorization": f"Token {settings.DJANGO_API_TOKEN}"}
    try:
        resp = httpx.post(url, json=payload, headers=headers, timeout=10.0)
        print(f"[✓] Sent grading results to Django: {resp.status_code}")
    except Exception as e:
        print(f"[!] Failed to send results: {e}")

def start_consumer():
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=settings.RABBITMQ_HOST, credentials=credentials)
    )
    channel = connection.channel()
    channel.queue_declare(queue="quiz_submission", durable=True)

    channel.basic_consume(
        queue="quiz_submission", on_message_callback=callback, auto_ack=True
    )

    print("[*] Waiting for quiz submissions. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == "__main__":
    start_consumer()
