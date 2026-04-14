# System Prompt Snapshot

This project uses `.codex_memories/` as Codex's durable working memory.

## Standing Rules

- Read the memory protocol at the start of every task.
- Prefer the smallest read set that restores enough context.
- Store durable project memory only inside `.codex_memories/`.
- Keep notes timestamped, compact, and separated by concern.
- Use dated folders for task logs, recovery notes, and request-specific artifacts.
- Update summaries and message pairs at task end.
- Promote stable facts to `project_brief.md`.
- Keep only live carry-forward context in `active_context.md`.
- When architecture or long-lived workflow changes, update external documentation such as Notion when the project uses it.
