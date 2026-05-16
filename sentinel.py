"""
sentinel.py — FASE 3
Úsalo cuando P4 haya mergeado feature/repo-analyzer a dev.
github_client y repo_analyzer son REALES. llm_reasoner y report_formatter siguen en stub.
"""

import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

import github_client   
import repo_analyzer   


def _get_diff(repo: str, pr_number: int, token: str) -> str:
    """REAL: obtiene el diff desde GitHub API."""
    diff = github_client.get_pr_diff(repo, pr_number, token)
    return diff if diff else ""


def _get_repo_files(repo: str, token: str) -> dict:
    """REAL: obtiene todos los archivos .py en paralelo con ThreadPoolExecutor."""
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
    """REAL: lee los ADRs y reglas del repositorio local."""
    adrs = repo_analyzer.read_adrs(local_path)
    rules = repo_analyzer.read_rules(local_path)
    return adrs, rules


def _build_import_map(files_dict: dict) -> dict:
    """REAL: mapea imports entre archivos .py usando ast."""
    return repo_analyzer.build_import_map(files_dict)


def _reason_with_llm(diff, adrs, rules, import_map, changed_files, api_key) -> dict:
    """STUB: llm_reasoner aún no está listo."""
    return {
        "blockers": [{
            "description": "El endpoint POST /users no usa @auth_middleware",
            "file": "api/users.py",
            "line": "14",
            "adr_reference": "ADR-002"
        }],
        "warnings": [],
        "suggestions": [{
            "description": "Agregar bloque try/except al endpoint",
            "file": "api/users.py",
            "line": "14",
            "adr_reference": "ADR-003"
        }]
    }


def _format_and_post(findings: dict, repo: str, pr_number: int, token: str) -> bool:
    """STUB: report_formatter aún no está listo. Publica texto plano en GitHub."""
    blockers = findings.get("blockers", [])
    warnings = findings.get("warnings", [])
    suggestions = findings.get("suggestions", [])

    lines = ["##  PR Sentinel — Reporte (stub formatter)\n"]
    lines.append(f"** Bloqueantes: {len(blockers)}**")
    for b in blockers:
        lines.append(f"- {b.get('description')} — `{b.get('file')}` ({b.get('adr_reference')})")
    lines.append(f"\n** Advertencias: {len(warnings)}**")
    lines.append(f"\n** Sugerencias: {len(suggestions)}**")
    for s in suggestions:
        lines.append(f"- {s.get('description')} — `{s.get('file')}` ({s.get('adr_reference')})")
    lines.append("\n---\n_Generado por PR Sentinel (stub formatter)_")

    body = "\n".join(lines)
    return github_client.post_pr_comment(repo, pr_number, body, token)


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="PR Sentinel — Fase 3 (github_client + repo_analyzer reales)")
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--pr", required=True, type=int, help="Número de PR")
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN")
    api_key = os.getenv("LLM_API_KEY", "stub-key")
    local_path = os.getenv("REPO_LOCAL_PATH", "./demo_repo")

    if not token:
        print(" Error: GITHUB_TOKEN no configurado en .env")
        sys.exit(1)

    print(f"\n  PR Sentinel FASE 3 — PR #{args.pr} en {args.repo}\n")

    try:
        print(f"[1/5] Obteniendo diff de PR #{args.pr}... ", end="", flush=True)
        diff = _get_diff(args.repo, args.pr, token)
        changed_files = [l.split(" b/")[-1] for l in diff.splitlines() if l.startswith("+++ b/")]
        print(f"OK ({len(diff.splitlines())} líneas modificadas)")

        print("[2/5] Leyendo ADRs y reglas del repo... ", end="", flush=True)
        adrs, rules = _read_adrs_and_rules(local_path)
        files_dict = _get_repo_files(args.repo, token)
        print(f"OK ({len(adrs)} ADRs encontrados)")

        print("[3/5] Analizando imports del repo... ", end="", flush=True)
        import_map = _build_import_map(files_dict)
        print(f"OK ({len(import_map)} módulos mapeados)")

        print("[4/5] Razonando con LLM... ", end="", flush=True)
        findings = _reason_with_llm(diff, adrs, rules, import_map, changed_files, api_key)
        print("OK")

        print(f"[5/5] Publicando comentario en PR #{args.pr}... ", end="", flush=True)
        success = _format_and_post(findings, args.repo, args.pr, token)
        print("OK" if success else "ADVERTENCIA — no se pudo publicar")

        n_b = len(findings.get("blockers", []))
        n_w = len(findings.get("warnings", []))
        n_s = len(findings.get("suggestions", []))
        print(f"\n-> Comentario publicado: {n_b} bloqueantes, {n_w} advertencias, {n_s} sugerencias\n")

        adr_002 = any(b.get("adr_reference") == "ADR-002" for b in findings.get("blockers", []))
        print(" CHECKPOINT ADR-002: detectado." if adr_002 else "⚠️  CHECKPOINT ADR-002: NO detectado.")

    except KeyboardInterrupt:
        print("\nInterrumpido.")
        sys.exit(0)
    except Exception as e:
        print(f"\n Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()