import os
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# Initialize extensions
db = SQLAlchemy()
ma = Marshmallow()

def create_app(test_config=None):
    """
    Create and configure the Flask application
    
    Args:
        test_config: Configuration for testing
        
    Returns:
        Flask application instance
    """
    # Create and configure app
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration from config.py
    app.config.from_object('app.config.config')
    
    # Override with test config if provided
    if test_config:
        app.config.update(test_config)
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize extensions with app
    db.init_app(app)
    ma.init_app(app)
    
    # Import and register blueprints
    from app.api.orders import orders_bp
    from app.api.cart import cart_bp
    
    app.register_blueprint(orders_bp)
    app.register_blueprint(cart_bp)
    
    # Root route
    @app.route('/')
    def index():
        return {'message': 'Welcome to Order Service'}
    
    # Health check route
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}
    
    # Create all tables in database
    with app.app_context():
        db.create_all()
    
    return app
