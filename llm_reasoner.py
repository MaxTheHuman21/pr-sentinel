"""
LLM Reasoner Module - IBM watsonx.ai Edition (granite-3-8b-instruct)
"""

import requests
import json
import os
import re


def _get_iam_token(api_key: str) -> str:
    response = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={api_key}",
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def _call_api(url: str, headers: dict, model_id: str, project_id: str, input_text: str) -> str:
    """Llama a watsonx.ai y retorna el texto generado con temperature=0 para consistencia."""
    payload = {
        "model_id": model_id,
        "project_id": project_id,
        "input": input_text,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 1500,
            "repetition_penalty": 1.0,
            "temperature": 0,
            "stop_sequences": ["\n\nPlease", "\n\nBased", "\n\nYour", "\n\nNote"],
        },
    }
    response = requests.post(url, headers=headers, json=payload, timeout=90)
    response.raise_for_status()
    data = response.json()

    if "results" in data and data["results"]:
        return data["results"][0].get("generated_text", "").strip()
    raise ValueError("Respuesta vacía de watsonx.ai")


def _extract_json(text: str) -> dict:
    """Intenta extraer un JSON válido del texto generado mediante múltiples estrategias."""
    clean = text.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        pass

    start = clean.find("{")
    end = clean.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(clean[start : end + 1])
        except json.JSONDecodeError:
            pass

    match = re.search(r"\{.*\}", clean, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"No se pudo extraer JSON válido del texto: {text[:200]}")


def _extract_file_contents_from_diff(diff: str, changed_files: list) -> dict:
    """
    Extrae el contenido completo de cada archivo desde el diff.
    Retorna: {filepath: full_content_string}
    
    Para archivos nuevos, el contenido son todas las líneas que empiezan con '+'.
    Para archivos modificados, reconstruye el contenido post-cambio.
    """
    file_contents = {}
    lines = diff.split("\n")
    current_file = None
    current_content_lines = []
    
    for line in lines:
        # Detectar inicio de un nuevo archivo
        if line.startswith("+++ b/"):
            # Guardar el archivo anterior si existe
            if current_file and current_content_lines:
                file_contents[current_file] = "\n".join(current_content_lines)
            
            # Iniciar nuevo archivo
            current_file = line[6:].strip()
            current_content_lines = []
        
        elif current_file:
            # Para archivos nuevos (@@... +1,27 @@), todas las líneas + son contenido
            # Para archivos modificados, tomamos las líneas + (agregadas) y las líneas sin prefijo (contexto)
            if line.startswith("+") and not line.startswith("+++"):
                # Línea agregada - es parte del contenido nuevo
                current_content_lines.append(line[1:])  # Remover el '+'
            elif not line.startswith("-") and not line.startswith("@@") and not line.startswith("+++") and not line.startswith("---"):
                # Línea de contexto (sin prefijo) - también es parte del contenido
                current_content_lines.append(line)
    
    # Guardar el último archivo
    if current_file and current_content_lines:
        file_contents[current_file] = "\n".join(current_content_lines)
    
    return file_contents


