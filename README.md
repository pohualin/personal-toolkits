# Automation Scripts Collection

A collection of Python automation scripts organized by domain for data processing, GitHub analytics, reporting, dependency analysis, and Jira-Confluence integration.

## Project Structure

```
src/
├── customer_cleanup/    # Customer data transformation and cleanup
│   ├── json_to_excel.py      # Convert JSON to Excel format
│   └── customer_sync.py       # Customer data synchronization
├── github/              # GitHub repository analysis
│   └── repos_by_query.py      # Query and analyze GitHub repositories
├── reporting/          # Report generation
│   ├── main.py               # Combined reporting runner
│   ├── fetch_esc_kpi.py      # ESC KPI metrics and analysis
│   └── fetch_weekly_report.py # Weekly objectives report
├── dependency/          # Project dependency analysis tools
│   ├── analyze_dependencies.py # Analyze JSON dependency files
│   ├── build_tree_json.py     # Generate Maven dependency trees as JSON
│   └── extract_versions.py    # Extract specific dependency versions
├── create_esc_wiki/    # ESC wiki page creation from Jira
│   └── main.py               # Create Confluence pages from Jira filter
├── jira/               # Jira ticket management
│   └── create_tickets.py     # Create Jira tickets from Excel data
├── config/             # Configuration modules
│   └── logging_config.py     # Global logging configuration
└── util/               # Shared utilities
    ├── data_processor.py      # Data processing utilities
    ├── file_utils.py          # File operations
    ├── github_rest_api.py     # GitHub API client
    ├── jira_rest_api.py       # Jira REST API client
    ├── wiki_rest_api.py       # Confluence REST API client
    └── output_capture.py      # Output capture utilities
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
python -m src.customer_cleanup.json_to_excel
python -m src.customer_cleanup.customer_sync
```

### GitHub Analytics
```bash
# Basic usage
python -m src.github.repos_by_query

# With custom query
python -m src.github.repos_by_query -q "language:Python stars:>100"

# Pull security alerts
python -m src.github.repos_by_query -s
```

**Arguments:**
- `-q, --query`: GitHub search query string
- `-d, --download`: Download (clone) the repositories
- `-s, --security`: Include Dependabot security alerts (requires GITHUB_TOKEN)

### Reporting
```bash
# Run combined ESC KPI and weekly report
python -m src.reporting.main

# Run individual reports
python -m src.reporting.fetch_esc_kpi
python -m src.reporting.fetch_weekly_report
```

**Output:**
- Text report: `weekly_report/YYYYmmdd_weekly_report.txt`
- JSON data: `weekly_report/YYYYmmdd_weekly_report.json`

### Dependency Analysis
```bash
# Analyze JSON dependency files and export to Excel
python -m src.dependency.analyze_dependencies

# Generate Maven dependency trees as JSON
python -m src.dependency.build_tree_json

# Extract specific dependency versions
python -m src.dependency.extract_versions -g com.h2database -a h2 -v 2.1.214
```

**Arguments for build_tree_json:**
- `-i, --includes`: Maven includes filter (default: com.trustwave,com.trustwave.dna)

**Arguments for extract_versions:**
- `-g, --groupId`: Group ID (e.g., com.h2database)
- `-a, --artifactId`: Artifact ID (e.g., h2)
- `-v, --version`: Version to compare against

### ESC Wiki Creation
```bash
# Create wiki pages from Jira filter (default filter: 18891)
python -m src.create_esc_wiki.main

# Use custom filter
python -m src.create_esc_wiki.main -f 18871
```

**Arguments:**
- `-f, --filter-id`: Jira filter ID (default: 18891)

### Jira Ticket Management
```bash
# Create Jira tickets from Excel data
python -m src.jira.create_tickets
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