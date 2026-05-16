# 🛡️ PR Sentinel - Guía de Instalación y Configuración

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Instalación](#instalación)
3. [Configuración de Variables de Entorno](#configuración-de-variables-de-entorno)
4. [Obtención de Credenciales](#obtención-de-credenciales)
5. [Ejecución del Proyecto](#ejecución-del-proyecto)
6. [Verificación de la Instalación](#verificación-de-la-instalación)
7. [Solución de Problemas](#solución-de-problemas)

---

## 📦 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- **Python 3.8 o superior**
  ```bash
  python --version
  # Debe mostrar: Python 3.8.x o superior
  ```

- **pip** (gestor de paquetes de Python)
  ```bash
  pip --version
  ```

- **Git**
  ```bash
  git --version
  ```

- **Cuenta de GitHub** con permisos para crear tokens de acceso personal

- **Cuenta de IBM Cloud** con acceso a watsonx.ai

---

## 🚀 Instalación

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/pr-sentinel.git
cd pr-sentinel
```

### Paso 2: Crear Entorno Virtual

Es **altamente recomendado** usar un entorno virtual para aislar las dependencias:

```bash
# Crear el entorno virtual
python -m venv .venv

# Activar el entorno virtual
# En Linux/macOS:
source .venv/bin/activate

# En Windows (PowerShell):
.venv\Scripts\Activate.ps1

# En Windows (CMD):
.venv\Scripts\activate.bat
```

**Nota:** Cuando el entorno virtual esté activo, verás `(.venv)` al inicio de tu línea de comandos.

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

Esto instalará:
- `requests>=2.31.0` - Para comunicación con APIs (GitHub, watsonx.ai)
- `python-dotenv>=1.0.0` - Para gestión de variables de entorno
- `pytest>=7.0.0` - Para ejecutar pruebas unitarias
- `pytest-cov>=4.1.0` - Para generar reportes de cobertura de código

---

## ⚙️ Configuración de Variables de Entorno

### Paso 1: Crear el Archivo .env

Crea un archivo llamado `.env` en la raíz del proyecto:

```bash
touch .env
```

### Paso 2: Configurar las Variables Requeridas

Edita el archivo `.env` y agrega las siguientes variables:

```env
# ============================================
# CONFIGURACIÓN DE GITHUB
# ============================================
# Token de acceso personal de GitHub
# Genera uno en: https://github.com/settings/tokens
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ============================================
# CONFIGURACIÓN DE IBM WATSONX.AI
# ============================================
# API Key de IBM Cloud
# Obtén una en: https://cloud.ibm.com/iam/apikeys
WATSONX_API_KEY=tu_api_key_de_ibm_cloud_aqui

# URL del servicio watsonx.ai (por defecto: us-south)
# Opciones: us-south, eu-de, eu-gb, jp-tok
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# ID del proyecto en watsonx.ai
# Obtén el ID desde tu proyecto en: https://dataplatform.cloud.ibm.com/
WATSONX_PROJECT_ID=tu_project_id_aqui

# Modelo de IA a utilizar (recomendado: granite-3-8b-instruct)
WATSONX_MODEL_ID=ibm/granite-3-8b-instruct

# ============================================
# CONFIGURACIÓN DEL REPOSITORIO
# ============================================
# Ruta local al repositorio que contiene los ADRs
# Por defecto apunta al repositorio de demostración incluido
REPO_LOCAL_PATH=./demo_repo
```

---

## 🔑 Obtención de Credenciales

### 1. Token de GitHub (GITHUB_TOKEN)

1. Ve a [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Haz clic en **"Generate new token"** → **"Generate new token (classic)"**
3. Dale un nombre descriptivo (ej: "PR Sentinel Token")
4. Selecciona los siguientes permisos:
   - ✅ `repo` (acceso completo a repositorios privados)
   - ✅ `read:org` (leer información de la organización)
5. Haz clic en **"Generate token"**
6. **IMPORTANTE:** Copia el token inmediatamente (solo se muestra una vez)
7. Pégalo en tu archivo `.env` como valor de `GITHUB_TOKEN`

**Formato del token:** `ghp_` seguido de 36 caracteres alfanuméricos

### 2. Credenciales de IBM watsonx.ai

#### A. Crear una API Key de IBM Cloud (WATSONX_API_KEY)

1. Inicia sesión en [IBM Cloud](https://cloud.ibm.com/)
2. Ve a **Manage** → **Access (IAM)** → **API keys**
3. Haz clic en **"Create an IBM Cloud API key"**
4. Dale un nombre descriptivo (ej: "PR Sentinel watsonx Key")
5. Haz clic en **"Create"**
6. **IMPORTANTE:** Descarga o copia la API key inmediatamente
7. Pégala en tu archivo `.env` como valor de `WATSONX_API_KEY`

#### B. Obtener el Project ID (WATSONX_PROJECT_ID)

1. Ve a [IBM watsonx.ai](https://dataplatform.cloud.ibm.com/)
2. Abre tu proyecto o crea uno nuevo:
   - Haz clic en **"New project"** → **"Create an empty project"**
   - Dale un nombre (ej: "PR Sentinel Project")
3. Una vez dentro del proyecto, ve a la pestaña **"Manage"**
4. En la sección **"General"**, encontrarás el **"Project ID"**
5. Copia el Project ID y pégalo en tu archivo `.env` como valor de `WATSONX_PROJECT_ID`

**Formato del Project ID:** UUID de 36 caracteres (ej: `12345678-1234-1234-1234-123456789abc`)

#### C. Configurar la URL del Servicio (WATSONX_URL)

Selecciona la región más cercana a tu ubicación:

- **US South (Dallas):** `https://us-south.ml.cloud.ibm.com` (recomendado para América)
- **EU Germany (Frankfurt):** `https://eu-de.ml.cloud.ibm.com`
- **EU UK (London):** `https://eu-gb.ml.cloud.ibm.com`
- **Japan (Tokyo):** `https://jp-tok.ml.cloud.ibm.com`

#### D. Modelo de IA (WATSONX_MODEL_ID)

El proyecto está configurado para usar **IBM Granite 3 8B Instruct**:

```env
WATSONX_MODEL_ID=ibm/granite-3-8b-instruct
```

Este modelo está optimizado para tareas de análisis de código y razonamiento.

**Modelos alternativos disponibles:**
- `ibm/granite-3-2b-instruct` (más rápido, menos preciso)
- `ibm/granite-20b-multilingual` (multilingüe)
- `meta-llama/llama-3-70b-instruct` (más potente, requiere más recursos)

---

## 🎯 Ejecución del Proyecto

### Uso Básico

Para analizar un Pull Request:

```bash
python sentinel.py --repo USUARIO/REPOSITORIO --pr NUMERO_PR
```

### Ejemplos

```bash
# Analizar PR #5 del repositorio example/my-project
python sentinel.py --repo example/my-project --pr 5

# Analizar PR #42 de tu propio repositorio
python sentinel.py --repo tu-usuario/tu-repo --pr 42
```

### Salida Esperada

El script mostrará un progreso paso a paso:

```
  PR Sentinel — Analizando PR #5 en example/my-project

[1/5] Obteniendo diff de PR #5... OK (127 líneas modificadas, 3 archivos)
[2/5] Leyendo ADRs y reglas del repo... OK (3 ADRs encontrados)
[3/5] Analizando imports del repo... OK (15 módulos mapeados)
[4/5] Razonando con WATSONX + análisis local... OK
[5/5] Publicando comentario en PR #5... OK

-> Comentario publicado: 1 bloqueantes, 2 advertencias, 1 sugerencias
```

El reporte completo se publicará automáticamente como comentario en el Pull Request.

---

## ✅ Verificación de la Instalación

### 1. Verificar Dependencias

```bash
pip list | grep -E "requests|python-dotenv|pytest"
```

Deberías ver:
```
python-dotenv    1.0.0
pytest           7.0.0
pytest-cov       4.1.0
requests         2.31.0
```

### 2. Ejecutar Pruebas Unitarias

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con información detallada
pytest -v

# Ejecutar con cobertura de código
pytest --cov=. --cov-report=html
```

### 3. Verificar Conexión con GitHub

```bash
python -c "
import os
from dotenv import load_dotenv
import github_client

load_dotenv()
token = os.getenv('GITHUB_TOKEN')
print('✅ Token de GitHub configurado' if token else '❌ Token de GitHub NO configurado')
"
```

### 4. Verificar Conexión con watsonx.ai

```bash
python test_watsonx.py
```

Si todo está configurado correctamente, deberías ver:
```
✅ Conexión exitosa con watsonx.ai
✅ Modelo granite-3-8b-instruct disponible
```

---

## 🔧 Solución de Problemas

### Error: "GITHUB_TOKEN no configurado en .env"

**Causa:** El archivo `.env` no existe o no contiene la variable `GITHUB_TOKEN`.

**Solución:**
1. Verifica que el archivo `.env` existe en la raíz del proyecto
2. Asegúrate de que contiene la línea: `GITHUB_TOKEN=tu_token_aqui`
3. Verifica que no hay espacios antes o después del `=`

### Error: "WATSONX_API_KEY no configurado en .env"

**Causa:** Falta la API Key de IBM Cloud.

**Solución:**
1. Sigue los pasos en [Obtención de Credenciales](#obtención-de-credenciales)
2. Agrega la API Key al archivo `.env`

### Error: "WATSONX_PROJECT_ID no configurado en .env"

**Causa:** Falta el ID del proyecto de watsonx.ai.

**Solución:**
1. Ve a [IBM watsonx.ai](https://dataplatform.cloud.ibm.com/)
2. Abre tu proyecto y copia el Project ID desde la pestaña "Manage"
3. Agrégalo al archivo `.env`

### Error: "HTTP 401 Unauthorized" al conectar con GitHub

**Causa:** Token de GitHub inválido o sin permisos suficientes.

**Solución:**
1. Verifica que el token es correcto (debe empezar con `ghp_`)
2. Regenera el token con los permisos correctos (`repo`, `read:org`)
3. Actualiza el archivo `.env` con el nuevo token

### Error: "HTTP 401 Unauthorized" al conectar con watsonx.ai

**Causa:** API Key de IBM Cloud inválida o expirada.

**Solución:**
1. Verifica que la API Key es correcta
2. Asegúrate de que tu cuenta de IBM Cloud está activa
3. Regenera la API Key si es necesario

### Error: "No se encontraron archivos Python válidos"

**Causa:** El repositorio no contiene archivos Python o están en carpetas excluidas.

**Solución:**
1. Verifica que el repositorio contiene archivos `.py`
2. Revisa que no están en carpetas excluidas (`node_modules/`, `.venv/`, etc.)

### Error: "ModuleNotFoundError: No module named 'requests'"

**Causa:** Las dependencias no están instaladas.

**Solución:**
```bash
pip install -r requirements.txt
```

### El script se ejecuta pero no publica el comentario

**Causa:** Permisos insuficientes del token de GitHub.

**Solución:**
1. Verifica que el token tiene permisos de escritura (`repo`)
2. Asegúrate de tener permisos de escritura en el repositorio

---

## 📚 Recursos Adicionales

- [Documentación de GitHub API](https://docs.github.com/en/rest)
- [Documentación de IBM watsonx.ai](https://www.ibm.com/docs/en/watsonx-as-a-service)
- [Guía de ADRs](https://adr.github.io/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)

---

## 📞 Soporte

Si encuentras problemas no cubiertos en esta guía:

1. Revisa los logs de error completos
2. Verifica que todas las variables de entorno están configuradas correctamente
3. Asegúrate de estar usando Python 3.8 o superior
4. Consulta la documentación oficial de las APIs utilizadas

---

**¡Listo! Ahora puedes usar PR Sentinel para auditar tus Pull Requests automáticamente.** 🛡️
