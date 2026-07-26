# SimpleMem Architecture

SimpleMem is a dependency-free Python CLI distributed as an FPM package.

- `simplemem/cli.py` parses commands and JSON/stdin payloads.
- `simplemem/protocol.py` owns initialization, lifecycle writes, bounded context,
  lexical recall, validation, and safe migration.
- `simplemem/templates/` is the single source for generated Markdown.
- `skills/use-simplemem/` contains the portable prompt skill and F.R.I.D.A.Y
  manifest adapter.
- `fpm.json` publishes the command and skill entrypoints to FPM.

The storage API is human-readable Markdown plus versioned JSON control files.
`tasks.json` maps stable task IDs to immutable task-attempt records.
`index/search.jsonl` is a deterministic, rebuildable content index spanning
live and archived Markdown. Project-local locks and atomic replacement protect
shared state from concurrent agents. Root current context is derived and
bounded; dated task records and checksum-verified archives remain the durable
source of truth.
