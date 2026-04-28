# Contributing to SimpleMem

## Development Setup

```bash
git clone https://github.com/prrathnayake/simpleMem.git
cd simpleMem
pip install -e ".[dev]"
```

## Running Tests

```bash
python -m pytest tests/
```

## Running Linting

```bash
ruff check simplemem/
```

## Building Package

```bash
pip install build
python -m build
```

## Publishing

1. Update version in `pyproject.toml`
2. Create GitHub release
3. CI will publish to PyPI automatically

## Code Style

- Follow PEP 8
- Use `ruff check simplemem/` before committing
- Add tests for new features

## Documentation

When you change the memory protocol, file list, or reading chain, update these files in the same PR:

1. `README.md` — Human-facing overview and canonical protocol
2. `AGENTS.md` — Agent entrypoint (must stay in sync with README)
3. `simplemem/cli.py` — Python bootstrap templates
4. `scripts/init-agent-memory.sh` — Bash bootstrap templates
5. `scripts/init-agent-memory.ps1` — PowerShell bootstrap templates
6. `scripts/validate-memory.ps1` — Validation script
7. `scripts/validate-protocol.ps1` — Protocol consistency checker

**Rule:** If any two of these files disagree, `README.md` wins.