---
name: clawdna
description: Generate a public, privacy-safe wiki-style profile from full OpenClaw history when the user explicitly asks to run ClawDNA.
---

# ClawDNA

## Goal
Generate a concise, interesting, wiki-style profile from full historical behavior.
Output must be factual, standardized, and privacy-safe.

## When to Use
Trigger this skill **only** on explicit user intent, such as:
- `use ClawDNA`
- `/clawdna`
- `generate with ClawDNA`

Do not auto-trigger from generic bio/profile requests.

## Required Tools
- `jq` (required)
- `rg` or `grep` (recommended)

If `jq` is unavailable, stop and ask the user to install it before continuing.

## Mandatory Data Scope
Default scope (minimal): recent window only.
Full-history mode requires explicit user confirmation in the current request.

Allowed paths only:
1. `~/.openclaw/agents/<runtime-agent-id>/sessions/*.jsonl`
2. `memory/*.md`
3. `MEMORY.md` (only when allowed in the current context)

Scope controls:
- Use current runtime agent id only.
- Do not read other agents' logs unless user explicitly asks and confirms.
- Do not expand to additional directories automatically.
- If required paths are missing, ask before changing scope.

## Non-Negotiable Rules
1. No speculation. If unsupported, omit.
2. Public privacy output only (redacted by default).
3. Show time span only in coverage note (no file-count disclosure).
4. Output language follows the user's current language by default.
5. Keep proper nouns/agent names in original form (no translation of names).
6. `Core Capabilities` and `Representative Work` must be titles only.
7. Avoid rigid wording like “OpenClaw instance” in final prose.
8. Data minimization: extract only fields needed for the profile, keep no raw-log copies, and do not output raw transcript excerpts.

## Context Overflow Strategy
When history is too large:
1. Build metadata index first (do not load all raw text at once).
2. Process by time chunks (week/month).
3. Produce fixed-format chunk summaries.
4. Merge chunk summaries (map-reduce style).
5. Keep cross-window high-frequency patterns when conflicts appear.

## Core Commands
```bash
# message events
jq -c 'select(.type=="message")' ~/.openclaw/agents/<agentId>/sessions/*.jsonl

# assistant text
jq -r 'select(.type=="message" and .message.role=="assistant")
| .message.content[]? | select(.type=="text") | .text' \
~/.openclaw/agents/<agentId>/sessions/*.jsonl

# tool calls (action signals)
jq -r 'select(.type=="message" and .message.role=="assistant")
| .message.content[]? | select(.type=="toolCall")
| "\(.name)\t\(.arguments|tostring)"' \
~/.openclaw/agents/<agentId>/sessions/*.jsonl

# time span
jq -r '.timestamp // empty' ~/.openclaw/agents/<agentId>/sessions/*.jsonl \
| sort | sed -n '1p;$p'
```

## Extraction Method
Step 1: Build full index
- first active timestamp
- latest active timestamp
- interaction surfaces
- recurring action clusters

Step 2: Broad action recognition
- Execution: edit/fix/deploy/restart/cleanup/release
- Collaboration: reply/thread/split/coordinate/follow-up
- Analysis: search/compare/evaluate/summarize/review
- Operations: monitor/alert/healthcheck/recovery/stability
- Creation: write/generate/design/propose/script
- Governance: confirm/risk-gate/privacy-redaction/boundary

Step 3: Stability filtering
- Keep only repeated cross-window patterns.
- Single events cannot become persona traits.

Step 4: Privacy redaction
- Remove secrets, direct identifiers, and sensitive internal references.

Step 5: Section mapping
- Map stable signals to the fixed output template.

## Output
Return one Markdown display profile only.
Do not output audit appendix.

## Fixed Output Template

Use section labels in one language only (the output language).
Do not output bilingual headings.

# {{Name}}

## {{LeadLabel}}
{{1 paragraph: identity + start time + stable traits + value}}

## {{InfoboxLabel}}
- {{NameLabel}}: {{}}
- {{TypeLabel}}: {{execution/creative/analysis/operations/hybrid}}
- {{FirstActivationLabel}}: {{YYYY-MM-DD}}
- {{ActiveTimeSpanLabel}}: {{Start ~ Now}}
- {{TotalTokensLabel}}: {{optional; include only if reliably available}}
- {{PrimaryDomainsLabel}}: {{max 3}}
- {{InteractionStyleLabel}}: {{}}
- {{CollaborationModeLabel}}: {{}}
- {{DefaultPrinciplesLabel}}: {{privacy-first / risk-confirmation / rollback-first}}

## {{OriginEvolutionLabel}}
- {{InitialStageLabel}}: {{}}
- {{EvolutionStageLabel}}: {{}}
- {{CurrentStageLabel}}: {{}}

## {{OperatingMethodLabel}}
- {{}}
- {{}}
- {{}}

## {{PersonalitySnapshotLabel}}
{{2-3 short behavior-based sentences}}

## {{CoreCapabilitiesLabel}}
- {{title only}}
- {{title only}}
- {{title only}}

## {{RepresentativeWorkLabel}}
- {{title only}}
- {{title only}}
- {{title only}}

## {{MilestonesLabel}}
- {{Date}}: {{}}
- {{Date}}: {{}}
- {{Date}}: {{}}

## {{CollaborationGuideLabel}}
- {{BestInputLabel}}: {{goal / constraints / priority / deadline}}
- {{BestRhythmLabel}}: {{}}
- {{PreferredOutputLabel}}: {{}}

## {{BoundariesSafetyLabel}}
- {{}}
- {{}}
- {{}}

## {{PersonaTagsLabel}}
{{tag1}} / {{tag2}} / {{tag3}} / {{tag4}}

## {{EndingLabel}}
Preset persona = initial intent; long-term behavior = real persona; user habits = persona shaper.

## Final Checks
- Full history used (not recent-only)
- No speculative claims
- Core Capabilities and Representative Work are title-only
- Privacy-safe wording
- Coverage includes time span only
