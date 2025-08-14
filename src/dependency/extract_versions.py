#!/usr/bin/env python3
"""
Extract dependency versions from JSON files and export to Excel.
"""

import argparse
import json
import os
import pandas as pd
from datetime import datetime
from packaging import version

def find_dependency_version(data, group_id, artifact_id, version=None):
    """Recursively search for dependency version in dependency tree."""
    if not data:
        return version
    
    # Check if current dependency matches
    if (data.get('groupId') == group_id and 
        data.get('artifactId') == artifact_id):
        version = data.get('version')
    
    # Search in dependencies
    for dep in data.get('dependencies', []):
        found_version = find_dependency_version(dep, group_id, artifact_id, version)
        if found_version:
            version = found_version
    
    return version

def main():
    """Extract dependency versions from JSON files and create Excel report."""
    parser = argparse.ArgumentParser(description='Extract dependency versions from JSON files')
    parser.add_argument('-g', '--groupId', required=True, help='Group ID (e.g., com.h2database)')
    parser.add_argument('-a', '--artifactId', required=True, help='Artifact ID (e.g., h2)')
    parser.add_argument('-v', '--version', required=True, help='Version to compare against')
    
    args = parser.parse_args()
    
    group_dir = args.groupId.replace('.', '_')
    json_dir = os.path.expanduser(f"~/Workspace/analysis/{group_dir}/json")
    
    if not os.path.exists(json_dir):
        print(f"Directory {json_dir} does not exist")
        return
    
    results = []
    
    # Process all JSON files
    for filename in os.listdir(json_dir):
        if not filename.endswith('.json'):
            continue
            
        file_path = os.path.join(json_dir, filename)
        project_name = filename[:-5]  # Remove .json extension
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            found_version = find_dependency_version(data, args.groupId, args.artifactId)
            
            # Check if version is greater than the given version
            updated = False
            if found_version and found_version != 'Not Found':
                try:
                    updated = version.parse(found_version) >= version.parse(args.version)
                except:
                    updated = False
            
            results.append({
                'repository': project_name,
                args.artifactId: found_version or 'Not Found',
                'updated': updated
            })
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            results.append({
                'repository': project_name,
                args.artifactId: 'Error',
                'updated': False
            })
    
    # Create Excel file
    if results:
        df = pd.DataFrame(results)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.expanduser(f"~/Workspace/analysis/{args.artifactId}_versions_{timestamp}.xlsx")
        
        df.to_excel(output_file, index=False)
        print(f"{args.artifactId} versions exported to: {output_file}")
        print(f"Processed {len(results)} files")
    else:
        print("No JSON files found to process")

if __name__ == "__main__":
    main()