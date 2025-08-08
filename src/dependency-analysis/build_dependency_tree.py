import os
import sys
import subprocess
import json
from dotenv import load_dotenv

load_dotenv()

def main():
    # Get repos directory from environment
    repos_dir = os.getenv('REPOS_DIR')
    if not repos_dir:
        raise ValueError("REPOS_DIR environment variable is required")
    abs_folder = os.path.expanduser(repos_dir)
    if not os.path.isdir(abs_folder):
        print(f"Folder {abs_folder} does not exist.")
        sys.exit(1)
    os.chdir(abs_folder)

    # Loop through all folders in the current directory
    subfolders = [f for f in os.listdir('.') if os.path.isdir(f) and not f.startswith('.')]
    
    # List of specific subfolders to process
    folders_to_process = [
        "global-finding",
        "tw-parent-external",
        "tw-parent-api",
        "tw-parent-service"
    ]

    # If folders_to_process is not empty, filter subfolders to only those in folders_to_process
    if folders_to_process:
        subfolders = [f for f in subfolders if f in folders_to_process]

    for subfolder in subfolders:
        print("-" * 40)
        print(subfolder)
        os.chdir(abs_folder)
        subfolder_abs_path = os.path.abspath(subfolder)
        process_folder(subfolder_abs_path) 
        print("-" * 40)

    print("Final artifact_parent_map:")
    for k, v in process_folder.artifact_parent_map.items():
        print(f"  {k}: {v}")

def process_folder(abs_folder):
    print(f"Processing folder: {abs_folder}")
    
    pom_path = os.path.join(abs_folder, "pom.xml")
    if not os.path.isfile(pom_path):
        print(f"pom.xml not found in {abs_folder}, skipping.")
        # Check one level deeper for pom.xml
        subdirs = [d for d in os.listdir(abs_folder) if os.path.isdir(os.path.join(abs_folder, d))]
        found = False
        for subdir in subdirs:
            pom_path_deep = os.path.join(abs_folder, subdir, "pom.xml")
            if os.path.isfile(pom_path_deep):
                print(f"Found pom.xml in subdirectory: {pom_path_deep}")
                process_folder(os.path.join(abs_folder, subdir))
                found = True
        if found:
            analysis_dir = os.getenv('ANALYSIS_DIR')
            if not analysis_dir:
                raise ValueError("ANALYSIS_DIR environment variable is required")
            error_dir = os.path.join(os.path.expanduser(analysis_dir), "error")
            os.makedirs(error_dir, exist_ok=True)
            error_file_path = os.path.join(error_dir, f"{os.path.basename(abs_folder)}.error")
            with open(error_file_path, "w") as f:
                f.write(f"pom.xml not found in {abs_folder}, skipping.")
            return
    
    # Change directory to the folder containing pom.xml
    os.chdir(abs_folder)

    # Run mvn dependency:tree with outputType=json
    output_file_name = f"{os.path.basename(abs_folder)}.tmp"
    analysis_dir = os.getenv('ANALYSIS_DIR')
    if not analysis_dir:
        raise ValueError("ANALYSIS_DIR environment variable is required")
    output_json_dir = os.path.join(os.path.expanduser(analysis_dir), "json")
    output_file_path = os.path.join(output_json_dir, output_file_name)
    print(f"Running 'mvn dependency:tree -DoutputType=json -DoutputFile={output_file_path}' in {abs_folder} ...")
    result = subprocess.run(
        [
            "mvn",
            "dependency:tree",
            "-DoutputType=json",
            f"-DoutputFile={output_file_path}",
            "-Dincludes=com.trustwave,com.trustwave.dna"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Read parent info from pom.xml and store in a map
    artifact_id = os.path.basename(abs_folder)
    parent = read_pom_parent_and_version(pom_path)
    if not hasattr(process_folder, "artifact_parent_map"):
        process_folder.artifact_parent_map = {}
    process_folder.artifact_parent_map[artifact_id] = parent
    
    if result.returncode != 0:
        print(f"Maven command failed: {abs_folder}")
        analysis_dir = os.getenv('ANALYSIS_DIR')
        if not analysis_dir:
            raise ValueError("ANALYSIS_DIR environment variable is required")
        error_dir = os.path.join(os.path.expanduser(analysis_dir), "error")
        os.makedirs(error_dir, exist_ok=True)
        error_file_path = os.path.join(error_dir, f"{os.path.basename(abs_folder)}.error")
        with open(error_file_path, "w") as f:
            f.write(result.stderr)
        return
    
    # Change directory to ../json
    os.chdir(output_json_dir)

    # Call parse_tree.py
    parse_tree_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "parse_tree.py"))
    print(f"Calling parse_tree.py at {parse_tree_path} with input file {output_file_name} ...")
    if os.path.isfile(parse_tree_path):
        subprocess.run(
            [sys.executable, parse_tree_path, output_file_name, parent],
            check=True
        )
    else:
        print(f"parse_tree.py not found at {parse_tree_path}")

def read_pom_parent_and_version(pom_path):
    import xml.etree.ElementTree as ET
    if not os.path.isfile(pom_path):
        return None, None
    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()
        ns = {'m': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
        parent = None

        # Find parent groupId:artifactId:version if present
        parent_elem = root.find('m:parent', ns) if ns else root.find('parent')
        if parent_elem is not None:
            group_id = parent_elem.find('m:groupId', ns).text if ns else parent_elem.find('groupId').text
            artifact_id = parent_elem.find('m:artifactId', ns).text if ns else parent_elem.find('artifactId').text
            parent_version = parent_elem.find('m:version', ns).text if ns else parent_elem.find('version').text
            parent = f"{group_id}:{artifact_id}:{parent_version}"

       
        if parent_elem is not None:
            parent_version = parent_elem.find('m:version', ns).text if ns else parent_elem.find('version').text
            artifact_id = root.find('m:artifactId', ns).text if ns else root.find('artifactId').text
            print(f"Artifact: {artifact_id}, Parent: {parent}")
            return parent
        else:
            print(f"Parent: {parent}, Version: None")
            return parent
    except Exception as e:
        print(f"Error reading pom.xml: {e}")
        return None, None

if __name__ == "__main__":
    main()