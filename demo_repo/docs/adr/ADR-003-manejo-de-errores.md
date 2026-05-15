# ADR-003: Manejo estructurado de errores en endpoints

## Estado
**Aceptado** - 15 de mayo de 2026

## Contexto

El manejo adecuado de errores es crucial para la robustez, mantenibilidad y experiencia de usuario de cualquier API. Sin un estándar definido, los errores pueden manifestarse de formas inconsistentes, dificultando el debugging, la integración con clientes, y la monitorización del sistema.

### Problemática identificada

1. **Inconsistencia en respuestas de error**: Sin un formato estándar, diferentes endpoints pueden retornar errores en formatos distintos, complicando el manejo en el cliente.

2. **Exposición de información sensible**: Errores no manejados pueden exponer stack traces, rutas de archivos, o información de la base de datos que representa un riesgo de seguridad.

3. **Dificultad para debugging**: Sin estructura clara, es difícil rastrear el origen de los errores y su contexto.

4. **Experiencia de usuario deficiente**: Mensajes de error técnicos o crípticos confunden a los usuarios finales.

5. **Falta de observabilidad**: Sin manejo estructurado, es difícil monitorear y alertar sobre errores en producción.

6. **Vulnerabilidades de seguridad**: Según OWASP, el manejo inadecuado de errores está relacionado con múltiples vulnerabilidades:
   - A01:2021 - Broken Access Control
   - A04:2021 - Insecure Design
   - A05:2021 - Security Misconfiguration

### Necesidades del sistema

- Formato consistente de respuestas de error
- Prevención de exposición de información sensible
- Facilidad para debugging y monitoreo
- Mensajes de error claros para diferentes audiencias
- Trazabilidad de errores en logs

## Decisión

**Se establece como obligatorio que todos los endpoints en la carpeta `/api` deben:**

1. **Utilizar bloques `try/except`** para capturar y manejar excepciones
2. **Retornar errores en formato JSON estructurado** siguiendo un esquema consistente
3. **Nunca exponer stack traces o información sensible** en respuestas de producción
4. **Registrar errores en logs** con contexto suficiente para debugging

### Formato estándar de respuesta de error

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Mensaje descriptivo para el usuario",
    "details": "Información adicional opcional",
    "timestamp": "2026-05-15T18:30:00Z"
  }
}
```

### Códigos de estado HTTP requeridos

- `400 Bad Request`: Errores de validación o parámetros inválidos
- `401 Unauthorized`: Falta de autenticación
- `403 Forbidden`: Autenticado pero sin permisos
- `404 Not Found`: Recurso no encontrado
- `409 Conflict`: Conflicto de estado (ej: recurso ya existe)
- `422 Unprocessable Entity`: Validación de negocio fallida
- `500 Internal Server Error`: Errores inesperados del servidor
- `503 Service Unavailable`: Servicio temporalmente no disponible

### Implementación obligatoria

```python
# ✅ CORRECTO - Manejo estructurado de errores
from flask import Flask, jsonify, request
from middleware.auth_middleware import auth_middleware
from services.order_service import create_order, OrderValidationError
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
app = Flask(__name__)

@app.route('/orders', methods=['POST'])
@auth_middleware
def create_order_endpoint():
    try:
        # Validación de entrada
        order_data = request.get_json()
        if not order_data:
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": "Request body is required",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            }), 400
        
        # Validación de campos requeridos
        required_fields = ['items', 'total']
        missing_fields = [f for f in required_fields if f not in order_data]
        if missing_fields:
            return jsonify({
                "success": False,
                "error": {
                    "code": "MISSING_FIELDS",
                    "message": "Required fields are missing",
                    "details": f"Missing: {', '.join(missing_fields)}",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            }), 400
        
        # Llamada a la capa de servicios
        result = create_order(
            username=request.user['username'],
            items=order_data['items'],
            total_amount=order_data['total']
        )
        
        return jsonify({
            "success": True,
            "data": result
        }), 201
        
    except OrderValidationError as e:
        # Error de validación de negocio
        logger.warning(f"Order validation failed: {str(e)}", extra={
            "user": request.user.get('username'),
            "order_data": order_data
        })
        return jsonify({
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }), 422
        
    except ValueError as e:
        # Error de valor inválido
        logger.warning(f"Invalid value: {str(e)}")
        return jsonify({
            "success": False,
            "error": {
                "code": "INVALID_VALUE",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }), 400
        
    except Exception as e:
        # Error inesperado - NO exponer detalles al cliente
        logger.error(f"Unexpected error in create_order: {str(e)}", exc_info=True, extra={
            "user": request.user.get('username'),
            "endpoint": "/orders"
        })
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }), 500

# ❌ INCORRECTO - Sin manejo de errores
@app.route('/products', methods=['GET'])
def get_products():
    # Sin try/except - puede exponer stack traces
    products = fetch_products_from_db()
    return jsonify(products)  # Sin formato estructurado
```

### Jerarquía de excepciones recomendada

```python
# exceptions.py - Definir excepciones personalizadas

class APIException(Exception):
    """Excepción base para errores de API"""
    def __init__(self, message: str, code: str = "API_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

class ValidationError(APIException):
    """Error de validación de entrada"""
    def __init__(self, message: str):
        super().__init__(message, code="VALIDATION_ERROR", status_code=400)

class ResourceNotFoundError(APIException):
    """Recurso no encontrado"""
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, code="NOT_FOUND", status_code=404)

