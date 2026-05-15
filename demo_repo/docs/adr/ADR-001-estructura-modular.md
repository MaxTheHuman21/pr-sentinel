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