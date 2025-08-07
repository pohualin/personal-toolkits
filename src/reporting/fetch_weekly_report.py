import os
import requests
import csv
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

load_dotenv()

JIRA_BASE_URL = "https://trustwave.atlassian.net"
API_ENDPOINT = "/rest/api/3/search"
API_TOKEN = os.getenv("JIRA_API_TOKEN")  # Store your token in .env as JIRA_API_TOKEN
EMAIL = os.getenv("JIRA_EMAIL")          # Store your email in .env as JIRA_EMAIL
# AUTH = (EMAIL, API_TOKEN)
JQL_QUERY = "parent="
AND_DONE = " AND statusCategory = Done"

HEADERS = {
    "Authorization": "Basic {API_TOKEN}".format(API_TOKEN=API_TOKEN),
    "Accept": "application/json"
}

def csv_export(epic):
    url = f"{JIRA_BASE_URL}{API_ENDPOINT}?jql={JQL_QUERY}{epic}"
    logging.info(f"Requesting issues for epic {epic} from {url}")
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    with open(f"{epic}.csv", "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Key", "StatusCategory"])
        for issue in data.get("issues", []):
            writer.writerow([issue["key"], issue["fields"]["status"]["statusCategory"]["name"]])
    logging.info(f"Exported issues for epic {epic} to {epic}.csv")

def calculate(key):
    key = key.replace('"', '')
    issue_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{key}"
    # logging.info(f"Fetching issue details for key {key}")
    response = requests.get(issue_url, headers=HEADERS)
    epic = response.json().get("key")
    summary = ""
    try:
        summary = response.json().get("fields", {}).get("summary", "")
    except (IndexError, KeyError, TypeError):
        logging.warning(f"Could not retrieve summary for epic {epic}")

    search_url = f"{JIRA_BASE_URL}{API_ENDPOINT}?jql={JQL_QUERY}{epic}"
    # logging.info(f"Fetching issues for epic {epic} from {search_url}")
    response = requests.get(search_url, headers=HEADERS)
    data = response.json()
    total = data.get("total", 0)
    
    done_url = f"{JIRA_BASE_URL}{API_ENDPOINT}?jql={JQL_QUERY}{epic}{AND_DONE}"
    # logging.info(f"Fetching done issues for epic {epic} from {done_url}")
    response = requests.get(done_url, headers=HEADERS)
    done = response.json().get("total", 0)

    # logging.info(f"Epic: {epic}, Summary: {summary}, Total: {total}, Done: {done}")
    print(f"{epic},{summary},{total},{done}")

def get_keys():
    filter_url = f"{JIRA_BASE_URL}/rest/api/3/filter/18871"
    logging.info(f"Fetching filter from {filter_url}")
    response = requests.get(filter_url, headers=HEADERS)
    search_url = response.json().get("searchUrl", "")
    if search_url.startswith('"') and search_url.endswith('"'):
        search_url = search_url[1:-1]
    logging.info(f"Fetching issues from search URL: {search_url}")
    response = requests.get(search_url, headers=HEADERS)
    data = response.json()
    keys = [issue["id"] for issue in data.get("issues", [])]
    logging.info(f"Retrieved {len(keys)} keys")
    return keys

def main():
    keys = get_keys()
    for key in keys:
        calculate(key)
    logging.info("Script finished.")

if __name__ == "__main__":
    main()