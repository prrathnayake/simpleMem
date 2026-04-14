# Message Pairs

This file is a rolling log of exact user requests plus concise summaries of Codex's final responses.

## Entry Format

```text
## YYYY-MM-DD HH:MM
User:
> Exact user request

Codex final summary:
- concise outcome
- files changed or actions taken
- follow-up or unresolved items
```

## Compaction Rule

Keep this file readable. If it becomes too large, preserve recent entries here and move older bulky context into dated artifacts under `.codex_memories/YYYY-MM-DD/`.
