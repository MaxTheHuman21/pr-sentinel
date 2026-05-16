#!/usr/bin/env python3
"""
Test script para verificar las mejoras en report_formatter.py
"""

from report_formatter import format_report

# Test 1: Findings con suggested_fix
print("=" * 80)
print("TEST 1: Findings con suggested_fix colapsable")
print("=" * 80)

findings_with_fix = {
    "blockers": [
        {
            "description": "El endpoint POST /users no usa @auth_middleware",
            "file": "api/users.py",
            "line": "14",
            "adr_reference": "ADR-002",
            "suggested_fix": "@auth_middleware\n@app.post('/users')\ndef create_user(user_data: dict):\n    return user_service.create(user_data)"
        }
    ],
    "warnings": [
        {
            "description": "Importación directa desde /db/ viola la arquitectura modular",
            "file": "api/products.py",
            "line": "5",
            "adr_reference": "ADR-001",
            "suggested_fix": "# Cambiar:\nfrom db.database import get_connection\n\n# Por:\nfrom services.product_service import get_products"
        }
    ],
    "suggestions": [
        {
            "description": "Considerar agregar logging para mejor trazabilidad",
            "file": "services/order_service.py",
            "line": "23",
            "adr_reference": "ADR-003"
        }
    ]
}

result = format_report(findings_with_fix)
print(result)
print("\n")

# Test 2: Findings sin suggested_fix (backward compatibility)
print("=" * 80)
print("TEST 2: Findings sin suggested_fix (compatibilidad)")
print("=" * 80)

findings_without_fix = {
    "blockers": [
        {
            "description": "El endpoint POST /orders no usa @auth_middleware",
            "file": "api/orders.py",
            "line": "20",
            "adr_reference": "ADR-002"
        }
    ],
    "warnings": [],
    "suggestions": []
}

result2 = format_report(findings_without_fix)
print(result2)
print("\n")

# Test 3: Sin findings
print("=" * 80)
print("TEST 3: Sin findings detectados")
print("=" * 80)

findings_empty = {
    "blockers": [],
    "warnings": [],
    "suggestions": []
}

result3 = format_report(findings_empty)
print(result3)
print("\n")

print("=" * 80)
print("✅ TODOS LOS TESTS COMPLETADOS")
print("=" * 80)

# Made with Bob
