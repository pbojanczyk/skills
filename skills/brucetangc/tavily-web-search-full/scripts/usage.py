#!/usr/bin/env python3
"""
Tavily Usage API - Check API usage and credits
Based on: https://docs.tavily.com/documentation/api-reference/endpoint/usage

Usage:
    python3 usage.py
    python3 usage.py --json
"""
import json
import os
import pathlib
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime
from typing import Optional, Dict, Any

# Constants
TAVILY_URL = "https://api.tavily.com/usage"
LOG_FILE = pathlib.Path.home() / ".openclaw" / "logs" / "tavily_usage.log"
MAX_RETRIES = 3
RETRY_DELAY = 1.0


# ============================================================================
# Logging
# ============================================================================

def log(message: str, level: str = "INFO"):
    """Simple logging to file and stderr"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}\n"
    print(log_line.strip(), file=sys.stderr)
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception:
        pass


# ============================================================================
# API Key Management
# ============================================================================

def load_key() -> str:
    """Load API key from environment or .env file"""
    key = os.environ.get("TAVILY_API_KEY")
    if key:
        return key.strip()

    env_path = pathlib.Path.home() / ".openclaw" / ".env"
    if env_path.exists():
        try:
            txt = env_path.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r"^\s*TAVILY_API_KEY\s*=\s*(.+?)\s*$", txt, re.M)
            if m:
                v = m.group(1).strip().strip('"').strip("'")
                if v:
                    return v
        except Exception as e:
            log(f"Error reading .env: {e}", "ERROR")

    return None


# ============================================================================
# Tavily Usage API
# ============================================================================

def get_usage(project_id: Optional[str] = None) -> Dict:
    """Get API usage information"""
    key = load_key()
    if not key:
        log("Missing API key", "ERROR")
        raise SystemExit(
            "Missing TAVILY_API_KEY. Set env var TAVILY_API_KEY or add it to ~/.openclaw/.env"
        )

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log(f"Request attempt {attempt}/{MAX_RETRIES}", "DEBUG")
            
            # Build URL with optional project_id
            url = TAVILY_URL
            if project_id:
                url += f"?project_id={project_id}"
            
            req = urllib.request.Request(
                url,
                headers={
                    "Authorization": f"Bearer {key}",
                    "Accept": "application/json",
                },
                method="GET",
            )

            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8", errors="replace")

            try:
                obj = json.loads(body)
            except json.JSONDecodeError as e:
                log(f"JSON decode error: {e}", "ERROR")
                raise SystemExit(f"Tavily returned non-JSON: {body[:300]}")

            if "error" in obj:
                error_msg = obj.get("error", {}).get("message", "Unknown error")
                log(f"API error: {error_msg}", "ERROR")
                raise SystemExit(f"Tavily API error: {error_msg}")

            log(f"Success", "INFO")
            return obj

        except urllib.error.HTTPError as e:
            last_error = f"HTTP {e.code}: {e.reason}"
            log(f"HTTP error (attempt {attempt}): {last_error}", "ERROR")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)
                continue
            break
            
        except urllib.error.URLError as e:
            last_error = f"URL error: {e.reason}"
            log(f"Network error (attempt {attempt}): {last_error}", "ERROR")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)
                continue
            break
            
        except Exception as e:
            last_error = str(e)
            log(f"Unexpected error (attempt {attempt}): {last_error}", "ERROR")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)
                continue
            break

    log(f"All retries failed: {last_error}", "ERROR")
    raise SystemExit(f"Tavily usage request failed after {MAX_RETRIES} attempts: {last_error}")


# ============================================================================
# Output Formatters
# ============================================================================

def format_usage_human(usage: Dict) -> str:
    """Format usage information for human reading"""
    lines = []
    
    # Account info
    lines.append("## Tavily API Usage")
    lines.append("")
    
    # Credits
    if "credits" in usage:
        credits = usage["credits"]
        lines.append("### Credits")
        lines.append("")
        
        used = credits.get("used", 0)
        remaining = credits.get("remaining", 0)
        total = used + remaining
        
        # Calculate percentage
        pct_used = (used / total * 100) if total > 0 else 0
        
        lines.append(f"- **Used**: {used:,}")
        lines.append(f"- **Remaining**: {remaining:,}")
        lines.append(f"- **Total**: {total:,}")
        lines.append(f"- **Usage**: {pct_used:.1f}%")
        lines.append("")
        
        # Visual bar
        bar_width = 30
        filled = int(bar_width * pct_used / 100)
        bar = "█" * filled + "░" * (bar_width - filled)
        lines.append(f"`[{bar}]` {pct_used:.1f}%")
        lines.append("")
    
    # Requests breakdown
    if "requests" in usage:
        requests = usage["requests"]
        lines.append("### Requests by Endpoint")
        lines.append("")
        
        for endpoint, count in requests.items():
            lines.append(f"- **{endpoint}**: {count:,}")
        lines.append("")
    
    # Time range
    if "start_date" in usage or "end_date" in usage:
        lines.append("### Time Range")
        lines.append("")
        if "start_date" in usage:
            lines.append(f"- **Start**: {usage['start_date']}")
        if "end_date" in usage:
            lines.append(f"- **End**: {usage['end_date']}")
        lines.append("")
    
    # Project
    if "project_id" in usage:
        lines.append(f"### Project")
        lines.append("")
        lines.append(f"- **Project ID**: {usage['project_id']}")
        lines.append("")
    
    return "\n".join(lines).strip() + "\n"


def format_usage_compact(usage: Dict) -> str:
    """Format usage as compact summary"""
    lines = []
    
    if "credits" in usage:
        credits = usage["credits"]
        used = credits.get("used", 0)
        remaining = credits.get("remaining", 0)
        total = used + remaining
        pct_used = (used / total * 100) if total > 0 else 0
        
        lines.append(f"📊 Tavily API Usage")
        lines.append(f"   Used: {used:,} | Remaining: {remaining:,} | Total: {total:,}")
        lines.append(f"   Usage: {pct_used:.1f}%")
        
        # Warning if low on credits
        if remaining < 100:
            lines.append(f"   ⚠️  Low credits! ({remaining} remaining)")
        elif remaining < 500:
            lines.append(f"   ⚡ Moderate credits ({remaining} remaining)")
        else:
            lines.append(f"   ✅ Good credit balance")
    else:
        lines.append("No usage data available")
    
    return "\n".join(lines).strip() + "\n"


# ============================================================================
# Main
# ============================================================================

def main():
    import argparse
    
    ap = argparse.ArgumentParser(
        description="Tavily Usage - Check API usage and credits",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check usage (human-readable)
  %(prog)s

  # Check usage (compact)
  %(prog)s --compact

  # Check usage (JSON)
  %(prog)s --json

  # Check usage for specific project
  %(prog)s --project-id "my-project-123"
        """
    )
    
    # Output format
    ap.add_argument(
        "--json",
        action="store_true",
        help="Output as raw JSON"
    )
    ap.add_argument(
        "--compact",
        action="store_true",
        help="Output as compact summary (default)"
    )
    ap.add_argument(
        "--md",
        action="store_true",
        help="Output as detailed Markdown"
    )
    
    # Project filter
    ap.add_argument(
        "--project-id",
        help="Filter usage by project ID"
    )
    
    args = ap.parse_args()
    
    # Get usage
    usage = get_usage(project_id=args.project_id)
    
    # Output
    if args.json:
        json.dump(usage, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    elif args.md:
        sys.stdout.write(format_usage_human(usage))
    else:
        sys.stdout.write(format_usage_compact(usage))


if __name__ == "__main__":
    main()
