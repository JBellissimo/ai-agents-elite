"""
brief_agent.py -- Daily Briefing Agent for Bellissimo OS

Reads all active tasks from Supabase, calls Claude, returns a prioritized
daily brief. Used by:
    - Scheduled 5am job (automatic)
    - /brief command (on-demand)
    - !brief message handler (on-demand)

WHY Claude here (not just a sorted list):
    138 tasks. JB needs to know which 3 matter TODAY and WHY.
    The Theory of Constraints says one bottleneck limits everything.
    Claude finds it. A sorted list cannot.

CONTEXT LOADING:
    Reads STRATEGIC_NORTH_STAR.md and PROJECT_THREADS.md at runtime so the
    brief is grounded in actual strategy, not just the task list.
    Both files live next to this script on VPS (/opt/bellissimo/).
"""

import os
import anthropic
from datetime import date
from pathlib import Path

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Resolve paths relative to this file so it works locally and on VPS
_HERE = Path(__file__).parent


def _load_context_file(filename: str, max_chars: int = 3000) -> str:
    """Load a markdown context file, truncating if needed to save tokens."""
    path = _HERE / filename
    try:
        text = path.read_text(encoding="utf-8")
        if len(text) > max_chars:
            text = text[:max_chars] + "\n...[truncated]"
        return text
    except FileNotFoundError:
        return f"[{filename} not found]"


def _format_tasks_for_prompt(tasks: list[dict]) -> str:
    lines = []
    for t in tasks:
        flag = "[URGENT]" if t.get("priority") == "urgent" else ""
        area = t.get("area") or "General"
        title = t["title"]
        next_action = t.get("next_action") or ""
        notes = t.get("notes") or ""

        line = f"- {flag} [{area}] {title}"
        if next_action and next_action != "--":
            line += f"\n  Next: {next_action}"
        if notes:
            line += f"\n  Notes: {notes}"
        lines.append(line)
    return "\n".join(lines)


def generate_brief(tasks: list[dict]) -> str:
    """
    Calls Claude with all active tasks and returns a formatted daily brief.
    Runs synchronously -- wrap in asyncio.to_thread() from async callers.
    """
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    today = date.today().strftime("%A, %B %d").replace(" 0", " ")  # "Saturday, February 28" (cross-platform)
    task_text = _format_tasks_for_prompt(tasks)

    # Load live strategy context so the brief is grounded in what's actually true
    north_star = _load_context_file("STRATEGIC_NORTH_STAR.md", max_chars=3000)
    threads = _load_context_file("PROJECT_THREADS.md", max_chars=2500)

    system_prompt = f"""You are Bellissimo OS — JB's personal operating system and chief of staff.

=== STRATEGIC CONTEXT (read this first) ===
{north_star}

=== ACTIVE WORK THREADS ===
{threads}

=== YOUR MISSION ===
JB reads this brief on his iPhone at 5am. It must be immediately actionable.
North star metric: Revenue per JB hour. Everything else is noise.

REASONING FRAMEWORK (apply in order):
1. Theory of Constraints: What ONE bottleneck is limiting the $20M goal right now?
2. Revenue filter: Of all tasks, which directly creates or protects revenue today?
3. Inversion: What would guarantee today is wasted?

OUTPUT FORMAT (strict):
Today: {today}

TOP 3 TODAY:
1. [task] — [one sentence why this is #1]
2. [task] — [one sentence why]
3. [task] — [one sentence why]

TIME-SENSITIVE:
[anything with a deadline in the next 7 days, or "None"]

DEFER:
[one thing NOT to do today and why]

CONSTRAINT:
[the single bottleneck to the $20M goal right now, in one sentence]

Be direct. No filler. JB wants to be pushed, not agreed with."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system=system_prompt,
        messages=[{
            "role": "user",
            "content": f"Active tasks ({len(tasks)} total):\n\n{task_text}\n\nGenerate today's brief."
        }]
    )

    return response.content[0].text
