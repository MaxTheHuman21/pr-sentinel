"""
GitHub API Client Module
Provides functions to interact with GitHub API for PR analysis.
"""

import base64
import requests
from requests.exceptions import HTTPError, ConnectionError


def get_pr_diff(repo: str, pr_number: int, token: str) -> tuple:
    """
    Obtiene el diff de una PR y los archivos modificados.
    Retorna: (diff_string, [list_of_changed_files])
    """
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        files = response.json()
        patches = []
        changed_files = []
        
        for file in files:
            # Filtro: ignorar archivos removidos
            if file.get('status') == 'removed':
                continue
            
            filename = file.get('filename')
            patch = file.get('patch')
            
            if filename:
                changed_files.append(filename)
            if patch:
                patches.append(patch)
        
        diff = '\n'.join(patches)
        return diff, changed_files
    
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
        response = requests.get(url, headers=headers, timeout=10)
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


class NoValidFilesError(Exception):
    """Exception raised when no valid files remain after filtering."""
    pass


def _should_exclude_by_extension(filepath: str) -> bool:
    """
    Capa 1: Excluir extensiones no deseadas.
    Retorna True si el archivo debe ser excluido.
    """
    excluded_extensions = (
        '.lock', '.log', '.min.js', '.min.css', '.map',
        '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp',
        '.pdf', '.zip', '.tar', '.gz', '.rar', '.7z',
        '.woff', '.woff2', '.ttf', '.eot', '.otf'
    )
    return filepath.lower().endswith(excluded_extensions)


def _should_exclude_by_folder(filepath: str) -> bool:
    """
    Capa 2: Excluir carpetas no deseadas.
    Retorna True si el archivo está en una carpeta excluida.
    """
    excluded_folders = (
        'node_modules/', 'dist/', 'build/', '.next/',
        '__pycache__/', '.pytest_cache/', 'coverage/',
        '.git/', '.venv/', 'venv/', 'env/',
        '.idea/', '.vscode/', 'target/', 'out/'
    )
    
    # Normalizar path para comparación
    normalized_path = filepath.replace('\\', '/')
    
    for folder in excluded_folders:
        if f'/{folder}' in f'/{normalized_path}' or normalized_path.startswith(folder):
            return True
    
    return False


def _is_whitelisted_extension(filepath: str) -> bool:
    """
    Capa 3: Whitelist de inclusión.
    Retorna True si el archivo tiene una extensión permitida.
    """
    whitelisted_extensions = (
        '.py', '.js', '.ts', '.tsx', '.jsx',
        '.yaml', '.yml', '.json', '.toml',
        '.sh', '.bash', '.md', '.txt',
        '.go', '.rs', '.java', '.kt', '.rb'
    )
    return filepath.lower().endswith(whitelisted_extensions)


def _apply_three_layer_filter(files: list[str]) -> list[str]:
    """
    Aplica el filtro de 3 capas a la lista de archivos.
    
    Capa 1: Excluir extensiones no deseadas
    Capa 2: Excluir carpetas no deseadas
    Capa 3: Whitelist de inclusión
    
    Retorna lista de archivos válidos.
    """
    valid_files = []
    
    for filepath in files:
        # Capa 1: Excluir extensiones
        if _should_exclude_by_extension(filepath):
            continue
        
        # Capa 2: Excluir carpetas
        if _should_exclude_by_folder(filepath):
            continue
        
        # Capa 3: Whitelist
        if not _is_whitelisted_extension(filepath):
            continue
        
        valid_files.append(filepath)
    
    return valid_files


def list_python_files(repo: str, token: str) -> list[str]:
    """
    Obtiene todos los archivos Python válidos del repositorio.
    Aplica filtrado de 3 capas para excluir archivos no deseados.
    
    Args:
        repo: Nombre del repositorio en formato "owner/repo"
        token: Token de autenticación de GitHub
    
    Returns:
        Lista de rutas de archivos Python válidos
    
    Raises:
        NoValidFilesError: Si no quedan archivos válidos después del filtrado
        HTTPError: Si hay un error en la petición HTTP
        ConnectionError: Si hay un error de conexión
    """
    url = f"https://api.github.com/repos/{repo}/git/trees/HEAD?recursive=1"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Control de Truncado
        if data.get('truncated', False):
            print('[WARN] Árbol del repo truncado por GitHub - análisis parcial')
        
        # Obtener todos los archivos del repositorio
        tree = data.get('tree', [])
        all_files = [
            item['path']
            for item in tree
            if item.get('type') == 'blob' and item.get('path')
        ]
        
        # Filtrar solo archivos Python
        python_files = [f for f in all_files if f.endswith('.py')]
        
        # Aplicar filtro de 3 capas
        valid_files = _apply_three_layer_filter(python_files)
        
        # Validación: si no quedan archivos válidos
        if not valid_files:
            raise NoValidFilesError(
                f"No se encontraron archivos Python válidos en {repo} después del filtrado"
            )
        
        return valid_files
    
    except HTTPError as e:
        print(f"[ERROR] HTTP error in list_python_files: {e}")
        raise
    except ConnectionError as e:
        print(f"[ERROR] Connection error in list_python_files: {e}")
        raise


def list_valid_files(repo: str, token: str) -> list[str]:
    """
    Obtiene todos los archivos válidos del repositorio (no solo Python).
    Aplica filtrado de 3 capas para excluir archivos no deseados.
    
    Args:
        repo: Nombre del repositorio en formato "owner/repo"
        token: Token de autenticación de GitHub
    
    Returns:
        Lista de rutas de archivos válidos
    
    Raises:
        NoValidFilesError: Si no quedan archivos válidos después del filtrado
        HTTPError: Si hay un error en la petición HTTP
        ConnectionError: Si hay un error de conexión
    """
    url = f"https://api.github.com/repos/{repo}/git/trees/HEAD?recursive=1"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Control de Truncado
        if data.get('truncated', False):
            print('[WARN] Árbol del repo truncado por GitHub - análisis parcial')
        
        # Obtener todos los archivos del repositorio
        tree = data.get('tree', [])
        all_files = [
            item['path']
            for item in tree
            if item.get('type') == 'blob' and item.get('path')
        ]
        
        # Aplicar filtro de 3 capas
        valid_files = _apply_three_layer_filter(all_files)
        
        # Validación: si no quedan archivos válidos
        if not valid_files:
            raise NoValidFilesError(
                f"No se encontraron archivos válidos en {repo} después del filtrado"
            )
        
        return valid_files
    
    except HTTPError as e:
        print(f"[ERROR] HTTP error in list_valid_files: {e}")
        raise
    except ConnectionError as e:
        print(f"[ERROR] Connection error in list_valid_files: {e}")
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
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        
        return response.status_code == 201
    
    except HTTPError as e:
        print(f"[ERROR] HTTP error in post_pr_comment: {e}")
        return False
    except ConnectionError as e:
        print(f"[ERROR] Connection error in post_pr_comment: {e}")
        return False

# Made with Bob and modified by P2