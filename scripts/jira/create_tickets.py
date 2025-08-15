#!/usr/bin/env python3

import pandas as pd
import os
import logging
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))
from api.jira_rest_api import JiraRestApi
from config.logging_config import setup_logging

setup_logging()

def main():
    excel_file = os.path.expanduser("~/Workspace/analysis/java_repos.xlsx")
    
    if not os.path.exists(excel_file):
        logging.error(f"Excel file not found: {excel_file}")
        return
    
    df = pd.read_excel(excel_file)
    
    if 'jira ticket' not in df.columns:
        df['jira ticket'] = ''
    
    jira = JiraRestApi()
    
    for index, row in df.iterrows():
        issue_data = {
            "fields": {
                "project": {"key": "DORS"},
                "parent": {"key": "DORS-4075"},
                "issuetype": {"name": "Sub-task"},
                "summary": f"Upgrade {row.get('name')}",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Repository: "
                                },
                                {
                                    "type": "text",
                                    "text": row.get('url'),
                                    "marks": [
                                        {
                                            "type": "link",
                                            "attrs": {
                                                "href": row.get('url')
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        }
        
        try:
            result = jira.create_issue(issue_data)
            ticket_key = result['key']
            df.at[index, 'jira ticket'] = ticket_key
            logging.info(f"Created ticket {ticket_key} for {row.get('name')}")
        except Exception as e:
            logging.error(f"Failed to create ticket for {row.get('name')}: {e}")
    
    df.to_excel(excel_file, index=False)
    logging.info("Finished processing all rows")

if __name__ == "__main__":
    main()