# Repository Guidelines

## Project Identity


## Project Structure & Important Directories


## Build, Setup, and Run Commands


## Testing Commands & Conventions
- Preferred test root: `tests/`.


## Coding Style & Naming Conventions


## Comments & Docstrings
- Preserve useful comments/docstrings when touching orchestration-heavy, gateway-heavy, schema-heavy, or otherwise non-trivial code.
- Add or refresh concise comments where they help future readers understand sequencing, invariants, protocol expectations, or failure handling.
- Do not add noisy comments for obvious code.

## Commit & PR Rules
- Work only on `main` unless the user explicitly asks otherwise.
- The current local checkout may not already be on `main`; verify branch state before branch-sensitive work instead of assuming.
- Never revert unrelated user changes.
- Before any commit, review `.env` and `.gitignore` and do not commit secrets or local-only outputs.
- Keep commits focused and imperative. Prefer short subjects such as `Add swan startup validation`, `Update replay docs`, or `Fix source registry contract`.
- Conventional Commit prefixes are acceptable when they stay imperative and scoped, for example `fix: stabilize replay rendering`.

## Security & Configuration Rules
- Copy `.env.example` for local setup; never commit real secrets.
- Keep connection details and tokens in environment variables, not source, fixtures, or docs examples.
- Database-backed work assumes PostgreSQL/PostGIS; treat migrations and schema docs as coupled changes.
- Review `.env` and `.gitignore` before commits to avoid leaking credentials or accidental local artifacts.

## Memory & Task Protocol
- Persist reusable context only in `.codex_memories/`.
- Always read these files before starting any task:
  - `.codex_memories/_agent_rules.md`
  - `.codex_memories/system_prompt.md`
  - `.codex_memories/daily_summary.md`
  - today's `.codex_memories/YYYY-MM-DD/revival_summary.md`
  - today's `.codex_memories/YYYY-MM-DD/task_log.md`
- Use one folder per day under `.codex_memories/YYYY-MM-DD/`.
- On the first task of a day, review the previous day folder if it exists and write or refresh today's `revival_summary.md` before doing substantive work.
- Keep memory files separated by concern:
  - `system_prompt.md` for the compact operating protocol
  - `daily_summary.md` for the current rolling state
  - `message_pairs.md` for exact user messages plus concise final-response summaries
  - daily `revival_summary.md` for session restart context
  - daily `task_log.md` for timestamped task history
- At the end of every task:
  - append a timestamped entry to today's `task_log.md`
  - refresh today's `revival_summary.md`
  - update `.codex_memories/daily_summary.md`
  - append the full exact user message plus a concise summary of the assistant's final response to `.codex_memories/message_pairs.md`
- Do not collapse all memory into one catch-all file.

## Documentation Sync Expectations
- No external docs hub URL is currently configured for this repo. Treat that as `none` until the user provides one.
- The local `docs/` tree is still part of the required workflow and should stay aligned with meaningful code changes.
- When a task materially changes architecture, prompts, memory flow, tools, gateways, workflows, or user-facing apps, update the relevant local docs in `docs/`.
- If an external docs hub is introduced later and is unavailable during a docs-worthy task, record the follow-up explicitly in `.codex_memories/` before ending the task.
