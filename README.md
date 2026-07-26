# SimpleMem

SimpleMem is an agent-neutral, project-local long-term memory protocol delivered
through Friday Package Manager. It keeps current context small while preserving
durable task evidence for future agents.

## Install and initialize

```bash
fpm install simplemem
fpm run simplemem -- init --adapter agents-md
```

Initialization creates `.agent_memory/` and adds a managed pointer to
`AGENTS.md` without replacing existing contributor guidance.

## Lifecycle

```bash
# Start and receive bounded context
printf '%s' '{"intent":"Fix session recovery"}' |
  fpm run simplemem -- start --task session-recovery --input -

# Record progress
printf '%s' '{"summary":"Found stale lock state","files":["src/session.py"]}' |
  fpm run simplemem -- log --task session-recovery --status in-progress --input -

# Finish and update long-term indexes
printf '%s' '{"outcome":"Recovery fixed","verification":["18 tests passed"]}' |
  fpm run simplemem -- finish --task session-recovery --input -
```

Other commands:

- `context [query]`: build a bounded context bundle.
- `recall <query>`: search dated memory and evidence indexes.
- `reindex`: deterministically rebuild the content index after manual edits.
- `status`: report days, tasks, artifacts, and schema version.
- `validate --strict --json`: check protocol integrity.
- `migrate --from .codex_memories`: inspect a legacy migration; add `--apply`
  only after reviewing the report and `--finalize` only after validation.

## Storage model

`.agent_memory/` contains versioned configuration, protocol rules, durable
project and codebase facts, bounded current context, an authoritative task
registry, deterministic content indexes, and isolated daily task/artifact
directories. A checksum-verified archive keeps migrated legacy history
searchable without loading it at task start. Exact requests are disabled by
default. Historical task records are never deleted by compaction.

## Development

```bash
python3 -m pip install -e '.[dev]'
python3 -m pytest
ruff check simplemem tests
```

Python packaging remains a development convenience; FPM is the supported
distribution channel.
