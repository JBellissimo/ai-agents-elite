#!/usr/bin/env python3
"""
orchestrator.py -- Bellissimo Agent OS
Phase 0: Prove the loop. Telegram connection only.

This is the always-on process that runs on the Hetzner VPS.
It is the single entry point for all agent commands.

Architecture:
    JB (iPhone) --> Telegram --> This process --> Agents/Data

Security:
    TELEGRAM_USER_ID in .env is the ONLY authorized sender.
    All other users are rejected immediately.

Phase 0 (now):    Telegram connected. Basic commands. Loop proven.
Phase 1 (next):   Supabase connected. !tasks, !add, !done, !brief live.
Phase 2 (later):  Cron agents. 5am brief reads Obsidian Daily Note.
Phase 3 (future): Gmail, Calendar, Monday.com integrations.

Run on VPS:
    screen -S bellissimo
    python orchestrator.py

Deploy:
    From Windows: run deploy.ps1 (pushes to GitHub, VPS pulls + restarts)
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

load_dotenv()

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Your personal Telegram user ID. Get it by messaging @userinfobot in Telegram.
# IMPORTANT: If not set, bot will respond to anyone. Set this before deploying.
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))

# Obsidian vault path.
# On Windows (local): C:\Users\Admin\Documents\Obsidian Vault
# On VPS (Phase 2): path to cloned bellissimo-obsidian-vault repo
OBSIDIAN_VAULT_PATH = Path(
    os.getenv("OBSIDIAN_VAULT_PATH", "/home/bellissimo/obsidian-vault")
)

# ---------------------------------------------------------------------------
# MENTAL MODELS — 4-STEP REASONING CHAIN
#
# These files live at: {vault}/99_System/Mental Models/
# The orchestrator loads them as context before any planning or prioritization.
#
# WHEN TO USE THIS CHAIN:
#   YES — 5am daily brief, /coo, /ceo, /cgo, task prioritization
#   LIGHTWEIGHT (steps 1-2 only) — new task capture, !add evaluation
#   NO — direct data ops: !tasks, !done, !status, !add (just storing)
#
# WHY: Before deciding what to do, the agent must first identify the real
# constraint, validate the solution, anticipate failure, and check second-
# order effects. This prevents solving the wrong problem efficiently.
# ---------------------------------------------------------------------------

MENTAL_MODELS_DIR = OBSIDIAN_VAULT_PATH / "99_System" / "Mental Models"

MENTAL_MODELS_CHAIN = [
    {
        "step": 1,
        "name": "Theory of Constraints",
        "file": MENTAL_MODELS_DIR / "Theory_of_Constraints.md",
        "question": "What is the real constraint right now?",
    },
    {
        "step": 2,
        "name": "First Principles",
        "file": MENTAL_MODELS_DIR / "First_Principles.md",
        "question": "Is our proposed solution actually valid?",
    },
    {
        "step": 3,
        "name": "Invert Everything",
        "file": MENTAL_MODELS_DIR / "Invert_Everything.md",
        "question": "What would guarantee this fails?",
    },
    {
        "step": 4,
        "name": "Systems Thinking",
        "file": MENTAL_MODELS_DIR / "Systems_Thinking.md",
        "question": "If this works, what does it break?",
    },
]


def load_mental_models(steps: list = None) -> str:
    """
    Loads mental model files from the Obsidian vault and returns them
    as a formatted string for inclusion in an agent system prompt.

    Args:
        steps: List of step numbers to load (1-4). Default: all four.
               Pass [1, 2] for lightweight mode (task capture).

    Returns:
        Formatted string ready to inject into a system prompt.
        Returns a fallback string if vault is not yet accessible (pre-Phase 2).

    WHY: Agents need the mental models as context, not just their names.
    Reading the actual .md files means the agent gets JB's exact framing.
    """
    steps_to_load = steps or [1, 2, 3, 4]
    output_parts = ["## Reasoning Chain (apply before planning or prioritizing)\n"]

    loaded_any = False
    for model in MENTAL_MODELS_CHAIN:
        if model["step"] not in steps_to_load:
            continue

        file_path = model["file"]
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            output_parts.append(
                f"### Step {model['step']}: {model['name']}\n"
                f"Question to answer: {model['question']}\n\n"
                f"{content}\n"
            )
            loaded_any = True
        else:
            # Vault not yet accessible (Obsidian Git not set up, or VPS pre-Phase 2)
            output_parts.append(
                f"### Step {model['step']}: {model['name']}\n"
                f"Question: {model['question']}\n"
                f"[File not found: {file_path} -- set up Obsidian Git to enable]\n"
            )

    if not loaded_any:
        logger.warning(
            f"Mental models not accessible at {MENTAL_MODELS_DIR}. "
            "This is expected until Obsidian Git is configured on VPS (Phase 2)."
        )

    return "\n".join(output_parts)


def build_planning_prompt(base_prompt: str, use_full_chain: bool = True) -> str:
    """
    Wraps a base system prompt with the mental models reasoning chain.

    Use for: 5am brief, /coo, /ceo, /cgo, /cmo, task prioritization.
    Set use_full_chain=False for lightweight mode (task capture, steps 1-2 only).

    WHY: Every planning and prioritization decision should run through
    the 4-step chain before producing output. This is the reasoning gate.
    """
    steps = [1, 2, 3, 4] if use_full_chain else [1, 2]
    mental_models_context = load_mental_models(steps=steps)
    return f"{base_prompt}\n\n{mental_models_context}"

# ---------------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# SECURITY
# Only JB's Telegram user ID can issue commands.
# This is the security primitive -- enforced on every handler.
# ---------------------------------------------------------------------------

async def is_authorized(update: Update) -> bool:
    """
    Returns True if the message is from JB.
    Logs and rejects all unauthorized attempts.

    WHY: Telegram is the ONLY authenticated command channel.
    Anyone who finds the bot handle cannot use it without JB's user ID matching.
    """
    if TELEGRAM_USER_ID and update.effective_user.id != TELEGRAM_USER_ID:
        logger.warning(
            f"Unauthorized access attempt: user_id={update.effective_user.id} "
            f"username={update.effective_user.username}"
        )
        await update.message.reply_text("Unauthorized.")
        return False
    return True


# ---------------------------------------------------------------------------
# COMMAND HANDLERS
# ---------------------------------------------------------------------------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start -- confirms bot is alive and connected to VPS.
    This is the Phase 0 proof-of-loop command.
    Send this from iPhone. If you get a response, Phase 0 is complete.
    """
    if not await is_authorized(update):
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await update.message.reply_text(
        "Bellissimo OS Online\n"
        f"Phase 0 -- loop proven\n"
        f"VPS time: {now}\n\n"
        "Phase 1 commands (coming soon):\n"
        "  !tasks    -- see your tasks\n"
        "  !add      -- capture a task\n"
        "  !brief    -- priority summary\n"
        "  /status   -- system health"
    )
    logger.info(f"Loop proven. Start command from user_id={update.effective_user.id}")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /status -- system health check.
    Phase 0: confirms orchestrator is running.
    Phase 1+: will show Supabase connection, cron schedule, agent queue.
    """
    if not await is_authorized(update):
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await update.message.reply_text(
        "Orchestrator Status\n"
        "-------------------\n"
        f"Online:    Yes\n"
        f"Phase:     0 (Foundation)\n"
        f"Time:      {now}\n"
        f"Supabase:  Not connected (Phase 1)\n"
        f"Cron:      Not scheduled (Phase 2)\n"
        f"Agents:    None spawned yet"
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /help -- show available commands.
    Grows as phases are completed.
    """
    if not await is_authorized(update):
        return

    await update.message.reply_text(
        "Bellissimo OS -- Commands\n"
        "-------------------------\n"
        "Phase 0 (now):\n"
        "  /start    -- confirm online\n"
        "  /status   -- system health\n"
        "  /help     -- this message\n\n"
        "Phase 1 (coming):\n"
        "  !tasks [area]\n"
        "  !add [task]\n"
        "  !done [task]\n"
        "  !brief\n"
        "  !scope [company]\n"
        "  !prep [name]\n\n"
        "C-Suite (Phase 2):\n"
        "  /ceo  /coo  /cmo  /cgo"
    )


