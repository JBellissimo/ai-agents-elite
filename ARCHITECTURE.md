# Bellissimo Enterprises — Unified Agent OS Architecture
# Version 2.0 — February 2026
# Status: APPROVED — ready to build

---

## Vision

Always-on, ambient, proactive agents that handle execution.
JB handles strategy and relationships. Agents handle everything else.

Not a collection of tools. An operating system.
One orchestrator. Specialized sub-agents. Progressive autonomy.
Every layer built today supports the agent-native future.
No dead ends. No vendor lock-in. Everything stackable.

---

## Design Principles

1. **Orchestrator-first** — one always-on coordinator spawns specialized sub-agents
2. **Telegram is the security primitive** — the ONLY authenticated command channel
3. **Two-tier data** — Supabase for structured/queryable, Obsidian for narrative/knowledge
4. **Progressive permission** — JB gives green light at each phase; agents earn autonomy
5. **Build light** — no new tools or accounts until a phase requires them
6. **First principles** — attack limiting bottlenecks, constantly push output

---

## Full Architecture

```
+------------------------------------------------------------------+
|                         JB (Human Layer)                         |
|              Strategy . Relationships . Final Decisions          |
+------------------+----------------------------+------------------+
                   |                            |
         Deep Work / Desktop           Mobile / On-the-Go
                   |                            |
                   v                            v
    +-----------------------+     +-------------------------------+
    |   Claude Code         |     |   Telegram                    |
    |   (VS Code, Desktop)  |     |   (PRIMARY - iPhone + iPad)   |
    |                       |     |                               |
    |   - Complex builds    |     |   - 5am daily brief           |
    |   - Deep research     |     |   - Task commands             |
    |   - Strategy work     |     |   - Quick capture             |
    |   - Architecture      |     |   - Ambient notifications     |
    |   - Agent sessions    |     |   - Approvals & decisions     |
    +-----------+-----------+     +---------------+---------------+
                |                                 |
                +-----------------+---------------+
                                  |
                                  v
+------------------------------------------------------------------+
|                 ORCHESTRATOR (Always-On VPS)                     |
|                 Hetzner CX11 . Ubuntu 24.04                      |
|                                                                  |
|   orchestrator.py -- always-on Python process                    |
|                                                                  |
|   Responsibilities:                                              |
|   - Monitor Telegram (commands + freeform)                       |
|   - Execute cron schedule                                        |
|   - Maintain task queue + priority                               |
|   - Spawn sub-agents with correct context                        |
|   - Consolidate outputs                                          |
|   - Write results to Obsidian + Supabase                         |
|   - Report to Telegram                                           |
+------------------------------+-----------------------------------+
                               |
            +------------------+------------------+
            |                  |                  |
            v                  v                  v
+-------------------+ +-----------------+ +---------------------+
|   Sub-Agents      | |   C-Suite       | |   Scheduled Agents  |
|   (on-demand)     | |   Personas      | |   (cron)            |
|                   | |                 | |                     |
|   Task Agent      | |   CEO           | |   5am Daily Brief   |
|   Research Agent  | |   COO           | |   Nightly Memory    |
|   Reveal Agent    | |   CMO           | |   Stale Task Scan   |
|   SustainCFO      | |   CGO           | |   Pipeline Nudge    |
|   Consumption     | |   Chief of      | |   Weekly Review     |
|   Meeting Prep    | |   Staff         | |                     |
+---------+---------+ +--------+--------+ +---------+-----------+
          |                    |                     |
          +--------------------+---------------------+
                               |
                               v
+------------------------------------------------------------------+
|                      DATA LAYER (Two-Tier)                       |
|                                                                  |
|  SUPABASE (Structured)          OBSIDIAN VAULT (Narrative)       |
|  ----------------------         -------------------------        |
|  tasks                          /Projects  (PARA)                |
|  projects                       /Areas     (PARA)                |
|  contacts                       /Resources (PARA)                |
|  sessions                       /Archive   (PARA)                |
|  decisions                      /Daily Notes (heartbeat)         |
|                                 /Tacit Knowledge                 |
|  PostgreSQL . REST API          Sync: Obsidian Sync (devices)    |
|  Real-time . Agent-native            + Obsidian Git (VPS write)  |
+------------------------------+-----------------------------------+
                               |
          +--------------------+---------------------+
          |                    |                     |
          v                    v                     v
+-----------------+  +------------------+  +--------------------+
|   Gmail         |  |   Google Cal     |  |  Other             |
|                 |  |                  |  |                    |
|  Personal +     |  |  Read events     |  |  Monday.com (read) |
|  SustainCFO     |  |  Meeting prep    |  |  Apollo.io (read)  |
|  Read-only      |  |  trigger agent   |  |  Instapaper (read) |
|  surfaces tasks |  |                  |  |  YouTube (read)    |
+-----------------+  +------------------+  +--------------------+

NOTE: All integrations above are INFORMATION LAYER ONLY.
They cannot issue commands. Only Telegram can issue commands.
```

