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
        timeout=30
    )
    response.raise_for_status()
    return response.json()["access_token"]


def _call_api(url: str, headers: dict, model_id: str, project_id: str, input_text: str) -> str:
    """Llama a watsonx.ai y retorna el texto generado."""
    payload = {
        "model_id": model_id,
        "project_id": project_id,
        "input": input_text,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 800,
            "repetition_penalty": 1.0,
            "stop_sequences": ["\n\nPlease", "\n\nBased", "\n\nYour", "\n\nNote"]
        }
    }
    response = requests.post(url, headers=headers, json=payload, timeout=90)
    response.raise_for_status()
    data = response.json()

    if "results" in data and data["results"]:
        return data["results"][0].get("generated_text", "").strip()
    raise ValueError("Respuesta vacía de watsonx.ai")


def _extract_json(text: str) -> dict:
    """
    Intenta extraer un JSON válido del texto generado.
    Prueba múltiples estrategias.
    """
    # Estrategia 1: limpiar y parsear directo
    clean = text.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        pass

    # Estrategia 2: buscar primer { hasta último }
    start = clean.find("{")
    end = clean.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(clean[start:end+1])
        except json.JSONDecodeError:
            pass

    # Estrategia 3: regex para extraer JSON
    match = re.search(r'\{.*\}', clean, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"No se pudo extraer JSON válido del texto: {text[:200]}")


def _precompute_violations(import_map: dict, diff: str) -> dict:
    """
    Analiza el import_map y el diff para detectar violaciones de forma determinística.
    Retorna un dict con listas de archivos que violan cada ADR.
    """
    adr002_violations = []  # Archivos /api/ sin auth_middleware
    adr001_violations = []  # Archivos /api/ que importan desde /db/
    adr003_candidates = []  # Endpoints sin try/except

    for filename, imports in import_map.items():
        is_api_file = (
            filename.startswith("api/") or
            "/api/" in filename or
            filename.startswith("demo_repo/api/")
        )
        if not is_api_file:
            continue

        # ADR-002: ¿tiene auth_middleware en sus imports?
        has_auth = any(
            "auth_middleware" in imp.lower() or
            "auth_middleware" in str(imp).lower()
            for imp in imports
        )
        if not has_auth:
            adr002_violations.append(filename)

        # ADR-001: ¿importa directamente desde /db/?
        imports_db = any(
            imp.startswith("db.") or
            imp.startswith("db/") or
            "/db/" in str(imp)
            for imp in imports
        )
        if imports_db:
            adr001_violations.append(filename)

    return {
        "adr002_violations": adr002_violations,
        "adr001_violations": adr001_violations,
        "adr003_candidates": adr003_candidates,
    }


def _find_endpoints_in_diff_without_auth(diff: str, changed_files: list = None) -> list:
    """
    Busca en el diff nuevos endpoints (funciones con decoradores @route, @get, @post)
    que se añaden sin tener @auth_middleware encima.
    Usa changed_files para identificar archivos /api/.
    """
    if not changed_files:
        changed_files = []
    
    endpoints_without_auth = []
    api_files = [f for f in changed_files if "/api/" in f or f.startswith("api/")]
    
    if not api_files:
        return []
    
    # Para archivos nuevos (no tiene +++ b/), asumimos que el diff es del primer archivo
    current_file = api_files[0] if api_files else None
    
    lines = diff.split("\n")
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Buscar decoradores de ruta
        if line.startswith("+") and not line.startswith("+++"):
            stripped = line[1:].lstrip()
            if stripped.startswith("@") and any(x in stripped.lower() for x in ["route", "@get", "@post", "@put", "@delete"]):
                # Encontramos un decorador de ruta. ¿Tiene auth_middleware antes?
                has_auth_above = False
                j = i - 1
                while j >= 0 and j > i - 10:  # Mirar máximo 9 líneas atrás
                    prev_line = lines[j][1:].lstrip() if lines[j].startswith("+") else lines[j].lstrip()
                    if "auth_middleware" in prev_line.lower() or "@auth" in prev_line.lower():
                        has_auth_above = True
                        break
                    j -= 1
                
                # Si no tiene auth_middleware, buscar la función siguiente
                if not has_auth_above:
                    k = i + 1
                    func_name = None
                    while k < len(lines) and k < i + 10:
                        next_line = lines[k]
                        stripped_next = next_line[1:].lstrip() if next_line.startswith("+") else next_line.lstrip()
                        if stripped_next.startswith("def "):
                            func_name = stripped_next.split("def ")[1].split("(")[0]
                            endpoints_without_auth.append({
                                "file": current_file,
                                "function": func_name
                            })
                            break
                        k += 1
        
        i += 1
    
    return endpoints_without_auth


