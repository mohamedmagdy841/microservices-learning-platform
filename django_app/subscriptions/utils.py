from django.utils.timezone import now
from .models import Subscription, SubscriptionStatus

def has_active_subscription(user):
    return Subscription.objects.filter(
        user=user,
        status=SubscriptionStatus.ACTIVE,
        end_date__gte=now()
    ).exists()
