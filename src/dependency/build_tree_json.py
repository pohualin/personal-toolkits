"""Maven dependency tree analyzer that generates JSON output."""

import os
import sys
import subprocess
import json
import logging
import re
import argparse
import xml.etree.ElementTree as ET
import shutil

from dotenv import load_dotenv
from ..config.logging_config import setup_logging

# Initialize environment and logging
load_dotenv()
load_dotenv('.env')
setup_logging()

# Global variables for sharing state
repos_dir = None
processing = None
des_dir_json = None
des_dir_error = None
includes_filter = None

def _process_folder(folder_name):
    """Process a single Maven project folder."""
    global processing
    processing = folder_name
    logging.info(f"Processing folder: {processing}")
    
    # Check for pom.xml file
    pom_path = os.path.join(processing, "pom.xml")
    if not os.path.isfile(pom_path):
        _handle_missing_pom()
        return
    
    # Setup output paths
    os.chdir(processing)
    tmp_file_name = f"{processing}.tmp"
    tmp_file_path = os.path.join(des_dir_json, tmp_file_name)
    
    # Run Maven dependency tree command
    logging.info(f"Running Maven dependency:tree in {processing}")
    result = subprocess.run(
        [
            "mvn",
            "dependency:tree",
            "-DoutputType=json",
            f"-DoutputFile={tmp_file_path}",
            f"-Dincludes={includes_filter}"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Handle Maven command result
    if result.returncode != 0:
        logging.error(f"Maven command failed: {processing}")
        _write_error_file(result.stderr)
        return
    
    # Process the generated dependency tree file
    os.chdir(des_dir_json)
    logging.info(f"Parsing dependency tree from {tmp_file_name}")
    _build_tree_json(tmp_file_name)


def _build_tree_json(tmp_file):
    """Convert Maven dependency tree text file to JSON format."""
    try:
        # Read dependency tree file
        with open(tmp_file) as f:
            lines = f.readlines()
        
        # Parse Maven dependency tree text output into structured JSON format
        def parse_line(line):
            return re.sub(r'^([|\\+\- ]+)', '', line)

        def parse_dep(dep_str):
            parts = dep_str.split(':')
            if len(parts) < 4:
                return {"artifact": dep_str.rstrip('\n')}
            return {
                "groupId": parts[0],
                "artifactId": parts[1],
                "type": parts[2],
                "version": parts[3]
            }

        root = None
        stack = []

        for line in lines:
            if not line.strip():
                continue
                
            # Calculate nesting depth
            match = re.match(r'^([|\\+\- ]+)', line)
            depth = match.group(0).count('|') + match.group(0).count('+') + match.group(0).count('\\') if match else 0
            
            # Parse dependency
            dep_str = parse_line(line)
            dep = parse_dep(dep_str)
            dep["dependencies"] = []

            if depth == 0:
                root = dep
                stack = [(dep, depth)]
            else:
                # Find correct parent in stack
                while stack and stack[-1][1] >= depth:
                    stack.pop()
                if stack:
                    stack[-1][0]["dependencies"].append(dep)
                stack.append((dep, depth))
        
        out_file = tmp_file.rsplit('.', 1)[0] + ".json"
        
        # Only write JSON output if root is not null
        if root is None:
            logging.info(f"JSON file is null for {out_file}")
        else:
            with open(out_file, "w") as out_f:
                json.dump(root, out_f, indent=2)
            logging.info(f"Created dependency tree JSON: {out_file}")
        
        # Clean up temporary file
        os.remove(tmp_file)
        
    except Exception as e:
        logging.error(f"Error parsing dependency tree: {e}")


def _handle_missing_pom():
    """Process pom files one level deeper."""
    global processing
    current_folder = processing  # Save current processing value
    subdirs = [d for d in os.listdir(current_folder) if os.path.isdir(os.path.join(current_folder, d)) and not d.startswith('.')]
    
    # Collect all subdirectories with pom.xml files
    pom_dirs = []
    for subdir in subdirs:
        subdir_path = os.path.join(current_folder, subdir)
        pom_path = os.path.join(subdir_path, "pom.xml")
        if os.path.isfile(pom_path):
            pom_dirs.append(subdir_path)
    
    # Process all found pom directories
    for pom_dir in pom_dirs:
        os.chdir(repos_dir)  # Reset to base directory
        _process_folder(pom_dir)
    
    if not pom_dirs:
        processing = current_folder  # Restore processing value for error file
        _write_error_file(f"pom.xml not found in {current_folder}")


def _write_error_file(error_message):
    """Write error message to error file."""
    error_file_path = os.path.join(des_dir_error, f"{processing}.error")
    with open(error_file_path, "w") as f:
        f.write(error_message)


def main():
    """Main entry point for dependency tree analysis."""
    global repos_dir, des_dir_json, des_dir_error, includes_filter
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate Maven dependency tree JSON files')
    parser.add_argument('-i', '--includes', 
                       default='com.trustwave,com.trustwave.dna',
                       help='Maven includes filter (default: com.trustwave,com.trustwave.dna)')
    args = parser.parse_args()
    
    # Setup global variables
    includes_filter = args.includes
    repos_dir = os.getenv('REPOS_DIR')
    analysis_dir = os.getenv('ANALYSIS_DIR')
    if not repos_dir or not analysis_dir:
        raise ValueError("REPOS_DIR and ANALYSIS_DIR environment variables are required")
    
    repos_dir = os.path.expanduser(repos_dir)
    if not os.path.isdir(repos_dir):
        logging.error(f"Folder {repos_dir} does not exist.")
        sys.exit(1)
    
    # Remove old and create new destination directories
    includes_name = includes_filter.replace(',', '-').replace('.', '_')
    base_dir = os.path.join(os.path.expanduser(analysis_dir), includes_name)
    # Remove all files in base_dir if it exists
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    des_dir_json = os.path.join(base_dir, "json")
    des_dir_error = os.path.join(base_dir, "error")
    os.makedirs(des_dir_json, exist_ok=True)
    os.makedirs(des_dir_error, exist_ok=True)
    
    os.chdir(repos_dir)

    # Get folders to process
    subfolders = [f for f in os.listdir('.') if os.path.isdir(f) and not f.startswith('.')]
    
    # Remove comment if only want to process some folders
    # folders_to_process = [
    #     "global-finding",
    #     "tw-parent-external",
    #     "tw-parent-api",
    #     "tw-parent-service"
    # ]
    # subfolders = [f for f in subfolders if f in folders_to_process]

    # Process each subfolder
    for subfolder in subfolders:
        logging.info("-" * 40)
        logging.info(subfolder)
        os.chdir(repos_dir)
        _process_folder(subfolder) 
        logging.info("-" * 40)

if __name__ == "__main__":
    main()