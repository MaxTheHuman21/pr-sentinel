#!/usr/bin/env python3
"""
Test detallado de detección de violaciones
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
    print("TEST: Detección de violaciones paso a paso")
    print("=" * 80)
    
    # Extraer contenido
    file_contents = llm_reasoner._extract_file_contents_from_diff(diff, changed_files)
    
    for filepath, content in file_contents.items():
        print(f"\n{'=' * 80}")
        print(f"Analizando: {filepath}")
        print(f"{'=' * 80}")
        
        normalized_filepath = filepath.replace("demo_repo/", "").replace("\\", "/")
        print(f"Normalized: {normalized_filepath}")
        
        is_api_file = (
            normalized_filepath.startswith("api/") or "/api/" in normalized_filepath
        )
        print(f"Is API file: {is_api_file}")
        
        if is_api_file:
            # Check decorador
            has_auth_decorator = "@auth_middleware" in content
            print(f"Has @auth_middleware decorator: {has_auth_decorator}")
            
            # Check import
            lines = content.split("\n")
            print(f"\nAnalizando imports línea por línea:")
            has_auth_import = False
            for i, line in enumerate(lines[:10], 1):  # Primeras 10 líneas
                has_import = "import" in line and "auth_middleware" in line
                print(f"  Línea {i}: {line[:60]}... -> import auth? {has_import}")
                if has_import:
                    has_auth_import = True
            
            print(f"\nHas auth import: {has_auth_import}")
            
            # Check endpoints
            has_endpoints = ("@" in content and "route" in content.lower()) or "def " in content
            print(f"Has endpoints: {has_endpoints}")
            
            # Decisión
            should_flag = has_endpoints and not (has_auth_decorator or has_auth_import)
            print(f"\n>>> SHOULD FLAG AS ADR-002 VIOLATION: {should_flag}")
            
            if should_flag:
                print(f"    Razón: tiene endpoints={has_endpoints}, pero no tiene auth_decorator={has_auth_decorator} ni auth_import={has_auth_import}")

if __name__ == "__main__":
    main()

# Made with Bob
