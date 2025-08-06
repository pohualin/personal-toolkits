"""File system utilities."""

import os
from datetime import datetime
from pathlib import Path


def ensure_file_exists(file_path: str) -> bool:
    """Check if file exists and return boolean."""
    return os.path.exists(file_path)


def generate_timestamped_filename(base_name: str, extension: str, directory: str = None) -> str:
    """Generate filename with timestamp."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{base_name}_{timestamp}.{extension}"
    
    if directory:
        return os.path.join(os.path.expanduser(directory), filename)
    return filename


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent