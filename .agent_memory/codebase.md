# Codebase Guide

Record stable information that helps a new agent work accurately.

## Structure

- `simplemem/cli.py`: argparse and JSON/stdin interface.
- `simplemem/protocol.py`: storage, lifecycle, recall, validation, and migration.
- `simplemem/templates/`: sole source for generated Markdown.
- `skills/use-simplemem/`: portable skill plus F.R.I.D.A.Y manifest.
- `tests/`: unit, migration, retention, validation, and FPM integration tests.

## Commands

- Tests: `python3 -m pytest -q`
- Lint: `ruff check simplemem tests`
- Skill validation: `quick_validate.py skills/use-simplemem`
- FPM use: `fpm run simplemem -- <command>`

## Conventions

- Python 3.10+, four-space indentation, typed public functions.
- Keep filesystem operations deterministic and project-root constrained.
- Never duplicate templates in shell or PowerShell scripts.
- Preserve project-owned files outside marked SimpleMem adapter blocks.

## Entry Points and Data Flow

- FPM resolves `simplemem.cli:main`; the CLI delegates all behavior to
  `simplemem.protocol` and renders JSON or Markdown results.
- Task lifecycle: `init` → `start` → `log` → `finish` → `validate`; stable task
  IDs resolve through immutable attempts in `tasks.json`.
- Retrieval: bounded, source-attributed `context` for startup and ranked
  full-content `recall` over live and archived Markdown.
- `reindex` rebuilds chunk metadata and source checksums; shared mutations use
  project-local locks and atomic replacement.
