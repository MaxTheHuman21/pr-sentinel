"""
repo_analyzer.py — Lee ADRs, reglas de arquitectura y construye el mapa de imports.
"""

import ast
from pathlib import Path


def read_adrs(local_path: str) -> list:
    """
    Lee todos los archivos ADR (.md) dentro de docs/adr/
    """
    adr_path = Path(local_path) / "docs" / "adr"

    if not adr_path.exists():
        return []

    adrs = []
    for file in sorted(adr_path.glob("*.md")):
        try:
            adrs.append(file.read_text(encoding="utf-8"))
        except Exception:
            continue

    return adrs


def read_rules(local_path: str) -> str:
    """
    Lee ARCHITECTURE.md o CLAUDE.md desde la raíz del repositorio.
    """
    root_path = Path(local_path)

    for candidate in ("ARCHITECTURE.md", "CLAUDE.md"):
        target = root_path / candidate
        if target.exists():
            return target.read_text(encoding="utf-8")

    return ""


def extract_imports(source_code: str) -> list:
    """
    Extrae imports de un código Python usando AST.
    """
    imports = []

    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return imports


def build_import_map(files_dict: dict) -> dict:
    """
    Construye un mapa { filename: [import, ...] } para todos los archivos del repo.
    """
    import_map = {}
    for filename, source_code in files_dict.items():
        import_map[filename] = extract_imports(source_code)
    return import_map