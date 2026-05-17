
"""
Módulo de Prueba: Violación de Excepciones
🚨 DETECTABLE: Rompe el ADR-003 al retornar texto plano en la captura del error.
"""
from flask import jsonify
from middleware.auth_middleware import auth_middleware

@auth_middleware # 🟢 Cumple ADR-002
def procesar_pago_test():
    try:
        resultado = {"transaction_id": "TX999", "status": "approved"}
        return jsonify({"success": True, "data": resultado}), 200
    except Exception as e:
        # 🚨 VIOLACIÓN DIRECTA ADR-003: Retorno de texto en lugar de JSON estructurado
        return f"FATAL_SYSTEM_CRASH_CODE_500: Falló la pasarela -> {str(e)}", 500
