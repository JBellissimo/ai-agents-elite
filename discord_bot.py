"""
discord_bot.py — Bellissimo AI Labs Discord Bot
=================================================
A Discord bot that lets you trigger agents by sending a message.
Run it on any machine (your laptop, a VPS, a Mac Mini) and it stays
connected to Discord 24/7, waiting for your commands.

COMMANDS:
    !scope  <company name>   Run a Bellissimo Scope diagnostic
    !xray   <company name>   Run a SustainCFO X-Ray financial diagnostic
    !prep   <name>           Meeting prep brief (uses Obsidian notes if found)
    !eval   <deal text>      Score + verdict on any deal or opportunity
    !help                    Show available commands
    !status                  Show how many jobs have run this session
    !threads                 Show status of all project threads
    !nudge                   Trigger the daily morning brief on demand

EXAMPLE:
    You type in Discord:   !scope Huntington Family Dental
    Bot replies:           Running Scope on Huntington Family Dental... (~45 sec)
    45 seconds later:      [Full 2-page intelligence report]

SETUP (one-time):
    1. Go to discord.com/developers/applications
    2. Click "New Application" → name it "Bellissimo"
    3. Click "Bot" in the left sidebar → "Add Bot"
    4. Under "Token" click "Reset Token" → copy it
    5. Under "Privileged Gateway Intents" enable "Message Content Intent"
    6. Click "OAuth2" → "URL Generator"
       Scopes: bot | Permissions: Send Messages, Read Message History
    7. Open the generated URL → add bot to your server
    8. Add DISCORD_BOT_TOKEN to your .env file

RUN:
    python discord_bot.py

HAIKU vs SONNET:
    Conversational replies (help, status, errors) → Haiku (fast + cheap)
    Scope / X-Ray runs                            → Sonnet (best quality)
"""

import asyncio
import io
import json
import os
import re
import sys
from datetime import datetime, timezone

# Force UTF-8 on Windows — must happen before any print() calls
# WHY: Windows defaults to cp1252 encoding which can't handle unicode
# characters (like → em-dashes, etc.) that appear in agent output.
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import discord
from anthropic import Anthropic
from dotenv import load_dotenv

from agent import run_agent
from apollo_tools import (
    parse_prospect_query,
    search_companies,
    search_contacts,
    format_company_results,
    format_contact_results,
)

load_dotenv()

# =============================================================================
# CONFIG
# =============================================================================

DISCORD_BOT_TOKEN  = os.getenv("DISCORD_BOT_TOKEN")
MODEL_CHAT         = "claude-haiku-4-5-20251001"   # Fast + cheap for bot chatter
MODEL_AGENT        = "claude-sonnet-4-6"            # Full power for Scope/X-Ray

# Path to Obsidian vault — used by !prep to pull existing notes on a company/person.
# Set OBSIDIAN_VAULT_PATH in .env. Falls back gracefully if not set (VPS has no vault).
OBSIDIAN_VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH", "")

# Channel the daily nudge posts to. Must exactly match the Discord channel name.
DAILY_NUDGE_CHANNEL = "chief-of-staff"
# Time to post daily nudge (24-hour, UTC). 12:00 UTC = 8am ET / 7am CT
DAILY_NUDGE_HOUR_UTC = 12

anthropic_client = Anthropic()

# Session stats — resets when bot restarts
session_stats = {"scopes": 0, "xrays": 0, "started_at": datetime.now(timezone.utc)}

# =============================================================================
# CHANNEL AGENT SYSTEM PROMPTS
# Each conversational channel gets its own agent personality.
# Commands (!scope, !xray, etc.) work in any channel — these prompts only apply
# to freeform messages in channels marked responds_to_all in channel_config.json.
# =============================================================================

