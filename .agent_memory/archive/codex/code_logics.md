# Code Logics

As you explore and modify this codebase, document how it works here. Keep this file updated so future agents can onboard quickly.

## Sections to Maintain

- **Package/Module Layout:** Map the directory structure and what each module does.
- **Entry Points:** List CLI commands, main functions, and startup scripts.
- **Key Algorithms:** Document complex or critical business logic.
- **Data Flow:** Trace how data moves between components.
- **Dependencies:** Note important external libraries and why they are used.
- **Test Conventions:** Document the test framework, fixtures, and coverage expectations.
- **Build Notes:** Document build steps, compilation, or bundling requirements.

## Current Understanding

### Package Layout

```
simplemem/
├── __init__.py          # Package init; __version__ = "0.2.0"
└── cli.py               # All CLI logic: init_memory, validate_memory, main

tests/
└── test_cli.py          # 10 pytest tests covering init, validate, idempotency
```

### Entry Points

- `pyproject.toml` defines `[project.scripts] simplemem = "simplemem.cli:main"`
- `main()` uses `argparse` with subparsers: `init` and `validate`

### CLI Commands

- `simplemem init` — Creates `.codex_memories/` tree:
  - Root files: `AGENTS.md`, `ARCHITECTURE.md`, `DESIGN.md`
  - Core memory files: `_agent_rules.md`, `system_prompt.md`, `code_logics.md`, `system_logics.md`, `daily_summary.md`, `project_state.md`, `folder_map.md`
  - Daily folder: `YYYY-MM-DD/` with `task_log.md`, `message_pairs.md`, `revival_summary.md`, `end_of_day_summary.md`, `artifacts/.gitkeep`
- `simplemem validate` — Checks existence and non-emptiness of all expected files

### Build Notes

```bash
python3 -m build          # produces dist/*.whl and dist/*.tar.gz
pip install dist/*.whl    # installs console script
```

### Test Conventions

- Run: `python3 -m pytest tests/ -v`
- Uses `tempfile.mkdtemp()` fixture with `os.chdir()` to test in isolated dirs
- 10 tests covering creation, idempotency, validation pass/fail
