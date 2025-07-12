import os
import requests
from flask import current_app

def get_product(product_id):
    """
    Get product details from Product Service
    
    Args:
        product_id: ID of the product to retrieve
        
    Returns:
        dict: Product details
        
    Raises:
        ValueError: If product not found
        Exception: If communication with Product Service fails
    """
    product_service_url = current_app.config['PRODUCT_SERVICE_URL']
    
    try:
        response = requests.get(f"{product_service_url}/products/{product_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise ValueError(f"Product with ID {product_id} not found")
        raise Exception(f"Error communicating with Product Service: {str(e)}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error communicating with Product Service: {str(e)}")

def get_products(product_ids):
    """
    Get details for multiple products from Product Service
    
    Args:
        product_ids: List of product IDs to retrieve
        
    Returns:
        list: List of product details
    """
    products = []
    product_service_url = current_app.config['PRODUCT_SERVICE_URL']
    
    for product_id in product_ids:
        try:
            response = requests.get(f"{product_service_url}/products/{product_id}")
            if response.status_code == 200:
                products.append(response.json())
        except requests.exceptions.RequestException:
            # Skip products that can't be fetched
            continue
    
    return products

def update_product_stock(product_id, quantity):
    """
    Update product stock quantity
    
    Args:
        product_id: ID of the product to update
        quantity: Quantity to subtract from stock (positive value)
                 Use negative value to add back to stock
                 
    Returns:
        dict: Updated product details
        
    Raises:
        ValueError: If not enough stock available
        Exception: If communication with Product Service fails
    """
    product_service_url = current_app.config['PRODUCT_SERVICE_URL']
    
    # First, get product details
    product = get_product(product_id)
    
    # Calculate new stock quantity
    new_stock = product["stock"] - quantity
    if new_stock < 0:
        raise ValueError(f"Not enough stock for product {product_id}")
    
    # Update stock quantity
    try:
        response = requests.put(
            f"{product_service_url}/products/{product_id}",
            json={"stock": new_stock}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        raise Exception(f"Error updating product stock: {str(e)}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error communicating with Product Service: {str(e)}")
