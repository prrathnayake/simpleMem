"""Filesystem protocol and lifecycle operations for SimpleMem."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from importlib import resources
from pathlib import Path
from typing import Any, Iterable, Iterator

MEMORY_ROOT = ".agent_memory"
SCHEMA_VERSION = 2
DEFAULT_CONTEXT_BUDGET = 12_000
MAX_CURRENT_ENTRIES = 40
CURRENT_DAYS = 14
MANAGED_START = "<!-- simplemem:start -->"
MANAGED_END = "<!-- simplemem:end -->"
ENTRY_START = "<!-- simplemem:entry -->"
ENTRY_END = "<!-- /simplemem:entry -->"
TASK_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
ACTIVE_STATUSES = {"in-progress", "blocked"}
TERMINAL_STATUSES = {"completed", "failed"}
ALL_STATUSES = ACTIVE_STATUSES | TERMINAL_STATUSES
INDEX_FILES = {"search.jsonl", "search-manifest.json"}
LOCK_TIMEOUT_SECONDS = 10.0
STALE_LOCK_SECONDS = 120.0


@dataclass(frozen=True)
class RecallResult:
    path: str
    score: float
    excerpt: str
    heading: str = ""
    source_kind: str = "history"
    date: str | None = None
    task_id: str | None = None
    status: str | None = None


@dataclass(frozen=True)
class ContextBundle:
    context: str
    sources: list[str]
    warnings: list[str]
    budget: int
    used: int


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def today_iso() -> str:
    return date.today().isoformat()


def validate_task_id(task_id: str) -> str:
    if not TASK_ID_PATTERN.fullmatch(task_id) or ".." in task_id:
        raise ValueError(
            "task id must be 1-64 letters, digits, dots, underscores, or hyphens"
        )
    return task_id


def memory_root(project: Path) -> Path:
    return project.resolve() / MEMORY_ROOT


def _template(name: str, **values: str) -> str:
    content = (
        resources.files("simplemem.templates")
        .joinpath(name)
        .read_text(encoding="utf-8")
    )
    return content.format(**values) if values else content


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _write_new(path: Path, content: str) -> bool:
    if path.exists():
        return False
    _atomic_write(path, content)
    return True


def _read_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"invalid {label}: root must be an object")
    return payload


def _process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except (PermissionError, OSError):
        return True
    return True


@contextmanager
def _memory_lock(root: Path, name: str = "memory") -> Iterator[None]:
    lock_dir = root / ".runtime" / "locks"
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_path = lock_dir / f"{name}.lock"
    deadline = time.monotonic() + LOCK_TIMEOUT_SECONDS
    acquired = False
    while not acquired:
        try:
            descriptor = os.open(
                lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600
            )
            payload = json.dumps(
                {"pid": os.getpid(), "created_at": now_iso(), "time": time.time()}
            )
            os.write(descriptor, payload.encode("utf-8"))
            os.close(descriptor)
            acquired = True
        except FileExistsError:
            stale = False
            try:
                lock_payload = _read_json(lock_path, label="SimpleMem lock")
                lock_age = time.time() - float(lock_payload.get("time", 0))
                stale = lock_age > STALE_LOCK_SECONDS and not _process_alive(
                    int(lock_payload.get("pid", -1))
                )
            except (OSError, TypeError, ValueError):
                try:
                    stale = (
                        time.time() - lock_path.stat().st_mtime
                    ) > STALE_LOCK_SECONDS
                except OSError:
                    stale = False
            if stale:
                try:
                    lock_path.unlink()
                except FileNotFoundError:
                    pass
                continue
            if time.monotonic() >= deadline:
                raise ValueError(f"timed out waiting for SimpleMem lock: {name}")
            time.sleep(0.025)
    try:
        yield
    finally:
        if acquired:
            lock_path.unlink(missing_ok=True)


def _default_config(adapter: str = "agents-md") -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "memory_root": MEMORY_ROOT,
        "adapter": adapter,
        "retention": {
            "capture_exact_requests": False,
            "current_max_entries": MAX_CURRENT_ENTRIES,
            "current_days": CURRENT_DAYS,
        },
        "search": {"index_version": 1},
    }


def _config(root: Path) -> dict[str, Any]:
    path = root / "config.json"
    if not path.exists():
        raise ValueError(f"SimpleMem is not initialized at {root.parent}")
    payload = _read_json(path, label="SimpleMem config")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"unsupported SimpleMem schema: {payload.get('schema_version')}")
    return payload


def _managed_block() -> str:
    return f"""{MANAGED_START}
## SimpleMem Repository Memory

Repository-development memory is stored in `.agent_memory/`. It is separate
from any memory owned by the application being developed.

- At task start, run `simplemem start --task <stable-id>` and read its bounded context.
- Use `simplemem recall <query>` for targeted historical knowledge.
- Record only high-signal decisions, blockers, files, and evidence with `simplemem log`.
- Before finishing, run `simplemem finish` and `simplemem validate --strict`.
- Never store secrets. Exact user requests are opt-in only.

