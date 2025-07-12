from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db

router = APIRouter()

@router.get("/health", tags=["health"])
def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint for Product Service
    
    Checks:
    - API is running
    - Database connection is working
    """
    try:
        # Check database connection
        db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "service": "product-service",
            "checks": {
                "api": "up",
                "database": "connected"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "product-service",
            "checks": {
                "api": "up",
                "database": "error: " + str(e)
            }
        }
