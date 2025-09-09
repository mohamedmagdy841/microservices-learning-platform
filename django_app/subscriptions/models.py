from django.db import models
from django.conf import settings

class SubscriptionPlan(models.Model):
    stripe_plan_id = models.CharField(
        max_length=100,
        unique=True,
    )
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_months = models.PositiveSmallIntegerField(
        help_text="Duration of the plan in months"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (${self.price})"
    
class Subscription(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        CANCELED = "canceled", "Canceled"
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name="subscriptions")
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    
    def __str__(self):
        return f"{self.plan.name} ({self.status})"

class Payment(models.Model):
    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        PENDING = "pending", "Pending"
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="payments")
    stripe_payment_id = models.CharField(
        max_length=150,
        unique=True,
        help_text="Stripe Payment Intent ID",
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment {self.stripe_payment_id} - {self.status}"
