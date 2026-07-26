# SimpleMem Protocol

SimpleMem is the project-local repository-development memory shared by agents
working in this repository. The canonical root is `.agent_memory/`. It is
separate from application runtime memory.

## Start work

1. Run `simplemem start --task <stable-id>` and provide a concise intent as JSON.
2. Read the returned bounded context and source list before changing the project.
3. Use `simplemem recall <query>` when the current context does not answer a
   historical question. Do not load the entire memory tree by default.

## During work

- Run `simplemem log --task <id> --status <status>` with structured JSON for
  decisions, blockers, files, and evidence.
- Put detailed plans, research, and verification under the task's `artifacts/`
  directory and reference them from the task record.
- Store facts and outcomes, not hidden reasoning or a verbatim conversation.
- Never store credentials, tokens, private keys, or sensitive environment data.

## Finish work

1. Run `simplemem finish --task <id>` with the outcome, verification, and next
   actions.
2. Confirm `simplemem validate --strict` succeeds. Run `simplemem reindex` if
   validation reports a stale search index.
3. Leave unfinished work explicit so another agent can resume it.

## Memory layers

- `project_state.md`: durable project facts and active cross-session threads.
- `codebase.md`: stable architecture, commands, conventions, and entrypoints.
- `current.md`: bounded recent outcomes and blockers.
- `index/`: monthly long-term lookup indexes.
- `index/search.jsonl`: deterministic, rebuildable content index.
- `tasks.json`: authoritative task-attempt and active-task registry.
- `YYYY-MM-DD/tasks/`: one isolated record per task.
- `YYYY-MM-DD/artifacts/`: detailed task evidence.
- `archive/`: lossless, read-only legacy memory with checksum manifests.

Exact requests are not captured unless the project or task explicitly opts in.
