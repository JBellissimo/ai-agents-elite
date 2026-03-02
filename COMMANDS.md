# Bellissimo OS — Command Reference
# Interface: Telegram (@BellissimoLabs_bot)
# Last updated: 2026-03-01

---

## System Commands

| Command | What it does | Speed |
|---------|-------------|-------|
| `/start` | Confirm VPS is alive | instant |
| `/status` | System health check | instant |
| `/help` | Full command list | instant |
| `/brief` | AI daily brief (on demand) | ~20 sec |

---

## Task Commands

| Command | What it does | Speed |
|---------|-------------|-------|
| `!tasks` | Area summary with task counts | instant |
| `!tasks [area]` | All tasks in that area | instant |
| `!add [task]` | Capture a normal task | instant |
| `!add !! [task]` | Capture an urgent task | instant |
| `!add [Area] [task]` | Task with explicit area tag | instant |
| `!add !! [Area] [task]` | Urgent task with area | instant |
| `!done [partial title]` | Mark task done (fuzzy match) | instant |
| `!brief` | AI brief — Claude reads tasks + strategy | ~20 sec |

**Examples:**
```
!tasks
!tasks SustainCFO
!add Call Ali Laith back
!add !! Follow up on dental proposal
!add [Bellissimo] Draft Reveal template
!add !! [SustainCFO] Josh needs P&L by EOD
!done Ali Laith
```

---

## Meeting Prep

| Command | What it does | Speed |
|---------|-------------|-------|
| `!meetingprep [Full Name]` | Research + background + conversation script | ~20 sec |

**Flow:**
1. Send `!meetingprep Bryan Gelnett`
2. Bot asks: "Paste email/LinkedIn context, or reply 'skip'"
3. Paste any email thread, LinkedIn message, or notes — or just reply `skip`
4. Brief arrives in ~20 seconds. Saved to `meeting_briefs/` on VPS.

**Examples:**
```
!meetingprep Sammy Popat
!meetingprep Bryan Gelnett
!meetingprep Josh Notes
```

---

## VS Code / Claude Code Shortcuts

| Action | Shortcut |
|--------|---------|
| Open terminal | Ctrl+` (backtick) |
| New terminal tab | Ctrl+Shift+` |
| Quick open file | Ctrl+P → type filename |
| Command palette | Ctrl+Shift+P |
| Stop running process | Ctrl+C |
| Clear terminal | Ctrl+L |

---

## Deploy

From VS Code terminal (one command):
```
powershell -File deploy.ps1
```

What it does: git push → VPS git pull → pip install → kill old process → start new screen session.

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
| View logs | `screen -r bellissimo` (scroll up) |

---

## What's Coming

- `!meetingprep` auto-pull Gmail thread (OAuth not yet set up)
- `/ceo` `/coo` `/cmo` `/cgo` as Telegram commands
- Todoist integration for task sync
- Google Calendar integration for auto-triggered meeting prep
