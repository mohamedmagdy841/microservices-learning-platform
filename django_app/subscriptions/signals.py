from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Subscription
from django.utils import timezone
from dateutil.relativedelta import relativedelta

@receiver(pre_save, sender=Subscription)
def set_subscription_end_date(sender, instance, **kwargs):
    """
    Automatically set end_date based on plan.duration_months
    if not already set.
    """
    if instance.end_date is None and instance.plan:
        start = instance.start_date or timezone.now()
        instance.end_date = start + relativedelta(months=instance.plan.duration_months)
