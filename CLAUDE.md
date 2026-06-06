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
- Define what to build → /spec
- Break work into tasks → /plan
- Implement a task → /build
- Verify coverage → /test
- Review code quality → /review
- Reduce complexity → /code-simplify
- Push to production → /ship
- Bugs, errors, crashes → /investigate (or superpowers:systematic-debugging)
- Data, SQL, BigQuery, analysis → [external]-data-analyst skill
- Writing, copy, email, comms → copywriting skill
- Strategy, decisions → strategy-advisor skill
- Skills-first: ALWAYS invoke a skill before specialized work

## Development Workflow (agent-skills)

7 commands cover everything. Use them in order:

| Command | When | Output |
|---------|------|--------|
| `/spec` | Starting something new | SPEC.md — objective, constraints, boundaries |
| `/plan` | Before coding | tasks/plan.md + tasks/todo.md |
| `/build` | Implementing each task | TDD: red → green → commit |
| `/test` | After build | Test gaps identified + fixed |
| `/review` | Before pushing | 5-axis: correctness, readability, architecture, security, performance |
| `/code-simplify` | After review | Reduce complexity, no behavior change |
| `/ship` | Before merge/push | Parallel: code-reviewer + security-auditor + test-engineer → GO/NO-GO |

**Rules:**
- Read SPEC.md before starting any task (boundaries and constraints)
- Read tasks/todo.md to pick the next task
- `uv run pytest -q` passes before every commit
- `git push origin master` after each task (no worktrees, no branches, master only)
- Update tasks/todo.md when a task completes

**Kept from old workflow:**
- `superpowers:finishing-a-development-branch` for git completion when needed
- `superpowers:systematic-debugging` for deep bug investigations

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
