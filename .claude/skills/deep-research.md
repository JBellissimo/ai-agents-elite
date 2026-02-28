---
name: deep-research
description: Produces a structured market intelligence brief on any topic. Use it by typing /deep-research followed by your topic. Example: "/deep-research fractional CFO market" or "/deep-research AI consulting competitive landscape". Returns market size, players, ICP, pricing benchmarks, trends, and strategic opportunities.
---

# Deep Research Skill

## When to Use
Invoke with `/deep-research <topic>` when you need:
- Market sizing and competitive landscape before entering a space
- ICP validation (who actually buys this, at what price)
- Pricing benchmarks to position against
- Trend signals that affect the business
- Strategic opportunities others are missing

Example invocations:
- `/deep-research fractional CFO market`
- `/deep-research AI consulting pricing 2025`
- `/deep-research SustainCFO competitors`
- `/deep-research dental practice M&A fractional CFO need`

## Process

1. Parse the research topic from the user's prompt
2. Use WebSearch to find current data (market reports, competitor sites, pricing pages, job boards, industry press)
3. Cross-reference multiple sources — don't rely on a single article
4. Synthesize into the structured brief below
5. Flag anything that directly changes how Bellissimo AI Labs or SustainCFO should position

## Output Format

```
## Research Brief: [Topic]
Date: [Today]

### Market Size & Growth
- Current market size (cite source)
- Growth rate / trajectory
- Key drivers of growth

### Who's Buying (ICP)
- Company profile (size, stage, sector)
- Who in the company makes the decision
- Trigger events that create demand (growth, audit, raise, CFO departure)
- What they search for / how they find solutions

### Pricing Benchmarks
- Low end: [what the cheapest option charges]
- Mid market: [where the volume is]
- High end: [what premium providers charge and why]
- Pricing model variations (hourly, retainer, project, equity)

### Key Players
| Player | Positioning | Price | Weakness |
|---|---|---|---|
| [Name] | [How they position] | [Price] | [Gap you can exploit] |

### Trends
- [Trend 1: what's changing and what it means]
- [Trend 2]
- [Trend 3]

### Strategic Opportunities
[2-3 specific gaps in the market that Bellissimo AI Labs or SustainCFO could exploit. Be concrete — not "there's an opportunity for AI-enhanced CFO services" but "no fractional CFO firm is offering a $500 diagnostic entry product; they all require a full discovery call first"]

### Implications for SustainCFO / Bellissimo
[Direct translation: what does this research change about pricing, positioning, ICP targeting, or messaging?]

### Sources
[List URLs and publication dates]
```

## Rules
- Always cite sources with dates. Market data from 2022 is not current.
- If you can't find a number, say so — don't estimate without flagging it.
- The "Implications" section is the most important. Don't bury it.
- If the research contradicts something in SALES_PACKAGE.md or PROJECT_THREADS.md, flag the conflict explicitly.
- Keep the brief scannable. Use tables and bullets, not paragraphs.
