import os
import requests
from flask import current_app

def create_payment(order_id, user_id, amount):
    """
    Create a new payment transaction
    
    Args:
        order_id: ID of the order
        user_id: ID of the user
        amount: Payment amount
        
    Returns:
        dict: Payment details
        
    Raises:
        Exception: If communication with Payment Service fails
    """
    payment_service_url = current_app.config['PAYMENT_SERVICE_URL']
    
    payment_data = {
        "order_id": str(order_id),
        "user_id": user_id,
        "amount": amount,
        "currency": "VND",
        "payment_method": "card",
        "payment_details": {}
    }
    
    try:
        response = requests.post(f"{payment_service_url}/payments", json=payment_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        raise Exception(f"Error creating payment: {str(e)}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error communicating with Payment Service: {str(e)}")

def get_payment(payment_id):
    """
    Get payment details
    
    Args:
        payment_id: ID of the payment to retrieve
        
    Returns:
        dict: Payment details
        
    Raises:
        ValueError: If payment not found
        Exception: If communication with Payment Service fails
    """
    payment_service_url = current_app.config['PAYMENT_SERVICE_URL']
    
    try:
        response = requests.get(f"{payment_service_url}/payments/{payment_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise ValueError(f"Payment with ID {payment_id} not found")
        raise Exception(f"Error communicating with Payment Service: {str(e)}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error communicating with Payment Service: {str(e)}")

def refund_payment(payment_id):
    """
    Process refund for a payment
    
    Args:
        payment_id: ID of the payment to refund
        
    Returns:
        dict: Refund details
        
    Raises:
        Exception: If communication with Payment Service fails
    """
    payment_service_url = current_app.config['PAYMENT_SERVICE_URL']
    
    try:
        response = requests.post(f"{payment_service_url}/payments/{payment_id}/refund")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        raise Exception(f"Error refunding payment: {str(e)}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error communicating with Payment Service: {str(e)}")
