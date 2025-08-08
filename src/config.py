"""Configuration settings for the project."""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = os.path.expanduser(os.getenv('CUSTOMER_SYNC_DIR', '~/Workspace/customer_sync'))

# File paths
DEFAULT_INPUT_FILE = os.path.join(DATA_DIR, "true_active.json")
DEFAULT_OUTPUT_DIR = DATA_DIR

# Excel export settings
EXCEL_COLUMNS = ['Customer ID', 'Customer Name', 'Products']

# Logging configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'