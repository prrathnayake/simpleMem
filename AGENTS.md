# Repository Guidelines

## Agent Memory Entrypoint

Before doing substantive work, always read these in order:

1. `.codex_memories/_agent_rules.md`
2. `.codex_memories/project_state.md`
3. `.codex_memories/system_prompt.md`
4. `.codex_memories/daily_summary.md`
5. `.codex_memories/YYYY-MM-DD/revival_summary.md`
6. `.codex_memories/YYYY-MM-DD/task_log.md`

Write all reusable session memory only under `.codex_memories/`.
Do not create or use any alternate memory root.

## Small-File Protocol

This repo is optimized for higher-accuracy memory retrieval with small files.

- Keep root memory files short and index-like.
- Prefer one concern per file.
- Prefer one request artifact per request, investigation, or verification thread.
- If a file starts becoming narrative, split it into smaller sibling files.
- Use `.codex_memories/YYYY-MM-DD/artifacts/` for detail that does not belong in the daily index files.
- Keep `message_pairs.md` concise. If the exact user request is long, store the full request in an artifact file and reference it from the daily message index.
- Keep `daily_summary.md` as a rolling recent index, not a transcript.

## Project Identity

_(Project name and description - fill in for your project)_

## Project Structure & Important Directories

_(List important directories for your project)_

## Build, Setup, and Run Commands

_(Commands to build, test, and run your project)_

## Testing Commands & Conventions

- Preferred test root: `tests/`

## Comments & Docstrings

- Preserve useful comments/docstrings where they help future readers
- Do not add noisy comments for obvious code

## Documentation Sync Expectations

- Update local docs in `docs/` when architecture or workflow changes
- Keep docs aligned with meaningful code changes