The complete protocol is in `.agent_memory/protocol.md`.
{MANAGED_END}"""


def install_agents_adapter(project: Path) -> str:
    path = project / "AGENTS.md"
    block = _managed_block()
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        pattern = re.compile(
            re.escape(MANAGED_START) + r".*?" + re.escape(MANAGED_END), re.DOTALL
        )
        updated = (
            pattern.sub(block, existing)
            if pattern.search(existing)
            else existing.rstrip() + "\n\n" + block + "\n"
        )
    else:
        updated = "# Repository Guidelines\n\n" + block + "\n"
    _atomic_write(path, updated)
    return str(path)


def remove_agents_adapter(project: Path) -> bool:
    path = project / "AGENTS.md"
    if not path.exists():
        return False
    existing = path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"\n*" + re.escape(MANAGED_START) + r".*?" + re.escape(MANAGED_END) + r"\n*",
        re.DOTALL,
    )
    updated, count = pattern.subn("\n", existing)
    if count:
        _atomic_write(path, updated.rstrip() + "\n")
    return bool(count)


def _ensure_runtime_ignore(project: Path) -> None:
    path = project / ".gitignore"
    marker = "# SimpleMem transient state"
    lines = [marker, ".agent_memory/.runtime/", ".agent_memory/**/*.tmp"]
    block = "\n".join(lines)
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        if marker in existing:
            return
        content = existing.rstrip() + "\n\n" + block + "\n"
    else:
        content = block + "\n"
    _atomic_write(path, content)


def _date_dirs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(
        path
        for path in root.iterdir()
        if path.is_dir() and re.fullmatch(r"\d{4}-\d{2}-\d{2}", path.name)
    )


def _record_id() -> str:
    stamp = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%f")
    return f"{stamp}-{uuid.uuid4().hex[:8]}"


def _empty_registry() -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "records": {}, "active": {}}


def _registry(root: Path) -> dict[str, Any]:
    path = root / "tasks.json"
    if not path.exists():
        return _empty_registry()
    payload = _read_json(path, label="SimpleMem task registry")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("task registry schema does not match SimpleMem schema")
    if not isinstance(payload.get("records"), dict) or not isinstance(
        payload.get("active"), dict
    ):
        raise ValueError("invalid SimpleMem task registry structure")
    return payload


def _write_registry(root: Path, registry: dict[str, Any]) -> None:
    _atomic_write(
        root / "tasks.json",
        json.dumps(registry, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
    )


def _parse_task_metadata(path: Path) -> dict[str, str]:
    content = path.read_text(encoding="utf-8")
    values: dict[str, str] = {}
    for key in ("Record ID", "Task ID", "Date", "Started", "Status", "Intent"):
        matches = re.findall(
            rf"^- {re.escape(key)}: (.+)$", content, re.MULTILINE
        )
        if matches:
            values[key.lower().replace(" ", "_")] = matches[-1].strip()
    if "task_id" not in values:
        heading = re.search(r"^# Task — (.+)$", content, re.MULTILINE)
        if heading:
            values["task_id"] = heading.group(1).strip()
    return values


def _rebuild_task_registry(root: Path) -> dict[str, Any]:
    registry = _empty_registry()
    for path in sorted(root.glob("????-??-??/tasks/*.md")):
        metadata = _parse_task_metadata(path)
        task_id = metadata.get("task_id")
        if not task_id:
            continue
        record_id = metadata.get("record_id") or hashlib.sha256(
            str(path.relative_to(root)).encode("utf-8")
        ).hexdigest()[:24]
        status = metadata.get("status", "in-progress")
        record = {
            "record_id": record_id,
            "task_id": task_id,
            "status": status,
            "path": str(path.relative_to(root)),
            "started_at": metadata.get("started", ""),
            "updated_at": metadata.get("started", ""),
            "finish_fingerprint": None,
        }
        registry["records"][record_id] = record
        if status in ACTIVE_STATUSES:
            existing = registry["active"].get(task_id)
            if existing:
                prior = registry["records"][existing]
                if prior.get("started_at", "") > record.get("started_at", ""):
                    continue
            registry["active"][task_id] = record_id
    _write_registry(root, registry)
    return registry


def _upgrade_schema_one(root: Path, existing: dict[str, Any]) -> dict[str, Any]:
    upgraded = {
        **_default_config(str(existing.get("adapter", "agents-md"))),
        **existing,
        "schema_version": SCHEMA_VERSION,
        "memory_root": MEMORY_ROOT,
    }
    upgraded["retention"] = {
        **_default_config()["retention"],
        **dict(existing.get("retention", {})),
    }
    upgraded["search"] = {"index_version": 1}
    _atomic_write(
        root / "config.json",
        json.dumps(upgraded, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
    )
    _rebuild_task_registry(root)
    return upgraded


def init_project(
    project: Path, *, force: bool = False, adapter: str = "agents-md"
) -> dict[str, Any]:
    if adapter not in {"agents-md", "none"}:
        raise ValueError(f"unsupported adapter: {adapter}")
    project = project.resolve()
    project.mkdir(parents=True, exist_ok=True)
    root = memory_root(project)
    root.mkdir(parents=True, exist_ok=True)
    (root / "index").mkdir(exist_ok=True)
    created: list[str] = []
    with _memory_lock(root):
        config_path = root / "config.json"
        existing: dict[str, Any] | None = None
        if config_path.exists():
            existing = _read_json(config_path, label="SimpleMem config")
            if existing.get("schema_version") == 1:
                existing = _upgrade_schema_one(root, existing)
            elif existing.get("schema_version") != SCHEMA_VERSION:
                raise ValueError(
                    f"unsupported SimpleMem schema: {existing.get('schema_version')}"
                )
        config = {
            **_default_config(adapter),
            **(existing or {}),
            "schema_version": SCHEMA_VERSION,
            "memory_root": MEMORY_ROOT,
            "adapter": adapter,
        }
        config["retention"] = {
            **_default_config()["retention"],
            **dict(config.get("retention", {})),
        }
        config["search"] = {"index_version": 1}
        if force or existing != config:
            _atomic_write(
                config_path,
                json.dumps(config, indent=2, ensure_ascii=False, sort_keys=True)
                + "\n",
            )
            created.append(str(config_path.relative_to(project)))
        if not (root / "tasks.json").exists():
            _write_registry(root, _empty_registry())
            created.append(str((root / "tasks.json").relative_to(project)))
        core_templates = {
            "protocol.md": "protocol.md",
            "project_state.md": "project_state.md",
            "codebase.md": "codebase.md",
            "current.md": "current.md",
        }
        for filename, template_name in core_templates.items():
            path = root / filename
            if filename == "protocol.md" and force:
                _atomic_write(path, _template(template_name))
                created.append(str(path.relative_to(project)))
            elif _write_new(path, _template(template_name)):
                created.append(str(path.relative_to(project)))
        _ensure_day_unlocked(project)
        _reindex_unlocked(project)
    _ensure_runtime_ignore(project)
    if adapter == "agents-md":
        install_agents_adapter(project)
    else:
        remove_agents_adapter(project)
    return {
        "project": str(project),
        "root": str(root),
        "created": created,
        "adapter": adapter,
        "schema_version": SCHEMA_VERSION,
    }


def _ensure_day_unlocked(project: Path, day: str | None = None) -> Path:
    root = memory_root(project)
    _config(root)
    day = day or today_iso()
    day_root = root / day
    (day_root / "tasks").mkdir(parents=True, exist_ok=True)
    (day_root / "artifacts").mkdir(parents=True, exist_ok=True)
    previous = [path for path in _date_dirs(root) if path.name < day]
    previous_summary = "No previous SimpleMem day was found."
    if previous:
        prior_file = previous[-1] / "end_of_day_summary.md"
        if prior_file.exists():
            previous_summary = prior_file.read_text(encoding="utf-8").strip()
    _write_new(
        day_root / "revival_summary.md",
        _template("revival_summary.md", date=day, previous_day=previous_summary),
    )
    _write_new(
        day_root / "end_of_day_summary.md",
        _template("end_of_day_summary.md", date=day),
    )
    return day_root


def ensure_day(project: Path, day: str | None = None) -> Path:
    project = project.resolve()
    root = memory_root(project)
    with _memory_lock(root):
        result = _ensure_day_unlocked(project, day)
        _reindex_unlocked(project)
        return result


def _payload_list(payload: dict[str, Any], key: str) -> list[str]:
    value = payload.get(key, [])
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    raise ValueError(f"{key} must be a string or list")


def _bullets(values: Iterable[str], empty: str = "None recorded.") -> str:
    items = [str(value).strip() for value in values if str(value).strip()]
    return "\n".join(f"- {item}" for item in items) if items else empty


def _active_record(
    project: Path, registry: dict[str, Any], task_id: str
) -> tuple[dict[str, Any], Path]:
    record_id = registry["active"].get(task_id)
    if not record_id:
        raise ValueError(f"active task not found: {task_id}")
    record = registry["records"].get(record_id)
    if not isinstance(record, dict):
        raise ValueError(f"task registry is missing active record: {record_id}")
    task_path = memory_root(project) / str(record.get("path", ""))
    if not task_path.is_file():
        raise ValueError(f"task record file is missing: {task_path}")
    return record, task_path


def _latest_record(registry: dict[str, Any], task_id: str) -> dict[str, Any] | None:
    matches = [
        record
        for record in registry["records"].values()
        if isinstance(record, dict) and record.get("task_id") == task_id
    ]
    return max(matches, key=lambda item: str(item.get("started_at", "")), default=None)


def start_task(
    project: Path,
    task_id: str,
    payload: dict[str, Any] | None = None,
    *,
    query: str | None = None,
    budget: int = DEFAULT_CONTEXT_BUDGET,
) -> dict[str, Any]:
    project = project.resolve()
    task_id = validate_task_id(task_id)
    payload = payload or {}
    root = memory_root(project)
    config = _config(root)
    with _memory_lock(root):
        day_root = _ensure_day_unlocked(project)
        registry = _registry(root)
        active_id = registry["active"].get(task_id)
        request_artifact = None
        if active_id:
            record = registry["records"][active_id]
            task_path = root / record["path"]
            created = False
        else:
            record_id = _record_id()
            intent = str(payload.get("intent") or "Not supplied").strip()
            task_path = day_root / "tasks" / f"{task_id}--{record_id}.md"
            created = _write_new(
                task_path,
                _template(
                    "task.md",
                    task_id=task_id,
                    record_id=record_id,
                    date=day_root.name,
                    timestamp=now_iso(),
                    intent=intent,
                ),
            )
            record = {
                "record_id": record_id,
                "task_id": task_id,
                "status": "in-progress",
                "path": str(task_path.relative_to(root)),
                "started_at": now_iso(),
                "updated_at": now_iso(),
                "finish_fingerprint": None,
            }
            registry["records"][record_id] = record
            registry["active"][task_id] = record_id
            _write_registry(root, registry)
        capture = bool(payload.get("capture_exact_request")) or bool(
            config.get("retention", {}).get("capture_exact_requests")
        )
        request = payload.get("exact_request")
        if capture and isinstance(request, str) and request.strip():
            artifact_dir = task_path.parents[1] / "artifacts" / task_id
            artifact_dir.mkdir(parents=True, exist_ok=True)
            artifact = artifact_dir / f"{record['record_id']}-request.md"
            _write_new(artifact, "# Exact Request\n\n" + request.strip() + "\n")
            request_artifact = str(artifact.relative_to(project))
        _reindex_unlocked(project)
        bundle = _build_context_bundle_unlocked(
            project,
            query=query or str(payload.get("intent") or task_id),
            budget=budget,
            current_task=task_path,
        )
    return {
        "task": task_id,
        "record_id": record["record_id"],
        "task_file": str(task_path.relative_to(project)),
        "created": created,
        "request_artifact": request_artifact,
        "context": bundle.context,
        "sources": bundle.sources,
        "warnings": bundle.warnings,
        "budget": bundle.budget,
        "used": bundle.used,
    }


def _append_task_entry(task_path: Path, entry: str) -> None:
    current = task_path.read_text(encoding="utf-8")
    _atomic_write(task_path, current.rstrip() + "\n" + entry.rstrip() + "\n")


def _set_task_status(task_path: Path, status: str) -> None:
    content = task_path.read_text(encoding="utf-8")
    updated, count = re.subn(
        r"^- Status: .+$",
        f"- Status: {status}",
        content,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise ValueError(f"task record has no status field: {task_path}")
    _atomic_write(task_path, updated)


def log_task(
    project: Path, task_id: str, status: str, payload: dict[str, Any] | None = None
) -> dict[str, Any]:
    project = project.resolve()
    if status not in ALL_STATUSES:
        raise ValueError(f"unsupported task status: {status}")
    payload = payload or {}
    root = memory_root(project)
    with _memory_lock(root):
        registry = _registry(root)
        record, task_path = _active_record(project, registry, validate_task_id(task_id))
        summary = str(payload.get("summary") or "Progress recorded.").strip()
        entry = f"""
