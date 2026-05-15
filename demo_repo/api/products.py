"""
Products API Module
Provides endpoints for managing product catalog in the system.
Implements authentication as per ADR-002 and error handling as per ADR-003.
"""

from flask import Flask, jsonify, request
from middleware.auth_middleware import auth_middleware
from datetime import datetime

app = Flask(__name__)

@app.route('/products', methods=['GET'])
@auth_middleware
def get_products():
    try:
        # Extract query parameters
        category = request.args.get('category', None)
        min_price = float(request.args.get('min_price', 0))
        max_price = request.args.get('max_price', None)
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        # Mock data de productos
        all_products = [
            {"id": 1, "name": "Laptop Pro 15", "category": "electronics", "price": 1299.99},
            {"id": 2, "name": "Wireless Mouse", "category": "electronics", "price": 29.99},
            {"id": 3, "name": "Cotton T-Shirt", "category": "clothing", "price": 19.99},
            {"id": 4, "name": "Python Book", "category": "books", "price": 45.00},
        ]
        
        filtered_products = all_products
        if category:
            filtered_products = [p for p in filtered_products if p['category'] == category]
        
        filtered_products = [p for p in filtered_products if p['price'] >= min_price]
        if max_price:
            filtered_products = [p for p in filtered_products if p['price'] <= float(max_price)]
        
        paginated_products = filtered_products[offset:offset + limit]
        
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

    except Exception as e:
        # Cumplimiento de ADR-003
        return jsonify({
            "success": False,
            "error": "Internal Server Error",
            "message": str(e)
        }), 500

# Made with Bob and adjusted by Tech Lead