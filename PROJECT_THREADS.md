# Project Threads — Active Work Tracker
# READ THIS FIRST at the start of every session.
# It tells you where things stand across every parallel workstream.
# Update it at the end of each session.

---

## How to Use This File
1. Open this at the start of every Claude Code session
2. Say: "Read PROJECT_THREADS.md and tell me where we left off"
3. Pick one thread to work on — don't try to advance all of them at once
4. Update the STATUS and NEXT ACTION fields before ending the session

---

## THREAD 1 — Legal & Business Formation
**Status:** NOT STARTED
**Priority:** LOW — deprioritized until revenue is flowing
**Key File:** [BUSINESS_SETUP.md](BUSINESS_SETUP.md)

**What's done:**
- Full agent-runnable checklist created (12 tasks, 5 tracks)

**Next action:**
- [ ] File a simple LLC (state TBD — Wyoming not required)
- [ ] Get EIN from IRS
- [ ] Open Mercury Bank account
- [ ] Secure domain (bellissimo.ai or bellissimoailabs.com)

**Blocker:** Not urgent. Start after first paying client or when legal protection becomes necessary.

---

## THREAD 2 — Bellissimo AI Labs Brand & Website
**Status:** BRAND IN PROGRESS / WEBSITE NOT STARTED
**Priority:** HIGH — needed before any outreach
**Key Files:** [BRAND_STYLE_GUIDE.md](BRAND_STYLE_GUIDE.md), [BELLISSIMO_ROADMAP.md](BELLISSIMO_ROADMAP.md)

**What's done:**
- Brand style guide created (colors, fonts, voice, logo direction)
- Roadmap created with Phase 3 (Website) defined

**Next action:**
- [ ] Review brand style guide and confirm direction
- [ ] Choose website stack: Webflow (fastest) or Next.js (most control)
- [ ] Wireframe homepage: hero + Reveal CTA + products
- [ ] Build "Request Your Reveal" intake form

**Blocker:** Need brand approval before website design begins.

---

## THREAD 3 — The Bellissimo Reveal (Core Product)
**Status:** AGENT RUNNING / DISCORD BOT ON VPS (ALWAYS-ON)
**Priority:** HIGH — this is the revenue starter
**Key Files:** [agent.py](agent.py), [tools.py](tools.py), [discord_bot.py](discord_bot.py), [agent_server.py](agent_server.py)

**What's done:**
- agent.py updated to run in "reveal" mode (Bellissimo) or "xray" mode (SustainCFO)
- REVEAL_SYSTEM_PROMPT defined with 6-section framework
- 5 financial tools in tools.py (simulated data)
- agent_server.py built — FastAPI server with async job queue (POST /scope, POST /xray, GET /jobs/{id})
- discord_bot.py built — !scope, !xray, !help, !status, !threads commands
- Agent ran end-to-end successfully (Acme Manufacturing Co. demo via Discord !scope)
- Anthropic API funded + confirmed working

**Next action:**
- [ ] Add 4 new tools to tools.py for Reveal mode:
    - get_digital_presence_audit
    - get_operations_bottleneck_survey
    - get_ai_readiness_score
    - get_revenue_model_map
- [ ] Run the agent against a real prospect (not demo data)
- [ ] Build async CEO interview intake (web form or voice)
- [ ] Design the 2-page Reveal output template
- [x] Deploy discord_bot.py to Hetzner VPS for always-on operation
- [x] !prep command with Obsidian vault + inline context (| syntax)
- [x] !eval command — deal scoring + verdict
- [ ] Enhance daily nudge to read PROJECT_THREADS.md and surface specific per-thread asks
- [ ] Add 4 new tools to tools.py for Reveal mode
- [ ] Build Reveal intake form (web form → feeds agent)
- [ ] Gmail integration for !prep (pulls recent email threads with contact)

**Blocker:** New tools needed before running a real Reveal.

---

## THREAD 4 — Sales Package & Go-to-Market
**Status:** SUSTAINCFO SALES SYSTEM IN PROGRESS
**Priority:** HIGH — direct path to revenue
**Key Files:** [SALES_PACKAGE.md](SALES_PACKAGE.md), Google Form (Financial Clarity Assessment)

