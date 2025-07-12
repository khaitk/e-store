from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
import os
import stripe

router = APIRouter()

@router.get("/health", tags=["health"])
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint for Payment Service
    
    Checks:
    - API is running
    - Database connection is working
    - Stripe API key is configured
    """
    health_status = {
        "status": "healthy",
        "service": "payment-service",
        "checks": {
            "api": "up",
            "database": "unknown",
            "stripe": "unknown"
        }
    }
    
    # Check database connection
    try:
        db.execute("SELECT 1")
        health_status["checks"]["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = f"error: {str(e)}"
    
    # Check Stripe configuration
    stripe_key = os.getenv("STRIPE_API_KEY")
    if not stripe_key:
        health_status["status"] = "unhealthy"
        health_status["checks"]["stripe"] = "error: API key not configured"
    else:
        try:
            # Just check if we can initialize the library
            stripe.api_key = stripe_key
            health_status["checks"]["stripe"] = "configured"
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["checks"]["stripe"] = f"error: {str(e)}"
    
    return health_status
