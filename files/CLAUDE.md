# CLAUDE.md — AI Agents Elite Learning Project

## Project Context
JB is building an AI agents learning project with three goals:
1. Understand AI agents at an elite level (conceptual + hands-on)
2. Deploy agentic operations for SustainCFO (a ~$1M fractional CFO practice)
3. Prepare for interviews at AI companies (Anthropic, Google, etc.)

## Project Structure
- `agent.py` — Business X-Ray diagnostic agent (core learning artifact)
- `tools.py` — Tool definitions with simulated data (to be replaced with real APIs)
- `LEARNING_PATH.md` — 5-phase curriculum with checkboxes
- `LEARNING_GUIDE.md` — Maps code concepts to interview-ready knowledge
- `SESSION_LOG.md` — End-of-session summaries (append new entries, don't overwrite)
- `.claude/skills/` — Custom skills directory (to be populated in Phase 4)

## Key Architectural Decisions
- NO frameworks (LangChain, CrewAI, etc.) — use raw Anthropic API for deep understanding
- Simulated tool data for rapid prototyping, swap in real APIs incrementally
- Every file is heavily commented to explain WHY, not just WHAT

## The 5-Layer Agent Hierarchy (Reference)
1. Augmented LLM — single call + tools
2. Workflows — deterministic multi-step orchestration
3. Agents — LLM-controlled loops
4. Skills — reusable packaged expertise (SKILL.md + scripts)
5. Flywheels — multi-agent coordination with compounding tool libraries

## Session Summary Convention
When JB says "end of session" or "generate session summary":
1. Summarize what was covered
2. List key insights and decisions
3. Create action items for next session
4. Note open questions
5. List files created/modified
6. Append to SESSION_LOG.md (don't overwrite previous entries)

## JB's Preferences
- First principles thinking, direct communication
- Challenge assumptions when warranted
- Precision over politeness
- Learn by building, not watching courses
- End-of-session summaries with concrete action items
