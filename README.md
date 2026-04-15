# SimpleMem: The File-System Agent Graph

SimpleMem treats repository memories as an executable graph explicitly targeted at **Coding Agents** (like Codex or Antigravity).

Instead of maintaining brittle, massive context logs universally, the agent's memory mechanics traverse explicitly connected nodes down into date-segregated namespaces.

## Installation

```bash
pip install simplemem
```

## Quick Start

```bash
simplemem init
```

That's it. Creates all memory files in `.codex_memories/`.

## The Reading Graph

When an agent connects to the project, it executes the following path:

`AGENTS.md` ➡️ `.codex_memories/_agent_rules.md` ➡️ `.codex_memories/project_state.md` ➡️ `.codex_memories/YYYY-MM-DD/`

## Canonical Protocol

Memory root: `.codex_memories/`

Agent startup order:
1. `AGENTS.md`
2. `.codex_memories/_agent_rules.md`
3. `.codex_memories/project_state.md`
4. `.codex_memories/system_prompt.md`
5. `.codex_memories/daily_summary.md`
6. `.codex_memories/YYYY-MM-DD/revival_summary.md`
7. `.codex_memories/YYYY-MM-DD/task_log.md`

**If any other file disagrees with this section, this section wins.**

## Separation of Concerns
- **`AGENTS.md`**: The absolute entrypoint. Agents read this first to discover the protocol.
- **`ARCHITECTURE.md` & `DESIGN.md`**: These files belong to the **working project**. They do NOT track Agent memory mechanics.
- **`.codex_memories/YYYY-MM-DD/`**: All user-agent conversations, task journals, and end-of-day aggregates are hard-isolated into date folders.

## CLI Commands

```bash
simplemem init          # Initialize memory system (idempotent)
simplemem validate    # Validate memory system integrity
```

## Legacy Scripts

The `scripts/` directory contains legacy PowerShell/bash scripts. The Python package is the recommended approach.

## Development

```bash
pip install -e ".[dev]"
python -m pytest tests/
```