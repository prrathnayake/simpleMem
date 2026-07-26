"""Behavioral tests for the SimpleMem 0.3 protocol and CLI."""

from __future__ import annotations

import hashlib
import io
import json
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pytest

from simplemem.cli import main
from simplemem.protocol import (
    MANAGED_END,
    MANAGED_START,
    build_context,
    finish_task,
    init_project,
    log_task,
    memory_root,
    migrate,
    recall,
    reindex,
    start_task,
    status,
    today_iso,
    validate,
)


def _complete_parallel_task(arguments: tuple[str, int]) -> str:
    project_path, number = arguments
    project = Path(project_path)
    task_id = f"parallel-{number}"
    started = start_task(project, task_id, {"intent": f"Concurrent work {number}"})
    finish_task(
        project,
        task_id,
        payload={
            "outcome": f"Concurrent outcome {number}",
            "verification": [f"worker {number} passed"],
        },
    )
    return str(started["record_id"])


def _start_shared_task(project_path: str) -> str:
    result = start_task(
        Path(project_path), "shared-task", {"intent": "Shared concurrent work"}
    )
    return str(result["record_id"])


@pytest.fixture
def project(tmp_path: Path) -> Path:
    init_project(tmp_path)
    return tmp_path


def test_init_creates_universal_structure_without_project_docs(tmp_path: Path) -> None:
    result = init_project(tmp_path)
    root = tmp_path / ".agent_memory"
    assert result["root"] == str(root)
    for name in ["config.json", "protocol.md", "project_state.md", "codebase.md", "current.md", "index"]:
        assert (root / name).exists()
    day = root / today_iso()
    assert (day / "tasks").is_dir()
    assert (day / "artifacts").is_dir()
    assert (day / "revival_summary.md").is_file()
    assert not (tmp_path / "ARCHITECTURE.md").exists()
    assert not (tmp_path / "DESIGN.md").exists()


def test_agents_adapter_preserves_guidance_and_is_idempotent(tmp_path: Path) -> None:
    agents = tmp_path / "AGENTS.md"
    agents.write_text("# Existing\n\nKeep this rule.\n", encoding="utf-8")
    init_project(tmp_path)
    init_project(tmp_path)
    content = agents.read_text(encoding="utf-8")
    assert "Keep this rule." in content
    assert content.count(MANAGED_START) == 1
    assert content.count(MANAGED_END) == 1
    assert ".agent_memory" in content
    assert ".codex_memories" not in content


def test_adapter_can_be_disabled_without_deleting_project_guidance(tmp_path: Path) -> None:
    agents = tmp_path / "AGENTS.md"
    agents.write_text("# Existing\n\nKeep this rule.\n", encoding="utf-8")
    init_project(tmp_path)
    init_project(tmp_path, adapter="none")
    content = agents.read_text(encoding="utf-8")
    assert "Keep this rule." in content
    assert MANAGED_START not in content
    config = json.loads((memory_root(tmp_path) / "config.json").read_text(encoding="utf-8"))
    assert config["adapter"] == "none"


def test_force_refreshes_policy_but_preserves_user_memory(project: Path) -> None:
    root = memory_root(project)
    (root / "protocol.md").write_text("stale generated policy", encoding="utf-8")
    (root / "project_state.md").write_text("valuable user fact", encoding="utf-8")
    init_project(project, force=True)
    assert "SimpleMem Protocol" in (root / "protocol.md").read_text(encoding="utf-8")
    assert (root / "project_state.md").read_text(encoding="utf-8") == "valuable user fact"


def test_lifecycle_records_summary_and_retrieves_it(project: Path) -> None:
    start = start_task(project, "session-recovery", {"intent": "Repair stale session recovery"})
    assert start["created"] is True
    log_task(
        project,
        "session-recovery",
        "in-progress",
        {"summary": "Found a stale lock", "files": ["src/session.py"], "evidence": ["test failed"]},
    )
    finish = finish_task(
        project,
        "session-recovery",
        payload={"outcome": "Fixed stale session lock", "verification": ["18 tests passed"]},
    )
    task = project / finish["task_file"]
    assert "Fixed stale session lock" in task.read_text(encoding="utf-8")
    assert "18 tests passed" in (memory_root(project) / "current.md").read_text(encoding="utf-8")
    assert any("stale session lock" in item.excerpt.lower() for item in recall(project, "stale session lock"))


def test_exact_request_capture_is_opt_in(project: Path) -> None:
    secret_prompt = "full exact user request that should not be copied"
    start_task(
        project,
        "default-capture",
        {"intent": "concise intent", "exact_request": secret_prompt},
    )
    all_text = "\n".join(
        path.read_text(encoding="utf-8") for path in memory_root(project).rglob("*.md")
    )
    assert secret_prompt not in all_text

    captured = start_task(
        project,
        "explicit-capture",
        {
            "intent": "capture requested",
            "exact_request": secret_prompt,
            "capture_exact_request": True,
        },
    )
    assert captured["request_artifact"]
    assert secret_prompt in (project / captured["request_artifact"]).read_text(encoding="utf-8")


