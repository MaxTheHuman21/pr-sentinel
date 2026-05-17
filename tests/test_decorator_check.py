#!/usr/bin/env python3
"""
Test específico para el check del decorador
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
    
    # Extraer contenido
    file_contents = llm_reasoner._extract_file_contents_from_diff(diff, changed_files)
    
    for filepath, content in file_contents.items():
        print(f"Archivo: {filepath}")
        print("=" * 80)
        
        lines = content.split("\n")
        print(f"Total líneas: {len(lines)}\n")
        
        print("Buscando decoradores @auth_middleware:")
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            starts_with_at = stripped.startswith("@")
            has_auth = "auth_middleware" in line
            
            if starts_with_at or has_auth:
                print(f"  Línea {i}: starts_with_@={starts_with_at}, has_auth={has_auth}")
                print(f"    Content: {line}")
                
                if starts_with_at and has_auth:
                    print(f"    >>> MATCH! Esta línea tiene el decorador")
        
        # Ejecutar el check real
        has_auth_decorator = any(
            line.strip().startswith("@") and "auth_middleware" in line
            for line in lines
        )
        
        print(f"\nResultado final: has_auth_decorator = {has_auth_decorator}")

if __name__ == "__main__":
    main()

# Made with Bob
