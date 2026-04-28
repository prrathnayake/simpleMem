# SimpleMem

A **per-project memory protocol** for coding agents. SimpleMem lets AI agents persist context, log progress, and hand off work across sessions — without exhausting their context windows.

## The Problem

Coding agents lose their memory at the end of every session. When a new agent picks up the same project tomorrow, it has no idea:

- What was built yesterday
- What is currently broken
- Which files were touched
- What design decisions were made

Developers end up repeating explanations, and agents waste tokens re-discovering the codebase.

## The Solution

SimpleMem treats the repository as a **file-system memory graph**. It scaffolds a small, standardized set of Markdown files that agents read at the start of every session and update at the end.

The result: agents bootstrap in seconds instead of minutes, and project context survives across days, weeks, and agent instances.

## How It Works

### 1. Bootstrap the Memory System

```bash
pip install simplemem
simplemem init
```

This creates `.codex_memories/` — the memory root — and a set of starter files.

### 2. Agent Reading Chain (Every Session)

When an agent connects, it reads memory files in this exact order:

```
AGENTS.md
  → .codex_memories/_agent_rules.md      (checklists)
  → .codex_memories/project_state.md      (stable facts)
  → .codex_memories/system_prompt.md      (behavioral rules)
  → .codex_memories/code_logics.md        (how the codebase works)
  → .codex_memories/system_logics.md      (work scenarios)
  → .codex_memories/daily_summary.md      (recent active work)
  → .codex_memories/YYYY-MM-DD/revival_summary.md  (today's plan)
  → .codex_memories/YYYY-MM-DD/task_log.md         (today's journal)
```

This chain gives the agent:
- **Rules** for how to operate in this repo
- **State** about the project (stack, architecture, active threads)
- **History** of what was done recently
- **Plan** for what to do today

### 3. Logging Progress

During a session, the agent writes to dated files under `.codex_memories/YYYY-MM-DD/`:

| File | What Goes Here |
|---|---|
| `task_log.md` | Files touched, blockers, decisions made |
| `message_pairs.md` | Compact index of user requests and outcomes |
| `revival_summary.md` | Today's plan, bootstrapped from yesterday |
| `end_of_day_summary.md` | Completed, in-progress, next steps |
| `artifacts/` | Detailed write-ups: API specs, migration plans, bug analyses |

**Small-file rule:** Root memory files stay short (index-like). Detailed research, debugging, or long requests go into `artifacts/` and are referenced, not inlined.

### 4. State Update (End of Session)

Before disconnecting, the agent:
1. Updates `daily_summary.md` with active tasks and blockers
2. Writes `end_of_day_summary.md` so tomorrow's agent knows where to start
3. Updates `project_state.md` with any new durable facts (schema changes, architecture shifts)

## File Roles

### Project Root Files (for the agent to fill in)

| File | Purpose |
|---|---|
| `AGENTS.md` | Absolute entrypoint. Tells the agent the reading chain. |
| `ARCHITECTURE.md` | Application stack and module interactions. |
| `DESIGN.md` | UI/UX design system and layout rules. |

### Memory Root Files (`.codex_memories/`)

| File | Purpose |
|---|---|
| `_agent_rules.md` | Start/end session checklists, navigation rules |
| `system_prompt.md` | Core behavioral protocol for this repo |
| `code_logics.md` | How the codebase works (modules, entry points, data flow) |
| `system_logics.md` | Which memory files to touch for backend, frontend, bug fixes, etc. |
| `daily_summary.md` | Rolling index of active tasks, blockers, completions |
| `project_state.md` | Durable facts: project name, architecture, active threads |
| `folder_map.md` | Directory structure map for quick navigation |

### Daily Files (`.codex_memories/YYYY-MM-DD/`)

| File | Purpose |
|---|---|
| `task_log.md` | Timestamped task entries |
| `message_pairs.md` | Conversation index (user intent → assistant summary) |
| `revival_summary.md` | Today's plan, bootstrapped from yesterday |
| `end_of_day_summary.md` | Aggregate for tomorrow's revival |
| `artifacts/` | One small file per request/concern when detail is needed |

## Separation of Concerns

- **`AGENTS.md`, `ARCHITECTURE.md`, `DESIGN.md`** belong to the **working project**. They describe what the application is.
- **`.codex_memories/*`** belongs to the **agent memory system**. They describe how the agent should work on the application.

Never mix the two. `ARCHITECTURE.md` should not contain session logs. `_agent_rules.md` should not contain API specs.

## CLI Commands

```bash
simplemem init          # Initialize memory system (idempotent)
simplemem validate      # Validate memory system integrity
```

## Scripts

The `scripts/` directory contains PowerShell and shell helpers that follow the same protocol as the Python package:

```bash
scripts/init-agent-memory.sh       # Bash bootstrap
scripts/validate-memory.ps1        # PowerShell validation
scripts/validate-protocol.ps1      # Protocol consistency check
```

## Small-File Protocol

- Keep root memory files short enough to scan in one read.
- Prefer one concern per file.
- If a file exceeds ~50 lines, split it into an artifact.
- Reference long content; do not inline it.
- Optimize for **future retrieval accuracy**, not human diary completeness.

## Development

```bash
pip install -e ".[dev]"
python -m pytest tests/
```

## Why This Works

1. **Agents are stateless.** SimpleMem gives them state.
2. **Context windows are finite.** Small files fit; large logs don't.
3. **Projects outlive sessions.** Memory files hand off context from one agent to the next.
4. **Retrieval beats recall.** A structured graph of small files is easier to scan than a single massive log.

---

*SimpleMem is not a database. It is a protocol. The files are the API.*
