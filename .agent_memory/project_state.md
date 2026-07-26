# Project State

Keep only durable, project-wide facts and active cross-session threads here.

## Identity

- Name: SimpleMem
- Purpose: Agent-neutral, project-local long-term memory distributed through
  Friday Package Manager.

## Stable Facts

- Version 0.3.0 uses `.agent_memory/` as its canonical root.
- The Python CLI is dependency-free at runtime and accepts structured JSON over
  stdin or files.
- FPM is the supported distribution channel; Python packaging remains a
  development convenience.
- Exact requests are disabled by default. Dated task and evidence files are the
  durable source of truth.
- Schema 2 uses immutable task-attempt IDs, an authoritative task registry,
  atomic shared writes, and deterministic chunk metadata indexes.
- Lossless legacy archives remain searchable by content without duplicating
  their full text in the derived index.

## Active Threads

- The 0.3.0 hardening and live F.R.I.D.A.Y migration are complete pending final
  review of the uncommitted package changes.
