import argparse
import os
import sys
import subprocess
import uuid
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Spawn a coder subagent")
    parser.add_argument("--pr-file", required=True, help="Path to the PR Contract file")
    parser.add_argument("--prd-file", required=True, help="Path to the PRD file")
    parser.add_argument("--feedback-file", required=False, help="Path to the Review Report / Feedback file")
    args = parser.parse_args()

    if not os.path.exists(args.pr_file):
        print(f"[Pre-flight Failed] Coder cannot start. PR Contract not found at '{args.pr_file}'. You must run spawn_planner.py first.")
        sys.exit(1)

    test_mode = os.environ.get("SDLC_TEST_MODE") == "true"

    if test_mode:
        log_entry = str({'tool': 'spawn_coder', 'args': {'pr_file': args.pr_file, 'prd_file': args.prd_file, 'feedback_file': args.feedback_file}})
        
        # Ensure tests dir exists
        Path("tests").mkdir(exist_ok=True)
        
        with open("tests/tool_calls.log", "a") as f:
            f.write(log_entry + "\n")
        
        print('{"status": "mock_success", "role": "coder"}')
        sys.exit(0)
    else:
        try:
            with open(args.pr_file, "r") as f:
                pr_content = f.read()
            with open(args.prd_file, "r") as f:
                prd_content = f.read()
        except FileNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)
            
        task_string = f"You are a Coder. Please implement the PR Contract below.\n\n--- PR Contract ({args.pr_file}) ---\n{pr_content}\n\n--- PRD ({args.prd_file}) ---\n{prd_content}\n"
        
        if args.feedback_file:
            try:
                with open(args.feedback_file, "r") as f:
                    feedback_content = f.read()
                task_string += f"\n--- Revision Feedback ---\n{feedback_content}\n\nYou are in a revision loop. Your previous attempt was rejected. Address the feedback above and modify the codebase accordingly."
            except FileNotFoundError as e:
                print(f"Error: {e}")
                sys.exit(1)

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
