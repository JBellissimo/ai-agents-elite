# Bellissimo AI Labs — Project State Export
**Generated:** 2026-03-01
**Purpose:** Advisor review — evaluate what's valuable, what's a distraction, what should be prioritized next.
**Prepared by:** Claude Code (Anthropic) working with JB (founder)

---

## 1. WHO IS BUILDING THIS

**JB (Jess Bellissimo)** — solo operator, building in parallel:
- **SustainCFO** — fractional CFO/COO practice. ~$1M ARR, 12–15 clients, co-run with a partner (Josh). JB functions as the business development and operational partner.
- **Bellissimo AI Labs** — AI consulting firm being built from scratch. $0 ARR today. Goal: $20M ARR as a solo operator + agents. Target 2026: $250K.

**North star metric:** Revenue per hour of JB's time.

**The thesis:** AI agents do the delivery work. JB does relationships, sales, and strategy. Every tool built here is designed to multiply JB-hours, not add to his to-do list.

---

## 2. DIRECTORY TREE

```
ai-agents-elite/                          ← GitHub repo, primary working directory
│
├── CORE AGENTS
│   ├── orchestrator.py                   ← Main process. Always-on on VPS. Telegram bot.
│   ├── brief_agent.py                    ← Daily brief generator. Claude API.
│   ├── meeting_prep_agent.py             ← Meeting research + brief. Claude API. (NEW - 3/1)
│   ├── agent.py                          ← Business X-Ray / Reveal agent. Claude API.
│   └── agent_server.py                   ← FastAPI server. Async job queue. Not actively used.
│
├── DATA LAYER
│   ├── db.py                             ← Supabase wrapper. Tasks CRUD.
│   ├── tools.py                          ← 5 simulated financial tools for agent.py
│   └── import_tasks.py                   ← One-time script. Imported MASTER_TASKS.md → Supabase.
│
├── OTHER AGENTS/SCRIPTS
│   ├── discord_bot.py                    ← Discord bot. DEPRECATED. Replaced by Telegram.
│   ├── apollo_tools.py                   ← Apollo.io API wrapper. BLOCKED (Cloudflare 403 on VPS).
│   ├── conversation_extractor.py         ← Reads local Claude JSONL transcripts → extracts actions.
│   └── map_generator.py                  ← Generates city maps from OpenStreetMap. Concept only.
│
├── STRATEGY / CONTEXT DOCS
│   ├── STRATEGIC_NORTH_STAR.md           ← The mandate. $20M vision, pipeline math, phase strategy.
│   ├── PROJECT_THREADS.md                ← 9 active workstreams with status + next actions.
│   ├── BELLISSIMO_ROADMAP.md             ← 6-phase product roadmap (Phase 1–6).
│   ├── SALES_PACKAGE.md                  ← ICP, routing questions, pricing, talking points.
│   ├── BRAND_STYLE_GUIDE.md              ← Colors, fonts, voice, logo direction.
│   └── MASTER_TASKS.md                   ← 138 tasks. DEPRECATED. Moving to Todoist.
│
├── REFERENCE DOCS
│   ├── ARCHITECTURE.md                   ← Full technical architecture (v2.0).
│   ├── VISUAL_ARCHITECTURE.md            ← Mermaid diagram of system.
│   ├── HOW_I_LEARN.md                    ← JB's learning style profile for agent context.
│   ├── COMMANDS.md                       ← Command reference card.
│   ├── USER_GUIDE.md                     ← Daily cadence, keyboard shortcuts, VPS reference.
│   ├── BUSINESS_SETUP.md                 ← Legal formation checklist. Not started.
│   ├── LEARNING_PATH.md                  ← 5-phase agent learning curriculum.
│   ├── LEARNING_GUIDE.md                 ← Maps code → interview knowledge.
│   └── SESSION_LOG.md                    ← Append-only session summaries.
│
├── OUTPUT DIRECTORIES
│   └── meeting_briefs/                   ← Saved meeting prep briefs (NEW - 3/1).
│
├── CLAUDE SKILLS (.claude/skills/)
│   ├── ceo.md                            ← CEO persona. Reads North Star. Capital allocation.
│   ├── cmo.md                            ← CMO persona. Demand gen, positioning, copy.
│   ├── cgo.md                            ← CGO persona. Growth momentum, thread priority.
│   ├── coo.md                            ← COO persona. Limiting factor, EOS/Traction.
│   ├── deep-research.md                  ← Market intelligence brief generator.
│   ├── seek-counsel.md                   ← Multi-model council (Deploy + Synthesize modes).
│   └── session-summary.md                ← Session summary template.
│
├── DEPLOY
│   ├── deploy.ps1                        ← One-command deploy: git push + VPS pull + restart.
│   ├── requirements.txt                  ← Python deps. Installed on VPS via deploy.ps1.
│   ├── .env.example                      ← Template. Real .env never committed.
│   └── channel_config.json               ← Discord channel config. DEPRECATED.
│
└── CONVERSATION_INTEL.md                 ← Auto-generated action item extract from past sessions.
```

