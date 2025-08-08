# Automation Scripts Collection

A collection of Python automation scripts organized by domain for data processing, GitHub analytics, reporting, and dependency analysis.

## Project Structure

```
src/
├── customer-cleanup/    # Customer data transformation and cleanup
│   ├── json_to_excel.py      # Convert JSON to Excel format
│   └── customer_sync.py       # Customer data synchronization
├── github-analytics/    # GitHub repository analysis
│   └── projects_by_query.py   # Query and analyze GitHub projects
├── reporting/          # Report generation
│   └── fetch_weekly_report.py # Generate weekly reports
├── dependency-analysis/ # Project dependency tools
│   ├── analyze_dependencies.py # Analyze project dependencies
│   ├── build_dependency_tree.py # Build dependency trees
│   └── parse_tree.py          # Parse dependency structures
└── util/               # Shared utilities
    ├── data_processor.py      # Data processing utilities
    ├── file_utils.py          # File operations
    └── github_utils.py        # GitHub API utilities
```

## Installation

### Development Installation
```bash
pip install -e .
```

### Production Installation
```bash
pip install .
```

### With Development Dependencies
```bash
pip install -e ".[dev]"
```

## Usage

### Customer Cleanup
```bash
python -m src.customer-cleanup.json_to_excel
python -m src.customer-cleanup.customer_sync
```

### GitHub Analytics
```bash
# Basic usage
python -m src.github-analytics.projects_by_query

# With custom query
python -m src.github-analytics.projects_by_query -q "language:Python stars:>100"

# Pull security alerts
python -m src.github-analytics.projects_by_query -s
```

**Arguments:**
- `-q, --query`: GitHub search query string
- `-d, --download`: Download (clone) the repositories
- `-s, --security`: Include Dependabot security alerts (requires GITHUB_TOKEN)

### Reporting
```bash
python -m src.reporting.fetch_weekly_report
```

### Dependency Analysis
```bash
python -m src.dependency-analysis.analyze_dependencies
python -m src.dependency-analysis.build_dependency_tree
```

## Configuration

Create a `.env` file in the project root with the following variables:

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|----------|
| `CUSTOMER_SYNC_DIR` | Directory for customer data files | `~/Workspace/customer_sync` |
| `ANALYSIS_DIR` | Directory for analysis outputs | `~/Workspace/analysis` |
| `REPOS_DIR` | Directory for cloned repositories | `~/Workspace/all` |

### Optional Environment Variables

| Variable | Description | Required For |
|----------|-------------|-------------|
| `GITHUB_TOKEN` | GitHub personal access token | GitHub analytics, security scanning |
| `JIRA_API_TOKEN` | JIRA API token | JIRA integration scripts |

### Example `.env` file:

```bash
# Required directories
CUSTOMER_SYNC_DIR=~/Workspace/customer_sync
ANALYSIS_DIR=~/Workspace/analysis
REPOS_DIR=~/Workspace/all

# Optional API tokens
GITHUB_TOKEN=ghp_your_token_here
JIRA_API_TOKEN=your_jira_token_here
```

## Running Tests

```bash
python -m unittest discover -s tests
```