import ast
from pathlib import Path


def read_adrs(local_path: str) -> list[str]:
    """
    Lee todos los archivos ADR (.md) dentro de docs/adr/
    """
    adr_path = Path(local_path) / "docs" / "adr"

    if not adr_path.exists():
        return []

    adrs = []

    for file in adr_path.glob("*.md"):
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

    architecture_file = root_path / "ARCHITECTURE.md"
    claude_file = root_path / "CLAUDE.md"

    if architecture_file.exists():
        return architecture_file.read_text(encoding="utf-8")

    if claude_file.exists():
        return claude_file.read_text(encoding="utf-8")

    return ""


def extract_imports(source_code: str) -> list[str]:
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


def build_import_map(files_dict: dict[str, str]) -> dict[str, list[str]]:
    """
    Construye un mapa de imports por archivo.
    """
    import_map = {}

    for filename, source_code in files_dict.items():
        import_map[filename] = extract_imports(source_code)

    return import_map