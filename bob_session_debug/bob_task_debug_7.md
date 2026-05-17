**User:**

<task>
Actúa como un Ingeniero de Software Senior y Tech Lead de QA. Necesito que escribas una suite de pruebas unitarias usando `pytest`, consolides las dependencias y generes la documentación principal en el archivo `README.md` para nuestro proyecto "PR Sentinel". 

Todo debe estructurarse de manera profesional y limpia en la raíz del repositorio. No debes hacer llamadas HTTP reales a GitHub ni a la API del LLM; todo en el código de pruebas debe usar mocks.

Escribe e implementa los siguientes entregables organizados:

1. PRUEBAS DE FILTRADO EN CAPAS (github_client.py / repo_analyzer.py):
   - Caso A: Un listado de archivos que contenga elementos válidos (.py, .js) y elementos que deban ser excluidos por extensión (.lock, .log, .map) o por ruta (node_modules/, __pycache__/, dist/). Verifica que solo pasen los archivos permitidos por la whitelist.
   - Caso B (Caso de Borde): Un PR donde, tras aplicar el filtro de 3 capas, queden 0 archivos válidos. Verifica que el sistema maneje este escenario devolviendo una estructura controlada o lanzando la excepción esperada para notificar que no hay código relevante que auditar.

2. PRUEBAS DE FORMATO HTML COLAPSABLE (report_formatter.py):
   - Caso A (Multi-vulnerabilidad): Pasa un diccionario 'findings' que contenga simultáneamente múltiples errores distribuidos en diferentes archivos: 2 Bloqueantes (violando ADR-001 y ADR-002) y 1 Advertencia (violando ADR-003). Verifica que el Markdown generado contenga las etiquetas `<details open><summary>🔴 Bloqueantes (2)</summary>` y `<details><summary>🟡 Advertencias (1)</summary>` con sus respectivas tablas estructuradas.
   - Caso B (Sección Vacía): Pasa un diccionario donde la lista de 'suggestions' esté vacía. Verifica que el reporte no omita la sección, sino que renderice correctamente `<details><summary>🟢 Sugerencias (0)</summary>` conteniendo el mensaje "✅ Sin sugerencias detectadas" dentro del bloque HTML.

3. PRUEBAS DE RESPUESTA MULTI-ERROR DEL LLM (llm_reasoner.py):
   - Caso A: Mockea una respuesta de la API que devuelva un JSON con múltiples fallos concurrentes en más de un archivo a la vez (ej. api/users.py y api/analytics.py). Verifica que call_llm() parsee correctamente toda la lista completa de objetos sin truncar ni detenerse en el primer error detectado.

4. ACTUALIZACIÓN DE CONFIGURACIÓN (requirements.txt):
   - Genera el archivo `requirements.txt` en la raíz del proyecto agregando de forma limpia las versiones exactas estipuladas en las bases técnicas del plan:
     requests>=2.31.0
     python-dotenv>=1.0.0
     pytest>=7.0.0

5. DOCUMENTACIÓN DE PRODUCCIÓN (README.md):
   - Genera un archivo `README.md` con un diseño altamente profesional y estructurado usando Badges, títulos limpios y bloques de código claros. El documento debe incluir obligatoriamente:
     - **Título y Tagline:** PR Sentinel — Auditor Semántico de Pull Requests (Powered by IBM watsonx.ai).
     - **Problema que resuelve:** Explicar el concepto del "Verification Tax" (cómo los seniors pierden tiempo revisando código basura o que viola reglas arquitectónicas de IA) y cómo automatiza la gobernanza.
     - **Core Tecnológico (Crucial):** Detallar explícitamente que el motor de razonamiento de `llm_reasoner.py` utiliza la API Cloud de **IBM watsonx.ai** integrada con el modelo fundacional **Granite**, configurado con `temperature: 0` para auditorías semánticas deterministas y reproducibles.
     - **Características Principales:** Filtro inteligente de archivos en 3 capas, análisis concurrente multi-vulnerabilidad (ADR-001, ADR-002, ADR-003), y formateo premium de reportes inyectados en la PR usando bloques colapsables HTML nativos de GitHub.
     - **Guía de Instalación y Ejecución:** Explicar paso a paso la creación del entorno virtual (`venv`), la instalación con `pip install -r requirements.txt`, la configuración de variables de entorno en el `.env` (sin revelar credenciales reales), y los comandos exactos para ejecutar el pipeline (`python sentinel.py`) y la suite de pruebas (`pytest tests/test_improvements.py -v`).

Proporciona el código de `tests/test_improvements.py`, el contenido de `requirements.txt` y el cuerpo completo en Markdown del nuevo `README.md`.
</task>
<environment_details>
# VSCode Visible Files
README.md

# VSCode Open Tabs
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md,demo_repo/docs/adr/ADR-001-estructura-modular.md,demo_repo/docs/adr/ADR-003-manejo-de-errores.md,demo_repo/ARCHITECTURE.md,ARCHITECTURE.md,README.md,tests/test_report_formatter.py,tests/test_repo_analyzer.py,.env,test_enhanced_formatter.py,EXAMPLE_PR_COMMENT.md,tests/test_llm_reasoner.py,repo_analyzer.py,report_formatter.py,MEJORAS_REPORT_FORMATTER.md,llm_reasoner.py,github_client.py,tests/test_improvements.py,requirements.txt,GUIA_INSTALACION.md

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T23:06:51.207Z
User time zone: America/Mexico_City, UTC-6:00

# Current Cost
$0.00

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>


