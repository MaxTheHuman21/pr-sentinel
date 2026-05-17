#!/usr/bin/env python3
"""
Test para debugear la extracción de contenido del diff
"""
import os
from dotenv import load_dotenv
import github_client
import llm_reasoner

load_dotenv()

def main():
    token = os.getenv("GITHUB_TOKEN")
    repo = "MaxTheHuman21/pr-sentinel"
    pr_number = 5
    
    # Obtener diff
    diff, changed_files = github_client.get_pr_diff(repo, pr_number, token)
    
    print("=" * 80)
    print("TEST: Extracción de contenido del diff")
    print("=" * 80)
    
    print(f"\nChanged files: {changed_files}")
    print(f"\nDiff length: {len(diff)} caracteres")
    
    print("\n--- DIFF RAW ---")
    print(diff)
    print("--- END DIFF ---\n")
    
    # Probar extracción
    file_contents = llm_reasoner._extract_file_contents_from_diff(diff, changed_files)
    
    print(f"\nArchivos extraídos: {len(file_contents)}")
    for filepath, content in file_contents.items():
        print(f"\n{'=' * 80}")
        print(f"Archivo: {filepath}")
        print(f"Contenido length: {len(content)} caracteres")
        print(f"{'=' * 80}")
        print(content)
        print(f"{'=' * 80}\n")
        
        # Análisis del contenido
        print(f"Análisis de {filepath}:")
        print(f"  - Tiene 'def ': {'def ' in content}")
        print(f"  - Tiene '@auth_middleware': {'@auth_middleware' in content}")
        print(f"  - Tiene 'auth_middleware': {'auth_middleware' in content}")
        print(f"  - Tiene '@route': {'@route' in content.lower()}")
        print(f"  - Tiene 'route': {'route' in content.lower()}")
        print(f"  - Tiene 'import': {'import' in content}")

if __name__ == "__main__":
    main()

# Made with Bob
