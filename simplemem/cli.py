#!/usr/bin/env python
"""SimpleMem CLI - One-command agent memory system initialization."""

import argparse
import sys
from datetime import date
from pathlib import Path

MEMORY_ROOT = ".codex_memories"


def get_today() -> str:
    return date.today().isoformat()


def log(msg: str, level: str = "INFO") -> None:
    timestamp = __import__("datetime").datetime.now().strftime("%H:%M:%S")
    prefix = f"[{timestamp}] {level}"
    print(f"{prefix}: {msg}")


def ensure_dir(path: Path) -> bool:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        log(f"Created directory: {path}")
        return True
    return False


def ensure_file(path: Path, content: str = "") -> bool:
    ensure_dir(path.parent)
    if path.exists():
        log(f"Skipping existing file: {path}")
        return False
    path.write_text(content)
    log(f"Created file: {path}")
    return True


def init_memory(root: Path, force: bool = False, full: bool = True) -> None:
    today = get_today()
    log("Starting SimpleMem bootstrap...")
    log(f"Memory root: {MEMORY_ROOT}")
    log(f"Today: {today}")

    ensure_dir(root)

    files_created = []

    root_files = {
        "AGENTS.md": """# Repository Guidelines

## Agent Memory Entrypoint

Before doing substantive work, always read these in order:

1. `.codex_memories/_agent_rules.md`
2. `.codex_memories/project_state.md`
3. `.codex_memories/system_prompt.md`
4. `.codex_memories/daily_summary.md`
5. `.codex_memories/YYYY-MM-DD/revival_summary.md`
6. `.codex_memories/YYYY-MM-DD/task_log.md`

Write all reusable session memory only under `.codex_memories/`.
Do not create or use any alternate memory root.

## Small-File Protocol

This repo is optimized for higher-accuracy memory retrieval with small files.

- Keep root memory files short and index-like.
- Prefer one concern per file.
- Prefer one request artifact per request, investigation, or verification thread.
- If a file starts becoming narrative, split it into smaller sibling files.
- Use `.codex_memories/YYYY-MM-DD/artifacts/` for detail that does not belong in the daily index files.
- Keep `message_pairs.md` concise. If the exact user request is long, store the full request in an artifact file and reference it from the daily message index.
- Keep `daily_summary.md` as a rolling recent index, not a transcript.

## Project Identity

_(Project name and description - fill in for your project)_

## Project Structure & Important Directories

_(List important directories for your project)_

## Build, Setup, and Run Commands

_(Commands to build, test, and run your project)_

## Testing Commands & Conventions

- Preferred test root: `tests/`

## Comments & Docstrings

- Preserve useful comments/docstrings where they help future readers
- Do not add noisy comments for obvious code

## Documentation Sync Expectations

- Update local docs in `docs/` when architecture or workflow changes
- Keep docs aligned with meaningful code changes
""",
        "ARCHITECTURE.md": """# Project Architecture

_(This file is for the coding agent. It contains the architecture of the actual project being built.)_

## Application Stack
- Frontend: []
- Backend: []
- Database: []

## Structural Logic
_(Explain how the code modules interact for this specific end-product)_
""",
        "DESIGN.md": """# Application Design & UI

_(This file is for the coding agent. It contains UI/UX design and aesthetics for the project being built.)_

## Design System
- Primary Colors: []
- Typography: []

## Layout Rules
_(Describe the interactive mechanics and styling tokens for the target application)_
""",
    }

    for filename, content in root_files.items():
        path = Path(filename)
        if ensure_file(path, content):
            files_created.append(filename)

    core_files = {
        "_agent_rules.md": """# Core Agent Memory Engine

This system exists purely for **the coding agent** to persist its intelligence context securely across sessions without destroying its context window limits.

You are treating this repository as a Graph Data-Structure.
AGENTS.md -> .codex_memories/_agent_rules.md -> .codex_memories/project_state.md -> .codex_memories/system_prompt.md -> .codex_memories/daily_summary.md -> .codex_memories/YYYY-MM-DD/revival_summary.md -> .codex_memories/YYYY-MM-DD/task_log.md

## Start of Task Checklist
1. **Mandatory Load:** Trace from `AGENTS.md` and read `.codex_memories/_agent_rules.md` (this file).
2. **State Load:** Read `.codex_memories/project_state.md` to see stable facts and active threads.
3. **Protocol Load:** Read `.codex_memories/system_prompt.md` and `.codex_memories/daily_summary.md`.
4. **Daily Hub Creation:** If a `.codex_memories/YYYY-MM-DD/` folder for today does not exist, create it.
5. **Session Revival:** On the *first task of a new day*, read yesterday's folder. Write a `revival_summary.md` inside *today's* folder to bootstrap context.
6. **Detail Budget:** Load artifact files only when the daily index files are not enough. Do not read entire history by default.

## Navigation & Work Logic
7. **Architectural Guardrails:** Target project architecture is in `/ARCHITECTURE.md` and UI design is in `/DESIGN.md`. Do NOT use these files for your AI engine memory. They are strictly for the application you are building.
8. **Dynamic Discovery:** Whenever you enter a code directory, look for a `folder_map.md`. If missing, generate one so future agents can parse the directory structure without reading every dense codebase file.
9. **Small-File Rule:** Root files stay compact. Prefer one concern per file and create small files under `.codex_memories/YYYY-MM-DD/artifacts/` for detailed debugging, verification, migrations, or long requests.

## End of Task Checklist
10. **Conversations:** Inside today's `YYYY-MM-DD/` folder, create or append to `message_pairs.md`. Keep it concise. If the exact user prompt is long, store it in an artifact file and reference it from `message_pairs.md`.
11. **Task Log:** Inside today's `YYYY-MM-DD/` folder, create or append to `task_log.md`. Log only the high-signal summary of what was coded, debugged, and blocked during this run.
12. **Final Summarization:** Maintain an `end_of_day_summary.md` in today's folder. Keep it short and action-oriented so tomorrow's agent can scan it quickly.
13. **State Update:** Update your specific agent thread in `.codex_memories/project_state.md`.
14. **Split Early:** If any memory file starts to sprawl, split it into a new artifact file instead of continuing to append.

## Memory Root
- Write all reusable session memory only under `.codex_memories/`.
- Do not create or use any alternate memory root.
""",
        "system_prompt.md": """# System Prompt

Compact operating protocol for coding agents in this repository.

## Core Principles
- Read AGENTS.md first on connect
- Use `.codex_memories/` as the memory root
- Create date folders for daily isolation
- Keep memory files separated by concern
- Prefer small files over large logs
- Read artifact files only when the indexes are insufficient

## File Locations
- `_agent_rules.md` - Core memory engine
- `project_state.md` - Stable project facts
- `system_prompt.md` - This file
- `daily_summary.md` - Rolling recent index
- `YYYY-MM-DD/message_pairs.md` - Daily conversation index
- `YYYY-MM-DD/artifacts/` - Request-level or concern-level detail
- `YYYY-MM-DD/` - Daily folders
""",
        "daily_summary.md": """# Daily Summary

Rolling recent index for active work only.

## Format Rules
- Keep this file short enough to scan in one read.
- Use one bullet per task or change.
- Move detailed debugging, research, or verification into dated artifact files.
- Remove or archive stale bullets instead of letting this file grow.

## Active Tasks
_(Short bullets only)_

## Blockers
_(Short bullets only)_

## Recent Completions
_(Short bullets only)_
""",
        "project_state.md": """# Project State & Active Context

Stable facts and active threads for this project.

Keep this file compact. Durable facts belong here; long narratives do not.

## STABLE FACTS
project_name: ""
project_focus: ""
architecture: ""

## ACTIVE CONTEXT
active_threads: {}

## NOTES
_(Only durable, project-wide notes. Put task detail in dated files.)_
""",
        "folder_map.md": """# Directory: .codex_memories

| File | Purpose |
| --- | --- |
| _agent_rules.md | Core memory engine |
| system_prompt.md | Operating protocol |
| daily_summary.md | Rolling recent index |
| project_state.md | Stable facts |
| YYYY-MM-DD/message_pairs.md | Daily conversation index |
| YYYY-MM-DD/artifacts/ | Request-level detail |
| folder_map.md | This file |
| YYYY-MM-DD/ | Daily folders |
""",
    }

    for filename, content in core_files.items():
        path = root / filename
        if ensure_file(path, content):
            files_created.append(filename)

    today_folder = root / today
    ensure_dir(today_folder)
    ensure_dir(today_folder / "artifacts")

    daily_files = {
        "task_log.md": f"""# Task Log: {today}

Timestamped high-signal task entries for this day.

Keep rows concise. If a topic needs more detail, create an artifact file and reference it.

| Timestamp | Status | Summary | Files Touched | Blockers | Artifact |
| --- | --- | --- | --- | --- | --- |
""",
        "message_pairs.md": f"""# Message Pairs: {today}

Compact daily index of user requests and assistant outcomes.

If the exact prompt is long, store it in an artifact file and reference it here.

| Timestamp | Request ID | User Intent | Assistant Summary | Artifact |
| --- | --- | --- | --- | --- |
""",
        "revival_summary.md": """# Revival Summary

Context for today's session, bootstrapped from yesterday (if exists).

## Yesterday's Highlights
_(Fill in from previous day's end_of_day_summary.md)_

## Today's Plan
_(What needs to be done today)_

## Open Threads
_(Carried forward from previous sessions)_
""",
        "end_of_day_summary.md": """# End of Day Summary

Aggregate of today's tasks for tomorrow's revival.

## Completed Tasks
_(List completed tasks)_

## In Progress
_(List in-progress items)_

## Next Steps
_(What tomorrow should pick up)_
""",
        "artifacts/.gitkeep": "",
    }

    for filename, content in daily_files.items():
        path = today_folder / filename
        if ensure_file(path, content):
            files_created.append(f"{today}/{filename}")

    log("Bootstrap complete.")
    log(f"Files created: {len(files_created)}")
    if files_created:
        for f in files_created:
            log(f"  - {f}")


