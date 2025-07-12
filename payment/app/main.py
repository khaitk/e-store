import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import payments, invoices, webhooks
from app.db.database import engine
from app.models import models

# Initialize Stripe
import stripe
stripe.api_key = os.getenv("STRIPE_API_KEY")

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Payment Service", description="Payment Service for E-Store Microservices")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(payments.router, prefix="/api", tags=["payments"])
app.include_router(invoices.router, prefix="/api", tags=["invoices"])
app.include_router(webhooks.router, prefix="/api", tags=["webhooks"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Payment Service"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
