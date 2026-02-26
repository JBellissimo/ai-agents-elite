# Learning Guide — Code Concepts → Interview Knowledge

This file maps what you see in the code to what you need to say in interviews.
Every section: what it is in the code → why it matters → how to talk about it.

---

## 1. The Agent Loop (agent.py: `run_agent()`)

**What you see in the code:**
```python
while iteration < max_iterations:
    response = client.messages.create(...)
    if response.stop_reason == "tool_use":
        # execute tools, append results, loop
    elif response.stop_reason == "end_turn":
        return final_text
```

**Why it matters:**
The loop is the entire definition of an agent. Without it, you have a single-turn LLM call.
The loop gives the model agency — it decides when it has enough information to stop.

**Interview language:**
> "An agent is fundamentally a loop that lets the model drive its own execution.
> The model decides which tools to call, in what order, and when it's done.
> My implementation runs this loop explicitly so I can observe and control each iteration."

**Common interview question:** "What's the difference between an LLM and an agent?"
**Answer:** Agency = the loop. The model controls flow, not just content.

---

## 2. Tool Definitions vs Tool Implementations (tools.py)

**What you see in the code:**
- `TOOL_DEFINITIONS` — JSON schemas (what the model reads)
- `execute_tool()` — dispatcher (what your code runs)
- `_get_revenue_data()` etc. — implementations (simulated → real APIs)

**Why it matters:**
This separation is the correct architecture. The model never sees your implementation —
it only sees the schema. This means you can swap implementations (simulated → QuickBooks)
without changing a single line in agent.py.

**Interview language:**
> "Tool definitions are a contract between my code and the model. The model reads the
> JSON schema to understand what tools exist and when to call them. My dispatch layer
> translates model intent into actual function calls. This separation means the agent
> layer is completely decoupled from the data layer."

---

## 3. Message History (agent.py: `messages` list)

**What you see in the code:**
```python
messages = [{"role": "user", "content": user_message}]
# After each tool call:
messages.append({"role": "assistant", "content": response.content})
messages.append({"role": "user", "content": tool_results})
```

**Why it matters:**
The API is stateless. Every call sends the full conversation history.
This is both the limitation (context window) and the feature (complete replay).

**Interview language:**
> "State management is one of the hardest parts of agent design. The API is stateless —
> there's no session on the server. I maintain the message history client-side and send
> it with every call. This gives me complete control and observability, but requires me
> to manage context window limits explicitly."

**The gotcha about tool results:**
Tool results must be sent as `role: "user"` messages. This is an API requirement —
the model treats tool output as external information coming back to it.

---

## 4. System Prompt as Agent Behavior Control

**What you see in the code:**
```python
SYSTEM_PROMPT = """You are a Business X-Ray Agent...
DIAGNOSTIC FRAMEWORK:
1. Revenue Health...
RULES:
- Call ALL relevant tools before writing your final analysis"""
```

**Why it matters:**
The system prompt is your primary mechanism for shaping agent behavior.
It defines role, constraints, output format, and decision rules.
Bad system prompts = unpredictable agents.

**Interview language:**
> "System prompt engineering is underrated in agent design. For production agents,
> the system prompt is essentially the agent's operating procedure — it defines
> what the agent optimizes for, what it avoids, and how it structures its output.
> I've found that explicit rules ('call ALL tools before writing analysis') produce
> more reliable behavior than vague persona descriptions."

---

## 5. The 5-Layer Hierarchy

**What you see in this project:**
- `agent.py` is currently **Layer 3 (Agent)** — LLM-controlled loop with tools
- `.claude/skills/` will hold **Layer 4 (Skills)** — packaged expertise
- Phase 5 will build **Layer 5 (Flywheels)** — multi-agent coordination

**The layers:**
| Layer | Name | Key Characteristic |
|-------|------|--------------------|
| 1 | Augmented LLM | Single call + tools, no loop |
| 2 | Workflow | Deterministic steps, LLM fills in slots |
| 3 | Agent | LLM controls the loop |
| 4 | Skills | Reusable expertise packaged for reuse |
| 5 | Flywheel | Multi-agent + compounding tool library |

**Interview language:**
> "I think about agents in 5 layers. Most people jump to 'multi-agent' when they hear
> 'agentic system' but the real power progression is: first make the loop reliable,
> then package expertise as skills, then coordinate multiple agents. The mistake is
> building coordination complexity before you have reliable single-agent behavior."

---

## 6. Why No Frameworks

**The decision:** Raw Anthropic API only (no LangChain, CrewAI, AutoGen, etc.)

**Why:**
- Frameworks abstract the message history, tool dispatch loop, and stop_reason handling
- If you don't know what's under the abstraction, you can't debug it in production
- You can't speak about agent architecture credibly if you only know the framework layer
- Frameworks change constantly; the underlying API patterns are stable

**Interview language:**
> "I chose to use the raw Anthropic API rather than a framework deliberately.
> I wanted to understand every architectural decision before adopting abstractions.
> In production, I'd evaluate frameworks for specific use cases — LangGraph for
> complex DAG-based workflows, for example — but I'd use them knowing what they're
> hiding, not as a black box."

---

## 7. Simulated Data → Real APIs (tools.py architecture)

**What you see in the code:**
Every tool function currently returns hardcoded data for "Acme Manufacturing Co."

**Why this is the right architecture:**
- The agent loop and tool dispatch work identically whether data is simulated or real
- Swapping in a real QuickBooks API call requires changing only the function body
- You can test agent behavior and prompt engineering without API credentials

**The swap pattern:**
```python
# Current (simulated):
def _get_revenue_data(client_name: str, months: int = 12) -> dict:
    return {"monthly_detail": [...hardcoded...]}

# Real version (same signature, different body):
def _get_revenue_data(client_name: str, months: int = 12) -> dict:
    client_id = quickbooks_client_lookup(client_name)
    return quickbooks_api.get_revenue(client_id, months=months)
```

`agent.py` never changes.

---

## 8. Context Window Management

**The constraint:** Claude models have token limits (200K for claude-sonnet-4-6).
Long agent loops with many tool calls accumulate tokens fast.

**Strategies (Phase 2-3 work):**
1. **Summarize and truncate** — replace old messages with a summary
2. **Selective history** — only keep last N tool calls
3. **Structured memory** — extract key facts to a separate store, not the message list

**Interview language:**
> "Context management is the scaling problem of agents. The naive implementation
> sends the full message history every call. For long-running agents, you need a
> strategy: summarize completed tool calls, extract persistent facts to external
> memory, and keep the active context focused on what's relevant to the current task."

---

## 9. max_iterations as a Safety Mechanism

**What you see in the code:**
```python
max_iterations = 10  # Safety limit — prevents infinite loops
```

**Why it matters:**
Without this, a misbehaving agent could loop forever, consuming tokens and money.
Production agents need circuit breakers.

**Other production safety patterns:**
- Token budget limits per session
- Timeout per tool call
- Anomaly detection on tool call patterns (e.g., calling same tool 5x in a row)
- Human-in-the-loop confirmation for high-stakes actions (sending emails, making payments)
