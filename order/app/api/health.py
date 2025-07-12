from flask import Blueprint, jsonify, current_app
from app import db
import requests

health_bp = Blueprint('health', __name__, url_prefix='')

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for Order Service
    
    Checks:
    - API is running
    - Database connection is working
    - Connections to other services
    """
    health_status = {
        "status": "healthy",
        "service": "order-service",
        "checks": {
            "api": "up",
            "database": "unknown",
            "dependencies": {
                "product-service": "unknown",
                "payment-service": "unknown",
                "coupon-service": "unknown"
            }
        }
    }
    
    # Check database connection
    try:
        db.session.execute("SELECT 1")
        health_status["checks"]["database"] = "connected"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = f"error: {str(e)}"
    
    # Check connections to other services
    services = {
        "product-service": current_app.config.get('PRODUCT_SERVICE_URL', ''),
        "payment-service": current_app.config.get('PAYMENT_SERVICE_URL', ''),
        "coupon-service": current_app.config.get('COUPON_SERVICE_URL', '')
    }
    
    for service_name, base_url in services.items():
        if not base_url:
            health_status["checks"]["dependencies"][service_name] = "error: URL not configured"
            health_status["status"] = "unhealthy"
            continue
            
        try:
            # Try to connect to the service's health endpoint
            response = requests.get(f"{base_url.rstrip('/')}/health", timeout=2)
            if response.status_code == 200:
                health_status["checks"]["dependencies"][service_name] = "connected"
            else:
                health_status["checks"]["dependencies"][service_name] = f"error: HTTP {response.status_code}"
                health_status["status"] = "unhealthy"
        except requests.exceptions.RequestException as e:
            health_status["checks"]["dependencies"][service_name] = f"error: {str(e)}"
            health_status["status"] = "unhealthy"
    
    return jsonify(health_status)
