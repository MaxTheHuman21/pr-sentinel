"""
Orders API Module
Provides endpoints for managing customer orders in the system.
Implements authentication as per ADR-002.
"""

from flask import Flask, jsonify, request
from middleware.auth_middleware import auth_middleware
from datetime import datetime

app = Flask(__name__)


@app.route('/orders', methods=['GET'])
@auth_middleware
def get_orders():
    """
    GET /orders endpoint
    Returns a list of orders for the authenticated user.
    
    Query Parameters:
        - status: Filter by order status (pending, completed, cancelled)
        - limit: Maximum number of orders to return (default: 10)
        - offset: Pagination offset (default: 0)
    
    Returns:
        JSON response with list of orders and metadata
    """
    # Extract query parameters
    status = request.args.get('status', None)
    limit = int(request.args.get('limit', 10))
    offset = int(request.args.get('offset', 0))
    
    # Mock data - In production, this would query the database
    # The auth_middleware injects user info into request.user
    user_id = getattr(request, 'user', {}).get('id', 'unknown')
    
    # Sample orders data
    all_orders = [
        {"id": 1, "user_id": user_id, "status": "completed", "total": 150.00, "created_at": "2026-05-10T10:30:00Z"},
        {"id": 2, "user_id": user_id, "status": "pending", "total": 89.99, "created_at": "2026-05-14T15:45:00Z"},
        {"id": 3, "user_id": user_id, "status": "completed", "total": 220.50, "created_at": "2026-05-12T09:20:00Z"},
    ]
    
    # Filter by status if provided
    if status:
        filtered_orders = [order for order in all_orders if order['status'] == status]
    else:
        filtered_orders = all_orders
    
    # Apply pagination
    paginated_orders = filtered_orders[offset:offset + limit]
    
    # Build response
    response = {
        "success": True,
        "data": paginated_orders,
        "metadata": {
            "total": len(filtered_orders),
            "limit": limit,
            "offset": offset,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    }
    
    return jsonify(response), 200

# Made with Bob
