import pika, json, httpx
from app.config import settings
from app.schemas import PaymentEvent

def callback(ch, method, properties, body):
    data = json.loads(body)
    event = PaymentEvent(**data)

    # Notify Django
    with httpx.Client() as client:
        response = client.post(
            f"{settings.DJANGO_API_URL}/subscriptions/payment-callback/",
            headers={"Authorization": f"Token {settings.DJANGO_API_TOKEN}"},
            json=event.dict(),
        )
        print("Django response:", response.status_code, response.text)

    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(settings.RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=settings.RABBITMQ_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=settings.RABBITMQ_QUEUE, on_message_callback=callback)
    print(" [*] Waiting for payment events. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == "__main__":
    start_consumer()
