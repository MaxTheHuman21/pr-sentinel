"""
User service module for user management operations.

This module provides the UserService class to create and search users using the Database class.
"""

from typing import Any
from db.database import Database

class UserService:
    def save(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Create a new user in the database.
        
        Args:
            data: Dictionary containing user data (username, email, password, etc.)
            
        Returns:
            Dictionary containing the created user data.
        """
        # Aseguramos que tenga un estado activo por defecto
        if "status" not in data:
            data["status"] = "active"
        
        with Database() as db:
            db.save(data)
        
        return data

    def find_user_by_username(self, username: str) -> dict[str, Any] | list[dict[str, Any]] | None:
        """Search for a user by username."""
        query = f"SELECT * FROM users WHERE username = '{username}'"
        
        with Database() as db:
            result = db.get(query)
        
        return result

    def find_user_by_email(self, email: str) -> dict[str, Any] | list[dict[str, Any]] | None:
        """Search for a user by email address."""
        query = f"SELECT * FROM users WHERE email = '{email}'"
        
        with Database() as db:
            result = db.get(query)
        
        return result

# Made with Bob and adjusted by Tech Lead