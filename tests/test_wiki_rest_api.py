import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from src.util.wiki_rest_api import WikiRestApi

class TestWikiRestApi:
    
    @patch.dict(os.environ, {'CONFLUENCE_BASE_URL': 'https://test.atlassian.net/wiki', 'CONFLUENCE_API_TOKEN': 'test_token'})
    def test_init_success(self):
        api = WikiRestApi()
        assert api.base_url == 'https://test.atlassian.net/wiki'
        assert api.api_token == 'test_token'
        assert 'Authorization' in api.headers
    
    @patch.dict(os.environ, {}, clear=True)
    def test_init_missing_token(self):
        with pytest.raises(ValueError, match="CONFLUENCE_API_TOKEN environment variable is required"):
            WikiRestApi()
    
    @patch.dict(os.environ, {'CONFLUENCE_API_TOKEN': 'test_token'}, clear=True)
    def test_init_missing_base_url(self):
        with pytest.raises(ValueError, match="CONFLUENCE_BASE_URL environment variable is required"):
            WikiRestApi()
    
    @patch.dict(os.environ, {'CONFLUENCE_BASE_URL': 'https://test.atlassian.net/wiki', 'CONFLUENCE_API_TOKEN': 'test_token'})
    @patch('src.util.wiki_rest_api.requests.get')
    def test_search(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'results': [{'id': '123', 'title': 'Test Page'}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        api = WikiRestApi()
        result = api.search("space=TEST")
        
        mock_get.assert_called_once()
        assert result == {'results': [{'id': '123', 'title': 'Test Page'}]}
    
    @patch.dict(os.environ, {'CONFLUENCE_BASE_URL': 'https://test.atlassian.net/wiki', 'CONFLUENCE_API_TOKEN': 'test_token'})
    @patch('src.util.wiki_rest_api.requests.get')
    def test_read_page(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'id': '123', 'title': 'Test Page', 'body': {'storage': {'value': '<p>content</p>'}}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        api = WikiRestApi()
        result = api.read_page("123")
        
        mock_get.assert_called_once()
        assert result['id'] == '123'
        assert result['title'] == 'Test Page'
    
    @patch.dict(os.environ, {'CONFLUENCE_BASE_URL': 'https://test.atlassian.net/wiki', 'CONFLUENCE_API_TOKEN': 'test_token'})
    @patch('src.util.wiki_rest_api.requests.post')
    def test_write_page(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {'id': '456', 'title': 'New Page'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        api = WikiRestApi()
        result = api.write_page("TEST", "New Page", "<p>content</p>")
        
        mock_post.assert_called_once()
        assert result['id'] == '456'
        assert result['title'] == 'New Page'
    
    @patch.dict(os.environ, {'CONFLUENCE_BASE_URL': 'https://test.atlassian.net/wiki', 'CONFLUENCE_API_TOKEN': 'test_token'})
    @patch('src.util.wiki_rest_api.requests.put')
    def test_update_page(self, mock_put):
        mock_response = Mock()
        mock_response.json.return_value = {'id': '123', 'title': 'Updated Page', 'version': {'number': 2}}
        mock_response.raise_for_status.return_value = None
        mock_put.return_value = mock_response
        
        api = WikiRestApi()
        result = api.update_page("123", "Updated Page", "<p>updated content</p>", 1)
        
        mock_put.assert_called_once()
        assert result['title'] == 'Updated Page'
        assert result['version']['number'] == 2