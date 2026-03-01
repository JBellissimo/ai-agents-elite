"""
meeting_prep_agent.py -- Meeting Prep Agent for Bellissimo OS

Given a person's name + optional email/LinkedIn context:
    1. Web searches for their background (3 targeted queries via DuckDuckGo)
    2. Calls Claude to synthesize research into a structured brief
    3. Saves as markdown file to meeting_briefs/
    4. Returns (brief_text, file_path) to the caller

Triggered by !meetingprep [name] in Telegram.
Context (email thread, LinkedIn message) is optionally provided by the user
before the agent runs — the Telegram handler asks for it explicitly.

WHY this pattern (research → Claude → template):
    Raw search results are noise. Claude turns them into signal.
    The template forces the output into something usable 60 seconds before a call.
    Context (emails) is the highest-quality signal — it comes first in the prompt.
"""

import os
import re
import anthropic
from datetime import date
from pathlib import Path

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Paths — relative to this file so they work identically locally and on VPS
_HERE = Path(__file__).parent
BRIEFS_DIR = _HERE / "meeting_briefs"


# ---------------------------------------------------------------------------
# WEB SEARCH
# ---------------------------------------------------------------------------

def _web_search(query: str, max_results: int = 4) -> list[dict]:
    """
    Searches DuckDuckGo. Returns list of {title, href, body} dicts.
    Falls back gracefully if duckduckgo-search is unavailable or rate-limited.
    """
    try:
        from duckduckgo_search import DDGS
        return list(DDGS().text(query, max_results=max_results))
    except Exception as e:
        return [{"title": "Search unavailable", "href": "", "body": str(e)}]


def _research_person(name: str) -> str:
    """
    Runs 3 targeted searches and returns a consolidated research block.
    Queries: general identity, professional background, recent news.
    """
    queries = [
        name,
        f"{name} professional background career",
        f"{name} 2025 2026 news company announcement",
    ]

    blocks = []
    for query in queries:
        results = _web_search(query, max_results=4)
        for r in results:
            title = r.get("title", "").strip()
            body = r.get("body", "").strip()
            href = r.get("href", "").strip()
            if body:
                blocks.append(f"[{title}]\n{body}\nSource: {href}")

    return "\n\n---\n\n".join(blocks) if blocks else "[No research results found]"


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _slug(name: str) -> str:
    """'Bryan Gelnett' -> 'bryan-gelnett'"""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _load_north_star(max_chars: int = 2000) -> str:
    """Load STRATEGIC_NORTH_STAR.md as context for the prompt."""
    path = _HERE / "STRATEGIC_NORTH_STAR.md"
    try:
        text = path.read_text(encoding="utf-8")
        if len(text) > max_chars:
            text = text[:max_chars] + "\n...[truncated]"
        return text
    except FileNotFoundError:
        return "[STRATEGIC_NORTH_STAR.md not found]"


# ---------------------------------------------------------------------------
# BRIEF GENERATION
# ---------------------------------------------------------------------------

def run_meeting_prep(name: str, context: str = "") -> tuple[str, Path]:
    """
    Main entry point. Orchestrates: research -> Claude -> save -> return.

    Args:
        name:    Person's full name (e.g., "Bryan Gelnett")
        context: Optional email/LinkedIn thread pasted by user. Empty if skipped.

    Returns:
        (brief_text, file_path) — text to send to Telegram, path to saved .md file

    Runs synchronously. Wrap in asyncio.to_thread() from async callers.
    """
    BRIEFS_DIR.mkdir(exist_ok=True)

    research = _research_person(name)
    north_star = _load_north_star()
    today = date.today().strftime("%Y-%m-%d")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    system_prompt = f"""You are Bellissimo OS — JB's personal operating system and chief of staff.

JB runs two businesses:
- Bellissimo AI Labs: AI consulting firm. Builds company operating systems + AI automation.
  Pricing: $5K-$15K build fee + $1K-$3K/mo retainer. ICP: $3-20M revenue companies.
- SustainCFO: Fractional CFO practice. ~$1M ARR, 12-15 clients.
  Pricing: $2,500-$7,500/mo. ICP: Growth-stage companies without a full-time CFO.

Strategic context:
{north_star}

YOUR JOB:
Generate a meeting prep brief JB will read 60 seconds before his call.
Be direct. No filler. Identify the real opportunity and give JB the exact words.

OUTPUT FORMAT (use exactly this structure — no deviations):

# Meeting Prep: {name}
Date: {today}

---

## BACKGROUND
[2-3 paragraphs. Who they are. Role, company, career arc. What's notable about
their current position. Any relevant recent news, posts, or announcements.]

## OPPORTUNITY
[1-2 paragraphs. Be specific. Name the service (SustainCFO or Bellissimo),
the problem they likely have, and the revenue potential. If this is a
relationship/career/advisory play rather than a sale, say so explicitly.]

## CONVERSATION SCRIPT

**Opener:**
> [One opening line — warm but purposeful. Gets them talking immediately.]

**Discovery:**
> [Question 1 — surfaces their current situation]
> [Question 2 — identifies the gap or opportunity]

**Pivot (when the moment is right):**
> [The bridge from their world to your solution. One sentence.]

**Close:**
> [The specific ask or next step. Concrete. Direct.]

---
*Generated by Bellissimo OS*"""

    # Build user message — context (email/LinkedIn) comes first if provided
    # because it's the highest-quality signal
    user_parts = []
    if context:
        user_parts.append(
            f"CONTEXT (email/LinkedIn thread provided by JB — highest priority):\n{context}"
        )
    user_parts.append(
        f"WEB RESEARCH on {name}:\n\n{research}"
    )
    user_parts.append(f"Generate the meeting prep brief for {name}.")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1200,
        system=system_prompt,
        messages=[{"role": "user", "content": "\n\n---\n\n".join(user_parts)}],
    )

    brief_text = response.content[0].text

    # Save to file
    filename = f"{today}_{_slug(name)}.md"
    file_path = BRIEFS_DIR / filename
    file_path.write_text(brief_text, encoding="utf-8")

    return brief_text, file_path