def test_parallel_tasks_use_isolated_files(project: Path) -> None:
    first = start_task(project, "worker-a", {"intent": "First worker"})
    second = start_task(project, "worker-b", {"intent": "Second worker"})
    assert first["task_file"] != second["task_file"]
    assert (project / first["task_file"]).is_file()
    assert (project / second["task_file"]).is_file()


def test_resumed_task_updates_existing_index_entry(project: Path) -> None:
    start_task(project, "resume-me", {"intent": "Wait for dependency"})
    finish_task(
        project,
        "resume-me",
        status="blocked",
        payload={"outcome": "Waiting", "blockers": ["dependency unavailable"]},
    )
    finish_task(
        project,
        "resume-me",
        status="completed",
        payload={"outcome": "Dependency processed", "verification": ["check passed"]},
    )
    index = (memory_root(project) / "index" / f"{today_iso()[:7]}.md").read_text(encoding="utf-8")
    assert index.count("`resume-me`") == 1
    assert "completed | Dependency processed" in index
    assert "blocked | Waiting" not in index


def test_current_context_is_bounded_to_40_entries(project: Path) -> None:
    for number in range(45):
        task_id = f"task-{number:02d}"
        start_task(project, task_id, {"intent": f"Work item {number}"})
        finish_task(project, task_id, payload={"outcome": f"Outcome {number}"})
    content = (memory_root(project) / "current.md").read_text(encoding="utf-8")
    assert content.count("<!-- simplemem:entry -->") == 40
    assert "Outcome 44" in content
    assert "Outcome 0\n" not in content
    assert status(project)["tasks"] == 45


def test_context_respects_budget(project: Path) -> None:
    content = build_context(project, query="project", budget=800)
    assert len(content) <= 800
    assert "Relevant durable knowledge" in content


def test_validate_reports_missing_core_file(project: Path) -> None:
    (memory_root(project) / "codebase.md").unlink()
    result = validate(project, strict=True)
    assert not result["valid"]
    assert any("codebase.md" in error for error in result["errors"])


def test_cli_accepts_json_from_stdin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["init", "--project", str(tmp_path)]) == 0
    monkeypatch.setattr("sys.stdin", io.StringIO('{"intent":"stdin task"}'))
    assert main(["start", "--project", str(tmp_path), "--task", "stdin-task", "--input", "-"]) == 0
    assert "stdin-task" in capsys.readouterr().out
    assert "stdin task" in next(
        (tmp_path / ".agent_memory").glob("????-??-??/tasks/stdin-task--*.md")
    ).read_text(encoding="utf-8")


def test_cli_default_relative_project_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    assert main(["init"]) == 0
    assert main(["start", "--task", "relative-project"]) == 0
    assert next(
        (tmp_path / ".agent_memory").glob(
            "????-??-??/tasks/relative-project--*.md"
        )
    ).is_file()


def test_invalid_task_id_is_rejected(project: Path) -> None:
    with pytest.raises(ValueError, match="task id"):
        start_task(project, "../escape", {"intent": "bad"})


def test_migration_dry_run_apply_and_finalize_preserve_content(tmp_path: Path) -> None:
    legacy = tmp_path / ".codex_memories"
    dated = legacy / "2026-07-18"
    dated.mkdir(parents=True)
    evidence = dated / "task_log.md"
    evidence.write_text("# Legacy task\n\nVerified important behavior.\n", encoding="utf-8")
    original_hash = hashlib.sha256(evidence.read_bytes()).hexdigest()
    (tmp_path / "CUSTOM.md").write_text("Read .codex_memories before work.\n", encoding="utf-8")

    dry_run = migrate(tmp_path)
    assert dry_run["mode"] == "dry-run"
    assert dry_run["files"] == 1
    assert not (tmp_path / ".agent_memory").exists()

    applied = migrate(tmp_path, apply=True)
    archived = (
        tmp_path
        / ".agent_memory"
        / "archive"
        / "codex"
        / "2026-07-18"
        / "task_log.md"
    )
    assert archived.is_file()
    assert hashlib.sha256(archived.read_bytes()).hexdigest() == original_hash
    assert evidence.is_file()
    assert "CUSTOM.md" in applied["unresolved_references"]
    assert (tmp_path / ".agent_memory" / "index" / "2026-07.md").is_file()

    finalized = migrate(tmp_path, apply=True, finalize=True)
    assert finalized["finalized"] is True
    assert archived.is_file()
    assert not legacy.exists()


def test_migrated_archive_is_searchable_by_content(tmp_path: Path) -> None:
    legacy = tmp_path / ".codex_memories" / "2026-03-07"
    legacy.mkdir(parents=True)
    (legacy / "decision.md").write_text(
        "# Architecture decision\n\nThe heliotrope queue prevents duplicate delivery.\n",
        encoding="utf-8",
    )
    migrate(tmp_path, apply=True)
    results = recall(tmp_path, "heliotrope duplicate delivery")
    assert results
    assert results[0].source_kind == "archive"
    assert results[0].path.endswith("2026-03-07/decision.md")


