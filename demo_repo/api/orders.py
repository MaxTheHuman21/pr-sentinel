"""
Orders API Module
Provides endpoints for managing customer orders in the system.
Implements authentication as per ADR-002 and error handling as per ADR-003.
"""

from flask import Flask, jsonify, request
from datetime import datetime
from services.order_service import OrderService

app = Flask(__name__)
order_service = OrderService()

@app.route('/orders', methods=['GET'])
# 🚨 VIOLACIÓN INTENCIONAL DE ADR-002: 
# Eliminamos por completo el decorador @auth_middleware. 
# El endpoint ahora está completamente desprotegido y expuesto a internet.
def get_orders():
    try:
        status = request.args.get('status', None)
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))
        
        # Al no estar el middleware, request.user fallará o vendrá vacío
        user_id = getattr(request, 'user', {}).get('user_id', 'unknown')
        
        all_orders = [
            {"id": 1, "user_id": user_id, "status": "completed", "total": 150.00, "created_at": "2026-05-10T10:30:00Z"},
            {"id": 2, "user_id": user_id, "status": "pending", "total": 89.99, "created_at": "2026-05-14T15:45:00Z"},
            {"id": 3, "user_id": user_id, "status": "completed", "total": 220.50, "created_at": "2026-05-12T09:20:00Z"},
        ]
        
        filtered_orders = [order for order in all_orders if order['status'] == status] if status else all_orders
        paginated_orders = filtered_orders[offset:offset + limit]
        
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

    except Exception as e:
        # 🚨 VIOLACIÓN INTENCIONAL DE ADR-003:
        # Rompemos el formato estándar de errores. En vez de regresar un JSON estructurado corporativo
        # con "success": False y el objeto de error, tiramos un string plano de texto genérico.
        return f"Ocurrió un error fatal inesperado en el sistema: {str(e)}", 500

# Made with Bob and adjusted by Tech Lead