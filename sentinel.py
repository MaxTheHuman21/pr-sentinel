"""
sentinel.py — Auditor semántico de Pull Requests con análisis local de respaldo.
Si el LLM no detecta una violación, el análisis local la confirma usando el
import map y el diff (que ahora incluye cabeceras +++ b/<file> gracias al fix
en github_client.py).
"""

import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

import github_client
import repo_analyzer
import llm_reasoner
import report_formatter


def _get_diff(repo: str, pr_number: int, token: str) -> tuple:
    diff, changed_files = github_client.get_pr_diff(repo, pr_number, token)
    return diff if diff else "", changed_files if changed_files else []


def _get_repo_files(repo: str, token: str) -> dict:
    file_paths = github_client.list_python_files(repo, token)
    files_dict = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(github_client.get_repo_file, repo, p, token): p
            for p in file_paths
        }
        for future in as_completed(futures):
            path = futures[future]
            content = future.result()
            if content:
                files_dict[path] = content
    return files_dict


def _read_adrs_and_rules(local_path: str) -> tuple:
    adrs = repo_analyzer.read_adrs(local_path)
    rules = repo_analyzer.read_rules(local_path)
    return adrs, rules


def _build_import_map(files_dict: dict) -> dict:
    return repo_analyzer.build_import_map(files_dict)


def _reason_with_llm(
    diff, adrs, rules, import_map, changed_files, api_key, files_dict
) -> dict:
    prompt = llm_reasoner.build_prompt(
        diff, adrs, rules, import_map, changed_files, files_dict
    )
    return llm_reasoner.call_llm(prompt, api_key)


def _local_adr_analysis(diff: str, import_map: dict, changed_files: list) -> tuple:
    """
    Análisis local de violaciones ADR usando el nuevo análisis de diff.
    
    Este análisis actúa como respaldo cuando el LLM falla.
    Usa _analyze_diff_for_violations de llm_reasoner para consistencia.
    """
    import llm_reasoner
    
    # Usar el análisis de diff que ya implementamos
    violations = llm_reasoner._analyze_diff_for_violations(diff, changed_files, {})
    
    blockers = []
    warnings = []
    
    # ADR-002: Auth middleware (BLOCKER)
    for filename in violations.get("adr002_violations", []):
        blockers.append({
            "description": (
                f"{filename} expone endpoints sin el decorador obligatorio "
                "@auth_middleware. Violación crítica de ADR-002."
            ),
            "file": filename,
            "line": "0",
            "adr_reference": "ADR-002",
        })
    
    # ADR-001: DB directo (BLOCKER)
    for filename in violations.get("adr001_violations", []):
        blockers.append({
            "description": (
                f"{filename} importa directamente la capa de datos (db/) "
                "infringiendo ADR-001. Debe usar services/."
            ),
            "file": filename,
            "line": "0",
            "adr_reference": "ADR-001",
        })
    
    # ADR-003 CRITICAL: except Exception: pass (BLOCKER)
    for filename in violations.get("adr003_critical_violations", []):
        blockers.append({
            "description": (
                f"{filename} usa 'except Exception: pass' silenciando errores críticos. "
                "Violación grave de ADR-003."
            ),
            "file": filename,
            "line": "0",
            "adr_reference": "ADR-003",
        })
    
    # ADR-003 WARNING: missing try/except (WARNING)
    for filename in violations.get("adr003_warnings", []):
        warnings.append({
            "description": (
                f"{filename} no incluye manejo de errores apropiado. "
                "Debe implementar try/except según ADR-003."
            ),
            "file": filename,
            "line": "0",
            "adr_reference": "ADR-003",
        })
    
    return blockers, warnings