---

## 3. ACTIVE AGENTS & SKILLS

### 3A. orchestrator.py — The Always-On Agent OS
**Status:** LIVE on VPS. Working.
**Trigger:** Telegram messages from JB's iPhone. Authorized by TELEGRAM_USER_ID.
**What it does:**

| Command | What it does | Status |
|---|---|---|
| `/start` | Confirms VPS is alive | Working |
| `/status` | System health check | Working |
| `/help` | Lists all commands | Working |
| `/brief` | Calls Claude → AI daily brief | Working |
| `!tasks [area]` | Lists Supabase tasks (no area = summary counts) | Working |
| `!add [!!] [[Area]] title` | Inserts task to Supabase | Working |
| `!done [partial title]` | Marks task done by fuzzy match | Working |
| `!brief` | Same as /brief | Working |
| `!meetingprep [name]` | Prompts for context, runs research + brief | Working (NEW, untested in prod) |

**Scheduled job:** 5am EST daily brief via JobQueue.

**Mental models infrastructure:** Code to load Theory of Constraints → First Principles → Invert Everything → Systems Thinking from Obsidian vault is built into orchestrator.py. **However, the Obsidian vault files don't exist on VPS.** The loader handles this gracefully (returns placeholder text), but the feature is non-functional until vault is set up on VPS.

---

### 3B. brief_agent.py — Daily Briefing Agent
**Status:** LIVE. Working.
**Trigger:** `/brief`, `!brief`, or 5am EST scheduled job.
**What it does:** Reads all active tasks from Supabase + reads STRATEGIC_NORTH_STAR.md + reads PROJECT_THREADS.md → calls Claude (sonnet-4-6) → returns:
- TOP 3 TODAY (with reasoning)
- TIME-SENSITIVE items
- DEFER recommendation
- CONSTRAINT (bottleneck sentence)

**Reasoning framework:** Theory of Constraints → Revenue filter → Inversion.

**Known issue:** Task data quality. When 138 tasks were imported from MASTER_TASKS.md, "waiting" and "blocked" statuses were all mapped to "active." The brief therefore surfaces tasks like "Waiting on Josh" as top priorities. JB has decided to pivot task management to Todoist (Supabase task system will be deprecated or rebuilt with proper status types).

---

### 3C. meeting_prep_agent.py — Meeting Research Agent
**Status:** LIVE on VPS as of 3/1. Untested in production.
**Trigger:** `!meetingprep [name]` in Telegram, followed by pasted email/LinkedIn context (or "skip").
**What it does:**
1. Runs 3 DuckDuckGo web searches on the person (identity, professional background, recent news)
2. Combines with user-provided context (email thread, LinkedIn messages — highest priority signal)
3. Reads STRATEGIC_NORTH_STAR.md for ICP/service context
4. Calls Claude (sonnet-4-6) → generates: Background + Opportunity + Conversation Script
5. Saves to `meeting_briefs/YYYY-MM-DD_name.md`
6. Sends to Telegram (chunked for 4096-char limit)

