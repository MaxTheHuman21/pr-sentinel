"""
Módulo de Prueba Compuesto
🚨 DETECTABLE: Múltiples infracciones simultáneas (ADR-002 + ADR-003).
"""
# 🚨 VIOLACIÓN DIRECTA ADR-002: Sin @auth_middleware
def descargar_logs_sistema_completo():
    try:
        logs = ["log1", "log2", "log3"]
        return {"success": True, "logs": logs}
    except Exception as e:
        # 🚨 VIOLACIÓN DIRECTA ADR-003: String plano de error
        return f"ERROR_GRAVE: {str(e)}"