SYSTEM_PROMPTS = {
    "daily_nudge": (
        "You are the Bellissimo AI Labs Chief of Staff delivering a daily morning brief. "
        "JB is a solo operator building an AI consulting firm (Bellissimo AI Labs) alongside "
        "a fractional CFO practice (SustainCFO). He values precision and speed. "
        "Active project threads: (1) Legal Formation — NOT STARTED, needs attorney consult; "
        "(2) Brand & Website — BRAND IN PROGRESS; (3) Reveal Product — AGENT RUNNING, needs 4 new tools + first real prospect; "
        "(4) Sales Package — FIRST DRAFT DONE, needs slide deck + 10 warm prospects; "
        "(5) Guerrilla Marketing — CONCEPT DEFINED; (6) Company OS — CONCEPT DEFINED; "
        "(7) Learning Path — PHASE 1 UNDERWAY; (8) SustainCFO — ONGOING.\n\n"
        "Generate a sharp, direct morning brief (max 200 words) that:\n"
        "1. Names the single most important thing to do today and WHY\n"
        "2. Calls out the #1 blocker across all threads\n"
        "3. Gives one specific action JB can take RIGHT NOW (< 15 min)\n"
        "4. Ends with one sharp question to sharpen his thinking\n\n"
        "Vary the tone each day — some days urgent, some days strategic, some days challenging. "
        "Never repeat the same focus two days in a row. Push him forward."
    ),
    "chief_of_staff": (
        "You are the Bellissimo AI Labs Chief of Staff, running inside Discord. "
        "JB is a solo operator building an AI consulting firm (Bellissimo AI Labs) "
        "alongside a fractional CFO practice (SustainCFO). He values precision over politeness. "
        "Active projects are tracked across 8 threads (legal, brand, product, sales, "
        "guerrilla marketing, company OS, learning path, SustainCFO integration). "
        "\n\nYou help by:\n"
        "- Answering questions about active projects directly and concisely\n"
        "- Routing to the right agent command when needed ('Run !scope [company]')\n"
        "- Developing half-baked ideas into actionable next steps\n"
        "- Flagging what's blocking forward progress\n\n"
        "Be concise. No filler. When you see an idea, develop it. When you see a question, "
        "answer it. When something needs a Scope or X-Ray, give the exact command to run."
    ),
    "idea_developer": (
        "You are the Bellissimo Ideas Agent, running in Discord's #ideas-inbox channel. "
        "Users paste raw Apple Notes, voice transcriptions, or half-baked thoughts here. "
        "Your job: turn every input into a structured project brief — fast and decisive.\n\n"
        "For every input, return exactly this structure:\n"
        "**Idea:** [1-sentence summary]\n"
        "**Problem it solves:** [who has this pain, how bad is it]\n"
        "**What you'd build:** [concrete MVP, be specific]\n"
        "**Revenue angle:** [how money flows — consulting fee, product, subscription]\n"
        "**First 3 steps:** [immediate, actionable, in order]\n"
        "**Fits thread:** [which of the 8 PROJECT_THREADS this belongs to, or 'New thread needed']\n\n"
        "Be decisive. No hedging. JB needs a clear path, not a list of questions. "
        "If you need to make assumptions to be decisive, make them and note it briefly."
    ),
    "meeting_prep": (
        "You are a meeting preparation specialist for JB, a fractional CFO/COO and AI consultant. "
        "JB runs SustainCFO (fractional CFO) and is building Bellissimo AI Labs (AI consulting). "
        "He is prep-ping for a business meeting and needs sharp, actionable intelligence.\n\n"
        "Given a company name and any notes provided, return this structured brief:\n\n"
        "**COMPANY SNAPSHOT**\n"
        "[What they do, size, stage, key people, recent news]\n\n"
        "**LIKELY PAIN POINTS**\n"
        "[Top 3 operational or financial problems companies like this typically face]\n\n"
        "**JB'S ANGLE**\n"
        "[Which service fits best: SustainCFO (financial ops), Bellissimo Scope (AI diagnostic), "
        "or Bellissimo OS (ongoing AI implementation). Be specific about WHY.]\n\n"
        "**TALKING POINTS**\n"
        "[3 things to lead with — value-first, not pitch-first]\n\n"
        "**KEY QUESTIONS TO ASK**\n"
        "[5 questions that surface pain, budget, and fit — in priority order]\n\n"
        "**RECOMMENDED NEXT STEP**\n"
        "[One concrete action to advance the relationship after this meeting]\n\n"
        "Be specific and direct. If Obsidian notes are provided, incorporate them fully."
    ),
    "deal_eval": (
        "You are a deal evaluation specialist for JB, a solo operator and AI consultant. "
        "JB evaluates opportunities including: sales commission deals, consulting referrals, "
        "partnerships, and new client engagements. He needs fast, honest deal assessments.\n\n"
        "Given a deal description (email thread, conversation summary, or notes), return:\n\n"
        "**DEAL SUMMARY**\n"
        "[1-2 sentences: what this actually is]\n\n"
        "**OPPORTUNITY SCORE: X/10**\n"
        "[Revenue potential, strategic fit, probability of closing]\n\n"
        "**FIT SCORE: X/10**\n"
        "[Does this match JB's skills, time, and positioning? Is it SustainCFO, Bellissimo, or neither?]\n\n"
        "**UPSIDE**\n"
        "[Best case: what this could become]\n\n"
        "**RISKS & RED FLAGS**\n"
        "[What could go wrong, what's missing from the pitch, what's unclear]\n\n"
        "**VERDICT: PURSUE / NEGOTIATE / PASS**\n"
        "[Clear recommendation with one-sentence rationale]\n\n"
        "**NEXT MOVE**\n"
        "[Specific action if pursuing: what to ask, what to verify, what to propose]\n\n"
        "Be blunt. JB's time is finite. A 'pass' saves more than a weak 'pursue'."
    ),
}

