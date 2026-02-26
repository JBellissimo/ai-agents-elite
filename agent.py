"""
agent.py — The Bellissimo Reveal Agent
=======================================
This is the core diagnostic agent for Bellissimo AI Labs.

TWO MODES:
    MODE 1 — "reveal"    : Bellissimo AI Labs full business intelligence diagnostic
    MODE 2 — "xray"      : SustainCFO financial deep-dive (CFO-grade output)

WHAT IT IS:
    A tool-using agent that interviews a business (via structured intake) and
    produces a 2-page intelligence report — The Bellissimo Reveal.
    The report routes the prospect to the right product:
    SustainCFO (financial track) or Bellissimo AI Labs (OS/automation track).

WHY RAW ANTHROPIC API (no LangChain/CrewAI):
    Frameworks hide the architecture. To understand agents at an elite level,
    you need to see exactly what's happening:
    - The model decides when/which tools to call (not you)
    - You run a loop until the model stops requesting tools
    - Tool results are fed back as structured messages
    - The model synthesizes everything into a final response

THE AGENT LOOP (memorize this pattern):
    1. Send messages + tool definitions to the API
    2. If response contains tool_use blocks → execute the tools → loop
    3. If response is end_turn with text → done

LAYER IN THE HIERARCHY:
    This is Layer 1 (Augmented LLM) → single agent with tool access
    NOT yet a multi-agent system (that's Phase 4+)
"""

import json
import os
from anthropic import Anthropic
from tools import TOOL_DEFINITIONS, execute_tool
from dotenv import load_dotenv

load_dotenv()

# Initialize the Anthropic client
# WHY: The client handles auth (ANTHROPIC_API_KEY from .env) and HTTP
client = Anthropic()

# The model to use — claude-sonnet-4-6 is the sweet spot: fast + capable
MODEL = "claude-sonnet-4-6"

# System prompts: one per mode
# WHY this matters: The system prompt is your primary way to shape agent behavior.
# Two modes allow one agent.py to serve both Bellissimo AI Labs and SustainCFO.

# MODE 1: Bellissimo Reveal — broad business intelligence diagnostic
REVEAL_SYSTEM_PROMPT = """You are the Bellissimo Reveal Agent for Bellissimo AI Labs.

Your job: Conduct a warm, intelligent diagnostic of a business and produce
a sharp 2-page intelligence report that the owner has never seen before.
This report should feel like it was written by a brilliant advisor who actually
listened — not a generic consultant template.

THE REVEAL FRAMEWORK:
1. Business Model Clarity — how they make money, what's sticky, what's fragile
2. Operational Bottlenecks — where time and money is leaking
3. AI Readiness Score — which workflows are immediately automatable (score 1-10)
4. Digital Presence Gap — what their online footprint says vs. what it should say
5. The Big Opportunity — one insight they probably haven't articulated yet
6. Routing Recommendation — SustainCFO track, Company OS track, or both

TONE:
- Warm but precise. Like a brilliant friend who happens to be an expert.
- No jargon. No filler. Every sentence earns its place.
- Be direct about risks. Be specific about opportunities.

RULES:
- Call ALL relevant tools before writing your final analysis
- Surface at least one insight that will surprise the owner
- End with a clear, specific recommended next step
- Format as a structured report with section headers

Start by calling your tools, then write The Reveal."""

# MODE 2: SustainCFO X-Ray — deep financial diagnostic
XRAY_SYSTEM_PROMPT = """You are a Business X-Ray Agent for SustainCFO, a fractional CFO practice.

Your job: Run a structured diagnostic on a client business and produce a clear,
actionable report that a CFO would be proud to present to a board.

DIAGNOSTIC FRAMEWORK:
1. Revenue Health — growth trend, concentration risk, recurring vs one-time
2. Expense Structure — fixed vs variable, major categories, red flags
3. Cash Flow Position — operating, investing, financing; runway
4. Key Financial Ratios — gross margin, burn rate, months of runway
5. Priority Recommendations — top 3 actions with estimated financial impact

RULES:
- Call ALL relevant tools before writing your final analysis
- Be specific with numbers — no vague observations
- Flag any data gaps explicitly
- Format output as a structured report, not a conversation

Start by introducing what you're about to do, then call your tools, then write the report."""

