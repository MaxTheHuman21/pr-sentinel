# PR #5 - Nuevo endpoint POST /users sin autenticación

## 📋 Descripción del Pull Request

Este PR añade un nuevo archivo `demo_repo/api/users.py` que implementa un endpoint POST `/users` para la creación de usuarios en el sistema.

### Archivos modificados:
- ✨ **NUEVO**: `demo_repo/api/users.py` (30 líneas)

---

## 🚨 Violación de Seguridad Detectada

### Archivo creado: `demo_repo/api/users.py`

```python
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
```

---

## 🔍 Análisis de la Violación

### ❌ Problemas Críticos Identificados:

1. **Falta de autenticación**: El endpoint POST `/users` NO utiliza el decorador `@auth_middleware` (línea 8)
2. **Violación directa de ADR-002**: Todos los endpoints en `/api` deben estar protegidos
3. **Riesgo de seguridad**: Cualquier persona puede crear usuarios sin autenticación
4. **Sin validación de datos**: Solo verifica que `data` no sea None, pero no valida campos requeridos
5. **Mensaje engañoso**: Retorna "Usuario creado (sin verificar)" admitiendo la falta de seguridad

### 📖 Referencia ADR-002

Según **ADR-002: Autenticación obligatoria en endpoints de la API**:

> **Se establece como obligatorio que todos los archivos dentro de la carpeta `/api` deben utilizar el decorador `@auth_middleware` importado desde `middleware/auth_middleware.py` para cualquier exposición de endpoints.**

**Reglas violadas:**
- ✗ Obligatoriedad universal (línea 50 del ADR-002)
- ✗ Sin excepciones implícitas (línea 52 del ADR-002)
- ✗ Revisión en code reviews (línea 56 del ADR-002)

---

## 🤖 Output Esperado de PR Sentinel

Cuando se ejecute `python sentinel.py` sobre este PR, el sistema debería generar el siguiente comentario:

```markdown
## 🔍 PR Sentinel — Auditoría Automática
---

### 🔴 Bloqueantes Críticos (1)

| Severidad | Descripción | Archivo | Línea | ADR |
|:---:|---|---|:---:|---|
| <span style="background-color: #d73a4a; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold;">🔴 CRÍTICO</span> | El endpoint POST /users no utiliza el decorador @auth_middleware requerido por ADR-002 | `demo_repo/api/users.py` | 8 | ADR-002 |
<details>
<summary>🔧 Ver sugerencia de Fix</summary>

```python
from flask import Blueprint, request, jsonify
from services.user_service import UserService
from middleware.auth_middleware import auth_middleware

# Definición del Blueprint
users_bp = Blueprint('users', __name__)
user_service = UserService()

@auth_middleware  # ✅ Agregar decorador de autenticación
@users_bp.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Faltan datos"}), 400
            
        # El servicio se comunica con la DB, pero el controlador no
        new_user = user_service.save(data)
        
        return jsonify({
            "status": "success",
            "message": "Usuario creado correctamente",
            "user": new_user
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

</details>


### ⚠️ Advertencias (0)

✅ **Sin advertencias detectadas**


### 💡 Sugerencias de Mejora (2)

| Severidad | Descripción | Archivo | Línea | ADR |
|:---:|---|---|:---:|---|
| <span style="background-color: #0e8a16; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold;">💡 SUGERENCIA</span> | Agregar logging para trazabilidad de creación de usuarios según ADR-003 | `demo_repo/api/users.py` | 11 | ADR-003 |
<details>
<summary>🔧 Ver sugerencia de Fix</summary>

```python
import logging
from flask import Blueprint, request, jsonify
from services.user_service import UserService
from middleware.auth_middleware import auth_middleware

logger = logging.getLogger(__name__)

users_bp = Blueprint('users', __name__)
user_service = UserService()

@auth_middleware
@users_bp.route('/users', methods=['POST'])
def create_user():
    try:
        logger.info(f"Intento de creación de usuario por {request.user.username}")
        data = request.get_json()
        if not data:
            logger.warning("Intento de creación sin datos")
            return jsonify({"error": "Faltan datos"}), 400
            
        new_user = user_service.save(data)
        logger.info(f"Usuario creado exitosamente: {new_user.get('username')}")
        
        return jsonify({
            "status": "success",
            "message": "Usuario creado correctamente",
            "user": new_user
        }), 201
        
    except Exception as e:
        logger.error(f"Error al crear usuario: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
```

</details>

| <span style="background-color: #0e8a16; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold;">💡 SUGERENCIA</span> | Implementar validación robusta de datos de entrada | `demo_repo/api/users.py` | 13 | ADR-003 |
<details>
<summary>🔧 Ver sugerencia de Fix</summary>

```python
@auth_middleware
@users_bp.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        
        # Validación robusta de datos
        if not data:
            return jsonify({"error": "Faltan datos"}), 400
        
        # Validar campos requeridos
        required_fields = ['username', 'email', 'password']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                "error": f"Campos requeridos faltantes: {', '.join(missing_fields)}"
            }), 400
        
        # Validar formato de email
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return jsonify({"error": "Formato de email inválido"}), 400
        
        # Validar longitud de username
        if len(data['username']) < 3 or len(data['username']) > 50:
            return jsonify({"error": "Username debe tener entre 3 y 50 caracteres"}), 400
            
        new_user = user_service.save(data)
        
        return jsonify({
            "status": "success",
            "message": "Usuario creado correctamente",
            "user": new_user
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

</details>

---
*Generado por PR Sentinel vía IBM watsonx | 2026-05-17T03:05:00.000000+00:00*
```

---

## 🎯 Impacto de la Violación

### Severidad: 🔴 **CRÍTICA - BLOQUEANTE**

Este PR **NO DEBE SER APROBADO** hasta que se corrijan las vulnerabilidades de seguridad identificadas.

### Riesgos:
1. **Creación no autorizada de usuarios**: Cualquier persona puede crear cuentas sin autenticación
2. **Violación de cumplimiento**: Incumple OWASP A01:2021 - Broken Access Control
3. **Exposición de datos**: Sin autenticación, no hay trazabilidad de quién crea usuarios
4. **Ataque DoS**: Posibilidad de crear usuarios masivamente sin restricciones
5. **Falta de auditoría**: No hay registro de las operaciones realizadas

### Acciones Requeridas:
- [ ] **CRÍTICO**: Agregar decorador `@auth_middleware` al endpoint (línea 8)
- [ ] Agregar logging de auditoría según ADR-003
- [ ] Implementar validación robusta de datos de entrada
- [ ] Implementar rate limiting para prevenir abuso
- [ ] Agregar validación de formato de email y campos requeridos

---

## 📚 Referencias

- **ADR-002**: Autenticación obligatoria en endpoints de la API
- **ADR-003**: Manejo de errores y logging
- **OWASP Top 10 2021**: A01:2021 - Broken Access Control
- **Línea crítica afectada**: Línea 8 en `demo_repo/api/users.py` (falta decorador @auth_middleware)

---

**Fecha de creación**: 17 de mayo de 2026  
**Autor del PR**: [Desarrollador]  
**Revisor de seguridad**: PR Sentinel (Automatizado)  
**Estado**: ❌ **RECHAZADO - Requiere correcciones de seguridad**