# Load channel config — maps channel names to agent behavior
def load_channel_config() -> dict:
    """
    Reads channel_config.json to determine which channels have conversational agents.
    Reloading on bot restart picks up config changes without code deploys.
    """
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "channel_config.json")
    try:
        with open(config_path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"WARNING: channel_config.json not found at {config_path}")
        return {}

CHANNEL_CONFIG = load_channel_config()

# =============================================================================
# BOT SETUP
# =============================================================================

intents = discord.Intents.default()
intents.message_content = True   # Required to read message text
bot = discord.Client(intents=intents)


# =============================================================================
# HELPERS
# =============================================================================

def haiku_reply(prompt: str) -> str:
    """
    Quick conversational response using Haiku.
    Used for: help text, errors, status messages, chitchat.
    WHY Haiku here: 10x cheaper than Sonnet. No need for heavy reasoning
    on short responses. Keeps costs low for high-frequency interactions.
    """
    response = anthropic_client.messages.create(
        model=MODEL_CHAT,
        max_tokens=300,
        system=(
            "You are the Bellissimo AI Labs assistant bot on Discord. "
            "Be warm, concise, and professional. Max 3 sentences."
        ),
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def generate_daily_nudge() -> str:
    """
    Generate the daily morning brief using Haiku.
    Synchronous — called via asyncio.to_thread() in the scheduler.
    """
    response = anthropic_client.messages.create(
        model=MODEL_CHAT,
        max_tokens=400,
        system=SYSTEM_PROMPTS["daily_nudge"],
        messages=[{"role": "user", "content": "Generate today's morning brief."}],
    )
    return response.content[0].text


def haiku_chat(user_message: str, system_prompt_key: str) -> str:
    """
    Conversational response for designated channels (chief-of-staff, ideas-inbox).
    Uses Haiku for speed + cost efficiency — no heavy agent loop needed here.
    WHY synchronous: called via asyncio.to_thread() in on_message(), same pattern
    as run_agent(). Keeps the event loop free while the API call runs in a thread.
    """
    response = anthropic_client.messages.create(
        model=MODEL_CHAT,
        max_tokens=800,
        system=SYSTEM_PROMPTS[system_prompt_key],
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


def read_thread_statuses() -> str:
    """
    Parse PROJECT_THREADS.md and return a compact Discord-ready status summary.
    Extracts thread name + status for each of the 8 threads.
    """
    threads_file = os.path.join(os.path.dirname(__file__), "PROJECT_THREADS.md")
    try:
        with open(threads_file, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        return "PROJECT_THREADS.md not found."

    # Extract "## THREAD N — Name" and the following "**Status:** VALUE" line
    thread_pattern = re.compile(
        r"## THREAD (\d+) — (.+?)\n\*\*Status:\*\* (.+?)(?:\n|$)"
    )
    matches = thread_pattern.findall(content)

    if not matches:
        return "Could not parse thread statuses from PROJECT_THREADS.md."

    lines = ["**Bellissimo — Project Threads**", "─" * 38]
    for num, name, status in matches:
        # Truncate long status strings
        status_short = status.split(" / ")[0] if " / " in status else status
        if len(status_short) > 30:
            status_short = status_short[:27] + "..."
        lines.append(f"**{num}.** {name}\n    `{status_short}`")

    # Append last session date from SESSION NOTES if present
    session_match = re.search(r"### (\d{4}-\d{2}-\d{2})", content)
    if session_match:
        lines.append(f"\nLast updated: {session_match.group(1)}")

    return "\n".join(lines)


def find_obsidian_note(query: str) -> str:
    """
    Search the Obsidian vault for a .md file matching the query (company or person name).
    Returns file contents if found, empty string if vault not configured or no match.
    Searches all .md filenames case-insensitively — skips hidden directories.
    """
    if not OBSIDIAN_VAULT_PATH or not os.path.isdir(OBSIDIAN_VAULT_PATH):
        return ""

    query_lower = query.lower()
    query_words = query_lower.split()

    for root, dirs, files in os.walk(OBSIDIAN_VAULT_PATH):
        dirs[:] = [d for d in dirs if not d.startswith(".")]   # skip .obsidian etc.
        for filename in files:
            if not filename.endswith(".md"):
                continue
            name_lower = filename[:-3].lower()
            # Match if the full query appears in filename, or all words do
            if query_lower in name_lower or all(w in name_lower for w in query_words):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, encoding="utf-8") as f:
                        return f.read()
                except Exception:
                    return ""
    return ""


def generate_prep_brief(company: str, notes: str) -> str:
    """
    Generate a structured meeting prep brief.
    Uses Haiku for speed — this is a pre-meeting tool, not a deep research session.
    Includes Obsidian notes as context if found.
    """
    user_content = f"Company / Person: {company}\n\n"
    if notes:
        user_content += f"Obsidian Notes:\n{notes}\n\n"
    user_content += "Generate the meeting prep brief."

    response = anthropic_client.messages.create(
        model=MODEL_CHAT,
        max_tokens=900,
        system=SYSTEM_PROMPTS["meeting_prep"],
        messages=[{"role": "user", "content": user_content}],
    )
    return response.content[0].text


def generate_deal_eval(description: str) -> str:
    """
    Evaluate a deal or opportunity.
    Uses Sonnet (MODEL_AGENT) — deals require more nuanced reasoning than chat.
    """
    response = anthropic_client.messages.create(
        model=MODEL_AGENT,
        max_tokens=900,
        system=SYSTEM_PROMPTS["deal_eval"],
        messages=[{"role": "user", "content": description}],
    )
    return response.content[0].text


def format_report_for_discord(report: str, company: str, agent_type: str) -> list[str]:
    """
    Discord has a 2000 character message limit.
    Split long reports into multiple messages with clear headers.
    """
    header = f"**Bellissimo {'Scope' if agent_type == 'scope' else 'X-Ray'}: {company}**\n{'─' * 40}\n"
    full_text = header + report

    # Split into 1900-char chunks (leave room for overhead)
    chunks = []
    while len(full_text) > 1900:
        # Try to split at a newline
        split_at = full_text[:1900].rfind('\n')
        if split_at == -1:
            split_at = 1900
        chunks.append(full_text[:split_at])
        full_text = full_text[split_at:].lstrip('\n')

    chunks.append(full_text)
    return chunks


# =============================================================================
# EVENT HANDLERS
# =============================================================================

async def daily_nudge_scheduler():
    """
    Runs in the background. At DAILY_NUDGE_HOUR_UTC each day, posts a
    proactive morning brief to DAILY_NUDGE_CHANNEL — no user message needed.
    WHY: The chief of staff should push JB forward, not wait to be asked.
    """
    await bot.wait_until_ready()
    print(f"Daily nudge scheduler running — posts at {DAILY_NUDGE_HOUR_UTC}:00 UTC to #{DAILY_NUDGE_CHANNEL}")
    while not bot.is_closed():
        now = datetime.now(timezone.utc)
        # Calculate seconds until next nudge time today (or tomorrow)
        target = now.replace(hour=DAILY_NUDGE_HOUR_UTC, minute=0, second=0, microsecond=0)
        if now >= target:
            target = target.replace(day=target.day + 1)
        wait_seconds = (target - now).total_seconds()
        await asyncio.sleep(wait_seconds)

        # Find the chief-of-staff channel across all guilds
        for guild in bot.guilds:
            channel = discord.utils.get(guild.text_channels, name=DAILY_NUDGE_CHANNEL)
            if channel:
                try:
                    nudge = await asyncio.to_thread(generate_daily_nudge)
                    await channel.send(f"**Good morning — Daily Brief**\n{'─' * 38}\n{nudge}")
                    print(f"Daily nudge posted to #{DAILY_NUDGE_CHANNEL} in {guild.name}")
                except Exception as e:
                    print(f"Daily nudge error: {e}")


@bot.event
async def on_ready():
    print(f"\n{'=' * 50}")
    print(f"Bellissimo Bot is online as: {bot.user}")
    print(f"Connected to {len(bot.guilds)} server(s)")
    print(f"Commands: !scope, !xray, !prep, !eval, !threads, !nudge, !status, !help")
    print(f"{'=' * 50}\n")
    # Start the daily nudge background task
    bot.loop.create_task(daily_nudge_scheduler())


@bot.event
async def on_message(message: discord.Message):
    # Never respond to ourselves
    if message.author == bot.user:
        return

    content = message.content.strip()

    # ==========================================================
    # Per-channel conversational agents
    # If the channel has responds_to_all=true and no ! prefix,
    # route to the channel's designated agent personality.
    # ==========================================================
    channel_name = message.channel.name
    channel_cfg = CHANNEL_CONFIG.get(channel_name, {})

    if channel_cfg.get("responds_to_all") and not content.startswith("!"):
        if not content:
            return
        try:
            reply = await asyncio.to_thread(
                haiku_chat, content, channel_cfg["system_prompt"]
            )
            # Chunk if the reply is long (rare for chat, but safe)
            if len(reply) > 1900:
                for i in range(0, len(reply), 1900):
                    await message.reply(reply[i:i+1900])
            else:
                await message.reply(reply)
        except Exception as e:
            await message.reply(f"Error: `{e}`")
        return

    # ==========================================================
    # !scope <company name>
    # ==========================================================
    if content.lower().startswith("!scope "):
        company = content[7:].strip()
        if not company:
            await message.reply("Usage: `!scope <company name>`\nExample: `!scope Huntington Family Dental`")
            return

        await message.reply(
            f"Running **Scope** on *{company}*...\n"
            f"This takes about 45–60 seconds. I'll reply here when it's done."
        )

        try:
            # Run the heavy agent in a thread — don't block the event loop
            report = await asyncio.to_thread(run_agent, company, "", "reveal")
            session_stats["scopes"] += 1

            chunks = format_report_for_discord(report, company, "scope")
            for chunk in chunks:
                await message.reply(chunk)

        except Exception as e:
            await message.reply(f"Error running Scope on *{company}*: `{e}`")

    # ==========================================================
    # !xray <company name>
    # ==========================================================
    elif content.lower().startswith("!xray "):
        company = content[6:].strip()
        if not company:
            await message.reply("Usage: `!xray <company name>`\nExample: `!xray Acme Manufacturing`")
            return

        await message.reply(
            f"Running **X-Ray** on *{company}*...\n"
            f"CFO-grade financial diagnostic. About 45–60 seconds."
        )

        try:
            report = await asyncio.to_thread(run_agent, company, "", "xray")
            session_stats["xrays"] += 1

            chunks = format_report_for_discord(report, company, "xray")
            for chunk in chunks:
                await message.reply(chunk)

        except Exception as e:
            await message.reply(f"Error running X-Ray on *{company}*: `{e}`")

    # ==========================================================
    # !help
    # ==========================================================
    elif content.lower() == "!help":
        help_text = (
            "**Bellissimo AI Labs — Available Commands**\n"
            "─────────────────────────────────────────\n"
            "`!scope <company>`  — Full business intelligence diagnostic\n"
            "`!xray <company>`   — SustainCFO financial deep-dive\n"
            "`!prep <name> [| notes]` — Meeting prep brief (Obsidian + inline context)\n"
            "`!eval <deal>`      — Score + verdict on any opportunity\n"
            "`!prospect <query>` — Search Apollo for target companies or contacts\n"
            "`!threads`          — Project thread status overview\n"
            "`!nudge`            — Trigger the daily morning brief now\n"
            "`!status`           — Session stats\n"
            "`!help`             — This message\n\n"
            "**Examples:**\n"
            "`!scope Huntington Family Dental`\n"
            "`!prep Mat Sposta`\n"
            "`!eval Commission deal — 15% on $50K contract, close by March`\n"
            "`!prospect dental practices Long Island NY`\n"
            "`!prospect CFO referral partners attorneys Huntington WV`"
        )
        await message.reply(help_text)

    # ==========================================================
    # !status
    # ==========================================================
    elif content.lower() == "!status":
        uptime = datetime.now(timezone.utc) - session_stats["started_at"]
        hours = int(uptime.total_seconds() // 3600)
        minutes = int((uptime.total_seconds() % 3600) // 60)

        status_text = (
            f"**Bellissimo Bot Status**\n"
            f"Uptime: {hours}h {minutes}m\n"
            f"Scopes run: {session_stats['scopes']}\n"
            f"X-Rays run: {session_stats['xrays']}\n"
            f"Status: Online"
        )
        await message.reply(status_text)

    # ==========================================================
    # !threads
    # ==========================================================
    elif content.lower() == "!threads":
        thread_summary = read_thread_statuses()
        await message.reply(thread_summary)

    # ==========================================================
    # !nudge  — trigger the daily brief on demand
    # ==========================================================
    elif content.lower() == "!nudge":
        await message.reply("Generating your brief...")
        try:
            nudge = await asyncio.to_thread(generate_daily_nudge)
            await message.reply(f"**Daily Brief (on demand)**\n{'─' * 38}\n{nudge}")
        except Exception as e:
            await message.reply(f"Error generating brief: `{e}`")

    # ==========================================================
    # !prep <name> [| <inline context>]
    # Finds Obsidian notes on the target, generates a meeting prep brief.
    # Inline context (after |) lets you add texts, updates, or any notes.
    # Example: !prep Mat Sposta | Recent texts: wants intro to Goldin team
    # ==========================================================
    elif content.lower().startswith("!prep "):
        raw = content[6:].strip()
        if not raw:
            await message.reply(
                "Usage: `!prep <name>` or `!prep <name> | <notes>`\n"
                "Example: `!prep Mat Sposta | Recent texts: he wants to intro me to Goldin`"
            )
            return

        # Split on | to separate name from inline context
        if "|" in raw:
            company, inline_notes = raw.split("|", 1)
            company = company.strip()
            inline_notes = inline_notes.strip()
        else:
            company = raw
            inline_notes = ""

        await message.reply(f"Prepping for *{company}*...")
        try:
            vault_notes = await asyncio.to_thread(find_obsidian_note, company)

            # Combine vault notes + inline context
            combined_notes = ""
            if vault_notes:
                combined_notes += f"[From Obsidian vault]\n{vault_notes}"
            if inline_notes:
                if combined_notes:
                    combined_notes += f"\n\n[Additional context]\n{inline_notes}"
                else:
                    combined_notes = inline_notes

            brief = await asyncio.to_thread(generate_prep_brief, company, combined_notes)

            source_tag = ""
            if vault_notes and inline_notes:
                source_tag = "\n\n*[Obsidian notes + inline context incorporated]*"
            elif vault_notes:
                source_tag = "\n\n*[Obsidian notes incorporated]*"
            elif inline_notes:
                source_tag = "\n\n*[Inline context incorporated]*"

            full = f"**Meeting Prep: {company}**\n{'─' * 40}\n{brief}{source_tag}"

            for i in range(0, len(full), 1900):
                await message.reply(full[i:i+1900])
        except Exception as e:
            await message.reply(f"Error generating prep for *{company}*: `{e}`")

    # ==========================================================
    # !eval <deal description or pasted text>
    # Scores and verdicts an opportunity (email, summary, bullet points).
    # ==========================================================
    elif content.lower().startswith("!eval "):
        description = content[6:].strip()
        if not description:
            await message.reply(
                "Usage: `!eval <deal description>`\n"
                "Paste an email, summary, or bullet points after the command."
            )
            return

        await message.reply("Evaluating deal...")
        try:
            evaluation = await asyncio.to_thread(generate_deal_eval, description)
            full = f"**Deal Evaluation**\n{'─' * 40}\n{evaluation}"

            for i in range(0, len(full), 1900):
                await message.reply(full[i:i+1900])
        except Exception as e:
            await message.reply(f"Error evaluating deal: `{e}`")

    # ==========================================================
    # !prospect <natural language description>
    # Searches Apollo.io for matching companies or contacts.
    # Requires APOLLO_API_KEY in .env
    # ==========================================================
    elif content.lower().startswith("!prospect "):
        query = content[10:].strip()
        if not query:
            await message.reply(
                "Usage: `!prospect <description>`\n"
                "Examples:\n"
                "`!prospect dental practices Long Island NY`\n"
                "`!prospect law firm partners Huntington WV under 20 employees`\n"
                "`!prospect CFO referral partners attorneys NYC`"
            )
            return

        await message.reply(f"Searching Apollo for: *{query}*...")
        try:
            def run_prospect_search():
                params = parse_prospect_query(query, anthropic_client)
                search_type = params.get("search_type", "companies")

                if search_type == "contacts":
                    results = search_contacts(
                        titles=params.get("titles", []),
                        locations=params.get("locations", []),
                        industries=params.get("industries", []),
                        company_headcount=params.get("employee_ranges", []),
                        per_page=10,
                    )
                    return format_contact_results(results, query)
                else:
                    results = search_companies(
                        keywords=params.get("keywords", ""),
                        locations=params.get("locations", []),
                        industries=params.get("industries", []),
                        employee_ranges=params.get("employee_ranges", []),
                        per_page=10,
                    )
                    return format_company_results(results, query)

            output = await asyncio.to_thread(run_prospect_search)
            for i in range(0, len(output), 1900):
                await message.reply(output[i:i+1900])

        except ValueError as e:
            # Missing API key
            await message.reply(f"Apollo not configured: `{e}`\nSet APOLLO_API_KEY in .env to enable prospecting.")
        except Exception as e:
            await message.reply(f"Prospect search error: `{e}`")

    # ==========================================================
    # Unknown command starting with !
    # ==========================================================
    elif content.startswith("!"):
        await message.reply(
            "Unknown command. Try `!help` to see what I can do."
        )


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN:
        print("ERROR: DISCORD_BOT_TOKEN not found in .env")
        print("See the setup instructions at the top of this file.")
        exit(1)

    print("Starting Bellissimo Bot...")
    bot.run(DISCORD_BOT_TOKEN)