def _local_adr_analysis_OLD(diff: str, import_map: dict, changed_files: list) -> tuple:
    """
    DEPRECATED: Análisis local antiguo de violaciones ADR.
    Mantenido por si se necesita revertir.
    """
    blockers = []
    warnings = []

    # Identify API files touched in this PR
    api_files_in_pr = {
        f for f in changed_files if "api/" in f or "api\\" in f
    }

    if not api_files_in_pr:
        return blockers, warnings

    # Collect diff lines per file using the "+++ b/<file>" headers added by
    # the fixed github_client.get_pr_diff().
    diff_lines = diff.splitlines()
    current_file = None
    file_diff_lines: dict = {f: [] for f in api_files_in_pr}

    for line in diff_lines:
        if line.startswith("+++ b/"):
            current_file = line.replace("+++ b/", "").strip()
        elif current_file in api_files_in_pr:
            file_diff_lines[current_file].append(line)

    for filename in api_files_in_pr:
        lines = file_diff_lines[filename]

        # --- ADR-002 ---
        auth_removed = any(
            line.startswith("-") and ("auth_middleware" in line or "@auth" in line)
            for line in lines
        )

        file_imports = import_map.get(filename, [])
        imports_auth = any(
            "auth_middleware" in imp or "middleware" in imp for imp in file_imports
        )
        has_decorator_added = any(
            line.startswith("+") and "@auth_middleware" in line for line in lines
        )
        # New endpoint functions explicitly added in this PR
        new_endpoint_defs = [
            line for line in lines
            if line.startswith("+") and line.lstrip("+").lstrip().startswith("def ")
        ]

        if auth_removed or (
            new_endpoint_defs and not imports_auth and not has_decorator_added
        ):
            blockers.append(
                {
                    "description": (
                        f"{filename} expone o modifica endpoints sin el decorador "
                        "obligatorio @auth_middleware. Violación crítica de ADR-002."
                    ),
                    "file": filename,
                    "line": "0",
                    "adr_reference": "ADR-002",
                }
            )

        # --- ADR-001 ---
        imports_db_directly = any(
            "db" in imp and "service" not in imp for imp in file_imports
        )
        if imports_db_directly:
            warnings.append(
                {
                    "description": (
                        f"{filename} importa directamente la capa de datos (db/) "
                        "infringiendo ADR-001. Debe usar services/."
                    ),
                    "file": filename,
                    "line": "0",
                    "adr_reference": "ADR-001",
                }
            )

        # --- ADR-003 ---
        # BUG FIX: only warn when a *new* def is added in this PR AND no try
        # block is added nearby (within 20 lines after the def). This avoids
        # flagging existing endpoints whose try blocks weren't changed.
        if new_endpoint_defs:
            for i, def_line in enumerate(lines):
                if not (def_line.startswith("+") and def_line.lstrip("+").lstrip().startswith("def ")):
                    continue
                # Look for a try: block within the next 20 added/context lines
                window = lines[i + 1 : i + 20]
                has_try_nearby = any(
                    l.startswith("+") and "try:" in l for l in window
                )
                if not has_try_nearby:
                    warnings.append(
                        {
                            "description": (
                                f"La nueva función en {filename} no incluye un bloque "
                                "try/except. Es obligatorio retornar errores JSON homogéneos "
                                "según ADR-003."
                            ),
                            "file": filename,
                            "line": "0",
                            "adr_reference": "ADR-003",
                        }
                    )
                    break  # one warning per file is enough

    return blockers, warnings


def _merge_findings(
    llm_findings: dict, local_blockers: list, local_warnings: list
) -> dict:
    """
    Combina hallazgos del LLM con los del análisis local.
    Prioriza los hallazgos del LLM (más detallados) y solo agrega
    hallazgos locales si el LLM no detectó esa violación en ese archivo.
    
    Deduplicación inteligente:
    - Extrae el ADR de la descripción si no está en adr_reference
    - Si el LLM detectó un ADR en un archivo, no agregar violaciones locales del mismo ADR+archivo
    """
    final_blockers = list(llm_findings.get("blockers", []))
    final_warnings = list(llm_findings.get("warnings", []))
    final_suggestions = list(llm_findings.get("suggestions", []))

    def extract_adr(item):
        """Extrae el ADR del adr_reference o de la descripción"""
        adr = item.get("adr_reference", "").strip()
        if adr:
            return adr
        # Intentar extraer de la descripción
        desc = item.get("description", "")
        if "ADR-001" in desc:
            return "ADR-001"
        elif "ADR-002" in desc:
            return "ADR-002"
        elif "ADR-003" in desc:
            return "ADR-003"
        return "UNKNOWN"

    # Crear conjuntos de (ADR, archivo) ya detectados por el LLM
    llm_blocker_keys = set()
    for b in final_blockers:
        adr = extract_adr(b)
        file = b.get("file", "").strip()
        llm_blocker_keys.add((adr, file))
    
    # Solo agregar blockers locales si el LLM NO detectó ese (ADR, archivo)
    for blocker in local_blockers:
        adr = extract_adr(blocker)
        file = blocker.get("file", "").strip()
        key = (adr, file)
        
        if key not in llm_blocker_keys:
            final_blockers.append(blocker)
            llm_blocker_keys.add(key)  # Evitar duplicados entre locales

    # Mismo proceso para warnings
    llm_warning_keys = set()
    for w in final_warnings:
        adr = extract_adr(w)
        file = w.get("file", "").strip()
        llm_warning_keys.add((adr, file))
    
    for warning in local_warnings:
        adr = extract_adr(warning)
        file = warning.get("file", "").strip()
        key = (adr, file)
        
        if key not in llm_warning_keys:
            final_warnings.append(warning)
            llm_warning_keys.add(key)

    return {
        "blockers": final_blockers,
        "warnings": final_warnings,
        "suggestions": final_suggestions,
    }


