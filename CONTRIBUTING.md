# Contributing to SimpleMem

## Development setup

```bash
python3 -m pip install -e '.[dev]'
python3 -m pytest
ruff check simplemem tests
```

## FPM package verification

SimpleMem is distributed through Friday Package Manager. Before release:

1. Keep the version aligned in `fpm.json`, `pyproject.toml`,
   `simplemem/__init__.py`, and `skills/use-simplemem/skill.json`.
2. Pack and install it into a temporary FPM project.
3. Verify `fpm run simplemem -- validate --strict --json` and
   `fpm skills --json`.
4. Run the cross-repository integration test when Friday Package Manager is
   available beside this repository.

## Protocol changes

`simplemem/templates/` is the only source for generated Markdown. Keep the CLI,
README, portable skill, tests, and migration behavior aligned with those
templates. Do not add alternate Bash or PowerShell template implementations.

Use small, focused changes and add regression tests for every lifecycle,
migration, retention, or adapter change. Never place secrets or real user
conversations in fixtures.
