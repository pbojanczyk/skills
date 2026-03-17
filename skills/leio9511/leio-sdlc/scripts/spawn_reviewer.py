import argparse
import os
import sys
import subprocess
import uuid

def main():
    parser = argparse.ArgumentParser(description="Spawn a reviewer agent.")
    parser.add_argument("--pr-file", required=True, help="Path to the PR Contract file")
    parser.add_argument("--diff-target", required=True, help="Git diff target range (e.g., base_hash..latest_hash)")
    parser.add_argument("--override-diff-file", help="Override the diff file and skip git diff", default=None)
    parser.add_argument("--job-dir", required=False, default=".", help="Working directory for the Reviewer to generate artifacts")
    
    args = parser.parse_args()

    if not args.override_diff_file:
        diff_out = subprocess.run(["git", "diff", "HEAD"], capture_output=True, text=True).stdout
        if not diff_out or not diff_out.strip():
            print("[Pre-flight Failed] Reviewer cannot start. Git working tree is completely clean. The Coder did not write any code. You must spawn the Coder first.")
            sys.exit(1)
    
    # Check test mode
    if os.environ.get("SDLC_TEST_MODE") == "true":
        # Write to log
        log_dir = "tests"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "tool_calls.log")
        
        log_data = {'tool': 'spawn_reviewer', 'args': {'pr_file': args.pr_file, 'diff_target': args.diff_target, 'job_dir': args.job_dir}}
        
        with open(log_file, "a") as f:
            f.write(str(log_data) + "\n")
            
        print('{"status": "mock_success", "role": "reviewer"}')
        sys.exit(0)
    
    # Production mode
    if not os.path.exists(args.pr_file):
        print(f"Error: PR file not found: {args.pr_file}")
        sys.exit(1)
        
    with open(args.pr_file, "r") as f:
        pr_content = f.read()
        
    # [Anti-Poisoning Fix] Manager (this script) executes diff and saves to file proxy
    if args.override_diff_file:
        diff_file = args.override_diff_file
    else:
        diff_file = "current_review.diff"
        diff_cmd = f"git diff {args.diff_target} --no-color > {diff_file}"
        subprocess.run(diff_cmd, shell=True)
        
    task_string = (
        f"You are the Reviewer. Please strictly follow your playbook: playbooks/reviewer_playbook.md\n\n"
        f"--- PR Contract ---\n"
        f"{pr_content}\n"
        f"-------------------\n\n"
        f"I have already generated the code diff for you. "
        f"Use the `read` tool to read the file: {diff_file} \n"
        f"DO NOT execute `git diff` yourself. Read the file, analyze it internally, and write your verdict to Review_Report.md. "
        f"Your working directory is {args.job_dir}. You must generate Review_Report.md inside it."
    )
    
    import time
    session_id = f"subtask-{uuid.uuid4().hex[:8]}"
    cmd = ["openclaw", "agent", "--session-id", session_id, "-m", task_string]
    for attempt in range(3):
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
            break
        else:
            print(f"Error: subprocess returned non-zero exit status {result.returncode}")
            if attempt < 2:
                sleep_time = 3 * (2 ** attempt)
                time.sleep(sleep_time)
            else:
                sys.exit(1)

if __name__ == "__main__":
    main()
