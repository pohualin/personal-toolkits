#!/usr/bin/env python3
"""
GitHub Projects Query Tool

Searches GitHub repositories based on query criteria and optionally:
- Downloads/clones repositories locally
- Includes security vulnerability information
- Exports results to Excel spreadsheet

Usage:
    python -m src.github.repos_by_query -q "language:Java" -d -s
"""

import argparse
import logging
import os
import re
import subprocess
from datetime import datetime
from typing import Dict, List
import pandas as pd
import requests
from dotenv import load_dotenv
from ..util.github_utils import GithubUtils
from ..config.logging_config import setup_logging

# Load environment variables from global and module-specific .env files
load_dotenv()  # Global .env
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))  # Module .env

# Setup logging after environment variables are loaded
setup_logging()

# Default GitHub search query for portal-core-team repositories
DEFAULT_QUERY = "topic:portal-core-team -topic:archive-team -topic:not-deployed language:Java archived:false"

# Packages to exclude from security vulnerability counts
EXCLUDED_PACKAGES = ['com.h2database:h2', 'org.liquibase:liquibase-core']

def get_security_alerts(repo_owner: str, repo_name: str, github_token: str) -> Dict:
    """Get Dependabot security alerts grouped by severity level.
    
    Args:
        repo_owner: GitHub repository owner/organization
        repo_name: Repository name
        github_token: GitHub API token for authentication
        
    Returns:
        Dictionary with counts by severity: Critical, High, Moderate, Low, Excluded, Total
    """
    logging.debug(f"Fetching security alerts for {repo_owner}/{repo_name}")
    
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Initialize severity counters
    severity_counts = {'Critical': 0, 'High': 0, 'Moderate': 0, 'Low': 0, 'Excluded': 0, 'Total': 0}
    
    try:
        # Call GitHub Dependabot alerts API
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/dependabot/alerts?state=open"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            alerts = response.json()
            severity_counts['Total'] = len(alerts)
            logging.debug(f"Found {len(alerts)} alerts for {repo_name}")
            
            # Process each alert and categorize by severity
            for alert in alerts:
                package_name = alert.get('dependency', {}).get('package', {}).get('name', '')
                
                # Skip excluded packages (e.g., test dependencies)
                if package_name in EXCLUDED_PACKAGES:
                    severity_counts['Excluded'] += 1
                    continue
                
                # Count alerts by severity level
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
            logging.info(f"Dependabot alerts not available for {repo_name}")
        elif response.status_code == 403:
            logging.warning(f"Access denied for Dependabot alerts on {repo_name}")
        else:
            logging.warning(f"Error fetching alerts for {repo_name}: {response.status_code}")
            
    except Exception as e:
        logging.warning(f"Could not fetch alerts for {repo_name}: {e}")
    
    return severity_counts


def clone_or_update_repo(repo: Dict, base_dir: str) -> None:
    """Clone repository locally or update if it already exists.
    
    Args:
        repo: Repository data from GitHub API
        base_dir: Base directory where repositories should be stored
    """
    repo_name = repo.get('name', '')
    repo_url = repo.get('ssh_url', '')
    if not repo_name or not repo_url:
        return
        
    repo_dir = os.path.join(base_dir, repo_name)
    
    # Clone if directory doesn't exist, otherwise pull latest changes
    if not os.path.exists(repo_dir):
        logging.info(f"Cloning {repo_name}")
        subprocess.run(['git', 'clone', repo_url, repo_dir])
    else:
        logging.info(f"Updating {repo_name}")
        subprocess.run(['git', '-C', repo_dir, 'pull'])


def save_results(data: List[Dict], query_string: str) -> None:
    """Save repository analysis results to timestamped Excel file.
    
    Args:
        data: List of repository data dictionaries
        query_string: GitHub search query used (for filename)
    """
    analysis_dir = os.getenv('ANALYSIS_DIR')
    if not analysis_dir:
        raise ValueError("ANALYSIS_DIR environment variable is required")
        
    # Convert data to DataFrame and create timestamped filename
    df = pd.DataFrame(data)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_query = re.sub(r'[:/\s]', '_', query_string)  # Remove invalid filename characters
    output_file = os.path.join(os.path.expanduser(analysis_dir), f'{timestamp}_{safe_query}.xlsx')
    
    # Export to Excel without row indices
    df.to_excel(output_file, index=False)
    logging.info(f"Saved results to {output_file}")


