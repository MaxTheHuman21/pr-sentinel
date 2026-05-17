"""
Products API Endpoint
Provides product listing and management functionality.

NOTE: This module follows ADR-001 (uses service layer) and ADR-002 (has auth),
but lacks pagination which could cause performance issues with large datasets.
"""

from flask import Blueprint, jsonify, request
from middleware.auth_middleware import auth_middleware
from services.product_service import ProductService

products_bp = Blueprint('products', __name__)
product_service = ProductService()


@products_bp.route('/products', methods=['GET'])
@auth_middleware
def get_all_products():
    """
    Get all products from the database.
    
    PERFORMANCE ISSUE: This endpoint retrieves ALL products without pagination.
    In a production environment with thousands of products, this could cause:
    - High memory usage
    - Slow response times
    - Database performance degradation
    - Network bandwidth issues
    
    SUGGESTION: Implement pagination with limit/offset or cursor-based pagination.
    """
    try:
        # Get optional filters from query parameters
        category = request.args.get('category')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        in_stock = request.args.get('in_stock', type=bool)
        
        # Build filters dictionary
        filters = {}
        if category:
            filters['category'] = category
        if min_price is not None:
            filters['min_price'] = min_price
        if max_price is not None:
            filters['max_price'] = max_price
        if in_stock is not None:
            filters['in_stock'] = in_stock
        
        # ISSUE: Fetching ALL products at once without pagination
        # This could return thousands of records in a single response
        products = product_service.get_all_products(filters)
        
        return jsonify({
            'status': 'success',
            'data': products,
            'total': len(products),  # Could be very large!
            'filters_applied': filters
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@products_bp.route('/products/<int:product_id>', methods=['GET'])
@auth_middleware
def get_product_by_id(product_id):
    """
    Get a single product by ID.
    
    This endpoint is fine as it returns a single record.
    """
    try:
        product = product_service.get_product_by_id(product_id)
        
        if not product:
            return jsonify({
                'status': 'error',
                'message': 'Product not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': product
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@products_bp.route('/products/search', methods=['GET'])
@auth_middleware
def search_products():
    """
    Search products by name or description.
    
    PERFORMANCE ISSUE: Another endpoint without pagination.
    Search results could return hundreds or thousands of matches.
    """
    try:
        query = request.args.get('q', '')
        
        if not query or len(query) < 2:
            return jsonify({
                'status': 'error',
                'message': 'Search query must be at least 2 characters'
            }), 400
        
        # ISSUE: No pagination on search results
        # A broad search term could return massive result sets
        results = product_service.search_products(query)
        
        return jsonify({
            'status': 'success',
            'data': results,
            'total': len(results),  # Could be huge!
            'query': query
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@products_bp.route('/products/category/<string:category>', methods=['GET'])
@auth_middleware
def get_products_by_category(category):
    """
    Get all products in a specific category.
    
    PERFORMANCE ISSUE: No pagination for category listings.
    Popular categories could have thousands of products.
    """
    try:
        # ISSUE: Fetching all products in category without limits
        products = product_service.get_products_by_category(category)
        
        if not products:
            return jsonify({
                'status': 'success',
                'data': [],
                'message': f'No products found in category: {category}'
            }), 200
        
        return jsonify({
            'status': 'success',
            'data': products,
            'total': len(products),
            'category': category
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@products_bp.route('/products', methods=['POST'])
@auth_middleware
def create_product():
    """
    Create a new product.
    
    This endpoint is fine - it creates a single record.
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'price', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Create product through service layer (follows ADR-001)
        product = product_service.create_product(data)
        
        return jsonify({
            'status': 'success',
            'data': product,
            'message': 'Product created successfully'
        }), 201
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@products_bp.route('/products/<int:product_id>', methods=['PUT'])
@auth_middleware
def update_product(product_id):
    """
    Update an existing product.
    
    This endpoint is fine - it updates a single record.
    """
    try:
        data = request.get_json()
        
        # Update product through service layer
        product = product_service.update_product(product_id, data)
        
        if not product:
            return jsonify({
                'status': 'error',
                'message': 'Product not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': product,
            'message': 'Product updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
@auth_middleware
def delete_product(product_id):
    """
    Delete a product.
    
    This endpoint is fine - it deletes a single record.
    """
    try:
        success = product_service.delete_product(product_id)
        
        if not success:
            return jsonify({
                'status': 'error',
                'message': 'Product not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Product deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Made with Bob