def _analyze_diff_for_violations(diff: str, changed_files: list, files_dict: dict | None = None) -> dict:
    """
    Analiza el DIFF directamente para detectar violaciones arquitectónicas.
    
    Esta función NO depende del import_map (que solo contiene archivos existentes),
    sino que parsea el diff para analizar archivos nuevos y modificados.
    
    Esto resuelve el problema donde archivos nuevos en una PR nunca eran analizados.
    """
    adr002_violations = []
    adr001_violations = []
    adr003_critical_violations = []  # BLOCKERS: except Exception: pass
    adr003_warnings = []  # WARNINGS: missing try/except
    suggestions = []
    
    # Extraer contenido de archivos desde el diff
    file_contents = _extract_file_contents_from_diff(diff, changed_files)
    
    for filepath, content in file_contents.items():
        normalized_filepath = filepath.replace("demo_repo/", "").replace("\\", "/")
        
        # Identificar tipo de archivo para sugerencias específicas
        is_api_file = (
            normalized_filepath.startswith("api/") or "/api/" in normalized_filepath
        )
        is_service_file = (
            normalized_filepath.startswith("services/") or "/services/" in normalized_filepath
        )
        is_db_file = (
            normalized_filepath.startswith("db/") or "/db/" in normalized_filepath
        )
        
        lines = content.split("\n")
        
        # ADR-002: Archivos con endpoints Flask sin @auth_middleware decorator
        # Buscar el decorador @auth_middleware (debe estar en una línea que empiece con @)
        has_auth_decorator = any(
            line.strip().startswith("@") and "auth_middleware" in line
            for line in lines
        )
        
        # Buscar import de auth_middleware (debe estar en línea de import)
        has_auth_import = any(
            "import" in line and "auth_middleware" in line
            for line in lines
        )
        
        # Detectar si el archivo define endpoints Flask (cualquier función con decoradores o rutas)
        has_flask_endpoints = (
            ("@app.route" in content or "@route" in content or "route(" in content) or
            ("def " in content and ("jsonify" in content or "flask" in content.lower()))
        )
        
        # Si define endpoints Flask pero no tiene auth, es violación ADR-002
        if has_flask_endpoints and not (has_auth_decorator or has_auth_import):
            adr002_violations.append(normalized_filepath)
        
        # ADR-001: CUALQUIER archivo importando directamente de db layer
        # (no solo archivos en api/, puede ser cualquier módulo)
        imports_db_directly = (
            "from db." in content or
            "import db." in content or
            "from db " in content or
            "import db " in content or
            "from database import" in content or
            "from database_utils import" in content or
            "DatabaseClient" in content
        )
        if imports_db_directly:
            # Verificar que no sea un archivo de la capa db/ o services/ (permitido)
            if not (is_db_file or is_service_file):
                adr001_violations.append(normalized_filepath)
        
        # SUGGESTION: missing pagination (solo para archivos API)
        if is_api_file and (
            "get_all" in content.lower()
            and "limit" not in content.lower()
            and "offset" not in content.lower()
        ):
            suggestions.append(
                {
                    "file": normalized_filepath,
                    "type": "pagination",
                    "description": (
                        f"Endpoint in {normalized_filepath} fetches all records without "
                        "pagination, which could cause performance issues with large datasets."
                    ),
                }
            )
        
        # ADR-003: CUALQUIER archivo con manejo pobre de excepciones
        # (no limitado a api/ o services/)
        has_function_def = "def " in content
        has_try_block = "try:" in content
        has_generic_except = "except Exception:" in content or "except Exception as" in content
        
        # CRITICAL: Check for silent failures (except Exception: pass)
        has_critical_violation = False
        if has_generic_except:
            for i, line in enumerate(lines):
                if "except Exception" in line:
                    next_lines = lines[i + 1 : i + 5] if i + 5 < len(lines) else lines[i + 1:]
                    has_pass = any("pass" in l.strip() and l.strip() == "pass" for l in next_lines)
                    has_only_print = any(
                        "print(" in l and "error" in l.lower() for l in next_lines
                    )
                    has_no_logging = not any(
                        "logger." in l or "logging." in l for l in next_lines
                    )
                    
                    # ADR-003 CRITICAL: Check for returning plain strings instead of JSON
                    has_string_return = any(
                        "return" in l and (
                            ('f"' in l or "f'" in l) or  # f-string
                            ('"' in l and "jsonify" not in l) or  # plain string
                            ("'" in l and "jsonify" not in l)  # plain string
                        ) and "jsonify" not in l
                        for l in next_lines
                    )
                    
                    # BLOCKER: Silent failure, print-only, or string return in except block
                    if has_pass or (has_only_print and has_no_logging) or has_string_return:
                        has_critical_violation = True
                        break
        
        if has_critical_violation:
            # This is a BLOCKER - silent failure
            if normalized_filepath not in adr003_critical_violations:
                adr003_critical_violations.append(normalized_filepath)
        elif has_function_def and not has_try_block:
            # WARNING: Function without try/except
            if normalized_filepath not in adr003_warnings:
                adr003_warnings.append(normalized_filepath)
        
        # SUGGESTION: inefficient string concatenation in loops
        if is_service_file or is_db_file:
            lines = content.split("\n")
            in_loop = False
            has_string_concat = False
            for line in lines:
                if "for " in line and " in " in line:
                    in_loop = True
                elif in_loop and ("+=" in line or " + " in line) and (
                    '"' in line or "'" in line
                ):
                    has_string_concat = True
                    break
                elif line.strip() and not line.strip().startswith((" ", "\t")) and in_loop:
                    in_loop = False
            
            if has_string_concat:
                suggestions.append(
                    {
                        "file": normalized_filepath,
                        "type": "string_concatenation",
                        "description": (
                            f"File {normalized_filepath} uses inefficient string concatenation "
                            "in loops. Consider using f-strings or str.join() for better performance."
                        ),
                    }
                )
        
        # SUGGESTION: connection leaks
        if is_db_file:
            if "sqlite3.connect" in content or "Database()" in content:
                if "with " not in content or content.count("connect") > content.count("with "):
                    suggestions.append(
                        {
                            "file": normalized_filepath,
                            "type": "resource_leak",
                            "description": (
                                f"File {normalized_filepath} opens database connections without "
                                "using context managers (with statement), which can cause resource leaks."
                            ),
                        }
                    )
    
    return {
        "adr002_violations": adr002_violations,
        "adr001_violations": adr001_violations,
        "adr003_critical_violations": adr003_critical_violations,
        "adr003_warnings": adr003_warnings,
        "suggestions": suggestions,
    }


