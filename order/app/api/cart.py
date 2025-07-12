from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.models import CartItem
from app.models.schemas import cart_item_schema, cart_items_schema, cart_item_create_schema, cart_items_with_product_schema
from app.services import product_service
from marshmallow import ValidationError

cart_bp = Blueprint('cart', __name__, url_prefix='/api')

@cart_bp.route('/cart/<string:user_id>', methods=['GET'])
def get_cart(user_id):
    """
    Get user's shopping cart
    """
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    
    # Get product details for each cart item
    result = []
    for item in cart_items:
        cart_item_dict = cart_item_schema.dump(item)
        try:
            product = product_service.get_product(item.product_id)
            cart_item_dict['product'] = product
        except Exception:
            # If product details can't be fetched, return item without product details
            cart_item_dict['product'] = None
        result.append(cart_item_dict)
    
    return jsonify(result)

@cart_bp.route('/cart/<string:user_id>', methods=['POST'])
def add_to_cart(user_id):
    """
    Add product to shopping cart
    """
    try:
        # Validate request data
        data = cart_item_create_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    
    product_id = data['product_id']
    quantity = data.get('quantity', 1)
    
    # Check if product exists
    try:
        product = product_service.get_product(product_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    # Check stock availability
    if product["stock"] < quantity:
        return jsonify({"error": "Not enough stock available"}), 400
    
    # Check if product already exists in cart
    existing_item = CartItem.query.filter_by(
        user_id=user_id,
        product_id=product_id
    ).first()
    
    if existing_item:
        # Update quantity
        existing_item.quantity += quantity
        db.session.commit()
        return jsonify(cart_item_schema.dump(existing_item)), 200
    
    # Add new product to cart
    cart_item = CartItem(
        user_id=user_id,
        product_id=product_id,
        quantity=quantity
    )
    
    db.session.add(cart_item)
    db.session.commit()
    
    return jsonify(cart_item_schema.dump(cart_item)), 201

@cart_bp.route('/cart/<string:user_id>/items/<int:item_id>', methods=['PUT'])
def update_cart_item(user_id, item_id):
    """
    Update cart item quantity
    """
    try:
        # Validate request data
        data = cart_item_create_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    
    # Check if cart item exists
    cart_item = CartItem.query.filter_by(
        id=item_id,
        user_id=user_id
    ).first()
    
    if not cart_item:
        return jsonify({"error": "Cart item not found"}), 404
    
    product_id = data['product_id']
    quantity = data.get('quantity', 1)
    
    # Check if product exists
    try:
        product = product_service.get_product(product_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    # Check stock availability
    if product["stock"] < quantity:
        return jsonify({"error": "Not enough stock available"}), 400
    
    # Update quantity
    cart_item.quantity = quantity
    db.session.commit()
    
    return jsonify(cart_item_schema.dump(cart_item))

@cart_bp.route('/cart/<string:user_id>/items/<int:item_id>', methods=['DELETE'])
def remove_from_cart(user_id, item_id):
    """
    Remove item from shopping cart
    """
    # Check if cart item exists
    cart_item = CartItem.query.filter_by(
        id=item_id,
        user_id=user_id
    ).first()
    
    if not cart_item:
        return jsonify({"error": "Cart item not found"}), 404
    
    # Remove item from cart
    db.session.delete(cart_item)
    db.session.commit()
    
    return '', 204

@cart_bp.route('/cart/<string:user_id>', methods=['DELETE'])
def clear_cart(user_id):
    """
    Clear entire shopping cart
    """
    # Delete all items in user's cart
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    
    return '', 204