def validate_memory(root: Path) -> bool:
    log("Running SimpleMem validation...")

    issues = []

    if not root.exists():
        issues.append(f"Memory root not found: {root}")
        return False

    if not (root / "_agent_rules.md").exists():
        issues.append("Core file missing: _agent_rules.md")
    if not (root / "project_state.md").exists():
        issues.append("Core file missing: project_state.md")
    if not (root / "system_prompt.md").exists():
        issues.append("Core file missing: system_prompt.md")
    if not (root / "daily_summary.md").exists():
        issues.append("Core file missing: daily_summary.md")

    today = get_today()
    today_folder = root / today
    if not today_folder.exists():
        issues.append(f"Today's folder missing: {today}")
    else:
        required_daily = [
            "task_log.md",
            "message_pairs.md",
            "revival_summary.md",
            "end_of_day_summary.md",
            "artifacts",
        ]
        for f in required_daily:
            if not (today_folder / f).exists():
                issues.append(f"Daily file missing: {f}")

    if issues:
        for issue in issues:
            log(issue, "ERROR")
        return False

    log("All checks passed!", "INFO")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="simplemem", description="SimpleMem - One-command agent memory system initialization"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize memory system")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing files")

    subparsers.add_parser("validate", help="Validate memory system")

    args = parser.parse_args()

    if args.command == "init":
        init_memory(Path(".") / MEMORY_ROOT, force=args.force)
        return 0
    elif args.command == "validate":
        success = validate_memory(Path(".") / MEMORY_ROOT)
        return 0 if success else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
