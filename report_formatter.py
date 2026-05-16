from datetime import datetime, UTC

def format_report(findings: dict | None) -> str:    
    """
    Genera un reporte Markdown para publicar como comentario en una Pull Request.
    """

    if not isinstance(findings, dict):
        return "Error: findings inválido. No se pudo generar el reporte."

    blockers = findings.get("blockers", [])
    warnings = findings.get("warnings", [])
    suggestions = findings.get("suggestions", [])

    report = []

    # HEADER [cite: 137]
    report.append("## 🔍 PR Sentinel — Auditoría Automática")
    report.append("---")
    report.append("")

    # BLOQUEANTES [cite: 138, 139]
    report.append(f"### 🔴 Bloqueantes ({len(blockers)})")
    if blockers:
        report.append("| Descripción | Archivo | Línea | ADR |")
        report.append("|---|---|---|---|")
        for item in blockers:
            report.append(
                f"| {item.get('description', '')} | "
                f"{item.get('file', '')} | "
                f"{item.get('line', '')} | "
                f"{item.get('adr_reference', '')} |"
            )
    else:
        report.append("✅ Sin bloqueantes detectados")
    report.append("")

    # ADVERTENCIAS [cite: 139]
    report.append(f"### 🟡 Advertencias ({len(warnings)})")
    if warnings:
        report.append("| Descripción | Archivo | Línea | ADR |")
        report.append("|---|---|---|---|")
        for item in warnings:
            report.append(
                f"| {item.get('description', '')} | "
                f"{item.get('file', '')} | "
                f"{item.get('line', '')} | "
                f"{item.get('adr_reference', '')} |"
            )
    else:
        report.append("✅ Sin advertencias detectadas")
    report.append("")

    # SUGERENCIAS [cite: 139]
    report.append(f"### 🟢 Sugerencias ({len(suggestions)})")
    if suggestions:
        report.append("| Descripción | Archivo | Línea | ADR |")
        report.append("|---|---|---|---|")
        for item in suggestions:
            report.append(
                f"| {item.get('description', '')} | "
                f"{item.get('file', '')} | "
                f"{item.get('line', '')} | "
                f"{item.get('adr_reference', '')} |"
            )
    else:
        report.append("✅ Sin sugerencias detectadas")
    report.append("")

    # FOOTER [cite: 140]
    report.append("---")
    timestamp = datetime.now(UTC).isoformat()
    report.append(f"Generado por PR Sentinel vía IBM Bob | {timestamp}")

    return "\n".join(report)