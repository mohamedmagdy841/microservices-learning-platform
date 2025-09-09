# subscriptions/serializers.py
from rest_framework import serializers
from .models import SubscriptionPlan, Subscription, Payment
from django.contrib.auth import get_user_model

User = get_user_model()


# ------------------------
# SubscriptionPlan
# ------------------------
class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            "id",
            "name",
            "price",
            "duration_months",
            "stripe_plan_id",
            "created_at",
        ]


# ------------------------
# Payment
# ------------------------
class PaymentSerializer(serializers.ModelSerializer):
    subscription = serializers.CharField(source="subscription.plan.name")
    
    class Meta:
        model = Payment
        fields = [
            "id",
            "stripe_payment_id",
            "amount",
            "status",
            "created_at",
            "subscription",
        ]


# ------------------------
# Subscription
# ------------------------
class SubscriptionListSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = [
            "id",
            "plan",
            "status",
            "start_date",
            "end_date",
        ]


class SubscriptionDetailSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Subscription
        fields = [
            "id",
            "plan",
            "status",
            "start_date",
            "end_date",
            "payments",
        ]
