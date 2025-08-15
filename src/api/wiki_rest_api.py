import os
import requests
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class WikiRestApi:
    """Utility class for Confluence REST API operations"""
    
    def __init__(self):
        self.base_url = os.getenv("CONFLUENCE_BASE_URL")
        self.api_token = os.getenv("CONFLUENCE_API_TOKEN")
        
        if not self.api_token:
            raise ValueError("CONFLUENCE_API_TOKEN environment variable is required")
        if not self.base_url:
            raise ValueError("CONFLUENCE_BASE_URL environment variable is required")
        
        self.headers = {
            "Authorization": f"Basic {self.api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def search(self, cql: str, limit: int = 25) -> Dict:
        """Search content using CQL (Confluence Query Language)"""
        url = f"{self.base_url}/wiki/rest/api/content/search"
        params = {
            "cql": cql,
            "limit": limit
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def read_page(self, page_id: str, expand: str = "body.storage,version") -> Dict:
        """Read a page by ID"""
        url = f"{self.base_url}/wiki/rest/api/content/{page_id}"
        params = {"expand": expand}
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def write_page(self, space_key: str, title: str, content: str, parent_id: Optional[str] = None) -> Dict:
        """Create a new page using v2 API"""
        url = f"{self.base_url}/wiki/api/v2/pages"
        
        data = {
            "spaceId": space_key,
            "status": "current",
            "title": title,
            "body": {
                "representation": "storage",
                "value": content
            }
        }
        
        if parent_id:
            data["parentId"] = parent_id
        
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()
    
    def update_page(self, page_id: str, title: str, content: str, version: int) -> Dict:
        """Update an existing page"""
        url = f"{self.base_url}/wiki/rest/api/content/{page_id}"
        
        data = {
            "version": {"number": version + 1},
            "title": title,
            "type": "page",
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            }
        }
        
        response = requests.put(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()