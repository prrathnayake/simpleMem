---
name: use-simplemem
description: Maintain durable, project-local memory with the SimpleMem CLI. Use when an agent starts or resumes work in a repository containing `.agent_memory`, needs to recall prior decisions or evidence, records progress or blockers, hands work to another agent, or finishes a task that future sessions must understand.
---

# Use SimpleMem

Use the CLI as the reliable lifecycle boundary. Keep detailed evidence in the
task artifact directory; do not turn root memory files into transcripts.

Examples use `fpm run simplemem --`, the supported installed-package path. If
the current harness exposes the registered command directly, use `simplemem`
instead. Do not install an unrelated package from a public registry as a
fallback.

## Start or resume work

1. Choose a stable task ID containing letters, digits, dots, underscores, or
   hyphens.
2. Send a concise intent through stdin:

```bash
printf '%s' '{"intent":"Diagnose the failing session test"}' |
  fpm run simplemem -- start --task session-test --input -
```

3. Read the returned context, source list, and truncation warnings before
   changing the project.
4. If needed, run `fpm run simplemem -- recall "specific topic"` instead of
   loading the full `.agent_memory` tree.

Initialize only when `.agent_memory/config.json` is absent:

```bash
fpm run simplemem -- init --adapter agents-md
```

## Record meaningful progress

Use `log` after a decision, verified finding, blocker, or coherent implementation
checkpoint. Send summaries and lists as JSON through stdin:

```bash
printf '%s' '{"summary":"Isolated the race","evidence":["pytest tests/test_session.py -q"],"files":["src/session.py"]}' |
  fpm run simplemem -- log --task session-test --status in-progress --input -
```

Write long research, plans, and diagnostics under
`.agent_memory/YYYY-MM-DD/artifacts/<task-id>/`, then reference the path in
`evidence`. Never store secrets, environment values, hidden reasoning, or exact
conversations. Capture an exact request only when the user explicitly requires
it.

## Finish or hand off

Send the outcome, verification, blockers, and next actions to `finish`:

```bash
printf '%s' '{"outcome":"Fixed session locking","verification":["23 tests passed"],"next_actions":[]}' |
  fpm run simplemem -- finish --task session-test --input -
fpm run simplemem -- validate --strict --json
```

Use `--status blocked` or `--status in-progress` for a handoff. Make the next
action executable by a fresh agent.

## Recover from failures

- If a command reports an invalid task ID, choose a short filesystem-safe ID.
- If validation fails, repair only the paths it reports; preserve project-owned
  files and historical evidence.
- If validation reports a stale index after a manual memory edit, run
  `fpm run simplemem -- reindex`, then validate again.
- If only `.codex_memories` exists, run `migrate` without `--apply` first, review
  the report, then apply. Do not finalize until validation succeeds.
