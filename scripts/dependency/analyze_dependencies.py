#!/usr/bin/env python3
"""
Analyze JSON dependency files to find the most used projects/artifacts.
"""

import json
import os
from collections import Counter, defaultdict
from pathlib import Path
import pandas as pd
from datetime import datetime

def extract_dependencies(dep_obj, all_deps, current_project):
    """Recursively extract all dependencies from a dependency object."""
    if isinstance(dep_obj, dict):
        if 'artifactId' in dep_obj:
            artifact_name = dep_obj['artifactId']
            group_id = dep_obj.get('groupId', '')
            version = dep_obj.get('version', 'N/A')
            
            # Store both just artifact name and full coordinates
            all_deps['artifacts'].append(artifact_name)
            all_deps['full_coords'].append(f"{group_id}:{artifact_name}")
            all_deps['versions'][artifact_name].append(version)
            all_deps['artifact_projects'][artifact_name].add(current_project)
            
            # Track project-version combinations
            project_version_key = f"{current_project}:{version}"
            all_deps['project_versions'][artifact_name].add(project_version_key)
            
        # Recursively process nested dependencies
        if 'dependencies' in dep_obj and isinstance(dep_obj['dependencies'], list):
            for nested_dep in dep_obj['dependencies']:
                extract_dependencies(nested_dep, all_deps, current_project)
    elif isinstance(dep_obj, list):
        for item in dep_obj:
            extract_dependencies(item, all_deps, current_project)

def analyze_json_files(json_dir):
    """Analyze all JSON files in the directory."""
    json_path = Path(json_dir)
    all_dependencies = {
        'artifacts': [],
        'full_coords': [],
        'versions': defaultdict(list),
        'artifact_projects': defaultdict(set),
        'project_versions': defaultdict(set)
    }
    
    projects_analyzed = []
    error_files = []
    
    for json_file in json_path.glob('*.json'):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                
            # Extract the main artifact info
            main_artifact = json_file.stem
            projects_analyzed.append(main_artifact)
            
            # Extract all dependencies
            if 'dependencies' in data:
                extract_dependencies(data['dependencies'], all_dependencies, main_artifact)
                
        except Exception as e:
            error_files.append(f"{json_file.name}: {str(e)}")
    
    return all_dependencies, projects_analyzed, error_files

def print_analysis_results(all_deps, projects_analyzed, error_files):
    """Print the analysis results."""
    print(f"🔍 Analysis of JSON Dependencies")
    print(f"=" * 50)
    print(f"📊 Total projects analyzed: {len(projects_analyzed)}")
    print(f"❌ Files with errors: {len(error_files)}")
    print()
    
    if error_files:
        print("❌ Error Files:")
        for error in error_files[:5]:  # Show first 5 errors
            print(f"  - {error}")
        if len(error_files) > 5:
            print(f"  ... and {len(error_files) - 5} more")
        print()
     # Count most common artifacts
    artifact_counts = Counter(all_deps['artifacts'])
    
    # print(f"🏆 TOP 15 MOST USED ARTIFACTS (by number of projects):")
    # print("-" * 70)
    
    # # Sort by number of projects that use each artifact
    # artifacts_by_projects = [(artifact, len(projects)) for artifact, projects in all_deps['artifact_projects'].items()]
    # artifacts_by_projects.sort(key=lambda x: x[1], reverse=True)
    
    # for i, (artifact, project_count) in enumerate(artifacts_by_projects[:15], 1):
    #     total_usage = artifact_counts[artifact]
    #     versions = len(set(all_deps['versions'][artifact]))
    #     print(f"{i:2d}. {artifact:<35} | {project_count:3d} projects | {total_usage:3d} total uses | {versions} versions")

def calculate_all_recursive_dependents(all_deps):
    """Calculate recursive dependents for all artifacts using iterative BFS."""
    result = {}
    
    for artifact in all_deps['artifact_projects']:
        visited = set()
        queue = [artifact]
        all_dependents = set()
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            direct_deps = all_deps['artifact_projects'].get(current, set())
            all_dependents.update(direct_deps)
            queue.extend(direct_deps)
        
        result[artifact] = all_dependents
    
    return result

