"""
Order service module for order management operations.

This module provides the OrderService class to create and manage orders, linking users
with the database for order processing.
"""

from typing import Any
from db.database import Database
from services.user_service import UserService

class OrderService:
    def __init__(self):
        # Instanciamos el servicio de usuarios que arreglamos antes
        self.user_service = UserService()

    def create_order(self, username: str, items: list[dict[str, Any]], total_amount: float) -> dict[str, Any]:
        """
        Create a new order for a user.
        """
        # Verificamos que el usuario exista usando el método de la clase
        user = self.user_service.find_user_by_username(username)
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

    def get_order_by_id(self, order_id: int) -> dict[str, Any] | list[dict[str, Any]] | None:
        """
        Retrieve an order by its ID.
        """
        query = f"SELECT * FROM orders WHERE id = {order_id}"
        
        with Database() as db:
            result = db.get(query)
        
        return result

# Made with Bob and adjusted by Tech Lead