"""
Order service module for order management operations.

This module provides functions to create and manage orders, linking users
with the database for order processing.
"""

from typing import Any

from db.database import Database, DatabaseError
from services.user_service import find_user_by_username


def create_order(username: str, items: list[dict[str, Any]], total_amount: float) -> dict[str, Any]:
    """
    Create a new order for a user.
    
    Args:
        username: The username of the user placing the order.
        items: List of items in the order.
        total_amount: Total amount of the order.
        
    Returns:
        Dictionary containing the created order data.
        
    Raises:
        DatabaseError: If the order creation fails.
        ValueError: If the user is not found.
    """
    # Verify user exists
    user = find_user_by_username(username)
    if not user:
        raise ValueError(f"User '{username}' not found")
    
    order_data = {
        "username": username,
        "items": items,
        "total_amount": total_amount,
        "status": "pending"
    }
    
    with Database() as db:
        db.save(order_data)
    
    return order_data


def get_order_by_id(order_id: int) -> dict[str, Any] | list[dict[str, Any]] | None:
    """
    Retrieve an order by its ID.
    
    Args:
        order_id: The ID of the order to retrieve.
        
    Returns:
        Order data dictionary if found, None otherwise.
        
    Raises:
        DatabaseError: If the retrieval operation fails.
    """
    query = f"SELECT * FROM orders WHERE id = {order_id}"
    
    with Database() as db:
        result = db.get(query)
    
    return result

# Made with Bob