# ADR-002: Autenticación obligatoria en endpoints de la API

## Estado
**Aceptado** - 15 de mayo de 2026

## Contexto

En el desarrollo de aplicaciones web modernas, la seguridad de los endpoints de la API es fundamental para proteger los datos sensibles y garantizar que solo usuarios autorizados puedan acceder a los recursos del sistema.

### Problemática identificada

1. **Riesgos de seguridad**: La exposición de endpoints sin mecanismos de autenticación representa una vulnerabilidad crítica que puede ser explotada por actores maliciosos para:
   - Acceder a datos confidenciales de usuarios
   - Modificar o eliminar información sin autorización
   - Realizar ataques de denegación de servicio (DoS)
   - Ejecutar operaciones fraudulentas

2. **Cumplimiento normativo**: Las regulaciones de protección de datos (GDPR, CCPA, LGPD) requieren controles de acceso estrictos para datos personales.

3. **Inconsistencia en la implementación**: Sin un estándar definido, diferentes desarrolladores pueden implementar la autenticación de manera inconsistente o, peor aún, omitirla por completo.

4. **Vulnerabilidades OWASP**: La falta de control de acceso adecuado está clasificada como A01:2021 - Broken Access Control en el OWASP Top 10, siendo una de las vulnerabilidades más críticas y comunes.

### Necesidades del sistema

- Mecanismo centralizado y consistente de autenticación
- Facilidad de auditoría y mantenimiento
- Prevención de accesos no autorizados
- Trazabilidad de las operaciones realizadas por usuarios autenticados

## Decisión

**Se establece como obligatorio que todos los archivos dentro de la carpeta `/api` deben utilizar el decorador `@auth_middleware` importado desde `middleware/auth_middleware.py` para cualquier exposición de endpoints.**

### Implementación

```python
# Importación obligatoria en todos los archivos de /api
from middleware.auth_middleware import auth_middleware

# Aplicación del decorador en cada endpoint
@auth_middleware
def endpoint_handler(request):
    # Lógica del endpoint
    pass
```

### Reglas de aplicación

1. **Obligatoriedad universal**: Ningún endpoint en la carpeta `/api` puede ser expuesto sin el decorador `@auth_middleware`.

2. **Sin excepciones implícitas**: Si un endpoint requiere acceso público (ej: login, registro), debe documentarse explícitamente en un ADR específico y utilizar un decorador alternativo claramente identificado (ej: `@public_endpoint`).

3. **Orden de decoradores**: Cuando se utilicen múltiples decoradores, `@auth_middleware` debe ser el primero en la cadena para garantizar que la autenticación se valide antes que cualquier otra lógica.

4. **Revisión en code reviews**: Todo pull request que añada o modifique endpoints debe ser revisado específicamente para verificar el cumplimiento de esta política.

### Responsabilidades del middleware

El `auth_middleware` debe:
- Validar la presencia y validez de tokens de autenticación
- Verificar la vigencia de las sesiones
- Rechazar peticiones no autenticadas con código HTTP 401 (Unauthorized)
- Rechazar peticiones con tokens inválidos con código HTTP 403 (Forbidden)
- Inyectar información del usuario autenticado en el contexto de la petición
- Registrar intentos de acceso no autorizado para auditoría

## Alternativas consideradas

### 1. Autenticación a nivel de gateway/proxy
**Rechazada**: Aunque proporciona una capa adicional de seguridad, no elimina la necesidad de validación a nivel de aplicación. Además, complica el desarrollo local y las pruebas.

### 2. Autenticación manual en cada endpoint
**Rechazada**: Propensa a errores humanos, inconsistente, difícil de mantener y auditar. Aumenta significativamente la superficie de ataque.

### 3. Autenticación opcional con configuración
**Rechazada**: La seguridad no debe ser opcional. Un enfoque de "secure by default" es fundamental para prevenir vulnerabilidades.

