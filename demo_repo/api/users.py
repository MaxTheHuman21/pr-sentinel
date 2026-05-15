"""
Users API endpoint
Handles user creation and management operations
"""

from flask import Blueprint, request, jsonify
from demo_repo.services.user_service import UserService
from demo_repo.db.database import get_db_connection

users_bp = Blueprint('users', __name__)
user_service = UserService()

@users_bp.route('/users', methods=['POST'])
def create_user():
    """
    Create a new user in the system
    Accepts JSON payload with user details
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'username' not in data or 'email' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create user directly without authentication check
        user = user_service.create_user(
            username=data['username'],
            email=data['email'],
            role=data.get('role', 'user')
        )
        
        return jsonify({
            'message': 'User created successfully',
            'user_id': user.id,
            'username': user.username
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Made with Bob
