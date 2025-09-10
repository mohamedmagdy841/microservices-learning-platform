from django.utils.timezone import now
from .models import Subscription

def has_active_subscription(user):
    return Subscription.objects.filter(
        user=user,
        status=Subscription.Status.ACTIVE,
        end_date__gte=now()
    ).exists()
