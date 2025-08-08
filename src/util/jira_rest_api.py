import os
import requests
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class JiraRestApi:
    """Utility class for Jira REST API operations"""
    
    def __init__(self):
        self.base_url = os.getenv("JIRA_BASE_URL")
        self.api_token = os.getenv("JIRA_API_TOKEN")
        
        if not self.api_token:
            raise ValueError("JIRA_API_TOKEN environment variable is required")
        if not self.base_url:
            raise ValueError("JIRA_BASE_URL environment variable is required") 
               
        self.headers = {
            "Authorization": f"Basic {self.api_token}",
            "Accept": "application/json"
        }
    
    def search_issues(self, jql: str) -> Dict:
        """Search for issues using JQL query"""
        url = f"{self.base_url}/rest/api/3/search"
        params = {"jql": jql}
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_issue(self, issue_key: str) -> Dict:
        """Get a specific issue by key"""
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_filter(self, filter_id: str) -> Dict:
        """Get filter details by ID"""
        url = f"{self.base_url}/rest/api/3/filter/{filter_id}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def count_issues(self, jql: str) -> int:
        """Count issues matching JQL query"""
        data = self.search_issues(jql)
        return data.get("total", 0)