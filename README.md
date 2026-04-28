# SimpleMem: The File-System Agent Graph

SimpleMem treats repository memories as an executable graph explicitly targeted at coding agents.

Instead of maintaining brittle, massive context logs, the memory graph stays intentionally small:

- root files are short indexes
- daily folders isolate current work
- `artifacts/` holds one small file per request or concern when detail is needed
- large prompts or long investigations are referenced, not copied into every summary file

## Installation

```bash
pip install simplemem
```

## Quick Start

```bash
simplemem init
```

That bootstraps a small-file memory system in `.codex_memories/`.

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
5. `.codex_memories/code_logics.md`
6. `.codex_memories/system_logics.md`
7. `.codex_memories/daily_summary.md`
8. `.codex_memories/YYYY-MM-DD/revival_summary.md`
9. `.codex_memories/YYYY-MM-DD/task_log.md`

**If any other file disagrees with this section, this section wins.**

## Small-File Rules

- Keep `project_state.md`, `system_prompt.md`, and `daily_summary.md` brief enough to reread quickly.
- Put detailed research, debugging, and verification into `.codex_memories/YYYY-MM-DD/artifacts/`.
- Keep `message_pairs.md` as a compact index. If a prompt is long, store the full request in an artifact and reference it.
- Split by concern before a file becomes a general-purpose dump.
- Optimize for future retrieval accuracy, not human diary completeness.

## Separation of Concerns
- **`AGENTS.md`**: The absolute entrypoint. Agents read this first to discover the protocol.
- **`ARCHITECTURE.md` & `DESIGN.md`**: These files belong to the **working project**. They do NOT track Agent memory mechanics.
- **`.codex_memories/YYYY-MM-DD/`**: All user-agent conversations, task journals, and end-of-day aggregates are hard-isolated into date folders.

## CLI Commands

```bash
simplemem init          # Initialize memory system (idempotent)
simplemem validate    # Validate memory system integrity
```

## Scripts

The `scripts/` directory contains PowerShell and shell helpers that follow the same protocol as the Python package.

## Development

```bash
pip install -e ".[dev]"
python -m pytest tests/
```
