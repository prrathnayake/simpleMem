# Package Fix & Test Report

## Root Cause

`pip install simplemem` from PyPI installs a **different** package (also named `simplemem` v0.1.0) that depends on OpenAI, LanceDB, sentence-transformers, etc. That package does not expose a `simplemem` CLI command, so `simplemem init` fails with "command not found".

The local project in this repo is the **correct** `simplemem` (file-system agent memory system). It was never published to PyPI under this name, or the PyPI name was squatted by another project.

## Fixes Applied

1. **Version sync:** `simplemem/__init__.py` had `__version__ = "0.1.0"`, mismatched with `pyproject.toml` (`0.2.0`). Updated to `0.2.0`.

## Build & Install Verification

Built with `python3 -m build`:
- `dist/simplemem-0.2.0.tar.gz`
- `dist/simplemem-0.2.0-py3-none-any.whl`

Entry point confirmed in wheel:
```
[console_scripts]
simplemem = simplemem.cli:main
```

Installed in clean venv:
```bash
python3 -m venv /tmp/simplemem-test-venv
/tmp/simplemem-test-venv/bin/pip install dist/simplemem-0.2.0-py3-none-any.whl
```

CLI commands verified:
- `simplemem --help` → works
- `simplemem init` → creates `.codex_memories/` tree correctly
- `simplemem validate` → passes when valid

## Test Results

```
pytest tests/ -v
============================= 10 passed in 0.03s ==============================
```

## How to Install This Package (Not the PyPI One)

```bash
# From repo root
python3 -m build
pip install dist/simplemem-0.2.0-py3-none-any.whl

# Or editable
pip install -e .
```

## Recommendation

If you want to publish this package, you will need to either:
1. Claim/`simplemem` on PyPI (if possible), or
2. Rename the package to something available (e.g., `simplemem-agent`, `codex-memories`).