def main(query_string: str, download: bool, include_security: bool) -> None:
    """Main function to search and analyze GitHub repositories.
    
    Args:
        query_string: GitHub search query (uses default if None)
        download: Whether to clone/update repositories locally
        include_security: Whether to include Dependabot security alerts
    """
    logging.info("Starting GitHub projects analysis")
    logging.info(f"Options: download={download}, security={include_security}")
    
    # Use default query if none provided
    if not query_string:
        query_string = DEFAULT_QUERY
        logging.info(f"Using default query: {query_string}")
    else:
        logging.info(f"Using custom query: {query_string}")

    # Search GitHub repositories using the query
    logging.info("Searching GitHub repositories...")
    projects = GithubUtils.search(query_string)
    logging.info(f"Found {len(projects)} projects")
    
    # Check for GitHub token if security information is requested
    github_token = os.getenv('GITHUB_TOKEN')
    if include_security and not github_token:
        logging.warning("GITHUB_TOKEN not set. Security information will not be included.")
        include_security = False

    # Prepare for repository downloads if requested
    data = []
    repos_dir = None
    if download:
        repos_dir = os.getenv('REPOS_DIR')
        if not repos_dir:
            raise ValueError("REPOS_DIR environment variable is required")
        repos_dir = os.path.expanduser(repos_dir)
        logging.info(f"Repository downloads will be saved to: {repos_dir}")

    # Process each repository
    logging.info("Processing repositories...")
    for i, repo in enumerate(projects, 1):
        repo_name = repo.get('name', '')
        logging.debug(f"Processing {i}/{len(projects)}: {repo_name}")
        # Extract basic repository information
        repo_data = {
            'name': repo.get('name', ''),
            'url': repo.get('html_url', ''),
            'topics': ', '.join(repo.get('topics', [])),  # Convert list to comma-separated string
            'num_topics': len(repo.get('topics', [])),
            'language': repo.get('language', ''),
            'default_branch': repo.get('default_branch', ''),
            'updated_at': repo.get('updated_at', ''),
            'pushed_at': repo.get('pushed_at', '')
        }
        
        # Add security information if requested
        if include_security:
            repo_full_name = repo.get('full_name', '')
            if '/' in repo_full_name:
                repo_owner, repo_name = repo_full_name.split('/', 1)
                logging.debug(f"Fetching security info for {repo_name}")
                security_info = get_security_alerts(repo_owner, repo_name, github_token)
                repo_data.update(security_info)  # Merge security data into repo_data
                if security_info.get('Total', 0) > 0:
                    logging.info(f"{repo_name}: {security_info['Total']} security alerts")
        
        # Clone or update repository if download is enabled
        if download:
            clone_or_update_repo(repo, repos_dir)
        
        data.append(repo_data)

    # Save all collected data to Excel file
    logging.info(f"Analysis complete. Processed {len(data)} repositories")
    save_results(data, query_string)
    logging.info("GitHub projects analysis finished successfully")


if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description="Search and analyze GitHub repositories with optional security scanning and local cloning"
    )
    parser.add_argument(
        '-q', '--query', 
        type=str, 
        help='GitHub search query string (e.g., "language:Java topic:microservice")')
    parser.add_argument(
        '-d', '--download', 
        action='store_true', 
        help='Clone repositories locally or update if they exist (requires REPOS_DIR env var)')
    parser.add_argument(
        '-s', '--security', 
        action='store_true', 
        help='Include Dependabot security vulnerability counts (requires GITHUB_TOKEN env var)')
    
    args = parser.parse_args()
    
    logging.info(f"Starting with arguments: query='{args.query}', download={args.download}, security={args.security}")

    try:
        # Execute main function with parsed arguments
        main(args.query, args.download, args.security)
    except Exception as e:
        logging.error(f"Script failed: {e}")
        raise