import stripe
from django.conf import settings
from ..models import Subscription, SubscriptionPlan
from django.db import transaction

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(user, plan_id):
    try:
        with transaction.atomic():
            plan = SubscriptionPlan.objects.select_for_update().get(id=plan_id)
            
            subscription = Subscription.objects.create(
                user=user,
                plan=plan,
                status=Subscription.Status.PENDING
            )

            session = stripe.checkout.Session.create(
                mode="subscription",
                line_items=[{"price": plan.stripe_plan_id, "quantity": 1}],
                customer_email=user.email,
                success_url=f"{settings.FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/payment/cancel",
                metadata={"subscription_id": subscription.id},
            )

            return session, subscription

    except Exception as e:
        raise e
