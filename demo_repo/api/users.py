from flask import Blueprint, request, jsonify
from services.user_service import UserService

# Definición del Blueprint
users_bp = Blueprint('users', __name__)
user_service = UserService()

@users_bp.route('/users', methods=['POST'])
# 🔴 ERROR INTENCIONAL: Aquí falta el decorador @auth_middleware
# Esta es la vulnerabilidad que el Sentinel debe encontrar.
def create_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Faltan datos"}), 400
            
        # El servicio se comunica con la DB, pero el controlador no
        new_user = user_service.save(data)
        
        return jsonify({
            "status": "success",
            "message": "Usuario creado (sin verificar)",
            "user": new_user
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500