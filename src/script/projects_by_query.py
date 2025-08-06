import sys
import logging
from util.github_utils import GithubUtils
import pandas as pd
import os
import subprocess
from datetime import datetime
import re
import argparse
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def get_dependabot_alerts_by_severity(repo_owner, repo_name, github_token):
    """Get open Dependabot alerts grouped by severity"""
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    severity_counts = {
        'Critical': 0,
        'High': 0,
        'Moderate': 0,
        'Low': 0,
        'Excluded': 0,
        'Total': 0
    }
    
    try:
        # Get all open Dependabot alerts
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/dependabot/alerts?state=open"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            alerts = response.json()
            severity_counts['Total'] = len(alerts)
            
            # Count alerts by severity
            for alert in alerts:
                package_name = alert.get('dependency', {}).get('package', {}).get('name', '')
                excluded_packages = ['com.h2database:h2', 'org.liquibase:liquibase-core']  # Add your excluded package names here
                if package_name in excluded_packages:
                    severity_counts['Excluded'] += 1
            
                severity = alert.get('security_advisory', {}).get('severity', '').lower()
                if severity == 'critical':
                    severity_counts['Critical'] += 1
                elif severity == 'high':
                    severity_counts['High'] += 1
                elif severity == 'medium':
                    severity_counts['Moderate'] += 1
                elif severity == 'low':
                    severity_counts['Low'] += 1

        elif response.status_code == 404:
            logging.info(f"Dependabot alerts not available for {repo_name} (404)")
        elif response.status_code == 403:
            logging.warning(f"Access denied for Dependabot alerts on {repo_name} (403)")
        else:
            logging.warning(f"Error fetching Dependabot alerts for {repo_name}: {response.status_code}")
            
    except Exception as e:
        logging.warning(f"Could not fetch Dependabot alerts for {repo_name}: {e}")
    
    return severity_counts

def main(query_string, download, include_security):
    
    if not query_string:
        query_string = "topic:portal-core-team -topic:archive-team -topic:not-deployed language:Java archived:false"
        logging.info(f"No query string provided. Using default: {query_string}")

    projects = GithubUtils.search(query_string)
    
    # Get GitHub token for security API calls
    github_token = os.getenv('GITHUB_TOKEN')
    if include_security and not github_token:
        logging.warning("GITHUB_TOKEN environment variable not set. Security information will not be included.")
        include_security = False

    data = []
    for repo in projects:
        repo_data = {
            'name': repo.get('name', ''),
            'url': repo.get('html_url', ''),
            'topics': ', '.join(repo.get('topics', [])),
            'num_topics': len(repo.get('topics', [])),
            'language': repo.get('language', ''),
            'updated_at': repo.get('updated_at', ''),
            'pushed_at': repo.get('pushed_at', '')
        }
        
        if include_security:
            # Extract owner and repo name from URL
            repo_full_name = repo.get('full_name', '')
            if '/' in repo_full_name:
                repo_owner, repo_name = repo_full_name.split('/', 1)
                security_info = get_dependabot_alerts_by_severity(repo_owner, repo_name, github_token)
                repo_data.update(security_info)
                
                logging.info(f"Dependabot alerts for {repo_name}: {security_info}")
        
        data.append(repo_data)

    df = pd.DataFrame(data)
    base_dir = os.path.expanduser('~/Workspace/analysis')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # Replace only characters not valid in Mac file names: /, :, and optionally control chars
    safe_query = re.sub(r'[:/\s]', '_', query_string)
    output_file = os.path.join(base_dir, f'{timestamp}_{safe_query}.xlsx')
    df.to_excel(output_file, index=False)
    logging.info(f"Saved project names and topics to {output_file}")

    if download:
        base_dir = os.path.expanduser('~/Workspace/all')
        for repo in projects:
            repo_name = repo.get('name', '')
            repo_url = repo.get('ssh_url', '')
            if not repo_name or not repo_url:
                continue
            repo_dir = os.path.join(base_dir, repo_name)
            if not os.path.exists(repo_dir):
                logging.info(f"Cloning {repo_url} into {repo_dir}")
                subprocess.run(['git', 'clone', repo_url, repo_dir])
            else:
                logging.info(f"Repository {repo_name} already exists at {repo_dir}, pulling latest changes")
                subprocess.run(['git', '-C', repo_dir, 'pull'])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search and optionally download GitHub projects by query.")
    parser.add_argument('-q', '--query', type=str, default="topic:portal-core-team -topic:archive-team -topic:not-deployed language:Java archived:false", help='GitHub search query string')
    parser.add_argument('-d', '--download', action='store_true', default=False, help='Download (clone) the repositories')
    parser.add_argument('-s', '--security', action='store_true', default=False, help='Include Dependabot security alerts by severity (requires GITHUB_TOKEN)')
    args = parser.parse_args()

    logging.info(f"Arguments: {args}")

    main(args.query, args.download, args.security)