# Current Workspace Directory (/home/yamato/pr-sentinel) Files
.gitignore
ARCHITECTURE.md
EXAMPLE_PR_COMMENT.md
github_client.py
GUIA_INSTALACION.md
LICENSE
llm_reasoner.py
MEJORAS_REPORT_FORMATTER.md
README.md
repo_analyzer.py
report_formatter.py
requirements.txt
sentinel.py
test_enhanced_formatter.py
test_watsonx.py
.venv/
Bob_sesion_llm-reasoner/
Bob_sesion_llm-reasoner/.DS_Store
Bob_sesion_llm-reasoner/bob_task_may-15-2026_11-03-32-am.md
Bob_sesion_llm-reasoner/bob_task_may-15-2026_11-18-10-am.md
Bob_sesion_llm-reasoner/bob_task_may-15-2026_11-21-48-am.md
bob_sessions_demo/
bob_sessions_demo/bob_task_1_ADR002.png
bob_sessions_demo/bob_task_1.md
bob_sessions_demo/bob_task_2_API_Orders.md
bob_sessions_demo/bob_task_2_API_ORDERS.md
bob_sessions_demo/bob_task_2_API_Orders.png
bob_sessions_demo/bob_task_2_APIOrders.png
bob_sessions_demo/bob_task_3_API_USERS.md
bob_sessions_demo/bob_task_3_API_Users.png
bob_sessions_demo/bob_task_4_MIDDLEWARE.md
bob_sessions_demo/bob_task_4_MIDDLEWARE.png
bob_sessions_demo/bob_task_5_DB.md
bob_sessions_demo/bob_task_5_DB.png
bob_sessions_demo/bob_task_6_USER_SERVICE.md
bob_sessions_demo/bob_task_6_USER_SERVICE.png
bob_sessions_demo/bob_task_7_ORDER_SERVICE.md
bob_sessions_demo/bob_task_7_ORDER_SERVICE.png
bob_sessions_demo/bob_task_8_PRODUCTS.md
bob_sessions_demo/bob_task_8_PRODUCTS.png
bob_sessions_demo/bob_task_9_ADR001_ADR003.md
bob_sessions_demo/bob_task_9_ADR001_ADR003.png
bob_sessions_demo/bob_task_10_ARCHITECTURE.md
bob_sessions_demo/bob_task_10_ARCHUITECTURE.png
bob_sessions_demo/bob_task_11_README.md
bob_sessions_demo/bob_task_11_README.png
demo_repo/
demo_repo/ARCHITECTURE.md
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
tests/test_improvements.py
tests/test_llm_reasoner.py
tests/test_repo_analyzer.py
tests/test_report_formatter.py
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

I'll help you create a comprehensive test suite, consolidate dependencies, and generate professional documentation for the PR Sentinel project. Let me start by reading the existing code to understand the structure.

<read_file>
<args>
<file>
<path>github_client.py</path>
</file>
<file>
<path>repo_analyzer.py</path>
</file>
<file>
<path>report_formatter.py</path>
</file>
<file>
<path>llm_reasoner.py</path>
</file>
<file>
<path>requirements.txt</path>
</file>
</args>
</read_file>

---

**User:**

[read_file for 5 files] Result:
<files>
<file><path>github_client.py</path>
<content lines="1-311">
  1 | """
  2 | GitHub API Client Module
  3 | Provides functions to interact with GitHub API for PR analysis.
  4 | """
  5 | 
  6 | import base64
  7 | import requests
  8 | from requests.exceptions import HTTPError, ConnectionError
  9 | 
 10 | 
 11 | def get_pr_diff(repo: str, pr_number: int, token: str) -> tuple:
 12 |     """
 13 |     Obtiene el diff de una PR y los archivos modificados.
 14 |     Retorna: (diff_string, [list_of_changed_files])
 15 |     """
 16 |     url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
 17 |     headers = {
 18 |         "Authorization": f"Bearer {token}",
 19 |         "Accept": "application/vnd.github.v3+json"
 20 |     }
 21 |     
 22 |     try:
 23 |         response = requests.get(url, headers=headers, timeout=10)
 24 |         response.raise_for_status()
 25 |         
 26 |         files = response.json()
 27 |         patches = []
 28 |         changed_files = []
 29 |         
 30 |         for file in files:
 31 |             # Filtro: ignorar archivos removidos
 32 |             if file.get('status') == 'removed':
 33 |                 continue
 34 |             
 35 |             filename = file.get('filename')
 36 |             patch = file.get('patch')
 37 |             
 38 |             if filename:
 39 |                 changed_files.append(filename)
 40 |             if patch:
 41 |                 patches.append(patch)
 42 |         
 43 |         diff = '\n'.join(patches)
 44 |         return diff, changed_files
 45 |     
 46 |     except HTTPError as e:
 47 |         print(f"[ERROR] HTTP error in get_pr_diff: {e}")
 48 |         raise
 49 |     except ConnectionError as e:
 50 |         print(f"[ERROR] Connection error in get_pr_diff: {e}")
 51 |         raise
 52 | 
 53 | 
 54 | def get_repo_file(repo: str, path: str, token: str) -> str:
 55 |     url = f"https://api.github.com/repos/{repo}/contents/{path}"
 56 |     headers = {
 57 |         "Authorization": f"Bearer {token}",
 58 |         "Accept": "application/vnd.github.v3+json"
 59 |     }
 60 |     
 61 |     try:
 62 |         response = requests.get(url, headers=headers, timeout=10)
 63 |         response.raise_for_status()
 64 |         
 65 |         data = response.json()
 66 |         
 67 |         # Decodificar base64
 68 |         content_b64 = data.get('content', '')
 69 |         content_decoded = base64.b64decode(content_b64).decode('utf-8')
 70 |         
 71 |         return content_decoded
 72 |     
 73 |     except HTTPError as e:
 74 |         print(f"[ERROR] HTTP error in get_repo_file for {path}: {e}")
 75 |         raise
 76 |     except ConnectionError as e:
 77 |         print(f"[ERROR] Connection error in get_repo_file for {path}: {e}")
 78 |         raise
 79 | 
 80 | 
 81 | class NoValidFilesError(Exception):
 82 |     """Exception raised when no valid files remain after filtering."""
 83 |     pass
 84 | 
 85 | 
 86 | def _should_exclude_by_extension(filepath: str) -> bool:
 87 |     """
 88 |     Capa 1: Excluir extensiones no deseadas.
 89 |     Retorna True si el archivo debe ser excluido.
 90 |     """
 91 |     excluded_extensions = (
 92 |         '.lock', '.log', '.min.js', '.min.css', '.map',
 93 |         '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp',
 94 |         '.pdf', '.zip', '.tar', '.gz', '.rar', '.7z',
 95 |         '.woff', '.woff2', '.ttf', '.eot', '.otf'
 96 |     )
 97 |     return filepath.lower().endswith(excluded_extensions)
 98 | 
 99 | 
