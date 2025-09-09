# subscriptions/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .services.stripe_service import create_checkout_session
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

# ------------------------
# Checkout
# ------------------------
class SubscriptionCheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        plan_id = request.data.get("plan_id")
        if not plan_id:
            return Response({"error": "plan_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        success_url = request.build_absolute_uri("/success/")
        cancel_url = request.build_absolute_uri("/cancel/")

        session, subscription = create_checkout_session(
            user=request.user,
            plan_id=plan_id,
            success_url=success_url,
            cancel_url=cancel_url,
        )

        return Response({"checkout_url": session.url})
