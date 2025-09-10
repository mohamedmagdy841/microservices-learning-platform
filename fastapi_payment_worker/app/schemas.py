from pydantic import BaseModel
from enum import Enum

class PaymentStatus(str, Enum):
    success = "success"
    failed = "failed"
    pending = "pending"

class PaymentEvent(BaseModel):
    subscription_id: int
    stripe_payment_id: str
    amount: float
    status: PaymentStatus