**What's done:**
- SustainCFO ICP defined ($3-20M revenue, no FT CFO, service businesses + venture-backed)
- 10-question Financial Clarity Assessment built in Google Form (sent to Josh for review)
- Full sales process map defined (7 stages: Identify → Outreach → Diagnostic → Deliver → Discovery → Propose → Close)
- Pricing tiers confirmed: $2,500/mo (productized) / $5,000/mo (growth) / $7,500+/mo (scale)
- Proposal reviewed — feedback given on personalization + differentiation gaps
- "SustainCFO for a Week" identified as $10K value entry tactic → converts to retainer
- 3 GHL pipelines reviewed: 107 marketing / 37 affiliate / 11 active sales
- Active sales pipeline prioritized: Ali Laith (dental, HOT), Commercial Filter, Rentwell
- ICP + diagnostic document drafted and sent to Josh for feedback
- Product renamed: "Scope" (not Reveal) for SustainCFO product

**Next action (pending Josh conversation tonight):**
- [ ] Josh feedback on Google Form questions
- [ ] Confirm "CFO for a Week" pricing/positioning ($10K value, free entry offer)
- [ ] Decide GHL outreach strategy for 107-contact marketing list
- [ ] Get Josh's discovery call questions (may update diagnostic)
- [ ] Confirm commission structure for JB on direct closes
- [ ] Draft direct prospect email + affiliate activation email
- [ ] Follow up on Ali Laith scope review call (7 days stale, $90K opportunity)
- [ ] Re-engage or archive cold pipeline (US Boston 150 days, Etchison 205, Wastebox 251, OKSA 323)

---

## THREAD 5 — Guerrilla Marketing
**Status:** CONCEPT DEFINED / EXECUTION NOT STARTED
**Priority:** MEDIUM
**Key File:** [map_generator.py](map_generator.py)

**What's done:**
- City map concept defined (dark satellite + cyan building footprints)
- map_generator.py script written (generates map from OpenStreetMap data)
- Bellissimo watermark approach defined

**Next action:**
- [ ] Install required Python packages: geopandas, matplotlib, osmnx
- [ ] Run map_generator.py for Huntington, WV + Bradenton, FL
- [ ] Add Bellissimo AI Labs watermark in Canva/Figma
- [ ] Design mailer/postcard template: map + "We see your city. We'd like to see your business."
- [ ] Identify first 50 target businesses in Huntington

---

## THREAD 6 — Company OS Product
**Status:** CONCEPT DEFINED / NOT BUILT
**Priority:** MEDIUM — Phase 4 work
**Key File:** [BELLISSIMO_ROADMAP.md](BELLISSIMO_ROADMAP.md) (Phase 4)

**What's done:**
- Company OS concept defined: Claude + Skills + MCP = AI Chief of Staff
- Skills list drafted (5 initial: Financial Red Flag, Meeting Prep, Client Intel, Proposal Gen, Weekly Digest)
- Flywheel-as-product concept defined

**Next action:**
- [ ] Build first skill: financial-red-flag-detector
- [ ] Document the OS architecture (what MCP servers, what skills, what agents)
- [ ] Identify first OS pilot client from SustainCFO network

---

## THREAD 7 — Learning Path (Agent Fundamentals)
**Status:** PHASE 1 UNDERWAY — AGENT LOOP CONFIRMED WORKING
**Priority:** LOW (but foundational — do this in parallel with everything else)
**Key Files:** [LEARNING_PATH.md](LEARNING_PATH.md), [LEARNING_GUIDE.md](LEARNING_GUIDE.md)

**What's done:**
- Full 5-phase curriculum defined
- agent.py and tools.py built and documented
- Agent loop confirmed working end-to-end (tool_use -> execute -> loop -> end_turn)
- asyncio.to_thread() pattern learned for wrapping sync agents in async servers
- discord.py bot pattern learned (intents, on_message, asyncio.to_thread)
- FastAPI background tasks + in-memory job queue pattern learned

**Next action:**
- [ ] Complete remaining Phase 1 checkboxes
- [ ] Add 6th tool: get_competitor_benchmarks
- [ ] Document agent loop internals in LEARNING_GUIDE.md

---

## THREAD 8 — SustainCFO Integration
**Status:** ONGOING / BEING AUTOMATED
**Priority:** BACKGROUND — keep revenue flowing while building Bellissimo

**Next action:**
- [ ] Identify which SustainCFO workflows can be AI-assisted immediately
- [ ] Use SustainCFO clients as beta testers for the Reveal product
- [ ] Target: reduce SustainCFO time by 50% within 6 months
- [ ] Apollo.io + Go High Level outreach integration (see Thread 9)

---

## THREAD 9 — Conversation Intelligence & Outreach Automation
**Status:** PLANNING
**Priority:** HIGH — unlocks visibility + sales motion
**Key Files:** [conversation_extractor.py](conversation_extractor.py) (to be created)

