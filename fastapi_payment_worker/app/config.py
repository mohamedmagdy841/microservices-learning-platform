import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    STRIPE_SECRET = os.getenv("STRIPE_SECRET")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
    RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE")

    DJANGO_API_URL = os.getenv("DJANGO_API_URL", "http://django_app:8000/api")
    DJANGO_API_TOKEN = os.getenv("DJANGO_API_TOKEN")

settings = Settings()
