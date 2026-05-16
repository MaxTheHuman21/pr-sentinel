from datetime import datetime, UTC


def _format_severity_badge(severity: str) -> str:
    """
    Genera un badge HTML con estilo visual mejorado para la severidad.
    """
    badges = {
        "blocker": '<span style="background-color: #d73a4a; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold;">🔴 CRÍTICO</span>',
        "warning": '<span style="background-color: #fbca04; color: black; padding: 2px 8px; border-radius: 3px; font-weight: bold;">⚠️ ADVERTENCIA</span>',
        "suggestion": '<span style="background-color: #0e8a16; color: white; padding: 2px 8px; border-radius: 3px; font-weight: bold;">💡 SUGERENCIA</span>',
    }
    return badges.get(severity, severity)


def _format_finding_with_fix(item: dict, severity: str) -> str:
    """
    Formatea un finding individual con soporte para suggested_fix colapsable.
    """
    description = item.get('description', '')
    file_path = item.get('file', '')
    line = item.get('line', '')
    adr_ref = item.get('adr_reference', '')
    suggested_fix = item.get('suggested_fix', '')
    
    # Badge de severidad
    badge = _format_severity_badge(severity)
    
    # Construir la fila base
    row = f"| {badge} | {description} | `{file_path}` | {line} | {adr_ref} |"
    
    # Si hay suggested_fix, agregar detalles colapsables
    if suggested_fix:
        details = f"\n<details>\n<summary>🔧 Ver sugerencia de Fix</summary>\n\n```python\n{suggested_fix}\n```\n\n</details>\n"
        return row + details
    
    return row


def format_report(findings: dict | None) -> str:
    """
    Genera un reporte Markdown mejorado para publicar como comentario en una Pull Request.
    
    Mejoras:
    - Badges de severidad con estilo HTML visual
    - Bloques de código sugeridos en <details> colapsables
    - Mejor formato de tabla con columnas más claras
    """

    if not isinstance(findings, dict):
        return "Error: findings inválido. No se pudo generar el reporte."

    blockers = findings.get("blockers", [])
    warnings = findings.get("warnings", [])
    suggestions = findings.get("suggestions", [])

    report = []

    # HEADER
    report.append("## 🔍 PR Sentinel — Auditoría Automática")
    report.append("---")
    report.append("")

    # BLOQUEANTES
    report.append(f"### 🔴 Bloqueantes Críticos ({len(blockers)})")
    report.append("")
    if blockers:
        report.append("| Severidad | Descripción | Archivo | Línea | ADR |")
        report.append("|:---:|---|---|:---:|---|")
        for item in blockers:
            report.append(_format_finding_with_fix(item, "blocker"))
    else:
        report.append("✅ **Sin bloqueantes detectados**")
    report.append("")

    # ADVERTENCIAS
    report.append(f"### ⚠️ Advertencias ({len(warnings)})")
    report.append("")
    if warnings:
        report.append("| Severidad | Descripción | Archivo | Línea | ADR |")
        report.append("|:---:|---|---|:---:|---|")
        for item in warnings:
            report.append(_format_finding_with_fix(item, "warning"))
    else:
        report.append("✅ **Sin advertencias detectadas**")
    report.append("")

    # SUGERENCIAS
    report.append(f"### 💡 Sugerencias de Mejora ({len(suggestions)})")
    report.append("")
    if suggestions:
        report.append("| Severidad | Descripción | Archivo | Línea | ADR |")
        report.append("|:---:|---|---|:---:|---|")
        for item in suggestions:
            report.append(_format_finding_with_fix(item, "suggestion"))
    else:
        report.append("✅ **Sin sugerencias detectadas**")
    report.append("")

    # FOOTER
    report.append("---")
    timestamp = datetime.now(UTC).isoformat()
    report.append(f"*Generado por PR Sentinel vía IBM Bob | {timestamp}*")

    return "\n".join(report)