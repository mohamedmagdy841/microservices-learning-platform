import json
import pika
from django.conf import settings
from django.db import transaction
from .models import Subscription, Payment

def callback(ch, method, properties, body):
    print("Django consumer received")
    data = json.loads(body)

    subscription_id = data["subscription_id"]
    stripe_payment_id = data["stripe_payment_id"]
    amount = data["amount"]
    status = data["status"]

    try:
        with transaction.atomic():
            subscription = Subscription.objects.get(id=subscription_id)

            payment, _ = Payment.objects.update_or_create(
                stripe_payment_id=stripe_payment_id,
                defaults={
                    "subscription": subscription,
                    "amount": amount,
                    "status": status,
                },
            )

            if status == Payment.Status.SUCCESS:
                subscription.status = Subscription.Status.ACTIVE
            elif status == Payment.Status.FAILED:
                subscription.status = Subscription.Status.CANCELED
            subscription.save(update_fields=["status"])

        print("Processed payment")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print("Error processing payment:", e)

def start_consumer():
    credentials = pika.PlainCredentials(
        settings.RABBITMQ_USER, settings.RABBITMQ_PASS
    )
    parameters = pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        credentials=credentials,
    )
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=settings.RABBITMQ_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=settings.RABBITMQ_QUEUE, on_message_callback=callback
    )
    print(" [*] Django waiting for payment events. To exit press CTRL+C")
    channel.start_consuming()

# python manage.py run_payment_consumer