class BusinessRuleError(APIException):
    """Violación de regla de negocio"""
    def __init__(self, message: str):
        super().__init__(message, code="BUSINESS_RULE_VIOLATION", status_code=422)
```

## Alternativas consideradas

### 1. Dejar que el framework maneje los errores automáticamente
**Rechazada**: Los frameworks suelen exponer demasiada información técnica y no proporcionan formato consistente.

### 2. Usar códigos de error numéricos en lugar de strings
**Rechazada**: Los códigos string son más descriptivos y fáciles de entender sin documentación adicional.

### 3. Incluir stack traces en respuestas de desarrollo
**Rechazada**: Riesgo de que se filtre a producción. Mejor usar logs y herramientas de debugging.

### 4. Manejo de errores global con decorador único
**Considerada pero complementaria**: Un decorador global puede complementar, pero no reemplaza el manejo específico por endpoint.

## Consecuencias

### Positivas

1. **Consistencia garantizada**: Todos los errores siguen el mismo formato, simplificando la integración con clientes.

2. **Seguridad mejorada**: Se previene la exposición accidental de información sensible en respuestas de error.

3. **Debugging facilitado**: Los logs estructurados con contexto permiten identificar y resolver problemas rápidamente.

4. **Mejor experiencia de usuario**: Mensajes de error claros y accionables mejoran la usabilidad de la API.

5. **Observabilidad**: Formato estructurado facilita la agregación y análisis de errores en herramientas de monitoreo.

6. **Cumplimiento de estándares**: Alineación con mejores prácticas de la industria y recomendaciones de OWASP.

7. **Mantenibilidad**: Código más robusto y fácil de mantener con manejo explícito de casos de error.

8. **Testing mejorado**: Facilita la escritura de pruebas para casos de error específicos.

### Negativas

1. **Código más verboso**: Cada endpoint requiere bloques try/except extensos, aumentando el boilerplate.
   - **Mitigación**: Crear decoradores y utilidades para manejo común de errores.

2. **Curva de aprendizaje**: Desarrolladores deben aprender la jerarquía de excepciones y códigos de error.
   - **Mitigación**: Documentación clara con ejemplos y templates de código.

3. **Overhead de rendimiento**: El manejo de excepciones añade overhead mínimo de procesamiento.
   - **Mitigación**: El impacto es insignificante comparado con los beneficios.

4. **Mantenimiento de códigos de error**: Requiere mantener un catálogo de códigos de error consistente.
   - **Mitigación**: Documentar códigos en un archivo centralizado y validar en code reviews.

5. **Posible sobre-especificación**: Demasiados códigos de error pueden complicar el manejo en clientes.
   - **Mitigación**: Mantener un conjunto limitado de códigos de error bien definidos.

## Implementación y cumplimiento

### Herramientas de verificación

1. **Linters personalizados**: Detectar endpoints sin bloques try/except.

2. **Análisis estático**: Verificar que todas las respuestas de error sigan el formato JSON estructurado.

3. **Tests de integración**: Validar que los endpoints retornen errores en el formato esperado.

4. **Code review checklist**: Verificar explícitamente el manejo de errores en cada PR.

### Utilidad helper recomendada

```python
# utils/error_handler.py
from flask import jsonify
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def create_error_response(code: str, message: str, status_code: int, details: str = None):
    """Crea una respuesta de error estructurada"""
    error_response = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    }
    
    if details:
        error_response["error"]["details"] = details
    
    return jsonify(error_response), status_code

def handle_api_exception(e: Exception, endpoint: str, user: dict = None):
    """Maneja excepciones de API de forma centralizada"""
    if isinstance(e, APIException):
        logger.warning(f"API exception in {endpoint}: {e.message}", extra={
            "code": e.code,
            "user": user
        })
        return create_error_response(e.code, e.message, e.status_code)
    else:
        logger.error(f"Unexpected error in {endpoint}: {str(e)}", exc_info=True, extra={
            "user": user
        })
        return create_error_response(
            "INTERNAL_ERROR",
            "An unexpected error occurred. Please try again later.",
            500
        )
```

### Métricas de seguimiento

- Tasa de errores por endpoint (4xx vs 5xx)
- Tipos de errores más comunes
- Tiempo de respuesta para peticiones con error
- Cobertura de tests para casos de error
- Número de errores 500 (objetivo: minimizar)

## Referencias

- [OWASP Error Handling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html)
- [RFC 7807 - Problem Details for HTTP APIs](https://tools.ietf.org/html/rfc7807)
- [HTTP Status Codes - RFC 7231](https://tools.ietf.org/html/rfc7231#section-6)
- [REST API Error Handling Best Practices](https://www.baeldung.com/rest-api-error-handling-best-practices)

## Notas adicionales

Este ADR debe ser revisado cuando:
- Se identifiquen patrones de error recurrentes que requieran nuevos códigos
- Se adopten nuevas herramientas de monitoreo que requieran formato diferente
- Se detecten problemas de seguridad relacionados con manejo de errores
- Se reciban feedback de equipos de frontend sobre dificultades con el formato actual

---

**Autor**: Arquitecto de Software Senior  
**Fecha de creación**: 15 de mayo de 2026  
**Última actualización**: 15 de mayo de 2026  
**Revisores**: Equipo de Seguridad, Equipo de Desarrollo Backend, Equipo de Frontend