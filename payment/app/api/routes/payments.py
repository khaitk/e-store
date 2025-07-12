from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import models, schemas
from app.services.stripe_service import StripeService

router = APIRouter()

@router.get("/payments", response_model=List[schemas.Payment])
def get_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    payments = db.query(models.Payment).offset(skip).limit(limit).all()
    return payments

@router.get("/payments/{payment_id}", response_model=schemas.Payment)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.post("/payments", response_model=schemas.Payment, status_code=status.HTTP_201_CREATED)
def create_payment(payment: schemas.PaymentCreate, db: Session = Depends(get_db)):
    # Create payment record
    db_payment = models.Payment(**payment.dict())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    
    # Create Stripe payment intent
    try:
        metadata = {
            "payment_id": str(db_payment.id),
            "order_id": db_payment.order_id,
            "user_id": db_payment.user_id
        }
        
        stripe_payment = StripeService.create_payment_intent(
            amount=payment.amount,
            currency=payment.currency,
            metadata=metadata
        )
        
        # Update payment with Stripe payment intent ID
        db_payment.stripe_payment_intent_id = stripe_payment.payment_intent_id
        db_payment.payment_details = {
            **db_payment.payment_details,
            "client_secret": stripe_payment.client_secret
        }
        db.commit()
        db.refresh(db_payment)
        
        return db_payment
    except Exception as e:
        # Rollback in case of error
        db.delete(db_payment)
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/payments/{payment_id}/refund", response_model=schemas.Payment)
def refund_payment(payment_id: int, db: Session = Depends(get_db)):
    # Get payment
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Check if payment can be refunded
    if payment.status != models.PaymentStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Only completed payments can be refunded")
    
    # Refund payment in Stripe
    try:
        if not payment.stripe_payment_intent_id:
            raise HTTPException(status_code=400, detail="No Stripe payment intent ID found")
        
        refund = StripeService.refund_payment(payment.stripe_payment_intent_id)
        
        # Update payment status
        payment.status = models.PaymentStatus.REFUNDED
        payment.payment_details = {
            **payment.payment_details,
            "refund_id": refund.id
        }
        db.commit()
        db.refresh(payment)
        
        return payment
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payments/user/{user_id}", response_model=List[schemas.Payment])
def get_user_payments(user_id: str, db: Session = Depends(get_db)):
    payments = db.query(models.Payment).filter(models.Payment.user_id == user_id).all()
    return payments
