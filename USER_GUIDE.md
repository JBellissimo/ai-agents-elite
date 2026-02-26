# Bellissimo Discord OS — User Guide

## What This Is

Your Discord server is a 24/7 AI command center running on a Hetzner VPS in Virginia.
It does not need your laptop. It does not go offline. It responds from your phone.

Three modes of interaction:
- **Commands** (`!` prefix) — trigger specific agents from any channel
- **Conversation** — talk to agents in designated channels, no `!` needed
- **Automatic** — bot proactively posts without you doing anything

---

## Daily Cadence

### Automatic (no action required)
| Time | What happens | Where |
|------|-------------|-------|
| **8:00 AM ET** | Daily brief posts automatically | `#chief-of-staff` |

The daily brief includes: #1 priority for today, top blocker across all threads,
one action you can take in < 15 min, one sharp question to sharpen your thinking.

### On-Demand Habits
| When | Command | What you get |
|------|---------|-------------|
| Before any meeting | `!prep <name>` | Sharp brief with talking points + questions |
| Inbound lead or deal | `!eval <description>` | Score, verdict, next move |
| Monday morning | `!nudge` + `!threads` | Brief + project status board |
| Running a prospect | `!scope <company>` | Full business intelligence report |
| Financial diagnosis | `!xray <company>` | CFO-grade financial diagnostic |

---

## All Commands

### Agent Commands (work in any channel)

| Command | What it does | Speed |
|---------|-------------|-------|
| `!scope <company>` | Full Bellissimo Scope diagnostic | ~45 sec |
| `!xray <company>` | SustainCFO financial deep-dive | ~45 sec |
| `!prep <name>` | Meeting prep — pulls Obsidian notes if on laptop | ~5 sec |
| `!prep <name> \| <notes>` | Meeting prep with pasted context (texts, updates) | ~5 sec |
| `!eval <deal text>` | Score + verdict on any opportunity | ~10 sec |
| `!threads` | All 8 project thread statuses | instant |
| `!nudge` | Trigger daily brief on demand | ~3 sec |
| `!status` | Bot uptime + session run counts | instant |
| `!help` | Command list in Discord | instant |

### !prep Context Examples
```
# Basic (uses Obsidian if on laptop, LLM knowledge only on VPS)
!prep Mat Sposta

# With inline context — paste texts, notes, or updates after the |
!prep Mat Sposta | Recent texts: wants to intro me to someone at Goldin. Interested in fractional COO for CHCK.AI. Meeting is about partnership, not consulting pitch.

# Works for any name or company
!prep Huntington Family Dental | Referred by Dr. Cohen. They have 3 locations. Staff of 40. No current CFO.
```

### !eval Examples
```
# Paste any deal description — email, bullet points, whatever you have
!eval Commission deal — 15% on a $50K contract, close by end of March, warm referral from Josh

!eval Mat Sposta wants me to do fractional COO for CHCK.AI. Early stage, ~$200K revenue, 2 employees. No equity discussed yet, retainer model.

!eval Inbound from law firm in Huntington — 8 attorneys, $2M revenue, no in-house CFO, saw me on LinkedIn
```

---

## Conversational Channels

### #chief-of-staff
Just type. No `!` needed. The agent knows your 8 project threads, both businesses, and how to route tasks.

```
What's blocking Thread 3?
I have a call with Mat Sposta in an hour — what should I focus on?
What should I work on this afternoon?
I'm thinking about doing a newsletter for Huntington business owners. Thoughts?
```

### #ideas-inbox
Paste raw Apple Notes, voice transcription dumps, or half-baked ideas. Returns a structured project brief every time.

```
[paste any messy Apple Notes text]
[paste voice-to-text transcription]
Had an idea while driving: what if I...
```

---

## Updating the Bot (When Code Changes)

When you build something new with Claude Code:

**Step 1 — Push from VS Code**
```
git push
```
(or use VS Code Source Control sidebar → Sync)

**Step 2 — Update the VPS**
Open a terminal and SSH in:
```bash
ssh root@5.161.215.26
cd /opt/bellissimo && git pull
screen -r bellissimo
```
Then: **Ctrl+C** → `python3 /opt/venv/bin/python3 discord_bot.py` → **Ctrl+A then D**

---

## Keyboard Shortcuts

### VS Code
| Action | Shortcut |
|--------|---------|
| Open/close terminal | Ctrl+` |
| New terminal tab | Ctrl+Shift+` |
| Quick open file | Ctrl+P → type filename |
| Command palette | Ctrl+Shift+P |
| Split editor | Ctrl+\ |
| Stop running process | Ctrl+C (in terminal) |
| Clear terminal | Ctrl+L |

### Discord (Desktop)
| Action | Shortcut |
|--------|---------|
| Jump to any channel | Ctrl+K |
| Mark all as read | Escape |
| Edit last message | Up arrow |
| React to message | Hover → click emoji |
| View keyboard shortcuts | Ctrl+/ |

### Discord (Mobile)
- Swipe right to open server list
- Long-press any message to react/copy
- @ mention + channel name to jump

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

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Bot not responding | SSH in → `screen -r bellissimo` — is it running? |
| Double replies | Two instances running — kill local Python process |
| `!prep` returns no Obsidian notes | Either: (a) run bot locally, or (b) use `!prep name \| notes` format |
| Bot went offline | `screen -r bellissimo` → restart with python3 command |
| Code changes not live | Did you `git push` and then `git pull` on VPS? |

---

## What's Coming (Future Builds)

- `!add-thread` — add new project thread from Discord
- Daily brief pulls from Google Calendar
- `!scope` sends output to `#scope-runs` channel automatically
- Apple Shortcuts → auto-post to `#ideas-inbox` on iPhone
- Multi-turn memory in `#chief-of-staff`
