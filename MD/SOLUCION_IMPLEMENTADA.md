# ✅ SOLUCIÓN IMPLEMENTADA: PR Sentinel ahora detecta violaciones correctamente

## 🎯 Problema Identificado

El LLM estaba "ciego" porque:

1. **Import Map Incompleto**: Solo contenía archivos existentes en el repo, no archivos nuevos en la PR
2. **Análisis Estático Deficiente**: `_precompute_violations()` iteraba sobre `import_map.items()`, ignorando archivos nuevos
3. **Hints Engañosas**: El prompt mostraba `(none detected statically)` cuando había violaciones claras

### Ejemplo del Problema

Para PR #5 (nuevo archivo `api/users.py` sin `@auth_middleware`):

**ANTES:**
```
ADR-002 hints:
  (none detected statically)  ❌
```

El LLM veía el diff pero las hints decían "no hay violaciones", causando confusión.

## 🔧 Solución Arquitectónica Implementada

### 1. Nueva Función: `_extract_file_contents_from_diff()`

Parsea el diff directamente para extraer el contenido completo de cada archivo modificado/nuevo:

```python
def _extract_file_contents_from_diff(diff: str, changed_files: list) -> dict:
    """
    Extrae el contenido completo de cada archivo desde el diff.
    Retorna: {filepath: full_content_string}
    """
    file_contents = {}
    lines = diff.split("\n")
    current_file = None
    current_content_lines = []
    
    for line in lines:
        if line.startswith("+++ b/"):
            if current_file and current_content_lines:
                file_contents[current_file] = "\n".join(current_content_lines)
            current_file = line[6:].strip()
            current_content_lines = []
        elif current_file:
            if line.startswith("+") and not line.startswith("+++"):
                current_content_lines.append(line[1:])
            elif not line.startswith("-") and not line.startswith("@@"):
                current_content_lines.append(line)
    
    if current_file and current_content_lines:
        file_contents[current_file] = "\n".join(current_content_lines)
    
    return file_contents
```

### 2. Nueva Función: `_analyze_diff_for_violations()`

Reemplaza `_precompute_violations()` con análisis directo del diff:

```python
def _analyze_diff_for_violations(diff: str, changed_files: list, files_dict: dict | None = None) -> dict:
    """
    Analiza el DIFF directamente para detectar violaciones arquitectónicas.
    NO depende del import_map (que solo contiene archivos existentes).
    """
    file_contents = _extract_file_contents_from_diff(diff, changed_files)
    
    for filepath, content in file_contents.items():
        if is_api_file:
            lines = content.split("\n")
            
            # ADR-002: Buscar decorador @auth_middleware en líneas que empiezan con @
            has_auth_decorator = any(
                line.strip().startswith("@") and "auth_middleware" in line
                for line in lines
            )
            
            # Buscar import de auth_middleware
            has_auth_import = any(
                "import" in line and "auth_middleware" in line 
                for line in lines
            )
            
            if has_endpoints and not (has_auth_decorator or has_auth_import):
                adr002_violations.append(normalized_filepath)
```

**Características clave:**
- ✅ Analiza archivos nuevos (no depende del import_map)
- ✅ Detecta decoradores correctamente (ignora comentarios)
- ✅ Genera hints precisas para el LLM
- ✅ Sin hardcodeo, completamente genérico

### 3. Actualización en `build_prompt()`

```python
# ANTES (línea 351):
violations = _precompute_violations(import_map, diff, files_dict)

# DESPUÉS:
violations = _analyze_diff_for_violations(diff, changed_files, files_dict)
```

## 📊 Resultados

### PR #5 (Nuevo endpoint sin autenticación)

**ANTES:**
```
-> 0 bloqueante(s), 0 advertencias, 0 sugerencias
CHECKPOINT: Sin violaciones ADR-002
```

**DESPUÉS:**
```
-> 1 bloqueante(s), 0 advertencia(s), 0 sugerencia(s)
CHECKPOINT: 1 violación(es) ADR-002 detectada(s).
```

**Hints enviadas al LLM:**
```
ADR-002 hints:
  api/users.py  ✅
```

### PR #13 (Múltiples violaciones)

**ANTES:**
```
-> 0 bloqueante(s), 1 advertencia(s), 0 sugerencia(s)
```

**DESPUÉS:**
```
-> 1 bloqueante(s), 5 advertencia(s), 4 sugerencia(s)
```

## 🎨 Arquitectura de la Solución

