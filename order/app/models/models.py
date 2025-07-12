from datetime import datetime
from app import db
import enum
import json

class OrderStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class Order(db.Model):
    """
    Order model representing customer orders
    """
    __tablename__ = "orders"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), index=True, nullable=False)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    discount_amount = db.Column(db.Float, default=0)
    shipping_cost = db.Column(db.Float, default=0)
    final_amount = db.Column(db.Float, nullable=False)
    _shipping_address = db.Column("shipping_address", db.Text, nullable=False)
    payment_id = db.Column(db.String(50), nullable=True)
    coupon_code = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")
    
    @property
    def shipping_address(self):
        """
        Convert JSON string to dictionary for shipping address
        """
        return json.loads(self._shipping_address)
    
    @shipping_address.setter
    def shipping_address(self, value):
        """
        Convert dictionary to JSON string for shipping address
        """
        self._shipping_address = json.dumps(value)
    
    def __repr__(self):
        return f'<Order {self.id}>'

class OrderItem(db.Model):
    """
    Order item model representing products in an order
    """
    __tablename__ = "order_items"
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<OrderItem {self.id}>'

class CartItem(db.Model):
    """
    Cart item model representing products in a user's shopping cart
    """
    __tablename__ = "cart_items"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), index=True, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CartItem {self.id}>'
