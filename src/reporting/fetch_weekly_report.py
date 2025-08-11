import logging
from ..config.logging_config import setup_logging
from ..util.jira_rest_api import JiraRestApi

jira = JiraRestApi()

def analyze_epic(epic_key):
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

def fetch_weekly_report():
    """Fetch weekly report data from filter 18871"""
    logging.info("Fetching filter 18871 for weekly report")
    
    try:
        # Get epics from filter
        issues = jira.get_issues_from_filter("18871")
        epic_keys = [issue["id"] for issue in issues]
        
        print(f"\n=== High Level Objectives ===")
        
        results = []
        for key in epic_keys:
            epic_data = analyze_epic(key)
            results.append(epic_data)
            
            # Print formatted row
            print(f"{epic_data['epic_key']},{epic_data['summary']},{epic_data['total_issues']},{epic_data['done_issues']}")        
        return results
        
    except Exception as e:
        logging.error(f"Error fetching weekly report: {e}")
        return []

def main():
    """Main function for weekly report"""
    return fetch_weekly_report()

if __name__ == "__main__":
    main()