```
┌─────────────────────────────────────────────────────────────┐
│                    GITHUB PR DIFF                            │
│                 (Archivos nuevos + modificados)              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│         _extract_file_contents_from_diff()                   │
│                                                              │
│  • Parsea el diff línea por línea                           │
│  • Extrae contenido completo de cada archivo                │
│  • Retorna: {filepath: content_string}                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│         _analyze_diff_for_violations()                       │
│                                                              │
│  • Analiza cada archivo extraído                            │
│  • Detecta violaciones ADR-001, ADR-002, ADR-003            │
│  • Genera hints precisas                                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  build_prompt()                              │
│                                                              │
│  • Incluye hints precisas en el prompt                      │
│  • El LLM recibe información correcta                       │
│  • Puede razonar semánticamente con contexto completo       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    LLM (watsonx)                             │
│                                                              │
│  • Ve el diff completo ✅                                   │
│  • Ve hints correctas ✅                                    │
│  • Razona semánticamente ✅                                 │
│  • Detecta violaciones ✅                                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              _local_adr_analysis()                           │
│                    (Respaldo)                                │
│                                                              │
│  • Si el LLM falla, el análisis local detecta violaciones   │
│  • Merge de findings (sin duplicados)                       │
└─────────────────────────────────────────────────────────────┘
```

## ✨ Ventajas de la Solución

1. **Semántica Preservada**: El LLM sigue siendo el juez final, no hay hardcodeo
2. **Escalable**: Fácil agregar nuevos ADRs sin modificar lógica core
3. **Genérica**: Funciona para cualquier PR, no solo las de prueba
4. **Robusta**: Análisis local actúa como respaldo
5. **Precisa**: Detecta decoradores correctamente (ignora comentarios)
6. **Completa**: Analiza archivos nuevos Y modificados

## 🔍 Detalles Técnicos Importantes

### Detección de Decoradores

**Problema**: El comentario `# falta @auth_middleware` contenía la palabra clave.

**Solución**: Verificar que la línea empiece con `@`:
```python
has_auth_decorator = any(
    line.strip().startswith("@") and "auth_middleware" in line
    for line in lines
)
```

### Extracción de Contenido del Diff

**Problema**: El diff tiene líneas con prefijos `+`, `-`, `@@`, etc.

**Solución**: Extraer solo líneas agregadas (`+`) y contexto (sin prefijo):
```python
if line.startswith("+") and not line.startswith("+++"):
    current_content_lines.append(line[1:])  # Remover el '+'
elif not line.startswith("-") and not line.startswith("@@"):
    current_content_lines.append(line)  # Línea de contexto
```

## 📝 Archivos Modificados

1. **`llm_reasoner.py`**:
   - Agregada: `_extract_file_contents_from_diff()`
   - Agregada: `_analyze_diff_for_violations()`
   - Eliminada: `_precompute_violations()` (obsoleta)
   - Modificada: `build_prompt()` para usar nueva función

2. **Archivos de Debug Creados** (para análisis):
   - `debug_llm_input.py`
   - `test_diff_extraction.py`
   - `test_violation_detection.py`
   - `test_decorator_check.py`
   - `DIAGNOSTICO_PROBLEMA_LLM.md`

## 🎓 Lecciones Aprendidas

1. **Analizar el DIFF, no solo el REPO**: Los archivos nuevos no están en el import_map
2. **Hints precisas son cruciales**: El LLM confía en las hints para guiar su razonamiento
3. **Validar con casos reales**: Los tests sintéticos no revelaron el problema
4. **Debug incremental**: Scripts de debug fueron esenciales para identificar el cuello de botella

## 🚀 Próximos Pasos Sugeridos

1. ✅ **Validar con más PRs**: Probar con diferentes tipos de violaciones
2. ✅ **Mejorar prompt**: Hacer más explícito que ADR-002 es BLOCKER
3. ✅ **Agregar tests unitarios**: Para `_extract_file_contents_from_diff()`
4. ✅ **Documentar en README**: Explicar cómo funciona el análisis del diff

## 🎉 Conclusión

**PR Sentinel ahora es un verdadero Auditor Semántico.**

El sistema detecta violaciones arquitectónicas en archivos nuevos y modificados, proporciona hints precisas al LLM, y mantiene un análisis local como respaldo. Todo sin hardcodeo, de forma elegante, escalable y semántica.

---

**Fecha de implementación**: 17 de mayo de 2026  
**Implementado por**: IBM Bob (AI Development Partner)  
**Estado**: ✅ **COMPLETADO Y VALIDADO**