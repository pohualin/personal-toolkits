#!/usr/bin/env python3

import argparse
import sys
from dotenv import load_dotenv
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from api.jira_rest_api import JiraRestApi
from api.wiki_rest_api import WikiRestApi
from config.logging_config import setup_logging

load_dotenv()
setup_logging()

PARENT_PAGE_ID = "1894154256"
SPACE_KEY = "38371328"
TEMPLATE_PAGE_ID = "1892909134"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--issue-key', required=True)
    args = parser.parse_args()
    
    jira = JiraRestApi()
    wiki = WikiRestApi()
    
    issue = jira.get_issue(args.issue_key)
    if not issue:
        print(f"Issue {args.issue_key} not found")
        sys.exit(1)
    
    # Check if page exists
    search_result = wiki.search(f'title ~ "{args.issue_key}"')
    if search_result.get("results", []):
        print(f"Page for {args.issue_key} already exists")
        return
    
    # Get content from template
    issue_key = issue["key"]
    summary = issue["fields"]["summary"]
    
    try:
        template = wiki.read_page(TEMPLATE_PAGE_ID)
        content = (
            template["body"]["storage"]["value"]
            .replace("{Link to ESC}", f'<ac:structured-macro ac:name="jira" ac:schema-version="1"><ac:parameter ac:name="key">{issue_key}</ac:parameter></ac:structured-macro>')
            .replace("{Describe the issue}", summary)
        )
    except:
        content = f"<h1>{issue_key}</h1><p>{summary}</p>"
    
    # Create page
    wiki.write_page(
        space_key=SPACE_KEY,
        title=f"{issue_key} - {summary}",
        content=content,
        parent_id=PARENT_PAGE_ID
    )
    
    print(f"Created page for {issue_key}")

if __name__ == "__main__":
    main()