---

## Security Model

```
AUTHENTICATED (can issue commands):
  Telegram      -- JB's personal bot token. Full command access.
  Claude Code   -- direct session. Full access.

INFORMATION LAYER ONLY (cannot issue commands):
  Gmail            -- read threads, surface intel, create task drafts
  Google Calendar  -- read events, trigger prep agents
  Monday.com       -- read SustainCFO tasks, mirror to Supabase
  Apollo.io        -- read prospect data
  Instapaper       -- read saved articles
  YouTube          -- read watch history / queued content
  Web content      -- research only
```

---

## Sub-Agent Directory

### Daily Briefing Agent
- **Trigger:** 5am cron
- **Reads:** Supabase P1 + This Week tasks, Obsidian Daily Note, Google Calendar
- **Outputs:** Telegram message with today's priorities, calendar, flagged items
- **Permission level:** Read-only (Phase 1)

### Task Agent
- **Trigger:** Telegram command or orchestrator signal
- **Reads:** Input context (Telegram message, email summary, etc.)
- **Outputs:** Categorized task proposal -> Telegram for JB approval -> write to Supabase
- **Permission level:** Write to Supabase after JB approval (Phase 1)

### Memory Agent
- **Trigger:** Nightly cron (11pm)
- **Reads:** Today's Telegram history, tasks completed, decisions made
- **Outputs:** Obsidian Daily Note update, tacit knowledge .md updates
- **Permission level:** Write to Obsidian (Phase 2)

### Consumption Agent
- **Trigger:** On-demand or daily
- **Reads:** Instapaper queue, YouTube history
- **Outputs:** Summaries + key takeaways -> Obsidian Daily Note or /Resources
- **Permission level:** Write to Obsidian (Phase 2)

### Research Agent
- **Trigger:** `!research [topic]` from Telegram
- **Reads:** Web, context files, Supabase contacts/projects
- **Outputs:** Structured research brief -> Telegram + Obsidian /Resources
- **Permission level:** Read web + write Obsidian (Phase 2)

### Meeting Prep Agent
- **Trigger:** Calendar event in 60 min
- **Reads:** Obsidian contact notes, recent Gmail threads, open tasks
- **Outputs:** Pre-brief -> Telegram
- **Permission level:** Read Gmail + Calendar (Phase 3)

### SustainCFO Agent
- **Trigger:** `!cfo [task]` or scheduled
- **Reads:** Monday.com client tasks, Gmail SustainCFO, Supabase contacts
- **Outputs:** Client brief, action items -> Telegram
- **Permission level:** Read Monday + Gmail SustainCFO (Phase 3)

### Reveal / Scope Agent
- **Trigger:** `!scope [company]` from Telegram or Claude Code
- **Reads:** Apollo prospect data, web research, Supabase contact history
- **Outputs:** 2-page Bellissimo Reveal report -> Telegram + Obsidian
- **Permission level:** Read Apollo + web (Phase 3)

