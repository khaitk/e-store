from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.models import Order, OrderItem, CartItem, OrderStatus
from app.models.schemas import order_schema, orders_schema, order_create_schema, order_update_schema
from app.services import product_service, payment_service, coupon_service
from marshmallow import ValidationError

orders_bp = Blueprint('orders', __name__, url_prefix='/api')

@orders_bp.route('/orders', methods=['GET'])
def get_orders():
    """
    Get list of orders with pagination
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    orders = Order.query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'orders': orders_schema.dump(orders.items),
        'total': orders.total,
        'pages': orders.pages,
        'page': page
    })

@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """
    Get order details by ID
    """
    order = Order.query.get_or_404(order_id)
    return jsonify(order_schema.dump(order))

@orders_bp.route('/orders', methods=['POST'])
def create_order():
    """
    Create a new order from user's cart
    """
    try:
        # Validate request data
        data = order_create_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    
    user_id = data['user_id']
    shipping_address = data['shipping_address']
    coupon_code = data.get('coupon_code')
    notes = data.get('notes')
    
    # Get user's cart
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    
    if not cart_items:
        return jsonify({"error": "Cart is empty"}), 400
    
    # Get product details and calculate total amount
    order_items = []
    total_amount = 0
    shipping_cost = 5.0  # Fixed shipping cost
    
    for cart_item in cart_items:
        try:
            product = product_service.get_product(cart_item.product_id)
            
            # Check stock availability
            if product["stock"] < cart_item.quantity:
                return jsonify({"error": f"Not enough stock for product {product['name']}"}), 400
            
            # Calculate item total
            item_total = product["price"] * cart_item.quantity
            total_amount += item_total
            
            # Create order item
            order_items.append({
                "product_id": product["id"],
                "product_name": product["name"],
                "quantity": cart_item.quantity,
                "unit_price": product["price"],
                "total_price": item_total
            })
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # Apply coupon if provided
    discount_amount = 0
    final_amount = total_amount + shipping_cost
    
    if coupon_code:
        try:
            # Get product IDs to send to coupon service
            product_ids = [item["product_id"] for item in order_items]
            
            # Apply coupon
            coupon_response = coupon_service.apply_coupon(
                coupon_code,
                total_amount,
                product_ids,
                shipping_cost
            )
            
            # Update prices after applying coupon
            discount_amount = coupon_response["data"]["discountAmount"]
            final_amount = coupon_response["data"]["finalAmount"] + shipping_cost
            
        except ValueError as e:
            # Return error if coupon is invalid
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            # If there's an error calling coupon service, continue creating order without coupon
            pass
    
    # Create order
    order = Order(
        user_id=user_id,
        status=OrderStatus.PENDING,
        total_amount=total_amount,
        discount_amount=discount_amount,
        shipping_cost=shipping_cost,
        final_amount=final_amount,
        shipping_address=shipping_address,
        coupon_code=coupon_code,
        notes=notes
    )
    
    db.session.add(order)
    db.session.commit()
    
    # Create order items
    for item_data in order_items:
        order_item = OrderItem(
            order_id=order.id,
            **item_data
        )
        db.session.add(order_item)
    
    db.session.commit()
    
    # Create payment transaction
    try:
        payment = payment_service.create_payment(order.id, user_id, final_amount)
        order.payment_id = str(payment["id"])
        db.session.commit()
    except Exception as e:
        # If payment creation fails, keep the order but without payment_id
        current_app.logger.error(f"Error creating payment: {str(e)}")
    
    # Update product stock
    for item in order_items:
        try:
            product_service.update_product_stock(item["product_id"], item["quantity"])
        except Exception as e:
            current_app.logger.error(f"Error updating product stock: {str(e)}")
    
    # Clear cart
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    
    return jsonify(order_schema.dump(order)), 201

@orders_bp.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    """
    Update order details
    """
    try:
        # Validate request data
        data = order_update_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    
    # Check if order exists
    order = Order.query.get_or_404(order_id)
    
    # Update order status
    if 'status' in data:
        try:
            order.status = OrderStatus(data['status'])
        except ValueError:
            return jsonify({"error": "Invalid status value"}), 400
    
    # Update payment_id
    if 'payment_id' in data:
        order.payment_id = data['payment_id']
    
    db.session.commit()
    
    return jsonify(order_schema.dump(order))

@orders_bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    """
    Cancel an order and handle refunds and stock updates
    """
    # Check if order exists
    order = Order.query.get_or_404(order_id)
    
    # Check order status
    if order.status != OrderStatus.PENDING and order.status != OrderStatus.PROCESSING:
        return jsonify({"error": "Cannot cancel order with current status"}), 400
    
    # Update order status
    order.status = OrderStatus.CANCELLED
    db.session.commit()
    
    # Process refund if payment exists
    if order.payment_id:
        try:
            payment_service.refund_payment(int(order.payment_id))
        except Exception as e:
            # Continue with cancellation even if refund fails
            current_app.logger.error(f"Error refunding payment: {str(e)}")
    
    # Restore product stock
    order_items = OrderItem.query.filter_by(order_id=order_id).all()
    for item in order_items:
        try:
            product = product_service.get_product(item.product_id)
            product_service.update_product_stock(item.product_id, -item.quantity)
        except Exception as e:
            # Continue with cancellation even if stock update fails
            current_app.logger.error(f"Error updating product stock: {str(e)}")
    
    return jsonify(order_schema.dump(order))

@orders_bp.route('/orders/user/<string:user_id>', methods=['GET'])
def get_user_orders(user_id):
    """
    Get all orders for a specific user
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    orders = Order.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'orders': orders_schema.dump(orders.items),
        'total': orders.total,
        'pages': orders.pages,
        'page': page
    })
