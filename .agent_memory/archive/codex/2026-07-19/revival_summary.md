# Revival Summary — 2026-07-19

- SimpleMem 0.2.0 is an argparse-based Python CLI with `init` and `validate`.
- The current canonical root is `.codex_memories/`; templates are duplicated
  across Python, Bash, and PowerShell implementations.
- Existing worktree changes update package memory and align `__version__` with
  `pyproject.toml`; preserve them during the redesign.
- Active blocker from prior work: the PyPI `simplemem` name belongs to another
  package. The 0.3 redesign will use Friday Package Manager only.

## Today's Goal

Implement the approved agent-neutral `.agent_memory` protocol, hybrid lifecycle
CLI, safe migration, portable skill, and required FPM execution/discovery support.