---

## C-Suite Persona Directory

All personas have write access to Supabase (create/update tasks) and can message Telegram.
They propose before acting on anything external-facing.

| Persona | Domain | Scheduled | On-Demand | Primary Action |
|---|---|---|---|---|
| **CEO** | Enterprise strategy | Monthly | `/ceo` | Reprioritize threads, reallocate JB time |
| **COO** | Operations + bottlenecks | Weekly | `/coo` | Create tasks for constraints, flag stale |
| **CMO** | Demand + pipeline | Weekly | `/cmo` | Draft outreach, flag cold prospects |
| **CGO** | Revenue growth | Weekly | `/cgo` | Surface pipeline gaps, thread advancement |
| **Chief of Staff** | Routing + orchestration | Daily (pre-brief) | Always-on | Route -> dispatch -> close loop |

**Chief of Staff is the linchpin.**
You talk to CoS. CoS dispatches to the right persona. Persona acts. CoS closes the loop.
You get a report in Telegram.

---

## Memory Architecture (Three Layers)

```
Layer 1 -- PARA Life Directory (Obsidian /Projects, /Areas, /Resources, /Archive)
  Persistent knowledge: one .md per project, per person, per resource.
  Agents read and update these as context evolves.
  This is what you KNOW -- not what happened today.

Layer 2 -- Daily Notes (Obsidian /Daily Notes/YYYY-MM-DD.md)
  What happened today. Open loops. Completed tasks. Decisions made.
  Memory Agent writes here nightly.
  Daily Briefing Agent reads this every morning.
  This is the heartbeat.

Layer 3 -- Tacit Knowledge (Obsidian /Tacit/ + CLAUDE.md files)
  Preferences, security rules, trusted channels, patterns, lessons learned.
  Agents reference this before acting to avoid known failure modes.
  Example: "Never commit .env files." "JB prefers direct communication."
  This is what you've LEARNED.
```

---

## Data Model (Supabase)

### tasks
The core unit. Everything actionable lives here. Designed for hundreds of tasks.

| Field       | Type      | Notes                                               |
|-------------|-----------|-----------------------------------------------------|
| id          | uuid      | Primary key                                         |
| title       | text      | The task                                            |
| status      | enum      | backlog / this_week / in_progress / waiting / done  |
| area        | enum      | bellissimo_labs / sustaincfo / health / personal_finance / family / personal_growth |
| priority    | enum      | p1 / p2 / p3                                        |
| due_date    | date      | Optional                                            |
| next_action | text      | Specific next physical action                       |
| notes       | text      | Context, links, Gmail thread IDs                    |
| source      | text      | manual / telegram / agent / gmail / monday          |
| project_id  | uuid      | FK to projects (optional)                           |
| created_at  | timestamp |                                                     |
| updated_at  | timestamp |                                                     |

### projects
Workstreams. Designed for dozens of projects.

| Field       | Type      | Notes                              |
|-------------|-----------|-------------------------------------|
| id          | uuid      |                                     |
| name        | text      |                                     |
| area        | enum      |                                     |
| status      | enum      | active / waiting / done / parked    |
| description | text      |                                     |
| north_star  | text      | What does done look like?           |
| priority    | enum      | p1 / p2 / p3                        |
| created_at  | timestamp |                                     |
| updated_at  | timestamp |                                     |

### contacts

| Field        | Type    | Notes                                  |
|--------------|---------|----------------------------------------|
| id           | uuid    |                                        |
| name         | text    |                                        |
| email        | text    |                                        |
| company      | text    |                                        |
| relationship | enum    | client / prospect / partner / personal |
| area         | enum    | sustaincfo / bellissimo / personal     |
| last_contact | date    |                                        |
| notes        | text    |                                        |

### sessions
Log of every significant Claude Code or agent session.