def export_to_excel(all_deps, output_file, recursive=False):
    """Export analysis results to Excel file."""
    # Calculate recursive dependents if requested
    if recursive:
        recursive_deps_cache = calculate_all_recursive_dependents(all_deps)
    
    # Prepare data for Excel export
    excel_data = []
    
    for artifact_name, projects in all_deps['artifact_projects'].items():
        # Get unique projects (dependents)
        unique_dependents = sorted(list(projects))
        unique_dependents_str = ', '.join(unique_dependents)
        
        # Calculate total dependents based on recursive flag
        if recursive:
            total_dependents = len(recursive_deps_cache[artifact_name])
        else:
            total_dependents = len(projects)
        
        # Get unique versions for this artifact
        versions = list(set(all_deps['versions'][artifact_name]))
        versions = [v for v in versions if v and v != 'N/A']  # Remove empty/N/A versions
        if not versions:  # If no real versions, include N/A
            versions = ['N/A']
        unique_versions_str = ', '.join(sorted(versions))
        total_unique_versions = len(versions)
        
        # Get dependent:version combinations
        dependent_versions = sorted(list(all_deps['project_versions'][artifact_name]))
        dependent_versions_str = ', '.join(dependent_versions)
        
        excel_data.append({
            'Artifact Name': artifact_name,
            'List of Unique Dependents': unique_dependents_str,
            'Total Number of Dependents': total_dependents,
            'List of Unique Versions': unique_versions_str,
            'Total Number of Unique Versions': total_unique_versions,
            'Dependent:Version': dependent_versions_str
        })
    
    # Sort by total number of dependents (descending)
    excel_data.sort(key=lambda x: x['Total Number of Dependents'], reverse=True)
    
    try:
        # Create DataFrame and export to Excel
        df = pd.DataFrame(excel_data)
        
        # Create Excel writer with multiple sheets
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Main sheet with all artifacts
            df.to_excel(writer, sheet_name='Artifact Usage', index=False)
            
            # Summary sheet
            total_projects = len(set(proj for projects in all_deps['artifact_projects'].values() for proj in projects))
            summary_data = {
                'Metric': [
                    'Total Unique Artifacts',
                    'Total Projects Analyzed',
                    'Average Dependencies per Project',
                    'Most Used Artifact',
                    'Most Used Artifact Project Count',
                    'Analysis Date'
                ],
                'Value': [
                    len(all_deps['artifact_projects']),
                    total_projects,
                    round(len(all_deps['artifacts']) / total_projects, 1) if total_projects > 0 else 0,
                    excel_data[0]['Artifact Name'] if excel_data else 'N/A',
                    excel_data[0]['Total Number of Dependents'] if excel_data else 0,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Top 20 most used artifacts
            top_20_df = df.head(20)
            top_20_df.to_excel(writer, sheet_name='Top 20 Most Used', index=False)
        
        return True, f"Excel file exported successfully to: {output_file}"
    except ImportError:
        return False, "pandas/openpyxl not available. Please install with: pip install pandas openpyxl"
    except Exception as e:
        return False, f"Error exporting to Excel: {str(e)}"

if __name__ == "__main__":
    json_directory = "/Users/PLin/Workspace/analysis/com_trustwave-com_trustwave_dna/json"
    
    print("🚀 Starting dependency analysis...")
    all_deps, projects, errors = analyze_json_files(json_directory)
    print_analysis_results(all_deps, projects, errors)
    
    # Export to Excel
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_file = f"/Users/PLin/Workspace/analysis/dependency_analysis_{timestamp}.xlsx"
    
    print(f"\n📊 Exporting results to Excel...")
    success, message = export_to_excel(all_deps, excel_file, recursive=False)
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"⚠️ {message}")
        print("💡 To enable Excel export, install required packages:")
        print("   pip install pandas openpyxl")
