from report_formatter import format_report


def test_format_report_with_blockers():
    findings = {
        "blockers": [
            {
                "description": "El endpoint POST /users no usa @auth_middleware",
                "file": "api/users.py",
                "line": "14",
                "adr_reference": "ADR-002",
            }
        ],
        "warnings": [],
        "suggestions": [],
    }

    result = format_report(findings)

    assert "PR Sentinel" in result
    assert "Bloqueantes" in result
    assert "api/users.py" in result
    assert "ADR-002" in result


def test_format_report_empty():
    findings = {
        "blockers": [],
        "warnings": [],
        "suggestions": [],
    }

    result = format_report(findings)

    assert "Sin bloqueantes detectados" in result
    assert "Sin advertencias detectadas" in result
    assert "Sin sugerencias detectadas" in result


def test_format_report_invalid_findings():
    result = format_report(None)

    assert "Error" in result