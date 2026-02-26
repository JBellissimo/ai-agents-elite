# Bellissimo Bot — Command Reference

## Agent Commands (work in any Discord channel)

| Command | What it does | Time |
|---------|-------------|------|
| `!scope <company>` | Full Bellissimo Scope diagnostic | ~45 sec |
| `!xray <company>` | SustainCFO financial deep-dive | ~45 sec |
| `!prep <name>` | Meeting prep brief — pulls Obsidian notes if found | ~5 sec |
| `!eval <deal text>` | Score + verdict on any opportunity or deal | ~10 sec |
| `!threads` | Project thread status board | instant |
| `!nudge` | Trigger the daily morning brief on demand | ~3 sec |
| `!status` | Bot uptime + runs this session | instant |
| `!help` | Command list | instant |

**Examples:**
```
!scope Huntington Family Dental
!xray Acme Manufacturing Co.
!prep Mat Sposta
!eval Commission deal — 15% on a $50K contract, close by end of March, intro via warm referral
```

---

## Conversational Channels (no ! needed — just talk)

| Channel | Agent | What it does |
|---------|-------|-------------|
| `#chief-of-staff` | Chief of Staff | Routes tasks, answers project questions, develops ideas, flags blockers |
| `#ideas-inbox` | Ideas Agent | Turns raw Apple Notes / voice dumps into structured project briefs |

**Examples in #chief-of-staff:**
```
What's the status of Thread 3?
I'm thinking about building a newsletter for Huntington business owners.
What should I focus on today?
```

**Examples in #ideas-inbox:**
```
[Paste raw Apple Notes text here — no formatting needed]
[Voice transcription dump — just paste]
Had an idea: what if I built a tool that...
```

---

## Workflow: Apple Notes → Project Brief

1. Open Apple Notes, copy your raw note (messy is fine)
2. Open Discord on your phone → go to **#ideas-inbox**
3. Paste the note — send
4. Bot returns a structured project brief in ~5 seconds
5. If it's a new project: the brief includes "Fits thread: New thread needed"
6. Next Claude Code session: paste the brief and say "add this to PROJECT_THREADS.md"

---

## Discord Channel Quick Reference

| Category | Channel | Purpose |
|----------|---------|---------|
| COMMAND CENTER | #chief-of-staff | Universal inbox, full conversation |
| COMMAND CENTER | #daily-brief | Future: 7am morning briefing |
| BELLISSIMO AI LABS | #scope-runs | !scope output goes here |
| BELLISSIMO AI LABS | #build-log | !threads, what shipped |
| SUSTAINCFO | #xray-runs | !xray output goes here |
| IDEAS & PROJECTS | #ideas-inbox | Raw idea capture |
| IDEAS & PROJECTS | #project-tracker | Roadmap / !threads |
| BOT ADMIN | #bot-log | !status, errors |

---

## VS Code / Claude Code Shortcuts

| Action | Shortcut |
|--------|---------|
| Open terminal | Ctrl+` (backtick) |
| New terminal | Ctrl+Shift+` |
| Run last command | Up arrow in terminal |
| Stop running process | Ctrl+C |
| Clear terminal | Ctrl+L |
| Open file quickly | Ctrl+P → type filename |
| Open Claude Code chat | Already open in sidebar |

---

## Bot Management

```bash
# Start the bot
python discord_bot.py

# Stop the bot (in terminal where it's running)
Ctrl+C

# Kill all Python processes (if stuck)
python -c "import psutil; [p.kill() for p in psutil.process_iter(['name']) if 'python' in p.info['name'].lower()]"

# Check if bot is running
python -c "import psutil; print([p.name() for p in psutil.process_iter(['name']) if 'python' in p.info['name'].lower()])"
```

---

## VPS (once deployed to Hetzner)

```bash
# SSH in
ssh root@<server-ip>

# Attach to bot screen session
screen -r bellissimo

# Detach without stopping bot
Ctrl+A then D

# Update bot after code changes
cd /opt/bellissimo && git pull && screen -r bellissimo
# Then Ctrl+C, python3 discord_bot.py, Ctrl+A+D
```
