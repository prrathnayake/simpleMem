# Repository Guidelines

## Project structure

- `simplemem/` contains the dependency-free Python CLI and protocol engine.
- `simplemem/templates/` is the sole source for generated Markdown.
- `skills/use-simplemem/` contains the portable agent skill.
- `tests/` covers lifecycle, migration, retention, and FPM integration.
- `fpm.json` declares the distributed command and skill.

## Development

Use Python 3.10 or newer. Run `python3 -m pytest` for tests and
`ruff check simplemem tests` for linting. Keep public functions typed, use four
spaces, and prefer small deterministic filesystem operations. Update all version
declarations together.

Do not recreate platform-specific bootstrap scripts or duplicate templates.
Never overwrite project-owned files outside the SimpleMem managed block.

<!-- simplemem:start -->
## SimpleMem Repository Memory

Repository-development memory is stored in `.agent_memory/`. It is separate
from any memory owned by the application being developed.

- At task start, run `fpm run simplemem -- start --task <stable-id>` and read its bounded context.
- Use `fpm run simplemem -- recall <query>` for targeted historical knowledge.
- Record only high-signal decisions, blockers, files, and evidence with
  `fpm run simplemem -- log`.
- Before finishing, run `fpm run simplemem -- finish` and
  `fpm run simplemem -- validate --strict`.
- Never store secrets. Exact user requests are opt-in only.

The complete protocol is in `.agent_memory/protocol.md`.
<!-- simplemem:end -->
