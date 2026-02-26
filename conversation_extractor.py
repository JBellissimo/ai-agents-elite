"""
conversation_extractor.py — Thread 9: Conversation Intelligence

Reads all local Claude Code JSONL transcripts across all projects,
extracts action items / decisions / follow-ups using Claude API,
and outputs a structured markdown report.

Usage:
    python conversation_extractor.py                    # all projects, last 7 days
    python conversation_extractor.py --days 30          # last 30 days
    python conversation_extractor.py --project ai-agents-elite   # one project only
    python conversation_extractor.py --post-discord     # also post summary to Discord

Output:
    Prints to stdout + writes CONVERSATION_INTEL.md in this project's folder
"""

import os
import json
import argparse
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dotenv import load_dotenv
import anthropic

load_dotenv()

# ─── Config ────────────────────────────────────────────────────────────────────

CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"
OUTPUT_FILE = Path(__file__).parent / "CONVERSATION_INTEL.md"

# Discord webhook (optional — set in .env if you want to post summaries)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ─── Transcript Reading ─────────────────────────────────────────────────────────

def get_project_dirs(filter_name: str = "") -> list[Path]:
    """Find all Claude Code project directories."""
    if not CLAUDE_PROJECTS_DIR.exists():
        print(f"Claude projects dir not found: {CLAUDE_PROJECTS_DIR}")
        return []
    dirs = [d for d in CLAUDE_PROJECTS_DIR.iterdir() if d.is_dir()]
    if filter_name:
        dirs = [d for d in dirs if filter_name.lower() in d.name.lower()]
    return sorted(dirs)

def human_project_name(dir_name: str) -> str:
    """Convert 'c--Users-Admin-Documents-Projects-ai-agents-elite' to 'ai-agents-elite'."""
    parts = dir_name.replace("--", "/").replace("-", " ").split("/")
    # Return the last meaningful segment
    return parts[-1].strip() if parts else dir_name

def read_jsonl_transcript(jsonl_path: Path, since: datetime) -> list[dict]:
    """
    Read a JSONL transcript and extract human + assistant turns newer than `since`.
    Returns list of {"role": "user"|"assistant", "text": str, "timestamp": str}
    """
    messages = []
    try:
        with open(jsonl_path, encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                msg_type = obj.get("type")
                if msg_type not in ("user", "assistant"):
                    continue

                # Parse timestamp
                ts_str = obj.get("timestamp", "")
                if ts_str:
                    try:
                        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                        if ts < since:
                            continue
                    except ValueError:
                        pass

                # Extract text content
                message = obj.get("message", {})
                content = message.get("content", "")

                if isinstance(content, str):
                    text = content.strip()
                elif isinstance(content, list):
                    # Pull text blocks, skip tool_use / tool_result
                    parts = []
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            parts.append(block.get("text", ""))
                    text = "\n".join(parts).strip()
                else:
                    continue

                if not text:
                    continue

                # Strip system-reminder injections (they add noise)
                text = re.sub(r"<system-reminder>.*?</system-reminder>", "", text, flags=re.DOTALL)
                text = text.strip()

                if text:
                    messages.append({
                        "role": "user" if msg_type == "user" else "assistant",
                        "text": text[:2000],  # cap per message to manage token count
                        "timestamp": ts_str,
                    })
    except Exception as e:
        print(f"  Error reading {jsonl_path.name}: {e}")
    return messages

def collect_conversations(since: datetime, project_filter: str = "") -> dict[str, list[dict]]:
    """
    Collect all conversations from all projects newer than `since`.
    Returns: {project_name: [messages]}
    """
    project_dirs = get_project_dirs(project_filter)
    result = {}

    for project_dir in project_dirs:
        project_name = human_project_name(project_dir.name)
        jsonl_files = sorted(project_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)

        all_messages = []
        for jsonl_file in jsonl_files:
            # Quick mtime check before parsing
            mtime = datetime.fromtimestamp(jsonl_file.stat().st_mtime, tz=timezone.utc)
            if mtime < since:
                continue
            msgs = read_jsonl_transcript(jsonl_file, since)
            all_messages.extend(msgs)

        if all_messages:
            result[project_name] = all_messages

    return result

# ─── Extraction with Claude ─────────────────────────────────────────────────────

EXTRACTION_SYSTEM = """You are an action intelligence analyst. You receive conversation transcripts
from Claude Code sessions and extract what matters for a solo operator running two businesses
(Bellissimo AI Labs — AI consulting firm, SustainCFO — fractional CFO practice).

For each project's conversation, extract and return ONLY:

## Open Action Items
Bullet list of things the user said they would do, or that were assigned to them. Include who/what it's blocked on.

## Decisions Made
Bullet list of choices locked in during this conversation (tech decisions, business decisions, strategy calls).

## Follow-Ups Needed
Things that were discussed but left unresolved — requiring the user's input, an external party, or a future session.

## Key Outputs Created
Files built, features shipped, tools written.

Be ruthlessly concise. No filler. Only include items that have actionable weight.
If a category is empty, write "None." and move on."""

def extract_intel(project_name: str, messages: list[dict]) -> str:
    """Send conversation transcript to Claude and get structured extraction."""
    # Build a condensed transcript (user messages are most important)
    transcript_parts = []
    for msg in messages[-80:]:  # last 80 turns max
        role_label = "JB" if msg["role"] == "user" else "Claude"
        # User messages get full text; Claude responses get truncated
        text = msg["text"] if msg["role"] == "user" else msg["text"][:500]
        transcript_parts.append(f"[{role_label}]: {text}")

    transcript = "\n\n".join(transcript_parts)

    try:
        response = anthropic_client.messages.create(
            model="claude-haiku-4-5-20251001",  # Fast + cheap for extraction
            max_tokens=1000,
            system=EXTRACTION_SYSTEM,
            messages=[{
                "role": "user",
                "content": f"Project: {project_name}\n\nConversation transcript:\n\n{transcript}"
            }]
        )
        return response.content[0].text
    except Exception as e:
        return f"Error extracting: {e}"

# ─── Output ────────────────────────────────────────────────────────────────────

def build_report(conversations: dict[str, list[dict]], since: datetime) -> str:
    """Build the full markdown report across all projects."""
    now = datetime.now(tz=timezone.utc)
    since_label = since.strftime("%Y-%m-%d")
    now_label = now.strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"# Conversation Intelligence Report",
        f"Generated: {now_label} | Period: {since_label} → now",
        f"Projects analyzed: {len(conversations)}",
        "",
        "---",
        "",
    ]

    for project_name, messages in sorted(conversations.items()):
        turn_count = len(messages)
        print(f"  Extracting intel for: {project_name} ({turn_count} turns)...")

        intel = extract_intel(project_name, messages)

        lines.append(f"## {project_name}")
        lines.append(f"*{turn_count} conversation turns analyzed*")
        lines.append("")
        lines.append(intel)
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)

