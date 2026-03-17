#!/usr/bin/env python3
import argparse
import os
import glob
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--job-dir", required=True)
    args = parser.parse_args()

    job_dir = args.job_dir

    if not os.path.exists(job_dir):
        print(f"[Pre-flight Failed] Job directory '{job_dir}' does not exist.")
        sys.exit(1)

    pattern = os.path.join(job_dir, "*.md")
    md_files = glob.glob(pattern)
    md_files.sort()

    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if "status: open" in content:
                    print(md_file)
                    sys.exit(0)
        except Exception:
            pass
    
    print(f"[QUEUE_EMPTY] All PRs in {job_dir} are closed or blocked.")
    sys.exit(0)

if __name__ == "__main__":
    main()