**Template output:**
```
# Meeting Prep: [Name]
Date: [today]
## BACKGROUND / ## OPPORTUNITY / ## CONVERSATION SCRIPT
(Opener → Discovery → Pivot → Close)
```

**Why built:** JB has 2 meetings this week where he needs research + talking points fast:
- Sammy Popat (UMD ecosystem catalyst, SustainCFO referral angle) — 3/2 @ 3:30pm
- Bryan Gelnett (former ServiceMaster CEO, now PE investment firm + first platform acquisition) — this week

---

### 3D. agent.py — Business X-Ray / Reveal Agent
**Status:** FUNCTIONAL locally. Not actively used in production.
**Trigger:** Slack/Discord `!scope` or `!xray` commands (Discord bot deprecated), or FastAPI POST /scope or /xray.
**What it does:** Runs a multi-tool diagnostic on a company. Two modes:
- `reveal`: Bellissimo scope (AI readiness, bottlenecks, opportunity map)
- `xray`: SustainCFO scope (financial health, cash, margins)

Uses 5 simulated financial tools in tools.py. Real tool integrations not built yet.

**Blocker:** Tools are simulated data. No real intake form. No web form connected. Not client-ready.

---

### 3E. agent_server.py — FastAPI Job Server
**Status:** Built. Not running. Not needed until Reveal intake form is built.
**What it does:** Async job queue for agent.py runs. POST /scope → job_id → GET /jobs/{id} to poll result. Originally built for web form integration.

---

### 3F. apollo_tools.py — Apollo.io Prospecting
**Status:** BLOCKED. Built but non-functional on VPS.
**Issue:** Cloudflare 403 errors on Apollo.io API calls from VPS IP addresses. VPS IPs are flagged.
**Workaround options not yet explored:** Proxy, Bright Data residential proxy, or local-only use.

---

### 3G. conversation_extractor.py — Session Intelligence
**Status:** Built locally. Not deployed.
**What it does:** Reads Claude Code JSONL transcript files → extracts open action items, decisions made → can post to Discord or PROJECT_THREADS.md.
**Current use:** CONVERSATION_INTEL.md was auto-generated by this tool (contains action items from sessions 1-4).

---

### 3H. discord_bot.py — Discord Bot
**Status:** DEPRECATED. Code still present. VPS runs orchestrator.py now.
**What it did:** !scope, !xray, !prep, !eval, !prospect, !threads, !status. Per-channel agent routing via channel_config.json.
**Replaced by:** orchestrator.py (Telegram).

---

### 3I. Claude Skills (.claude/skills/)

All skills are used within Claude Code sessions (VS Code) — not deployed as agents. They provide persistent role-based personas.

| Skill | What it does | Status |
|---|---|---|
| `/ceo` | CEO review: limiting factor, attention allocation, stop-doing list | Working in Claude Code |
| `/cmo` | CMO: positioning, copy, demand gen, LinkedIn strategy | Working in Claude Code |
| `/cgo` | CGO: growth momentum, thread priority, revenue velocity | Working in Claude Code |
| `/coo` | COO: ops efficiency, limiting factor (Goldratt), EOS/Traction | Working in Claude Code |
| `/deep-research` | Market intel brief: ICP, pricing, players, market size | Working in Claude Code |
| `/seek-counsel` | Multi-model council: generates prompts for o1 + Gemini, then synthesizes | Working (manual process) |

**Not yet connected to Telegram.** All Claude Code skills are desktop-only for now.

---

## 4. INFRASTRUCTURE

### VPS — Hetzner CX11
- **IP:** 5.161.215.26
- **Spec:** 2 vCPU, 2GB RAM, 40GB SSD, Ubuntu 24.04
- **Cost:** ~€4.51/month
- **Running:** `orchestrator.py` in a `screen` session named "bellissimo"
- **Python env:** `/opt/venv/` (venv with all pip packages)
- **Code:** `/opt/bellissimo/` (cloned from GitHub)
- **Config:** `.env` file on VPS with all real keys (never in git)

