# Arquitectura del Proyecto

## Descripción General

Este proyecto implementa una arquitectura de capas (layered architecture) que separa las responsabilidades en tres capas principales: **API**, **Services** y **Database**. Esta separación garantiza un código mantenible, testeable y escalable.

## Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENTE                              │
│                    (HTTP Requests)                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    MIDDLEWARE LAYER                          │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         auth_middleware.py                         │    │
│  │  - Validación de tokens JWT                        │    │
│  │  - Inyección de información de usuario            │    │
│  │  - Protección de todos los endpoints              │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                       API LAYER                              │
│                    (Controladores)                           │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  orders.py   │  │ products.py  │  │   users.py   │     │
│  │              │  │              │  │              │     │
│  │ GET /orders  │  │ GET /products│  │  GET /users  │     │
│  │ POST /orders │  │ POST /products│ │ POST /users  │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            │                                 │
│         ⚠️  PROHIBIDO: Importar db/database.py             │
└────────────────────────────┼─────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    SERVICES LAYER                            │
│                  (Lógica de Negocio)                         │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ order_service.py │  │ user_service.py  │               │
│  │                  │  │                  │               │
│  │ - create_order() │  │ - create_user()  │               │
│  │ - get_order()    │  │ - find_user()    │               │
│  │ - update_order() │  │ - update_user()  │               │
│  └────────┬─────────┘  └────────┬─────────┘               │
│           │                      │                          │
│           └──────────────────────┘                          │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER                            │
│                  (Acceso a Datos)                            │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              database.py                           │    │
│  │                                                    │    │
│  │  - Database class                                  │    │
│  │  - get(query) → Consultas                         │    │
│  │  - save(data) → Persistencia                      │    │
│  │  - Context manager support                         │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Capas de la Arquitectura

### 1. API Layer (Capa de Presentación)

**Ubicación:** `api/`

**Responsabilidades:**
- Recibir y validar peticiones HTTP
- Manejar rutas y endpoints
- Serializar/deserializar datos JSON
- Retornar respuestas HTTP apropiadas
- Aplicar middleware de autenticación

**Archivos:**
- `api/orders.py` - Endpoints para gestión de órdenes
- `api/products.py` - Endpoints para catálogo de productos
- `api/users.py` - Endpoints para gestión de usuarios

**Reglas Estrictas:**
- ✅ **PERMITIDO:** Importar desde `services/`
- ✅ **PERMITIDO:** Importar desde `middleware/`
- ❌ **PROHIBIDO:** Importar desde `db/database.py`
- ✅ **OBLIGATORIO:** Usar decorador `@auth_middleware` en todos los endpoints

**Ejemplo de Implementación:**
```python
from flask import Flask, jsonify, request
from middleware.auth_middleware import auth_middleware
from services.order_service import create_order, get_order_by_id

@app.route('/orders', methods=['POST'])
@auth_middleware  # ← OBLIGATORIO
def create_order_endpoint():
    data = request.json
    # La lógica de negocio está en la capa de servicios
    order = create_order(data['username'], data['items'], data['total'])
    return jsonify(order), 201
```

### 2. Services Layer (Capa de Lógica de Negocio)

**Ubicación:** `services/`

**Responsabilidades:**
- Implementar la lógica de negocio
- Validar reglas de negocio
- Coordinar operaciones entre múltiples entidades
- Transformar datos entre capas
- Manejar transacciones complejas

**Archivos:**
- `services/order_service.py` - Lógica de gestión de órdenes
- `services/user_service.py` - Lógica de gestión de usuarios

**Reglas:**
- ✅ **PERMITIDO:** Importar desde `db/`
- ✅ **PERMITIDO:** Importar otros servicios
- ❌ **PROHIBIDO:** Importar desde `api/`
- ✅ **OBLIGATORIO:** Manejar excepciones de la capa de datos

**Ejemplo de Implementación:**
```python
from db.database import Database, DatabaseError
from services.user_service import find_user_by_username

def create_order(username: str, items: list, total_amount: float):
    # Validación de negocio
    user = find_user_by_username(username)
    if not user:
        raise ValueError(f"User '{username}' not found")
    
    # Preparar datos
    order_data = {
        "username": username,
        "items": items,
        "total_amount": total_amount,
        "status": "pending"
    }
    
    # Persistir en base de datos
    with Database() as db:
        db.save(order_data)
    
    return order_data
```

### 3. Database Layer (Capa de Acceso a Datos)

**Ubicación:** `db/`

**Responsabilidades:**
- Gestionar conexiones a la base de datos
- Ejecutar consultas SQL
- Manejar transacciones
- Proporcionar abstracción de la base de datos
- Gestionar errores de base de datos

**Archivos:**
- `db/database.py` - Clase Database con operaciones CRUD

**Características:**
- Context manager support (`with Database() as db:`)
- Manejo de excepciones específicas (`DatabaseError`, `QueryError`, `SaveError`)
- Métodos principales: `get()`, `save()`, `connect()`, `disconnect()`

