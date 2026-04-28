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

You are a coding agent assigned to this project. This file is your absolute entrypoint. Read it fully, then follow the reading chain below before doing any substantive work.

## Agent Memory Entrypoint

Before writing, editing, or running any code, you MUST read these files in this exact order:

1. `.codex_memories/_agent_rules.md` — Core memory engine and mandatory checklists
2. `.codex_memories/project_state.md` — Stable facts and active threads
3. `.codex_memories/system_prompt.md` — Your operating protocol
4. `.codex_memories/code_logics.md` — How this codebase works
5. `.codex_memories/system_logics.md` — Work scenario guidance
6. `.codex_memories/daily_summary.md` — Rolling recent index
7. `.codex_memories/YYYY-MM-DD/revival_summary.md` — Today's session bootstrap
8. `.codex_memories/YYYY-MM-DD/task_log.md` — Today's task journal

## Memory Root Rule

Write all reusable session memory ONLY under `.codex_memories/`.
Do NOT create or use any alternate memory root.

## Small-File Protocol

This project uses a small-file memory system for higher-accuracy retrieval.

- Keep root memory files short and index-like.
- Prefer one concern per file.
- Prefer one request artifact per request, investigation, or verification thread.
- If a file starts becoming narrative, split it into smaller sibling files.
- Use `.codex_memories/YYYY-MM-DD/artifacts/` for detail that does not belong in the daily index files.
- Keep `message_pairs.md` concise. If the exact user request is long, store the full request in an artifact file and reference it from the daily message index.
- Keep `daily_summary.md` as a rolling recent index, not a transcript.

## Project Identity

_(As the coding agent, fill this in once you understand the project.)_

## Project Structure & Important Directories

_(As the coding agent, list important directories for this project once you discover them.)_

## Build, Setup, and Run Commands

_(As the coding agent, document commands to build, test, and run this project.)_

## Testing Commands & Conventions

- Preferred test root: `tests/`
- Document the actual test runner and conventions once discovered.

## Comments & Docstrings

- Preserve useful comments/docstrings where they help future readers.
- Do not add noisy comments for obvious code.

## Documentation Sync Expectations

- Update local docs in `docs/` when architecture or workflow changes.
- Keep docs aligned with meaningful code changes.
""",
        "ARCHITECTURE.md": """# Project Architecture

As the coding agent, document the architecture of the actual project here. Update this file as the architecture evolves.

## Application Stack

- Frontend: []  # Fill in frameworks and libraries
- Backend: []  # Fill in runtime, frameworks, and libraries
- Database: []  # Fill in database technology

## Structural Logic

_(Document how code modules interact for this specific project.)_
""",
        "DESIGN.md": """# Application Design & UI

As the coding agent, document the UI/UX design and aesthetics of the project here.

## Design System

- Primary Colors: []  # Fill in color palette
- Typography: []  # Fill in font families and scale

## Layout Rules

_(Describe interactive mechanics, styling tokens, and responsive behavior.)_
""",
    }

    for filename, content in root_files.items():
        path = Path(filename)
        if ensure_file(path, content):
            files_created.append(filename)

    core_files = {
        "_agent_rules.md": """# Core Agent Memory Engine

This system exists to help you persist intelligence context across sessions without exhausting your context window.

Treat this repository as a directed graph of memory files:

`AGENTS.md` → `_agent_rules.md` → `project_state.md` → `system_prompt.md` → `code_logics.md` → `system_logics.md` → `daily_summary.md` → `YYYY-MM-DD/revival_summary.md` → `YYYY-MM-DD/task_log.md`

## Start of Session Checklist

You MUST complete these steps at the start of every session before accepting user requests:

1. **Mandatory Load:** Read `AGENTS.md`, then this file (`_agent_rules.md`).
2. **State Load:** Read `project_state.md` to understand stable facts and active threads.
3. **Protocol Load:** Read `system_prompt.md`, `code_logics.md`, and `system_logics.md`.
4. **Daily Context:** Read `daily_summary.md` for recent active work.
5. **Daily Hub Creation:** If today's `YYYY-MM-DD/` folder does not exist, create it.
6. **Session Revival:** On the first task of a new day, read yesterday's folder. Write a `revival_summary.md` inside today's folder to bootstrap context.
7. **Detail Budget:** Load artifact files only when daily index files are insufficient. Do NOT read entire history by default.

## Navigation & Work Logic

8. **Architectural Guardrails:** Target project architecture is in `/ARCHITECTURE.md` and UI design is in `/DESIGN.md`. Use these files ONLY for understanding the application you are building. Do NOT use them for memory system mechanics.
9. **Dynamic Discovery:** Whenever you enter a code directory, look for a `folder_map.md`. If missing, generate one so future agents can parse the directory structure without reading every dense codebase file.
10. **Small-File Rule:** Keep root memory files compact. Prefer one concern per file. Create small files under `YYYY-MM-DD/artifacts/` for detailed debugging, verification, migrations, or long requests.