# ---------------------------------------------------------------------------
# CATCH-ALL MESSAGE HANDLER
# Phase 0: log and acknowledge everything.
# Phase 1: route to Task Agent or Chief of Staff based on content.
# ---------------------------------------------------------------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles all non-command text messages.

    Phase 0: logs the message + acknowledges receipt.
    Phase 1: will route to Task Agent or Chief of Staff.

    WHY this matters: in Phase 1, freeform messages like
    "remember to call Marcus tomorrow" get parsed by Task Agent
    and turned into structured tasks in Supabase automatically.
    """
    if not await is_authorized(update):
        return

    user_msg = update.message.text
    logger.info(f"Message received: {user_msg}")

    await update.message.reply_text(
        f"Received: {user_msg}\n\n"
        f"[Phase 1: this will route to Task Agent or Chief of Staff]"
    )


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    if not TELEGRAM_TOKEN:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN not set in .env\n"
            "1. Create bot via @BotFather in Telegram\n"
            "2. Copy token to .env as TELEGRAM_BOT_TOKEN=<token>"
        )

    if not TELEGRAM_USER_ID:
        logger.warning(
            "TELEGRAM_USER_ID not set -- bot will respond to ANYONE. "
            "Get your ID from @userinfobot and set it in .env before deploying."
        )

    logger.info("Bellissimo Orchestrator starting up...")
    logger.info(f"Authorized user ID: {TELEGRAM_USER_ID or 'NOT SET (open access)'}")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register handlers -- order matters
    # Commands first (matched by /command prefix)
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("help", cmd_help))

    # Catch-all text handler (must be last -- matches everything that isn't a command)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Orchestrator running. Listening for Telegram messages...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
