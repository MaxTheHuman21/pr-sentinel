"""
test_watsonx.py - Diagnóstico de conexión con watsonx.ai
Ejecutar: python test_watsonx.py
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
WATSONX_URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")

def get_iam_token(api_key):
    response = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={api_key}",
        timeout=30
    )
    response.raise_for_status()
    return response.json()["access_token"]


print("=== DIAGNÓSTICO WATSONX.AI ===\n")

# 1. Obtener IAM token
print("[1] Obteniendo IAM token... ", end="")
try:
    token = get_iam_token(WATSONX_API_KEY)
    print("OK ✓")
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 2. Listar modelos disponibles
print("[2] Listando modelos disponibles... ", end="")
try:
    r = requests.get(
        f"{WATSONX_URL}/ml/v1/foundation_model_specs?version=2023-05-29&limit=50",
        headers=headers,
        timeout=30
    )
    if r.status_code == 200:
        models = r.json().get("resources", [])
        print(f"OK ✓ ({len(models)} modelos encontrados)\n")
        print("Modelos disponibles:")
        for m in models:
            print(f"  - {m.get('model_id')}")
    else:
        print(f"ERROR {r.status_code}: {r.text[:200]}")
except Exception as e:
    print(f"ERROR: {e}")

# 3. Probar endpoint de generación con granite-3-8b
print("\n[3] Probando generación con ibm/granite-3-8b-instruct... ", end="")
try:
    payload = {
        "model_id": "ibm/granite-3-8b-instruct",
        "project_id": WATSONX_PROJECT_ID,
        "input": "Responde solo con JSON: {\"status\": \"ok\"}",
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 50
        }
    }
    r = requests.post(
        f"{WATSONX_URL}/ml/v1/text/generation?version=2023-05-29",
        headers=headers,
        json=payload,
        timeout=30
    )
    if r.status_code == 200:
        text = r.json()["results"][0]["generated_text"]
        print(f"OK ✓\n  Respuesta: {text[:100]}")
    else:
        print(f"ERROR {r.status_code}: {r.text[:300]}")
except Exception as e:
    print(f"ERROR: {e}")

# 4. Probar con granite-13b-chat-v2
print("\n[4] Probando generación con ibm/granite-13b-chat-v2... ", end="")
try:
    payload["model_id"] = "ibm/granite-13b-chat-v2"
    r = requests.post(
        f"{WATSONX_URL}/ml/v1/text/generation?version=2023-05-29",
        headers=headers,
        json=payload,
        timeout=30
    )
    if r.status_code == 200:
        text = r.json()["results"][0]["generated_text"]
        print(f"OK ✓\n  Respuesta: {text[:100]}")
    else:
        print(f"ERROR {r.status_code}: {r.text[:300]}")
except Exception as e:
    print(f"ERROR: {e}")