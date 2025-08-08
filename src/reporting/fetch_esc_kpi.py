import logging
from ..util.logging_config import setup_logging
from ..util.jira_rest_api import JiraRestApi

jira = JiraRestApi()

def fetch_esc_kpi():
    """Fetch ESC KPI summary from specified filters"""
    filter_ids = ["18891", "19040", "19041"]
    results = []
    
    print(f"\n=== ESC KPI Summary ===")
    print(f"{'Filter ID':<10} {'Filter Name':<50} {'Total Issues':<15}")
    print("-" * 75)
    
    for filter_id in filter_ids:
        try:
            # Get filter data
            filter_data = jira.get_filter(filter_id)
            filter_name = filter_data.get("name", f"Filter {filter_id}")
            
            # Get issues count
            issues = jira.get_issues_from_filter(filter_id)
            issue_count = len(issues)
            
            # Print summary row
            print(f"{filter_id:<10} {filter_name[:48]:<50} {issue_count:<15}")
            
            # Add to results
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

def analyze_filter_18891():
    """Analyze all issues in filter 18891 with detailed breakdown"""
    filter_id = "18891"
    
    try:
        logging.debug(f"Analyzing filter {filter_id}")
        
        # Get filter data and issues
        filter_data = jira.get_filter(filter_id)
        filter_name = filter_data.get("name", f"Filter {filter_id}")
        issues = jira.get_issues_from_filter(filter_id)
        
        # Analyze by status categories
        status_counts = {}
        assignee_counts = {}
        priority_counts = {}
        assignee_status_matrix = {}
        
        for issue in issues:
            fields = issue.get("fields", {})
            
            # Count by status
            status = fields.get("status", {}).get("name", "Unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by assignee
            assignee = fields.get("assignee", {}).get("displayName", "Unassigned") if fields.get("assignee") else "Unassigned"
            assignee_counts[assignee] = assignee_counts.get(assignee, 0) + 1
            
            # Count by priority
            priority = fields.get("priority", {}).get("name", "No Priority") if fields.get("priority") else "No Priority"
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            # Combined assignee-status matrix
            if assignee not in assignee_status_matrix:
                assignee_status_matrix[assignee] = {}
            assignee_status_matrix[assignee][status] = assignee_status_matrix[assignee].get(status, 0) + 1
        
        # Print analysis
        print(f"\n=== Analysis: {filter_name} (ID: {filter_id}) ===")
        print(f"Total Issues: {len(issues)}")
        
        print(f"\nBy Status:")
        for status, count in sorted(status_counts.items()):
            percentage = (count / len(issues) * 100) if len(issues) > 0 else 0
            print(f"  {status:<15}: {count:>3} ({percentage:>5.1f}%)")
        
        print(f"\nBy Assignee:")
        for assignee, count in sorted(assignee_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(issues) * 100) if len(issues) > 0 else 0
            print(f"  {assignee:<25}: {count:>3} ({percentage:>5.1f}%)")
        
        print(f"\nAssignee vs Status Matrix:")
        for assignee in sorted(assignee_status_matrix.keys()):
            print(f"\n  {assignee}:")
            for status, count in sorted(assignee_status_matrix[assignee].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / assignee_counts[assignee] * 100) if assignee_counts[assignee] > 0 else 0
                print(f"    {status:<15}: {count:>3} ({percentage:>5.1f}% of {assignee}'s work)")
        
        return {
            "total_issues": len(issues),
            "status_breakdown": status_counts,
            "assignee_breakdown": assignee_counts,
            "priority_breakdown": priority_counts,
            "assignee_status_matrix": assignee_status_matrix
        }
        
    except Exception as e:
        logging.error(f"Error analyzing filter {filter_id}: {e}")
        return None

def main():
    try:
        fetch_esc_kpi()
        analyze_filter_18891()
    except Exception as e:
        logging.error(f"Error generating ESC KPI summary: {e}")

if __name__ == "__main__":
    main()