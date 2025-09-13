import json
import pika
from django.conf import settings

def publish_quiz_submitted_event(attempt_id: int, quiz_id: int, user_id: int, answers: list):
    """
    Publishes a message to RabbitMQ when a student submits a quiz attempt.
    FastAPI AI grader will consume this event and return graded results.
    """
    payload = {
        "event": "quiz_submitted",
        "attempt_id": attempt_id,
        "quiz_id": quiz_id,
        "user_id": user_id,
        "answers": answers,
    }

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            credentials=pika.PlainCredentials(
                settings.RABBITMQ_USER,
                settings.RABBITMQ_PASS,
            ),
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue="quiz_submission", durable=True)

    channel.basic_publish(
        exchange="",
        routing_key="quiz_submission",
        body=json.dumps(payload),
        properties=pika.BasicProperties(delivery_mode=2),
    )
    connection.close()
