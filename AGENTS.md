# Codex Memory Protocol

This repository is a reusable template for project-scoped Codex working memory.

## Purpose

Codex memory in this repo means file-based agent memory stored in the project, not the application's runtime memory.

The goal is to preserve durable project context between coding tasks without depending on chat history alone.

## Hard Rules

1. Persistent Codex memory lives only in `.codex_memories/`.
2. At task start, read `INSTRUCTIONS.md`, `.codex_memories/system_prompt.md`, `.codex_memories/project_brief.md`, `.codex_memories/active_context.md`, `.codex_memories/daily_summary.md`, and today's dated folder if it exists.
3. On the first task of a new day, also review the previous dated folder and refresh today's `revival_summary.md`.
4. During work, store reusable context, decisions, blockers, and verification notes in today's dated folder.
5. At task end, update today's notes, refresh `.codex_memories/daily_summary.md`, and append the exact user request plus a concise summary of the final answer to `.codex_memories/message_pairs.md`.
6. Timestamp every durable note entry in local project time.
7. Separate notes by concern. Do not collapse stable project facts, active carry-forward context, and task logs into one file.
8. Keep memory files compact, scannable, and git-friendly.
9. Commit memory updates with the task unless the user explicitly asks otherwise.
10. If the task changes architecture, operating workflow, or other documentation-worthy behavior, update Notion in the same workflow when the project uses Notion.

## Optimized Layout

The base protocol uses the original four core files and adds two lightweight layers that reduce reread cost:

- `.codex_memories/project_brief.md`
  Stable project facts that rarely change.
- `.codex_memories/active_context.md`
  Small carry-forward context for the next few tasks.

This split keeps `system_prompt.md` focused on standing behavior and prevents `daily_summary.md` from becoming a second diary.

## Reading Strategy

Read the smallest set that can recover context:

1. `INSTRUCTIONS.md`
2. `.codex_memories/system_prompt.md`
3. `.codex_memories/project_brief.md`
4. `.codex_memories/active_context.md`
5. `.codex_memories/daily_summary.md`
6. Today's dated folder
7. Yesterday's folder only when starting a new day or when the summary is insufficient

## Compression Strategy

- Keep `system_prompt.md` under roughly one screen of high-signal rules.
- Keep `active_context.md` limited to currently live threads, blockers, and next actions.
- Use `daily_summary.md` as an index, not as a transcript.
- Use `message_pairs.md` as a rolling log and archive older entries into dated artifacts when it becomes noisy.
- Promote only durable facts into `project_brief.md`.

## Daily Folder Contract

Each `.codex_memories/YYYY-MM-DD/` folder should usually contain:

- `revival_summary.md`
- `task_log.md`
- optional request-specific artifacts such as research notes, migration plans, or verification logs

Use the templates in `.codex_memories/_templates/` when bootstrapping a new day.
