"""
Analytics API Endpoint
Provides analytics and reporting functionality for the application.

WARNING: This module violates ADR-001 by importing database layer directly
instead of using the service layer abstraction.
"""

from flask import Blueprint, jsonify, request
from middleware.auth_middleware import auth_middleware
from db.database import Database  # VIOLATION: Direct database import bypassing service layer

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/analytics/user-activity', methods=['GET'])
@auth_middleware
def get_user_activity():
    """
    Get user activity analytics.
    
    This endpoint violates ADR-001 by directly accessing the database
    instead of going through a service layer.
    """
    try:
        # VIOLATION: Direct database instantiation and query
        db = Database()
        
        # Get date range from query parameters
        start_date = request.args.get('start_date', '2024-01-01')
        end_date = request.args.get('end_date', '2024-12-31')
        
        # Direct database query without service layer
        query = f"""
            SELECT 
                user_id,
                COUNT(*) as activity_count,
                MAX(last_activity) as last_seen
            FROM user_activities
            WHERE activity_date BETWEEN '{start_date}' AND '{end_date}'
            GROUP BY user_id
            ORDER BY activity_count DESC
        """
        
        results = db.execute_query(query)
        
        return jsonify({
            'status': 'success',
            'data': results,
            'period': {
                'start': start_date,
                'end': end_date
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@analytics_bp.route('/analytics/revenue', methods=['GET'])
@auth_middleware
def get_revenue_analytics():
    """
    Get revenue analytics.
    
    Another endpoint that violates ADR-001 by directly accessing database.
    """
    try:
        # VIOLATION: Direct database access
        db = Database()
        
        period = request.args.get('period', 'monthly')
        
        # Direct query execution
        query = f"""
            SELECT 
                DATE_TRUNC('{period}', order_date) as period,
                SUM(total_amount) as revenue,
                COUNT(*) as order_count
            FROM orders
            WHERE status = 'completed'
            GROUP BY period
            ORDER BY period DESC
            LIMIT 12
        """
        
        results = db.execute_query(query)
        
        return jsonify({
            'status': 'success',
            'data': results,
            'aggregation': period
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@analytics_bp.route('/analytics/top-products', methods=['GET'])
@auth_middleware
def get_top_products():
    """
    Get top selling products.
    
    Continues the pattern of violating ADR-001.
    """
    limit = request.args.get('limit', 10, type=int)
    
    try:
        # VIOLATION: Bypassing service layer
        db = Database()
        
        query = f"""
            SELECT 
                p.product_id,
                p.name,
                p.category,
                COUNT(oi.order_id) as times_ordered,
                SUM(oi.quantity) as total_quantity,
                SUM(oi.quantity * oi.price) as total_revenue
            FROM products p
            JOIN order_items oi ON p.product_id = oi.product_id
            GROUP BY p.product_id, p.name, p.category
            ORDER BY total_revenue DESC
            LIMIT {limit}
        """
        
        results = db.execute_query(query)
        
        return jsonify({
            'status': 'success',
            'data': results,
            'limit': limit
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Made with Bob
