"""Tests for simplemem package."""

import os
import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp = tempfile.mkdtemp()
    original_cwd = os.getcwd()
    os.chdir(temp)
    yield Path(temp)
    os.chdir(original_cwd)
    shutil.rmtree(temp)


def test_init_creates_memory_root(temp_dir):
    """Test that init creates the memory root directory."""
    from simplemem.cli import init_memory, MEMORY_ROOT
    init_memory(temp_dir / MEMORY_ROOT)
    assert (temp_dir / MEMORY_ROOT).exists()


def test_init_creates_core_files(temp_dir):
    """Test that init creates all core files."""
    from simplemem.cli import init_memory, MEMORY_ROOT
    init_memory(temp_dir / MEMORY_ROOT)

    memory_root = temp_dir / MEMORY_ROOT
    assert (memory_root / "_agent_rules.md").exists()
    assert (memory_root / "system_prompt.md").exists()
    assert (memory_root / "code_logics.md").exists()
    assert (memory_root / "system_logics.md").exists()
    assert (memory_root / "daily_summary.md").exists()
    assert (memory_root / "project_state.md").exists()
    assert (memory_root / "folder_map.md").exists()


def test_init_creates_today_folder(temp_dir):
    """Test that init creates today's date folder."""
    from simplemem.cli import init_memory, MEMORY_ROOT, get_today
    init_memory(temp_dir / MEMORY_ROOT)

    today = get_today()
    memory_root = temp_dir / MEMORY_ROOT
    assert (memory_root / today).exists()
    assert (memory_root / today / "artifacts").exists()


def test_init_is_idempotent(temp_dir):
    """Test that init is idempotent."""
    from simplemem.cli import init_memory, MEMORY_ROOT
    memory_root = temp_dir / MEMORY_ROOT

    init_memory(memory_root)
    init_memory(memory_root)

    assert (memory_root / "_agent_rules.md").exists()


def test_validate_passes_when_valid(temp_dir):
    """Test that validate passes for a valid memory system."""
    from simplemem.cli import init_memory, validate_memory, MEMORY_ROOT
    memory_root = temp_dir / MEMORY_ROOT

    init_memory(memory_root)
    assert validate_memory(memory_root)


def test_validate_fails_when_missing_files(temp_dir):
    """Test that validate fails when files are missing."""
    from simplemem.cli import validate_memory, MEMORY_ROOT
    memory_root = temp_dir / MEMORY_ROOT

    memory_root.mkdir()
    assert not validate_memory(memory_root)

def test_init_creates_project_files(temp_dir):
    """Test that init creates AGENTS.md, ARCHITECTURE.md, and DESIGN.md."""
    from simplemem.cli import init_memory, MEMORY_ROOT
    init_memory(temp_dir / MEMORY_ROOT)

    assert (temp_dir / "AGENTS.md").exists()
    assert (temp_dir / "ARCHITECTURE.md").exists()
    assert (temp_dir / "DESIGN.md").exists()


def test_init_core_files_have_content(temp_dir):
    """Test that core memory files are not empty."""
    from simplemem.cli import init_memory, MEMORY_ROOT
    init_memory(temp_dir / MEMORY_ROOT)

    memory_root = temp_dir / MEMORY_ROOT
    for fname in [
        "_agent_rules.md",
        "system_prompt.md",
        "code_logics.md",
        "system_logics.md",
        "daily_summary.md",
        "project_state.md",
        "folder_map.md",
    ]:
        path = memory_root / fname
        assert path.stat().st_size > 0, f"{fname} should not be empty"


def test_validate_fails_when_empty_core_file(temp_dir):
    """Test that validate fails when a core file is empty."""
    from simplemem.cli import init_memory, validate_memory, MEMORY_ROOT
    memory_root = temp_dir / MEMORY_ROOT
    init_memory(memory_root)

    # Empty out a core file
    (memory_root / "_agent_rules.md").write_text("")
    assert not validate_memory(memory_root)


def test_validate_fails_when_missing_project_files(temp_dir):
    """Test that validate fails when ARCHITECTURE.md or DESIGN.md is missing."""
    from simplemem.cli import init_memory, validate_memory, MEMORY_ROOT
    memory_root = temp_dir / MEMORY_ROOT
    init_memory(memory_root)

    # Remove ARCHITECTURE.md
    (temp_dir / "ARCHITECTURE.md").unlink()
    assert not validate_memory(memory_root)
