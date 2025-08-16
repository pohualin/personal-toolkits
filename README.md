
# Personal Toolkits

A collection of Python automation tools for productivity, reporting, and data processing.

## Project Structure

```
src/
    api/         # External API clients (Jira, Confluence, GitHub)
    config/      # Configuration and logging
    util/        # General utilities
    scripts/     # Executable scripts (Twitter, Wiki, etc.)
tests/         # Unit tests
weekly_report/ # Generated reports
```

## Installation

```bash
pip install -e .
```

## Usage

Scripts are now located in `src/scripts/`. Example:

```bash
python src/scripts/twitter/download_by_channel.py <channel_name> [<post_id>]
```

## Configuration

Create a `.env` file in the project root with required and optional environment variables for API tokens, directories, and logging.

## Running Tests

```bash
python -m unittest discover -s tests
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

### Reporting
```bash
# Run combined ESC KPI and core report
python scripts/reporting/create_core_report.py

# Run individual reports
python scripts/reporting/fetch_esc_kpi.py -f 18891 19040 19041
python scripts/reporting/analyze_esc_filter.py -f 18891
python scripts/reporting/fetch_epics_status.py -f 18871
```

**Output:**
- Text report: `weekly_report/YYYYmmdd_weekly_report.txt`
- JSON data: `weekly_report/YYYYmmdd_weekly_report.json`

### Wiki/Confluence
```bash
# Create ESC pages from Jira filter
python scripts/wiki/create_esc_pages.py -f 18891

# Create page for specific issue
python scripts/wiki/create_issue_page.py -i ISSUE-123
```

### Jira Automation
```bash
# Create Jira tickets from Excel data
python scripts/jira/create_tickets.py
```

### GitHub Analytics
```bash
# Basic repository analysis
python scripts/github/repos_by_query.py

# With custom query
python scripts/github/repos_by_query.py -q "language:Python stars:>100"

# Include security alerts
python scripts/github/repos_by_query.py -s
```

**Arguments:**
- `-q, --query`: GitHub search query string
- `-d, --download`: Download (clone) repositories
- `-s, --security`: Include Dependabot security alerts

### Dependency Analysis
```bash
# Analyze JSON dependency files
python scripts/dependency/analyze_dependencies.py

# Generate Maven dependency trees
python scripts/dependency/build_tree_json.py

# Extract specific versions
python scripts/dependency/extract_versions.py -g com.h2database -a h2 -v 2.1.214
```

### Data Processing
```bash
# Convert JSON to Excel
python scripts/customer_cleanup/json_to_excel.py

# Customer data synchronization
python scripts/customer_cleanup/customer_sync.py
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
| `JIRA_API_TOKEN` | JIRA API token (Base64 encoded) | JIRA integration, ESC wiki creation, reporting |
| `JIRA_BASE_URL` | JIRA instance URL | JIRA integration, ESC wiki creation, reporting |
| `CONFLUENCE_API_TOKEN` | Confluence API token (Base64 encoded) | ESC wiki creation |
| `CONFLUENCE_BASE_URL` | Confluence instance URL | ESC wiki creation |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | Global logging control |

### Example `.env` file:

```bash
# Required directories
CUSTOMER_SYNC_DIR=~/Workspace/customer_sync
ANALYSIS_DIR=~/Workspace/analysis
REPOS_DIR=~/Workspace/all

# Optional API tokens
GITHUB_TOKEN=ghp_your_token_here

# Jira/Confluence integration
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_API_TOKEN=your_base64_encoded_token
CONFLUENCE_BASE_URL=https://your-domain.atlassian.net
CONFLUENCE_API_TOKEN=your_base64_encoded_token
```

## Running Tests

```bash
python -m unittest discover -s tests
```