### 4. Middleware global a nivel de framework
**Considerada pero complementaria**: Si bien algunos frameworks permiten middleware global, el uso explícito del decorador proporciona:
- Mayor visibilidad en el código
- Control granular por endpoint
- Facilita la identificación durante code reviews
- Mejor documentación implícita

## Consecuencias

### Positivas

1. **Seguridad centralizada**: Un único punto de implementación y mantenimiento de la lógica de autenticación reduce la probabilidad de errores y vulnerabilidades.

2. **Consistencia garantizada**: Todos los endpoints siguen el mismo patrón de seguridad, eliminando inconsistencias.

3. **Facilita auditorías**: Es trivial identificar qué endpoints están protegidos mediante búsqueda de código o análisis estático.

4. **Mantenimiento simplificado**: Cambios en la lógica de autenticación se realizan en un solo lugar y se propagan automáticamente a todos los endpoints.

5. **Cumplimiento normativo**: Facilita demostrar controles de acceso adecuados para auditorías de cumplimiento.

6. **Prevención de vulnerabilidades**: Reduce drásticamente el riesgo de exponer accidentalmente endpoints sin protección.

7. **Trazabilidad mejorada**: Todos los accesos a la API quedan registrados con información del usuario autenticado.

8. **Onboarding más rápido**: Nuevos desarrolladores aprenden un patrón claro y consistente desde el inicio.

### Negativas

1. **Overhead de rendimiento**: Cada petición debe pasar por el proceso de validación de autenticación, añadiendo latencia (típicamente 5-20ms).
   - **Mitigación**: Implementar caché de validación de tokens, usar tokens JWT con validación local.

2. **Complejidad inicial**: Desarrolladores nuevos deben entender el sistema de autenticación antes de crear endpoints.
   - **Mitigación**: Documentación clara, ejemplos de código, templates de inicio.

3. **Gestión de tokens/sesiones**: Requiere infraestructura adicional para manejo de tokens, expiración y renovación.
   - **Mitigación**: Utilizar soluciones probadas (JWT, OAuth 2.0) con librerías establecidas.

4. **Dificultad para endpoints públicos**: Requiere proceso adicional para documentar y aprobar excepciones.
   - **Mitigación**: Crear decorador `@public_endpoint` con documentación obligatoria del motivo.

5. **Testing más complejo**: Las pruebas unitarias deben incluir tokens de autenticación válidos.
   - **Mitigación**: Crear fixtures y helpers de testing que generen tokens de prueba automáticamente.

6. **Posible punto único de fallo**: Si el middleware falla, todos los endpoints se ven afectados.
   - **Mitigación**: Implementar circuit breakers, fallbacks, y monitoreo exhaustivo del middleware.

## Implementación y cumplimiento

### Herramientas de verificación

1. **Linters personalizados**: Crear reglas de linting que detecten endpoints sin el decorador.
2. **Pre-commit hooks**: Validar automáticamente antes de cada commit.
3. **CI/CD checks**: Incluir verificación automática en el pipeline de integración continua.
4. **Code review checklist**: Incluir verificación explícita en la plantilla de PR.

### Métricas de seguimiento

- Porcentaje de endpoints con autenticación
- Número de intentos de acceso no autorizado
- Tiempo promedio de validación de autenticación
- Incidentes de seguridad relacionados con autenticación

## Referencias

- [OWASP Top 10 2021 - A01:2021 Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [RFC 6749 - OAuth 2.0 Authorization Framework](https://tools.ietf.org/html/rfc6749)
- [RFC 7519 - JSON Web Token (JWT)](https://tools.ietf.org/html/rfc7519)

## Notas adicionales

Este ADR debe ser revisado anualmente o cuando:
- Se identifiquen nuevas vulnerabilidades de seguridad
- Cambien los requisitos de cumplimiento normativo
- Se adopten nuevas tecnologías de autenticación
- Se detecten problemas significativos de rendimiento

---

**Autor**: Arquitecto de Software Senior  
**Fecha de creación**: 15 de mayo de 2026  
**Última actualización**: 15 de mayo de 2026  
**Revisores**: Equipo de Seguridad, Equipo de Desarrollo Backend