---
name: context-brief
description: "Preserve critical context across compaction boundaries. Before OpenClaw compresses your conversation, this skill extracts and anchors key decisions, pending tasks, and important facts so nothing survives. Unlike native compaction which may lose nuance, context-brief gives you control over what matters. Completely stateless — reads no files, writes no files. Use when: (1) 'save context', (2) 'what do you remember', (3) long conversations approaching compaction, (4) 'context check', (5) agent starts forgetting earlier decisions, (6) 'hva husker du', (7) user wants to maximize conversation depth. Homepage: https://clawhub.ai/skills/context-brief"
---

# Context Brief

**Install:** `clawhub install context-brief`

**Your context survival kit.** Capture what matters before compaction erases it.

This skill operates entirely within session context. It reads no files and writes no files. All information exists only in the current conversation.

## Language

Detect from the user's message language. Default: English.

## When to Activate

- Conversation exceeds ~50% of model's context window
- Agent responses reference outdated information
- User mentions forgetting or losing context
- Compaction has occurred and important info was lost
- User asks: "context check", "hva husker du", "save context", "context status"
- User explicitly requests: "preserve context", "anchor decisions", "remember this"

## Context Health Check

Run periodically or when user asks. Check via `session_status`:

1. **Context usage %** — Tokens used vs window size
2. **Compaction count** — How many times context has been compacted
3. **Key information inventory** — What critical facts exist in conversation

**Report format** (adapts to user language):

```markdown
## 🧠 Context Health Report

| Metric | Value |
|--------|-------|
| Usage | X% (Xk / Xk tokens) |
| Compactions | X |

### Critical items at risk if compaction fires:
- [item 1]
- [item 2]
```

## Preservation Protocol

### Step 1: Extract Critical Information

Scan conversation and categorize into four buckets:

**🔴 Must survive** — Will cause errors or bad decisions if lost:
- Active task state and pending actions
- User decisions that override earlier instructions
- Authentication status, active connections, in-progress operations
- Corrected mistakes (the CORRECT version, not the original error)

**🟡 Should survive** — Would force re-asking if lost:
- User preferences expressed in this session
- Project context and naming conventions
- Agreed-upon approaches or architectures
- Important links, file paths, or identifiers discussed

**⚪ Nice to survive** — Convenient but recoverable:
- General conversation context
- Exploratory discussion and brainstorming
- Background information the user can re-provide

**⚫ Safe to discard:**
- Duplicate information
- Off-topic discussion
- Outdated guesses that were corrected

### Step 2: Generate Context Anchor

Create a compact anchor (5-10 lines) containing only 🔴 items:

```markdown
## Context Anchor — {date}

### Active State
- Task: [current task description]
- Status: [in progress / blocked / awaiting]

### Decisions Made
- [decision] → [chosen option] (reason: [brief])

### Pending Actions
- [ ] [next action with enough context to execute]

### Corrections
- [original wrong thing] → [correct thing]
```

### Step 3: Deliver the Anchor

The anchor is the LAST thing discussed before compaction is likely to fire. This maximizes the chance it survives into the post-compaction context.

Tell the user (in their language):
```
🔍 Context Anchor created. 8 critical items preserved.
   If compaction fires, these will survive in recent messages.
```

### Step 4: Post-Compaction Recovery

After compaction occurs:
1. Check if the anchor survived in recent messages
2. If yes → silently restore state, continue working
3. If no → tell the user: "Context ble kompakt. Noen detaljer kan mangle — kan du bekrefte [critical item]?"
4. Offer to regenerate the anchor for the new context window

## Guidelines for Agent

1. **Proactive anchoring** — Don't wait for the user to ask. If context is above 50%, offer to create an anchor.
2. **Ruthless prioritization** — A 5-line anchor with only 🔴 items beats a 20-line dump with everything.
3. **Never write files** — This skill operates entirely within session context.
4. **Never read files** — This skill operates entirely within session context.
5. **Timestamp anchors** — ISO 8601 for the anchor creation time.
6. **Correction emphasis** — When the user corrected the agent, the CORRECT version must be in the anchor, never the original error.

## Output

When context preservation is performed (adapts to user language):

```markdown
## 🧠 Context Anchor Created

🔴 Must survive: [N] items
🟡 Should survive: [N] items (not anchored, can re-ask if needed)

Anchored:
- [item 1]
- [item 2]
- [item 3]

Ready for compaction. These items are in recent messages.
```
