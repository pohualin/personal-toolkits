import sys
import logging
from util.github_utils import GithubUtils
import pandas as pd
import os
import subprocess
from datetime import datetime
import re
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def main(query_string, download):
    
    if not query_string:
        query_string = "topic:portal-core-team -topic:archive-team -topic:not-deployed language:Java archived:false"
        logging.info(f"No query string provided. Using default: {query_string}")

    projects = GithubUtils.search(query_string)

    data = [
        {
            'name': repo.get('name', ''),
            'url': repo.get('html_url', ''),
            'topics': ', '.join(repo.get('topics', [])),
            'num_topics': len(repo.get('topics', [])),
            'language': repo.get('language', ''),
            'updated_at': repo.get('updated_at', ''),
            'pushed_at': repo.get('pushed_at', '')
        }
        for repo in projects
    ]

    df = pd.DataFrame(data)
    analysis_dir = os.getenv('ANALYSIS_DIR')
    if not analysis_dir:
        raise ValueError("ANALYSIS_DIR environment variable is required")
    base_dir = os.path.expanduser(analysis_dir)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # Replace only characters not valid in Mac file names: /, :, and optionally control chars
    safe_query = re.sub(r'[:/\s]', '_', query_string)
    output_file = os.path.join(base_dir, f'{timestamp}_{safe_query}.xlsx')
    df.to_excel(output_file, index=False)
    logging.info(f"Saved project names and topics to {output_file}")

    if download:
        repos_dir = os.getenv('REPOS_DIR')
        if not repos_dir:
            raise ValueError("REPOS_DIR environment variable is required")
        base_dir = os.path.expanduser(repos_dir)
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
    args = parser.parse_args()

    logging.info(f"Arguments: {args}")

    main(args.query, args.download)