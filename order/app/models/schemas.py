from app import ma
from app.models.models import Order, OrderItem, CartItem, OrderStatus
from marshmallow import fields, post_dump
import json

# Address Schema
class AddressSchema(ma.Schema):
    street = fields.Str(required=True)
    city = fields.Str(required=True)
    state = fields.Str(required=True)
    postal_code = fields.Str(required=True)
    country = fields.Str(required=True)
    phone = fields.Str()

# Order Item Schema
class OrderItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = OrderItem
        include_fk = True

# Cart Item Schema
class CartItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CartItem
        include_fk = True

# Cart Item With Product Schema
class CartItemWithProductSchema(CartItemSchema):
    product = fields.Dict()

# Order Schema
class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        include_fk = True
    
    status = fields.Function(lambda obj: obj.status.value)
    shipping_address = fields.Dict()
    items = fields.List(fields.Nested(OrderItemSchema))

# Order Create Schema
class OrderCreateSchema(ma.Schema):
    user_id = fields.Str(required=True)
    shipping_address = fields.Nested(AddressSchema, required=True)
    coupon_code = fields.Str()
    notes = fields.Str()

# Order Update Schema
class OrderUpdateSchema(ma.Schema):
    status = fields.Str()
    payment_id = fields.Str()

# Cart Item Create Schema
class CartItemCreateSchema(ma.Schema):
    product_id = fields.Int(required=True)
    quantity = fields.Int(default=1)

# Initialize schemas
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
order_item_schema = OrderItemSchema()
order_items_schema = OrderItemSchema(many=True)
cart_item_schema = CartItemSchema()
cart_items_schema = CartItemSchema(many=True)
cart_item_with_product_schema = CartItemWithProductSchema()
cart_items_with_product_schema = CartItemWithProductSchema(many=True)
order_create_schema = OrderCreateSchema()
order_update_schema = OrderUpdateSchema()
cart_item_create_schema = CartItemCreateSchema()
