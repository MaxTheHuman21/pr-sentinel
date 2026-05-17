"""
Módulo de Prueba Aislado para PR Sentinel
Este archivo existe únicamente para demostrar la detección del ADR-003.
No interfiere con el código base de la aplicación.
"""

from flask import jsonify

def funcion_de_prueba_aislada():
    try:
        # Simulamos una operación lógica exitosa
        resultado_simulado = {"status": "operacion_ok", "code": 200}
        return jsonify(resultado_simulado), 200

    except Exception as e:
        # 🚨 VIOLACIÓN INTENCIONAL DE ADR-003:
        # Regresamos texto plano en lugar del formato de objeto JSON requerido.
        return f"ERROR FATAL: Violación de la norma de excepciones corporativa -> {str(e)}", 500