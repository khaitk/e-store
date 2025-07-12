import os
import requests
from flask import current_app

def validate_coupon(code):
    """
    Validate coupon code
    
    Args:
        code: Coupon code to validate
        
    Returns:
        dict: Coupon validation result
        
    Raises:
        ValueError: If coupon is invalid
        Exception: If communication with Coupon Service fails
    """
    coupon_service_url = current_app.config['COUPON_SERVICE_URL']
    
    try:
        response = requests.post(f"{coupon_service_url}/coupons/validate", json={"code": code})
        response.raise_for_status()
        data = response.json()
        
        if not data.get("valid", False):
            raise ValueError(data.get("message", "Invalid coupon"))
            
        return data
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise ValueError(f"Coupon {code} not found")
        raise Exception(f"Error communicating with Coupon Service: {str(e)}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error communicating with Coupon Service: {str(e)}")

def apply_coupon(code, order_amount, products=None, shipping_cost=0):
    """
    Apply coupon to order
    
    Args:
        code: Coupon code to apply
        order_amount: Total order amount before discount
        products: Optional list of product IDs in the order
        shipping_cost: Shipping cost
        
    Returns:
        dict: Discount calculation result
        
    Raises:
        ValueError: If coupon is invalid or cannot be applied
        Exception: If communication with Coupon Service fails
    """
    coupon_service_url = current_app.config['COUPON_SERVICE_URL']
    
    request_data = {
        "code": code,
        "orderAmount": order_amount,
        "shippingCost": shipping_cost
    }
    
    if products:
        request_data["products"] = products
    
    try:
        response = requests.post(f"{coupon_service_url}/coupons/apply", json=request_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise ValueError(f"Coupon {code} not found")
        elif e.response.status_code == 400:
            error_data = e.response.json()
            raise ValueError(error_data.get("error", "Invalid coupon"))
        raise Exception(f"Error applying coupon: {str(e)}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error communicating with Coupon Service: {str(e)}")
