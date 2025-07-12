from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Table, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class InvoiceStatus(str, enum.Enum):
    ISSUED = "issued"
    PAID = "paid"
    CANCELLED = "cancelled"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, index=True)
    user_id = Column(String, index=True)
    amount = Column(Float)
    currency = Column(String, default="VND")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(String)
    payment_details = Column(JSON, default={})
    stripe_payment_intent_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    invoices = relationship("Invoice", back_populates="payment")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"))
    user_id = Column(String, index=True)
    items = Column(JSON, default=[])
    total_amount = Column(Float)
    tax = Column(Float, default=0)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.ISSUED)
    due_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    payment = relationship("Payment", back_populates="invoices")