### {now_iso()} — {status}

{summary}

**Decisions**

{_bullets(_payload_list(payload, 'decisions'))}

**Files**

{_bullets(_payload_list(payload, 'files'))}

**Evidence**

{_bullets(_payload_list(payload, 'evidence'))}

**Blockers**

{_bullets(_payload_list(payload, 'blockers'))}
"""
        _append_task_entry(task_path, entry)
        _set_task_status(task_path, status)
        record["status"] = status
        record["updated_at"] = now_iso()
        if status in TERMINAL_STATUSES:
            registry["active"].pop(task_id, None)
        _write_registry(root, registry)
        _reindex_unlocked(project)
    return {
        "task": task_id,
        "record_id": record["record_id"],
        "status": status,
        "task_file": str(task_path.relative_to(project)),
    }


def _parse_current_entries(content: str) -> list[str]:
    pattern = re.compile(
        re.escape(ENTRY_START) + r".*?" + re.escape(ENTRY_END), re.DOTALL
    )
    return [match.group(0).strip() for match in pattern.finditer(content)]


def _entry_date(entry: str) -> date | None:
    match = re.search(r"Date: (\d{4}-\d{2}-\d{2})", entry)
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1))
    except ValueError:
        return None


def _update_current_unlocked(project: Path, entry: str) -> None:
    root = memory_root(project)
    path = root / "current.md"
    entries = _parse_current_entries(path.read_text(encoding="utf-8"))
    record_match = re.search(r"Record ID: ([^\n]+)", entry)
    if record_match:
        marker = f"Record ID: {record_match.group(1)}"
        entries = [existing for existing in entries if marker not in existing]
    entries.append(entry)
    config = _config(root)
    retention = config.get("retention", {})
    current_days = int(retention.get("current_days", CURRENT_DAYS))
    max_entries = int(retention.get("current_max_entries", MAX_CURRENT_ENTRIES))
    cutoff = date.today() - timedelta(days=current_days)
    recent = [item for item in entries if (_entry_date(item) or date.today()) >= cutoff]
    recent = recent[-max_entries:]
    header = _template("current.md").rstrip()
    _atomic_write(path, header + "\n\n" + "\n\n".join(recent) + "\n")


def _upsert_index_line(path: Path, key: str, line: str, heading: str) -> None:
    lines = (
        path.read_text(encoding="utf-8").rstrip().splitlines()
        if path.exists()
        else [heading.rstrip(), ""]
    )
    replaced = False
    for index, existing in enumerate(lines):
        if existing.startswith("- ") and key in existing:
            lines[index] = line.rstrip()
            replaced = True
            break
    if not replaced:
        lines.append(line.rstrip())
    _atomic_write(path, "\n".join(lines).rstrip() + "\n")


def _finish_fingerprint(status: str, payload: dict[str, Any]) -> str:
    canonical = json.dumps(
        {"status": status, "payload": payload},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def finish_task(
    project: Path,
    task_id: str,
    status: str = "completed",
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    project = project.resolve()
    if status not in ALL_STATUSES:
        raise ValueError(f"unsupported task status: {status}")
    task_id = validate_task_id(task_id)
    payload = payload or {}
    fingerprint = _finish_fingerprint(status, payload)
    root = memory_root(project)
    with _memory_lock(root):
        registry = _registry(root)
        active_id = registry["active"].get(task_id)
        if active_id:
            record, task_path = _active_record(project, registry, task_id)
        else:
            record = _latest_record(registry, task_id)
            if not record:
                raise ValueError(f"task not found: {task_id}")
            task_path = root / record["path"]
            if record.get("finish_fingerprint") == fingerprint:
                return {
                    "task": task_id,
                    "record_id": record["record_id"],
                    "status": record["status"],
                    "task_file": str(task_path.relative_to(project)),
                    "index": str(
                        (root / "index" / f"{task_path.parents[1].name[:7]}.md").relative_to(
                            project
                        )
                    ),
                    "idempotent": True,
                }
            if record.get("status") in TERMINAL_STATUSES:
                raise ValueError(
                    f"task already finished with different outcome: {task_id}"
                )
        outcome = str(payload.get("outcome") or "No outcome supplied.").strip()
        verification = _payload_list(payload, "verification")
        next_actions = _payload_list(payload, "next_actions")
        blockers = _payload_list(payload, "blockers")
        finished = now_iso()
        _append_task_entry(
            task_path,
            f"""
