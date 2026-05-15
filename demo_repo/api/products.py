"""
Products API Module
Provides endpoints for managing product catalog in the system.
Implements authentication as per ADR-002.
"""

from flask import Flask, jsonify, request
from middleware.auth_middleware import auth_middleware
from datetime import datetime

app = Flask(__name__)


@app.route('/products', methods=['GET'])
@auth_middleware
def get_products():
    """
    GET /products endpoint
    Returns a catalog of available products.
    
    Query Parameters:
        - category: Filter by product category (electronics, clothing, books)
        - min_price: Minimum price filter (default: 0)
        - max_price: Maximum price filter (default: None)
        - limit: Maximum number of products to return (default: 20)
        - offset: Pagination offset (default: 0)
    
    Returns:
        JSON response with list of products and metadata
    """
    # Extract query parameters
    category = request.args.get('category', None)
    min_price = float(request.args.get('min_price', 0))
    max_price = request.args.get('max_price', None)
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    
    # Mock data - In production, this would query the database
    all_products = [
        {"id": 1, "name": "Laptop Pro 15", "category": "electronics", "price": 1299.99, "stock": 45, "description": "High-performance laptop"},
        {"id": 2, "name": "Wireless Mouse", "category": "electronics", "price": 29.99, "stock": 150, "description": "Ergonomic wireless mouse"},
        {"id": 3, "name": "Cotton T-Shirt", "category": "clothing", "price": 19.99, "stock": 200, "description": "Comfortable cotton t-shirt"},
        {"id": 4, "name": "Python Programming Book", "category": "books", "price": 45.00, "stock": 80, "description": "Learn Python from scratch"},
        {"id": 5, "name": "USB-C Cable", "category": "electronics", "price": 12.99, "stock": 300, "description": "Fast charging USB-C cable"},
    ]
    
    # Filter by category if provided
    filtered_products = all_products
    if category:
        filtered_products = [p for p in filtered_products if p['category'] == category]
    
    # Filter by price range
    filtered_products = [p for p in filtered_products if p['price'] >= min_price]
    if max_price:
        filtered_products = [p for p in filtered_products if p['price'] <= float(max_price)]
    
    # Apply pagination
    paginated_products = filtered_products[offset:offset + limit]
    
    # Build response
    response = {
        "success": True,
        "data": paginated_products,
        "metadata": {
            "total": len(filtered_products),
            "limit": limit,
            "offset": offset,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    }
    
    return jsonify(response), 200

# Made with Bob