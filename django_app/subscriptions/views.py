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
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    inline_serializer,
    OpenApiResponse,
    OpenApiTypes,
    OpenApiExample
)

User = get_user_model()

# ------------------------
# Subscription Plans
# ------------------------
@extend_schema_view(
    get=extend_schema(
        tags=["Subscription Plans"],
        summary="List subscription plans",
        description="Retrieve a list of all available subscription plans ordered by price.",
        responses={200: SubscriptionPlanSerializer},
        auth=[],  # public endpoint
    )
)
class SubscriptionPlanListView(generics.ListAPIView):
    queryset = SubscriptionPlan.objects.all().order_by("price")
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]

@extend_schema_view(
    get=extend_schema(
        tags=["Subscription Plans"],
        summary="Retrieve subscription plan details",
        description="Retrieve details of a specific subscription plan by ID.",
        responses={200: SubscriptionPlanSerializer},
        auth=[],  # public endpoint
    )
)
class SubscriptionPlanDetailView(generics.RetrieveAPIView):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [permissions.AllowAny]


# ------------------------
# Subscriptions
# ------------------------
@extend_schema_view(
    get=extend_schema(
        tags=["Subscriptions"],
        summary="List subscriptions",
        description="Retrieve a list of subscriptions for the authenticated user.",
        responses={200: SubscriptionListSerializer},
    )
)
class SubscriptionListView(generics.ListAPIView):
    serializer_class = SubscriptionListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Subscription.objects.filter(user=self.request.user)
            .select_related("plan")
            .order_by("-start_date")
        )

@extend_schema_view(
    get=extend_schema(
        tags=["Subscriptions"],
        summary="Retrieve subscription details",
        description="Retrieve details of a specific subscription for the authenticated user.",
        responses={200: SubscriptionDetailSerializer},
    )
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
@extend_schema_view(
    get=extend_schema(
        tags=["Payments"],
        summary="List payments",
        description="Retrieve a list of payments related to the authenticated user’s subscriptions.",
        responses={200: PaymentSerializer},
    )
)
class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Payment.objects.filter(subscription__user=self.request.user)
            .select_related("subscription__plan")
            .order_by("-created_at")
        )

@extend_schema_view(
    get=extend_schema(
        tags=["Payments"],
        summary="Retrieve payment details",
        description="Retrieve details of a specific payment belonging to the authenticated user.",
        responses={200: PaymentSerializer},
    )
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
@extend_schema_view(
    post=extend_schema(
        tags=["Checkout"],
        summary="Create subscription checkout session",
        description=(
            "Create a Stripe Checkout session for a subscription plan. "
            "Returns a checkout URL that the client can redirect the user to."
        ),
        request=OpenApiTypes.OBJECT,  # you can replace with a small serializer if you prefer
        examples=[
            OpenApiExample(
                "Checkout request",
                value={"plan_id": 1},
            )
        ],
        responses={
            200: OpenApiResponse(
                description="Checkout session created successfully",
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Checkout response",
                        value={"checkout_url": "https://checkout.stripe.com/test-session"},
                    )
                ],
            ),
            400: OpenApiResponse(description="Invalid request"),
        },
    )
)
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
        

@extend_schema_view(
    post=extend_schema(
        tags=["Payments"],
        summary="Payment callback (Stripe webhook)",
        description=(
            "Endpoint used by Stripe webhook / internal service. "
            "Updates subscription status based on payment result."
        ),
        auth=[],  # service-to-service secured by token, not user auth
        request=PaymentCallbackSerializer,
        responses={200: OpenApiResponse(description="Payment processed successfully")},
    )
)
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
