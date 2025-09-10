import stripe
from fastapi import APIRouter, Request, HTTPException
from .config import settings
from .producers import publish_payment_event
from .schemas import PaymentEvent, PaymentStatus

router = APIRouter()
stripe.api_key = settings.STRIPE_SECRET

@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] in ["checkout.session.completed", "invoice.payment_succeeded", "invoice.payment_failed"]:
        data = event["data"]["object"]

        subscription_id = data.get("metadata", {}).get("subscription_id")
        if not subscription_id:
            raise HTTPException(status_code=400, detail="Missing subscription_id metadata")

        payment_event = PaymentEvent(
            subscription_id=int(subscription_id),
            stripe_payment_id=data.get("payment_intent") or data.get("id"),
            amount=float(data.get("amount_total", 0)) / 100,
            status=PaymentStatus.success if event["type"] in ["checkout.session.completed", "invoice.payment_succeeded"] else PaymentStatus.failed
        )

        publish_payment_event(payment_event)

    return {"status": "ok"}
