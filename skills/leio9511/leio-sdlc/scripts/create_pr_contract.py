#!/usr/bin/env python3
import argparse
import os
import re
import sys

def calculate_index(job_dir, insert_after):
    base_pattern = re.compile(r"^PR_(\d+)_.*\.md$")
    if not insert_after:
        max_base = 0
        for f in os.listdir(job_dir):
            match = base_pattern.match(f)
            if match:
                max_base = max(max_base, int(match.group(1)))
        return f"{max_base + 1:03d}"
    else:
        sub_pattern = re.compile(rf"^PR_{insert_after}_(\d+)_.*\.md$")
        max_sub = 0
        for f in os.listdir(job_dir):
            match = sub_pattern.match(f)
            if match:
                max_sub = max(max_sub, int(match.group(1)))
        return f"{insert_after}_{max_sub + 1}"

def main():
    parser = argparse.ArgumentParser(description="Create a PR contract file.")
    parser.add_argument("--job-dir", required=True, help="Path to job queue directory")
    parser.add_argument("--title", required=True, help="PR title")
    parser.add_argument("--content-file", required=True, help="Path to file with PR content")
    parser.add_argument("--insert-after", help="Prefix of the PR to insert after (e.g., 003)")
    args = parser.parse_args()

    # Validate content file
    if not os.path.exists(args.content_file):
        print(f"Error: Content file '{args.content_file}' not found.")
        sys.exit(1)

    # Validate/Create job dir
    os.makedirs(args.job_dir, exist_ok=True)

    # Calculate new index
    index = calculate_index(args.job_dir, args.insert_after)

    # Format title
    safe_title = args.title.replace(" ", "_")
    filename = f"PR_{index}_{safe_title}.md"
    file_path = os.path.join(args.job_dir, filename)

    # Read content
    with open(args.content_file, "r") as f:
        content = f.read()

    # Write new file
    with open(file_path, "w") as f:
        f.write("status: open\n\n")
        f.write(content)

    print(f"[PR_CREATED] {file_path}")

if __name__ == "__main__":
    main()
