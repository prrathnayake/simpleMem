# SimpleMem: The File-System Agent Graph

SimpleMem treats repository memories as an executable graph explicitly targeted at **Coding Agents** (like Codex or Antigravity).

Instead of maintaining brittle, massive context logs universally, the agent's memory mechanics traverse explicitly connected nodes down into date-segregated namespaces.

## The Reading Graph
When an agent connects to the project, it executes the following path:

`AGENTS.md` ➡️ `_agent_rules.md` ➡️ `project_state.md` ➡️ `[Today]/YYYY-MM-DD/`

Every file and folder created by this protocol is constructed solely to empower the agent to pick up where it left off.

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
- **`ARCHITECTURE.md` & `DESIGN.md`**: These files belong to the **working project** (e.g. the video engineering app architecture and UI layout). They do NOT track Agent memory mechanics.
- **`.codex_memories/YYYY-MM-DD/`**: Rather than infinitely appending to a master root file, all user-agent conversations (`message_pairs.md`), task journals (`task_log.md`), and end-of-day aggregates (`end_of_day_summary.md`) are hard-isolated into the folder corresponding to the timestamp of the task.

## Bootstrap It!
```powershell
./scripts/init-agent-memory.ps1
```
