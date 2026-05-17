#!/usr/bin/env python3
"""
Script de debug para ver exactamente qué recibe el LLM
"""
import os
import sys
from dotenv import load_dotenv
import github_client
import repo_analyzer
import llm_reasoner

load_dotenv()

def main():
    token = os.getenv("GITHUB_TOKEN")
    repo = "MaxTheHuman21/pr-sentinel"
    pr_number = 5
    local_path = "./demo_repo"
    
    print("=" * 80)
    print("DEBUG: Analizando qué recibe el LLM para PR #5")
    print("=" * 80)
    
    # 1. Obtener diff
    print("\n[1] Obteniendo diff...")
    diff, changed_files = github_client.get_pr_diff(repo, pr_number, token)
    print(f"Diff length: {len(diff)} caracteres")
    print(f"Changed files: {changed_files}")
    print("\n--- DIFF COMPLETO ---")
    print(diff)
    print("--- FIN DIFF ---\n")
    
    # 2. Leer ADRs
    print("\n[2] Leyendo ADRs...")
    adrs = repo_analyzer.read_adrs(local_path)
    rules = repo_analyzer.read_rules(local_path)
    print(f"ADRs encontrados: {len(adrs)}")
    for i, adr in enumerate(adrs, 1):
        print(f"  ADR {i}: {len(adr)} caracteres")
    
    # 3. Build import map
    print("\n[3] Construyendo import map...")
    files_dict = {}
    file_paths = github_client.list_python_files(repo, token)
    print(f"Archivos Python encontrados: {len(file_paths)}")
    
    # Solo cargar algunos archivos para debug
    for path in file_paths[:5]:
        try:
            content = github_client.get_repo_file(repo, path, token)
            files_dict[path] = content
            print(f"  Cargado: {path}")
        except:
            pass
    
    import_map = repo_analyzer.build_import_map(files_dict)
    print(f"Import map construido: {len(import_map)} archivos")
    
    # 4. Build prompt
    print("\n[4] Construyendo prompt para el LLM...")
    prompt = llm_reasoner.build_prompt(
        diff, adrs, rules, import_map, changed_files, files_dict
    )
    
    print(f"\nPrompt length: {len(prompt)} caracteres")
    print("\n" + "=" * 80)
    print("PROMPT COMPLETO QUE RECIBE EL LLM:")
    print("=" * 80)
    print(prompt)
    print("=" * 80)
    
    # 5. Análisis de violations desde el diff
    print("\n[5] Analizando violaciones desde el DIFF...")
    violations = llm_reasoner._analyze_diff_for_violations(diff, changed_files, files_dict)
    print(f"ADR-002 violations: {violations.get('adr002_violations', [])}")
    print(f"ADR-001 violations: {violations.get('adr001_violations', [])}")
    print(f"ADR-003 violations: {violations.get('adr003_violations', [])}")
    
    # 6. Análisis de endpoints sin auth
    print("\n[6] Buscando endpoints sin auth en el diff...")
    endpoints = llm_reasoner._find_endpoints_in_diff_without_auth(diff, changed_files)
    print(f"Endpoints sin auth encontrados: {len(endpoints)}")
    for ep in endpoints:
        print(f"  - {ep}")

if __name__ == "__main__":
    main()

# Made with Bob
