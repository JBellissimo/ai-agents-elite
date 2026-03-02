# Bellissimo OS — User Guide
# Interface: Telegram (@BellissimoLabs_bot)
# Last updated: 2026-03-01

## What This Is

Bellissimo OS is a 24/7 AI command center running on a Hetzner VPS.
It does not need your laptop. It does not go offline. It responds from your iPhone.

Interface: **Telegram** (@BellissimoLabs_bot). All commands go here.
Deploy: **deploy.ps1** from VS Code. One command pushes code + restarts the VPS bot.

---

## Daily Cadence

### Automatic
| Time | What happens |
|------|-------------|
| **5:00 AM ET** | AI daily brief sent to Telegram automatically |

The brief applies Theory of Constraints to your task list + STRATEGIC_NORTH_STAR.md.
Output: TOP 3 TODAY, TIME-SENSITIVE, DEFER, and the single CONSTRAINT.

### On-Demand Habits
| When | Command | What you get |
|------|---------|-------------|
| Before any meeting | `!meetingprep [Name]` | Background + opportunity + conversation script |
| Morning check-in | `!brief` | On-demand AI brief |
| Capture a thought | `!add [task]` | Task saved instantly |
| Inbound opportunity | `!add !! [Bellissimo] [description]` | Urgent, tagged |

---

## All Commands

### System
| Command | What it does |
|---------|-------------|
| `/start` | Confirm VPS is alive |
| `/status` | System health check |
| `/help` | Full command list |
| `/brief` | AI daily brief |

### Tasks
| Command | What it does |
|---------|-------------|
| `!tasks` | Area summary (counts by area) |
| `!tasks [area]` | Full list for that area |
| `!add [task]` | Add normal task |
| `!add !! [task]` | Add urgent task |
| `!add [Area] [task]` | Add task with area tag |
| `!done [partial title]` | Mark done by fuzzy match |
| `!brief` | AI-generated daily brief |

### Meeting Prep
| Command | What it does |
|---------|-------------|
| `!meetingprep [Full Name]` | Research + brief + conversation script (~20 sec) |

**Flow:** Send command → bot asks for context → paste email/LinkedIn or reply `skip` → brief arrives.

---

## Deploy Workflow

One command from VS Code terminal:
```powershell
powershell -File deploy.ps1
```

Automatically: git push → VPS git pull → pip install → restart orchestrator.

---

## VS Code Shortcuts

| Action | Shortcut |
|--------|---------|
| Open/close terminal | Ctrl+` |
| New terminal tab | Ctrl+Shift+` |
| Quick open file | Ctrl+P → type filename |
| Command palette | Ctrl+Shift+P |
| Stop process | Ctrl+C (in terminal) |
| Clear terminal | Ctrl+L |

---

## VPS Reference

| Thing | Value |
|-------|-------|
| IP | 5.161.215.26 |
| SSH | `ssh root@5.161.215.26` |
| Bot location | `/opt/bellissimo/` |
| Python env | `/opt/venv/bin/python3` |
| Screen session | `screen -r bellissimo` |
| Detach (keep running) | Ctrl+A then D |

Manual restart if needed:
```bash
ssh root@5.161.215.26
screen -r bellissimo   # attach
# Ctrl+C to stop
/opt/venv/bin/python3 /opt/bellissimo/orchestrator.py
# Ctrl+A then D to detach
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Bot not responding | SSH in → `screen -r bellissimo` — is it running? |
| Two replies per message | Two instances running — Ctrl+C local process |
| Bot went offline (VPS reboot) | SSH in → manually restart screen session |
| deploy.ps1 fails | Check for uncommitted local changes first |
| `!meetingprep` search fails | DuckDuckGo rate limit — wait 60 sec and retry |

---

## What's Coming

- `!meetingprep` auto-pull Gmail context
- `/ceo` `/coo` `/cmo` `/cgo` via Telegram
- Todoist task sync
- Google Calendar → auto-trigger `!meetingprep`
- Systemd service on VPS (auto-restart after reboots)
