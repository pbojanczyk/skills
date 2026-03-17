#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess
import uuid

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--job-dir", required=True)
    args = parser.parse_args()

    with open("/root/.openclaw/workspace/leio-sdlc/SKILL.md", "r") as f:
        skill_text = f.read()

    # We tell the Manager to run in the current directory, which in the test is the sandbox.
    # We must explicitly tell it to cd to the sandbox because openclaw agent starts in workspace root.
    cwd = os.getcwd()
    rel_cwd = os.path.relpath(cwd, "/root/.openclaw/workspace")

    task_string = f"""
You are the leio-sdlc Manager. 
CRITICAL: You are running in a test sandbox! Before doing anything, you MUST run:
`cd {rel_cwd}`

Then, process the job directory: {args.job_dir}
Follow your runbook strictly. When finished, output [DONE] and exit.

--- RUNBOOK ---
{skill_text}
"""
    
    session_id = f"mgr-{uuid.uuid4().hex[:8]}"
    cmd = ["openclaw", "agent", "--session-id", session_id, "-m", task_string]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Manager Agent Failed: {result.stderr}")
        sys.exit(1)
    else:
        print(result.stdout)

if __name__ == "__main__":
    main()