## End of Session Checklist

You MUST complete these steps before ending any session:

11. **Conversation Log:** In today's folder, create or append to `message_pairs.md`. Keep it concise. If the exact user prompt is long, store it in an artifact file and reference it from `message_pairs.md`.
12. **Task Log:** In today's folder, create or append to `task_log.md`. Log only the high-signal summary of what was coded, debugged, and blocked.
13. **Daily Summary Update:** Update `daily_summary.md` with active tasks, blockers, and recent completions. Keep it a rolling index; archive or remove stale items instead of letting it grow.
14. **End of Day Summary:** Maintain an `end_of_day_summary.md` in today's folder. Keep it short and action-oriented so tomorrow's agent can scan it quickly.
15. **State Update:** Update `project_state.md` with any new durable facts discovered during this session.
16. **Split Early:** If any memory file exceeds ~50 lines or starts to sprawl, split it into a new artifact file instead of continuing to append.

## Memory Root

- Write all reusable session memory only under `.codex_memories/`.
- Do not create or use any alternate memory root.
""",
        "system_prompt.md": """# System Prompt

You are a coding agent operating in this repository. Follow these rules at all times.

## Core Principles

- Read `AGENTS.md` first on every connect.
- Use `.codex_memories/` as the sole memory root.
- Create date folders for daily isolation.
- Keep memory files separated by concern.
- Prefer small files over large logs.
- Read artifact files only when the indexes are insufficient.

## Behavioral Rules

- Be concise in memory files. Favor bullet points over paragraphs.
- Write facts, not narratives.
- Update memory files incrementally. Do not let files grow unbounded.
- Reference long content; do not inline it.
- Always verify file paths before writing.

## File Locations

| File | Purpose |
| --- | --- |
| `_agent_rules.md` | Core memory engine and checklists |
| `project_state.md` | Stable project facts |
| `system_prompt.md` | This file — your operating protocol |
| `code_logics.md` | How the codebase works |
| `system_logics.md` | Work scenario guidance |
| `daily_summary.md` | Rolling recent index |
| `YYYY-MM-DD/message_pairs.md` | Daily conversation index |
| `YYYY-MM-DD/artifacts/` | Request-level or concern-level detail |
| `YYYY-MM-DD/` | Daily folders |
""",
        "code_logics.md": """# Code Logics

As you explore and modify this codebase, document how it works here. Keep this file updated so future agents can onboard quickly.

## Sections to Maintain

- **Package/Module Layout:** Map the directory structure and what each module does.
- **Entry Points:** List CLI commands, main functions, and startup scripts.
- **Key Algorithms:** Document complex or critical business logic.
- **Data Flow:** Trace how data moves between components.
- **Dependencies:** Note important external libraries and why they are used.
- **Test Conventions:** Document the test framework, fixtures, and coverage expectations.
- **Build Notes:** Document build steps, compilation, or bundling requirements.

## Current Understanding

_(Fill in as you discover the codebase.)_
""",
        "system_logics.md": """# System Logics: Work Scenarios

Use this guide when you need to know which memory files to read and update for different types of work.

## Scenario Matrix

| Area | What to Check First | Key Memory Files to Update |
| --- | --- | --- |
| Backend/API | `ARCHITECTURE.md`, `project_state.md` | `task_log.md`, `daily_summary.md`, `artifacts/` for API design |
| Frontend/UI | `DESIGN.md`, `ARCHITECTURE.md` | `task_log.md`, `message_pairs.md`, `artifacts/` for component specs |
| Database/Schema | `ARCHITECTURE.md`, `code_logics.md` | `task_log.md`, `project_state.md`, `artifacts/` for migrations |
| DevOps/CI/CD | `ARCHITECTURE.md`, repo root configs | `task_log.md`, `daily_summary.md`, `artifacts/` for deployment notes |
| Testing | `tests/`, build config | `task_log.md`, `artifacts/` for test strategy docs |
| Bug Fix | `daily_summary.md`, yesterday's `task_log.md` | `task_log.md`, `message_pairs.md`, `artifacts/` for root-cause analysis |
| Refactor | `code_logics.md`, `ARCHITECTURE.md` | `task_log.md`, `project_state.md`, `artifacts/` for migration plans |

## Area-Specific Workflows

### Backend / API Development
1. Read `ARCHITECTURE.md` to understand the stack and module boundaries.
2. Check `project_state.md` for active backend threads or API versioning notes.
3. Before coding, write an artifact in `artifacts/` describing the endpoint contract (URL, method, request/response shape).
4. After implementing, update `code_logics.md` if module interactions changed.
5. Log in `task_log.md` with files touched and any blockers.

### Frontend / UI Development
1. Read `DESIGN.md` for colors, typography, layout rules, and component hierarchy.
2. Check `project_state.md` for active UI threads or design system updates.
3. Before coding, write an artifact describing the component structure, state flow, and any new design tokens.
4. After implementing, update `code_logics.md` if component interactions or state management changed.
5. Log in `task_log.md` with files touched and visual verification notes.