100 | def _should_exclude_by_folder(filepath: str) -> bool:
101 |     """
102 |     Capa 2: Excluir carpetas no deseadas.
103 |     Retorna True si el archivo está en una carpeta excluida.
104 |     """
105 |     excluded_folders = (
106 |         'node_modules/', 'dist/', 'build/', '.next/',
107 |         '__pycache__/', '.pytest_cache/', 'coverage/',
108 |         '.git/', '.venv/', 'venv/', 'env/',
109 |         '.idea/', '.vscode/', 'target/', 'out/'
110 |     )
111 |     
112 |     # Normalizar path para comparación
113 |     normalized_path = filepath.replace('\\', '/')
114 |     
115 |     for folder in excluded_folders:
116 |         if f'/{folder}' in f'/{normalized_path}' or normalized_path.startswith(folder):
117 |             return True
118 |     
119 |     return False
120 | 
121 | 
122 | def _is_whitelisted_extension(filepath: str) -> bool:
123 |     """
124 |     Capa 3: Whitelist de inclusión.
125 |     Retorna True si el archivo tiene una extensión permitida.
126 |     """
127 |     whitelisted_extensions = (
128 |         '.py', '.js', '.ts', '.tsx', '.jsx',
129 |         '.yaml', '.yml', '.json', '.toml',
130 |         '.sh', '.bash', '.md', '.txt',
131 |         '.go', '.rs', '.java', '.kt', '.rb'
132 |     )
133 |     return filepath.lower().endswith(whitelisted_extensions)
134 | 
135 | 
136 | def _apply_three_layer_filter(files: list[str]) -> list[str]:
137 |     """
138 |     Aplica el filtro de 3 capas a la lista de archivos.
139 |     
140 |     Capa 1: Excluir extensiones no deseadas
141 |     Capa 2: Excluir carpetas no deseadas
142 |     Capa 3: Whitelist de inclusión
143 |     
144 |     Retorna lista de archivos válidos.
145 |     """
146 |     valid_files = []
147 |     
148 |     for filepath in files:
149 |         # Capa 1: Excluir extensiones
150 |         if _should_exclude_by_extension(filepath):
151 |             continue
152 |         
153 |         # Capa 2: Excluir carpetas
154 |         if _should_exclude_by_folder(filepath):
155 |             continue
156 |         
157 |         # Capa 3: Whitelist
158 |         if not _is_whitelisted_extension(filepath):
159 |             continue
160 |         
161 |         valid_files.append(filepath)
162 |     
163 |     return valid_files
164 | 
165 | 
166 | def list_python_files(repo: str, token: str) -> list[str]:
167 |     """
168 |     Obtiene todos los archivos Python válidos del repositorio.
169 |     Aplica filtrado de 3 capas para excluir archivos no deseados.
170 |     
171 |     Args:
172 |         repo: Nombre del repositorio en formato "owner/repo"
173 |         token: Token de autenticación de GitHub
174 |     
175 |     Returns:
176 |         Lista de rutas de archivos Python válidos
177 |     
178 |     Raises:
179 |         NoValidFilesError: Si no quedan archivos válidos después del filtrado
180 |         HTTPError: Si hay un error en la petición HTTP
181 |         ConnectionError: Si hay un error de conexión
182 |     """
183 |     url = f"https://api.github.com/repos/{repo}/git/trees/HEAD?recursive=1"
184 |     headers = {
185 |         "Authorization": f"Bearer {token}",
186 |         "Accept": "application/vnd.github.v3+json"
187 |     }
188 |     
189 |     try:
190 |         response = requests.get(url, headers=headers, timeout=10)
191 |         response.raise_for_status()
192 |         
193 |         data = response.json()
194 |         
195 |         # Control de Truncado
196 |         if data.get('truncated', False):
197 |             print('[WARN] Árbol del repo truncado por GitHub - análisis parcial')
198 |         
199 |         # Obtener todos los archivos del repositorio
200 |         tree = data.get('tree', [])
201 |         all_files = [
202 |             item['path']
203 |             for item in tree
204 |             if item.get('type') == 'blob' and item.get('path')
205 |         ]
206 |         
207 |         # Filtrar solo archivos Python
208 |         python_files = [f for f in all_files if f.endswith('.py')]
209 |         
210 |         # Aplicar filtro de 3 capas
211 |         valid_files = _apply_three_layer_filter(python_files)
212 |         
213 |         # Validación: si no quedan archivos válidos
214 |         if not valid_files:
215 |             raise NoValidFilesError(
216 |                 f"No se encontraron archivos Python válidos en {repo} después del filtrado"
217 |             )
218 |         
219 |         return valid_files
220 |     
221 |     except HTTPError as e:
222 |         print(f"[ERROR] HTTP error in list_python_files: {e}")
223 |         raise
224 |     except ConnectionError as e:
225 |         print(f"[ERROR] Connection error in list_python_files: {e}")
226 |         raise
227 | 
228 | 
229 | def list_valid_files(repo: str, token: str) -> list[str]:
230 |     """
231 |     Obtiene todos los archivos válidos del repositorio (no solo Python).
232 |     Aplica filtrado de 3 capas para excluir archivos no deseados.
233 |     
234 |     Args:
235 |         repo: Nombre del repositorio en formato "owner/repo"
236 |         token: Token de autenticación de GitHub
237 |     
238 |     Returns:
239 |         Lista de rutas de archivos válidos
240 |     
241 |     Raises:
242 |         NoValidFilesError: Si no quedan archivos válidos después del filtrado
243 |         HTTPError: Si hay un error en la petición HTTP
244 |         ConnectionError: Si hay un error de conexión
245 |     """
246 |     url = f"https://api.github.com/repos/{repo}/git/trees/HEAD?recursive=1"
247 |     headers = {
248 |         "Authorization": f"Bearer {token}",
249 |         "Accept": "application/vnd.github.v3+json"
250 |     }
251 |     
252 |     try:
253 |         response = requests.get(url, headers=headers, timeout=10)
254 |         response.raise_for_status()
255 |         
256 |         data = response.json()
257 |         
258 |         # Control de Truncado
259 |         if data.get('truncated', False):
260 |             print('[WARN] Árbol del repo truncado por GitHub - análisis parcial')
261 |         
262 |         # Obtener todos los archivos del repositorio
263 |         tree = data.get('tree', [])
264 |         all_files = [
265 |             item['path']
266 |             for item in tree
267 |             if item.get('type') == 'blob' and item.get('path')
268 |         ]
269 |         
270 |         # Aplicar filtro de 3 capas
271 |         valid_files = _apply_three_layer_filter(all_files)
272 |         
273 |         # Validación: si no quedan archivos válidos
274 |         if not valid_files:
275 |             raise NoValidFilesError(
276 |                 f"No se encontraron archivos válidos en {repo} después del filtrado"
277 |             )
278 |         
279 |         return valid_files
280 |     
281 |     except HTTPError as e:
282 |         print(f"[ERROR] HTTP error in list_valid_files: {e}")
283 |         raise
284 |     except ConnectionError as e:
285 |         print(f"[ERROR] Connection error in list_valid_files: {e}")
286 |         raise
287 | 
288 | 
289 | def post_pr_comment(repo: str, pr_number: int, body: str, token: str) -> bool:
290 |     url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
291 |     headers = {
292 |         "Authorization": f"Bearer {token}",
293 |         "Accept": "application/vnd.github.v3+json",
294 |         "Content-Type": "application/json"
295 |     }
296 |     payload = {"body": body}
297 |     
298 |     try:
299 |         response = requests.post(url, headers=headers, json=payload, timeout=10)
300 |         response.raise_for_status()
301 |         
302 |         return response.status_code == 201
303 |     
304 |     except HTTPError as e:
305 |         print(f"[ERROR] HTTP error in post_pr_comment: {e}")
306 |         return False
307 |     except ConnectionError as e:
308 |         print(f"[ERROR] Connection error in post_pr_comment: {e}")
309 |         return False
310 | 
311 | # Made with Bob and modified by P2
</content>
</file>
<file><path>repo_analyzer.py</path>
<content lines="1-75">
 1 | import ast
 2 | from pathlib import Path
 3 | 
 4 | 
 5 | def read_adrs(local_path: str) -> list[str]:
 6 |     """
 7 |     Lee todos los archivos ADR (.md) dentro de docs/adr/
 8 |     """
 9 |     adr_path = Path(local_path) / "docs" / "adr"
