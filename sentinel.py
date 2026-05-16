
import argparse
import os
import sys
from dotenv import load_dotenv


def _get_diff(repo: str, pr_number: int, token: str) -> str:
    """STUB: retorna un diff simulado con la violación ADR-002."""
    return (
        "+++ b/api/users.py\n"
        "+def create_user():\n"
        "+    pass  # Sin @auth_middleware — violación ADR-002\n"
    )


def _get_repo_files(repo: str, token: str) -> dict:
    """STUB: retorna diccionario vacío."""
    return {}


def _read_adrs_and_rules(local_path: str) -> tuple:
    """STUB: retorna ADRs simulados."""
    adrs = [
        "ADR-001: Separar en capas /api, /services, /db.",
        "ADR-002: TODOS los endpoints de /api deben usar @auth_middleware.",
        "ADR-003: Todos los endpoints deben usar try/except y retornar JSON.",
    ]
    return adrs, "Reglas generales del repositorio (stub)."


def _build_import_map(files_dict: dict) -> dict:
    """STUB: retorna mapa vacío."""
    return {}


def _reason_with_llm(diff, adrs, rules, import_map, changed_files, api_key) -> dict:
    """STUB: retorna hallazgos simulados con el bloqueante ADR-002."""
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
    """STUB: imprime el reporte en consola en lugar de publicar en GitHub."""
    blockers = findings.get("blockers", [])
    warnings = findings.get("warnings", [])
    suggestions = findings.get("suggestions", [])
    print("\n  [STUB] Reporte que se publicaría en GitHub:")
    print("  -----------------------------------------")
    print(f"   Bloqueantes: {len(blockers)}")
    for b in blockers:
        print(f"     - {b.get('description')} ({b.get('adr_reference')})")
    print(f"   Advertencias: {len(warnings)}")
    print(f"   Sugerencias: {len(suggestions)}")
    print("  -----------------------------------------")
    return True


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="PR Sentinel — Fase 1 (stubs)")
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--pr", required=True, type=int, help="Número de PR")
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN", "stub-token")
    api_key = os.getenv("LLM_API_KEY", "stub-key")
    local_path = os.getenv("REPO_LOCAL_PATH", "./demo_repo")

    print(f"\n  PR Sentinel FASE 1 (stubs) — PR #{args.pr} en {args.repo}\n")

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
        print("OK")

        n_b = len(findings.get("blockers", []))
        n_w = len(findings.get("warnings", []))
        n_s = len(findings.get("suggestions", []))
        print(f"\n-> Reporte generado (stub): {n_b} bloqueantes, {n_w} advertencias, {n_s} sugerencias\n")

        adr_002 = any(b.get("adr_reference") == "ADR-002" for b in findings.get("blockers", []))
        if adr_002:
            print(" CHECKPOINT: Bloqueante ADR-002 detectado correctamente.")
        else:
            print("  CHECKPOINT: ADR-002 NO detectado.")

    except KeyboardInterrupt:
        print("\nInterrumpido.")
        sys.exit(0)
    except Exception as e:
        print(f"\n Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()