"""
Test suite for llm_reasoner.py module.
Tests build_prompt and call_llm functions with mocked IBM Bob API calls.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from llm_reasoner import build_prompt, call_llm, validate_response_structure


class TestBuildPrompt:
    """Test suite for build_prompt function (Tarea 3.B)"""
    
    def test_build_prompt_receives_five_arguments(self):
        """Verifica que build_prompt reciba los 5 argumentos requeridos"""
        diff = "diff content"
        adrs = ["ADR-001"]
        rules = ["Rule 1"]
        import_map = {"file.py": ["module"]}
        changed_files = ["file.py"]
        
        result = build_prompt(diff, adrs, rules, import_map, changed_files)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_build_prompt_contains_required_sections(self):
        """Valida que el prompt contenga las 4 secciones obligatorias adaptadas para Bob"""
        diff = "diff content"
        adrs = ["ADR-001: Test ADR"]
        rules = ["Rule 1: Test rule"]
        import_map = {"file.py": ["module1", "module2"]}
        changed_files = ["file.py", "test.py"]
        
        result = build_prompt(diff, adrs, rules, import_map, changed_files)
        
        # Ajustado para hacer match exacto con los encabezados reales de llm_reasoner.py
        assert "=== ADRs ===" in result
        assert "=== Reglas de Arquitectura del Sistema ===" in result
        assert "=== Mapa de Imports y Dependencias ===" in result
        assert "=== Diff del Código Fuente a Evaluar ===" in result


class TestCallLLM:
    """Test suite for call_llm function (Tarea 3.C)"""
    
    @patch('llm_reasoner.requests.post')
    def test_call_llm_ibm_bob_configuration(self, mock_post):
        """Verifica configuración correcta de headers, portador Bearer y temperatura para IBM Bob"""
        mock_bob_response = {
            "choices": [
                {
                    "message": {
                        "content": '{"blockers": [], "warnings": [], "suggestions": []}'
                    }
                }
            ]
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_bob_response
        mock_post.return_value = mock_response
        
        prompt = "Test prompt"
        api_key = "bob-enterprise-token-xyz"
        
        call_llm(prompt, api_key)
        
        assert mock_post.called
        call_args = mock_post.call_args
        
        # Verificar cabeceras estándar de IBM Bob (Esquema Bearer)
        headers = call_args[1]['headers']
        assert 'Authorization' in headers
        assert headers['Authorization'] == f"Bearer {api_key}"
        assert headers['Content-Type'] == "application/json"
        
        # Verificar temperatura = 0 (RNF-05) y payload de mensajería estructurado
        json_data = call_args[1]['json']
        assert json_data['temperature'] == 0
        assert isinstance(json_data['messages'], list)
        assert json_data['messages'][0]['role'] == 'system'
    
    @patch('llm_reasoner.requests.post')
    def test_call_llm_retry_logic_with_context(self, mock_post):
        """Simula reintento con JSON malformado y luego válido bajo el contrato de objetos de IBM Bob"""
        # Primer intento: IBM Bob devuelve texto malformado
        mock_response_1 = Mock()
        mock_response_1.status_code = 200
        mock_response_1.json.return_value = {
            "choices": [{"message": {"content": "{\"blockers\": [invalid json}"}}]
        }
        
        # Segundo intento: IBM Bob corrige su salida y entrega el contrato estructurado pactado
        valido_mock_contrato = {
            "blockers": [
                {
                    "description": "Falta middleware de autenticacion",
                    "file": "users.py",
                    "line": "14",
                    "adr_reference": "ADR-002"
                }
            ],
            "warnings": [],
            "suggestions": []
        }
        mock_response_2 = Mock()
        mock_response_2.status_code = 200
        mock_response_2.json.return_value = {
            "choices": [{"message": {"content": json.dumps(valido_mock_contrato)}}]
        }
        
        mock_post.side_effect = [mock_response_1, mock_response_2]
        
        prompt = "Test prompt"
        api_key = "bob-enterprise-token-xyz"
        
        result = call_llm(prompt, api_key)
        
        # Verificar que se hicieron los dos intentos
        assert mock_post.call_count == 2
        
        # Verificar que el segundo intento incluye el historial de mensajes de corrección
        second_call_args = mock_post.call_args_list[1]
        json_data = second_call_args[1]['json']
        messages = json_data['messages']
        
        assert len(messages) == 4
        assert messages[2]['role'] == 'assistant'
        assert messages[3]['role'] == 'user'
        
        # Verificar que el resultado final cumple con el contrato estructurado
        assert validate_response_structure(result) is True
        assert result["blockers"][0]["file"] == "users.py"
        assert result["blockers"][0]["line"] == "14"
        assert result["blockers"][0]["adr_reference"] == "ADR-002"
    
    @patch('llm_reasoner.requests.post')
    def test_call_llm_handles_api_failure(self, mock_post):
        """Verifica manejo de errores cuando la API lanza una excepción general en ejecución"""
        mock_post.side_effect = Exception("API connection failed")
        
        prompt = "Test prompt"
        api_key = "bob-enterprise-token-xyz"
        
        result = call_llm(prompt, api_key)
        
        # Valida que intercepte el error inesperado de ejecución de forma segura
        assert isinstance(result, dict)
        assert validate_response_structure(result) is True
        assert len(result["blockers"]) == 1
        assert "Error inesperado" in result["blockers"][0]["description"]
        assert result["blockers"][0]["file"] == "None"
    
    @patch('llm_reasoner.requests.post')
    def test_call_llm_handles_http_error(self, mock_post):
        """Verifica manejo de errores cuando ocurre un fallo controlado de peticiones HTTP"""
        import requests
        # Forzar un error de petición HTTP nativo para que caiga en el bloque exacto del RequestException
        mock_post.side_effect = requests.exceptions.RequestException("Fallo de conexión HTTP")
        
        prompt = "Test prompt"
        api_key = "bob-enterprise-token-xyz"
        
        result = call_llm(prompt, api_key)
        
        # Debe retornar la estructura de contingencia de red de forma segura
        assert isinstance(result, dict)
        assert validate_response_structure(result) is True
        assert len(result["blockers"]) == 1
        assert "Fallo de conexión HTTP" in result["blockers"][0]["description"]
    
    @patch('llm_reasoner.requests.post')
    def test_call_llm_parses_ibm_bob_response_structure(self, mock_post):
        """Verifica que se parsea correctamente la estructura de objetos detallados devuelta por IBM Bob"""
        expected_contract_result = {
            "blockers": [
                {
                    "description": "Violación crítica detectada",
                    "file": "auth.py",
                    "line": "22",
                    "adr_reference": "ADR-001"
                }
            ],
            "warnings": [
                {
                    "description": "Línea muy larga o compleja",
                    "file": "utils.py",
                    "line": "105",
                    "adr_reference": "None"
                }
            ],
            "suggestions": []
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": json.dumps(expected_contract_result)}}]
        }
        mock_post.return_value = mock_response
        
        prompt = "Test prompt"
        api_key = "bob-enterprise-token-xyz"
        
        result = call_llm(prompt, api_key)
        
        # Validación de la estructura y tipos de datos del nuevo contrato de objetos
        assert validate_response_structure(result) is True
        assert result == expected_contract_result
        assert result["blockers"][0]["file"] == "auth.py"
        assert result["blockers"][0]["adr_reference"] == "ADR-001"
        assert result["warnings"][0]["line"] == "105"
        assert len(result["suggestions"]) == 0