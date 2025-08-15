import logging
import os
import requests

class GithubUtils:
    github_token = os.getenv("GITHUB_TOKEN")

    @staticmethod
    def make_request(url, params=None):
        """Make a GitHub API request with proper headers and error handling."""
        headers = {"Accept": "application/vnd.github+json"}
        if GithubUtils.github_token:
            headers["Authorization"] = f"Bearer {GithubUtils.github_token}"
        
        response = requests.get(url, headers=headers, params=params)
        return response

    @staticmethod
    def get_dependabot_alerts(repo_owner, repo_name):
        """Get Dependabot security alerts for a repository."""
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/dependabot/alerts?state=open"
        return GithubUtils.make_request(url)

    @staticmethod
    def search(query_string, per_page=100):
        url = "https://api.github.com/search/repositories"
        params = {
            "q": f"{query_string}",
            "sort": "stars",
            "order": "desc",
            "per_page": per_page
        }

        projects = []
        page = 1
        while True:
            params["page"] = page
            logging.info(f"Requesting page {page} for query '{query_string}' from GitHub API...")
            resp = GithubUtils.make_request(url, params)
            if resp.status_code != 200:
                logging.error(f"GitHub API error: {resp.status_code} {resp.text}")
                break
            data = resp.json()
            items = data.get("items", [])
            if not items:
                logging.info("No more repositories found.")
                break
            projects.extend(items)
            if len(items) < per_page:
                logging.info("Last page reached.")
                break
            page += 1

        logging.info(f"Total repositories collected: {len(projects)}")
        return projects

# Example usage:
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)