# Implementation Instructions For Codex Memory

Use this file as the operational checklist for every task.

## Start-Of-Task Checklist

1. Read `INSTRUCTIONS.md`.
2. Read `.codex_memories/system_prompt.md`.
3. Read `.codex_memories/project_brief.md`.
4. Read `.codex_memories/active_context.md`.
5. Read `.codex_memories/daily_summary.md`.
6. Read today's `.codex_memories/YYYY-MM-DD/` folder if it exists.
7. If this is the first task of a new day, review the previous day's folder and refresh today's `revival_summary.md`.

## During-Task Rules

1. Write durable notes only into `.codex_memories/`.
2. Keep notes separated by concern:
   - standing rules in `system_prompt.md`
   - stable facts in `project_brief.md`
   - live carry-forward context in `active_context.md`
   - day-level history in dated folders
3. Timestamp entries in local time.
4. Use today's folder for decisions, blockers, verification notes, and request-specific artifacts.
5. Promote only durable, reusable information upward into `project_brief.md` or `active_context.md`.
6. Keep the files concise enough that a future task can recover context quickly.

## End-Of-Task Checklist

1. Update today's `task_log.md`.
2. Refresh today's `revival_summary.md` when the next session would benefit from a sharper resume point.
3. Update `.codex_memories/active_context.md` to reflect the latest live state.
4. Update `.codex_memories/daily_summary.md` with a day-level summary entry.
5. Append the exact user message and a concise summary of Codex's final response to `.codex_memories/message_pairs.md`.
6. If the task changed architecture, workflow, or documentation-worthy behavior, update Notion as part of the same workflow when the project uses Notion.
7. Commit memory files with the task unless told not to.

## Compaction Rules

- `system_prompt.md` should stay short and directive.
- `project_brief.md` should store facts, not narratives.
- `active_context.md` should describe only open threads and near-term follow-up.
- `daily_summary.md` should function as an index, not a full log.
- `message_pairs.md` should remain rolling and concise; move older bulky context into dated artifacts when needed.

## Failure Mode To Avoid

Do not let `.codex_memories/` become one giant diary. If a note does not help future task recovery, keep it out.