**Reliability issue:** No systemd service. If VPS reboots, screen session dies and orchestrator doesn't auto-restart. Requires manual SSH to restart. Not yet converted to a proper system service.

### Deploy Workflow
`deploy.ps1` (Windows PowerShell):
1. `git push` to GitHub
2. SSH to VPS
3. `git pull`
4. `pip install -r requirements.txt -q`
5. Kill existing orchestrator + screen sessions
6. Start new screen session with orchestrator.py

**One command from VS Code terminal.** Works reliably.

### Supabase — PostgreSQL Database
- **Project:** xwdlowbuyhpoynaatout
- **Table:** `tasks` (id, created_at, title, area, status, priority, notes, next_action)
- **Current data:** 138 tasks imported from MASTER_TASKS.md (data quality issues — see above)
- **Usage:** Read by brief_agent.py, written by !add/!done commands
- **Status:** Connected and working. Data quality is the problem, not the infrastructure.

### GitHub
- **Repo:** `JBellissimo/ai-agents-elite` (public)
- **Purpose:** Source of truth for VPS deploy. All code lives here.

---

## 5. EXTERNAL INTEGRATIONS

| Integration | Status | What it's for |
|---|---|---|
| Anthropic API | Connected, funded | Powers all Claude agents (orchestrator, brief, meeting prep, reveal) |
| Telegram Bot API | Connected (@BellissimoLabs_bot) | JB's command channel from iPhone |
| Supabase | Connected | Task database |
| DuckDuckGo Search | Installed (duckduckgo-search lib) | Meeting prep web research. No API key needed. |
| Apollo.io | Built, BLOCKED | Prospecting / company search. Cloudflare 403 on VPS. |
| Discord | DEPRECATED | Old command channel, replaced by Telegram |
| Obsidian Vault | Partially wired | Mental models loaded in orchestrator.py, but vault not on VPS yet |
| Gmail | NOT CONNECTED | Target integration for meeting prep context automation |
| Google Calendar | NOT CONNECTED | Target integration for auto-triggering meeting prep |
| GHL (Go High Level) | NOT CONNECTED | SustainCFO outreach CRM. 107 marketing contacts, 37 affiliates live. |
| Todoist | NOT CONNECTED | JB pivoting from Supabase tasks to Todoist |

---

## 6. WHAT'S WORKING vs. WHAT'S NOT

### Working
- ✅ Telegram bot live on VPS, responds to commands from JB's iPhone
- ✅ 5am daily brief: Claude reads tasks + strategy docs + generates brief
- ✅ `!tasks`, `!add`, `!done` commands (with data quality caveat)
- ✅ `!meetingprep` command (deployed today, untested in production)
- ✅ deploy.ps1: one-command deploy from VS Code
- ✅ C-suite skill suite (CEO, CMO, CGO, COO, /seek-counsel, /deep-research) usable in VS Code
- ✅ agent.py runs end-to-end with simulated data

### Not Working / Blocked
- ❌ **Task data quality** — 138 tasks imported, ~30–40% are stale/waiting/not-JB's. Brief surfaces them anyway.
- ❌ **Apollo.io on VPS** — Cloudflare 403. Prospecting tool blocked.
- ❌ **Mental models** — Code infrastructure exists, vault files not on VPS. Feature non-functional.
- ❌ **Obsidian Git** — Not set up on VPS. Vault read/write to VPS planned but not built.
- ❌ **VPS auto-restart** — No systemd service. Manual restart required after reboots.
- ❌ **Reveal/Scope for real clients** — Tools are simulated. No real intake form. Not client-ready.
- ❌ **Gmail / Calendar integration** — Not started.
- ❌ **Todoist integration** — Not started. Pivoting away from Supabase tasks.