def _format_and_post(
    findings: dict, repo: str, pr_number: int, token: str
) -> bool:
    report = report_formatter.format_report(findings)
    return github_client.post_pr_comment(repo, pr_number, report, token)


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="PR Sentinel — Auditor Semántico de Pull Requests"
    )
    parser.add_argument("--repo", required=True, help="Repositorio en formato owner/repo")
    parser.add_argument(
        "--pr", required=True, type=int, help="Número de la Pull Request a auditar"
    )
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN")
    api_key = os.getenv("WATSONX_API_KEY")
    local_path = os.getenv("REPO_LOCAL_PATH", "./demo_repo")

    if not token:
        print("Error: GITHUB_TOKEN no configurado en .env")
        sys.exit(1)
    if not api_key:
        print("Error: WATSONX_API_KEY no configurado en .env")
        sys.exit(1)

    print(f"\nPR Sentinel — Analizando PR #{args.pr} en {args.repo}\n")

    try:
        print(f"[1/5] Obteniendo diff de PR #{args.pr}... ", end="", flush=True)
        diff, changed_files = _get_diff(args.repo, args.pr, token)
        print(f"OK ({len(diff.splitlines())} líneas, {len(changed_files)} archivos)")

        print("[2/5] Leyendo ADRs y reglas del repo... ", end="", flush=True)
        adrs, rules = _read_adrs_and_rules(local_path)
        files_dict = _get_repo_files(args.repo, token)
        print(f"OK ({len(adrs)} ADRs encontrados)")

        print("[3/5] Analizando imports del repo... ", end="", flush=True)
        import_map = _build_import_map(files_dict)
        print(f"OK ({len(import_map)} módulos mapeados)")

        print("[4/5] Razonando con WATSONX + análisis local... ", end="", flush=True)
        llm_findings = _reason_with_llm(
            diff, adrs, rules, import_map, changed_files, api_key, files_dict
        )
        local_blockers, local_warnings = _local_adr_analysis(
            diff, import_map, changed_files
        )
        findings = _merge_findings(llm_findings, local_blockers, local_warnings)
        print("OK")

        print(f"[5/5] Publicando comentario en PR #{args.pr}... ", end="", flush=True)
        success = _format_and_post(findings, args.repo, args.pr, token)
        print("OK" if success else "ADVERTENCIA — no se pudo publicar")

        n_b = len(findings.get("blockers", []))
        n_w = len(findings.get("warnings", []))
        n_s = len(findings.get("suggestions", []))
        print(f"\n-> {n_b} bloqueante(s), {n_w} advertencia(s), {n_s} sugerencia(s)\n")

        adr_002_violations = [
            b for b in findings.get("blockers", [])
            if b.get("adr_reference") == "ADR-002"
        ]

        api_files_in_pr = [
            f for f in changed_files if f.startswith("api/") or "/api/" in f
        ]

        if adr_002_violations:
            print(
                f"CHECKPOINT: {len(adr_002_violations)} violación(es) ADR-002 detectada(s)."
            )
        elif api_files_in_pr:
            print(
                f"CHECKPOINT: Sin violaciones ADR-002 en {len(api_files_in_pr)} archivo(s) API."
            )
        else:
            print("CHECKPOINT: No hay archivos API en este PR.")

    except KeyboardInterrupt:
        print("\nInterrumpido.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        print("Revisa tu .env y que todos los módulos estén correctamente integrados.")
        sys.exit(1)


if __name__ == "__main__":
    main()