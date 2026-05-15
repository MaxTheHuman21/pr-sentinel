"""
CONTRATO JSON - ACORDADO ENTRE P3 Y P4 
Este es el formato estricto que debe devolver la función call_llm().
"""
{
  "blockers": [
    {
      "description": "Explicación de la violación crítica",
      "file": "nombre_archivo.py",
      "line": "14",
      "adr_reference": "ADR-002"
    }
  ],
  "warnings": [
    {
      "description": "Aviso de posible inconsistencia",
      "file": "nombre_archivo.py",
      "line": "10",
      "adr_reference": "None"
    }
  ],
  "suggestions": [
    {
      "description": "Sugerencia de mejora de código",
      "file": "nombre_archivo.py",
      "line": "5",
      "adr_reference": "None"
    }
  ]
}

"""
LLM Reasoner Module - Tech Lead Brief v3.0
Maneja la comunicación con Anthropic Claude para análisis de PRs.
"""

import requests
import json
import os


def build_prompt(diff, adrs, rules, import_map, changed_files):
    """
    Construye el prompt completo para el LLM combinando todos los contextos.
    
    Args:
        diff (str): Diff de la Pull Request
        adrs (str): Architecture Decision Records concatenados
        rules (str): Reglas de arquitectura del proyecto
        import_map (str): Mapa de dependencias e imports
        changed_files (list): Lista de archivos modificados
    
    Returns:
        str: Prompt formateado listo para enviar al LLM
    """
    # Formatear lista de archivos cambiados
    files_list = "\n".join(f"- {file}" for file in changed_files) if changed_files else "Ninguno"
    
    # Construir el prompt completo
    prompt = f"""=== ADRs ===
{adrs}

=== Reglas de Arquitectura ===
{rules}

=== Mapa de Imports ===
{import_map}

=== Archivos Modificados ===
{files_list}

=== Diff de la PR ===
{diff}

Responde ÚNICAMENTE con un JSON válido que siga este esquema: {{"blockers": [], "warnings": [], "suggestions": []}}"""
    
    return prompt


def call_llm(prompt, api_key):
    """
    Llama a la API de Anthropic Claude con configuración crítica v3.0.
    Implementa lógica de reintento si el JSON es malformado.
    
    Args:
        prompt (str): Prompt construido con build_prompt
        api_key (str): API key de Anthropic
    
    Returns:
        dict: Diccionario con estructura {"blockers": [], "warnings": [], "suggestions": []}
    
    Raises:
        Exception: Si la API falla o el JSON no puede parsearse después del reintento
    """
    # Configuración de la API de Anthropic
    url = "https://api.anthropic.com/v1/messages"
    
    # Headers específicos de Anthropic (NO usar Bearer)
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    # System prompt exacto según especificaciones
    system_prompt = "Eres un auditor de código. Respondes SOLO en JSON válido."
    
    # Preparar mensajes iniciales
    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    # Parámetros del request
    payload = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 4096,
        "temperature": 0,  # Obligatorio para RNF-05 (reproducibilidad)
        "system": system_prompt,
        "messages": messages
    }
    
    # Primer intento
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        response_data = response.json()
        
        # Extraer el contenido de la respuesta
        if "content" in response_data and len(response_data["content"]) > 0:
            content = response_data["content"][0]["text"]
        else:
            raise ValueError("Respuesta de API sin contenido válido")
        
        # Intentar parsear el JSON
        try:
            result = json.loads(content)
            
            # Validar estructura básica
            if not isinstance(result, dict):
                raise ValueError("La respuesta no es un diccionario")
            
            # Asegurar que tenga las claves requeridas
            if "blockers" not in result:
                result["blockers"] = []
            if "warnings" not in result:
                result["warnings"] = []
            if "suggestions" not in result:
                result["suggestions"] = []
            
            return result
            
        except (json.JSONDecodeError, ValueError) as parse_error:
            # JSON malformado - implementar lógica de reintento
            print(f"Primer intento falló al parsear JSON: {parse_error}")
            print(f"Respuesta malformada: {content[:200]}...")
            
            # Agregar la respuesta malformada al historial
            messages.append({
                "role": "assistant",
                "content": content
            })
            
            # Agregar mensaje de corrección
            messages.append({
                "role": "user",
                "content": "Tu respuesta no fue JSON válido. Responde SOLO con JSON."
            })
            
            # Actualizar payload con el historial
            payload["messages"] = messages
            
            # REINTENTO (una sola vez)
            print("Reintentando con historial de mensajes...")
            retry_response = requests.post(url, headers=headers, json=payload, timeout=60)
            retry_response.raise_for_status()
            
            retry_data = retry_response.json()
            
            if "content" in retry_data and len(retry_data["content"]) > 0:
                retry_content = retry_data["content"][0]["text"]
            else:
                raise ValueError("Respuesta de reintento sin contenido válido")
            
            # Intentar parsear el JSON del reintento
            try:
                result = json.loads(retry_content)
                
                # Validar estructura básica
                if not isinstance(result, dict):
                    raise ValueError("La respuesta del reintento no es un diccionario")
                
                # Asegurar que tenga las claves requeridas
                if "blockers" not in result:
                    result["blockers"] = []
                if "warnings" not in result:
                    result["warnings"] = []
                if "suggestions" not in result:
                    result["suggestions"] = []
                
                print("Reintento exitoso - JSON válido obtenido")
                return result
                
            except (json.JSONDecodeError, ValueError) as retry_error:
                # Segundo intento también falló
                error_msg = f"Reintento falló. Error: {retry_error}. Respuesta: {retry_content[:200]}"
                print(error_msg)
                raise Exception(f"No se pudo obtener JSON válido después del reintento: {error_msg}")
    
    except requests.exceptions.RequestException as req_error:
        print(f"Error en la petición HTTP: {req_error}")
        return {"blockers": [], "warnings": [], "suggestions": []}
    
    except Exception as e:
        print(f"Error inesperado: {e}")
        return {"blockers": [], "warnings": [], "suggestions": []}


# Función auxiliar para testing (opcional)
def validate_response_structure(response):
    """
    Valida que la respuesta tenga la estructura correcta.
    
    Args:
        response (dict): Respuesta del LLM
    
    Returns:
        bool: True si la estructura es válida
    """
    if not isinstance(response, dict):
        return False
    
    required_keys = ["blockers", "warnings", "suggestions"]
    
    for key in required_keys:
        if key not in response:
            return False
        if not isinstance(response[key], list):
            return False
    
    return True

# Made with Bob
