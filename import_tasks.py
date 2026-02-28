#!/usr/bin/env python3
"""
import_tasks.py -- One-time import of MASTER_TASKS.md into Supabase.

Run from local machine (not VPS):
    python import_tasks.py

Deletes all existing tasks first, then re-inserts with full context.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
MASTER_TASKS_PATH = Path("MASTER_TASKS.md")

PRIORITY_MAP = {"p1": "urgent", "p2": "normal", "p3": "normal"}

SKIP_SECTIONS = {
    "Completed / Reference",
    "Agent OS Infrastructure (meta)",
}

SKIP_STATUSES = {"done", "--"}


def parse_tasks() -> list[dict]:
    content = MASTER_TASKS_PATH.read_text(encoding="utf-8")
    tasks = []
    current_section = None

    for line in content.splitlines():
        if line.startswith("## "):
            current_section = line[3:].strip()
            continue

        if not current_section or current_section in SKIP_SECTIONS:
            continue

        if not line.startswith("|"):
            continue

        cells = [c.strip() for c in line.split("|")[1:-1]]
        if not cells or not cells[0] or "---" in cells[0] or cells[0] == "Title":
            continue

        title = cells[0]

        # URGENT section: Title | Priority | Deadline | Notes
        if current_section == "URGENT \u2014 Do Today":
            priority_raw = cells[1] if len(cells) > 1 else "p1"
            notes = cells[3] if len(cells) > 3 else None
            next_action = None
            area = "Urgent"
            status_raw = "active"
        else:
            # Standard: Title | Status | Priority | Next Action | Notes
            status_raw = cells[1] if len(cells) > 1 else "backlog"
            priority_raw = cells[2] if len(cells) > 2 else "p2"
            next_action = cells[3] if len(cells) > 3 else None
            notes = cells[4] if len(cells) > 4 else None
            area = current_section

        if status_raw in SKIP_STATUSES:
            continue

        # Clean up empty/placeholder values
        next_action = next_action if next_action and next_action != "--" else None
        notes = notes if notes else None

        tasks.append({
            "title": title,
            "area": area,
            "status": "active",
            "priority": PRIORITY_MAP.get(priority_raw, "normal"),
            "next_action": next_action,
            "notes": notes,
        })

    return tasks


def main():
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("ERROR: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env")
        return

    tasks = parse_tasks()
    urgent = [t for t in tasks if t["priority"] == "urgent"]
    with_action = [t for t in tasks if t.get("next_action")]

    print(f"Parsed {len(tasks)} tasks from MASTER_TASKS.md")
    print(f"  Urgent: {len(urgent)}  |  Normal: {len(tasks) - len(urgent)}")
    print(f"  With next_action: {len(with_action)}\n")

    print("Sample (first 8):")
    for t in tasks[:8]:
        flag = "!!" if t["priority"] == "urgent" else "  "
        area = (t["area"] or "")[:20]
        action = f" -> {t['next_action'][:35]}" if t.get("next_action") else ""
        print(f"  {flag} [{area:<20}] {t['title'][:40]}{action}")
    if len(tasks) > 8:
        print(f"  ... and {len(tasks) - 8} more\n")

    confirm = input(f"\nDelete existing tasks and re-insert {len(tasks)}? [y/N] ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        return

    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

    # Delete all existing tasks
    client.table("tasks").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    print("Deleted existing tasks.")

    # Insert fresh
    result = client.table("tasks").insert(tasks).execute()
    print(f"Inserted {len(result.data)} tasks.")
    print("Run !tasks [area] from Telegram to verify.")


if __name__ == "__main__":
    main()
