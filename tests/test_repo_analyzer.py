from repo_analyzer import read_adrs, read_rules, extract_imports, build_import_map


def test_extract_imports():
    code = """
import os
import requests
from pathlib import Path
from middleware.auth_middleware import auth_middleware
"""

    imports = extract_imports(code)

    assert "os" in imports
    assert "requests" in imports
    assert "pathlib" in imports
    assert "middleware.auth_middleware" in imports


def test_extract_imports_with_invalid_code():
    code = "def esto_no_es_valido(:"

    imports = extract_imports(code)

    assert imports == []


def test_build_import_map():
    files = {
        "api/orders.py": "from middleware.auth_middleware import auth_middleware",
        "api/users.py": "from services.user_service import create_user",
    }

    result = build_import_map(files)

    assert "api/orders.py" in result
    assert "api/users.py" in result
    assert "middleware.auth_middleware" in result["api/orders.py"]
    assert "services.user_service" in result["api/users.py"]


def test_read_adrs(tmp_path):
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)

    adr_file = adr_dir / "ADR-002-autenticacion-obligatoria.md"
    adr_file.write_text("Todos los endpoints deben usar auth_middleware", encoding="utf-8")

    result = read_adrs(str(tmp_path))

    assert len(result) == 1
    assert "auth_middleware" in result[0]


def test_read_rules_architecture(tmp_path):
    architecture_file = tmp_path / "ARCHITECTURE.md"
    architecture_file.write_text("Reglas de arquitectura del proyecto", encoding="utf-8")

    result = read_rules(str(tmp_path))

    assert "Reglas de arquitectura" in result