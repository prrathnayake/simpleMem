# Core Agent Memory Engine

This system exists to help you persist intelligence context across sessions without exhausting your context window.

Treat this repository as a directed graph of memory files:

`AGENTS.md` → `_agent_rules.md` → `project_state.md` → `system_prompt.md` → `code_logics.md` → `system_logics.md` → `daily_summary.md` → `YYYY-MM-DD/revival_summary.md` → `YYYY-MM-DD/task_log.md`

## Start of Session Checklist

You MUST complete these steps at the start of every session before accepting user requests:

1. **Mandatory Load:** Read `AGENTS.md`, then this file (`_agent_rules.md`).
2. **State Load:** Read `project_state.md` to understand stable facts and active threads.
3. **Protocol Load:** Read `system_prompt.md`, `code_logics.md`, and `system_logics.md`.
4. **Daily Context:** Read `daily_summary.md` for recent active work.
5. **Daily Hub Creation:** If today's `YYYY-MM-DD/` folder does not exist, create it.
6. **Session Revival:** On the first task of a new day, read yesterday's folder. Write a `revival_summary.md` inside today's folder to bootstrap context.
7. **Detail Budget:** Load artifact files only when daily index files are insufficient. Do NOT read entire history by default.

## Navigation & Work Logic

8. **Architectural Guardrails:** Target project architecture is in `/ARCHITECTURE.md` and UI design is in `/DESIGN.md`. Use these files ONLY for understanding the application you are building. Do NOT use them for memory system mechanics.
9. **Dynamic Discovery:** Whenever you enter a code directory, look for a `folder_map.md`. If missing, generate one so future agents can parse the directory structure without reading every dense codebase file.
10. **Small-File Rule:** Keep root memory files compact. Prefer one concern per file. Create small files under `YYYY-MM-DD/artifacts/` for detailed debugging, verification, migrations, or long requests.

## End of Session Checklist

You MUST complete these steps before ending any session:

11. **Conversation Log:** In today's folder, create or append to `message_pairs.md`. Keep it concise. If the exact user prompt is long, store it in an artifact file and reference it from `message_pairs.md`.
12. **Task Log:** In today's folder, create or append to `task_log.md`. Log only the high-signal summary of what was coded, debugged, and blocked.
13. **Daily Summary Update:** Update `daily_summary.md` with active tasks, blockers, and recent completions. Keep it a rolling index; archive or remove stale items instead of letting it grow.
14. **End of Day Summary:** Maintain an `end_of_day_summary.md` in today's folder. Keep it short and action-oriented so tomorrow's agent can scan it quickly.
15. **State Update:** Update `project_state.md` with any new durable facts discovered during this session.
16. **Split Early:** If any memory file exceeds ~50 lines or starts to sprawl, split it into a new artifact file instead of continuing to append.

## Memory Root

- Write all reusable session memory only under `.codex_memories/`.
- Do not create or use any alternate memory root.