def post_to_discord(report: str):
    """Post a condensed version to Discord via webhook."""
    try:
        import urllib.request
        # Discord message limit is 2000 chars — post a truncated version
        summary = f"**Conversation Intel Report** ({datetime.now().strftime('%Y-%m-%d')})\n\n"
        summary += report[:1800] + ("..." if len(report) > 1800 else "")
        payload = json.dumps({"content": summary}).encode("utf-8")
        req = urllib.request.Request(
            DISCORD_WEBHOOK_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        urllib.request.urlopen(req)
        print("  Posted to Discord.")
    except Exception as e:
        print(f"  Discord post failed: {e}")

# ─── CLI Entry Point ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Extract action intel from Claude Code sessions")
    parser.add_argument("--days", type=int, default=7, help="Look back N days (default: 7)")
    parser.add_argument("--project", type=str, default="", help="Filter to one project name")
    parser.add_argument("--post-discord", action="store_true", help="Post summary to Discord webhook")
    parser.add_argument("--no-save", action="store_true", help="Print only, don't write file")
    args = parser.parse_args()

    since = datetime.now(tz=timezone.utc) - timedelta(days=args.days)
    print(f"\nConversation Extractor — scanning last {args.days} days")
    print(f"Projects dir: {CLAUDE_PROJECTS_DIR}")
    if args.project:
        print(f"Filtering to projects matching: {args.project}")
    print()

    print("Collecting conversations...")
    conversations = collect_conversations(since, args.project)

    if not conversations:
        print("No conversations found in the specified time window.")
        return

    print(f"Found {len(conversations)} projects with activity. Extracting intel...\n")
    report = build_report(conversations, since)

    print("\n" + "=" * 60)
    # Safe print for Windows terminals that don't support all Unicode
    safe_report = report.encode("ascii", errors="replace").decode("ascii")
    print(safe_report)
    print("=" * 60)

    if not args.no_save:
        OUTPUT_FILE.write_text(report, encoding="utf-8")
        print(f"\nReport saved to: {OUTPUT_FILE}")

    if args.post_discord and DISCORD_WEBHOOK_URL:
        post_to_discord(report)
    elif args.post_discord:
        print("DISCORD_WEBHOOK_URL not set in .env — skipping Discord post")

if __name__ == "__main__":
    main()
