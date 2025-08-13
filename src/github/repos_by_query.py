#!/usr/bin/env python3
"""
GitHub Projects Query Tool

Searches GitHub repositories based on query criteria and optionally:
- Downloads/clones repositories locally
- Includes security vulnerability information
- Exports results to Excel spreadsheet
"""

import argparse
import logging
import os
import re
import subprocess
from datetime import datetime
from typing import Dict, List
import pandas as pd
from dotenv import load_dotenv
from ..util.github_rest_api import GithubUtils
from ..config.logging_config import setup_logging

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
setup_logging()

DEFAULT_QUERY = "topic:portal-core-team -topic:archive-team -topic:not-deployed language:Java archived:false"
EXCLUDED_PACKAGES = ['com.h2database:h2', 'org.liquibase:liquibase-core']

def get_security_alerts(repo_owner: str, repo_name: str) -> Dict:
    """Get Dependabot security alerts grouped by severity level."""
    severity_counts = {'Critical': 0, 'High': 0, 'Moderate': 0, 'Low': 0, 'Excluded': 0, 'Total': 0}
    
    try:
        response = GithubUtils.get_dependabot_alerts(repo_owner, repo_name)
        
        if response.status_code == 200:
            alerts = response.json()
            severity_counts['Total'] = len(alerts)
            
            severity_map = {'critical': 'Critical', 'high': 'High', 'medium': 'Moderate', 'low': 'Low'}
            
            for alert in alerts:
                package_name = alert.get('dependency', {}).get('package', {}).get('name', '')
                
                if package_name in EXCLUDED_PACKAGES:
                    severity_counts['Excluded'] += 1
                    continue
                
                severity = alert.get('security_advisory', {}).get('severity', '').lower()
                if severity in severity_map:
                    severity_counts[severity_map[severity]] += 1
                    
    except Exception as e:
        logging.warning(f"Could not fetch alerts for {repo_name}: {e}")
    
    logging.info(f"Security alerts for {repo_name}: {severity_counts}")
    return severity_counts


def cleanup_old_repos(projects: List[Dict], base_dir: str) -> None:
    """Delete repositories not in current projects list."""
    if not os.path.exists(base_dir):
        return
        
    current_names = {repo.get('name') for repo in projects if repo.get('name')}
    existing_dirs = [d for d in os.listdir(base_dir) 
                    if os.path.isdir(os.path.join(base_dir, d)) and not d.startswith('.')]
    
    for dir_name in existing_dirs:
        if dir_name not in current_names:
            logging.info(f"Deleting old repository: {dir_name}")
            subprocess.run(['rm', '-rf', os.path.join(base_dir, dir_name)])


def clone_or_update_repo(repo: Dict, base_dir: str) -> None:
    """Clone repository or update if exists."""
    repo_name = repo.get('name')
    repo_url = repo.get('ssh_url')
    if not repo_name or not repo_url:
        return
        
    repo_dir = os.path.join(base_dir, repo_name)
    
    if not os.path.exists(repo_dir):    
        logging.info(f"Cloning new repository: {repo_name}")
        subprocess.run(['git', 'clone', repo_url, repo_dir])
    else:
        logging.info(f"Updating existing repository: {repo_name}")
        subprocess.run(['git', '-C', repo_dir, 'pull'])


def save_results(data: List[Dict], query_string: str) -> None:
    """Save results to timestamped Excel file."""
    analysis_dir = os.getenv('ANALYSIS_DIR')
    if not analysis_dir:
        raise ValueError("ANALYSIS_DIR environment variable is required")
        
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_query = re.sub(r'[:/\s]', '_', query_string)
    output_file = os.path.join(os.path.expanduser(analysis_dir), f'{timestamp}_{safe_query}.xlsx')
    
    pd.DataFrame(data).to_excel(output_file, index=False)
    logging.info(f"Saved results to {output_file}")


def main(query_string: str, download: bool, include_security: bool) -> None:
    """Main function to search and analyze GitHub repositories."""
    # Validate environment variables
    if not os.getenv('GITHUB_TOKEN'):
        raise ValueError("GITHUB_TOKEN environment variable is required")
    
    repos_dir = os.getenv('REPOS_DIR') if download else None
    if download and not repos_dir:
        raise ValueError("REPOS_DIR environment variable is required for downloads")
    
    query = query_string or DEFAULT_QUERY
    projects = GithubUtils.search(query)
    logging.info(f"Found {len(projects)} projects")
    
    if download:
        repos_dir = os.path.expanduser(repos_dir)
        cleanup_old_repos(projects, repos_dir)
    
    data = []
    for repo in projects:
        repo_data = {
            'name': repo.get('name', ''),
            'url': repo.get('html_url', ''),
            'topics': ', '.join(repo.get('topics', [])),
            'num_topics': len(repo.get('topics', [])),
            'language': repo.get('language', ''),
            'default_branch': repo.get('default_branch', ''),
            'updated_at': repo.get('updated_at', ''),
            'pushed_at': repo.get('pushed_at', '')
        }
        
        if include_security:
            repo_full_name = repo.get('full_name', '')
            if '/' in repo_full_name:
                repo_owner, repo_name = repo_full_name.split('/', 1)
                security_info = get_security_alerts(repo_owner, repo_name)
                repo_data.update(security_info)
        
        if download:
            clone_or_update_repo(repo, repos_dir)
        
        data.append(repo_data)
    
    save_results(data, query)
    logging.info("Analysis complete")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search and analyze GitHub repositories")
    parser.add_argument('-q', '--query', help='GitHub search query string')
    parser.add_argument('-d', '--download', action='store_true', help='Clone repositories locally')
    parser.add_argument('-s', '--security', action='store_true', help='Include security vulnerability counts')
    
    args = parser.parse_args()
    
    try:
        main(args.query, args.download, args.security)
    except Exception as e:
        logging.error(f"Script failed: {e}")
        raise