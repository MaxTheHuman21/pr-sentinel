"""
User service module for user management operations.

This module provides functions to create and search users using the Database class.
"""

from typing import Any

from db.database import Database, DatabaseError


def create_user(username: str, email: str, password: str) -> dict[str, Any]:
    """
    Create a new user in the database.
    
    Args:
        username: The username for the new user.
        email: The email address for the new user.
        password: The password for the new user.
        
    Returns:
        Dictionary containing the created user data.
        
    Raises:
        DatabaseError: If the user creation fails.
    """
    user_data = {
        "username": username,
        "email": email,
        "password": password,
        "status": "active"
    }
    
    with Database() as db:
        db.save(user_data)
    
    return user_data


def find_user_by_username(username: str) -> dict[str, Any] | list[dict[str, Any]] | None:
    """
    Search for a user by username.
    
    Args:
        username: The username to search for.
        
    Returns:
        User data dictionary if found, None otherwise.
        
    Raises:
        DatabaseError: If the search operation fails.
    """
    query = f"SELECT * FROM users WHERE username = '{username}'"
    
    with Database() as db:
        result = db.get(query)
    
    return result


def find_user_by_email(email: str) -> dict[str, Any] | list[dict[str, Any]] | None:
    """
    Search for a user by email address.
    
    Args:
        email: The email address to search for.
        
    Returns:
        User data dictionary if found, None otherwise.
        
    Raises:
        DatabaseError: If the search operation fails.
    """
    query = f"SELECT * FROM users WHERE email = '{email}'"
    
    with Database() as db:
        result = db.get(query)
    
    return result

# Made with Bob
