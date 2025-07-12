import os

# Database
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5434/order_db')
SQLALCHEMY_DATABASE_URI = DATABASE_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Microservices URLs
PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://product-service:8000/api')
PAYMENT_SERVICE_URL = os.getenv('PAYMENT_SERVICE_URL', 'http://payment-service:8001/api')
COUPON_SERVICE_URL = os.getenv('COUPON_SERVICE_URL', 'http://coupon-service:8002/api')

# App settings
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-for-order-service')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
