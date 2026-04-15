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