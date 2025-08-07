import sys
import json
import re
import os

def parse_dependency_tree(lines):
    def parse_line(line):
        # Remove leading tree characters and spaces
        clean = re.sub(r'^([|\\+\- ]+)', '', line)
        return clean

    def parse_dep(dep_str):
        # Split into groupId, artifactId, type, version, scope
        parts = dep_str.split(':')
        if len(parts) < 5:
            return {"artifact": dep_str.rstrip('\n')}
        return {
            "groupId": parts[0],
            "artifactId": parts[1],
            "type": parts[2],
            "version": parts[3]
            # "scope": parts[4]
        }

    root = None
    stack = []

    for line in lines:
        if not line.strip():
            continue
        # Count depth by number of leading tree characters
        match = re.match(r'^([|\\+\- ]+)', line)
        depth = 0
        if match:
            depth = match.group(0).count('|') + match.group(0).count('+') + match.group(0).count('\\')
        dep_str = parse_line(line)
        dep = parse_dep(dep_str)
        dep["dependencies"] = []

        if depth == 0:
            root = dep
            stack = [(dep, depth)]
        else:
            # Find parent at depth-1
            while stack and stack[-1][1] >= depth:
                stack.pop()
            if stack:
                stack[-1][0]["dependencies"].append(dep)
            stack.append((dep, depth))
    return root

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_tree.py <tree.txt>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        lines = f.readlines()
    tree = parse_dependency_tree(lines)
    out_file = sys.argv[1].rsplit('.', 1)[0] + ".json"
    with open(out_file, "w") as out_f:
        json.dump(tree, out_f, indent=2)
        os.remove(sys.argv[1])