10 | 
11 |     if not adr_path.exists():
12 |         return []
13 | 
14 |     adrs = []
15 | 
16 |     for file in adr_path.glob("*.md"):
17 |         try:
18 |             adrs.append(file.read_text(encoding="utf-8"))
19 |         except Exception:
20 |             continue
21 | 
22 |     return adrs
23 | 
24 | 
25 | def read_rules(local_path: str) -> str:
26 |     """
27 |     Lee ARCHITECTURE.md o CLAUDE.md desde la raíz del repositorio.
28 |     """
29 |     root_path = Path(local_path)
30 | 
31 |     architecture_file = root_path / "ARCHITECTURE.md"
32 |     claude_file = root_path / "CLAUDE.md"
33 | 
34 |     if architecture_file.exists():
35 |         return architecture_file.read_text(encoding="utf-8")
36 | 
37 |     if claude_file.exists():
38 |         return claude_file.read_text(encoding="utf-8")
39 | 
40 |     return ""
41 | 
42 | 
43 | def extract_imports(source_code: str) -> list[str]:
44 |     """
45 |     Extrae imports de un código Python usando AST.
46 |     """
47 |     imports = []
48 | 
49 |     try:
50 |         tree = ast.parse(source_code)
51 |     except SyntaxError:
52 |         return []
53 | 
54 |     for node in ast.walk(tree):
55 |         if isinstance(node, ast.Import):
56 |             for alias in node.names:
57 |                 imports.append(alias.name)
58 | 
59 |         elif isinstance(node, ast.ImportFrom):
60 |             if node.module:
61 |                 imports.append(node.module)
62 | 
63 |     return imports
64 | 
65 | 
66 | def build_import_map(files_dict: dict[str, str]) -> dict[str, list[str]]:
67 |     """
68 |     Construye un mapa de imports por archivo.
69 |     """
70 |     import_map = {}
71 | 
72 |     for filename, source_code in files_dict.items():
73 |         import_map[filename] = extract_imports(source_code)
74 | 
75 |     return import_map
</content>
</file>
<file><path>report_formatter.py</path>
<content lines="1-105">
  1 | from datetime import datetime, UTC
  2 | 
  3 | 
  4 | def _format_severity_badge(severity: str) -> str:
  5 |     """
  6 |     Genera un badge HTML con estilo visual mejorado para la severidad.
  7 |     """
  8 |     badges = {
  9 |         "blocker": '<span style="background-color: #d73a4a; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold;">🔴 CRÍTICO</span>',
 10 |         "warning": '<span style="background-color: #fbca04; color: black; padding: 2px 8px; border-radius: 3px; font-weight: bold;">⚠️ ADVERTENCIA</span>',
 11 |         "suggestion": '<span style="background-color: #0e8a16; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold;">💡 SUGERENCIA</span>',
 12 |     }
 13 |     return badges.get(severity, severity)
 14 | 
 15 | 
 16 | def _format_finding_with_fix(item: dict, severity: str) -> str:
 17 |     """
 18 |     Formatea un finding individual con soporte para suggested_fix colapsable.
 19 |     """
 20 |     description = item.get('description', '')
 21 |     file_path = item.get('file', '')
 22 |     line = item.get('line', '')
 23 |     adr_ref = item.get('adr_reference', '')
 24 |     suggested_fix = item.get('suggested_fix', '')
 25 |     
 26 |     # Badge de severidad
 27 |     badge = _format_severity_badge(severity)
 28 |     
 29 |     # Construir la fila base
 30 |     row = f"| {badge} | {description} | `{file_path}` | {line} | {adr_ref} |"
 31 |     
 32 |     # Si hay suggested_fix, agregar detalles colapsables
 33 |     if suggested_fix:
 34 |         details = f"\n<details>\n<summary>🔧 Ver sugerencia de Fix</summary>\n\n```python\n{suggested_fix}\n```\n\n</details>\n"
 35 |         return row + details
 36 |     
 37 |     return row
 38 | 
 39 | 
 40 | def format_report(findings: dict | None) -> str:
 41 |     """
 42 |     Genera un reporte Markdown mejorado para publicar como comentario en una Pull Request.
 43 |     
 44 |     Mejoras:
 45 |     - Badges de severidad con estilo HTML visual
 46 |     - Bloques de código sugeridos en <details> colapsables
 47 |     - Mejor formato de tabla con columnas más claras
 48 |     """
 49 | 
 50 |     if not isinstance(findings, dict):
 51 |         return "Error: findings inválido. No se pudo generar el reporte."
 52 | 
 53 |     blockers = findings.get("blockers", [])
 54 |     warnings = findings.get("warnings", [])
 55 |     suggestions = findings.get("suggestions", [])
 56 | 
 57 |     report = []
 58 | 
 59 |     # HEADER
 60 |     report.append("## 🔍 PR Sentinel — Auditoría Automática")
 61 |     report.append("---")
 62 |     report.append("")
 63 | 
 64 |     # BLOQUEANTES
 65 |     report.append(f"### 🔴 Bloqueantes Críticos ({len(blockers)})")
 66 |     report.append("")
 67 |     if blockers:
 68 |         report.append("| Severidad | Descripción | Archivo | Línea | ADR |")
 69 |         report.append("|:---:|---|---|:---:|---|")
 70 |         for item in blockers:
 71 |             report.append(_format_finding_with_fix(item, "blocker"))
 72 |     else:
 73 |         report.append("✅ **Sin bloqueantes detectados**")
 74 |     report.append("")
 75 | 
 76 |     # ADVERTENCIAS
 77 |     report.append(f"### ⚠️ Advertencias ({len(warnings)})")
 78 |     report.append("")
 79 |     if warnings:
 80 |         report.append("| Severidad | Descripción | Archivo | Línea | ADR |")
 81 |         report.append("|:---:|---|---|:---:|---|")
 82 |         for item in warnings:
 83 |             report.append(_format_finding_with_fix(item, "warning"))
 84 |     else:
 85 |         report.append("✅ **Sin advertencias detectadas**")
 86 |     report.append("")
 87 | 
 88 |     # SUGERENCIAS
 89 |     report.append(f"### 💡 Sugerencias de Mejora ({len(suggestions)})")
 90 |     report.append("")
 91 |     if suggestions:
 92 |         report.append("| Severidad | Descripción | Archivo | Línea | ADR |")
 93 |         report.append("|:---:|---|---|:---:|---|")
 94 |         for item in suggestions:
 95 |             report.append(_format_finding_with_fix(item, "suggestion"))
 96 |     else:
 97 |         report.append("✅ **Sin sugerencias detectadas**")
 98 |     report.append("")
 99 | 
