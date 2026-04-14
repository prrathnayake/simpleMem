# Core Agent Memory Engine

This system exists purely for **the coding agent** to persist its intelligence context securely across sessions without destroying its context window limits.

You are treating this repository as a Graph Data-Structure.
`AGENTS.md` -> `_agent_rules.md` -> `project_state.md` -> `YYYY-MM-DD/`

## Start of Task Checklist
1. **Mandatory Load:** Trace from `AGENTS.md` and read `_agent_rules.md` (this file). 
2. **State Load:** Read `project_state.md` to see stable facts and active threads.
3. **Daily Hub Creation:** If an `.agent_memories/YYYY-MM-DD/` folder for today does not exist, create it.
4. **Session Revival:** On the *first task of a new day*, read yesterday's folder. Write a `revival_summary.md` inside *today's* folder to bootstrap context.

## Navigation & Work Logic
5. **Architectural Guardrails:** Target project architecture is in `/ARCHITECTURE.md` and UI design is in `/DESIGN.md`. Do NOT use these files for your AI engine memory. They are strictly for the application you are building.
6. **Dynamic Discovery:** Whenever you enter a code directory, look for a `folder_map.md`. If missing, generate one so future agents can parse the directory structure without reading every dense codebase file. 

## End of Task Checklist
7. **Conversations:** Inside today's `YYYY-MM-DD/` folder, create or append to `message_pairs.md`. Log the exact user prompt and a tight summary of your final response.
8. **Task Log:** Inside today's `YYYY-MM-DD/` folder, create or append to `task_log.md`. Log what specifically you coded, debugged, and any blockers hit during this run.
9. **Final Summarization:** Maintain an `end_of_day_summary.md` in today's folder. When wrapping up your shift, aggregate your task logs into this file so tomorrow's agent can read it quickly.
10. **State Update:** Update your specific agent thread in `project_state.md`.