| Field      | Type      | Notes           |
|------------|-----------|-----------------|
| id         | uuid      |                 |
| date       | date      |                 |
| summary    | text      |                 |
| decisions  | text[]    |                 |
| actions    | text[]    |                 |
| files      | text[]    |                 |

---

## Telegram Command Reference

```
TASK MANAGEMENT
!tasks [area]        -- show tasks, optionally filter by area
!add [task]          -- capture new task (Task Agent categorizes + queues)
!done [task]         -- mark complete
!brief               -- on-demand priority summary

AGENT RUNS
!scope [company]     -- run Bellissimo Reveal
!xray [company]      -- run SustainCFO X-Ray
!prep [name]         -- meeting prep for person
!research [topic]    -- deep research brief
!prospect [ICP]      -- Apollo search for prospect targeting

C-SUITE
/ceo                 -- CEO strategic review
/coo                 -- COO operations + bottleneck scan
/cmo                 -- CMO pipeline + outreach review
/cgo                 -- CGO growth audit

SYSTEM
!status              -- orchestrator + agent health
!threads             -- PROJECT_THREADS.md summary
!memory              -- today's Obsidian Daily Note summary
```

---

## Obsidian Vault Integration

```
Sync architecture:
  Device sync:  Obsidian Sync ($5/mo) -- iPhone + iPad + Windows + 2nd computer
  VPS writes:   Obsidian Git (free plugin) -- vault as private GitHub repo
                VPS agents git commit + push -> Obsidian pulls on devices

Vault path (local Windows): C:\Users\Admin\Documents\Obsidian Vault

Vault path (Windows): C:\Users\Admin\Documents\Obsidian Vault

Actual vault structure (map to this -- do NOT impose PARA on top):
  00_Inbox/       -- capture notes, quick captures
  01_Daily/       -- YYYY-MM-DD.md daily notes (HEARTBEAT -- agents read/write here)
  02_Evergreen/   -- permanent atomic notes
  03_Topics/      -- topic-based notes (companies, concepts, areas)
  04_Decisions/   -- decision logs
  05_Prompt Library/ -- prompts and templates
  08_Journal/     -- journal entries
  10_Library/     -- books, references, saved content
  97_Attachments/ -- files
  98_Archive/     -- archived content
  99_System/      -- system config, agent rules
  [root level]    -- project files (e.g. Bellissimo Enterprises.md, contact MDs)

Agent write paths (mapped to actual vault):
  Memory Agent      -> 01_Daily/YYYY-MM-DD.md  (append to today's note)
  Research Agent    -> 10_Library/[topic].md   (new file per research run)
  Consumption Agent -> 01_Daily/ (append) OR 10_Library/ (permanent reference)
  Meeting Prep      -> 03_Topics/[company-or-person].md
  Decisions         -> 04_Decisions/YYYY-MM-DD-[topic].md
  Agent rules/tacit -> 99_System/[file].md
```

---

## Progressive Permission Model

JB gives green light at each phase. Agents earn autonomy incrementally.

