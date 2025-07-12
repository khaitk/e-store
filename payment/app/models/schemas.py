from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from app.models.models import PaymentStatus, InvoiceStatus

# Payment schemas
class PaymentBase(BaseModel):
    order_id: str
    user_id: str
    amount: float
    currency: str = "VND"
    payment_method: str
    payment_details: Optional[Dict[str, Any]] = {}

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    status: Optional[PaymentStatus] = None
    payment_details: Optional[Dict[str, Any]] = None
    stripe_payment_intent_id: Optional[str] = None

class Payment(PaymentBase):
    id: int
    status: PaymentStatus
    stripe_payment_intent_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Invoice schemas
class InvoiceItem(BaseModel):
    product_id: str
    quantity: int
    price: float

class InvoiceBase(BaseModel):
    payment_id: int
    user_id: str
    items: List[InvoiceItem]
    total_amount: float
    tax: float = 0
    due_date: Optional[datetime] = None

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceUpdate(BaseModel):
    status: Optional[InvoiceStatus] = None

class Invoice(InvoiceBase):
    id: int
    status: InvoiceStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Stripe schemas
class StripePaymentIntent(BaseModel):
    client_secret: str
    payment_intent_id: str

class StripeWebhookPayload(BaseModel):
    type: str
    data: Dict[str, Any]
