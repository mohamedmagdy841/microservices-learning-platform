from django.core.management.base import BaseCommand
from subscriptions import consumers

class Command(BaseCommand):
    help = "Run RabbitMQ payment consumer"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting payment consumer..."))
        consumers.start_consumer()
