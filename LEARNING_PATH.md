# Learning Path — AI Agents Elite

5-phase curriculum. Each phase builds on the last. Check boxes as you complete them.

---

## Phase 1 — Foundation: The Agent Loop
*Goal: Understand exactly what makes an agent an agent.*

- [ ] Read `agent.py` end-to-end and explain the loop in your own words
- [ ] Read `tools.py` and understand why tool definitions are separate from tool logic
- [ ] Run the agent against the Acme demo — observe the stop_reason cycle
- [ ] Answer without notes: What is stop_reason="tool_use" telling you?
- [ ] Answer without notes: Why does the API require tool results in role="user"?
- [ ] Explain the difference between an agent and a chatbot (one sentence)
- [ ] Add a 6th tool to tools.py (e.g., `get_competitor_benchmarks`) and verify it works
- [ ] Modify the system prompt and observe how agent behavior changes

**Phase 1 Complete when:** You can rebuild the agent loop from memory on a whiteboard.

---

## Phase 2 — Control: Memory, State, and Context
*Goal: Understand how agents manage state across turns.*

- [ ] Explain why the API is stateless and what that means for agent design
- [ ] Add "session memory" — persist conversation history to a JSON file between runs
- [ ] Implement a simple key-value memory store the agent can read/write via tools
- [ ] Add a `summarize_previous_session` tool that loads the last session summary
- [ ] Experiment: What happens when the context window fills up? How do you handle it?
- [ ] Implement context compression (summarize old messages to save tokens)

**Phase 2 Complete when:** Your agent remembers what it learned about a client last session.

---

## Phase 3 — Reliability: Error Handling, Validation, and Observability
*Goal: Build agents that fail gracefully and that you can debug.*

- [ ] Add structured logging to every tool call (input, output, latency)
- [ ] Implement retry logic with exponential backoff for API errors
- [ ] Add input validation to every tool function
- [ ] Handle the case where a tool returns an error — does the agent recover?
- [ ] Add a cost tracker (token usage per session, cumulative cost)
- [ ] Build a simple test harness: run agent, assert output contains expected sections
- [ ] Implement timeout handling — what if a tool call hangs?

**Phase 3 Complete when:** You can run the agent in production and know exactly what happened.

---

## Phase 4 — Skills: Packaged Reusable Expertise
*Goal: Understand how skills compound an agent's capabilities.*

- [ ] Read `.claude/skills/session-summary.md` — understand the skill format
- [ ] Build a custom skill: `financial-red-flag-detector` (scans any data for CFO red flags)
- [ ] Build a custom skill: `ratio-benchmarker` (compares metrics to industry benchmarks)
- [ ] Package the Business X-Ray agent as a skill callable by other agents
- [ ] Understand: Why are skills different from tools? (tools = functions; skills = expertise patterns)
- [ ] Create a skill library directory: `.claude/skills/` with 5+ skills

**Phase 4 Complete when:** You have a skill library that makes every future agent smarter.

---

## Phase 5 — Flywheels: Multi-Agent Coordination
*Goal: Build systems where agents hand off work to other agents.*

- [ ] Build a coordinator agent that spawns sub-agents for specific tasks
- [ ] Implement the "subagent" pattern: coordinator → specialist → result → coordinator
- [ ] Build a parallel execution pattern: multiple agents running simultaneously
- [ ] Connect agents to real APIs (start with one: QuickBooks or Stripe sandbox)
- [ ] Design a SustainCFO flywheel: new client onboarding → diagnostic → ongoing monitoring
- [ ] Interview prep: explain multi-agent tradeoffs (coordination overhead vs parallelism)

**Phase 5 Complete when:** You have a working multi-agent system and can describe its architecture to an interviewer.

---

## Interview Readiness Checklist

- [ ] Explain the agent loop without referring to notes
- [ ] Describe the 5-layer hierarchy with real examples from this project
- [ ] Articulate why you'd choose raw API over frameworks (and when you wouldn't)
- [ ] Explain context window management tradeoffs
- [ ] Describe a production failure mode you've encountered and how you handled it
- [ ] Walk through a multi-agent architecture you designed
- [ ] Explain how skills/tools/agents differ from each other