## Final Outcome

- Finished: {finished}
- Status: {status}

{outcome}

### Verification

{_bullets(verification)}

### Remaining Blockers

{_bullets(blockers)}

### Next Actions

{_bullets(next_actions)}
""",
        )
        _set_task_status(task_path, status)
        record["status"] = status
        record["updated_at"] = finished
        record["finish_fingerprint"] = fingerprint
        if status in TERMINAL_STATUSES:
            registry["active"].pop(task_id, None)
        else:
            registry["active"][task_id] = record["record_id"]
        _write_registry(root, registry)
        day = task_path.parents[1].name
        current_entry = f"""{ENTRY_START}
## {finished} — {task_id} [{status}]

- Date: {day}
- Task: {task_id}
- Record ID: {record['record_id']}
- Outcome: {outcome}
- Verification: {'; '.join(verification) if verification else 'None recorded.'}
- Blockers: {'; '.join(blockers) if blockers else 'None.'}
- Next: {'; '.join(next_actions) if next_actions else 'None.'}
- Record: `{task_path.relative_to(project)}`
{ENTRY_END}"""
        _update_current_unlocked(project, current_entry)
        month_index = root / "index" / f"{day[:7]}.md"
        index_line = (
            f"- {day} | `{task_id}` | `{record['record_id']}` | {status} | "
            f"{outcome} | `{task_path.relative_to(project)}`"
        )
        _upsert_index_line(
            month_index,
            f"`{record['record_id']}`",
            index_line,
            f"# SimpleMem Index — {day[:7]}",
        )
        end_day = task_path.parents[1] / "end_of_day_summary.md"
        _upsert_index_line(
            end_day,
            f"`{record['record_id']}`",
            index_line,
            _template("end_of_day_summary.md", date=day),
        )
        _reindex_unlocked(project)
    return {
        "task": task_id,
        "record_id": record["record_id"],
        "status": status,
        "task_file": str(task_path.relative_to(project)),
        "index": str(month_index.relative_to(project)),
        "idempotent": False,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in root.rglob("*.md"):
        relative = path.relative_to(root)
        if relative.parts[0] in {"index", ".runtime"}:
            continue
        paths.append(path)
    return sorted(
        paths,
        key=lambda item: (
            str(item.relative_to(root)).startswith("archive/"),
            str(item.relative_to(root)),
        ),
    )


def _source_kind(relative: str) -> str:
    if relative == "project_state.md" or relative == "codebase.md":
        return "durable"
    if relative == "current.md":
        return "current"
    if relative == "protocol.md":
        return "protocol"
    if relative.startswith("archive/"):
        return "archive"
    if "/tasks/" in relative:
        return "task"
    if "revival_summary.md" in relative or "end_of_day_summary.md" in relative:
        return "daily"
    return "history"


def _split_markdown(content: str) -> list[tuple[str, str]]:
    chunks: list[tuple[str, str]] = []
    heading = "Document"
    buffer: list[str] = []
    for line in content.splitlines():
        if line.startswith("#"):
            if buffer and "\n".join(buffer).strip():
                chunks.append((heading, "\n".join(buffer).strip()))
            heading = line.lstrip("#").strip() or "Document"
            buffer = [line]
        else:
            buffer.append(line)
    if buffer and "\n".join(buffer).strip():
        chunks.append((heading, "\n".join(buffer).strip()))
    if not chunks and content.strip():
        chunks.append(("Document", content.strip()))
    return chunks


def _extract_date(relative: str, content: str) -> str | None:
    match = re.search(r"\d{4}-\d{2}-\d{2}", relative)
    if match:
        return match.group(0)
    match = re.search(r"^- Date: (\d{4}-\d{2}-\d{2})$", content, re.MULTILINE)
    return match.group(1) if match else None


def _extract_field(content: str, field: str) -> str | None:
    match = re.search(rf"^- {re.escape(field)}: (.+)$", content, re.MULTILINE)
    return match.group(1).strip() if match else None


def _index_entries(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    entries: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    seen_chunks: dict[str, int] = {}
    for path in _source_paths(root):
        relative = str(path.relative_to(root))
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        file_hash = _sha256(path)
        sources.append(
            {"path": relative, "size": path.stat().st_size, "sha256": file_hash}
        )
        task_id = _extract_field(content, "Task ID") or _extract_field(content, "Task")
        status = _extract_field(content, "Status")
        source_date = _extract_date(relative, content)
        for position, (heading, text) in enumerate(_split_markdown(content)):
            normalized = " ".join(text.split())
            chunk_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
            if chunk_hash in seen_chunks:
                entries[seen_chunks[chunk_hash]]["aliases"].append(relative)
                continue
            entry = {
                "id": hashlib.sha256(
                    f"{relative}\0{position}\0{chunk_hash}".encode("utf-8")
                ).hexdigest()[:24],
                "path": relative,
                "aliases": [],
                "heading": heading,
                "source_kind": _source_kind(relative),
                "date": source_date,
                "task_id": task_id,
                "status": status,
                "sha256": chunk_hash,
            }
            seen_chunks[chunk_hash] = len(entries)
            entries.append(entry)
    return entries, sources


def _reindex_unlocked(project: Path) -> dict[str, Any]:
    root = memory_root(project)
    entries, sources = _index_entries(root)
    index_path = root / "index" / "search.jsonl"
    manifest_path = root / "index" / "search-manifest.json"
    rendered = "".join(
        json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n"
        for entry in entries
    )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "index_version": 1,
        "entries": len(entries),
        "sources": sources,
    }
    _atomic_write(index_path, rendered)
    _atomic_write(
        manifest_path,
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
    )
    return {
        "index": str(index_path.relative_to(project)),
        "manifest": str(manifest_path.relative_to(project)),
        "entries": len(entries),
        "sources": len(sources),
    }


def reindex(project: Path) -> dict[str, Any]:
    project = project.resolve()
    root = memory_root(project)
    _config(root)
    with _memory_lock(root):
        return _reindex_unlocked(project)


def _current_source_manifest(root: Path) -> list[dict[str, Any]]:
    return [
        {"path": str(path.relative_to(root)), "size": path.stat().st_size, "sha256": _sha256(path)}
        for path in _source_paths(root)
    ]


def _index_is_fresh(root: Path) -> bool:
    manifest_path = root / "index" / "search-manifest.json"
    index_path = root / "index" / "search.jsonl"
    if not manifest_path.is_file() or not index_path.is_file():
        return False
    try:
        manifest = _read_json(manifest_path, label="SimpleMem search manifest")
    except ValueError:
        return False
    return manifest.get("sources") == _current_source_manifest(root)


def _load_index(root: Path) -> list[dict[str, Any]]:
    path = root / "index" / "search.jsonl"
    entries: list[dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                item = json.loads(line)
                if isinstance(item, dict):
                    entries.append(item)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid SimpleMem search index: {exc}") from exc
    return entries


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9_-]{2,}", text.lower())


def _score_entry(
    entry: dict[str, Any], query: str, terms: list[str], text: str
) -> float:
    path = str(entry.get("path", "")).lower()
    heading = str(entry.get("heading", "")).lower()
    text = text.lower()
    phrase = " ".join(query.lower().split())
    score = 0.0
    matched = False
    if phrase and phrase in heading:
        score += 16
        matched = True
    elif phrase and phrase in text:
        score += 10
        matched = True
    for term in set(terms):
        if term in path:
            score += 7
            matched = True
        if term in heading:
            score += 5
            matched = True
        term_count = text.count(term)
        if term_count:
            score += min(term_count, 6) * 1.5
            matched = True
    if not matched:
        return 0.0
    kind = entry.get("source_kind")
    score += {"durable": 4, "current": 4, "task": 2, "daily": 1}.get(kind, 0)
    if entry.get("status") in ACTIVE_STATUSES:
        score += 3
    source_date = entry.get("date")
    if isinstance(source_date, str):
        try:
            age = max(0, (date.today() - date.fromisoformat(source_date)).days)
            score += max(0.0, 3.0 - age / 30.0)
        except ValueError:
            pass
    return score


def _indexed_text(
    root: Path,
    entry: dict[str, Any],
    cache: dict[str, dict[str, str]],
) -> str:
    relative = str(entry.get("path", ""))
    if relative not in cache:
        path = root / relative
        chunks: dict[str, str] = {}
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            cache[relative] = chunks
            return ""
        for _, text in _split_markdown(content):
            normalized = " ".join(text.split())
            chunk_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
            chunks[chunk_hash] = normalized
        cache[relative] = chunks
    return cache[relative].get(str(entry.get("sha256", "")), "")


def _recall_unlocked(
    project: Path, query: str, *, limit: int = 8
) -> list[RecallResult]:
    root = memory_root(project)
    terms = _tokenize(query)
    if not terms:
        return []
    if not _index_is_fresh(root):
        _reindex_unlocked(project)
    results: list[RecallResult] = []
    text_cache: dict[str, dict[str, str]] = {}
    for entry in _load_index(root):
        text = _indexed_text(root, entry, text_cache)
        score = _score_entry(entry, query, terms, text)
        if score <= 0:
            continue
        lower = text.lower()
        positions = [lower.find(term) for term in terms if lower.find(term) >= 0]
        start = max(0, min(positions) - 160) if positions else 0
        excerpt = text[start : start + 700].strip()
        results.append(
            RecallResult(
                path=str(entry.get("path", "")),
                score=round(score, 3),
                excerpt=excerpt,
                heading=str(entry.get("heading", "")),
                source_kind=str(entry.get("source_kind", "history")),
                date=entry.get("date"),
                task_id=entry.get("task_id"),
                status=entry.get("status"),
            )
        )
    return sorted(
        results,
        key=lambda item: (-item.score, item.path, item.heading),
    )[: max(0, limit)]


def recall(project: Path, query: str, *, limit: int = 8) -> list[RecallResult]:
    project = project.resolve()
    root = memory_root(project)
    _config(root)
    with _memory_lock(root):
        return _recall_unlocked(project, query, limit=limit)


def _append_context_section(
    sections: list[str],
    sources: list[str],
    warnings: list[str],
    *,
    title: str,
    source: str,
    content: str,
    budget: int,
    cap: int,
) -> int:
    used = sum(len(section) for section in sections)
    remaining = budget - used
    if remaining <= 0:
        warnings.append(f"omitted {source}: context budget exhausted")
        return 0
    rendered = f"## {title}\n\n{content.strip()}\n"
    allowed = min(remaining, cap)
    if len(rendered) > allowed:
        if allowed < 80:
            warnings.append(f"omitted {source}: insufficient context budget")
            return 0
        rendered = rendered[: allowed - 24].rstrip() + "\n\n[truncated]\n"
        warnings.append(f"truncated {source} to fit context budget")
    sections.append(rendered)
    if source not in sources:
        sources.append(source)
    return len(rendered)


def _build_context_bundle_unlocked(
    project: Path,
    query: str | None = None,
    *,
    budget: int = DEFAULT_CONTEXT_BUDGET,
    current_task: Path | None = None,
) -> ContextBundle:
    if budget < 500:
        raise ValueError("context budget must be at least 500 characters")
    root = memory_root(project)
    _config(root)
    day_root = _ensure_day_unlocked(project)
    if not _index_is_fresh(root):
        _reindex_unlocked(project)
    sections: list[str] = []
    sources: list[str] = []
    warnings: list[str] = []
    if current_task and current_task.is_file():
        relative = str(current_task.relative_to(project))
        _append_context_section(
            sections,
            sources,
            warnings,
            title=f"Active task — {current_task.stem}",
            source=relative,
            content=current_task.read_text(encoding="utf-8"),
            budget=budget,
            cap=max(500, budget * 30 // 100),
        )
    # Fetch a wider ranked pool before source-kind grouping so a large archive
    # cannot crowd durable/current records out of the bounded startup bundle.
    matches = _recall_unlocked(project, query or "active project", limit=64)
    durable = [item for item in matches if item.source_kind == "durable"]
    current_matches = [
        item for item in matches if item.source_kind in {"current", "task"}
    ]
    history = [
        item
        for item in matches
        if item.source_kind not in {"durable", "current", "task", "protocol"}
    ]
    used_match_keys: set[tuple[str, str]] = set()
    for label, group, cap_share in (
        ("Relevant durable knowledge", durable, 25),
        ("Current blockers and outcomes", current_matches, 25),
        ("Relevant history", history, 30),
    ):
        if not group:
            continue
        lines: list[str] = []
        group_sources: list[str] = []
        for item in group:
            key = (item.path, item.heading)
            if key in used_match_keys:
                continue
            used_match_keys.add(key)
            lines.append(
                f"- `{item.path}` — {item.heading} (score {item.score}): {item.excerpt}"
            )
            group_sources.append(item.path)
            if len(lines) >= 6:
                break
        if lines:
            before = len(sections)
            _append_context_section(
                sections,
                sources,
                warnings,
                title=label,
                source=group_sources[0],
                content="\n".join(lines),
                budget=budget,
                cap=max(400, budget * cap_share // 100),
            )
            if len(sections) > before:
                for source in group_sources:
                    if source not in sources:
                        sources.append(source)
    revival = day_root / "revival_summary.md"
    if revival.is_file():
        _append_context_section(
            sections,
            sources,
            warnings,
            title="Daily handoff",
            source=str(revival.relative_to(project)),
            content=revival.read_text(encoding="utf-8"),
            budget=budget,
            cap=max(300, budget * 10 // 100),
        )
    _append_context_section(
        sections,
        sources,
        warnings,
        title="Memory protocol",
        source=".agent_memory/protocol.md",
        content=(
            "Protocol: `.agent_memory/protocol.md`. Use `simplemem recall <query>` "
            "for targeted history. Record high-signal "
            "progress with `simplemem log`; finish with `simplemem finish` and "
            "`simplemem validate --strict`. Exact requests are opt-in."
        ),
        budget=budget,
        cap=500,
    )
    context = "\n".join(sections).strip()
    return ContextBundle(
        context=context,
        sources=sources,
        warnings=warnings,
        budget=budget,
        used=len(context),
    )


def build_context_bundle(
    project: Path, query: str | None = None, *, budget: int = DEFAULT_CONTEXT_BUDGET
) -> ContextBundle:
    project = project.resolve()
    root = memory_root(project)
    _config(root)
    with _memory_lock(root):
        return _build_context_bundle_unlocked(project, query=query, budget=budget)


def build_context(
    project: Path, query: str | None = None, *, budget: int = DEFAULT_CONTEXT_BUDGET
) -> str:
    return build_context_bundle(project, query=query, budget=budget).context


def status(project: Path) -> dict[str, Any]:
    project = project.resolve()
    root = memory_root(project)
    config = _config(root)
    registry = _registry(root)
    task_files = list(root.glob("????-??-??/tasks/*.md"))
    artifact_files = [
        path
        for path in root.glob("????-??-??/artifacts/**/*")
        if path.is_file()
    ]
    archive_files = [
        path for path in (root / "archive").rglob("*") if path.is_file()
    ] if (root / "archive").exists() else []
    return {
        "project": str(project),
        "root": str(root),
        "schema_version": config["schema_version"],
        "days": len(_date_dirs(root)),
        "tasks": len(task_files),
        "active_tasks": len(registry["active"]),
        "artifacts": len(artifact_files),
        "archive_files": len(archive_files),
        "index_fresh": _index_is_fresh(root),
        "legacy_source_present": (project / ".codex_memories").exists(),
    }


def _validate_archive(root: Path, errors: list[str]) -> None:
    archive_root = root / "archive" / "codex"
    manifest_path = root / "archive" / "codex-manifest.json"
    if not archive_root.exists() and not manifest_path.exists():
        return
    if not archive_root.is_dir() or not manifest_path.is_file():
        errors.append("archive root and manifest must both exist")
        return
    try:
        manifest = _read_json(manifest_path, label="SimpleMem archive manifest")
    except ValueError as exc:
        errors.append(str(exc))
        return
    files = manifest.get("files")
    if not isinstance(files, list):
        errors.append("archive manifest files must be a list")
        return
    for item in files:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            errors.append("archive manifest contains an invalid file entry")
            continue
        path = archive_root / item["path"]
        if not path.is_file():
            errors.append(f"archived file is missing: {item['path']}")
            continue
        if path.stat().st_size != item.get("size") or _sha256(path) != item.get(
            "sha256"
        ):
            errors.append(f"archived file checksum mismatch: {item['path']}")


def validate(project: Path, *, strict: bool = False) -> dict[str, Any]:
    project = project.resolve()
    root = memory_root(project)
    errors: list[str] = []
    warnings: list[str] = []
    config: dict[str, Any] | None = None
    required = [
        "config.json",
        "protocol.md",
        "project_state.md",
        "codebase.md",
        "current.md",
        "tasks.json",
        "index",
    ]
    if not root.exists():
        errors.append(f"memory root missing: {root}")
    else:
        for name in required:
            path = root / name
            if not path.exists():
                errors.append(f"required path missing: {name}")
            elif path.is_file() and path.stat().st_size == 0:
                errors.append(f"required file is empty: {name}")
        try:
            config = _config(root)
            if config.get("memory_root") != MEMORY_ROOT:
                errors.append("config memory_root is not .agent_memory")
        except ValueError as exc:
            errors.append(str(exc))
        try:
            registry = _registry(root)
            active_record_ids = list(registry["active"].values())
            if len(active_record_ids) != len(set(active_record_ids)):
                errors.append("task registry maps multiple active tasks to one record")
            active_task_ids: set[str] = set()
            for task_id, record_id in registry["active"].items():
                if task_id in active_task_ids:
                    errors.append(f"duplicate active task id: {task_id}")
                active_task_ids.add(task_id)
                record = registry["records"].get(record_id)
                if not isinstance(record, dict):
                    errors.append(f"active task record missing: {record_id}")
                    continue
                if record.get("status") not in ACTIVE_STATUSES:
                    errors.append(f"active task has terminal/invalid status: {task_id}")
            for record_id, record in registry["records"].items():
                if not isinstance(record, dict):
                    errors.append(f"invalid task registry record: {record_id}")
                    continue
                if record.get("status") not in ALL_STATUSES:
                    errors.append(f"invalid task status in registry: {record_id}")
                path = root / str(record.get("path", ""))
                if not path.is_file():
                    errors.append(f"task record file missing: {record_id}")
        except ValueError as exc:
            errors.append(str(exc))
        if not _index_is_fresh(root):
            warnings.append("search index is missing or stale; run `simplemem reindex`")
        _validate_archive(root, errors)
    agents = project / "AGENTS.md"
    if config is not None and config.get("adapter") == "agents-md":
        if not agents.exists():
            errors.append("AGENTS.md adapter is configured but AGENTS.md is missing")
        else:
            content = agents.read_text(encoding="utf-8")
            if content.count(MANAGED_START) != 1 or content.count(MANAGED_END) != 1:
                errors.append("AGENTS.md must contain exactly one SimpleMem managed block")
    if (project / ".codex_memories").exists():
        warnings.append("legacy .codex_memories source is still present")
    if strict and warnings:
        errors.extend(f"strict: {warning}" for warning in warnings)
    return {"valid": not errors, "errors": errors, "warnings": warnings}


def _legacy_references(project: Path, source: Path, target: Path) -> list[str]:
    references: list[str] = []
    ignored_roots = {
        ".git",
        ".agent_memory",
        ".0",
        ".venv",
        "venv",
        "node_modules",
        "dist",
        "build",
        "logs",
    }
    for path in project.rglob("*"):
        if (
            not path.is_file()
            or source in path.parents
            or target in path.parents
            or any(part in ignored_roots for part in path.relative_to(project).parts)
        ):
            continue
        if path.suffix.lower() not in {
            ".md",
            ".txt",
            ".json",
            ".toml",
            ".yaml",
            ".yml",
            ".py",
            ".sh",
            ".ps1",
        }:
            continue
        try:
            if ".codex_memories" in path.read_text(encoding="utf-8"):
                references.append(str(path.relative_to(project)))
        except (OSError, UnicodeDecodeError):
            continue
    return sorted(references)


def _archive_manifest(source: Path) -> list[dict[str, Any]]:
    return [
        {
            "path": str(path.relative_to(source)),
            "size": path.stat().st_size,
            "sha256": _sha256(path),
        }
        for path in sorted(item for item in source.rglob("*") if item.is_file())
    ]


def _copy_atomic(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        shutil.copy2(source, temporary)
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def migrate(
    project: Path,
    source_name: str = ".codex_memories",
    *,
    apply: bool = False,
    finalize: bool = False,
) -> dict[str, Any]:
    project = project.resolve()
    source = (project / source_name).resolve()
    if project not in source.parents:
        raise ValueError("migration source must be inside the project")
    target = memory_root(project)
    archive_root = target / "archive" / "codex"
    manifest_path = target / "archive" / "codex-manifest.json"
    if not source.exists() or not source.is_dir():
        if finalize and archive_root.is_dir() and manifest_path.is_file():
            return {
                "mode": "apply",
                "source": str(source),
                "target": str(target),
                "files": len(_read_json(manifest_path, label="archive manifest").get("files", [])),
                "bytes": sum(
                    int(item.get("size", 0))
                    for item in _read_json(manifest_path, label="archive manifest").get("files", [])
                    if isinstance(item, dict)
                ),
                "unresolved_references": _legacy_references(project, source, target),
                "finalized": True,
                "archive": str(archive_root.relative_to(project)),
            }
        raise ValueError(f"migration source not found: {source}")
    manifest_files = _archive_manifest(source)
    report: dict[str, Any] = {
        "mode": "apply" if apply else "dry-run",
        "source": str(source),
        "target": str(target),
        "files": len(manifest_files),
        "bytes": sum(item["size"] for item in manifest_files),
        "unresolved_references": _legacy_references(project, source, target),
        "finalized": False,
    }
    if not apply:
        return report
    if not target.exists():
        init_project(project, adapter="agents-md")
    else:
        config_path = target / "config.json"
        if config_path.exists():
            existing = _read_json(config_path, label="SimpleMem config")
            if existing.get("schema_version") == 1:
                init_project(project, adapter=str(existing.get("adapter", "agents-md")))
        _config(target)
    with _memory_lock(target):
        for item in manifest_files:
            source_path = source / item["path"]
            destination = archive_root / item["path"]
            if (
                destination.is_file()
                and destination.stat().st_size == item["size"]
                and _sha256(destination) == item["sha256"]
            ):
                continue
            _copy_atomic(source_path, destination)
            if _sha256(destination) != item["sha256"]:
                raise ValueError(f"archive copy verification failed: {item['path']}")
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "source": source_name,
            "files": manifest_files,
        }
        _atomic_write(
            manifest_path,
            json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True)
            + "\n",
        )
        for item in manifest_files:
            date_match = re.search(r"\d{4}-\d{2}-\d{2}", item["path"])
            if not date_match:
                continue
            source_date = date_match.group(0)
            month_index = target / "index" / f"{source_date[:7]}.md"
            archive_path = f"archive/codex/{item['path']}"
            line = (
                f"- {source_date} | archived | `{item['path']}` | "
                f"`.agent_memory/{archive_path}`"
            )
            _upsert_index_line(
                month_index,
                f"`{item['path']}`",
                line,
                f"# SimpleMem Index — {source_date[:7]}",
            )
        _reindex_unlocked(project)
        if finalize:
            archive_errors: list[str] = []
            _validate_archive(target, archive_errors)
            if archive_errors:
                raise ValueError(
                    "cannot finalize damaged archive: " + "; ".join(archive_errors)
                )
            live_references = [
                item
                for item in _legacy_references(project, source, target)
                if Path(item).name in {"AGENTS.md", "imp_instructions.md"}
            ]
            if live_references:
                raise ValueError(
                    "cannot finalize while active instructions reference .codex_memories: "
                    + ", ".join(live_references)
                )
            shutil.rmtree(source)
            report["finalized"] = True
            report["archive"] = str(archive_root.relative_to(project))
    return report
