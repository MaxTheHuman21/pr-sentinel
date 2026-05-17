# 🔍 DIAGNÓSTICO: Por qué el LLM está "ciego"

## 📊 Hallazgos del Debug

### ✅ Lo que SÍ funciona:
1. **El diff llega correctamente** al LLM (976 caracteres, archivo completo visible)
2. **Los ADRs están presentes** (3 ADRs, ~30KB de documentación)
3. **El análisis estático funciona parcialmente**: `_find_endpoints_in_diff_without_auth()` SÍ detecta el endpoint sin auth
4. **El prompt es claro** y tiene instrucciones explícitas

### ❌ El CUELLO DE BOTELLA identificado:

```python
# En llm_reasoner.py, línea 294:
violations = _precompute_violations(import_map, diff, files_dict)

# RESULTADO DEL DEBUG:
ADR-002 violations: []  # ❌ VACÍO
ADR-001 violations: []  # ❌ VACÍO  
ADR-003 violations: []  # ❌ VACÍO
```

**¿Por qué están vacíos?**

## 🐛 PROBLEMA RAÍZ #1: Import Map Incompleto

El `import_map` solo contiene archivos **existentes** en el repo:
```python
Import map construido: 5 archivos
  - demo_repo/api/orders.py
  - demo_repo/api/products.py
  - demo_repo/db/database.py
  - demo_repo/middleware/auth_middleware.py
  - demo_repo/services/order_service.py
```

**PERO** el archivo `demo_repo/api/users.py` es **NUEVO** (no existe en el repo todavía).

Por lo tanto:
- `import_map['demo_repo/api/users.py']` → **NO EXISTE**
- `_precompute_violations()` itera sobre `import_map.items()` → **NUNCA VE users.py**
- Las "hints" que se envían al LLM dicen: `(none detected statically)` ❌

## 🐛 PROBLEMA RAÍZ #2: Hints Engañosos

El prompt dice al LLM:

```
HINTS FOUND BY STATIC ANALYSIS (Use only as a guide, rely on your semantic analysis of the Diff):
ADR-002 hints:
  (none detected statically)
```

Esto **confunde al LLM**. El modelo ve:
1. Un diff que claramente muestra un endpoint sin `@auth_middleware`
2. Pero las "hints" dicen que no hay violaciones
3. El LLM **confía en las hints** y concluye: "si el análisis estático no encontró nada, tal vez no sea una violación"

## 🐛 PROBLEMA RAÍZ #3: Análisis Estático Basado en Import Map

```python
# llm_reasoner.py, línea 82-101
for filename, imports in import_map.items():
    # ...
    if is_api_file:
        has_auth = any(
            "auth_middleware" in imp.lower() or "middleware.auth_middleware" in imp.lower()
            for imp in imports
        )
        if not has_auth:
            adr002_violations.append(normalized_filename)
```

**Problema**: Solo analiza archivos que YA EXISTEN en el repo. Los archivos nuevos en la PR no están en `import_map`, por lo tanto **nunca se analizan**.

## 🎯 SOLUCIÓN ARQUITECTÓNICA ELEGANTE

### Principio: "Analizar el DIFF, no solo el REPO"

El análisis estático debe:
1. **Parsear el DIFF** para extraer archivos nuevos/modificados
2. **Analizar el código del DIFF** directamente (no depender del import_map)
3. **Generar hints precisas** basadas en lo que realmente está en el diff

### Implementación Propuesta:

```python
def _analyze_diff_for_violations(diff: str, changed_files: list) -> dict:
    """
    Analiza el DIFF directamente para detectar violaciones.
    No depende del import_map (que solo tiene archivos existentes).
    """
    violations = {
        'adr002_violations': [],
        'adr001_violations': [],
        'adr003_violations': []
    }
    
    # Parsear el diff por archivo
    file_contents = _extract_file_contents_from_diff(diff, changed_files)
    
    for filepath, content in file_contents.items():
        if '/api/' in filepath or filepath.startswith('api/'):
            # ADR-002: Buscar @auth_middleware en el contenido
            if '@auth_middleware' not in content and 'auth_middleware' not in content:
                violations['adr002_violations'].append(filepath)
            
            # ADR-001: Buscar imports directos de db
            if 'from db.' in content or 'import db.' in content:
                violations['adr001_violations'].append(filepath)
            
            # ADR-003: Buscar try/except
            if 'def ' in content and 'try:' not in content:
                violations['adr003_violations'].append(filepath)
    
    return violations
```

### Ventajas de esta solución:

1. ✅ **Analiza archivos nuevos**: No depende del import_map
2. ✅ **Hints precisas**: El LLM recibe información correcta
3. ✅ **Semántica preservada**: El LLM sigue siendo el juez final
4. ✅ **Sin hardcodeo**: Es genérico y funciona para cualquier PR
5. ✅ **Escalable**: Fácil agregar nuevos ADRs

## 📈 Impacto Esperado

**ANTES** (estado actual):
```
HINTS FOUND BY STATIC ANALYSIS:
ADR-002 hints:
  (none detected statically)  ← ❌ ENGAÑOSO
```

**DESPUÉS** (con la solución):
```
HINTS FOUND BY STATIC ANALYSIS:
ADR-002 hints:
  demo_repo/api/users.py  ← ✅ CORRECTO
```

El LLM verá:
1. El diff muestra un endpoint sin auth ✅
2. Las hints confirman la violación ✅
3. Los ADRs explican por qué es crítico ✅
4. **Conclusión del LLM**: "Esto es un BLOCKER de ADR-002" ✅

## 🎬 Próximos Pasos

1. Implementar `_extract_file_contents_from_diff()`
2. Reemplazar `_precompute_violations()` con `_analyze_diff_for_violations()`
3. Actualizar `build_prompt()` para usar el nuevo análisis
4. Probar con PR #5 y PR #13
5. Validar que el LLM detecte las violaciones correctamente