def _find_endpoints_in_diff_without_auth(diff: str, changed_files: list | None = None) -> list:
    """
    Busca en el diff nuevos endpoints sin @auth_middleware o
    eliminación explícita de decoradores de seguridad.
    """
    if not changed_files:
        changed_files = []

    endpoints_without_auth = []
    lines = diff.split("\n")
    current_file = changed_files[0] if changed_files else None

    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith("+++ b/"):
            current_file = line[6:].strip()
            i += 1
            continue
        elif line.startswith("+++ "):
            current_file = line[4:].strip()
            i += 1
            continue

        if current_file and ("/api/" in current_file or current_file.startswith("api/")):
            # Detect removal of auth decorator
            if line.startswith("-") and not line.startswith("---"):
                stripped_removed = line[1:].lstrip()
                if "auth_middleware" in stripped_removed.lower() or "@auth" in stripped_removed.lower():
                    endpoints_without_auth.append(
                        {"file": current_file, "function": "[DECORADOR SEGURIDAD ELIMINADO]"}
                    )

            # Detect new route added without auth decorator above it
            if line.startswith("+") and not line.startswith("+++"):
                stripped = line[1:].lstrip()
                if stripped.startswith("@") and any(
                    x in stripped.lower() for x in ["route", "get", "post", "put", "delete"]
                ):
                    has_auth_above = False
                    j = i - 1
                    while j >= 0 and j > i - 10:
                        prev = lines[j]
                        prev_stripped = prev[1:].lstrip() if prev.startswith("+") else prev.lstrip()
                        if "auth_middleware" in prev_stripped.lower() or "@auth" in prev_stripped.lower():
                            has_auth_above = True
                            break
                        j -= 1

                    if not has_auth_above:
                        k = i + 1
                        while k < len(lines) and k < i + 10:
                            next_line = lines[k]
                            next_stripped = (
                                next_line[1:].lstrip()
                                if next_line.startswith("+")
                                else next_line.lstrip()
                            )
                            if next_stripped.startswith("def "):
                                func_name = next_stripped.split("def ")[1].split("(")[0]
                                endpoints_without_auth.append(
                                    {"file": current_file, "function": func_name}
                                )
                                break
                            k += 1
        i += 1

    return endpoints_without_auth


