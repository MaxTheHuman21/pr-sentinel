"""
Test suite for llm_reasoner.py module.
Tests build_prompt and call_llm functions with mocked API calls.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from llm_reasoner import build_prompt, call_llm


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
        """Valida que el prompt contenga las 4 secciones obligatorias"""
        diff = "diff content"
        adrs = ["ADR-001: Test ADR"]
        rules = ["Rule 1: Test rule"]
        import_map = {"file.py": ["module1", "module2"]}
        changed_files = ["file.py", "test.py"]
        
        result = build_prompt(diff, adrs, rules, import_map, changed_files)
        
        assert "=== ADRs ===" in result
        assert "=== Reglas de Arquitectura ===" in result
        assert "=== Mapa de Imports ===" in result
        assert "=== Diff de la PR ===" in result


class TestCallLLM:
    """Test suite for call_llm function (Tarea 3.C)"""
    
    @patch('llm_reasoner.requests.post')
    def test_call_llm_anthropic_configuration(self, mock_post):
        """Verifica configuración correcta de headers y temperatura para Anthropic"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"text": '{"blockers": [], "warnings": [], "suggestions": []}'}]
        }
        mock_post.return_value = mock_response
        
        prompt = "Test prompt"
        api_key = "test-api-key"
        
        call_llm(prompt, api_key)
        
        # Verificar que se llamó a requests.post
        assert mock_post.called
        call_args = mock_post.call_args
        
        # Verificar headers obligatorios
        headers = call_args[1]['headers']
        assert 'x-api-key' in headers
        assert headers['x-api-key'] == api_key
        assert 'anthropic-version' in headers
        assert headers['anthropic-version'] == '2023-06-01'
        
        # Verificar temperatura = 0 (RNF-05)
        json_data = call_args[1]['json']
        assert json_data['temperature'] == 0
    
    @patch('llm_reasoner.requests.post')
    def test_call_llm_retry_logic_with_context(self, mock_post):
        """Simula reintento con JSON malformado y luego válido (Fix Crítico #5)"""
        # Primer intento: JSON malformado
        mock_response_1 = Mock()
        mock_response_1.status_code = 200
        mock_response_1.json.return_value = {
            "content": [{"text": '{"blockers": [invalid json}'}]
        }
        
        # Segundo intento: JSON válido
        mock_response_2 = Mock()
        mock_response_2.status_code = 200
        mock_response_2.json.return_value = {
            "content": [{"text": '{"blockers": [], "warnings": [], "suggestions": []}'}]
        }
        
        mock_post.side_effect = [mock_response_1, mock_response_2]
        
        prompt = "Test prompt"
        api_key = "test-api-key"
        
        result = call_llm(prompt, api_key)
        
        # Verificar que se hicieron 2 llamadas
        assert mock_post.call_count == 2
        
        # Verificar que el segundo intento incluye historial de mensajes
        second_call_args = mock_post.call_args_list[1]
        json_data = second_call_args[1]['json']
        messages = json_data['messages']
        
        # Debe haber al menos 2 mensajes (user original + assistant con error)
        assert len(messages) >= 2
        
        # Verificar que el resultado final es válido
        assert isinstance(result, dict)
        assert "blockers" in result
        assert "warnings" in result
        assert "suggestions" in result
    
    @patch('llm_reasoner.requests.post')
    def test_call_llm_handles_api_failure(self, mock_post):
        """Verifica manejo de errores cuando la API falla completamente (RNF-04)"""
        # Simular fallo total de la API
        mock_post.side_effect = Exception("API connection failed")
        
        prompt = "Test prompt"
        api_key = "test-api-key"
        
        result = call_llm(prompt, api_key)
        
        # Verificar que retorna el diccionario vacío por defecto
        assert isinstance(result, dict)
        assert result == {"blockers": [], "warnings": [], "suggestions": []}
    
    @patch('llm_reasoner.requests.post')
    def test_call_llm_handles_http_error(self, mock_post):
        """Verifica manejo de errores HTTP (status code != 200)"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        prompt = "Test prompt"
        api_key = "test-api-key"
        
        result = call_llm(prompt, api_key)
        
        # Verificar que retorna el diccionario vacío por defecto
        assert isinstance(result, dict)
        assert result == {"blockers": [], "warnings": [], "suggestions": []}
    
    @patch('llm_reasoner.requests.post')
    def test_call_llm_parses_anthropic_response_structure(self, mock_post):
        """Verifica que se parsea correctamente la estructura de respuesta de Anthropic"""
        expected_result = {
            "blockers": ["Blocker 1"],
            "warnings": ["Warning 1"],
            "suggestions": ["Suggestion 1"]
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"text": json.dumps(expected_result)}]
        }
        mock_post.return_value = mock_response
        
        prompt = "Test prompt"
        api_key = "test-api-key"
        
        result = call_llm(prompt, api_key)
        
        assert result == expected_result
        assert result["blockers"] == ["Blocker 1"]
        assert result["warnings"] == ["Warning 1"]
        assert result["suggestions"] == ["Suggestion 1"]
