# Ejemplo de Comentario Mejorado en PR de GitHub

Este archivo muestra cómo se verá el comentario generado por PR Sentinel en una Pull Request de GitHub con las mejoras implementadas.

---

## 🔍 PR Sentinel — Auditoría Automática
---

### 🔴 Bloqueantes Críticos (2)

| Severidad | Descripción | Archivo | Línea | ADR |
|:---:|---|---|:---:|---|
| <span style="background-color: #d73a4a; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold;">🔴 CRÍTICO</span> | El endpoint POST /users no usa @auth_middleware | `api/users.py` | 14 | ADR-002 |
<details>
<summary>🔧 Ver sugerencia de Fix</summary>

```python
@auth_middleware
@app.post('/users')
def create_user(user_data: dict):
    return user_service.create(user_data)
```

</details>

| <span style="background-color: #d73a4a; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold;">🔴 CRÍTICO</span> | El endpoint DELETE /users/{id} no implementa validación de permisos | `api/users.py` | 45 | ADR-002 |
<details>
<summary>🔧 Ver sugerencia de Fix</summary>

```python
@auth_middleware
@require_admin_role
@app.delete('/users/{id}')
def delete_user(id: int):
    return user_service.delete(id)
```

</details>


### ⚠️ Advertencias (1)

| Severidad | Descripción | Archivo | Línea | ADR |
|:---:|---|---|:---:|---|
| <span style="background-color: #fbca04; color: black; padding: 2px 8px; border-radius: 3px; font-weight: bold;">⚠️ ADVERTENCIA</span> | Importación directa desde /db/ viola la arquitectura modular | `api/products.py` | 5 | ADR-001 |
<details>
<summary>🔧 Ver sugerencia de Fix</summary>

```python
# ❌ Evitar:
from db.database import get_connection

# ✅ Usar en su lugar:
from services.product_service import get_products
```

</details>


### 💡 Sugerencias de Mejora (1)

| Severidad | Descripción | Archivo | Línea | ADR |
|:---:|---|---|:---:|---|
| <span style="background-color: #0e8a16; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold;">💡 SUGERENCIA</span> | Considerar agregar logging para mejor trazabilidad | `services/order_service.py` | 23 | ADR-003 |
<details>
<summary>🔧 Ver sugerencia de Fix</summary>

```python
import logging

logger = logging.getLogger(__name__)

def process_order(order_data: dict):
    logger.info(f"Processing order: {order_data.get('id')}")
    try:
        result = validate_and_save(order_data)
        logger.info(f"Order processed successfully: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing order: {e}")
        raise
```

</details>

---
*Generado por PR Sentinel vía IBM Bob | 2026-05-16T22:36:45.517304+00:00*

---

## 🎨 Características Visuales Mejoradas

### ✅ Badges de Severidad con Estilo HTML
- **🔴 CRÍTICO**: Fondo rojo (#d73a4a) con texto blanco
- **⚠️ ADVERTENCIA**: Fondo amarillo (#fbca04) con texto negro
- **💡 SUGERENCIA**: Fondo verde (#0e8a16) con texto blanco

### ✅ Bloques de Código Colapsables
- Usa etiquetas HTML `<details>` y `<summary>`
- El código sugerido está oculto por defecto
- Click en "🔧 Ver sugerencia de Fix" para expandir
- Formato de código con syntax highlighting (```python)

### ✅ Mejor Organización
- Columna dedicada para badges de severidad
- Rutas de archivo en formato `code` para mejor legibilidad
- Líneas centradas para fácil referencia
- Mensajes de "sin findings" en negrita

### ✅ Compatibilidad Retroactiva
- Funciona con findings que NO tienen `suggested_fix`
- No rompe la estructura existente
- Mejora progresiva cuando se agrega el campo `suggested_fix`