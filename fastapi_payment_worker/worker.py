import pika, json, httpx
from app.config import settings
from app.schemas import PaymentEvent

def callback(ch, method, properties, body):
    data = json.loads(body)
    event = PaymentEvent(**data)

    try:
        with httpx.Client(timeout=10) as client:
            response = client.post(
                f"{settings.DJANGO_API_URL}/subscriptions/payments/callback/",
                headers={"Authorization": f"Token {settings.DJANGO_API_TOKEN}"},
                json=event.model_dump(),
            )

        if response.status_code == 200:
            print("Django processed payment:", response.json())
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            print("Django returned error:", response.status_code, response.text)
    except Exception as e:
        print("Failed to reach Django:", e)

def start_consumer():
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        credentials=credentials
    )
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=settings.RABBITMQ_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=settings.RABBITMQ_QUEUE, on_message_callback=callback)
    print(" [*] Waiting for payment events. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == "__main__":
    start_consumer()
