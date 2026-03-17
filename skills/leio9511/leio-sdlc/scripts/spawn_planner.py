import argparse
import os
import json
import sys
import subprocess
import uuid

def main():
    parser = argparse.ArgumentParser(description="Spawn Planner Agent")
    parser.add_argument("--prd-file", required=True, help="Path to the PRD file")
    parser.add_argument("--out-dir", required=False, default="docs/PRs", help="Output directory for PRs")
    args = parser.parse_args()

    if not (os.path.isfile(args.prd_file) and os.path.getsize(args.prd_file) > 0):
        print(f"[Pre-flight Failed] Planner cannot start. PRD file not found at '{args.prd_file}'. You must read or create the PRD first.")
        sys.exit(1)

    test_mode = os.environ.get("SDLC_TEST_MODE", "").lower() == "true"

    if test_mode:
        os.makedirs("tests", exist_ok=True)
        log_entry = str({'tool': 'spawn_planner', 'args': {'prd_file': args.prd_file}})
        with open("tests/tool_calls.log", "a") as f:
            f.write(log_entry + "\n")
        print('{"status": "mock_success", "role": "planner"}')
        sys.exit(0)
    else:
        try:
            with open(args.prd_file, "r") as f:
                prd_content = f.read()
        except FileNotFoundError:
            print(f"Error: PRD file not found: {args.prd_file}")
            sys.exit(1)
            
        task_string = (
            f"You are the leio-sdlc Planner. Please analyze the following PRD:\n{prd_content}\n\n"
            f"CORE INSTRUCTION: You are forbidden from generating a single monolithic PR contract. "
            f"You must break the PRD down into a sequential, dependency-ordered chain of Micro-PRs. "
            f"You MUST use `python3 scripts/create_pr_contract.py --job-dir {args.out_dir} --title <title> --content-file <file>` "
            f"to generate the PR contracts instead of raw file writing. "
            f"EVERY generated PR contract MUST include `status: open` in its YAML frontmatter. "
            f"You MUST generate at least 2 Micro-PRs for this feature. Start now."
        )
        
        import time
        print("Calling OpenClaw real API...")
        session_id = f"subtask-{uuid.uuid4().hex[:8]}"
        cmd = ["openclaw", "agent", "--session-id", session_id, "-m", task_string]
        
        for attempt in range(3):
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("Successfully spawned Planner subagent.")
                print(result.stdout)
                break
            else:
                print(f"Error: subprocess returned non-zero exit status {result.returncode}")
                if result.stderr:
                    print(result.stderr)
                if attempt < 2:
                    sleep_time = 3 * (2 ** attempt)
                    time.sleep(sleep_time)
                else:
                    sys.exit(1)

if __name__ == "__main__":
    main()