```
PHASE 0 -- Foundation (build now, this session)
Permissions: Read local files, write MASTER_TASKS.md, message Telegram
  - MASTER_TASKS.md created (flat markdown, all tasks, all areas)
  - Obsidian Git plugin installed + vault connected to GitHub
  - Telegram bot created (BotFather)
  - orchestrator.py skeleton -- Telegram connection only
  - Prove the loop: message Telegram -> orchestrator logs it

PHASE 1 -- Command Response (build next)
Permissions: Supabase read/write, Telegram send
  - Supabase tables created (tasks, projects, contacts, sessions)
  - Migrate MASTER_TASKS.md -> Supabase
  - 5am Daily Briefing Agent (cron -> Telegram)
  - Telegram commands: !tasks, !add, !done, !brief, !status
  - Port discord_bot.py -> telegram_bot.py (Discord DEPRECATED)

PHASE 2 -- Memory + Scheduled Agents
Permissions: Obsidian write (via Git), scheduled cron
  - Memory Agent -- nightly Obsidian Daily Note update
  - Consumption Agent -- Instapaper/YouTube -> Obsidian
  - Stale task scan (daily) -> Telegram ping
  - Pipeline nudge (weekly) -> Telegram
  - C-suite personas as Telegram commands (read + propose)

PHASE 3 -- Read Integrations
Permissions: Gmail read, Google Calendar read, Monday.com read
  - Gmail integration (personal + SustainCFO) -- surface action items
  - Meeting Prep Agent (60 min before calendar event)
  - SustainCFO Agent (Monday.com sync)
  - Reveal Agent (Apollo + web research)

PHASE 4 -- Propose + Approve
Permissions: Draft external actions, Telegram inline keyboard approvals
  - Agents draft emails -> JB approves in Telegram -> sends
  - Task auto-creation from email/calendar
  - C-suite personas create Supabase tasks autonomously

PHASE 5 -- Ambient (earned autonomy)
Permissions: Act on approved action types without per-action confirmation
  - Event-driven triggers (email arrives -> task created)
  - Full proactive loop -- agents push without being asked
  - JB sets policy, agents execute within policy
```

---

## What You Can Do -- End State

When all phases are built:

- **5am Telegram message arrives** -- priorities, calendar, flagged emails. You didn't ask.
- **Task capture:** "!add call Marcus about referral program" -> categorized, prioritized, in Supabase
- **Morning question:** "!tasks sustaincfo" -> your SustainCFO tasks, filtered
- **Meeting in 60 min:** Pre-brief appears in Telegram automatically
- **Email from known contact arrives:** Task created, Telegram notification
- **Weekly:** COO surfaces your constraint. CMO flags cold pipeline. No dashboards to check.
- **Nightly:** Memory Agent consolidates the day. Obsidian stays current.

Agents running:
- 1 always-on orchestrator (VPS)
- 6+ scheduled cron agents (brief, memory, stale scan, nudge, weekly review, c-suite checks)
- N on-demand agents (scope, research, prep -- spawn and terminate per request)

JB's job: Strategy, relationships, final decisions on anything consequential.
Agents' job: Everything else.

---

## What to Build This Session (Phase 0)

```
Step 1: MASTER_TASKS.md        -- flat task list, all areas, captures everything now
Step 2: Obsidian Git setup     -- install plugin, create private GitHub repo, connect
Step 3: Telegram bot creation  -- BotFather -> get token -> test connection
Step 4: orchestrator.py        -- connects to Telegram, receives messages, logs them
Step 5: Prove the loop         -- send message from iPhone -> see it logged on VPS
```

---

## What We Are NOT Building Yet

- Supabase (Phase 1 -- after Telegram loop is proven)
- Gmail integration (Phase 3)
- C-suite autonomous actions (Phase 4+)
- Any agent that takes external action without JB approval
- Custom web dashboard (Telegram is the dashboard)
- New Notion structure (deprecated -- Obsidian replaces for personal knowledge)
- Monday.com changes (SustainCFO team tool stays as-is)

---

## Open Decisions

- [x] Primary command interface: Telegram
- [x] Obsidian sync for VPS: Obsidian Git (+ keep Obsidian Sync for devices)
- [x] Discord: Deprecated -- port to Telegram (Phase 1)
- [x] Notion: Deprecated for personal use -- Obsidian replaces
- [x] Task visibility (interim): MASTER_TASKS.md flat file until Supabase live
- [ ] Supabase: free tier sufficient for hundreds of tasks -- confirm at Phase 1
- [x] Telegram bot name: @BellissimoLabs_bot
- [x] Private GitHub repo for Obsidian vault: bellissimo-obsidian-vault

---

*This document is the architecture contract. Version 2.0 supersedes Version 1.0.*
*Update version number when architecture decisions change.*
*Build nothing outside this architecture.*
