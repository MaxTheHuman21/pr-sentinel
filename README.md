# 🛡️ PR Sentinel

**Auditor Semántico de Pull Requests con IA**

PR Sentinel es una herramienta inteligente que analiza Pull Requests utilizando inteligencia artificial para detectar violaciones de arquitectura y seguridad basadas en Architecture Decision Records (ADRs). Automatiza la revisión de código asegurando que los cambios cumplan con las decisiones arquitectónicas y estándares de seguridad establecidos en tu proyecto.

## 🎯 Características

- **Análisis Semántico con IA**: Utiliza modelos de lenguaje avanzados (Claude) para comprender el contexto y la intención del código
- **Validación de ADRs**: Verifica automáticamente el cumplimiento de las decisiones arquitectónicas documentadas
- **Detección de Vulnerabilidades**: Identifica problemas de seguridad y malas prácticas en el código
- **Reportes Detallados**: Genera informes completos con recomendaciones específicas y referencias a ADRs
- **Integración con GitHub**: Se conecta directamente con la API de GitHub para analizar PRs

## 📋 Requisitos Previos

- Python 3.8 o superior
- Cuenta de GitHub con token de acceso personal
- API Key de Anthropic (Claude)
- Git instalado en tu sistema

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/pr-sentinel.git
cd pr-sentinel
```

### 2. Crear Entorno Virtual

```bash
# Crear el entorno virtual
python -m venv .venv

# Activar el entorno virtual
# En Linux/macOS:
source .venv/bin/activate

# En Windows:
.venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

Las dependencias incluyen:
- `requests>=2.31.0` - Para comunicación con APIs
- `python-dotenv>=1.0.0` - Para gestión de variables de entorno
- `pytest>=7.0.0` - Para pruebas unitarias

## ⚙️ Configuración

### 1. Crear Archivo de Configuración

Copia el archivo de ejemplo y configura tus credenciales:

```bash
cp .env.example .env
```

### 2. Configurar Variables de Entorno

Edita el archivo `.env` con tus credenciales:

```env
# Token de acceso personal de GitHub
# Genera uno en: https://github.com/settings/tokens
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# API Key de Anthropic (Claude)
# Obtén una en: https://console.anthropic.com/
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

# Proveedor del modelo de lenguaje
LLM_PROVIDER=anthropic

# Modelo a utilizar
LLM_MODEL=claude-sonnet-4-6

# Ruta local del repositorio a analizar
REPO_LOCAL_PATH=./demo_repo
```

### Descripción de Variables

- **GITHUB_TOKEN**: Token de acceso personal de GitHub con permisos de lectura de repositorios
- **LLM_API_KEY**: Clave API de Anthropic para acceder a Claude
- **LLM_PROVIDER**: Proveedor del modelo de IA (actualmente soporta `anthropic`)
- **LLM_MODEL**: Modelo específico a utilizar (recomendado: `claude-sonnet-4-6`)
- **REPO_LOCAL_PATH**: Ruta al repositorio local que contiene los ADRs y código base

## 💻 Uso

### Comando Básico

Para analizar un Pull Request específico:

```bash
python sentinel.py --repo [USUARIO/REPOSITORIO] --pr [NUMERO_PR]
```

### Ejemplos

```bash
# Analizar PR #42 del repositorio example/my-project
python sentinel.py --repo example/my-project --pr 42

# Analizar PR #15 con ruta personalizada al repositorio local
python sentinel.py --repo myorg/backend --pr 15
```

### Salida del Análisis

PR Sentinel generará un reporte detallado que incluye:

- ✅ **Cumplimiento de ADRs**: Verificación de cada decisión arquitectónica
- 🔒 **Análisis de Seguridad**: Detección de vulnerabilidades y malas prácticas
- 📊 **Métricas de Calidad**: Evaluación general del código
- 💡 **Recomendaciones**: Sugerencias específicas para mejorar el código
- 📚 **Referencias**: Enlaces a ADRs relevantes y documentación

## 📁 Estructura del Proyecto

```
pr-sentinel/
├── sentinel.py              # Script principal de la CLI
├── github_client.py         # Cliente para interactuar con GitHub API
├── llm_reasoner.py          # Motor de razonamiento con IA
├── repo_analyzer.py         # Analizador de repositorio y ADRs
├── report_formatter.py      # Formateador de reportes
├── requirements.txt         # Dependencias del proyecto
├── .env.example            # Plantilla de configuración
├── ARCHITECTURE.md         # Documentación de arquitectura
├── demo_repo/              # Repositorio de ejemplo
│   ├── docs/adr/          # Architecture Decision Records
│   └── ...
└── tests/                  # Pruebas unitarias
    ├── test_github_client.py
    ├── test_llm_reasoner.py
    ├── test_repo_analyzer.py
    └── test_report_formatter.py
```

## 🧪 Pruebas

Ejecutar las pruebas unitarias:

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con cobertura
pytest --cov=. --cov-report=html

# Ejecutar pruebas específicas
pytest tests/test_github_client.py
```

## 📖 Documentación de ADRs

PR Sentinel busca ADRs en la siguiente estructura:

```
tu-repositorio/
└── docs/
    └── adr/
        ├── ADR-001-nombre-decision.md
        ├── ADR-002-otra-decision.md
        └── ...
```

Cada ADR debe seguir el formato estándar con secciones:
- **Título**: Nombre descriptivo de la decisión
- **Estado**: Propuesto, Aceptado, Rechazado, etc.
- **Contexto**: Situación que motivó la decisión
- **Decisión**: Qué se decidió hacer
- **Consecuencias**: Impacto de la decisión

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🏆 Créditos

**PR Sentinel** fue desarrollado para el **Hackathon IBM Bob - Mayo 2026**.

Desarrollado con ❤️ utilizando:
- [Anthropic Claude](https://www.anthropic.com/) - Motor de IA
- [GitHub API](https://docs.github.com/en/rest) - Integración con repositorios
- [Python](https://www.python.org/) - Lenguaje de programación

## 📧 Contacto

Para preguntas, sugerencias o reportar problemas, por favor abre un issue en el repositorio.

---

**¡Mantén tu código limpio, seguro y alineado con tus decisiones arquitectónicas!** 🛡️

PR Trampa a Auditar: #[5]