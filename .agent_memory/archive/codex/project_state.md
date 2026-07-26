# Project State & Active Context

Maintain this file with durable facts about the project. Keep it compact. Long narratives do not belong here.

## STABLE FACTS

project_name: "simplemem"
project_focus: "One-command file-system agent memory system for coding agents"
architecture: "Python CLI package using argparse; generates `.codex_memories/` tree with dated folders and markdown templates"
entry_point: "`simplemem` console script → `simplemem.cli:main`"
version: "0.2.0"
pyproject_version: "0.2.0"

## ACTIVE CONTEXT

active_threads:
  pypi-collision: "`simplemem` name on PyPI is taken by an unrelated vector-memory package (v0.1.0). Local install from wheel or editable install required."

## NOTES

- Build system: setuptools>=61.0
- Tests: pytest, 10 tests in `tests/test_cli.py`
- CLI commands: `init`, `validate`
- Memory root: `.codex_memories/`
- Daily folder format: `YYYY-MM-DD/`
