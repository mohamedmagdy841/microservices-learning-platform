import stripe
from django.conf import settings
from ..models import Subscription, SubscriptionPlan

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(user, plan_id, success_url, cancel_url):
    plan = SubscriptionPlan.objects.get(id=plan_id)

    subscription = Subscription.objects.create(
        user=user,
        plan=plan,
        status=Subscription.Status.PENDING
    )

    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": plan.stripe_plan_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"subscription_id": subscription.id},
    )

    return session, subscription