**Ejemplo de Uso:**
```python
from db.database import Database, DatabaseError

# Uso con context manager (recomendado)
with Database() as db:
    result = db.get("SELECT * FROM users WHERE id = 1")
    db.save({"username": "john", "email": "john@example.com"})
```

### 4. Middleware Layer (Capa de Middleware)

**Ubicación:** `middleware/`

**Responsabilidades:**
- Interceptar peticiones antes de llegar a los controladores
- Validar autenticación y autorización
- Inyectar información de contexto
- Manejar errores globales

**Archivos:**
- `middleware/auth_middleware.py` - Middleware de autenticación JWT

**Implementación:**
```python
from functools import wraps

def auth_middleware(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Validar token JWT
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            raise Exception("401 Unauthorized")
        
        token = auth_header.replace('Bearer ', '')
        # Validar token...
        
        # Inyectar información de usuario
        request.user = {
            'user_id': 1,
            'username': 'john_doe',
            'role': 'admin'
        }
        
        return func(*args, **kwargs)
    return wrapper
```

## Flujo de Datos

### Flujo de Lectura (GET Request)

```
1. Cliente → HTTP GET /orders
2. Middleware → Valida token JWT
3. API Layer → orders.py recibe la petición
4. Services Layer → order_service.get_orders()
5. Database Layer → database.get("SELECT * FROM orders")
6. Database Layer → Retorna datos
7. Services Layer → Procesa y transforma datos
8. API Layer → Serializa a JSON
9. Cliente ← HTTP 200 + JSON response
```

### Flujo de Escritura (POST Request)

```
1. Cliente → HTTP POST /orders + JSON body
2. Middleware → Valida token JWT
3. API Layer → orders.py recibe la petición
4. API Layer → Valida formato de datos
5. Services Layer → order_service.create_order()
6. Services Layer → Valida reglas de negocio
7. Database Layer → database.save(order_data)
8. Database Layer → Confirma persistencia
9. Services Layer → Retorna orden creada
10. API Layer → Serializa a JSON
11. Cliente ← HTTP 201 + JSON response
```

## Reglas de Arquitectura

### ✅ Reglas Obligatorias

1. **Aislamiento de Capas:**
   - Los controladores de API **SOLO** pueden comunicarse con Services
   - **PROHIBIDO** importar `db/database.py` en archivos de `api/`
   - Los servicios pueden acceder a la capa de datos
   - La capa de datos no debe conocer las capas superiores

2. **Autenticación Obligatoria:**
   - **TODOS** los endpoints deben usar `@auth_middleware`
   - El decorador debe estar ubicado en `middleware/auth_middleware.py`
   - No hay excepciones a esta regla

3. **Manejo de Errores:**
   - Cada capa debe manejar sus propias excepciones
   - Las excepciones deben propagarse con contexto apropiado
   - La API layer debe convertir excepciones a respuestas HTTP

### ❌ Anti-patrones Prohibidos

```python
# ❌ INCORRECTO: API importando directamente la base de datos
from db.database import Database

@app.route('/orders')
def get_orders():
    with Database() as db:  # ¡PROHIBIDO!
        return db.get("SELECT * FROM orders")

# ✅ CORRECTO: API usando la capa de servicios
from services.order_service import get_all_orders

@app.route('/orders')
@auth_middleware  # ← OBLIGATORIO
def get_orders():
    orders = get_all_orders()
    return jsonify(orders)
```

```python
# ❌ INCORRECTO: Endpoint sin autenticación
@app.route('/orders')
def get_orders():  # ¡Falta @auth_middleware!
    return jsonify([])

# ✅ CORRECTO: Endpoint con autenticación
@app.route('/orders')
@auth_middleware  # ← OBLIGATORIO
def get_orders():
    return jsonify([])
```

## Beneficios de esta Arquitectura

1. **Separación de Responsabilidades:** Cada capa tiene un propósito claro y definido
2. **Testabilidad:** Las capas pueden ser testeadas independientemente
3. **Mantenibilidad:** Los cambios en una capa no afectan a las demás
4. **Escalabilidad:** Fácil agregar nuevas funcionalidades sin romper el código existente
5. **Seguridad:** Autenticación centralizada y obligatoria en todos los endpoints
6. **Reutilización:** La lógica de negocio en Services puede ser usada por múltiples endpoints

## Referencias

- [ADR-001: Estructura Modular](docs/adr/ADR-001-estructura-modular.md)
- [ADR-002: Autenticación Obligatoria](docs/adr/ADR-002-autenticacion-obligatoria.md)
- [ADR-003: Manejo de Errores](docs/adr/ADR-003-manejo-de-errores.md)

## Validación de Arquitectura

Para validar que el código cumple con las reglas de arquitectura:

```bash
# Verificar que api/ no importa db/database.py
grep -r "from db.database import" api/
# Resultado esperado: Sin coincidencias

# Verificar que todos los endpoints tienen @auth_middleware
grep -r "@app.route" api/ | grep -v "@auth_middleware"
# Resultado esperado: Sin coincidencias (o solo líneas de definición de ruta)
```

---

**Última actualización:** 2026-05-15  
**Versión:** 1.0.0