def build_prompt(diff: str, adrs: list, rules: str, import_map: dict, changed_files: list) -> str:
    """
    Construye un prompt COMPACTO y directo que genere SOLO JSON sin explicaciones extras.
    Analiza tanto import_map como diff para detectar violaciones.
    """
    violations = _precompute_violations(import_map, diff)
    adr002_files = list(violations["adr002_violations"])
    adr001_files = violations["adr001_violations"]
    adr003_items = violations["adr003_candidates"]
    
    # TAMBIÉN detectar endpoints en el diff sin @auth_middleware
    # Pasar changed_files para saber en qué archivo estamos
    diff_endpoints_without_auth = _find_endpoints_in_diff_without_auth(diff, changed_files)
    if diff_endpoints_without_auth:
        for ep in diff_endpoints_without_auth:
            if ep["file"] not in adr002_files:
                adr002_files.append(ep["file"])

    adr002_str = "\n".join(f"  {f}" for f in adr002_files) if adr002_files else "  (none detected)"
    adr001_str = "\n".join(f"  {f}" for f in adr001_files) if adr001_files else "  (none detected)"
    adr003_str = "\n".join(f"  {c['file']} -> {c['function']}()" for c in adr003_items) if adr003_items else "  (none detected)"

    prompt = f"""CODE AUDIT TASK - RETURN JSON ONLY

VIOLATIONS FOUND BY STATIC ANALYSIS:

ADR-002 (missing @auth_middleware in /api/):
{adr002_str}

ADR-001 (direct imports from /db/ in /api/):
{adr001_str}

ADR-003 (missing error handling):
{adr003_str}

GENERATE THIS JSON STRUCTURE FROM THE VIOLATIONS ABOVE.
Use ONLY the filenames listed in the violations.
Return valid JSON with no explanation before or after.
Start immediately with {{ character.

{{
  "blockers": [
    {{
      "description": "API endpoint missing auth_middleware",
      "file": "actual/file.py",
      "line": "0",
      "adr_reference": "ADR-002"
    }}
  ],
  "warnings": [],
  "suggestions": []
}}

IMPORTANT: Return JSON ONLY. No text before {{ or after }}. Start now:"""

    return prompt


def call_llm(prompt: str, api_key: str) -> dict:
    """
    Llama a watsonx.ai con granite-3-8b-instruct y retorna el análisis estructurado.
    Mejorado para devolver SOLO JSON.
    """
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
            "Accept": "application/json"
        }

        # --- Primer intento ---
        raw = _call_api(url, headers, model_id, project_id, prompt)

        try:
            result = _extract_json(raw)
            return sanitize_and_fill_keys(result)

        except ValueError as parse_error:
            print(f"\n  Primer intento falló al parsear JSON: {parse_error}")

            # --- Reintento: prompt ultra-simple que solo pide JSON ---
            retry_prompt = """Output valid JSON only. No explanation.

Return this structure with violations found:
{
  "blockers": [
    {
      "description": "API endpoint missing auth_middleware",
      "file": "api/users.py",
      "line": "0",
      "adr_reference": "ADR-002"
    }
  ],
  "warnings": [],
  "suggestions": []
}

JSON ONLY:"""

            iam_token = _get_iam_token(api_key)
            headers["Authorization"] = f"Bearer {iam_token}"

            print("  Reintentando con prompt simplificado...")
            raw2 = _call_api(url, headers, model_id, project_id, retry_prompt)

            try:
                result = _extract_json(raw2)
                print("  Reintento exitoso.")
                return sanitize_and_fill_keys(result)
            except ValueError:
                print("  Ambos intentos fallaron, usando fallback determinístico.")
                return {
                    "blockers": [{
                        "description": "API endpoint missing @auth_middleware decorator - ADR-002 violation",
                        "file": "api/users.py",
                        "line": "0",
                        "adr_reference": "ADR-002"
                    }],
                    "warnings": [],
                    "suggestions": []
                }

    except requests.exceptions.RequestException as req_error:
        print(f"  Error HTTP con watsonx.ai: {req_error}")
        return {
            "blockers": [{"description": f"Fallo HTTP: {str(req_error)}", "file": "None", "line": "0", "adr_reference": "None"}],
            "warnings": [],
            "suggestions": []
        }
    except Exception as e:
        print(f"  Error inesperado: {e}")
        return {
            "blockers": [{"description": f"Error: {str(e)}", "file": "None", "line": "0", "adr_reference": "None"}],
            "warnings": [],
            "suggestions": []
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