### Database / Schema Changes
1. Read `ARCHITECTURE.md` for the database technology and existing schema overview.
2. Check `project_state.md` for schema version or migration history.
3. Before changing schema, write an artifact in `artifacts/` with:
   - Current schema snapshot
   - Proposed changes with rationale
   - Migration script (if applicable)
   - Rollback plan
4. After applying, update `project_state.md` with new stable facts about the schema.
5. Log in `task_log.md` with migration status and any data integrity checks.

### DevOps / CI/CD / Infrastructure
1. Read `ARCHITECTURE.md` for deployment target and infrastructure overview.
2. Check `project_state.md` for environment configs and secrets management approach.
3. Before changing pipelines, write an artifact in `artifacts/` with:
   - Current pipeline diagram or step list
   - Proposed change and risk assessment
   - Verification steps
4. After applying, update `project_state.md` with new environment facts.
5. Log in `task_log.md` with pipeline run results and any incidents.

### Testing / QA
1. Read `code_logics.md` to understand the testing framework and conventions.
2. Check `daily_summary.md` for recently completed features that need test coverage.
3. Before writing tests, write an artifact in `artifacts/` with:
   - Test plan (unit, integration, e2e)
   - Edge cases and mock strategy
4. After running tests, update `task_log.md` with pass/fail status and flaky test notes.
5. If coverage gaps are found, add to `daily_summary.md` under "Active Tasks".

### Bug Fixes
1. Read `daily_summary.md` for active blockers and recent completions.
2. Read yesterday's `task_log.md` and `end_of_day_summary.md` for context.
3. Write an artifact in `artifacts/` with:
   - Bug reproduction steps
   - Root-cause hypothesis
   - Fix strategy and verification steps
4. After fixing, update `task_log.md` with root cause and resolution.
5. If the bug reveals a systemic issue, update `code_logics.md` or `project_state.md`.

### Refactoring
1. Read `code_logics.md` and `ARCHITECTURE.md` to understand current structure.
2. Check `project_state.md` for any threads that might conflict with refactoring.
3. Write an artifact in `artifacts/` with:
   - Scope of refactor (what changes, what stays)
   - Risk areas and rollback plan
   - Step-by-step execution order
4. After each step, update `task_log.md`.
5. After completion, update `code_logics.md` to reflect the new structure.

## Cross-Cutting Rules

- **Never skip the read chain.** Even if you are "just fixing a typo," read `_agent_rules.md`, `project_state.md`, `system_prompt.md`, `code_logics.md`, `system_logics.md`, and `daily_summary.md` first.
- **Always write an artifact before complex work.** If the task spans more than 2 files or involves design decisions, create an artifact.
- **Update `project_state.md` only for durable facts.** Temporary blockers belong in `daily_summary.md`.
- **Keep `daily_summary.md` short.** Archive or remove items older than a few days.
- **Split early.** If any file exceeds ~50 lines, consider splitting into an artifact or a new root file.
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

Maintain this file with durable facts about the project. Keep it compact. Long narratives do not belong here.

## STABLE FACTS

project_name: ""  # Fill in once known
project_focus: ""  # One-line description of what this project does
architecture: ""  # High-level architecture summary

## ACTIVE CONTEXT

active_threads: {}
# Example:
#   api-v2: "Redesigning REST endpoints for v2"
#   ui-refresh: "Updating component library to new design system"

## NOTES

# Only durable, project-wide notes. Put task detail in dated files.
""",
        "folder_map.md": """# Directory: .codex_memories

| File | Purpose |
| --- | --- |
| `_agent_rules.md` | Core memory engine and checklists |
| `system_prompt.md` | Operating protocol |
| `code_logics.md` | How the codebase works |
| `system_logics.md` | Work scenario guidance |
| `daily_summary.md` | Rolling recent index |
| `project_state.md` | Stable facts |
| `YYYY-MM-DD/message_pairs.md` | Daily conversation index |
| `YYYY-MM-DD/artifacts/` | Request-level detail |
| `folder_map.md` | This file |
| `YYYY-MM-DD/` | Daily folders |
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

Context for today's session, bootstrapped from yesterday.

## Yesterday's Highlights

_(Fill in from previous day's `end_of_day_summary.md`)_

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

    core_files = [
        "_agent_rules.md",
        "project_state.md",
        "system_prompt.md",
        "code_logics.md",
        "system_logics.md",
        "daily_summary.md",
        "folder_map.md",
    ]
    for f in core_files:
        path = root / f
        if not path.exists():
            issues.append(f"Core file missing: {f}")
        elif path.stat().st_size == 0:
            issues.append(f"Core file is empty: {f}")

    repo_root = root.parent
    for f in ["ARCHITECTURE.md", "DESIGN.md"]:
        if not (repo_root / f).exists():
            issues.append(f"Project file missing: {f}")

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
