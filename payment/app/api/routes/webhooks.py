import os
from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
import stripe

from app.db.database import get_db
from app.models import models
from app.services.stripe_service import StripeService

router = APIRouter()

@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    # Get the webhook secret
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not webhook_secret:
        raise HTTPException(status_code=500, detail="Stripe webhook secret not configured")
    
    # Get the signature from headers
    signature = request.headers.get("stripe-signature")
    if not signature:
        raise HTTPException(status_code=400, detail="No Stripe signature found in request")
    
    # Get the request body
    payload = await request.body()
    
    try:
        # Verify the event
        event = StripeService.construct_event(payload, signature, webhook_secret)
        
        # Handle the event
        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            await handle_payment_success(payment_intent, db)
        elif event["type"] == "payment_intent.payment_failed":
            payment_intent = event["data"]["object"]
            await handle_payment_failure(payment_intent, db)
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

async def handle_payment_success(payment_intent, db: Session):
    # Get payment ID from metadata
    payment_id = payment_intent.get("metadata", {}).get("payment_id")
    if not payment_id:
        return
    
    # Update payment status
    payment = db.query(models.Payment).filter(models.Payment.id == int(payment_id)).first()
    if payment:
        payment.status = models.PaymentStatus.COMPLETED
        payment.payment_details = {
            **payment.payment_details,
            "transaction_id": payment_intent.get("id"),
            "receipt_url": payment_intent.get("charges", {}).get("data", [{}])[0].get("receipt_url")
        }
        db.commit()
        
        # Update related invoices
        invoices = db.query(models.Invoice).filter(models.Invoice.payment_id == int(payment_id)).all()
        for invoice in invoices:
            invoice.status = models.InvoiceStatus.PAID
        db.commit()

async def handle_payment_failure(payment_intent, db: Session):
    # Get payment ID from metadata
    payment_id = payment_intent.get("metadata", {}).get("payment_id")
    if not payment_id:
        return
    
    # Update payment status
    payment = db.query(models.Payment).filter(models.Payment.id == int(payment_id)).first()
    if payment:
        payment.status = models.PaymentStatus.FAILED
        payment.payment_details = {
            **payment.payment_details,
            "error": payment_intent.get("last_payment_error", {}).get("message")
        }
        db.commit()