# Default mode — change to "xray" for SustainCFO financial deep-dives
DEFAULT_MODE = "reveal"


def run_agent(client_name: str, context: str = "", mode: str = DEFAULT_MODE) -> str:
    """
    Run the Bellissimo diagnostic agent for a given client.

    Args:
        client_name: Name of the business to diagnose
        context:     Optional additional context from the user
        mode:        "reveal" (Bellissimo full diagnostic) or "xray" (SustainCFO financial)

    Returns:
        The agent's final analysis as a string

    HOW THE LOOP WORKS:
        messages starts with the user request.
        Each iteration: send to API → check stop reason
        If stop_reason == "tool_use":
            - Extract all tool_use blocks from the response
            - Execute each tool
            - Append assistant message (with tool_use blocks) to messages
            - Append user message (with tool_result blocks) to messages
            - Loop again
        If stop_reason == "end_turn":
            - Extract the text block → return it
    """

    # Select system prompt based on mode
    system_prompt = XRAY_SYSTEM_PROMPT if mode == "xray" else REVEAL_SYSTEM_PROMPT

    # Build the initial user message
    user_message = f"Run a full Business X-Ray diagnostic for: {client_name}"
    if context:
        user_message += f"\n\nAdditional context: {context}"

    # messages is the conversation history we maintain ourselves
    # WHY: The API is stateless — we must send full history every call
    messages = [{"role": "user", "content": user_message}]

    print(f"\n{'='*60}")
    print(f"Business X-Ray Agent - {client_name}")
    print(f"{'='*60}\n")

    # THE AGENT LOOP
    iteration = 0
    max_iterations = 10  # Safety limit — prevents infinite loops

    while iteration < max_iterations:
        iteration += 1
        print(f"[Loop iteration {iteration}] Calling API...")

        # Send messages + tool definitions to the model
        # WHY tools param: tells the model what tools exist and their schemas
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system_prompt,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        print(f"[Loop iteration {iteration}] stop_reason={response.stop_reason}")

        # CASE 1: Model wants to use tools
        if response.stop_reason == "tool_use":
            # Collect all tool calls from this response
            # WHY loop: model can request multiple tools in one turn
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_use_id = block.id

                    print(f"  -> Tool call: {tool_name}({json.dumps(tool_input)})")

                    # Execute the tool (calls functions in tools.py)
                    result = execute_tool(tool_name, tool_input)

                    print(f"  <- Result: {str(result)[:100]}...")  # truncate for readability

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": json.dumps(result),
                    })

            # Append the assistant's response (with tool_use blocks) to history
            messages.append({"role": "assistant", "content": response.content})

            # Append tool results as a user message
            # WHY role=user: the API requires tool results come from the "user" turn
            messages.append({"role": "user", "content": tool_results})

            # Loop again — model will now process tool results

        # CASE 2: Model is done
        elif response.stop_reason == "end_turn":
            # Extract the final text response
            final_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_text += block.text

            print(f"\n[Agent complete after {iteration} iterations]\n")
            return final_text

        else:
            # Unexpected stop reason — surface it clearly
            raise ValueError(f"Unexpected stop_reason: {response.stop_reason}")

    raise RuntimeError(f"Agent exceeded max_iterations ({max_iterations}). Check for loops.")


def main():
    """Entry point — runs a demo diagnostic."""
    result = run_agent(
        client_name="Acme Manufacturing Co.",
        context="Concerned about cash flow. Considering a line of credit."
    )
    print(result)


if __name__ == "__main__":
    main()
