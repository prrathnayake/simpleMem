"""Cross-repository FPM installation test for the distributed SimpleMem package."""

from __future__ import annotations

import json
import os
import shutil
import sys
import tarfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _fpm_cli() -> Path:
    configured = os.environ.get("FRIDAY_PACKAGE_MANAGER_ROOT")
    if configured:
        return Path(configured).expanduser().resolve() / "cli"
    for parent in PROJECT_ROOT.parents:
        manifest = parent / "friday-workspace.json"
        if manifest.is_file():
            workspace = json.loads(manifest.read_text(encoding="utf-8"))
            relative = workspace["repositories"]["friday.package-manager"]["path"]
            return (parent / relative / "cli").resolve()
    return PROJECT_ROOT.parents[1] / "Friday-Package-Manager" / "cli"


FPM_CLI = _fpm_cli()

pytestmark = pytest.mark.skipif(not FPM_CLI.is_dir(), reason="Friday Package Manager is not beside SimpleMem")


def test_fpm_pack_produces_portable_release_input(tmp_path: Path) -> None:
    source = tmp_path / "source"
    shutil.copytree(
        PROJECT_ROOT,
        source,
        ignore=shutil.ignore_patterns(".git", ".agent_memory", ".codex_memories", "dist", "__pycache__", ".pytest_cache"),
    )
    sys.path.insert(0, str(FPM_CLI))
    try:
        from fpm.commands.pack import pack_project

        archive, checksum = pack_project(source)
    finally:
        sys.path.remove(str(FPM_CLI))
    assert archive.is_file()
    assert len(checksum) == 64
    with tarfile.open(archive, "r:gz") as package:
        manifest_member = next(member for member in package.getmembers() if member.name.endswith("/fpm.json"))
        manifest_stream = package.extractfile(manifest_member)
        assert manifest_stream is not None
        manifest = json.load(manifest_stream)
    assert manifest["name"] == "simplemem"
    assert manifest["version"] == "0.3.0"
    assert manifest["commands"]["simplemem"]["entry"] == "simplemem.cli:main"
