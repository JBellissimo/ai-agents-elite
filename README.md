# ai-agents-elite

Build AI agents at an elite level — no frameworks, no shortcuts, first principles.

## Goals
1. Understand AI agents at an architectural level (conceptual + hands-on)
2. Deploy agentic operations for SustainCFO (~$1M fractional CFO practice)
3. Prepare for interviews at AI companies (Anthropic, Google, etc.)

## Philosophy
**No LangChain. No CrewAI. Raw Anthropic API only.**

Frameworks are fine for production — but they hide the architecture.
To think and talk about agents at an elite level, you need to see exactly
what's happening under the hood. Build from scratch first.

## The 5-Layer Agent Hierarchy

| Layer | Name | Description |
|-------|------|-------------|
| 1 | Augmented LLM | Single model call + tool access |
| 2 | Workflows | Deterministic multi-step orchestration |
| 3 | Agents | LLM-controlled loops with tool use |
| 4 | Skills | Reusable packaged expertise |
| 5 | Flywheels | Multi-agent coordination + compounding tool libraries |

## Project Structure

```
ai-agents-elite/
├── agent.py          # Business X-Ray agent (Layer 3 — the core artifact)
├── tools.py          # Tool definitions + simulated data (swap in real APIs)
├── .env              # Your API keys (never commit this)
├── .env.example      # Template for .env
├── LEARNING_PATH.md  # 5-phase curriculum with checkboxes
├── LEARNING_GUIDE.md # Code concepts → interview-ready knowledge
├── SESSION_LOG.md    # End-of-session summaries
└── .claude/
    ├── CLAUDE.md                      # Project context for Claude Code
    └── skills/
        └── session-summary.md         # /session-summary skill
```

## Quick Start

```bash
# 1. Clone and enter the project
cd ai-agents-elite

# 2. Set up virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install anthropic python-dotenv

# 4. Configure API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 5. Run the agent
python agent.py
```

## Current Status
- **Phase 1** — Foundation: The agent loop, tool use, message history
- First artifact: Business X-Ray diagnostic agent (Acme Manufacturing demo)

See `LEARNING_PATH.md` for the full curriculum.