100 |     # FOOTER
101 |     report.append("---")
102 |     timestamp = datetime.now(UTC).isoformat()
103 |     report.append(f"*Generado por PR Sentinel vía IBM Bob | {timestamp}*")
104 | 
105 |     return "\n".join(report)
</content>
</file>
<file><path>llm_reasoner.py</path>
<content lines="1-366">
  1 | """
  2 | LLM Reasoner Module - IBM watsonx.ai Edition (granite-3-8b-instruct)
  3 | """
  4 | 
  5 | import requests
  6 | import json
  7 | import os
  8 | import re
  9 | 
 10 | 
 11 | def _get_iam_token(api_key: str) -> str:
 12 |     response = requests.post(
 13 |         "https://iam.cloud.ibm.com/identity/token",
 14 |         headers={"Content-Type": "application/x-www-form-urlencoded"},
 15 |         data=f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={api_key}",
 16 |         timeout=30
 17 |     )
 18 |     response.raise_for_status()
 19 |     return response.json()["access_token"]
 20 | 
 21 | 
 22 | def _call_api(url: str, headers: dict, model_id: str, project_id: str, input_text: str) -> str:
 23 |     """Llama a watsonx.ai y retorna el texto generado con temperature=0 para consistencia."""
 24 |     payload = {
 25 |         "model_id": model_id,
 26 |         "project_id": project_id,
 27 |         "input": input_text,
 28 |         "parameters": {
 29 |             "decoding_method": "greedy",
 30 |             "max_new_tokens": 800,
 31 |             "repetition_penalty": 1.0,
 32 |             "temperature": 0,  # Garantiza consistencia y determinismo
 33 |             "stop_sequences": ["\n\nPlease", "\n\nBased", "\n\nYour", "\n\nNote"]
 34 |         }
 35 |     }
 36 |     response = requests.post(url, headers=headers, json=payload, timeout=90)
 37 |     response.raise_for_status()
 38 |     data = response.json()
 39 | 
 40 |     if "results" in data and data["results"]:
 41 |         return data["results"][0].get("generated_text", "").strip()
 42 |     raise ValueError("Respuesta vacía de watsonx.ai")
 43 | 
 44 | 
 45 | def _extract_json(text: str) -> dict:
 46 |     """
 47 |     Intenta extraer un JSON válido del texto generado.
 48 |     Prueba múltiples estrategias.
 49 |     """
 50 |     # Estrategia 1: limpiar y parsear directo
 51 |     clean = text.strip().replace("```json", "").replace("```", "").strip()
 52 |     try:
 53 |         return json.loads(clean)
 54 |     except json.JSONDecodeError:
 55 |         pass
 56 | 
 57 |     # Estrategia 2: buscar primer { hasta último }
 58 |     start = clean.find("{")
 59 |     end = clean.rfind("}")
 60 |     if start != -1 and end != -1 and end > start:
 61 |         try:
 62 |             return json.loads(clean[start:end+1])
 63 |         except json.JSONDecodeError:
 64 |             pass
 65 | 
 66 |     # Estrategia 3: regex para extraer JSON
 67 |     match = re.search(r'\{.*\}', clean, re.DOTALL)
 68 |     if match:
 69 |         try:
 70 |             return json.loads(match.group())
 71 |         except json.JSONDecodeError:
 72 |             pass
 73 | 
 74 |     raise ValueError(f"No se pudo extraer JSON válido del texto: {text[:200]}")
 75 | 
 76 | 
 77 | def _precompute_violations(import_map: dict, diff: str) -> dict:
 78 |     """
 79 |     Analiza el import_map y el diff para detectar violaciones de forma determinística.
 80 |     Retorna un dict con listas de archivos que violan cada ADR.
 81 |     """
 82 |     adr002_violations = []  # Archivos /api/ sin auth_middleware
 83 |     adr001_violations = []  # Archivos /api/ que importan desde /db/
 84 |     adr003_candidates = []  # Endpoints sin try/except
 85 | 
 86 |     for filename, imports in import_map.items():
 87 |         is_api_file = (
 88 |             filename.startswith("api/") or
 89 |             "/api/" in filename or
 90 |             filename.startswith("demo_repo/api/")
 91 |         )
 92 |         if not is_api_file:
 93 |             continue
 94 | 
 95 |         # ADR-002: ¿tiene auth_middleware en sus imports?
 96 |         has_auth = any(
 97 |             "auth_middleware" in imp.lower() or
 98 |             "auth_middleware" in str(imp).lower()
 99 |             for imp in imports
100 |         )
101 |         if not has_auth:
102 |             adr002_violations.append(filename)
103 | 
104 |         # ADR-001: ¿importa directamente desde /db/?
105 |         imports_db = any(
106 |             imp.startswith("db.") or
107 |             imp.startswith("db/") or
108 |             "/db/" in str(imp)
109 |             for imp in imports
110 |         )
111 |         if imports_db:
112 |             adr001_violations.append(filename)
113 | 
114 |     return {
115 |         "adr002_violations": adr002_violations,
116 |         "adr001_violations": adr001_violations,
117 |         "adr003_candidates": adr003_candidates,
118 |     }
119 | 
120 | 
121 | def _find_endpoints_in_diff_without_auth(diff: str, changed_files: list | None = None) -> list:
122 |     """
123 |     Busca en el diff nuevos endpoints (funciones con decoradores @route, @get, @post)
124 |     que se añaden sin tener @auth_middleware encima.
125 |     Usa changed_files para identificar archivos /api/.
126 |     """
127 |     if not changed_files:
128 |         changed_files = []
129 |     
130 |     endpoints_without_auth = []
131 |     api_files = [f for f in changed_files if "/api/" in f or f.startswith("api/")]
132 |     
133 |     if not api_files:
134 |         return []
135 |     
136 |     # Para archivos nuevos (no tiene +++ b/), asumimos que el diff es del primer archivo
137 |     current_file = api_files[0] if api_files else None
138 |     
139 |     lines = diff.split("\n")
140 |     
141 |     i = 0
142 |     while i < len(lines):
143 |         line = lines[i]
144 |         
145 |         # Buscar decoradores de ruta
146 |         if line.startswith("+") and not line.startswith("+++"):
147 |             stripped = line[1:].lstrip()
148 |             if stripped.startswith("@") and any(x in stripped.lower() for x in ["route", "@get", "@post", "@put", "@delete"]):
149 |                 # Encontramos un decorador de ruta. ¿Tiene auth_middleware antes?
150 |                 has_auth_above = False
151 |                 j = i - 1
152 |                 while j >= 0 and j > i - 10:  # Mirar máximo 9 líneas atrás
153 |                     prev_line = lines[j][1:].lstrip() if lines[j].startswith("+") else lines[j].lstrip()
154 |                     if "auth_middleware" in prev_line.lower() or "@auth" in prev_line.lower():
155 |                         has_auth_above = True
156 |                         break
157 |                     j -= 1
158 |                 
159 |                 # Si no tiene auth_middleware, buscar la función siguiente
160 |                 if not has_auth_above:
161 |                     k = i + 1
162 |                     func_name = None
163 |                     while k < len(lines) and k < i + 10:
164 |                         next_line = lines[k]
165 |                         stripped_next = next_line[1:].lstrip() if next_line.startswith("+") else next_line.lstrip()
166 |                         if stripped_next.startswith("def "):
167 |                             func_name = stripped_next.split("def ")[1].split("(")[0]
168 |                             endpoints_without_auth.append({
169 |                                 "file": current_file,
170 |                                 "function": func_name
171 |                             })
172 |                             break
173 |                         k += 1
174 |         
175 |         i += 1
176 |     
177 |     return endpoints_without_auth
178 | 
179 | 
180 | def build_prompt(diff: str, adrs: list, rules: str, import_map: dict, changed_files: list) -> str:
181 |     """
182 |     Construye un prompt COMPACTO y directo que genere SOLO JSON sin explicaciones extras.
183 |     Analiza tanto import_map como diff para detectar violaciones.
184 |     INSTRUYE EXPLÍCITAMENTE al LLM a auditar TODOS los archivos en changed_files.
185 |     """
186 |     violations = _precompute_violations(import_map, diff)
187 |     adr002_files = list(violations["adr002_violations"])
188 |     adr001_files = violations["adr001_violations"]
189 |     adr003_items = violations["adr003_candidates"]
190 |     
191 |     # TAMBIÉN detectar endpoints en el diff sin @auth_middleware
192 |     # Pasar changed_files para saber en qué archivo estamos
193 |     diff_endpoints_without_auth = _find_endpoints_in_diff_without_auth(diff, changed_files)
194 |     if diff_endpoints_without_auth:
195 |         for ep in diff_endpoints_without_auth:
196 |             if ep["file"] not in adr002_files:
197 |                 adr002_files.append(ep["file"])
198 | 
199 |     adr002_str = "\n".join(f"  {f}" for f in adr002_files) if adr002_files else "  (none detected)"
200 |     adr001_str = "\n".join(f"  {f}" for f in adr001_files) if adr001_files else "  (none detected)"
201 |     adr003_str = "\n".join(f"  {c['file']} -> {c['function']}()" for c in adr003_items) if adr003_items else "  (none detected)"
202 |     
203 |     # Lista de archivos modificados para auditoría exhaustiva
204 |     changed_files_str = "\n".join(f"  - {f}" for f in changed_files) if changed_files else "  (none)"
205 | 
206 |     prompt = f"""CODE AUDIT TASK - RETURN JSON ONLY
207 | 
208 | CRITICAL INSTRUCTION:
209 | You MUST audit ALL files listed in CHANGED FILES below against ALL rules (ADR-001, ADR-002, ADR-003).
210 | Do NOT stop at the first error you find. Analyze EXHAUSTIVELY each modified file and report ALL concurrent violations in the JSON output.
211 | 
212 | CHANGED FILES TO AUDIT:
213 | {changed_files_str}
214 | 
215 | VIOLATIONS FOUND BY STATIC ANALYSIS:
216 | 
217 | ADR-002 (missing @auth_middleware in /api/):
218 | {adr002_str}
219 | 
220 | ADR-001 (direct imports from /db/ in /api/):
221 | {adr001_str}
222 | 
223 | ADR-003 (missing error handling):
224 | {adr003_str}
225 | 
226 | AUDIT REQUIREMENTS:
227 | 1. Review EVERY file in the CHANGED FILES list above
228 | 2. Check each file against ADR-001, ADR-002, and ADR-003
229 | 3. Report ALL violations found, not just the first one
230 | 4. Include all violations in the JSON output structure below
231 | 
232 | GENERATE THIS JSON STRUCTURE FROM ALL VIOLATIONS FOUND.
233 | Use the filenames from the violations detected above.
234 | Return valid JSON with no explanation before or after.
235 | Start immediately with {{ character.
236 | 
237 | {{
238 |   "blockers": [
239 |     {{
240 |       "description": "API endpoint missing auth_middleware",
241 |       "file": "actual/file.py",
242 |       "line": "0",
243 |       "adr_reference": "ADR-002"
244 |     }}
245 |   ],
246 |   "warnings": [],
247 |   "suggestions": []
248 | }}
249 | 
250 | IMPORTANT: Return JSON ONLY. No text before {{ or after }}. Start now:"""
251 | 
252 |     return prompt
253 | 
254 | 
255 | def call_llm(prompt: str, api_key: str) -> dict:
256 |     """
257 |     Llama a watsonx.ai con granite-3-8b-instruct y retorna el análisis estructurado.
258 |     Mejorado para devolver SOLO JSON.
259 |     """
260 |     watsonx_url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
261 |     project_id = os.getenv("WATSONX_PROJECT_ID")
262 |     model_id = os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct")
263 |     url = f"{watsonx_url}/ml/v1/text/generation?version=2023-05-29"
264 | 
265 |     if not project_id:
266 |         raise ValueError("WATSONX_PROJECT_ID no configurado en .env")
267 | 
268 |     try:
269 |         iam_token = _get_iam_token(api_key)
270 |         headers = {
271 |             "Authorization": f"Bearer {iam_token}",
272 |             "Content-Type": "application/json",
273 |             "Accept": "application/json"
274 |         }
275 | 
276 |         # --- Primer intento ---
277 |         raw = _call_api(url, headers, model_id, project_id, prompt)
278 | 
279 |         try:
280 |             result = _extract_json(raw)
281 |             return sanitize_and_fill_keys(result)
282 | 
283 |         except ValueError as parse_error:
284 |             print(f"\n  Primer intento falló al parsear JSON: {parse_error}")
285 | 
286 |             # --- Reintento: prompt ultra-simple que solo pide JSON ---
287 |             retry_prompt = """Output valid JSON only. No explanation.
288 | 
289 | Return this structure with violations found:
290 | {
291 |   "blockers": [
292 |     {
293 |       "description": "API endpoint missing auth_middleware",
294 |       "file": "api/users.py",
295 |       "line": "0",
296 |       "adr_reference": "ADR-002"
297 |     }
298 |   ],
299 |   "warnings": [],
300 |   "suggestions": []
301 | }
302 | 
303 | JSON ONLY:"""
304 | 
305 |             iam_token = _get_iam_token(api_key)
306 |             headers["Authorization"] = f"Bearer {iam_token}"
307 | 
308 |             print("  Reintentando con prompt simplificado...")
309 |             raw2 = _call_api(url, headers, model_id, project_id, retry_prompt)
310 | 
311 |             try:
312 |                 result = _extract_json(raw2)
313 |                 print("  Reintento exitoso.")
314 |                 return sanitize_and_fill_keys(result)
315 |             except ValueError:
316 |                 print("  Ambos intentos fallaron, usando fallback determinístico.")
317 |                 return {
318 |                     "blockers": [{
319 |                         "description": "API endpoint missing @auth_middleware decorator - ADR-002 violation",
320 |                         "file": "api/users.py",
321 |                         "line": "0",
322 |                         "adr_reference": "ADR-002"
323 |                     }],
324 |                     "warnings": [],
325 |                     "suggestions": []
326 |                 }
327 | 
328 |     except requests.exceptions.RequestException as req_error:
329 |         print(f"  Error HTTP con watsonx.ai: {req_error}")
330 |         return {
331 |             "blockers": [{"description": f"Fallo HTTP: {str(req_error)}", "file": "None", "line": "0", "adr_reference": "None"}],
332 |             "warnings": [],
333 |             "suggestions": []
334 |         }
335 |     except Exception as e:
336 |         print(f"  Error inesperado: {e}")
337 |         return {
338 |             "blockers": [{"description": f"Error: {str(e)}", "file": "None", "line": "0", "adr_reference": "None"}],
339 |             "warnings": [],
340 |             "suggestions": []
341 |         }
342 | 
343 | 
344 | def sanitize_and_fill_keys(result: dict) -> dict:
345 |     if not isinstance(result, dict):
346 |         result = {}
347 |     for key in ["blockers", "warnings", "suggestions"]:
348 |         if key not in result or not isinstance(result[key], list):
349 |             result[key] = []
350 |     return result
351 | 
352 | 
353 | def validate_response_structure(response: dict) -> bool:
354 |     if not isinstance(response, dict):
355 |         return False
356 |     required_keys = ["blockers", "warnings", "suggestions"]
357 |     required_fields = ["description", "file", "line", "adr_reference"]
358 |     for key in required_keys:
359 |         if key not in response or not isinstance(response[key], list):
360 |             return False
361 |         for item in response[key]:
362 |             if not isinstance(item, dict):
363 |                 return False
364 |             if not all(f in item for f in required_fields):
365 |                 return False
366 |     return True
</content>
</file>
<file><path>requirements.txt</path>
<content lines="1-10">
 1 | # Core dependencies
 2 | requests>=2.31.0
 3 | python-dotenv>=1.0.0
 4 | 
 5 | # Testing dependencies
 6 | pytest>=7.0.0
 7 | pytest-cov>=4.1.0
 8 | 
 9 | # Code analysis (used by repo_analyzer.py for AST parsing)
