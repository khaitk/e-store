from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models import models, schemas

router = APIRouter()

@router.get("/invoices", response_model=List[schemas.Invoice])
def get_invoices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    invoices = db.query(models.Invoice).offset(skip).limit(limit).all()
    return invoices

@router.get("/invoices/{invoice_id}", response_model=schemas.Invoice)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@router.post("/invoices", response_model=schemas.Invoice, status_code=status.HTTP_201_CREATED)
def create_invoice(invoice: schemas.InvoiceCreate, db: Session = Depends(get_db)):
    # Check if payment exists
    payment = db.query(models.Payment).filter(models.Payment.id == invoice.payment_id).first()
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Set due date if not provided
    if not invoice.due_date:
        invoice.due_date = datetime.utcnow() + timedelta(days=30)
    
    db_invoice = models.Invoice(**invoice.dict())
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

@router.put("/invoices/{invoice_id}", response_model=schemas.Invoice)
def update_invoice(invoice_id: int, invoice_update: schemas.InvoiceUpdate, db: Session = Depends(get_db)):
    db_invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if db_invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Update status if provided
    if invoice_update.status:
        db_invoice.status = invoice_update.status
    
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

@router.get("/invoices/payment/{payment_id}", response_model=List[schemas.Invoice])
def get_invoices_by_payment(payment_id: int, db: Session = Depends(get_db)):
    invoices = db.query(models.Invoice).filter(models.Invoice.payment_id == payment_id).all()
    return invoices
