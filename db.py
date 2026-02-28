"""
db.py -- Supabase data layer for Bellissimo OS

Phase 1: Tasks only.
Phase 2+: Add projects, contacts, sessions tables.

Why a separate file:
    Keeps orchestrator.py focused on Telegram routing.
    All database logic lives here -- easy to test independently.

Table: tasks
    id          uuid (auto)
    created_at  timestamptz (auto)
    title       text
    area        text        -- Bellissimo, SustainCFO, Health, Personal, etc.
    status      text        -- 'active' | 'done'
    priority    text        -- 'urgent' | 'normal'
    notes       text
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")


def _client() -> Client:
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env"
        )
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


# ---------------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------------

def get_tasks(area: str = None, status: str = "active") -> list[dict]:
    """
    Returns active tasks, optionally filtered by area.
    area is case-insensitive partial match (e.g. 'sustain' matches 'SustainCFO').
    """
    q = _client().table("tasks").select("*").eq("status", status)
    if area:
        q = q.ilike("area", f"%{area}%")
    # Urgent tasks first, then by creation time
    result = q.order("priority", desc=True).order("created_at").execute()
    return result.data


def get_brief() -> list[dict]:
    """
    Returns all urgent active tasks across all areas.
    Used by !brief command.
    """
    result = (
        _client()
        .table("tasks")
        .select("*")
        .eq("status", "active")
        .eq("priority", "urgent")
        .order("created_at")
        .execute()
    )
    return result.data


# ---------------------------------------------------------------------------
# WRITE
# ---------------------------------------------------------------------------

def add_task(title: str, area: str = None, priority: str = "normal") -> dict:
    """
    Inserts a new task. Returns the created row.

    Parsing convention (handled by caller):
        '!add Call Marcus'              -> title='Call Marcus', area=None
        '!add [SustainCFO] Call Marcus' -> title='Call Marcus', area='SustainCFO'
        '!add !! Call Marcus'           -> title='Call Marcus', priority='urgent'
    """
    row = {"title": title, "priority": priority}
    if area:
        row["area"] = area
    result = _client().table("tasks").insert(row).execute()
    return result.data[0] if result.data else {}


def mark_done_by_match(search: str) -> dict | None:
    """
    Finds the first active task whose title contains `search` (case-insensitive)
    and marks it done. Returns the updated row, or None if not found.
    """
    result = (
        _client()
        .table("tasks")
        .select("*")
        .eq("status", "active")
        .ilike("title", f"%{search}%")
        .limit(1)
        .execute()
    )
    if not result.data:
        return None

    task_id = result.data[0]["id"]
    updated = (
        _client()
        .table("tasks")
        .update({"status": "done"})
        .eq("id", task_id)
        .execute()
    )
    return updated.data[0] if updated.data else None
