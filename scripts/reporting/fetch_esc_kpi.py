import argparse
import logging
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

from config.logging_config import setup_logging
from api.jira_rest_api import JiraRestApi

setup_logging()

def fetch_esc_kpi(filter_ids=None):
    """Fetch ESC KPI summary from specified filters"""
    if filter_ids is None:
        filter_ids = ["18891", "19040", "19041"]
    
    jira = JiraRestApi()
    results = []
    
    print("\n=== ESC KPI Summary ===")
    print(f"{'Filter ID':<10} {'Filter Name':<50} {'Total Issues':<15}")
    print("-" * 75)
    
    for filter_id in filter_ids:
        try:
            filter_data = jira.get_filter(filter_id)
            filter_name = filter_data.get("name", f"Filter {filter_id}")
            
            issues = jira.get_issues_from_filter(filter_id)
            issue_count = len(issues)
            
            print(f"{filter_id:<10} {filter_name[:48]:<50} {issue_count:<15}")
            results.append({
                "filter_id": filter_id,
                "filter_name": filter_name,
                "total_issues": issue_count
            })
            
        except Exception as e:
            logging.error(f"Error fetching filter {filter_id}: {e}")
            print(f"{filter_id:<10} {'ERROR':<50} {'N/A':<15}")
            results.append({
                "filter_id": filter_id,
                "filter_name": "ERROR",
                "total_issues": None,
                "error": str(e)
            })
    
    print("-" * 75)
    return results



def main():
    """Main function for ESC KPI fetching"""
    parser = argparse.ArgumentParser(description="Fetch ESC KPI summary from Jira filters")
    parser.add_argument('-f', '--filters', nargs='+', default=['18891', '19040', '19041'], 
                       help='List of Jira filter IDs (default: 18891 19040 19041)')
    args = parser.parse_args()
    
    try:
        return fetch_esc_kpi(args.filters)
    except Exception as e:
        logging.error(f"Error generating ESC KPI summary: {e}")

if __name__ == "__main__":
    main()