def build_prompt(
    diff: str,
    adrs: list,
    rules: str,
    import_map: dict,
    changed_files: list,
    *args,
    **kwargs,
) -> str:
    """
    Construye un prompt semántico unificado.
    Permite que el LLM evalúe el Diff de forma natural contra todos los ADRs.
    """
    # BUG FIX: files_dict was silently swallowed by *args and never passed to
    # _precompute_violations, so all content-based checks (pagination, ADR-003, etc.)
    # were dead code. Extract it explicitly and narrow to dict so the type
    # checker is satisfied — None becomes {} which safely skips content checks.
    raw_files_dict = args[0] if args else kwargs.get("files_dict")
    files_dict: dict = raw_files_dict if isinstance(raw_files_dict, dict) else {}

    violations = _analyze_diff_for_violations(diff, changed_files, files_dict)

    adr002_files = violations.get("adr002_violations", [])
    adr001_files = violations.get("adr001_violations", [])
    adr003_critical_files = violations.get("adr003_critical_violations", [])
    adr003_warning_files = violations.get("adr003_warnings", [])

    adr002_str = (
        "\n".join(f"  {f}" for f in adr002_files)
        if adr002_files
        else "  (none detected statically)"
    )
    adr001_str = (
        "\n".join(f"  {f}" for f in adr001_files)
        if adr001_files
        else "  (none detected statically)"
    )
    adr003_critical_str = (
        "\n".join(f"  {f} (CRITICAL: except Exception: pass)" for f in adr003_critical_files)
        if adr003_critical_files
        else "  (none detected statically)"
    )
    adr003_warning_str = (
        "\n".join(f"  {f} (missing try/except)" for f in adr003_warning_files)
        if adr003_warning_files
        else "  (none detected statically)"
    )

    changed_files_str = (
        "\n".join(f"  - {f}" for f in changed_files) if changed_files else "  (none)"
    )
    adrs_str = "\n\n".join(adrs) if adrs else "(none documented)"

    prompt = f"""You are 'PR Sentinel', an AI Semantic Code Auditor powered by IBM watsonx.
Your job is to read the raw Pull Request Diff and detect architectural violations based on the Architecture Decision Records (ADRs).

CRITICAL AUDIT INSTRUCTIONS (EVALUATE ALL ADRs EQUALLY):
1. RELY ON SEMANTICS: Read the RAW PULL REQUEST DIFF carefully. Understand the context of the added (+) and removed (-) lines.
2. BLOCKERS (Critical Architecture Breaches):
   - ADR-001: Flag as "blocker" if an API route (e.g., inside api/ folder) imports or queries the database directly (like `db.` or `sqlite3`) instead of passing through the `services/` layer.
   - ADR-002: Flag as "blocker" if a new API endpoint (a function handling a route) is added or modified WITHOUT the `@auth_middleware` decorator above it.
   - ADR-003 CRITICAL: Flag as "blocker" if code has `except Exception:` followed by `pass` (silent failure) or only a print statement without proper logging or re-raising. This hides critical errors and is a severe violation.
3. WARNINGS (Code Robustness Issues):
   - ADR-003 NON-CRITICAL: Flag as "warning" if an endpoint is missing try/except blocks entirely, or has generic exception handling with minimal logging but at least returns an error response.
4. SUGGESTIONS: Flag general code smells (e.g., missing pagination, bad string concatenation) that do not explicitly violate the ADRs.

GLOBAL ARCHITECTURE RULES:
{rules}

REPOSITORY ARCHITECTURE DECISION RECORDS (ADRs):
{adrs_str}

RAW PULL REQUEST DIFF TO ANALYZE:
{diff}

CHANGED FILES TO AUDIT:
{changed_files_str}

HINTS FOUND BY STATIC ANALYSIS (Use only as a guide, rely on your semantic analysis of the Diff):
ADR-002 hints:
{adr002_str}

ADR-001 hints:
{adr001_str}

ADR-003 CRITICAL hints (BLOCKERS - silent failures):
{adr003_critical_str}

ADR-003 WARNING hints (missing error handling):
{adr003_warning_str}

EXPECTED JSON SCHEMA (TypeScript notation):
type Violation = {{
  description: string; // Detailed semantic explanation of the breach
  file: string;
  line: string;
  adr_reference: string; // "ADR-001", "ADR-002", "ADR-003", or "None"
}}

GENERATE THIS JSON STRUCTURE:
Start with empty arrays. ONLY append Violation objects if you find REAL semantic violations in the diff based on the instructions above.
{{
  "blockers": [],
  "warnings": [],
  "suggestions": []
}}

IMPORTANT: JSON ONLY. Start immediately with the {{ character:"""

    return prompt


