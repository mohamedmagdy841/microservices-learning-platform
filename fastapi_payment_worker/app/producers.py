import pika
from .config import settings
from .schemas import PaymentEvent

def publish_payment_event(event: PaymentEvent):
    print("Connecting to RabbitMQ...")
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASS)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            credentials=credentials
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=settings.RABBITMQ_QUEUE, durable=True)

    message = event.json()

    channel.basic_publish(
        exchange="",
        routing_key=settings.RABBITMQ_QUEUE,
        body=message,
        properties=pika.BasicProperties(delivery_mode=2)
    )
    print("Message published")
    connection.close()
