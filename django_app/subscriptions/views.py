# subscriptions/views.py
from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .models import SubscriptionPlan, Subscription, Payment
from .serializers import (
    SubscriptionPlanSerializer,
    SubscriptionListSerializer,
    SubscriptionDetailSerializer,
    PaymentSerializer,
)

User = get_user_model()

# ------------------------
# Subscription Plans
# ------------------------
class SubscriptionPlanListView(generics.ListAPIView):
    queryset = SubscriptionPlan.objects.all().order_by("price")
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


class SubscriptionPlanDetailView(generics.RetrieveAPIView):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


# ------------------------
# Subscriptions
# ------------------------
class SubscriptionListView(generics.ListAPIView):
    serializer_class = SubscriptionListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Subscription.objects.filter(user=self.request.user)
            .select_related("plan")
            .order_by("-start_date")
        )


class SubscriptionDetailView(generics.RetrieveAPIView):
    serializer_class = SubscriptionDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Subscription.objects.filter(user=self.request.user)
            .select_related("plan")
            .prefetch_related("payments")
        )


# ------------------------
# Payments
# ------------------------
class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Payment.objects.filter(subscription__user=self.request.user)
            .select_related("subscription__plan")
            .order_by("-created_at")
        )


class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(subscription__user=self.request.user).select_related(
            "subscription__plan"
        )
