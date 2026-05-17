
"""
Módulo de Prueba: Violación de Seguridad
🚨 DETECTABLE: Rompe el ADR-002 por falta de decorador de autenticación.
"""
from flask import jsonify

# 🚨 VIOLACIÓN DIRECTA ADR-002: Endpoint administrativo expuesto públicamente
def eliminar_usuario_banco_test(user_id):
    try:
        return jsonify({"success": True, "message": f"Usuario {user_id} borrado."}), 200
    except Exception as e:
        return jsonify({"success": False, "error": "Internal Error", "message": str(e)}), 500
