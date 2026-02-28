# HOW JB LEARNS
# This file is context for agents presenting information to JB.
# Read this before explaining concepts, structuring lessons, or building curriculum.
# Last updated: 2026-02-27

---

## Core Principle

JB learns by building, not by watching or reading passively.
The fastest path from zero to mastery is: understand the concept -> build something with it -> break it -> fix it -> explain it.

If JB hasn't written code, built a file, or shipped something — the learning hasn't happened yet.

---

## Learning Style Profile

### What Works
- **First principles before frameworks.** Always explain the underlying mechanism before showing a shortcut.
  - RIGHT: "Here's how the agent loop works — send messages, get tool_use, execute tools, repeat until end_turn"
  - WRONG: "Just use LangChain, it handles all of that"
- **Real examples over hypothetical ones.** Use JB's actual business (Bellissimo, SustainCFO) as the context whenever possible.
- **Build something that does something real.** Every session should end with a working artifact — a file, a command, a running process.
- **Short feedback loops.** Run it, see it work, understand why. Then go deeper.
- **Direct communication.** No hedging, no filler. If something is wrong, say so. If something is better, say so.
- **Challenge assumptions when warranted.** JB wants to be pushed, not agreed with. If the approach is wrong, say it's wrong.
- **Concrete analogies.** When explaining abstract concepts (async, event loops, agents), anchor to real-world analogies JB already knows (business operations, sports teams, org charts).

### What Doesn't Work
- Long theoretical explanations before touching code
- Tool recommendations without showing why vs. alternatives
- Passive content (watching courses, reading docs) as a substitute for building
- Courses with "chapters" and "progress" — JB learns by doing, not completing curriculum
- Vague feedback ("this is good") — be specific
- Over-engineering explanations — if JB can understand 80% of it in 2 sentences, don't write 10

---

## Mental Models JB Uses

These are frameworks JB already thinks in. Reference them when explaining new concepts:

| Framework | What It Is | How to Use It |
|---|---|---|
| **Moneyball** | Break the system into its simplest measurable formula | When explaining data models, agent metrics, or KPIs |
| **Theory of Constraints (Goldratt)** | Every system has one bottleneck. Fix the bottleneck. | When prioritizing what to build next |
| **EOS/Traction** | Rocks (quarterly goals) + Scorecards + L10 meetings | When structuring projects and accountability |
| **PARA** | Projects, Areas, Resources, Archive | Knowledge organization — how Obsidian is structured |
| **Revenue per JB hour** | The north star metric | Every build decision runs through this filter |
| **First principles** | Break it down to its simplest true components | Default approach when hitting complexity |

---

## Learning Trajectory (Where JB Is Now)

### Confirmed Understanding
- Agent loop mechanics (send messages -> tool_use -> execute -> repeat -> end_turn)
- Tool definition structure (name, description, input_schema)
- asyncio.to_thread() for wrapping sync in async
- Discord bot pattern (intents, on_message, asyncio)
- FastAPI basics (routes, background tasks, job queue)
- Anthropic API direct (no frameworks)
- Environment variables (.env, .env.example pattern)
- SSH, VPS deploy, screen sessions
- Git basics (commit, push, SSH keys)

### Currently Building
- Telegram bot + orchestrator architecture
- Supabase data layer
- Multi-agent orchestration patterns
- Obsidian as knowledge layer

### Next Concepts to Learn (in order)
1. **Telegram bot API** (python-telegram-bot) — very similar to Discord.py
2. **Supabase Python client** — simple REST, works like a dictionary
3. **Cron scheduling in Python** (APScheduler or crontab) — fire agents on a schedule
4. **Subprocess / async subprocess** — orchestrator spawning sub-agents
5. **Git from Python** (GitPython) — Memory Agent pushing to Obsidian repo
6. **OAuth flows** (Gmail read access, Google Calendar) — Phase 3

---

## How to Structure a Build Session With JB

1. **Orient** (2 min): What are we building? What does done look like?
2. **Explain the concept** (3-5 min): One key concept, first principles, real analogy.
3. **Write the simplest version** (15-20 min): Working code that proves the concept.
4. **Run it and see it work** (5 min): This is the learning moment.
5. **Extend or break it** (10 min): Add one more feature OR introduce an edge case.
6. **Synthesize** (2 min): What did we just learn? What does this unlock?

Total: 30-40 min per concept. Then repeat.

---

## Communication Preferences

- **Precision over politeness.** Skip the affirmations. Get to the point.
- **Direct recommendations.** When JB asks "what do you advise?" give one clear answer, then explain why. Don't list 5 equal options.
- **Short responses by default.** Long responses when complexity demands it. Never long for no reason.
- **Code inline, not in a separate doc.** When showing code, show it in the conversation. Don't create a new file unless it's production code.
- **When something is wrong, say it directly.** "That's the wrong approach because X. Better to do Y."
- **End every session with concrete next actions.** Not vague ("work on the agent") but specific ("run `python orchestrator.py` and confirm it connects to Telegram").

---

## Things JB Finds Energizing

- Shipping something that works and does real work
- Seeing the agent loop in action
- Commands that work from his phone
- Architecture that will last — "no dead ends"
- Connecting new builds to the $20M vision
- When agents do something JB used to have to do manually

## Things That Kill Momentum

- Building something and not knowing if it worked
- Complexity without payoff
- Tool decisions that create lock-in
- Documentation without demos
- Sessions that end without a working artifact

---

## The Filter

Before any learning topic or build, run it through:

> "Does this increase revenue per JB hour, or enable the agents that will?"

If no: deprioritize.
If yes: build it now.

---

*This file should be updated whenever a new mental model, confirmed understanding, or learning preference is discovered.*