10 | # Note: ast is part of Python standard library, no need to install
</content>
</file>
</files>
<environment_details>
# VSCode Visible Files
README.md

# VSCode Open Tabs
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md,demo_repo/docs/adr/ADR-001-estructura-modular.md,demo_repo/docs/adr/ADR-003-manejo-de-errores.md,demo_repo/ARCHITECTURE.md,ARCHITECTURE.md,README.md,tests/test_report_formatter.py,tests/test_repo_analyzer.py,.env,test_enhanced_formatter.py,EXAMPLE_PR_COMMENT.md,tests/test_llm_reasoner.py,repo_analyzer.py,report_formatter.py,MEJORAS_REPORT_FORMATTER.md,llm_reasoner.py,github_client.py,tests/test_improvements.py,requirements.txt,GUIA_INSTALACION.md

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T23:06:58.133Z
User time zone: America/Mexico_City, UTC-6:00

# Current Cost
$0.01

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

I'll create a comprehensive test suite, update dependencies, and generate professional documentation for the PR Sentinel project. Let me start by creating a TODO list to organize this multi-step task.

<update_todo_list>
<todos>
[ ] Create comprehensive test suite in tests/test_improvements.py
[ ] Update requirements.txt with exact versions
[ ] Generate professional README.md with complete documentation
[ ] Verify all deliverables are complete
</todos>
</update_todo_list>

---

**User:**

[update_todo_list] Result:
Todo list updated successfully.
<environment_details>
# VSCode Visible Files
README.md

# VSCode Open Tabs
demo_repo/docs/adr/ADR-002-autenticacion-obligatoria.md,demo_repo/docs/adr/ADR-001-estructura-modular.md,demo_repo/docs/adr/ADR-003-manejo-de-errores.md,demo_repo/ARCHITECTURE.md,ARCHITECTURE.md,README.md,tests/test_report_formatter.py,tests/test_repo_analyzer.py,.env,test_enhanced_formatter.py,EXAMPLE_PR_COMMENT.md,tests/test_llm_reasoner.py,repo_analyzer.py,report_formatter.py,MEJORAS_REPORT_FORMATTER.md,llm_reasoner.py,github_client.py,tests/test_improvements.py,requirements.txt,GUIA_INSTALACION.md

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T23:07:13.302Z
User time zone: America/Mexico_City, UTC-6:00

# Current Cost
$0.06

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
| 1 | Create comprehensive test suite in tests/test_improvements.py | Pending |
| 2 | Update requirements.txt with exact versions | Pending |
| 3 | Generate professional README.md with complete documentation | Pending |
| 4 | Verify all deliverables are complete | Pending |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

