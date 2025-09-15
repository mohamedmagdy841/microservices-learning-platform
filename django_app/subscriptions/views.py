import stripe
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .services.stripe_service import create_checkout_session
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import SubscriptionPlan, Subscription, Payment, SubscriptionStatus
from django.utils.timezone import now
from .permissions import IsServiceToken
from .serializers import (
    SubscriptionPlanSerializer,
    SubscriptionListSerializer,
    SubscriptionDetailSerializer,
    PaymentSerializer,
    PaymentCallbackSerializer,
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
        return Response({"checkout_url": "Test"})
        # plan_id = request.data.get("plan_id")
        # if not plan_id:
        #     return Response({"error": "plan_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # has_active = Subscription.objects.filter(
        #     user=request.user,
        #     status=SubscriptionStatus.ACTIVE,
        #     end_date__gte=now()
        # ).exists()

        # if has_active:
        #     return Response(
        #         {"error": "You already have an active subscription."},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
            
        # try:
        #     session, subscription = create_checkout_session(
        #         user=request.user,
        #         plan_id=plan_id,
        #     )
        #     return Response({"checkout_url": session.url})
        # except stripe.error.StripeError as e:
        #     return Response({"error": str(e.user_message or str(e))}, status=400)
        # except Exception as e:
        #     return Response({"error": str(e)}, status=500)
        
class PaymentCallbackView(APIView):
    permission_classes = [IsServiceToken]

    def post(self, request, *args, **kwargs):
        return Response({"message": "Payment processed"}, status=status.HTTP_200_OK)
        # serializer = PaymentCallbackSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # data = serializer.validated_data

        # subscription = get_object_or_404(Subscription, id=data["subscription_id"])

        # payment, _ = Payment.objects.update_or_create(
        #     stripe_payment_id=data["stripe_payment_id"],
        #     defaults={
        #         "subscription": subscription,
        #         "amount": data["amount"],
        #         "status": data["status"],
        #     },
        # )

        # # Update subscription status
        # if data["status"] == Payment.Status.SUCCESS:
        #     subscription.status = SubscriptionStatus.ACTIVE
        # elif data["status"] == Payment.Status.FAILED:
        #     subscription.status = SubscriptionStatus.CANCELED
        # subscription.save(update_fields=["status"])

        # return Response({"message": "Payment processed"}, status=status.HTTP_200_OK)
