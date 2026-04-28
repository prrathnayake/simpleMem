# Repository Guidelines

You are a coding agent assigned to this project. This file is your absolute entrypoint. Read it fully, then follow the reading chain below before doing any substantive work.

## Agent Memory Entrypoint

Before writing, editing, or running any code, you MUST read these files in this exact order:

1. `.codex_memories/_agent_rules.md` — Core memory engine and mandatory checklists
2. `.codex_memories/project_state.md` — Stable facts and active threads
3. `.codex_memories/system_prompt.md` — Your operating protocol
4. `.codex_memories/code_logics.md` — How this codebase works
5. `.codex_memories/system_logics.md` — Work scenario guidance
6. `.codex_memories/daily_summary.md` — Rolling recent index
7. `.codex_memories/YYYY-MM-DD/revival_summary.md` — Today's session bootstrap
8. `.codex_memories/YYYY-MM-DD/task_log.md` — Today's task journal

## Memory Root Rule

Write all reusable session memory ONLY under `.codex_memories/`.
Do NOT create or use any alternate memory root.

## Small-File Protocol

This project uses a small-file memory system for higher-accuracy retrieval.

- Keep root memory files short and index-like.
- Prefer one concern per file.
- Prefer one request artifact per request, investigation, or verification thread.
- If a file starts becoming narrative, split it into smaller sibling files.
- Use `.codex_memories/YYYY-MM-DD/artifacts/` for detail that does not belong in the daily index files.
- Keep `message_pairs.md` concise. If the exact user request is long, store the full request in an artifact file and reference it from the daily message index.
- Keep `daily_summary.md` as a rolling recent index, not a transcript.

## Project Identity

_(As the coding agent, fill this in once you understand the project.)_

## Project Structure & Important Directories

_(As the coding agent, list important directories for this project once you discover them.)_

## Build, Setup, and Run Commands

_(As the coding agent, document commands to build, test, and run this project.)_

## Testing Commands & Conventions

- Preferred test root: `tests/`
- Document the actual test runner and conventions once discovered.

## Comments & Docstrings

- Preserve useful comments/docstrings where they help future readers.
- Do not add noisy comments for obvious code.

## Documentation Sync Expectations

- Update local docs in `docs/` when architecture or workflow changes.
- Keep docs aligned with meaningful code changes.
