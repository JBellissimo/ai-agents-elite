---
name: session-summary
description: Generates an end-of-session summary with what was covered, key insights, decisions made, action items, open questions, and files modified. Appends to SESSION_LOG.md without overwriting previous entries. Trigger when user says "end of session", "session summary", or "wrap up".
---

# Session Summary Skill

## When to Use
Trigger this skill when the user says any of:
- "end of session"
- "generate session summary"
- "wrap up"
- "what did we cover today?"

## Process
1. Review the current conversation context
2. Identify all topics discussed, decisions made, and files created/modified
3. Generate a summary entry in the format below
4. Read the existing SESSION_LOG.md to determine the next session number
5. Append (do NOT overwrite) the new entry to SESSION_LOG.md
6. Confirm completion and show the action items

## Output Format
```markdown
## Session [N] — [Date]

### What We Covered
[Numbered list of topics, 1-2 sentences each]

### Key Insights
[Bullet points of non-obvious realizations or important distinctions]

### Decisions Made
[What was decided and why]

### Action Items for Next Session
- [ ] [Specific, actionable task]
- [ ] [Specific, actionable task]

### Open Questions
[Questions that remain unanswered]

### Files Created/Modified
[List of files with brief description of changes]
```

## Rules
- Be specific, not generic. "Discussed agent architecture" is bad. "Established that Skills compound the expertise library, which is the actual 'recursion' mechanism — not model self-improvement" is good.
- Action items must be concrete and completable in one sitting
- Always check LEARNING_PATH.md and note which phase items were completed
- If any LEARNING_PATH.md checkboxes should be checked off, update them