**What this is:**
Two connected problems:
1. **Conversation Intelligence** — extract action items / decisions from all past Claude Code and ChatGPT sessions into one place
2. **Outreach Automation** — connect Apollo.io (prospect targeting) + Go High Level (pipeline/email sequences) so Claude Code can help find and contact companies

**What's done:**
- Thread defined, approach agreed

**Next action:**
- [ ] Build conversation_extractor.py — reads local Claude Code JSONL transcripts, extracts open actions + decisions, posts to Discord or PROJECT_THREADS.md
- [ ] Export ChatGPT conversation history (Settings → Export) and feed into extractor
- [ ] Set up Apollo.io API key (need account) — build !prospect command
- [ ] Set up Go High Level API key (need account) — build contact/pipeline push
- [ ] Decide: Airtable or GHL as primary CRM for Bellissimo pipeline

**Blocker:** Need Apollo.io account + GHL account (or Airtable) confirmed before building integrations.

---

## SESSION NOTES
*Append notes here at end of each session. Most recent at top.*

### 2026-02-26 (Session 2)
- Built SustainCFO ICP (revenue $3-20M, no FT CFO, sector-agnostic, local-first outreach)
- Designed 10-question Financial Clarity Assessment → built in Google Form → sent to Josh
- Defined 7-stage SustainCFO sales process map (Identify → Outreach → Diagnostic → Deliver → Discovery → Propose → Close)
- Pricing confirmed: $2,500 productized / $5K growth / $7,500+ scale
- Reviewed 2 proposals (Luminus $7,395/mo, Lumina Solar $4,895/mo) — feedback: personalize page 1, sharpen "Our Approach", add differentiation
- Reviewed 3 GHL pipelines: 107 marketing / 37 affiliate / 11 active sales
- Identified hottest active opportunity: Ali Laith dental rollup ($90K, 7 days stale)
- "SustainCFO for a Week" PDF reviewed — positioned as $10K value entry tactic → retainer conversion
- Thread 1 updated: LLC not Wyoming, LOW priority
- Product naming: "Scope" confirmed (not Reveal) for SustainCFO
- PENDING: Josh conversation tonight on form feedback, CFO-for-a-Week pricing, commission structure, GHL outreach strategy

### 2026-02-26
- Deployed discord_bot.py to Hetzner VPS (5.161.215.26) — bot is always-on
- Built !prep with Obsidian vault search + inline context via | separator
- Built !eval — deal scoring agent (score + verdict + next move)
- Built !prospect — Apollo.io search (BLOCKED: Cloudflare 403 on VPS IPs, needs alternate approach)
- Built conversation_extractor.py — reads local Claude Code sessions, extracts action items
- Built apollo_tools.py — Apollo API integration (local use only until proxy/alt solution)
- Built deploy.ps1 — one-command deploy from VS Code (replaces manual SSH workflow)
- Set up passwordless SSH (VPS key auth)
- Set up GitHub SSH key (no more password prompts on git push)
- Created USER_GUIDE.md — daily cadence, commands, keyboard shortcuts, VPS reference
- Resolved double-reply issue (killed local bot process, VPS only)
- Added Thread 9: Conversation Intelligence & Outreach Automation
- STRATEGIC DECISION: Infrastructure phase is done. Next session = revenue focus only.
- Next session priorities: (1) Tally intake form + webhook handler, (2) run real Reveal for 1 warm prospect, (3) Thread 1 legal filing

### 2026-02-25
- Named company: Bellissimo AI Labs
- Created: BELLISSIMO_ROADMAP.md, BUSINESS_SETUP.md, SALES_PACKAGE.md
- Updated: agent.py (two-mode: reveal/xray)
- Created: BRAND_STYLE_GUIDE.md, map_generator.py
- Created: requirements.txt, agent_server.py (FastAPI + async job queue)
- Created: discord_bot.py (!scope, !xray, !help, !status, !threads)
- Discord bot: live and connected, confirmed receiving commands
- Agent: ran end-to-end successfully via !scope in Discord (Acme Manufacturing Co.)
- Fixed: Windows cp1252 encoding errors (unicode arrows in print() replaced with ASCII)
- Fixed: .env vs .env.example — real keys in .env (gitignored), placeholders in .env.example
- Key decisions: Bellissimo Reveal/Scope (not "Brief"), guerrilla map marketing, Wyoming LLC
- Attorney consult needed: LLC vs C Corp before filing
- Priority for next session: Thread 1 (legal formation) + Thread 3 (add 4 new Reveal tools)
