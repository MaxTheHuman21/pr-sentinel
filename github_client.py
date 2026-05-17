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

    BUG FIX: Each patch hunk is now prefixed with "+++ b/{filename}\n" so that
    _local_adr_analysis() and _find_endpoints_in_diff_without_auth() can identify
    which file each hunk belongs to. Without this header the parsers always saw
    current_file = None and produced zero findings.
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
            # Ignore deleted files — they are no longer in the codebase.
            if file.get("status") == "removed":
                continue

            filename = file.get("filename")
            patch = file.get("patch")

            if filename:
                changed_files.append(filename)

            # Prepend the standard unified-diff header so downstream parsers
            # that look for "+++ b/<path>" can identify the current file.
            if patch and filename:
                patches.append(f"+++ b/{filename}\n{patch}")

        diff = "\n".join(patches)
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
        content_b64 = data.get("content", "")
        content_decoded = base64.b64decode(content_b64).decode("utf-8")
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
    excluded_extensions = (
        ".lock", ".log", ".min.js", ".min.css", ".map",
        ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp",
        ".pdf", ".zip", ".tar", ".gz", ".rar", ".7z",
        ".woff", ".woff2", ".ttf", ".eot", ".otf",
    )
    return filepath.lower().endswith(excluded_extensions)


def _should_exclude_by_folder(filepath: str) -> bool:
    excluded_folders = (
        "node_modules/", "dist/", "build/", ".next/",
        "__pycache__/", ".pytest_cache/", "coverage/",
        ".git/", ".venv/", "venv/", "env/",
        ".idea/", ".vscode/", "target/", "out/",
    )
    normalized_path = filepath.replace("\\", "/")
    for folder in excluded_folders:
        if f"/{folder}" in f"/{normalized_path}" or normalized_path.startswith(folder):
            return True
    return False


def _is_whitelisted_extension(filepath: str) -> bool:
    whitelisted_extensions = (
        ".py", ".js", ".ts", ".tsx", ".jsx",
        ".yaml", ".yml", ".json", ".toml",
        ".sh", ".bash", ".md", ".txt",
        ".go", ".rs", ".java", ".kt", ".rb",
    )
    return filepath.lower().endswith(whitelisted_extensions)


def _apply_three_layer_filter(files: list) -> list:
    valid_files = []
    for filepath in files:
        if _should_exclude_by_extension(filepath):
            continue
        if _should_exclude_by_folder(filepath):
            continue
        if not _is_whitelisted_extension(filepath):
            continue
        valid_files.append(filepath)
    return valid_files


def list_python_files(repo: str, token: str) -> list:
    url = f"https://api.github.com/repos/{repo}/git/trees/HEAD?recursive=1"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get("truncated", False):
            print("[WARN] Árbol del repo truncado por GitHub - análisis parcial")

        tree = data.get("tree", [])
        all_files = [
            item["path"]
            for item in tree
            if item.get("type") == "blob" and item.get("path")
        ]

        python_files = [f for f in all_files if f.endswith(".py")]
        valid_files = _apply_three_layer_filter(python_files)

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


def list_valid_files(repo: str, token: str) -> list:
    url = f"https://api.github.com/repos/{repo}/git/trees/HEAD?recursive=1"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get("truncated", False):
            print("[WARN] Árbol del repo truncado por GitHub - análisis parcial")

        tree = data.get("tree", [])
        all_files = [
            item["path"]
            for item in tree
            if item.get("type") == "blob" and item.get("path")
        ]

        valid_files = _apply_three_layer_filter(all_files)

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
        "Content-Type": "application/json",
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