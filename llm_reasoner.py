"""
LLM Reasoner Module - IBM Bob Platform Edition v3.0
Maneja la comunicación con el motor de inferencia de IBM Bob para análisis de PRs.

CONTRATO JSON - ACORDADO ENTRE P3 Y P4 
Este es el formato estricto que debe devolver la función call_llm():

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

import requests
import json
import os


def build_prompt(diff, adrs, rules, import_map, changed_files):
    """
    Construye el prompt completo para el LLM combinando todos los contextos de arquitectura.
    """
    # Formatear lista de archivos cambiados
    files_list = "\n".join(f"- {file}" for file in changed_files) if changed_files else "Ninguno"
    
    # Nuevo contrato JSON estricto acordado entre P3 y P4
    esquema_contrato = {
        "blockers": [
            {
                "description": "Explicación detallada de la violación crítica de arquitectura o seguridad",
                "file": "nombre_archivo.py",
                "line": "número_línea",
                "adr_reference": "ADR-XXX"
            }
        ],
        "warnings": [
            {
                "description": "Aviso de posible inconsistencia o mala práctica",
                "file": "nombre_archivo.py",
                "line": "número_línea",
                "adr_reference": "None o ADR-XXX"
            }
        ],
        "suggestions": [
            {
                "description": "Sugerencia de mejora de código u optimización limpia",
                "file": "nombre_archivo.py",
                "line": "número_línea",
                "adr_reference": "None"
            }
        ]
    }

    prompt = f"""=== ADRs ===
{adrs}

=== Reglas de Arquitectura del Sistema ===
{rules}

=== Mapa de Imports y Dependencias ===
{import_map}

=== Archivos Modificados en la PR ===
{files_list}

=== Diff del Código Fuente a Evaluar ===
{diff}

=== REQUERIMIENTO ESTRICTO DE SALIDA ===
Debes actuar como un auditor de código experto. Analiza el Diff contra las reglas y los ADRs. 
Responde ÚNICAMENTE con un JSON válido que siga exactamente este esquema de objetos detallados:
{json.dumps(esquema_contrato, indent=2)}

No incluyas texto explicativo, saludos ni bloques de código markdown, solo el objeto JSON plano."""
    
    return prompt


def call_llm(prompt, api_key):
    """
    Llama a la API oficial de inferencia de IBM Bob usando tokens del hackathon.
    Implementa lógica de reintento si el JSON es malformado.
    
    Args:
        prompt (str): Prompt construido con build_prompt
        api_key (str): Tu BOB_API_KEY generada en el panel de administración
    
    Returns:
        dict: Diccionario con las llaves 'blockers', 'warnings', 'suggestions'
    """
    # URL del endpoint del motor de razonamiento de IBM Bob
    url = os.getenv("BOB_API_URL", "https://api.ibm.com/bob/v1/chat/completions")
    
    # Configuración de cabeceras estándar para la API de Bob (Usa esquema Bearer Token)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    system_prompt = "Eres un auditor de código y ciberseguridad industrial. Tu salida debe ser única y exclusivamente JSON válido."
    
    # Construir mensajes iniciales
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    # Parámetros del request adaptados para optimizar el consumo de tokens y asegurar reproducibilidad
    payload = {
        "model": os.getenv("BOB_MODEL_NAME", "ibm/granite-13b-chat-v2"),
        "temperature": 0,  # Obligatorio para reproducibilidad analítica (RNF-05)
        "max_tokens": 2000,  # Límite de tokens para la respuesta
        "messages": messages
    }
    
    # Primer intento de auditoría
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        response_data = response.json()
        
        # Extraer el contenido textual según la estructura OpenAI compatible de Bob
        if "choices" in response_data and len(response_data["choices"]) > 0:
            content = response_data["choices"][0]["message"]["content"]
        else:
            raise ValueError("La API de IBM Bob respondió sin un bloque 'choices' válido.")
        
        # Limpiar posibles bloques de formateo markdown que agregue la IA por error
        content_clean = content.strip().replace("```json", "").replace("```", "")
        
        try:
            result = json.loads(content_clean)
            # Asegurar e inicializar la estructura acordada en caso de venir incompleta
            return sanitize_and_fill_keys(result)
            
        except (json.JSONDecodeError, ValueError) as parse_error:
            print(f"⚠️ Primer intento falló al parsear el JSON de Bob: {parse_error}")
            
            # Agregar la respuesta errónea y la corrección al historial de mensajes para el reintento
            messages.append({"role": "assistant", "content": content})
            messages.append({"role": "user", "content": "Tu respuesta no cumple con la estructura esperada o no es JSON válido. Corrige la respuesta e imprime únicamente el JSON plano."})
            payload["messages"] = messages
            
            # REINTENTO ÚNICO CONTROLADO
            print("🔄 Reintentando petición enviando el historial de corrección...")
            retry_response = requests.post(url, headers=headers, json=payload, timeout=60)
            retry_response.raise_for_status()
            
            retry_data = retry_response.json()
            retry_content = retry_data["choices"][0]["message"]["content"]
            retry_content_clean = retry_content.strip().replace("```json", "").replace("```", "")
            
            try:
                result = json.loads(retry_content_clean)
                print("✅ Reintento exitoso - Estructura JSON válida obtenida de IBM Bob")
                return sanitize_and_fill_keys(result)
                
            except (json.JSONDecodeError, ValueError) as retry_error:
                error_msg = f"El reintento con Bob también falló. Error: {retry_error}."
                print(error_msg)
                raise Exception(f"No se pudo estructurar el JSON final tras el reintento: {error_msg}")
    
    except requests.exceptions.RequestException as req_error:
        print(f"❌ Error en la comunicación HTTP con Bob: {req_error}")
        return {"blockers": [{"description": f"Fallo de conexión HTTP: {str(req_error)}", "file": "None", "line": "0", "adr_reference": "None"}], "warnings": [], "suggestions": []}
    
    except Exception as e:
        print(f"❌ Error inesperado en el módulo razonador: {e}")
        return {"blockers": [{"description": f"Error inesperado: {str(e)}", "file": "None", "line": "0", "adr_reference": "None"}], "warnings": [], "suggestions": []}


def sanitize_and_fill_keys(result):
    """
    Garantiza que el diccionario resultante contenga las tres llaves principales
    acordadas en el contrato con P4.
    """
    if not isinstance(result, dict):
        result = {}
        
    for key in ["blockers", "warnings", "suggestions"]:
        if key not in result or not isinstance(result[key], list):
            result[key] = []
    return result


def validate_response_structure(response):
    """
    Valida detalladamente que la respuesta siga el contrato de objetos acordado entre P3 y P4.
    """
    if not isinstance(response, dict):
        return False
    
    required_keys = ["blockers", "warnings", "suggestions"]
    required_object_fields = ["description", "file", "line", "adr_reference"]
    
    for key in required_keys:
        if key not in response or not isinstance(response[key], list):
            return False
        
        # Validar la estructura interna de cada objeto dentro de las listas
        for item in response[key]:
            if not isinstance(item, dict):
                return False
            if not all(field in item for field in required_object_fields):
                return False
                
    return True

# Made with Bob 🚀