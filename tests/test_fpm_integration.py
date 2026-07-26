"""Cross-repository FPM installation test for the distributed SimpleMem package."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FPM_CLI = PROJECT_ROOT.parents[1] / "Friday-Package-Manager" / "cli"

pytestmark = pytest.mark.skipif(not FPM_CLI.is_dir(), reason="Friday Package Manager is not beside SimpleMem")


def _fpm(environment: dict[str, str], cwd: Path, *arguments: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "fpm.main", *arguments],
        cwd=cwd,
        env=environment,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def test_fpm_pack_install_skill_and_memory_lifecycle(tmp_path: Path) -> None:
    source = tmp_path / "source"
    shutil.copytree(
        PROJECT_ROOT,
        source,
        ignore=shutil.ignore_patterns(".git", ".agent_memory", ".codex_memories", "dist", "__pycache__", ".pytest_cache"),
    )
    sys.path.insert(0, str(FPM_CLI))
    try:
        from fpm.commands.pack import pack_project

        archive, _ = pack_project(source)
    finally:
        sys.path.remove(str(FPM_CLI))

    consumer = tmp_path / "consumer"
    consumer.mkdir()
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(
        [str(FPM_CLI), environment.get("PYTHONPATH", "")]
    ).rstrip(os.pathsep)

    installed = _fpm(environment, consumer, "install", str(archive))
    assert installed.returncode == 0, installed.stderr
    skills = _fpm(environment, consumer, "skills", "--json")
    assert skills.returncode == 0, skills.stderr
    assert json.loads(skills.stdout)["skills"][0]["name"] == "use-simplemem"

    initialized = _fpm(environment, consumer, "run", "simplemem", "--", "init")
    assert initialized.returncode == 0, initialized.stderr
    started = _fpm(
        environment,
        consumer,
        "run",
        "simplemem",
        "--",
        "start",
        "--task",
        "integration",
        "--input",
        "-",
        input_text='{"intent":"Verify FPM lifecycle"}',
    )
    assert started.returncode == 0, started.stderr
    finished = _fpm(
        environment,
        consumer,
        "run",
        "simplemem",
        "--",
        "finish",
        "--task",
        "integration",
        "--input",
        "-",
        input_text='{"outcome":"Lifecycle passed","verification":["clean FPM install"]}',
    )
    assert finished.returncode == 0, finished.stderr
    validated = _fpm(
        environment, consumer, "run", "simplemem", "--", "validate", "--strict", "--json"
    )
    assert validated.returncode == 0, validated.stderr
    assert json.loads(validated.stdout)["valid"] is True
