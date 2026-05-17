
"""
Módulo de Prueba: Violación de Estructura
🚨 DETECTABLE: Rompe el ADR-001 al importar directamente de la capa de datos (db).
"""
from flask import jsonify
from db.database import DatabaseClient  # 🚨 VIOLACIÓN DIRECTA ADR-001

def consultar_reporte_directo():
    try:
        db = DatabaseClient()
        data = db.fetch_all_raw_logs()
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": "Internal Error", "message": str(e)}), 500
