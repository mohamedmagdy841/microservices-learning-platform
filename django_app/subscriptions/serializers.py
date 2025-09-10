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

class PaymentCallbackSerializer(serializers.Serializer):
    subscription_id = serializers.IntegerField()
    stripe_payment_id = serializers.CharField()
    amount = serializers.DecimalField(max_digits=8, decimal_places=2)
    status = serializers.ChoiceField(choices=Payment.Status.choices)

    def validate_subscription_id(self, value):
        if not Subscription.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid subscription_id")
        return value

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