### Intentionally Deprioritized
- ⏸ **Website** (Phase 3 in roadmap) — Not started by design. Revenue first.
- ⏸ **LLC formation** (Thread 1) — Intentionally deferred until first paying Bellissimo client.
- ⏸ **Discord bot** — Deprecated. All future work on Telegram.
- ⏸ **agent_server.py** — Parked. Not needed until web intake form exists.
- ⏸ **MASTER_TASKS.md** — Deprecated. Moving to Todoist.

---

## 7. REVENUE STATUS

### SustainCFO
- **ARR:** ~$1M (existing, running)
- **Clients:** 12–15 active retainers
- **2026 target:** $1.5M (+$500K)
- **Hot opportunities:** Ali Laith dental rollup ($90K, last contact 7+ days ago), Commercial Filter, Rentwell
- **Blocker:** Outreach not live. Josh hasn't approved Financial Clarity Assessment form yet. 107-contact GHL campaign not launched.

### Bellissimo AI Labs
- **ARR:** $0
- **2026 target:** $250K
- **Reveals run:** 0
- **Clients:** 0
- **Entry point:** Bellissimo Reveal/Scope ($500 diagnostic → retainer) — product designed but not delivered to any client

---

## 8. TIME INVESTED (ROUGH ESTIMATES)

| Component | Sessions | Est. Hours | Revenue-Connected? |
|---|---|---|---|
| agent.py (Business X-Ray/Reveal) | Sessions 1-2 | ~6 hrs | Yes — core product |
| tools.py (5 simulated tools) | Session 1 | ~2 hrs | Yes — supports Reveal |
| discord_bot.py | Session 2 | ~4 hrs | Indirect — now deprecated |
| agent_server.py (FastAPI) | Session 2 | ~3 hrs | Indirect — parked |
| VPS setup + deploy.ps1 | Session 2 | ~3 hrs | Yes — enables always-on |
| C-suite skill suite (6 files) | Session 3 | ~3 hrs | Yes — strategy execution |
| STRATEGIC_NORTH_STAR.md | Session 3 | ~2 hrs | Yes — drives all decisions |
| orchestrator.py (Phase 0) | Session 4 | ~4 hrs | Yes — command interface |
| Telegram + VPS Phase 0 deploy | Session 4 | ~3 hrs | Yes — mobile ops |
| db.py + Supabase setup | Session 5 | ~3 hrs | Indirect — task data |
| import_tasks.py + data import | Session 5 | ~2 hrs | Low — task data quality issues |
| brief_agent.py | Session 5 | ~2 hrs | Yes — daily prioritization |
| meeting_prep_agent.py | Session 6 (today) | ~2 hrs | Yes — sales conversations |
| Strategy/planning docs | All sessions | ~4 hrs | Yes — context for agents |
| **TOTAL** | | **~43 hrs** | |

---

## 9. INTENDED PURPOSE — HOW EACH COMPONENT CONNECTS TO REVENUE

### High-Leverage (direct path to revenue)
| Component | Revenue connection |
|---|---|
| agent.py | Runs the Bellissimo Reveal — the $500 entry point that converts to $10K+ engagements |
| meeting_prep_agent.py | Enables better sales conversations. Every meeting with a warm prospect is a potential $60–90K/yr retainer. |
| brief_agent.py | Keeps JB focused on revenue actions vs. getting lost in infrastructure. 5am brief = highest-value 5 minutes of the day. |
| SALES_PACKAGE.md | ICP, routing logic, talking points — foundation of every sales conversation |
| C-suite skill suite | Strategic clarity. /CEO and /CGO prevent productive-feeling work that doesn't move revenue. |

### Infrastructure (enables revenue, not directly revenue)
| Component | Purpose |
|---|---|
| orchestrator.py | Command interface from JB's iPhone. Mobile ops. Required for any automation to matter. |
| db.py + Supabase | Data layer for tasks/projects. Currently underutilized due to data quality issues. |
| deploy.ps1 | Removes friction from shipping. Every 10-minute deploy saved is JB-hours recaptured. |
| VPS (Hetzner) | Always-on compute for $4.51/mo. The infrastructure cost is negligible. |

