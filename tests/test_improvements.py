"""
Test Suite for PR Sentinel Improvements
Tests for robustness and multi-vulnerability detection features.

Author: QA Senior Engineer
Framework: pytest + unittest.mock
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

# Import modules to test
import github_client
import report_formatter
import llm_reasoner


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def mock_github_token():
    """Mock GitHub token for testing."""
    return "ghp_test_token_12345"


@pytest.fixture
def mock_repo():
    """Mock repository name."""
    return "test-owner/test-repo"


@pytest.fixture
def mock_api_key():
    """Mock watsonx API key."""
    return "test_api_key_12345"


@pytest.fixture
def sample_files_mixed():
    """
    Sample file list with valid and invalid files for 3-layer filtering.
    Contains:
    - Valid: .py, .js files
    - Invalid by extension: .lock, .log, .map
    - Invalid by folder: node_modules/, __pycache__/, dist/
    """
    return [
        "src/app.py",
        "src/utils.js",
        "api/users.py",
        "yarn.lock",  # Should be excluded (extension - ends with .lock)
        "debug.log",  # Should be excluded (extension)
        "build/app.min.js.map",  # Should be excluded (extension)
        "node_modules/express/index.js",  # Should be excluded (folder)
        "__pycache__/cache.pyc",  # Should be excluded (folder)
        "dist/bundle.js",  # Should be excluded (folder)
        "services/order_service.py",
        ".venv/lib/python3.9/site.py",  # Should be excluded (folder)
    ]


@pytest.fixture
def sample_files_all_excluded():
    """
    Sample file list where ALL files should be excluded after 3-layer filtering.
    """
    return [
        "yarn.lock",  # Excluded by extension (.lock)
        "debug.log",  # Excluded by extension (.log)
        "error.log",  # Excluded by extension (.log)
        "node_modules/package/index.js",  # Excluded by folder
        "__pycache__/module.pyc",  # Excluded by folder
        "dist/bundle.min.js",  # Excluded by extension (.min.js)
        ".venv/lib/site.py",  # Excluded by folder
        "build/output.map",  # Excluded by extension (.map)
        "assets/logo.png",  # Excluded by extension (.png)
        "docs/diagram.pdf",  # Excluded by extension (.pdf)
    ]


@pytest.fixture
def sample_multi_vulnerability_findings():
    """
    Sample findings with multiple concurrent errors across different files.
    2 Blockers (ADR-001, ADR-002) + 1 Warning (ADR-003)
    """
    return {
        "blockers": [
            {
                "description": "API endpoint missing @auth_middleware decorator",
                "file": "api/users.py",
                "line": "15",
                "adr_reference": "ADR-002",
                "suggested_fix": "@auth_middleware\n@app.route('/users')\ndef get_users():\n    pass"
            },
            {
                "description": "Direct import from /db/ layer violates modular architecture",
                "file": "api/analytics.py",
                "line": "3",
                "adr_reference": "ADR-001",
                "suggested_fix": "# Replace:\nfrom db.database import get_connection\n\n# With:\nfrom services.analytics_service import get_analytics_data"
            }
        ],
        "warnings": [
            {
                "description": "Missing try-except block for error handling",
                "file": "services/payment_service.py",
                "line": "42",
                "adr_reference": "ADR-003",
                "suggested_fix": "try:\n    process_payment()\nexcept PaymentError as e:\n    logger.error(f'Payment failed: {e}')\n    raise"
            }
        ],
        "suggestions": []
    }


@pytest.fixture
def sample_empty_suggestions_findings():
    """
    Sample findings where suggestions list is empty.
    Should render properly with "Sin sugerencias detectadas" message.
    """
    return {
        "blockers": [
            {
                "description": "Critical security issue",
                "file": "api/admin.py",
                "line": "10",
                "adr_reference": "ADR-002"
            }
        ],
        "warnings": [],
        "suggestions": []
    }


@pytest.fixture
def sample_llm_multi_error_response():
    """
    Mock LLM API response with multiple concurrent errors in different files.
    """
    return {
        "results": [
            {
                "generated_text": json.dumps({
                    "blockers": [
                        {
                            "description": "API endpoint missing @auth_middleware decorator",
                            "file": "api/users.py",
                            "line": "20",
                            "adr_reference": "ADR-002"
                        },
                        {
                            "description": "Direct database import violates architecture",
                            "file": "api/analytics.py",
                            "line": "5",
                            "adr_reference": "ADR-001"
                        },
                        {
                            "description": "Missing authentication in admin endpoint",
                            "file": "api/admin.py",
                            "line": "12",
                            "adr_reference": "ADR-002"
                        }
                    ],
                    "warnings": [
                        {
                            "description": "Incomplete error handling",
                            "file": "api/users.py",
                            "line": "45",
                            "adr_reference": "ADR-003"
                        }
                    ],
                    "suggestions": [
                        {
                            "description": "Consider adding input validation",
                            "file": "api/analytics.py",
                            "line": "30",
                            "adr_reference": "Best Practice"
                        }
                    ]
                })
            }
        ]
    }


# ============================================================================
# TEST SUITE 1: 3-LAYER FILTERING (github_client.py)
# ============================================================================

class TestThreeLayerFiltering:
    """Tests for the 3-layer filtering system in github_client.py"""

    def test_filter_mixed_files_valid_and_invalid(self, sample_files_mixed):
        """
        Caso A: Test filtering with mixed valid and invalid files.
        Should only return files that pass all 3 layers:
        - Not excluded by extension (.lock, .log, .map)
        - Not in excluded folders (node_modules/, __pycache__/, dist/)
        - In whitelist (.py, .js, etc.)
        """
        # Apply the 3-layer filter
        result = github_client._apply_three_layer_filter(sample_files_mixed)
        
        # Expected valid files
        expected_valid = [
            "src/app.py",
            "src/utils.js",
            "api/users.py",
            "services/order_service.py"
        ]
        
        # Assertions
        assert len(result) == 4, f"Expected 4 valid files, got {len(result)}"
        assert set(result) == set(expected_valid), f"Mismatch in filtered files"
        
        # Verify excluded files are NOT in result
        assert "yarn.lock" not in result, ".lock files should be excluded"
        assert "debug.log" not in result, ".log files should be excluded"
        assert "build/app.min.js.map" not in result, ".map files should be excluded"
        assert "node_modules/express/index.js" not in result, "node_modules/ should be excluded"
        assert "__pycache__/cache.pyc" not in result, "__pycache__/ should be excluded"
        assert "dist/bundle.js" not in result, "dist/ should be excluded"
        assert ".venv/lib/python3.9/site.py" not in result, ".venv/ should be excluded"

    def test_filter_all_files_excluded_edge_case(self, sample_files_all_excluded):
        """
        Caso B (Edge Case): Test when ALL files are excluded after filtering.
        Should return empty list.
        """
        # Apply the 3-layer filter
        result = github_client._apply_three_layer_filter(sample_files_all_excluded)
        
        # Assertions
        assert len(result) == 0, "Expected empty list when all files are excluded"
        assert result == [], "Result should be an empty list"

    @patch('github_client.requests.get')
    def test_list_valid_files_no_valid_files_raises_exception(
        self, mock_get, mock_repo, mock_github_token, sample_files_all_excluded
    ):
        """
        Caso B (Exception): Test that NoValidFilesError is raised when no valid files remain.
        """
        # Mock GitHub API response with only excluded files
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tree": [
                {"type": "blob", "path": path}
                for path in sample_files_all_excluded
            ],
            "truncated": False
        }
        mock_get.return_value = mock_response
        
        # Should raise NoValidFilesError
        with pytest.raises(github_client.NoValidFilesError) as exc_info:
            github_client.list_valid_files(mock_repo, mock_github_token)
        
        # Verify exception message
        assert "No se encontraron archivos válidos" in str(exc_info.value)
        assert mock_repo in str(exc_info.value)

    @patch('github_client.requests.get')
    def test_list_python_files_with_filtering(
        self, mock_get, mock_repo, mock_github_token
    ):
        """
        Test list_python_files applies 3-layer filtering correctly.
        """
        # Mock GitHub API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tree": [
                {"type": "blob", "path": "src/app.py"},
                {"type": "blob", "path": "tests/test_app.py"},
                {"type": "blob", "path": "__pycache__/app.pyc"},
                {"type": "blob", "path": ".venv/lib/site.py"},
                {"type": "blob", "path": "requirements.txt.lock"},
            ],
            "truncated": False
        }
        mock_get.return_value = mock_response
        
        # Call function
        result = github_client.list_python_files(mock_repo, mock_github_token)
        
        # Assertions
        assert len(result) == 2, "Should return only valid Python files"
        assert "src/app.py" in result
        assert "tests/test_app.py" in result
        assert "__pycache__/app.pyc" not in result
        assert ".venv/lib/site.py" not in result

    def test_should_exclude_by_extension(self):
        """Test extension exclusion logic."""
        # Should be excluded
        assert github_client._should_exclude_by_extension("yarn.lock") is True
        assert github_client._should_exclude_by_extension("debug.log") is True
        assert github_client._should_exclude_by_extension("app.min.js") is True
        assert github_client._should_exclude_by_extension("style.min.css") is True
        assert github_client._should_exclude_by_extension("bundle.js.map") is True
        assert github_client._should_exclude_by_extension("logo.png") is True
        assert github_client._should_exclude_by_extension("doc.pdf") is True
        
        # Should NOT be excluded (package-lock.json ends with .json, not .lock)
        assert github_client._should_exclude_by_extension("app.py") is False
        assert github_client._should_exclude_by_extension("script.js") is False
        assert github_client._should_exclude_by_extension("config.json") is False
        assert github_client._should_exclude_by_extension("package-lock.json") is False

    def test_should_exclude_by_folder(self):
        """Test folder exclusion logic."""
        # Should be excluded
        assert github_client._should_exclude_by_folder("node_modules/package/index.js") is True
        assert github_client._should_exclude_by_folder("dist/bundle.js") is True
        assert github_client._should_exclude_by_folder("__pycache__/cache.pyc") is True
        assert github_client._should_exclude_by_folder(".venv/lib/site.py") is True
        assert github_client._should_exclude_by_folder("build/output.js") is True
        assert github_client._should_exclude_by_folder(".git/config") is True
        
        # Should NOT be excluded
        assert github_client._should_exclude_by_folder("src/app.py") is False
        assert github_client._should_exclude_by_folder("api/users.py") is False
        assert github_client._should_exclude_by_folder("services/order_service.py") is False

    def test_is_whitelisted_extension(self):
        """Test whitelist extension logic."""
        # Should be whitelisted
        assert github_client._is_whitelisted_extension("app.py") is True
        assert github_client._is_whitelisted_extension("script.js") is True
        assert github_client._is_whitelisted_extension("component.tsx") is True
        assert github_client._is_whitelisted_extension("config.yaml") is True
        assert github_client._is_whitelisted_extension("data.json") is True
        assert github_client._is_whitelisted_extension("README.md") is True
        assert github_client._is_whitelisted_extension("main.go") is True
        
        # Should NOT be whitelisted
        assert github_client._is_whitelisted_extension("image.png") is False
        assert github_client._is_whitelisted_extension("archive.zip") is False
        assert github_client._is_whitelisted_extension("font.woff") is False


# ============================================================================
# TEST SUITE 2: HTML COLLAPSIBLE FORMAT (report_formatter.py)
# ============================================================================

class TestHTMLCollapsibleFormat:
    """Tests for HTML collapsible sections in report_formatter.py"""

    def test_multi_vulnerability_report_structure(self, sample_multi_vulnerability_findings):
        """
        Caso A: Test report with multiple concurrent vulnerabilities.
        Should generate proper HTML structure with:
        - 🔴 Bloqueantes (2)
        - ⚠️ Advertencias (1)
        - 💡 Sugerencias (0)
        """
        # Generate report
        report = report_formatter.format_report(sample_multi_vulnerability_findings)
        
        # Assertions for structure
        assert "## 🔍 PR Sentinel — Auditoría Automática" in report
        
        # Check Blockers section
        assert "### 🔴 Bloqueantes Críticos (2)" in report
        assert "api/users.py" in report
        assert "api/analytics.py" in report
        assert "ADR-002" in report
        assert "ADR-001" in report
        
        # Check Warnings section
        assert "### ⚠️ Advertencias (1)" in report
        assert "services/payment_service.py" in report
        assert "ADR-003" in report
        
        # Check Suggestions section (empty)
        assert "### 💡 Sugerencias de Mejora (0)" in report
        assert "✅ **Sin sugerencias detectadas**" in report
        
        # Verify tables are present
        assert "| Severidad | Descripción | Archivo | Línea | ADR |" in report
        assert report.count("| Severidad | Descripción | Archivo | Línea | ADR |") == 2  # Blockers and Warnings tables
        
        # Verify collapsible suggested_fix sections
        assert "<details>" in report
        assert "<summary>🔧 Ver sugerencia de Fix</summary>" in report
        assert "```python" in report

    def test_empty_suggestions_section_renders_correctly(self, sample_empty_suggestions_findings):
        """
        Caso B: Test that empty suggestions section renders with proper message.
        Should show "✅ Sin sugerencias detectadas" instead of omitting the section.
        """
        # Generate report
        report = report_formatter.format_report(sample_empty_suggestions_findings)
        
        # Assertions
        assert "### 💡 Sugerencias de Mejora (0)" in report
        assert "✅ **Sin sugerencias detectadas**" in report
        
        # Verify section is not omitted
        assert report.count("###") == 3  # Should have 3 sections: Blockers, Warnings, Suggestions

    def test_severity_badges_rendered_correctly(self, sample_multi_vulnerability_findings):
        """
        Test that severity badges are rendered with proper HTML styling.
        """
        report = report_formatter.format_report(sample_multi_vulnerability_findings)
        
        # Check for HTML badge elements
        assert '<span style="background-color: #d73a4a' in report  # Blocker badge
        assert '🔴 CRÍTICO</span>' in report
        assert '<span style="background-color: #fbca04' in report  # Warning badge
        assert '⚠️ ADVERTENCIA</span>' in report

    def test_suggested_fix_collapsible_details(self):
        """
        Test that suggested_fix is rendered in collapsible <details> blocks.
        """
        findings = {
            "blockers": [
                {
                    "description": "Test issue",
                    "file": "test.py",
                    "line": "10",
                    "adr_reference": "ADR-001",
                    "suggested_fix": "def fixed_function():\n    return True"
                }
            ],
            "warnings": [],
            "suggestions": []
        }
        
        report = report_formatter.format_report(findings)
        
        # Verify collapsible structure
        assert "<details>" in report
        assert "<summary>🔧 Ver sugerencia de Fix</summary>" in report
        assert "```python" in report
        assert "def fixed_function():" in report
        assert "</details>" in report

    def test_report_without_suggested_fix(self):
        """
        Test that findings without suggested_fix don't have collapsible sections.
        """
        findings = {
            "blockers": [
                {
                    "description": "Test issue",
                    "file": "test.py",
                    "line": "10",
                    "adr_reference": "ADR-001"
                    # No suggested_fix
                }
            ],
            "warnings": [],
            "suggestions": []
        }
        
        report = report_formatter.format_report(findings)
        
        # Should have table row but no collapsible details
        assert "Test issue" in report
        assert "test.py" in report
        # Should not have details/summary tags for this finding
        lines = report.split('\n')
        finding_line_idx = next(i for i, line in enumerate(lines) if 'Test issue' in line)
        # Check next few lines don't have <details>
        next_lines = '\n'.join(lines[finding_line_idx:finding_line_idx+3])
        assert "<details>" not in next_lines

    def test_all_sections_empty(self):
        """
        Test report generation when all sections are empty.
        """
        findings = {
            "blockers": [],
            "warnings": [],
            "suggestions": []
        }
        
        report = report_formatter.format_report(findings)
        
        # All sections should show "Sin X detectados"
        assert "✅ **Sin bloqueantes detectados**" in report
        assert "✅ **Sin advertencias detectadas**" in report
        assert "✅ **Sin sugerencias detectadas**" in report
        
        # Counts should be 0
        assert "(0)" in report
        assert report.count("(0)") == 3


# ============================================================================
# TEST SUITE 3: MULTI-ERROR LLM RESPONSE (llm_reasoner.py)
# ============================================================================

class TestMultiErrorLLMResponse:
    """Tests for multi-error parsing in llm_reasoner.py"""

    @patch('llm_reasoner.requests.post')
    def test_llm_parses_multiple_concurrent_errors(
        self, mock_post, sample_llm_multi_error_response, mock_api_key
    ):
        """
        Caso A: Test that call_llm() correctly parses multiple concurrent errors
        across different files without truncating or stopping at first error.
        """
        # Mock IAM token request
        mock_iam_response = Mock()
        mock_iam_response.status_code = 200
        mock_iam_response.json.return_value = {"access_token": "mock_token"}
        
        # Mock watsonx API response with multi-error JSON
        mock_watsonx_response = Mock()
        mock_watsonx_response.status_code = 200
        mock_watsonx_response.json.return_value = sample_llm_multi_error_response
        
        # Configure mock to return different responses based on URL
        def side_effect(*args, **kwargs):
            url = args[0] if args else kwargs.get('url', '')
            if 'iam.cloud.ibm.com' in url:
                return mock_iam_response
            else:
                return mock_watsonx_response
        
        mock_post.side_effect = side_effect
        
        # Set environment variables
        with patch.dict('os.environ', {
            'WATSONX_PROJECT_ID': 'test-project-id',
            'WATSONX_MODEL_ID': 'ibm/granite-3-8b-instruct',
            'WATSONX_URL': 'https://us-south.ml.cloud.ibm.com'
        }):
            # Call the function
            prompt = "Test prompt"
            result = llm_reasoner.call_llm(prompt, mock_api_key)
        
        # Assertions - verify ALL errors are parsed
        assert isinstance(result, dict)
        assert "blockers" in result
        assert "warnings" in result
        assert "suggestions" in result
        
        # Check blockers - should have 3 items from different files
        assert len(result["blockers"]) == 3, "Should parse all 3 blocker errors"
        blocker_files = [b["file"] for b in result["blockers"]]
        assert "api/users.py" in blocker_files
        assert "api/analytics.py" in blocker_files
        assert "api/admin.py" in blocker_files
        
        # Check warnings - should have 1 item
        assert len(result["warnings"]) == 1
        assert result["warnings"][0]["file"] == "api/users.py"
        
        # Check suggestions - should have 1 item
        assert len(result["suggestions"]) == 1
        assert result["suggestions"][0]["file"] == "api/analytics.py"
        
        # Verify no truncation - all ADR references present
        adr_refs = [b["adr_reference"] for b in result["blockers"]]
        assert "ADR-002" in adr_refs
        assert "ADR-001" in adr_refs

    @patch('llm_reasoner.requests.post')
    def test_llm_handles_multiple_files_in_blockers(self, mock_post, mock_api_key):
        """
        Test that multiple files with blockers are all captured in the response.
        """
        # Mock response with errors in 4 different files
        multi_file_response = {
            "results": [
                {
                    "generated_text": json.dumps({
                        "blockers": [
                            {"description": "Error 1", "file": "api/users.py", "line": "10", "adr_reference": "ADR-002"},
                            {"description": "Error 2", "file": "api/orders.py", "line": "20", "adr_reference": "ADR-002"},
                            {"description": "Error 3", "file": "api/products.py", "line": "30", "adr_reference": "ADR-001"},
                            {"description": "Error 4", "file": "api/analytics.py", "line": "40", "adr_reference": "ADR-003"},
                        ],
                        "warnings": [],
                        "suggestions": []
                    })
                }
            ]
        }
        
        # Mock IAM and watsonx responses
        mock_iam = Mock()
        mock_iam.json.return_value = {"access_token": "token"}
        mock_watsonx = Mock()
        mock_watsonx.json.return_value = multi_file_response
        
        def side_effect(*args, **kwargs):
            url = args[0] if args else kwargs.get('url', '')
            return mock_iam if 'iam.cloud.ibm.com' in url else mock_watsonx
        
        mock_post.side_effect = side_effect
        
        with patch.dict('os.environ', {'WATSONX_PROJECT_ID': 'test-id'}):
            result = llm_reasoner.call_llm("test", mock_api_key)
        
        # Verify all 4 files are captured
        assert len(result["blockers"]) == 4
        files = [b["file"] for b in result["blockers"]]
        assert "api/users.py" in files
        assert "api/orders.py" in files
        assert "api/products.py" in files
        assert "api/analytics.py" in files

    def test_extract_json_from_llm_response(self):
        """
        Test _extract_json function handles various response formats.
        """
        # Test clean JSON
        clean_json = '{"blockers": [], "warnings": [], "suggestions": []}'
        result = llm_reasoner._extract_json(clean_json)
        assert isinstance(result, dict)
        assert "blockers" in result
        
        # Test JSON with markdown code blocks
        markdown_json = '```json\n{"blockers": [], "warnings": [], "suggestions": []}\n```'
        result = llm_reasoner._extract_json(markdown_json)
        assert isinstance(result, dict)
        
        # Test JSON with surrounding text
        text_with_json = 'Here is the analysis:\n{"blockers": [{"description": "test", "file": "test.py", "line": "1", "adr_reference": "ADR-001"}], "warnings": [], "suggestions": []}\nEnd of analysis'
        result = llm_reasoner._extract_json(text_with_json)
        assert isinstance(result, dict)
        assert len(result["blockers"]) == 1

    def test_sanitize_and_fill_keys(self):
        """
        Test that sanitize_and_fill_keys ensures all required keys exist.
        """
        # Test with missing keys
        incomplete = {"blockers": []}
        result = llm_reasoner.sanitize_and_fill_keys(incomplete)
        assert "warnings" in result
        assert "suggestions" in result
        assert isinstance(result["warnings"], list)
        assert isinstance(result["suggestions"], list)
        
        # Test with non-dict input
        result = llm_reasoner.sanitize_and_fill_keys(None)
        assert isinstance(result, dict)
        assert all(k in result for k in ["blockers", "warnings", "suggestions"])
        
        # Test with invalid list values
        invalid = {"blockers": "not a list", "warnings": None, "suggestions": []}
        result = llm_reasoner.sanitize_and_fill_keys(invalid)
        assert isinstance(result["blockers"], list)
        assert isinstance(result["warnings"], list)

    def test_validate_response_structure(self):
        """
        Test response structure validation.
        """
        # Valid structure
        valid = {
            "blockers": [
                {"description": "test", "file": "test.py", "line": "1", "adr_reference": "ADR-001"}
            ],
            "warnings": [],
            "suggestions": []
        }
        assert llm_reasoner.validate_response_structure(valid) is True
        
        # Invalid - missing key
        invalid_missing_key = {"blockers": [], "warnings": []}
        assert llm_reasoner.validate_response_structure(invalid_missing_key) is False
        
        # Invalid - wrong type
        invalid_type = {"blockers": "not a list", "warnings": [], "suggestions": []}
        assert llm_reasoner.validate_response_structure(invalid_type) is False
        
        # Invalid - missing required field in item
        invalid_item = {
            "blockers": [{"description": "test"}],  # Missing file, line, adr_reference
            "warnings": [],
            "suggestions": []
        }
        assert llm_reasoner.validate_response_structure(invalid_item) is False

    @patch('llm_reasoner.requests.post')
    def test_llm_retry_mechanism_on_parse_failure(self, mock_post, mock_api_key):
        """
        Test that LLM retries with simplified prompt when initial parse fails.
        """
        # First call returns invalid JSON, second call returns valid JSON
        mock_iam = Mock()
        mock_iam.json.return_value = {"access_token": "token"}
        
        mock_invalid = Mock()
        mock_invalid.json.return_value = {
            "results": [{"generated_text": "This is not valid JSON at all"}]
        }
        
        mock_valid = Mock()
        mock_valid.json.return_value = {
            "results": [
                {
                    "generated_text": json.dumps({
                        "blockers": [{"description": "test", "file": "test.py", "line": "1", "adr_reference": "ADR-001"}],
                        "warnings": [],
                        "suggestions": []
                    })
                }
            ]
        }
        
        call_count = [0]
        def side_effect(*args, **kwargs):
            url = args[0] if args else kwargs.get('url', '')
            if 'iam.cloud.ibm.com' in url:
                return mock_iam
            else:
                call_count[0] += 1
                return mock_invalid if call_count[0] == 1 else mock_valid
        
        mock_post.side_effect = side_effect
        
        with patch.dict('os.environ', {'WATSONX_PROJECT_ID': 'test-id'}):
            result = llm_reasoner.call_llm("test", mock_api_key)
        
        # Should have retried and succeeded
        assert isinstance(result, dict)
        assert len(result["blockers"]) == 1
        # Verify watsonx was called twice (initial + retry)
        watsonx_calls = [call for call in mock_post.call_args_list if 'ml.cloud.ibm.com' in str(call)]
        assert len(watsonx_calls) == 2


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegrationScenarios:
    """Integration tests combining multiple components"""

    @patch('github_client.requests.get')
    def test_end_to_end_filtering_and_reporting(self, mock_get, mock_repo, mock_github_token):
        """
        Integration test: Filter files from GitHub API and generate report.
        """
        # Mock GitHub API with mixed files
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tree": [
                {"type": "blob", "path": "api/users.py"},
                {"type": "blob", "path": "api/orders.py"},
                {"type": "blob", "path": "node_modules/package/index.js"},
                {"type": "blob", "path": "yarn.lock"},
            ],
            "truncated": False
        }
        mock_get.return_value = mock_response
        
        # Get filtered files
        valid_files = github_client.list_valid_files(mock_repo, mock_github_token)
        
        # Should only have the 2 API files (yarn.lock and node_modules excluded)
        assert len(valid_files) == 2
        assert "api/users.py" in valid_files
        assert "api/orders.py" in valid_files
        
        # Create findings for these files
        findings = {
            "blockers": [
                {
                    "description": "Missing auth in users endpoint",
                    "file": "api/users.py",
                    "line": "10",
                    "adr_reference": "ADR-002"
                },
                {
                    "description": "Missing auth in orders endpoint",
                    "file": "api/orders.py",
                    "line": "15",
                    "adr_reference": "ADR-002"
                }
            ],
            "warnings": [],
            "suggestions": []
        }
        
        # Generate report
        report = report_formatter.format_report(findings)
        
        # Verify report contains both files
        assert "api/users.py" in report
        assert "api/orders.py" in report
        assert "### 🔴 Bloqueantes Críticos (2)" in report


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

# Made with Bob
