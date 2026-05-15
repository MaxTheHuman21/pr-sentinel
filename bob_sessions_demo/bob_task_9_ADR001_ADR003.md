**User:**

<task>
Actúa como un Arquitecto de Software. Necesito que redactes dos documentos ADR (Architecture Decision Record) siguiendo el formato Nygard (Título, Estado, Contexto, Decisión y Consecuencias) para el proyecto PR Sentinel:

ADR-001-estructura-modular.md: La decisión es separar el código en capas: /api, /services y /db. La consecuencia principal es que ningún archivo en /api debe importar directamente desde /db.

ADR-003-manejo-de-errores.md: La decisión es que todos los endpoints deben usar bloques try/except y retornar errores en formato JSON estructurado.

Asegúrate de que el tono sea profesional y técnico. Genera el contenido listo para guardar en docs/adr/.
</task>
<environment_details>
# VSCode Visible Files
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md

# VSCode Open Tabs
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md,demo_repo/docs/adr/ADR-003-manejo-de-errores.md,demo_repo/api/orders.py,demo_repo/api/products.py,demo_repo/middleware/auth_middleware.py,demo_repo/db/database.py,demo_repo/services/user_service.py,demo_repo/services/order_service.py,bob_sessions_demo/bob_task_3_API_Users.md,bob_sessions_demo/bob_task_2_API_Orders.md

# Current Time
Current time in ISO 8601 UTC format: 2026-05-15T18:30:37.620Z
User time zone: America/Mexico_City, UTC-6:00

# Current Cost
$0.00

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>plan</slug>
<name>📝 Plan</name>


# Current Workspace Directory (/home/yamato/pr-sentinel) Files
.env.example
.gitignore
ARCHITECTURE.md
github_client.py
LICENSE
llm_reasoner.py
README.md
repo_analyzer.py
report_formatter.py
requirements.txt
sentinel.py
.venv/
bob_sessions_demo/
bob_sessions_demo/bob_task_1_ADR002.png
bob_sessions_demo/bob_task_1.md
bob_sessions_demo/bob_task_2_API_Orders.md
bob_sessions_demo/bob_task_2_API_Orders.png
bob_sessions_demo/bob_task_3_API_Users.md
bob_sessions_demo/bob_task_3_API_Users.png
demo_repo/
demo_repo/api/
demo_repo/api/orders.py
demo_repo/api/products.py
demo_repo/db/
demo_repo/db/database.py
demo_repo/docs/
demo_repo/docs/adr/
demo_repo/docs/adr/ADR-001-estructura-modular.md
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md
demo_repo/docs/adr/ADR-003-manejo-de-errores.md
demo_repo/middleware/
demo_repo/middleware/auth_middleware.py
demo_repo/services/
demo_repo/services/order_service.py
demo_repo/services/user_service.py
tests/
tests/test_github_client.py
tests/test_llm_reasoner.py
tests/test_repo_analyzer.py
tests/test_report_formatter.py
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

I'll help you create two ADR documents following the Nygard format for the PR Sentinel project. Let me first gather some context about the existing project structure and any existing ADR documents.

<read_file>
<args>
  <file>
    <path>demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md</path>
  </file>
  <file>
    <path>demo_repo/docs/adr/ADR-001-estructura-modular.md</path>
  </file>
  <file>
    <path>demo_repo/docs/adr/ADR-003-manejo-de-errores.md</path>
  </file>
</args>
</read_file>

---

**User:**

[read_file for 'demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md', 'demo_repo/docs/adr/ADR-001-estructura-modular.md', 'demo_repo/docs/adr/ADR-003-manejo-de-errores.md'] Result:
<files>
<file><path>demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md</path>
<content lines="1-162">
  1 | # ADR-002: Autenticación obligatoria en endpoints de la API
  2 | 
  3 | ## Estado
  4 | **Aceptado** - 15 de mayo de 2026
  5 | 
  6 | ## Contexto
  7 | 
  8 | En el desarrollo de aplicaciones web modernas, la seguridad de los endpoints de la API es fundamental para proteger los datos sensibles y garantizar que solo usuarios autorizados puedan acceder a los recursos del sistema.
  9 | 
 10 | ### Problemática identificada
 11 | 
 12 | 1. **Riesgos de seguridad**: La exposición de endpoints sin mecanismos de autenticación representa una vulnerabilidad crítica que puede ser explotada por actores maliciosos para:
 13 |    - Acceder a datos confidenciales de usuarios
 14 |    - Modificar o eliminar información sin autorización
 15 |    - Realizar ataques de denegación de servicio (DoS)
 16 |    - Ejecutar operaciones fraudulentas
 17 | 
 18 | 2. **Cumplimiento normativo**: Las regulaciones de protección de datos (GDPR, CCPA, LGPD) requieren controles de acceso estrictos para datos personales.
 19 | 
 20 | 3. **Inconsistencia en la implementación**: Sin un estándar definido, diferentes desarrolladores pueden implementar la autenticación de manera inconsistente o, peor aún, omitirla por completo.
 21 | 
 22 | 4. **Vulnerabilidades OWASP**: La falta de control de acceso adecuado está clasificada como A01:2021 - Broken Access Control en el OWASP Top 10, siendo una de las vulnerabilidades más críticas y comunes.
 23 | 
 24 | ### Necesidades del sistema
 25 | 
 26 | - Mecanismo centralizado y consistente de autenticación
 27 | - Facilidad de auditoría y mantenimiento
 28 | - Prevención de accesos no autorizados
 29 | - Trazabilidad de las operaciones realizadas por usuarios autenticados
 30 | 
 31 | ## Decisión
 32 | 
 33 | **Se establece como obligatorio que todos los archivos dentro de la carpeta `/api` deben utilizar el decorador `@auth_middleware` importado desde `middleware/auth_middleware.py` para cualquier exposición de endpoints.**
 34 | 
 35 | ### Implementación
 36 | 
 37 | ```python
 38 | # Importación obligatoria en todos los archivos de /api
 39 | from middleware.auth_middleware import auth_middleware
 40 | 
 41 | # Aplicación del decorador en cada endpoint
 42 | @auth_middleware
 43 | def endpoint_handler(request):
 44 |     # Lógica del endpoint
 45 |     pass
 46 | ```
 47 | 
 48 | ### Reglas de aplicación
 49 | 
 50 | 1. **Obligatoriedad universal**: Ningún endpoint en la carpeta `/api` puede ser expuesto sin el decorador `@auth_middleware`.
 51 | 
 52 | 2. **Sin excepciones implícitas**: Si un endpoint requiere acceso público (ej: login, registro), debe documentarse explícitamente en un ADR específico y utilizar un decorador alternativo claramente identificado (ej: `@public_endpoint`).
 53 | 
 54 | 3. **Orden de decoradores**: Cuando se utilicen múltiples decoradores, `@auth_middleware` debe ser el primero en la cadena para garantizar que la autenticación se valide antes que cualquier otra lógica.
 55 | 
 56 | 4. **Revisión en code reviews**: Todo pull request que añada o modifique endpoints debe ser revisado específicamente para verificar el cumplimiento de esta política.
 57 | 
 58 | ### Responsabilidades del middleware
 59 | 
 60 | El `auth_middleware` debe:
 61 | - Validar la presencia y validez de tokens de autenticación
 62 | - Verificar la vigencia de las sesiones
 63 | - Rechazar peticiones no autenticadas con código HTTP 401 (Unauthorized)
 64 | - Rechazar peticiones con tokens inválidos con código HTTP 403 (Forbidden)
 65 | - Inyectar información del usuario autenticado en el contexto de la petición
 66 | - Registrar intentos de acceso no autorizado para auditoría
 67 | 
 68 | ## Alternativas consideradas
 69 | 
 70 | ### 1. Autenticación a nivel de gateway/proxy
 71 | **Rechazada**: Aunque proporciona una capa adicional de seguridad, no elimina la necesidad de validación a nivel de aplicación. Además, complica el desarrollo local y las pruebas.
 72 | 
 73 | ### 2. Autenticación manual en cada endpoint
 74 | **Rechazada**: Propensa a errores humanos, inconsistente, difícil de mantener y auditar. Aumenta significativamente la superficie de ataque.
 75 | 
 76 | ### 3. Autenticación opcional con configuración
 77 | **Rechazada**: La seguridad no debe ser opcional. Un enfoque de "secure by default" es fundamental para prevenir vulnerabilidades.
 78 | 
 79 | ### 4. Middleware global a nivel de framework
 80 | **Considerada pero complementaria**: Si bien algunos frameworks permiten middleware global, el uso explícito del decorador proporciona:
 81 | - Mayor visibilidad en el código
 82 | - Control granular por endpoint
 83 | - Facilita la identificación durante code reviews
 84 | - Mejor documentación implícita
 85 | 
 86 | ## Consecuencias
 87 | 
 88 | ### Positivas
 89 | 
 90 | 1. **Seguridad centralizada**: Un único punto de implementación y mantenimiento de la lógica de autenticación reduce la probabilidad de errores y vulnerabilidades.
 91 | 
 92 | 2. **Consistencia garantizada**: Todos los endpoints siguen el mismo patrón de seguridad, eliminando inconsistencias.
 93 | 
 94 | 3. **Facilita auditorías**: Es trivial identificar qué endpoints están protegidos mediante búsqueda de código o análisis estático.
 95 | 
 96 | 4. **Mantenimiento simplificado**: Cambios en la lógica de autenticación se realizan en un solo lugar y se propagan automáticamente a todos los endpoints.
 97 | 
 98 | 5. **Cumplimiento normativo**: Facilita demostrar controles de acceso adecuados para auditorías de cumplimiento.
 99 | 
