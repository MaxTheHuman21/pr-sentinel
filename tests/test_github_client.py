"""
Unit tests for github_client module.
Uses unittest.mock to simulate GitHub API responses without making real HTTP calls.
"""

import unittest
import base64
from unittest.mock import patch, Mock
from requests.exceptions import HTTPError, ConnectionError

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from github_client import (
    get_pr_diff,
    get_repo_file,
    list_python_files,
    post_pr_comment
)


class TestGetPRDiff(unittest.TestCase):
    """Tests for get_pr_diff function"""
    
    @patch('github_client.requests.get')
    def test_happy_path(self, mock_get):
        """Test successful PR diff retrieval with multiple files"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'filename': 'file1.py',
                'status': 'modified',
                'patch': '@@ -1,3 +1,3 @@\n-old line\n+new line'
            },
            {
                'filename': 'file2.py',
                'status': 'added',
                'patch': '@@ -0,0 +1,5 @@\n+new file content'
            }
        ]
        mock_get.return_value = mock_response
        
        result = get_pr_diff('owner/repo', 123, 'fake_token')
        
        self.assertIn('old line', result)
        self.assertIn('new line', result)
        self.assertIn('new file content', result)
        mock_get.assert_called_once()
    
    @patch('github_client.requests.get')
    def test_filters_removed_files(self, mock_get):
        """Test that removed files are filtered out (v3.0 critical filter)"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'filename': 'kept.py',
                'status': 'modified',
                'patch': '@@ -1,3 +1,3 @@\n-old\n+new'
            },
            {
                'filename': 'deleted.py',
                'status': 'removed',
                'patch': '@@ -1,10 +0,0 @@\n-deleted content'
            }
        ]
        mock_get.return_value = mock_response
        
        result = get_pr_diff('owner/repo', 123, 'fake_token')
        
        self.assertIn('old', result)
        self.assertIn('new', result)
        self.assertNotIn('deleted content', result)
    
    @patch('github_client.requests.get')
    def test_http_404_error(self, mock_get):
        """Test handling of HTTP 404 error"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        with self.assertRaises(HTTPError):
            get_pr_diff('owner/repo', 999, 'fake_token')
    
    @patch('github_client.requests.get')
    def test_connection_error(self, mock_get):
        """Test handling of connection error"""
        mock_get.side_effect = ConnectionError("Network unreachable")
        
        with self.assertRaises(ConnectionError):
            get_pr_diff('owner/repo', 123, 'fake_token')


class TestGetRepoFile(unittest.TestCase):
    """Tests for get_repo_file function"""
    
    @patch('github_client.requests.get')
    def test_happy_path(self, mock_get):
        """Test successful file retrieval and Base64 decoding"""
        content = "def hello():\n    print('Hello, World!')"
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'name': 'test.py',
            'content': encoded_content,
            'encoding': 'base64'
        }
        mock_get.return_value = mock_response
        
        result = get_repo_file('owner/repo', 'src/test.py', 'fake_token')
        
        self.assertEqual(result, content)
        mock_get.assert_called_once()
    
    @patch('github_client.requests.get')
    def test_http_404_error(self, mock_get):
        """Test handling of HTTP 404 error for missing file"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        with self.assertRaises(HTTPError):
            get_repo_file('owner/repo', 'nonexistent.py', 'fake_token')
    
    @patch('github_client.requests.get')
    def test_connection_error(self, mock_get):
        """Test handling of connection error"""
        mock_get.side_effect = ConnectionError("Network unreachable")
        
        with self.assertRaises(ConnectionError):
            get_repo_file('owner/repo', 'src/test.py', 'fake_token')


class TestListPythonFiles(unittest.TestCase):
    """Tests for list_python_files function"""
    
    @patch('github_client.requests.get')
    def test_happy_path(self, mock_get):
        """Test successful listing of Python files"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'tree': [
                {'path': 'src/main.py', 'type': 'blob'},
                {'path': 'tests/test_main.py', 'type': 'blob'},
                {'path': 'README.md', 'type': 'blob'},
                {'path': 'config.json', 'type': 'blob'},
                {'path': 'lib/utils.py', 'type': 'blob'}
            ],
            'truncated': False
        }
        mock_get.return_value = mock_response
        
        result = list_python_files('owner/repo', 'fake_token')
        
        self.assertEqual(len(result), 3)
        self.assertIn('src/main.py', result)
        self.assertIn('tests/test_main.py', result)
        self.assertIn('lib/utils.py', result)
        self.assertNotIn('README.md', result)
        self.assertNotIn('config.json', result)
    
    @patch('github_client.requests.get')
    @patch('builtins.print')
    def test_truncated_warning(self, mock_print, mock_get):
        """Test warning when tree is truncated (FIX v3.0)"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'tree': [
                {'path': 'file1.py', 'type': 'blob'},
                {'path': 'file2.py', 'type': 'blob'}
            ],
            'truncated': True
        }
        mock_get.return_value = mock_response
        
        result = list_python_files('owner/repo', 'fake_token')
        
        self.assertEqual(len(result), 2)
        mock_print.assert_called_with('[WARN] Árbol del repo truncado por GitHub análisis parcial')
    
    @patch('github_client.requests.get')
    def test_http_404_error(self, mock_get):
        """Test handling of HTTP 404 error"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        with self.assertRaises(HTTPError):
            list_python_files('owner/nonexistent', 'fake_token')
    
    @patch('github_client.requests.get')
    def test_connection_error(self, mock_get):
        """Test handling of connection error"""
        mock_get.side_effect = ConnectionError("Network unreachable")
        
        with self.assertRaises(ConnectionError):
            list_python_files('owner/repo', 'fake_token')


class TestPostPRComment(unittest.TestCase):
    """Tests for post_pr_comment function"""
    
    @patch('github_client.requests.post')
    def test_happy_path(self, mock_post):
        """Test successful comment posting (HTTP 201)"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response
        
        result = post_pr_comment('owner/repo', 123, '# Test Comment\nThis is a test.', 'fake_token')
        
        self.assertTrue(result)
        mock_post.assert_called_once()
        
        # Verify the payload
        call_args = mock_post.call_args
        self.assertEqual(call_args[1]['json']['body'], '# Test Comment\nThis is a test.')
    
    @patch('github_client.requests.post')
    def test_http_404_error_returns_false(self, mock_post):
        """Test that HTTP 404 error returns False instead of raising"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = HTTPError("404 Not Found")
        mock_post.return_value = mock_response
        
        result = post_pr_comment('owner/repo', 999, 'Comment', 'fake_token')
        
        self.assertFalse(result)
    
    @patch('github_client.requests.post')
    def test_connection_error_returns_false(self, mock_post):
        """Test that connection error returns False instead of raising"""
        mock_post.side_effect = ConnectionError("Network unreachable")
        
        result = post_pr_comment('owner/repo', 123, 'Comment', 'fake_token')
        
        self.assertFalse(result)
    
    @patch('github_client.requests.post')
    def test_non_201_status_returns_false(self, mock_post):
        """Test that non-201 status codes return False"""
        mock_response = Mock()
        mock_response.status_code = 200  # Success but not 201
        mock_post.return_value = mock_response
        
        result = post_pr_comment('owner/repo', 123, 'Comment', 'fake_token')
        
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()

# Made with Bob and P2
