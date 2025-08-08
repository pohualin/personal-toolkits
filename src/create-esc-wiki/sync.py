import logging
from typing import List, Dict
from ..util.jira_rest_api import JiraRestApi
from ..util.wiki_rest_api import WikiRestApi


class CreateEscWiki:
    """Create ESC wiki pages from Jira issues"""

    def __init__(self):
        self.jira = JiraRestApi()
        self.wiki = WikiRestApi()
        self.parent_id = "1892909160"
        self.space_key = "38371328"  # Changed from space_id to space_key



    def page_exists_for_issue(self, issue_key: str) -> bool:
        """Check if a Confluence page exists for the given issue key"""
        cql = f'title ~ "{issue_key}"'
        search_result = self.wiki.search(cql)
        return len(search_result.get("results", [])) > 0

    def create_page_for_issue(self, issue: Dict) -> Dict:
        """Create a Confluence page for a Jira issue"""
        issue_key = issue.get("key", "")
        summary = issue.get("fields", {}).get("summary", "")
        title = f"{issue_key} - {summary}"

        content = f"""
        <h1>{issue_key}</h1>
        <p><strong>Summary:</strong> {summary}</p>
        <p><strong>Status:</strong> {issue.get('fields', {}).get('status', {}).get('name', 'N/A')}</p>
        <p><strong>Assignee:</strong> {issue.get('fields', {}).get('assignee', {}).get('displayName', 'Unassigned') if issue.get('fields', {}).get('assignee') else 'Unassigned'}</p>
        <p><strong>Jira Link:</strong> <a href="{self.jira.base_url}/browse/{issue_key}">{issue_key}</a></p>
        """

        template_page = self.wiki.read_page("1892909134")
        if template_page:
            content = (
                template_page.get("body", {})
                .get("storage", {})
                .get("value", "")
                .replace(
                    "{Link to ESC}",
                    f'<ac:structured-macro ac:name="jira" ac:schema-version="1"><ac:parameter ac:name="key">{issue_key}</ac:parameter></ac:structured-macro>',
                )
                .replace("{Describe the issue}", summary)
            )
        else:
            logging.error("Template page not found, using default content")

        return self.wiki.write_page(
            space_key=self.space_key,
            title=title,
            content=content,
            parent_id=self.parent_id,
        )

    def sync_filter_to_confluence(self, filter_id: str) -> Dict:
        """Main sync method: get issues from filter and create pages if needed"""
        logging.info(f"Starting sync for filter {filter_id}")

        issues = self.jira.get_issues_from_filter(filter_id)
        logging.info(f"Found {len(issues)} issues from filter {filter_id}")
        results = {
            "total_issues": len(issues),
            "pages_created": 0,
            "pages_skipped": 0,
            "errors": [],
        }

        page_created = False

        for issue in issues:
            issue_key = issue.get("key", "")
            try:
                if self.page_exists_for_issue(issue_key):
                    logging.info(f"Page already exists for {issue_key}, skipping")
                    results["pages_skipped"] += 1
                else:
                    if not page_created:
                        # Create page for the first issue without a page
                        page_result = self.create_page_for_issue(issue)
                        logging.info(
                            f"Created page for {issue_key}: {page_result.get('id')}"
                        )
                        results["pages_created"] += 1
                        page_created = True
                    else:
                        # Skip creating pages for remaining issues without pages
                        logging.info(
                            f"Skipping page creation for {issue_key} (already created one page)"
                        )
                        results["pages_skipped"] += 1
            except Exception as e:
                error_msg = f"Error processing {issue_key}: {str(e)}"
                logging.error(error_msg)
                results["errors"].append(error_msg)

        logging.info(f"Sync completed: {results}")
        return results
