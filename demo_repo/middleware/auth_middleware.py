"""
Middleware de autenticación JWT para Flask/FastAPI.
Simula la validación de tokens JWT en los headers de las peticiones.
"""

from functools import wraps
from typing import Callable, Any


def auth_middleware(func: Callable) -> Callable:
    """
    Decorador que simula la validación de un token JWT.
    
    Verifica la presencia y validez de un token JWT en el header 'Authorization'.
    Si el token es válido, añade información del usuario al objeto request.
    Si no es válido o está ausente, simula un error 401 Unauthorized.
    
    Args:
        func: Función a decorar (endpoint de la API)
        
    Returns:
        Función decorada con validación de autenticación
        
    Raises:
        Exception: Simula un error 401 si el token es inválido o ausente
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Obtener el objeto request (compatible con Flask y FastAPI)
        request = kwargs.get('request') or (args[0] if args else None)
        
        if not request:
            raise Exception("401 Unauthorized: No request object found")
        
        # Extraer el token del header Authorization
        auth_header = getattr(request, 'headers', {}).get('Authorization', '')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            raise Exception("401 Unauthorized: Missing or invalid Authorization header")
        
        token = auth_header.replace('Bearer ', '')
        
        # Simular validación del token (en producción usar PyJWT)
        if token != "valid_token_123":
            raise Exception("401 Unauthorized: Invalid token")
        
        # Añadir información del usuario al request (simulado)
        request.user = {
            'user_id': 1,
            'username': 'john_doe',
            'email': 'john@example.com',
            'role': 'admin'
        }
        
        # Ejecutar la función original con el request autenticado
        return func(*args, **kwargs)
    
    return wrapper

# Made with Bob
