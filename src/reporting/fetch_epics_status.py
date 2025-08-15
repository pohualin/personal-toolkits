import argparse
import logging
from ..config.logging_config import setup_logging
from ..util.jira_rest_api import JiraRestApi

setup_logging()

def analyze_epic(jira, epic_key):
    """Analyze a single epic and return structured data"""
    try:
        epic_key = epic_key.replace('"', '')
        issue_data = jira.get_issue(epic_key)
        epic = issue_data.get("key")
        summary = issue_data.get("fields", {}).get("summary", "")
        
        total = jira.count_issues(f"parent={epic}")
        done = jira.count_issues(f"parent={epic} AND statusCategory = Done")
        completion_rate = (done / total * 100) if total > 0 else 0
        
        return {
            "epic_key": epic,
            "summary": summary,
            "total_issues": total,
            "done_issues": done,
            "completion_rate": round(completion_rate, 1)
        }
    except Exception as e:
        logging.error(f"Error analyzing epic {epic_key}: {e}")
        return {
            "epic_key": epic_key,
            "summary": "ERROR",
            "total_issues": 0,
            "done_issues": 0,
            "completion_rate": 0,
            "error": str(e)
        }

def fetch_epics_status(filter_id="18871"):
    """Fetch epic status data from filter"""
    jira = JiraRestApi()
    logging.info(f"Fetching filter {filter_id} for epic status")
    
    try:
        issues = jira.get_issues_from_filter(filter_id)
        epic_keys = [issue["id"] for issue in issues]
        
        print("\n=== High Level Objectives ===")
        
        results = []
        for key in epic_keys:
            epic_data = analyze_epic(jira, key)
            results.append(epic_data)
            
            print(f"{epic_data['epic_key']},{epic_data['summary']},{epic_data['total_issues']},{epic_data['done_issues']}")
        
        return results
        
    except Exception as e:
        logging.error(f"Error fetching epic status: {e}")
        return []

def main():
    """Main function for epic status"""
    parser = argparse.ArgumentParser(description="Fetch epic status from Jira filter")
    parser.add_argument('-f', '--filter-id', default='18871', help='Jira filter ID (default: 18871)')
    args = parser.parse_args()
    
    return fetch_epics_status(args.filter_id)

if __name__ == "__main__":
    main()