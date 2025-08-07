# Automation Scripts Collection

A collection of Python automation scripts organized by domain for data processing, GitHub analytics, reporting, and dependency analysis.

## Project Structure

```
src/
├── data-processing/     # Data transformation and synchronization
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

### Data Processing
```bash
python -m src.data-processing.json_to_excel
python -m src.data-processing.customer_sync
```

### GitHub Analytics
```bash
python -m src.github-analytics.projects_by_query
```

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

Copy `.env.example` to `.env` and configure your API tokens:

```bash
JIRA_API_TOKEN=your_token_here
GITHUB_TOKEN=your_token_here
```

## Running Tests

```bash
python -m unittest discover -s tests
```