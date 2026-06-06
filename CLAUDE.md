# CLAUDE.md — Daniel Ferraro @ [external]

## Who
Daniel Ferraro, Head of Growth at [external]. Lifecycle marketing, A/B testing, CRM, growth ops.
Full context: read via obsidian MCP — note: "03-AREAS/Me & Context/Daniel Ferraro"

## Session Start — Every Time
1. Read via obsidian MCP: note "00 - Home" — active projects and current status
2. Read via obsidian MCP: note "03-AREAS/Me & Context/Daniel Ferraro" — who Daniel is, tools, wedges
3. If project-specific session: read obsidian note "02-PROJECTS/personal/[name]" or "02-PROJECTS/[external]/[name]"
4. Brief in 3 lines: active / last completed / next
5. Ask: Ready to continue, or changing direction?

If no project context found in Obsidian, run Discuss phase to initialize before planning.

## Skill Routing (invoke BEFORE doing the work, not after)
- Product ideas, is this worth building, brainstorm → /office-hours
- Bugs, errors, broken, 500 → /investigate
- Ship, deploy, push, PR → /ship
- QA, test the site, find bugs → /qa
- Code review, check my diff → /review
- Architecture review → /plan-eng-review
- Data, SQL, BigQuery, analysis → [external]-data-analyst skill
- Writing, copy, email, comms → copywriting skill
- Strategy, decisions → strategy-advisor skill
- Skills-first: ALWAYS invoke a skill before specialized work

## GSD Workflow
Phase 0: Discuss → Phase 1: Plan → Phase 2: Execute → Phase 3: Verify
Quick mode for one-off tasks and bug fixes.
Full phases for multi-week projects with dependencies.
State goes to Obsidian project note — never leave it only in conversation.

## Rules
Coding: C:/Users/ferra/.claude/rules/coding-style.md
Python: C:/Users/ferra/.claude/rules/python-rules.md
Voice/writing: read obsidian note "06-SYSTEM/Rules/voice-guidelines"

## Memory and Knowledge
Obsidian vault is the canonical knowledge store. Use obsidian MCP to read and write it.
Vault structure: PARA (00-INBOX → 06-SYSTEM). Read _CLAUDE.md for full folder map.
For LC-OS terms: obsidian note "04-RESOURCES/lc-os/Glossary"
For people and team: obsidian note "03-AREAS/Me & Context/Team"
For [external] projects: obsidian note "02-PROJECTS/[external]/[name]"
For personal projects: obsidian note "02-PROJECTS/personal/[name]"
For archived projects: obsidian note "05-ARCHIVE/[external]/[name]" or "05-ARCHIVE/personal/[name]"
Fallback (if obsidian MCP unavailable): ~/.claude/projects/C--Users-ferra-OneDrive-Desktop-Projects/memory/MEMORY.md
Never let decisions live only in conversation. Write them back to Obsidian at session end.

## Prompt Template
For non-trivial tasks, use the anatomy template from obsidian note "06-SYSTEM/Templates/Prompt Anatomy".
Key structure: Task + Context Files + Reference + Success Brief + Rules (3) + Plan + Align.
