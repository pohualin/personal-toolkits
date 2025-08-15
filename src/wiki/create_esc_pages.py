#!/usr/bin/env python3

import argparse
import logging
import sys
from datetime import datetime, timedelta
from typing import Dict
from dotenv import load_dotenv
from ..util.jira_rest_api import JiraRestApi
from ..util.wiki_rest_api import WikiRestApi
from ..config.logging_config import setup_logging

load_dotenv()
setup_logging()

# Parent page ID in Confluence where new pages will be created
PARENT_PAGE_ID = "1892909160"
# Confluence space key where pages will be created
SPACE_KEY = "38371328" 
# Template page ID that contains the base content structure
TEMPLATE_PAGE_ID = "1892909134"

def page_exists(wiki: WikiRestApi, issue_key: str) -> bool:
    """Check if page exists for issue."""
    search_result = wiki.search(f'title ~ "{issue_key}"')
    return len(search_result.get("results", [])) > 0


def get_content(wiki: WikiRestApi, jira: JiraRestApi, issue: Dict) -> str:
    """Generate page content."""
    issue_key = issue.get("key", "")
    fields = issue.get("fields", {})
    summary = fields.get("summary", "")
    
    try:
        template = wiki.read_page(TEMPLATE_PAGE_ID)
        if template:
            return (
                template.get("body", {}).get("storage", {}).get("value", "")
                .replace("{Link to ESC}", f'<ac:structured-macro ac:name="jira" ac:schema-version="1"><ac:parameter ac:name="key">{issue_key}</ac:parameter></ac:structured-macro>')
                .replace("{Describe the issue}", summary)
            )
    except Exception as e:
        logging.warning(f"Template load failed: {e}")
    
    # Fallback content
    status = fields.get("status", {}).get("name", "N/A")
    assignee = fields.get("assignee")
    assignee_name = assignee.get("displayName", "Unassigned") if assignee else "Unassigned"
    
    return f"<h1>{issue_key}</h1><p><strong>Summary:</strong> {summary}</p><p><strong>Status:</strong> {status}</p><p><strong>Assignee:</strong> {assignee_name}</p><p><strong>Link:</strong> <a href=\"{jira.base_url}/browse/{issue_key}\">{issue_key}</a></p>"


def create_page(wiki: WikiRestApi, jira: JiraRestApi, issue: Dict) -> Dict:
    """Create page for issue."""
    issue_key = issue.get("key", "")
    summary = issue.get("fields", {}).get("summary", "")
    
    return wiki.write_page(
        space_key=SPACE_KEY,
        title=f"{issue_key} - {summary}",
        content=get_content(wiki, jira, issue),
        parent_id=PARENT_PAGE_ID
    )


def is_created_in_last_7_days(issue: Dict) -> bool:
    """Check if issue was created in the last 7 days."""
    created_str = issue.get("fields", {}).get("created", "")
    if not created_str:
        return False
    
    try:
        # Parse Jira datetime format (e.g., "2023-01-01T12:00:00.000+0000")
        created_date = datetime.fromisoformat(created_str.replace('Z', '+00:00').replace('.000', ''))
        seven_days_ago = datetime.now(created_date.tzinfo) - timedelta(days=7)
        return created_date >= seven_days_ago
    except Exception as e:
        logging.warning(f"Failed to parse created date: {created_str}, error: {e}")
        return False


def create_pages_for_filter(filter_id: str) -> Dict:
    """Create confluence pages for jira tickets created in last 7 days from filter."""
    jira = JiraRestApi()
    wiki = WikiRestApi()
    
    logging.info(f"Creating pages for filter {filter_id} (last 7 days only)")
    
    issues = jira.get_issues_from_filter(filter_id)
    logging.info(f"Found {len(issues)} issues")
    
    # Filter issues created in last 7 days
    recent_issues = [issue for issue in issues if is_created_in_last_7_days(issue)]
    logging.info(f"Found {len(recent_issues)} issues created in last 7 days")
    
    results = {"total_issues": len(recent_issues), "pages_created": 0, "pages_skipped": 0, "errors": []}
    
    for issue in recent_issues:
        issue_key = issue.get("key", "")
        if not issue_key:
            continue
        
        try:
            if page_exists(wiki, issue_key):
                results["pages_skipped"] += 1
            else:
                page_result = create_page(wiki, jira, issue)
                logging.info(f"Created page for {issue_key}: {page_result.get('id')}")
                results["pages_created"] += 1
        except Exception as e:
            error_msg = f"Error processing {issue_key}: {e}"
            logging.error(error_msg)
            results["errors"].append(error_msg)
    
    return results

def main() -> None:
    """Main entry point.
    Takes a Jira filter_id as input and creates Confluence pages 
    for Jira tickets created in the last 7 days from the given filter.
    """
    parser = argparse.ArgumentParser(description="Create Confluence pages for each Jira ticket")
    parser.add_argument('-f', '--filter-id', default='18891', help='Jira filter ID (default: 18891)')
    args = parser.parse_args()
    
    try:
        results = create_pages_for_filter(args.filter_id)
        
        logging.info(f"Results: {results['total_issues']} issues, {results['pages_created']} created, {results['pages_skipped']} skipped, {len(results['errors'])} errors")
        
        if results['errors']:
            logging.error("Errors occurred:")
            for error in results['errors']:
                logging.error(f"  - {error}")
                
    except Exception as e:
        logging.error(f"Failed to create pages: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()