### Low-Leverage / Distraction Risks
| Component | Honest assessment |
|---|---|
| MASTER_TASKS.md (138 tasks) | Built and immediately deprecated. The act of importing and managing 138 tasks in a custom system was a multi-hour investment with no revenue payoff. JB should use Todoist + Telegram for task capture, not a custom Supabase system. |
| discord_bot.py | ~7 hours of build replaced by Telegram in 2 sessions. The Discord infrastructure was right for the learning phase but premature for a business tool. |
| agent_server.py | FastAPI job queue built for a use case (web intake form) that doesn't exist yet. Speculative infrastructure. |
| map_generator.py | Guerrilla marketing concept. Zero progress. Probably never gets built — direct outreach has higher ROI. |
| apollo_tools.py | Built but blocked. Investing more time here has diminishing returns without a reliable proxy. |

---

## 10. THE CURRENT BOTTLENECK

This is the honest assessment from `STRATEGIC_NORTH_STAR.md` (written 2/26, still accurate):

> **The bottleneck is not technology. It is not strategy. It is sales pipeline.**
> - No Bellissimo clients yet
> - SustainCFO outreach not live (Josh hasn't approved Financial Clarity Assessment form)
> - Ali Laith ($90K) going cold
> - 37 affiliates not activated

Every infrastructure build since Session 1 has been done while the sales engine sat idle. The agent infrastructure is genuinely impressive for 6 weeks of work — but it is building leverage on top of zero revenue. The agents have nothing to amplify yet.

**The two actions that move the needle this week:**
1. Josh conversation → Financial Clarity Assessment approved → GHL outreach live (SustainCFO)
2. Sammy Popat meeting (tomorrow, 3/2) → position for UMD referral pipeline (Bellissimo)

---

## 11. WHAT'S NEXT (PLANNED, NOT COMMITTED)

In priority order based on revenue filter:

1. **Run meeting_prep_agent on Sammy Popat + Bryan Gelnett** — Telegram test in production (today/tomorrow)
2. **Fix Supabase task data** or deprecate entirely in favor of Todoist integration
3. **Wire Gmail into meeting_prep_agent** — pull email threads automatically (OAuth setup needed)
4. **Add 4 Reveal tools to tools.py** — make agent.py client-ready (get_digital_presence_audit, get_operations_bottleneck_survey, get_ai_readiness_score, get_revenue_model_map)
5. **Build Reveal intake form** — web form → feeds agent → delivers report (Phase 2 in roadmap)
6. **GHL outreach automation** — connect Go High Level API → automate 107-contact campaign
7. **Todoist API integration** — replace Supabase tasks with real task manager
8. **Systemd service for VPS** — auto-restart orchestrator on reboot
9. **C-suite skills → Telegram** — `/ceo`, `/coo`, `/cmo` as Telegram commands (not just VS Code)

---

## 12. TECH STACK SUMMARY

| Layer | Technology | Why |
|---|---|---|
| LLM | Anthropic Claude (sonnet-4-6) | Raw API — no LangChain/CrewAI by design. Deep understanding, interview readiness. |
| Bot/Interface | python-telegram-bot v20 (async) | Mobile command channel from iPhone. Always-on via screen on VPS. |
| Database | Supabase (PostgreSQL) | Free tier. Simple. supabase-py client. |
| Web search | duckduckgo-search (Python lib) | Free, no API key, works for meeting research. |
| Web framework | FastAPI + uvicorn | Parked. For Reveal intake form when built. |
| Deploy | PowerShell (deploy.ps1) + GitHub + Hetzner VPS | One-command from VS Code. €4.51/mo compute. |
| Skills/Personas | Claude Code .claude/skills/ markdown files | Custom persona system. Desktop VS Code only. |
| Scheduling | python-telegram-bot JobQueue (APScheduler) | 5am daily brief. No separate cron daemon needed. |
| Environment | python-dotenv, .env (never committed) | Standard secret management. |

---

*This document reflects the state as of 2026-03-01. For live status, check PROJECT_THREADS.md.*
