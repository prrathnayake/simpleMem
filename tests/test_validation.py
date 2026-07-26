"""Validation failure-path regressions."""

import json
from pathlib import Path

from simplemem.protocol import init_project, memory_root, validate


def test_validate_reports_invalid_config_instead_of_raising(tmp_path: Path) -> None:
    init_project(tmp_path)
    (memory_root(tmp_path) / "config.json").write_text("not json", encoding="utf-8")
    result = validate(tmp_path, strict=True)
    assert result["valid"] is False
    assert any("invalid SimpleMem config" in error for error in result["errors"])


def test_validate_reports_unsupported_schema(tmp_path: Path) -> None:
    init_project(tmp_path)
    config = memory_root(tmp_path) / "config.json"
    payload = json.loads(config.read_text(encoding="utf-8"))
    payload["schema_version"] = 99
    config.write_text(json.dumps(payload), encoding="utf-8")
    result = validate(tmp_path)
    assert result["valid"] is False
    assert any("unsupported SimpleMem schema" in error for error in result["errors"])
