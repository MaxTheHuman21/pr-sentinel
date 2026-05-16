"""
GitHub API Client Module
Provides functions to interact with GitHub API for PR analysis.
"""

import base64
import requests
from requests.exceptions import HTTPError, ConnectionError


def get_pr_diff(repo: str, pr_number: int, token: str) -> str:
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        files = response.json()
        patches = []
        
        for file in files:
            # Filtro: ignorar arquivos removidos
            if file.get('status') == 'removed':
                continue
            
            # Obter o diff de cada arquivo
            patch = file.get('patch')
            if patch:
                patches.append(patch)
        
        return '\n'.join(patches)
    
    except HTTPError as e:
        print(f"[ERROR] HTTP error in get_pr_diff: {e}")
        raise
    except ConnectionError as e:
        print(f"[ERROR] Connection error in get_pr_diff: {e}")
        raise


def get_repo_file(repo: str, path: str, token: str) -> str:
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        # Decodificar base64
        content_b64 = data.get('content', '')
        content_decoded = base64.b64decode(content_b64).decode('utf-8')
        
        return content_decoded
    
    except HTTPError as e:
        print(f"[ERROR] HTTP error in get_repo_file for {path}: {e}")
        raise
    except ConnectionError as e:
        print(f"[ERROR] Connection error in get_repo_file for {path}: {e}")
        raise


def list_python_files(repo: str, token: str) -> list[str]:
    url = f"https://api.github.com/repos/{repo}/git/trees/HEAD?recursive=1"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        # Control de Truncado
        if data.get('truncated', False):
            print('[WARN] Árbol del repo truncado por GitHub análisis parcial')
        
        # Obtener todos los archivos .py en el repositorio
        tree = data.get('tree', [])
        python_files = [
            item['path'] 
            for item in tree 
            if item.get('path', '').endswith('.py')
        ]
        
        return python_files
    
    except HTTPError as e:
        print(f"[ERROR] HTTP error in list_python_files: {e}")
        raise
    except ConnectionError as e:
        print(f"[ERROR] Connection error in list_python_files: {e}")
        raise


def post_pr_comment(repo: str, pr_number: int, body: str, token: str) -> bool:
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    payload = {"body": body}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        return response.status_code == 201
    
    except HTTPError as e:
        print(f"[ERROR] HTTP error in post_pr_comment: {e}")
        return False
    except ConnectionError as e:
        print(f"[ERROR] Connection error in post_pr_comment: {e}")
        return False

# Made with Bob and modified by P2