def call_llm(prompt: str, api_key: str) -> dict:
    """Llama a watsonx.ai con granite-3-8b-instruct y retorna el análisis estructurado."""
    watsonx_url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
    project_id = os.getenv("WATSONX_PROJECT_ID")
    model_id = os.getenv("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct")
    url = f"{watsonx_url}/ml/v1/text/generation?version=2023-05-29"

    if not project_id:
        raise ValueError("WATSONX_PROJECT_ID no configurado en .env")

    try:
        iam_token = _get_iam_token(api_key)
        headers = {
            "Authorization": f"Bearer {iam_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        raw = _call_api(url, headers, model_id, project_id, prompt)

        try:
            result = _extract_json(raw)
            return sanitize_and_fill_keys(result)

        except ValueError as parse_error:
            print(f"\n  Primer intento falló al parsear JSON: {parse_error}")

            retry_prompt = f"""{prompt}

[PREVIOUS INCOMPLETE RESPONSE]:
{raw}

⚠️ ERROR: Your previous response was truncated or is not valid JSON.
FIX INSTRUCTION: Please rewrite the entire JSON object correctly. Ensure all brackets, braces, and strings are fully closed.
Do NOT write any introduction or conversational text. Output valid JSON only.

JSON:"""

            iam_token = _get_iam_token(api_key)
            headers["Authorization"] = f"Bearer {iam_token}"

            print("  Reintentando con historial de mensajes incrustado...")
            raw2 = _call_api(url, headers, model_id, project_id, retry_prompt)

            try:
                result = _extract_json(raw2)
                print("  Reintento con historial exitoso.")
                return sanitize_and_fill_keys(result)
            except ValueError:
                # BUG FIX: previous fallback hardcoded "api/analytics.py" and "ADR-001",
                # injecting a phantom blocker for a file that may not exist in the PR.
                # Return safe empty structure so the local analysis (sentinel.py) can
                # still surface real violations found by static checks.
                print("  Ambos intentos fallaron. Usando fallback vacío — el análisis local cubrirá las violaciones.")
                return {"blockers": [], "warnings": [], "suggestions": []}

    except requests.exceptions.RequestException as req_error:
        print(f"  Error HTTP con watsonx.ai: {req_error}")
        return {
            "blockers": [
                {
                    "description": f"Fallo HTTP al conectar con watsonx.ai: {str(req_error)}",
                    "file": "N/A",
                    "line": "0",
                    "adr_reference": "None",
                }
            ],
            "warnings": [],
            "suggestions": [],
        }
    except Exception as e:
        print(f"  Error inesperado: {e}")
        return {
            "blockers": [
                {
                    "description": f"Error inesperado en el módulo LLM: {str(e)}",
                    "file": "N/A",
                    "line": "0",
                    "adr_reference": "None",
                }
            ],
            "warnings": [],
            "suggestions": [],
        }


def sanitize_and_fill_keys(result: dict) -> dict:
    if not isinstance(result, dict):
        result = {}
    for key in ["blockers", "warnings", "suggestions"]:
        if key not in result or not isinstance(result[key], list):
            result[key] = []
    return result


def validate_response_structure(response: dict) -> bool:
    if not isinstance(response, dict):
        return False
    required_keys = ["blockers", "warnings", "suggestions"]
    required_fields = ["description", "file", "line", "adr_reference"]
    for key in required_keys:
        if key not in response or not isinstance(response[key], list):
            return False
        for item in response[key]:
            if not isinstance(item, dict):
                return False
            if not all(f in item for f in required_fields):
                return False
    return True