def test_migration_resume_repairs_a_damaged_archive_copy(tmp_path: Path) -> None:
    legacy = tmp_path / ".codex_memories"
    legacy.mkdir()
    source = legacy / "evidence.md"
    source.write_text("# Evidence\n\nOriginal durable evidence.\n", encoding="utf-8")
    migrate(tmp_path, apply=True)
    archived = (
        tmp_path / ".agent_memory" / "archive" / "codex" / "evidence.md"
    )
    archived.write_text("damaged", encoding="utf-8")
    assert validate(tmp_path)["valid"] is False
    migrate(tmp_path, apply=True)
    assert archived.read_bytes() == source.read_bytes()
    assert validate(tmp_path)["valid"] is True


def test_start_resumes_active_task_and_creates_attempt_after_finish(
    project: Path,
) -> None:
    first = start_task(project, "stable", {"intent": "First attempt"})
    resumed = start_task(project, "stable", {"intent": "Ignored on resume"})
    assert resumed["created"] is False
    assert resumed["record_id"] == first["record_id"]
    finish_task(project, "stable", payload={"outcome": "First done"})
    second = start_task(project, "stable", {"intent": "Second attempt"})
    assert second["created"] is True
    assert second["record_id"] != first["record_id"]


def test_finish_is_idempotent_and_rejects_conflicting_terminal_update(
    project: Path,
) -> None:
    start_task(project, "idempotent", {"intent": "Finish safely"})
    payload = {"outcome": "Done", "verification": ["check passed"]}
    first = finish_task(project, "idempotent", payload=payload)
    repeated = finish_task(project, "idempotent", payload=payload)
    assert first["idempotent"] is False
    assert repeated["idempotent"] is True
    task = project / first["task_file"]
    assert task.read_text(encoding="utf-8").count("## Final Outcome") == 1
    with pytest.raises(ValueError, match="different outcome"):
        finish_task(project, "idempotent", payload={"outcome": "Changed"})


def test_strict_validation_rejects_stale_index(project: Path) -> None:
    state = memory_root(project) / "project_state.md"
    state.write_text(state.read_text(encoding="utf-8") + "\n- New manual fact.\n", encoding="utf-8")
    result = validate(project, strict=True)
    assert result["valid"] is False
    assert any("stale" in error for error in result["errors"])
    reindex(project)
    assert validate(project, strict=True)["valid"] is True


def test_concurrent_processes_do_not_lose_shared_updates(project: Path) -> None:
    with ProcessPoolExecutor(max_workers=4) as executor:
        record_ids = list(
            executor.map(
                _complete_parallel_task,
                [(str(project), number) for number in range(8)],
            )
        )
    assert len(set(record_ids)) == 8
    current = (memory_root(project) / "current.md").read_text(encoding="utf-8")
    for number in range(8):
        assert f"Concurrent outcome {number}" in current
    assert validate(project, strict=True)["valid"] is True


def test_same_task_concurrency_creates_one_active_record(project: Path) -> None:
    with ProcessPoolExecutor(max_workers=4) as executor:
        record_ids = list(executor.map(_start_shared_task, [str(project)] * 6))
    assert len(set(record_ids)) == 1
    registry = json.loads(
        (memory_root(project) / "tasks.json").read_text(encoding="utf-8")
    )
    assert registry["active"]["shared-task"] == record_ids[0]


def test_stale_lock_is_recovered(project: Path) -> None:
    lock = memory_root(project) / ".runtime" / "locks" / "memory.lock"
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_text(
        json.dumps({"pid": 99999999, "time": time.time() - 500}),
        encoding="utf-8",
    )
    result = start_task(project, "stale-lock", {"intent": "Recover lock"})
    assert result["created"] is True
    assert not lock.exists()


def test_schema_one_upgrade_uses_last_recorded_status(project: Path) -> None:
    root = memory_root(project)
    old_task = root / "2026-01-01" / "tasks" / "legacy.md"
    old_task.parent.mkdir(parents=True)
    old_task.write_text(
        "# Task — legacy\n\n"
        "- Date: 2026-01-01\n"
        "- Started: 2026-01-01T10:00:00+10:00\n"
        "- Status: in-progress\n"
        "- Intent: Legacy work\n\n"
        "## Final Outcome\n\n"
        "- Finished: 2026-01-01T11:00:00+10:00\n"
        "- Status: completed\n",
        encoding="utf-8",
    )
    config = root / "config.json"
    config_payload = json.loads(config.read_text(encoding="utf-8"))
    config_payload["schema_version"] = 1
    config.write_text(json.dumps(config_payload), encoding="utf-8")
    init_project(project)
    registry = json.loads((root / "tasks.json").read_text(encoding="utf-8"))
    legacy_records = [
        record
        for record in registry["records"].values()
        if record["task_id"] == "legacy"
    ]
    assert legacy_records[0]["status"] == "completed"
    assert "legacy" not in registry["active"]
