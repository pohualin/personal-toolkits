import csv
import logging
from ..util.logging_config import setup_logging
from ..util.jira_rest_api import JiraRestApi

jira = JiraRestApi()

def csv_export(epic):
    logging.debug(f"Requesting issues for epic {epic}")
    data = jira.search_issues(f"parent={epic}")
    with open(f"{epic}.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Key", "StatusCategory"])
        for issue in data.get("issues", []):
            writer.writerow([issue["key"], issue["fields"]["status"]["statusCategory"]["name"]])
    logging.debug(f"Exported issues for epic {epic} to {epic}.csv")

def calculate(key):
    key = key.replace('"', '')
    issue_data = jira.get_issue(key)
    epic = issue_data.get("key")
    summary = ""
    try:
        summary = issue_data.get("fields", {}).get("summary", "")
    except (IndexError, KeyError, TypeError):
        logging.warning(f"Could not retrieve summary for epic {epic}")

    total = jira.count_issues(f"parent={epic}")
    done = jira.count_issues(f"parent={epic} AND statusCategory = Done")

    print(f"{epic},{summary},{total},{done}")

def get_keys():
    logging.debug("Fetching filter 18871")
    filter_data = jira.get_filter("18871")
    search_url = filter_data.get("searchUrl", "")
    if search_url.startswith('"') and search_url.endswith('"'):
        search_url = search_url[1:-1]
    logging.debug(f"Fetching issues from search URL: {search_url}")
    
    # Extract JQL from search URL or use filter's JQL
    jql = filter_data.get("jql", "")
    data = jira.search_issues(jql)
    keys = [issue["id"] for issue in data.get("issues", [])]
    logging.debug(f"Retrieved {len(keys)} keys")
    return keys

def main():
    keys = get_keys()
    print(f"\n=== High Level Objectives ===")
    for key in keys:
        calculate(key)

if __name__ == "__main__":
    main()