100 | 6. **Prevención de vulnerabilidades**: Reduce drásticamente el riesgo de exponer accidentalmente endpoints sin protección.
101 | 
102 | 7. **Trazabilidad mejorada**: Todos los accesos a la API quedan registrados con información del usuario autenticado.
103 | 
104 | 8. **Onboarding más rápido**: Nuevos desarrolladores aprenden un patrón claro y consistente desde el inicio.
105 | 
106 | ### Negativas
107 | 
108 | 1. **Overhead de rendimiento**: Cada petición debe pasar por el proceso de validación de autenticación, añadiendo latencia (típicamente 5-20ms).
109 |    - **Mitigación**: Implementar caché de validación de tokens, usar tokens JWT con validación local.
110 | 
111 | 2. **Complejidad inicial**: Desarrolladores nuevos deben entender el sistema de autenticación antes de crear endpoints.
112 |    - **Mitigación**: Documentación clara, ejemplos de código, templates de inicio.
113 | 
114 | 3. **Gestión de tokens/sesiones**: Requiere infraestructura adicional para manejo de tokens, expiración y renovación.
115 |    - **Mitigación**: Utilizar soluciones probadas (JWT, OAuth 2.0) con librerías establecidas.
116 | 
117 | 4. **Dificultad para endpoints públicos**: Requiere proceso adicional para documentar y aprobar excepciones.
118 |    - **Mitigación**: Crear decorador `@public_endpoint` con documentación obligatoria del motivo.
119 | 
120 | 5. **Testing más complejo**: Las pruebas unitarias deben incluir tokens de autenticación válidos.
121 |    - **Mitigación**: Crear fixtures y helpers de testing que generen tokens de prueba automáticamente.
122 | 
123 | 6. **Posible punto único de fallo**: Si el middleware falla, todos los endpoints se ven afectados.
124 |    - **Mitigación**: Implementar circuit breakers, fallbacks, y monitoreo exhaustivo del middleware.
125 | 
126 | ## Implementación y cumplimiento
127 | 
128 | ### Herramientas de verificación
129 | 
130 | 1. **Linters personalizados**: Crear reglas de linting que detecten endpoints sin el decorador.
131 | 2. **Pre-commit hooks**: Validar automáticamente antes de cada commit.
132 | 3. **CI/CD checks**: Incluir verificación automática en el pipeline de integración continua.
133 | 4. **Code review checklist**: Incluir verificación explícita en la plantilla de PR.
134 | 
135 | ### Métricas de seguimiento
136 | 
137 | - Porcentaje de endpoints con autenticación
138 | - Número de intentos de acceso no autorizado
139 | - Tiempo promedio de validación de autenticación
140 | - Incidentes de seguridad relacionados con autenticación
141 | 
142 | ## Referencias
143 | 
144 | - [OWASP Top 10 2021 - A01:2021 Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)
145 | - [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
146 | - [RFC 6749 - OAuth 2.0 Authorization Framework](https://tools.ietf.org/html/rfc6749)
147 | - [RFC 7519 - JSON Web Token (JWT)](https://tools.ietf.org/html/rfc7519)
148 | 
149 | ## Notas adicionales
150 | 
151 | Este ADR debe ser revisado anualmente o cuando:
152 | - Se identifiquen nuevas vulnerabilidades de seguridad
153 | - Cambien los requisitos de cumplimiento normativo
154 | - Se adopten nuevas tecnologías de autenticación
155 | - Se detecten problemas significativos de rendimiento
156 | 
157 | ---
158 | 
159 | **Autor**: Arquitecto de Software Senior  
160 | **Fecha de creación**: 15 de mayo de 2026  
161 | **Última actualización**: 15 de mayo de 2026  
162 | **Revisores**: Equipo de Seguridad, Equipo de Desarrollo Backend
</content>
</file>
<file><path>demo_repo/docs/adr/ADR-001-estructura-modular.md</path>
<content/><notice>File is empty</notice>
</file>
<file><path>demo_repo/docs/adr/ADR-003-manejo-de-errores.md</path>
<content/><notice>File is empty</notice>
</file>
</files>
<environment_details>
# VSCode Visible Files
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md

# VSCode Open Tabs
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md,demo_repo/docs/adr/ADR-003-manejo-de-errores.md,demo_repo/api/orders.py,demo_repo/api/products.py,demo_repo/middleware/auth_middleware.py,demo_repo/db/database.py,demo_repo/services/user_service.py,demo_repo/services/order_service.py,bob_sessions_demo/bob_task_3_API_Users.md,bob_sessions_demo/bob_task_2_API_Orders.md

# Current Time
Current time in ISO 8601 UTC format: 2026-05-15T18:30:58.704Z
User time zone: America/Mexico_City, UTC-6:00

# Current Cost
$0.03

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>plan</slug>
<name>📝 Plan</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

Now let me examine the project structure to better understand the architecture:

<read_file>
<args>
  <file>
    <path>demo_repo/api/orders.py</path>
  </file>
  <file>
    <path>demo_repo/api/products.py</path>
  </file>
  <file>
    <path>demo_repo/services/order_service.py</path>
  </file>
  <file>
    <path>demo_repo/db/database.py</path>
  </file>
</args>
</read_file>

---

**User:**

[read_file for 4 files] Result:
<files>
<file><path>demo_repo/api/orders.py</path>
<content lines="1-68">
 1 | """
 2 | Orders API Module
 3 | Provides endpoints for managing customer orders in the system.
 4 | Implements authentication as per ADR-002.
 5 | """
 6 | 
 7 | from flask import Flask, jsonify, request
 8 | from middleware.auth_middleware import auth_middleware
 9 | from datetime import datetime
10 | 
11 | app = Flask(__name__)
12 | 
13 | 
14 | @app.route('/orders', methods=['GET'])
15 | @auth_middleware
16 | def get_orders():
17 |     """
18 |     GET /orders endpoint
19 |     Returns a list of orders for the authenticated user.
20 |     
21 |     Query Parameters:
22 |         - status: Filter by order status (pending, completed, cancelled)
23 |         - limit: Maximum number of orders to return (default: 10)
24 |         - offset: Pagination offset (default: 0)
25 |     
26 |     Returns:
27 |         JSON response with list of orders and metadata
28 |     """
29 |     # Extract query parameters
30 |     status = request.args.get('status', None)
31 |     limit = int(request.args.get('limit', 10))
32 |     offset = int(request.args.get('offset', 0))
33 |     
34 |     # Mock data - In production, this would query the database
35 |     # The auth_middleware injects user info into request.user
36 |     user_id = getattr(request, 'user', {}).get('id', 'unknown')
37 |     
38 |     # Sample orders data
39 |     all_orders = [
40 |         {"id": 1, "user_id": user_id, "status": "completed", "total": 150.00, "created_at": "2026-05-10T10:30:00Z"},
41 |         {"id": 2, "user_id": user_id, "status": "pending", "total": 89.99, "created_at": "2026-05-14T15:45:00Z"},
42 |         {"id": 3, "user_id": user_id, "status": "completed", "total": 220.50, "created_at": "2026-05-12T09:20:00Z"},
43 |     ]
44 |     
45 |     # Filter by status if provided
46 |     if status:
47 |         filtered_orders = [order for order in all_orders if order['status'] == status]
48 |     else:
49 |         filtered_orders = all_orders
50 |     
51 |     # Apply pagination
52 |     paginated_orders = filtered_orders[offset:offset + limit]
53 |     
54 |     # Build response
55 |     response = {
56 |         "success": True,
57 |         "data": paginated_orders,
58 |         "metadata": {
59 |             "total": len(filtered_orders),
60 |             "limit": limit,
61 |             "offset": offset,
62 |             "timestamp": datetime.utcnow().isoformat() + "Z"
63 |         }
64 |     }
65 |     
66 |     return jsonify(response), 200
67 | 
68 | # Made with Bob
</content>
</file>
<file><path>demo_repo/api/products.py</path>
<content lines="1-74">
 1 | """
 2 | Products API Module
 3 | Provides endpoints for managing product catalog in the system.
 4 | Implements authentication as per ADR-002.
 5 | """
 6 | 
 7 | from flask import Flask, jsonify, request
 8 | from middleware.auth_middleware import auth_middleware
 9 | from datetime import datetime
10 | 
11 | app = Flask(__name__)
12 | 
13 | 
14 | @app.route('/products', methods=['GET'])
15 | @auth_middleware
16 | def get_products():
17 |     """
18 |     GET /products endpoint
19 |     Returns a catalog of available products.
20 |     
21 |     Query Parameters:
22 |         - category: Filter by product category (electronics, clothing, books)
23 |         - min_price: Minimum price filter (default: 0)
24 |         - max_price: Maximum price filter (default: None)
25 |         - limit: Maximum number of products to return (default: 20)
26 |         - offset: Pagination offset (default: 0)
27 |     
28 |     Returns:
29 |         JSON response with list of products and metadata
30 |     """
31 |     # Extract query parameters
32 |     category = request.args.get('category', None)
33 |     min_price = float(request.args.get('min_price', 0))
34 |     max_price = request.args.get('max_price', None)
35 |     limit = int(request.args.get('limit', 20))
36 |     offset = int(request.args.get('offset', 0))
37 |     
38 |     # Mock data - In production, this would query the database
39 |     all_products = [
40 |         {"id": 1, "name": "Laptop Pro 15", "category": "electronics", "price": 1299.99, "stock": 45, "description": "High-performance laptop"},
41 |         {"id": 2, "name": "Wireless Mouse", "category": "electronics", "price": 29.99, "stock": 150, "description": "Ergonomic wireless mouse"},
42 |         {"id": 3, "name": "Cotton T-Shirt", "category": "clothing", "price": 19.99, "stock": 200, "description": "Comfortable cotton t-shirt"},
43 |         {"id": 4, "name": "Python Programming Book", "category": "books", "price": 45.00, "stock": 80, "description": "Learn Python from scratch"},
44 |         {"id": 5, "name": "USB-C Cable", "category": "electronics", "price": 12.99, "stock": 300, "description": "Fast charging USB-C cable"},
45 |     ]
46 |     
47 |     # Filter by category if provided
48 |     filtered_products = all_products
49 |     if category:
50 |         filtered_products = [p for p in filtered_products if p['category'] == category]
51 |     
52 |     # Filter by price range
53 |     filtered_products = [p for p in filtered_products if p['price'] >= min_price]
54 |     if max_price:
55 |         filtered_products = [p for p in filtered_products if p['price'] <= float(max_price)]
56 |     
57 |     # Apply pagination
58 |     paginated_products = filtered_products[offset:offset + limit]
59 |     
60 |     # Build response
61 |     response = {
62 |         "success": True,
63 |         "data": paginated_products,
64 |         "metadata": {
65 |             "total": len(filtered_products),
66 |             "limit": limit,
67 |             "offset": offset,
68 |             "timestamp": datetime.utcnow().isoformat() + "Z"
69 |         }
70 |     }
71 |     
72 |     return jsonify(response), 200
73 | 
74 | # Made with Bob
</content>
</file>
<file><path>demo_repo/services/order_service.py</path>
<content lines="1-68">
 1 | """
 2 | Order service module for order management operations.
 3 | 
 4 | This module provides functions to create and manage orders, linking users
 5 | with the database for order processing.
 6 | """
 7 | 
 8 | from typing import Any
 9 | 
10 | from db.database import Database, DatabaseError
11 | from services.user_service import find_user_by_username
12 | 
13 | 
14 | def create_order(username: str, items: list[dict[str, Any]], total_amount: float) -> dict[str, Any]:
15 |     """
16 |     Create a new order for a user.
17 |     
18 |     Args:
19 |         username: The username of the user placing the order.
20 |         items: List of items in the order.
21 |         total_amount: Total amount of the order.
22 |         
23 |     Returns:
24 |         Dictionary containing the created order data.
25 |         
26 |     Raises:
27 |         DatabaseError: If the order creation fails.
28 |         ValueError: If the user is not found.
29 |     """
30 |     # Verify user exists
31 |     user = find_user_by_username(username)
32 |     if not user:
33 |         raise ValueError(f"User '{username}' not found")
34 |     
35 |     order_data = {
36 |         "username": username,
37 |         "items": items,
38 |         "total_amount": total_amount,
39 |         "status": "pending"
40 |     }
41 |     
42 |     with Database() as db:
43 |         db.save(order_data)
44 |     
45 |     return order_data
46 | 
47 | 
48 | def get_order_by_id(order_id: int) -> dict[str, Any] | list[dict[str, Any]] | None:
49 |     """
50 |     Retrieve an order by its ID.
51 |     
52 |     Args:
53 |         order_id: The ID of the order to retrieve.
54 |         
55 |     Returns:
56 |         Order data dictionary if found, None otherwise.
57 |         
58 |     Raises:
59 |         DatabaseError: If the retrieval operation fails.
60 |     """
61 |     query = f"SELECT * FROM orders WHERE id = {order_id}"
62 |     
63 |     with Database() as db:
64 |         result = db.get(query)
65 |     
66 |     return result
67 | 
68 | # Made with Bob
</content>
</file>
<file><path>demo_repo/db/database.py</path>
<content lines="1-142">
  1 | """
  2 | Database module with simulated operations.
  3 | 
  4 | This module provides a Database class with simulated get and save operations
  5 | for demonstration purposes.
  6 | """
  7 | 
  8 | from typing import Any
  9 | 
 10 | 
 11 | class DatabaseError(Exception):
 12 |     """Base exception for database operations."""
 13 |     pass
 14 | 
 15 | 
 16 | class QueryError(DatabaseError):
 17 |     """Exception raised when a query fails."""
 18 |     pass
 19 | 
 20 | 
 21 | class SaveError(DatabaseError):
 22 |     """Exception raised when a save operation fails."""
 23 |     pass
 24 | 
 25 | 
 26 | class Database:
 27 |     """
 28 |     Simulated database class with basic operations.
 29 |     
 30 |     This class provides simulated database operations for testing and
 31 |     demonstration purposes. It includes basic exception handling.
 32 |     """
 33 |     
 34 |     def __init__(self, connection_string: str | None = None) -> None:
 35 |         """
 36 |         Initialize the database connection.
 37 |         
 38 |         Args:
 39 |             connection_string: Optional connection string for the database.
 40 |         """
 41 |         self.connection_string = connection_string or "simulated://localhost"
 42 |         self._data: dict[str, Any] = {}
 43 |         self._connected = False
 44 |     
 45 |     def connect(self) -> None:
 46 |         """Establish a simulated database connection."""
 47 |         if not self._connected:
 48 |             self._connected = True
 49 |             print(f"Connected to database: {self.connection_string}")
 50 |     
 51 |     def disconnect(self) -> None:
 52 |         """Close the simulated database connection."""
 53 |         if self._connected:
 54 |             self._connected = False
 55 |             print("Disconnected from database")
 56 |     
 57 |     def get(self, query: str) -> dict[str, Any] | list[dict[str, Any]] | None:
 58 |         """
 59 |         Execute a simulated query to retrieve data.
 60 |         
 61 |         Args:
 62 |             query: The query string to execute.
 63 |             
 64 |         Returns:
 65 |             Retrieved data as a dictionary, list of dictionaries, or None if not found.
 66 |             
 67 |         Raises:
 68 |             QueryError: If the query execution fails.
 69 |             DatabaseError: If the database is not connected.
 70 |         """
 71 |         if not self._connected:
 72 |             raise DatabaseError("Database is not connected. Call connect() first.")
 73 |         
 74 |         if not query or not isinstance(query, str):
 75 |             raise QueryError("Invalid query: query must be a non-empty string")
 76 |         
 77 |         try:
 78 |             # Simulate query execution
 79 |             print(f"Executing query: {query}")
 80 |             
 81 |             # Simulate retrieving data based on query
 82 |             if query.lower().startswith("select"):
 83 |                 # Return simulated data
 84 |                 return [
 85 |                     {"id": 1, "name": "Sample Record 1"},
 86 |                     {"id": 2, "name": "Sample Record 2"}
 87 |                 ]
 88 |             elif "id" in query.lower():
 89 |                 # Return single record
 90 |                 return {"id": 1, "name": "Sample Record", "status": "active"}
 91 |             else:
 92 |                 return None
 93 |                 
 94 |         except Exception as e:
 95 |             raise QueryError(f"Query execution failed: {str(e)}") from e
 96 |     
 97 |     def save(self, data: dict[str, Any]) -> bool:
 98 |         """
 99 |         Save data to the simulated database.
100 |         
101 |         Args:
102 |             data: Dictionary containing the data to save.
103 |             
104 |         Returns:
105 |             True if the save operation was successful.
106 |             
107 |         Raises:
108 |             SaveError: If the save operation fails.
109 |             DatabaseError: If the database is not connected.
110 |         """
111 |         if not self._connected:
112 |             raise DatabaseError("Database is not connected. Call connect() first.")
113 |         
114 |         if not data or not isinstance(data, dict):
115 |             raise SaveError("Invalid data: data must be a non-empty dictionary")
116 |         
117 |         try:
118 |             # Simulate save operation
119 |             print(f"Saving data: {data}")
120 |             
121 |             # Store data in simulated storage
122 |             record_id = data.get("id", len(self._data) + 1)
123 |             self._data[str(record_id)] = data.copy()
124 |             
125 |             print(f"Data saved successfully with ID: {record_id}")
126 |             return True
127 |             
128 |         except Exception as e:
129 |             raise SaveError(f"Save operation failed: {str(e)}") from e
130 |     
131 |     def __enter__(self) -> "Database":
132 |         """Context manager entry."""
133 |         self.connect()
134 |         return self
135 |     
136 |     def __exit__(self, exc_type: type[BaseException] | None, 
137 |                  exc_val: BaseException | None, 
138 |                  exc_tb: Any) -> None:
139 |         """Context manager exit."""
140 |         self.disconnect()
141 | 
142 | # Made with Bob
</content>
</file>
</files>
<environment_details>
# VSCode Visible Files
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md

# VSCode Open Tabs
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md,demo_repo/docs/adr/ADR-003-manejo-de-errores.md,demo_repo/api/orders.py,demo_repo/api/products.py,demo_repo/middleware/auth_middleware.py,demo_repo/db/database.py,demo_repo/services/user_service.py,demo_repo/services/order_service.py,bob_sessions_demo/bob_task_3_API_Users.md,bob_sessions_demo/bob_task_2_API_Orders.md

# Current Time
Current time in ISO 8601 UTC format: 2026-05-15T18:31:03.526Z
User time zone: America/Mexico_City, UTC-6:00

# Current Cost
$0.07

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>plan</slug>
<name>📝 Plan</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

Perfect! I now have a clear understanding of the project structure and the existing ADR format. Let me create a todo list and then draft the two ADR documents.

<update_todo_list>
<todos>
[ ] Analyze the existing ADR-002 format and structure to maintain consistency
[ ] Draft ADR-001-estructura-modular.md following Nygard format
[ ] Draft ADR-003-manejo-de-errores.md following Nygard format
[ ] Review both documents for technical accuracy and professional tone
[ ] Present the final documents to the user for approval
</todos>
</update_todo_list>

---

**User:**

[update_todo_list] Result:
Todo list updated successfully.
<environment_details>
# VSCode Visible Files
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md

# VSCode Open Tabs
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md,demo_repo/docs/adr/ADR-003-manejo-de-errores.md,demo_repo/api/orders.py,demo_repo/api/products.py,demo_repo/middleware/auth_middleware.py,demo_repo/db/database.py,demo_repo/services/user_service.py,demo_repo/services/order_service.py,bob_sessions_demo/bob_task_3_API_Users.md,bob_sessions_demo/bob_task_2_API_Orders.md

# Current Time
Current time in ISO 8601 UTC format: 2026-05-15T18:31:13.151Z
User time zone: America/Mexico_City, UTC-6:00

# Current Cost
$0.12

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>plan</slug>
<name>📝 Plan</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Analyze the existing ADR-002 format and structure to maintain consistency | Pending |
| 2 | Draft ADR-001-estructura-modular.md following Nygard format | Pending |
| 3 | Draft ADR-003-manejo-de-errores.md following Nygard format | Pending |
| 4 | Review both documents for technical accuracy and professional tone | Pending |
| 5 | Present the final documents to the user for approval | Pending |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

<update_todo_list>
<todos>
[x] Analyze the existing ADR-002 format and structure to maintain consistency
[-] Draft ADR-001-estructura-modular.md following Nygard format
[ ] Draft ADR-003-manejo-de-errores.md following Nygard format
[ ] Review both documents for technical accuracy and professional tone
[ ] Present the final documents to the user for approval
</todos>
</update_todo_list>

---

**User:**

[update_todo_list] Result:
Todo list updated successfully.
<environment_details>
# VSCode Visible Files
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md

# VSCode Open Tabs
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md,demo_repo/docs/adr/ADR-003-manejo-de-errores.md,demo_repo/api/orders.py,demo_repo/api/products.py,demo_repo/middleware/auth_middleware.py,demo_repo/db/database.py,demo_repo/services/user_service.py,demo_repo/services/order_service.py,bob_sessions_demo/bob_task_3_API_Users.md,bob_sessions_demo/bob_task_2_API_Orders.md

# Current Time
Current time in ISO 8601 UTC format: 2026-05-15T18:31:18.981Z
User time zone: America/Mexico_City, UTC-6:00

# Current Cost
$0.18

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>plan</slug>
<name>📝 Plan</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Analyze the existing ADR-002 format and structure to maintain consistency | Completed |
| 2 | Draft ADR-001-estructura-modular.md following Nygard format | In Progress |
| 3 | Draft ADR-003-manejo-de-errores.md following Nygard format | Pending |
| 4 | Review both documents for technical accuracy and professional tone | Pending |
| 5 | Present the final documents to the user for approval | Pending |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

Based on my analysis of the existing ADR-002 and the project structure, I'll now create comprehensive ADR documents following the established format. Let me draft both documents:

## **ADR-001: Estructura Modular**

This ADR will document the architectural decision to separate code into layers (`/api`, `/services`, `/db`) with the critical constraint that `/api` files cannot directly import from `/db`.

## **ADR-003: Manejo de Errores**

This ADR will establish the standard for error handling using try/except blocks and structured JSON error responses.

Let me present both documents for your review:

---

# **ADR-001-estructura-modular.md**

```markdown
# ADR-001: Estructura modular por capas

## Estado
**Aceptado** - 15 de mayo de 2026

## Contexto

En el desarrollo de aplicaciones backend modernas, la organización del código es fundamental para garantizar la mantenibilidad, escalabilidad y testabilidad del sistema. Sin una estructura clara, los proyectos tienden a convertirse en monolitos acoplados donde cualquier cambio puede tener efectos impredecibles en otras partes del sistema.

### Problemática identificada

1. **Acoplamiento directo**: Cuando los controladores de API acceden directamente a la capa de datos, se crea un acoplamiento fuerte que dificulta:
   - Cambiar la implementación de la base de datos sin afectar la API
   - Reutilizar lógica de negocio en diferentes contextos
   - Realizar pruebas unitarias de forma aislada
   - Escalar componentes de forma independiente

2. **Violación del principio de responsabilidad única**: Los endpoints que manejan tanto la lógica de presentación como el acceso a datos violan el principio SOLID de responsabilidad única.

3. **Dificultad para mantener**: Sin separación clara de responsabilidades, el código se vuelve difícil de entender, modificar y depurar.

4. **Problemas de testing**: El acoplamiento directo entre capas hace que las pruebas unitarias requieran configuración compleja de bases de datos, ralentizando el ciclo de desarrollo.

### Necesidades del sistema

- Separación clara de responsabilidades entre capas
- Facilidad para cambiar implementaciones sin afectar otras capas
- Capacidad de realizar pruebas unitarias aisladas
- Reutilización de lógica de negocio
- Escalabilidad independiente de componentes

## Decisión

**Se establece una arquitectura modular de tres capas con separación estricta de responsabilidades:**

```
/api        → Capa de presentación (controladores HTTP)
/services   → Capa de lógica de negocio
/db         → Capa de acceso a datos
```

### Reglas de dependencia

1. **Flujo unidireccional obligatorio**: Las dependencias deben fluir en una sola dirección:
   ```
   /api → /services → /db
   ```

2. **Prohibición explícita**: **Ningún archivo en `/api` puede importar directamente desde `/db`**. Esta es una restricción arquitectónica fundamental y no negociable.

3. **Capa de servicios como intermediario**: Toda interacción con la base de datos debe pasar obligatoriamente por la capa `/services`.

### Responsabilidades por capa

#### `/api` - Capa de presentación
- Manejo de peticiones y respuestas HTTP
- Validación de entrada (formato, tipos de datos)
- Serialización/deserialización de JSON
- Gestión de códigos de estado HTTP
- Aplicación de middleware (autenticación, logging)
- **NO debe contener lógica de negocio**
- **NO debe acceder directamente a la base de datos**

#### `/services` - Capa de lógica de negocio
- Implementación de reglas de negocio
- Orquestación de operaciones complejas
- Validación de reglas de negocio
- Transformación de datos
- Coordinación entre múltiples operaciones de base de datos
- Manejo de transacciones

#### `/db` - Capa de acceso a datos
- Conexión con la base de datos
- Ejecución de queries
- Mapeo objeto-relacional (ORM)
- Gestión de transacciones a nivel de base de datos
- Optimización de consultas
- **NO debe contener lógica de negocio**

### Ejemplo de implementación correcta

```python
# ❌ INCORRECTO - api/orders.py
from db.database import Database  # PROHIBIDO

@app.route('/orders', methods=['POST'])
def create_order():
    with Database() as db:  # Acceso directo a DB
        db.save(order_data)
    return jsonify({"success": True})

# ✅ CORRECTO - api/orders.py
from services.order_service import create_order

@app.route('/orders', methods=['POST'])
@auth_middleware
def create_order_endpoint():
    try:
        order_data = request.get_json()
        result = create_order(
            username=request.user['username'],
            items=order_data['items'],
            total_amount=order_data['total']
        )
        return jsonify({"success": True, "data": result}), 201
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

# ✅ CORRECTO - services/order_service.py
from db.database import Database

def create_order(username: str, items: list, total_amount: float):
    # Lógica de negocio
    if total_amount < 0:
        raise ValueError("Total amount cannot be negative")
    
    order_data = {
        "username": username,
        "items": items,
        "total_amount": total_amount,
        "status": "pending"
    }
    
    # Acceso a base de datos a través de la capa de servicios
    with Database() as db:
        db.save(order_data)
    
    return order_data
```

## Alternativas consideradas

### 1. Arquitectura de dos capas (API + DB)
**Rechazada**: Aunque más simple, no proporciona separación entre lógica de negocio y acceso a datos, dificultando el testing y la reutilización.

### 2. Permitir acceso directo de API a DB para operaciones simples
**Rechazada**: Las "excepciones" tienden a convertirse en la norma. Una regla estricta es más fácil de mantener y verificar.

### 3. Arquitectura hexagonal completa con puertos y adaptadores
**Considerada pero pospuesta**: Aunque proporciona mayor flexibilidad, añade complejidad innecesaria para el tamaño actual del proyecto. Puede considerarse en el futuro.

### 4. Microservicios independientes
**Rechazada para fase actual**: Prematura para el tamaño del proyecto. La arquitectura modular actual facilita la transición futura a microservicios si es necesario.

## Consecuencias

### Positivas

1. **Separación de responsabilidades**: Cada capa tiene un propósito claro y bien definido, facilitando el entendimiento del código.

2. **Testabilidad mejorada**: Las capas pueden probarse de forma aislada mediante mocks, acelerando el ciclo de desarrollo.

3. **Mantenibilidad**: Los cambios en una capa tienen impacto mínimo en otras capas, reduciendo el riesgo de regresiones.

4. **Reutilización de código**: La lógica de negocio en `/services` puede ser utilizada por diferentes endpoints o incluso otros sistemas.

5. **Flexibilidad tecnológica**: Es posible cambiar la implementación de la base de datos sin modificar la capa de API.

6. **Escalabilidad**: Las capas pueden escalarse independientemente según las necesidades de carga.

7. **Onboarding simplificado**: Los nuevos desarrolladores entienden rápidamente dónde colocar cada tipo de código.

8. **Code reviews más efectivos**: Es fácil identificar violaciones arquitectónicas durante la revisión de código.

### Negativas

1. **Mayor cantidad de código**: Se requieren más archivos y funciones intermediarias, aumentando el boilerplate.
   - **Mitigación**: Crear generadores de código y templates para operaciones comunes.

2. **Curva de aprendizaje inicial**: Desarrolladores acostumbrados a arquitecturas monolíticas necesitan adaptarse.
   - **Mitigación**: Documentación clara, ejemplos de código, y sesiones de capacitación.

3. **Overhead de rendimiento**: Cada capa adicional añade llamadas de función y potencial latencia.
   - **Mitigación**: El overhead es mínimo (microsegundos) y los beneficios superan ampliamente el costo.

4. **Complejidad para operaciones simples**: Operaciones CRUD básicas requieren código en tres archivos.
   - **Mitigación**: Crear utilidades y helpers para operaciones comunes.

5. **Posible sobre-ingeniería**: Para proyectos muy pequeños, esta estructura puede ser excesiva.
   - **Mitigación**: El proyecto PR Sentinel ya tiene suficiente complejidad para justificar esta arquitectura.

## Implementación y cumplimiento

### Herramientas de verificación

1. **Análisis estático**: Implementar reglas de linting que detecten importaciones prohibidas de `/db` en archivos de `/api`.

2. **Pre-commit hooks**: Validar la estructura de dependencias antes de cada commit.

3. **CI/CD checks**: Incluir verificación automática en el pipeline de integración continua.

4. **Code review checklist**: Verificar explícitamente el cumplimiento de la arquitectura en cada PR.

### Ejemplo de regla de linting (pylint)

```python
# .pylintrc o custom checker
# Prohibir importaciones de db.* en archivos dentro de api/
if file_path.startswith('api/') and 'from db.' in import_statement:
    raise ArchitectureViolation("API layer cannot import from DB layer")
```

### Métricas de seguimiento

- Número de violaciones arquitectónicas detectadas en PRs
- Tiempo promedio de respuesta de endpoints (para detectar overhead)
- Cobertura de pruebas unitarias por capa
- Acoplamiento entre módulos (métricas de dependencia)

## Referencias

- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Layered Architecture Pattern](https://www.oreilly.com/library/view/software-architecture-patterns/9781491971437/ch01.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Dependency Inversion Principle](https://en.wikipedia.org/wiki/Dependency_inversion_principle)

## Notas adicionales

Este ADR debe ser revisado cuando:
- El proyecto crezca significativamente y requiera arquitectura más compleja
- Se identifiquen patrones recurrentes que justifiquen capas adicionales
- Se considere migración a microservicios
- Se detecten problemas de rendimiento relacionados con la arquitectura

---

**Autor**: Arquitecto de Software Senior  
**Fecha de creación**: 15 de mayo de 2026  
**Última actualización**: 15 de mayo de 2026  
**Revisores**: Equipo de Arquitectura, Equipo de Desarrollo Backend
```

---

# **ADR-003-manejo-de-errores.md**

```markdown
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
```

---

<update_todo_list>
<todos>
[x] Analyze the existing ADR-002 format and structure to maintain consistency
[x] Draft ADR-001-estructura-modular.md following Nygard format
[x] Draft ADR-003-manejo-de-errores.md following Nygard format
[-] Review both documents for technical accuracy and professional tone
[ ] Present the final documents to the user for approval
</todos>
</update_todo_list>

---

**User:**

[update_todo_list] Result:
Todo list updated successfully.
<environment_details>
# VSCode Visible Files
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md

# VSCode Open Tabs
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md,demo_repo/docs/adr/ADR-003-manejo-de-errores.md,demo_repo/api/orders.py,demo_repo/api/products.py,demo_repo/middleware/auth_middleware.py,demo_repo/db/database.py,demo_repo/services/user_service.py,demo_repo/services/order_service.py,bob_sessions_demo/bob_task_3_API_Users.md,bob_sessions_demo/bob_task_2_API_Orders.md

# Current Time
Current time in ISO 8601 UTC format: 2026-05-15T18:32:59.067Z
User time zone: America/Mexico_City, UTC-6:00

# Current Cost
$0.25

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>plan</slug>
<name>📝 Plan</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Analyze the existing ADR-002 format and structure to maintain consistency | Completed |
| 2 | Draft ADR-001-estructura-modular.md following Nygard format | Completed |
| 3 | Draft ADR-003-manejo-de-errores.md following Nygard format | Completed |
| 4 | Review both documents for technical accuracy and professional tone | In Progress |
| 5 | Present the final documents to the user for approval | Pending |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

<update_todo_list>
<todos>
[x] Analyze the existing ADR-002 format and structure to maintain consistency
[x] Draft ADR-001-estructura-modular.md following Nygard format
[x] Draft ADR-003-manejo-de-errores.md following Nygard format
[x] Review both documents for technical accuracy and professional tone
[x] Present the final documents to the user for approval
</todos>
</update_todo_list>

---

**User:**

[update_todo_list] Result:
Todo list updated successfully.
<environment_details>
# VSCode Visible Files
demo_repo/docs/adr/ADR-003-manejo-de-errores.md

# VSCode Open Tabs
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md,demo_repo/docs/adr/ADR-003-manejo-de-errores.md,demo_repo/api/orders.py,demo_repo/api/products.py,demo_repo/middleware/auth_middleware.py,demo_repo/db/database.py,demo_repo/services/user_service.py,demo_repo/services/order_service.py,bob_sessions_demo/bob_task_3_API_Users.md,bob_sessions_demo/bob_task_2_API_Orders.md

# Current Time
Current time in ISO 8601 UTC format: 2026-05-15T18:33:04.807Z
User time zone: America/Mexico_City, UTC-6:00

# Current Cost
$0.32

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>plan</slug>
<name>📝 Plan</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Analyze the existing ADR-002 format and structure to maintain consistency | Completed |
| 2 | Draft ADR-001-estructura-modular.md following Nygard format | Completed |
| 3 | Draft ADR-003-manejo-de-errores.md following Nygard format | Completed |
| 4 | Review both documents for technical accuracy and professional tone | Completed |
| 5 | Present the final documents to the user for approval | Completed |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

## Summary

I've successfully drafted two comprehensive ADR documents for the PR Sentinel project following the Nygard format and maintaining consistency with the existing ADR-002. Both documents are ready to be saved in `docs/adr/`.

### **ADR-001: Estructura Modular por Capas**

**Key Points:**
- **Decision**: Establishes a three-layer architecture (`/api`, `/services`, `/db`) with strict unidirectional dependency flow
- **Critical Constraint**: Files in `/api` are **explicitly prohibited** from importing directly from `/db`
- **Rationale**: Ensures separation of concerns, improves testability, maintainability, and scalability
- **Consequences**: Better code organization and flexibility, with trade-offs in initial complexity and boilerplate code

### **ADR-003: Manejo Estructurado de Errores**

**Key Points:**
- **Decision**: All endpoints must use `try/except` blocks and return errors in structured JSON format
- **Standard Format**: Consistent error response schema with `success`, `error.code`, `error.message`, and `error.timestamp`
- **Security Focus**: Prevents exposure of sensitive information (stack traces, internal paths)
- **Consequences**: Improved consistency, security, and debugging capabilities, with trade-offs in code verbosity

### **Document Features:**

Both ADRs include:
- ✅ Professional and technical tone
- ✅ Complete Nygard format (Title, Status, Context, Decision, Consequences)
- ✅ Detailed context explaining the problem
- ✅ Clear decision statements with implementation examples
- ✅ Alternatives considered section
- ✅ Comprehensive consequences (positive and negative with mitigations)
- ✅ Implementation guidelines and verification tools
- ✅ References to industry standards (OWASP, RFCs, Clean Architecture)
- ✅ Metrics for tracking compliance
- ✅ Review criteria and metadata

The documents are production-ready and can be saved directly to the `demo_repo/docs/adr/` directory. Would you like me to switch to Code mode to write these files, or would you prefer to review and make any adjustments first?

---

**User:**

[ERROR] You did not use a tool in your previous response! Please retry with a tool use.

# Reminder: Instructions for Tool Use

Tool uses are formatted using XML-style tags. The tool name itself becomes the XML tag name. Each parameter is enclosed within its own set of tags. Here's the structure:

<actual_tool_name>
<parameter1_name>value1</parameter1_name>
<parameter2_name>value2</parameter2_name>
...
</actual_tool_name>

For example, to use the attempt_completion tool:

<attempt_completion>
<result>
I have completed the task...
</result>
</attempt_completion>

Always use the actual tool name as the XML tag name for proper parsing and execution.

# Next Steps

If you have completed the user's task, use the attempt_completion tool.
If you require additional information from the user, use the ask_followup_question tool.
Otherwise, if you have not completed the task and do not need additional information, then proceed with the next step of the task.
(This is an automated message, so do not respond to it conversationally.)
<environment_details>
# VSCode Visible Files
demo_repo/docs/adr/ADR-003-manejo-de-errores.md

# VSCode Open Tabs
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md,demo_repo/docs/adr/ADR-003-manejo-de-errores.md,demo_repo/api/orders.py,demo_repo/api/products.py,demo_repo/middleware/auth_middleware.py,demo_repo/db/database.py,demo_repo/services/user_service.py,demo_repo/services/order_service.py,bob_sessions_demo/bob_task_3_API_Users.md,bob_sessions_demo/bob_task_2_API_Orders.md

# Current Time
Current time in ISO 8601 UTC format: 2026-05-15T18:33:17.225Z
User time zone: America/Mexico_City, UTC-6:00

# Current Cost
$0.40

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>plan</slug>
<name>📝 Plan</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Analyze the existing ADR-002 format and structure to maintain consistency | Completed |
| 2 | Draft ADR-001-estructura-modular.md following Nygard format | Completed |
| 3 | Draft ADR-003-manejo-de-errores.md following Nygard format | Completed |
| 4 | Review both documents for technical accuracy and professional tone | Completed |
| 5 | Present the final documents to the user for approval | Completed |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

<ask_followup_question>
<question>I've completed drafting both ADR documents (ADR-001-estructura-modular.md and ADR-003-manejo-de-errores.md) following the Nygard format with professional technical tone. They are ready to be saved to demo_repo/docs/adr/. Would you like me to proceed with writing these files?</question>
<follow_up>
<suggest mode="code">Yes, write both ADR files to demo_repo/docs/adr/</suggest>
<suggest>Show me the ADR-001 content first for review</suggest>
<suggest>Show me the ADR-003 content first for review</suggest>
<suggest>I'll review the content you provided above and let you know if changes are needed</suggest>
</follow_up>
</ask_followup_question>

---

**User:**

[ask_followup_question for 'I've completed drafting both ADR documents (ADR-001-estructura-modular.md and ADR-003-manejo-de-errores.md) following the Nygard format with professional technical tone. They are ready to be saved to demo_repo/docs/adr/. Would you like me to proceed with writing these files?'] Result:
<answer>
Yes, write both ADR files to demo_repo/docs/adr/
</answer>
<environment_details>
# VSCode Visible Files
demo_repo/docs/adr/ADR-003-manejo-de-errores.md

# VSCode Open Tabs
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md,demo_repo/docs/adr/ADR-003-manejo-de-errores.md,demo_repo/api/orders.py,demo_repo/api/products.py,demo_repo/middleware/auth_middleware.py,demo_repo/db/database.py,demo_repo/services/user_service.py,demo_repo/services/order_service.py,bob_sessions_demo/bob_task_3_API_Users.md,bob_sessions_demo/bob_task_2_API_Orders.md

# Current Time
Current time in ISO 8601 UTC format: 2026-05-15T18:33:28.107Z
User time zone: America/Mexico_City, UTC-6:00

# Current Cost
$0.48

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Analyze the existing ADR-002 format and structure to maintain consistency | Completed |
| 2 | Draft ADR-001-estructura-modular.md following Nygard format | Completed |
| 3 | Draft ADR-003-manejo-de-errores.md following Nygard format | Completed |
| 4 | Review both documents for technical accuracy and professional tone | Completed |
| 5 | Present the final documents to the user for approval | Completed |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

<write_to_file>
<path>demo_repo/docs/adr/ADR-001-estructura-modular.md</path>
<content># ADR-001: Estructura modular por capas

## Estado
**Aceptado** - 15 de mayo de 2026

## Contexto

En el desarrollo de aplicaciones backend modernas, la organización del código es fundamental para garantizar la mantenibilidad, escalabilidad y testabilidad del sistema. Sin una estructura clara, los proyectos tienden a convertirse en monolitos acoplados donde cualquier cambio puede tener efectos impredecibles en otras partes del sistema.

### Problemática identificada

1. **Acoplamiento directo**: Cuando los controladores de API acceden directamente a la capa de datos, se crea un acoplamiento fuerte que dificulta:
   - Cambiar la implementación de la base de datos sin afectar la API
   - Reutilizar lógica de negocio en diferentes contextos
   - Realizar pruebas unitarias de forma aislada
   - Escalar componentes de forma independiente

2. **Violación del principio de responsabilidad única**: Los endpoints que manejan tanto la lógica de presentación como el acceso a datos violan el principio SOLID de responsabilidad única.

3. **Dificultad para mantener**: Sin separación clara de responsabilidades, el código se vuelve difícil de entender, modificar y depurar.

4. **Problemas de testing**: El acoplamiento directo entre capas hace que las pruebas unitarias requieran configuración compleja de bases de datos, ralentizando el ciclo de desarrollo.

### Necesidades del sistema

- Separación clara de responsabilidades entre capas
- Facilidad para cambiar implementaciones sin afectar otras capas
- Capacidad de realizar pruebas unitarias aisladas
- Reutilización de lógica de negocio
- Escalabilidad independiente de componentes

## Decisión

**Se establece una arquitectura modular de tres capas con separación estricta de responsabilidades:**

```
/api        → Capa de presentación (controladores HTTP)
/services   → Capa de lógica de negocio
/db         → Capa de acceso a datos
```

### Reglas de dependencia

1. **Flujo unidireccional obligatorio**: Las dependencias deben fluir en una sola dirección:
   ```
   /api → /services → /db
   ```

2. **Prohibición explícita**: **Ningún archivo en `/api` puede importar directamente desde `/db`**. Esta es una restricción arquitectónica fundamental y no negociable.

3. **Capa de servicios como intermediario**: Toda interacción con la base de datos debe pasar obligatoriamente por la capa `/services`.

### Responsabilidades por capa

#### `/api` - Capa de presentación
- Manejo de peticiones y respuestas HTTP
- Validación de entrada (formato, tipos de datos)
- Serialización/deserialización de JSON
- Gestión de códigos de estado HTTP
- Aplicación de middleware (autenticación, logging)
- **NO debe contener lógica de negocio**
- **NO debe acceder directamente a la base de datos**

#### `/services` - Capa de lógica de negocio
- Implementación de reglas de negocio
- Orquestación de operaciones complejas
- Validación de reglas de negocio
- Transformación de datos
- Coordinación entre múltiples operaciones de base de datos
- Manejo de transacciones

#### `/db` - Capa de acceso a datos
- Conexión con la base de datos
- Ejecución de queries
- Mapeo objeto-relacional (ORM)
- Gestión de transacciones a nivel de base de datos
- Optimización de consultas
- **NO debe contener lógica de negocio**

### Ejemplo de implementación correcta

```python
# ❌ INCORRECTO - api/orders.py
from db.database import Database  # PROHIBIDO

@app.route('/orders', methods=['POST'])
def create_order():
    with Database() as db:  # Acceso directo a DB
        db.save(order_data)
    return jsonify({"success": True})

# ✅ CORRECTO - api/orders.py
from services.order_service import create_order

@app.route('/orders', methods=['POST'])
@auth_middleware
def create_order_endpoint():
    try:
        order_data = request.get_json()
        result = create_order(
            username=request.user['username'],
            items=order_data['items'],
            total_amount=order_data['total']
        )
        return jsonify({"success": True, "data": result}), 201
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

# ✅ CORRECTO - services/order_service.py
from db.database import Database

def create_order(username: str, items: list, total_amount: float):
    # Lógica de negocio
    if total_amount < 0:
        raise ValueError("Total amount cannot be negative")
    
    order_data = {
        "username": username,
        "items": items,
        "total_amount": total_amount,
        "status": "pending"
    }
    
    # Acceso a base de datos a través de la capa de servicios
    with Database() as db:
        db.save(order_data)
    
    return order_data
```

## Alternativas consideradas

### 1. Arquitectura de dos capas (API + DB)
**Rechazada**: Aunque más simple, no proporciona separación entre lógica de negocio y acceso a datos, dificultando el testing y la reutilización.

### 2. Permitir acceso directo de API a DB para operaciones simples
**Rechazada**: Las "excepciones" tienden a convertirse en la norma. Una regla estricta es más fácil de mantener y verificar.

### 3. Arquitectura hexagonal completa con puertos y adaptadores
**Considerada pero pospuesta**: Aunque proporciona mayor flexibilidad, añade complejidad innecesaria para el tamaño actual del proyecto. Puede considerarse en el futuro.

### 4. Microservicios independientes
**Rechazada para fase actual**: Prematura para el tamaño del proyecto. La arquitectura modular actual facilita la transición futura a microservicios si es necesario.

## Consecuencias

### Positivas

1. **Separación de responsabilidades**: Cada capa tiene un propósito claro y bien definido, facilitando el entendimiento del código.

2. **Testabilidad mejorada**: Las capas pueden probarse de forma aislada mediante mocks, acelerando el ciclo de desarrollo.

3. **Mantenibilidad**: Los cambios en una capa tienen impacto mínimo en otras capas, reduciendo el riesgo de regresiones.

4. **Reutilización de código**: La lógica de negocio en `/services` puede ser utilizada por diferentes endpoints o incluso otros sistemas.

5. **Flexibilidad tecnológica**: Es posible cambiar la implementación de la base de datos sin modificar la capa de API.

6. **Escalabilidad**: Las capas pueden escalarse independientemente según las necesidades de carga.

7. **Onboarding simplificado**: Los nuevos desarrolladores entienden rápidamente dónde colocar cada tipo de código.

8. **Code reviews más efectivos**: Es fácil identificar violaciones arquitectónicas durante la revisión de código.

### Negativas

1. **Mayor cantidad de código**: Se requieren más archivos y funciones intermediarias, aumentando el boilerplate.
   - **Mitigación**: Crear generadores de código y templates para operaciones comunes.

2. **Curva de aprendizaje inicial**: Desarrolladores acostumbrados a arquitecturas monolíticas necesitan adaptarse.
   - **Mitigación**: Documentación clara, ejemplos de código, y sesiones de capacitación.

3. **Overhead de rendimiento**: Cada capa adicional añade llamadas de función y potencial latencia.
   - **Mitigación**: El overhead es mínimo (microsegundos) y los beneficios superan ampliamente el costo.

4. **Complejidad para operaciones simples**: Operaciones CRUD básicas requieren código en tres archivos.
   - **Mitigación**: Crear utilidades y helpers para operaciones comunes.

5. **Posible sobre-ingeniería**: Para proyectos muy pequeños, esta estructura puede ser excesiva.
   - **Mitigación**: El proyecto PR Sentinel ya tiene suficiente complejidad para justificar esta arquitectura.

## Implementación y cumplimiento

### Herramientas de verificación

1. **Análisis estático**: Implementar reglas de linting que detecten importaciones prohibidas de `/db` en archivos de `/api`.

2. **Pre-commit hooks**: Validar la estructura de dependencias antes de cada commit.

3. **CI/CD checks**: Incluir verificación automática en el pipeline de integración continua.

4. **Code review checklist**: Verificar explícitamente el cumplimiento de la arquitectura en cada PR.

### Ejemplo de regla de linting (pylint)

```python
# .pylintrc o custom checker
# Prohibir importaciones de db.* en archivos dentro de api/
if file_path.startswith('api/') and 'from db.' in import_statement:
    raise ArchitectureViolation("API layer cannot import from DB layer")
```

### Métricas de seguimiento

- Número de violaciones arquitectónicas detectadas en PRs
- Tiempo promedio de respuesta de endpoints (para detectar overhead)
- Cobertura de pruebas unitarias por capa
- Acoplamiento entre módulos (métricas de dependencia)

## Referencias

- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Layered Architecture Pattern](https://www.oreilly.com/library/view/software-architecture-patterns/9781491971437/ch01.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Dependency Inversion Principle](https://en.wikipedia.org/wiki/Dependency_inversion_principle)

## Notas adicionales

Este ADR debe ser revisado cuando:
- El proyecto crezca significativamente y requiera arquitectura más compleja
- Se identifiquen patrones recurrentes que justifiquen capas adicionales
- Se considere migración a microservicios
- Se detecten problemas de rendimiento relacionados con la arquitectura

---

**Autor**: Arquitecto de Software Senior  
**Fecha de creación**: 15 de mayo de 2026  
**Última actualización**: 15 de mayo de 2026  
**Revisores**: Equipo de Arquitectura, Equipo de Desarrollo Backend
</content>
<line_count>234</line_count>
</write_to_file>

---

**User:**

[write_to_file for 'demo_repo/docs/adr/ADR-001-estructura-modular.md'] Result:
<file_write_result>
<path>demo_repo/docs/adr/ADR-001-estructura-modular.md</path>
<operation>modified</operation>
<notice>
<i>You do not need to re-read the file, as you have seen all changes</i>
<i>Proceed with the task using these changes as the new baseline.</i>
</notice>
</file_write_result>

<environment_details>
# VSCode Visible Files
demo_repo/docs/adr/ADR-001-estructura-modular.md

# VSCode Open Tabs
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md,demo_repo/docs/adr/ADR-001-estructura-modular.md,demo_repo/api/orders.py,demo_repo/api/products.py,demo_repo/middleware/auth_middleware.py,demo_repo/db/database.py,demo_repo/services/user_service.py,demo_repo/services/order_service.py,bob_sessions_demo/bob_task_3_API_Users.md,bob_sessions_demo/bob_task_2_API_Orders.md

# Recently Modified Files
These files have been modified since you last accessed them (file was just edited so you may need to re-read it before editing):
demo_repo/docs/adr/ADR-001-estructura-modular.md

# Current Time
Current time in ISO 8601 UTC format: 2026-05-15T18:39:41.754Z
User time zone: America/Mexico_City, UTC-6:00

# Current Cost
$0.54

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Analyze the existing ADR-002 format and structure to maintain consistency | Completed |
| 2 | Draft ADR-001-estructura-modular.md following Nygard format | Completed |
| 3 | Draft ADR-003-manejo-de-errores.md following Nygard format | Completed |
| 4 | Review both documents for technical accuracy and professional tone | Completed |
| 5 | Present the final documents to the user for approval | Completed |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

<write_to_file>
<path>demo_repo/docs/adr/ADR-003-manejo-de-errores.md</path>
<content># ADR-003: Manejo estructurado de errores en endpoints

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
</content>
<line_count>318</line_count>
</write_to_file>

---

**User:**

[write_to_file for 'demo_repo/docs/adr/ADR-003-manejo-de-errores.md'] Result:
<file_write_result>
<path>demo_repo/docs/adr/ADR-003-manejo-de-errores.md</path>
<operation>modified</operation>
<notice>
<i>You do not need to re-read the file, as you have seen all changes</i>
<i>Proceed with the task using these changes as the new baseline.</i>
</notice>
</file_write_result>

<environment_details>
# VSCode Visible Files
demo_repo/docs/adr/ADR-003-manejo-de-errores.md

# VSCode Open Tabs
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md,demo_repo/docs/adr/ADR-001-estructura-modular.md,demo_repo/docs/adr/ADR-003-manejo-de-errores.md,demo_repo/api/orders.py,demo_repo/api/products.py,demo_repo/middleware/auth_middleware.py,demo_repo/db/database.py,demo_repo/services/user_service.py,demo_repo/services/order_service.py,bob_sessions_demo/bob_task_3_API_Users.md,bob_sessions_demo/bob_task_2_API_Orders.md

# Recently Modified Files
These files have been modified since you last accessed them (file was just edited so you may need to re-read it before editing):
demo_repo/docs/adr/ADR-003-manejo-de-errores.md

# Current Time
Current time in ISO 8601 UTC format: 2026-05-15T18:40:49.800Z
User time zone: America/Mexico_City, UTC-6:00

# Current Cost
$0.62

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Analyze the existing ADR-002 format and structure to maintain consistency | Completed |
| 2 | Draft ADR-001-estructura-modular.md following Nygard format | Completed |
| 3 | Draft ADR-003-manejo-de-errores.md following Nygard format | Completed |
| 4 | Review both documents for technical accuracy and professional tone | Completed |
| 5 | Present the final documents to the user for approval | Completed |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

<attempt_completion>
<result>
Successfully created two comprehensive ADR documents for the PR Sentinel project:

## **ADR-001: Estructura Modular por Capas** (234 lines)
- **Decision**: Establishes three-layer architecture (`/api`, `/services`, `/db`) with strict unidirectional dependency flow
- **Key Constraint**: Files in `/api` are explicitly prohibited from importing directly from `/db`
- **Rationale**: Ensures separation of concerns, improves testability, maintainability, and scalability
- **Includes**: Detailed implementation examples, alternatives considered, comprehensive consequences analysis, and compliance tools

## **ADR-003: Manejo Estructurado de Errores** (318 lines)
- **Decision**: All endpoints must use `try/except` blocks and return errors in structured JSON format
- **Standard Format**: Consistent error response schema with `success`, `error.code`, `error.message`, and `error.timestamp`
- **Security Focus**: Prevents exposure of sensitive information (stack traces, internal paths)
- **Includes**: HTTP status code guidelines, exception hierarchy, implementation examples, and monitoring metrics

Both documents follow the Nygard format (Title, Status, Context, Decision, Consequences) and maintain consistency with the existing ADR-002. They feature professional technical tone, comprehensive context explanations, practical code examples, and detailed implementation guidelines ready for production use.

Files saved to:
- `demo_repo/docs/adr/ADR-001-estructura-modular.md`
- `demo_repo/docs/adr/ADR-003-manejo-de-errores.md`
</result>
</attempt_completion>

