#!/usr/bin/env bash
#
# SimpleMem bootstrap script - scaffolds memory system for coding agents.
# Cross-platform: works on Linux, macOS, and Windows (via Git Bash/WSL).
#
# Usage:
#   ./init-agent-memory.sh          # Creates missing files only
#   ./init-agent-memory.sh --force # Overwrite existing files
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MEMORY_ROOT="$REPO_ROOT/.codex_memories"
TODAY=$(date +%Y-%m-%d)
FORCE=false
VERBOSE=false

usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

OPTIONS:
    -f, --force    Overwrite existing files
    -v, --verbose Show all operations
    -h, --help    Show this help

EXAMPLES:
    $0              # Creates missing files only
    $0 --force      # Overwrite existing files
EOF
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--force) FORCE=true ;;
        -v|--verbose) VERBOSE=true ;;
        -h|--help) usage; exit 0 ;;
        *) usage; exit 1 ;;
    esac
    shift
done

log() {
    local level="$1"
    shift
    echo "[$(date +%H:%M:%S)] $level: $*"
}

ensure_dir() {
    if [[ ! -d "$1" ]]; then
        mkdir -p "$1"
        log "INFO" "Created directory: $1"
        return 0
    fi
    return 1
}

ensure_file() {
    local path="$1"
    local content="$2"
    local dir
    dir=$(dirname "$path")
    
    [[ -n "$dir" ]] && ensure_dir "$dir"
    
    if [[ -f "$path" && "$FORCE" != "true" ]]; then
        log "INFO" "Skipping existing (use --force): $path"
        return 0
    fi
    
    echo "$content" > "$path"
    log "INFO" "Created file: $path"
}

log "INFO" "Starting SimpleMem bootstrap..."
log "INFO" "Memory root: $MEMORY_ROOT"
log "INFO" "Today: $TODAY"

ensure_dir "$MEMORY_ROOT"

AGENTS_CONTENT='# Repository Guidelines

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
'

ARCHITECTURE_CONTENT='# Project Architecture

_(This file is for the coding agent. It contains the architecture of the actual project being built.)_

## Application Stack
- Frontend: []
- Backend: []
- Database: []

## Structural Logic
_(Explain how the code modules interact for this specific end-product)_
'

DESIGN_CONTENT='# Application Design & UI

_(This file is for the coding agent. It contains UI/UX design and aesthetics for the project being built.)_

## Design System
- Primary Colors: []
- Typography: []

## Layout Rules
_(Describe the interactive mechanics and styling tokens for the target application)_
'

SYS_PROMPT_CONTENT='# System Prompt

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
'

DAILY_SUMMARY_CONTENT='# Daily Summary

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
'

PROJECT_STATE_CONTENT='# Project State & Active Context

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
'

FOLDER_MAP_CONTENT='# Directory: .codex_memories

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
'

AGENT_RULES_CONTENT='# Core Agent Memory Engine

This system exists purely for **the coding agent** to persist its intelligence context securely across sessions without destroying its context window limits.

You are treating this repository as a Graph Data-Structure.
`AGENTS.md` -> `.codex_memories/_agent_rules.md` -> `.codex_memories/project_state.md` -> `.codex_memories/system_prompt.md` -> `.codex_memories/daily_summary.md` -> `.codex_memories/YYYY-MM-DD/revival_summary.md` -> `.codex_memories/YYYY-MM-DD/task_log.md`

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
12. **Daily Summary Update:** Update `.codex_memories/daily_summary.md` with active tasks, blockers, and recent completions. Keep it a rolling index; archive or remove stale items instead of letting it grow.
13. **Final Summarization:** Maintain an `end_of_day_summary.md` in today's folder. Keep it short and action-oriented so tomorrow's agent can scan it quickly.
14. **State Update:** Update your specific agent thread in `.codex_memories/project_state.md`.
15. **Split Early:** If any memory file starts to sprawl, split it into a new artifact file instead of continuing to append.

## Memory Root
- Write all reusable session memory only under `.codex_memories/`.
- Do not create or use any alternate memory root.
'

ensure_file "$REPO_ROOT/AGENTS.md" "$AGENTS_CONTENT"
ensure_file "$REPO_ROOT/ARCHITECTURE.md" "$ARCHITECTURE_CONTENT"
ensure_file "$REPO_ROOT/DESIGN.md" "$DESIGN_CONTENT"

ensure_file "$MEMORY_ROOT/_agent_rules.md" "$AGENT_RULES_CONTENT"
ensure_file "$MEMORY_ROOT/system_prompt.md" "$SYS_PROMPT_CONTENT"
ensure_file "$MEMORY_ROOT/daily_summary.md" "$DAILY_SUMMARY_CONTENT"
ensure_file "$MEMORY_ROOT/project_state.md" "$PROJECT_STATE_CONTENT"
ensure_file "$MEMORY_ROOT/folder_map.md" "$FOLDER_MAP_CONTENT"

TODAY_DIR="$MEMORY_ROOT/$TODAY"
ensure_dir "$TODAY_DIR"
ensure_dir "$TODAY_DIR/artifacts"

TASK_LOG_CONTENT="# Task Log: $TODAY

Timestamped high-signal task entries for this day.

Keep rows concise. If a topic needs more detail, create an artifact file and reference it.

| Timestamp | Status | Summary | Files Touched | Blockers | Artifact |
| --- | --- | --- | --- | --- | --- |
"

MESSAGE_PAIRS_CONTENT="# Message Pairs: $TODAY

Compact daily index of user requests and assistant outcomes.

If the exact prompt is long, store it in an artifact file and reference it here.

| Timestamp | Request ID | User Intent | Assistant Summary | Artifact |
| --- | --- | --- | --- | --- |
"

REVIVAL_CONTENT="# Revival Summary

Context for today'"'"'s session, bootstrapped from yesterday (if exists).

## Yesterday'"'"'s Highlights
_(Fill in from previous day'"'"'s end_of_day_summary.md)_

## Today'"'"'s Plan
_(What needs to be done today)_

## Open Threads
_(Carried forward from previous sessions)_
"

END_OF_DAY_CONTENT="# End of Day Summary

Aggregate of today'"'"'s tasks for tomorrow'"'"'s revival.

## Completed Tasks
_(List completed tasks)_

## In Progress
_(List in-progress items)_

## Next Steps
_(What tomorrow should pick up)_
"

ensure_file "$TODAY_DIR/task_log.md" "$TASK_LOG_CONTENT"
ensure_file "$TODAY_DIR/message_pairs.md" "$MESSAGE_PAIRS_CONTENT"
ensure_file "$TODAY_DIR/revival_summary.md" "$REVIVAL_CONTENT"
ensure_file "$TODAY_DIR/end_of_day_summary.md" "$END_OF_DAY_CONTENT"
ensure_file "$TODAY_DIR/artifacts/.gitkeep" ""

log "INFO" "Bootstrap complete."
log "INFO" "Memory root: $MEMORY_ROOT"
log "INFO" "Today: $TODAY"

if [[ ! -f "$REPO_ROOT/AGENTS.md" ]]; then
    log "WARN" "AGENTS.md not found. Create it to define project rules."
fi

exit 0
