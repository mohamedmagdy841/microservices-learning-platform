import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_USER = os.getenv("RABBITMQ_USER")
    RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")

    DJANGO_API_URL = os.getenv("DJANGO_API_URL", "http://django_app:8000/api")
    DJANGO_API_TOKEN = os.getenv("DJANGO_API_TOKEN")

settings = Settings()
