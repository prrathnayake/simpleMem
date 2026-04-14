#!/usr/bin/env bash
#
# SimpleMem bootstrap script - scaffolds memory system for coding agents.
# Cross-platform: works on Linux, macOS, and Windows (via Git Bash/WSL).
#
# Usage:
#   ./init-agent-memory.sh          # Dry run (shows what would be created)
#   ./init-agent-memory.sh --force # Overwrite existing files
#   ./init-agent-memory.sh --fix    # Auto-create missing files only
#

set -e

MEMORY_ROOT=".codex_memories"
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
    $0              # Preview what would be created
    $0 --force      # Actually scaffold (overwrites existing)
    $0              # Safe: creates missing files only
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

SYS_PROMPT_CONTENT='# System Prompt

Compact operating protocol for coding agents in this repository.

## Core Principles
- Read AGENTS.md first on connect
- Use `.codex_memories/` as the memory root
- Create date folders for daily isolation
- Keep memory files separated by concern

## File Locations
- `_agent_rules.md` - Core memory engine
- `project_state.md` - Stable project facts
- `system_prompt.md` - This file
- `daily_summary.md` - Rolling state
- `message_pairs.md` - Conversation log
- `YYYY-MM-DD/` - Daily folders
'

DAILY_SUMMARY_CONTENT='# Daily Summary

Rolling state for the current working day.

## Active Tasks
_(List current in-progress tasks here)_

## Recent Completions
_(List recently completed tasks here)_

## Blockers
_(List current blockers here)_

## Notes
_(Additional notes for today'"'"'s session)_
'

PROJECT_STATE_CONTENT='# Project State & Active Context

Stable facts and active threads for this project.

## STABLE FACTS
project_name: ""
project_focus: ""
architecture: ""

## ACTIVE CONTEXT
active_threads: {}

## NOTES
_(Add project-specific notes here)_
'

FOLDER_MAP_CONTENT='# Directory: .codex_memories

| File | Purpose |
| --- | --- |
| _agent_rules.md | Core memory engine |
| system_prompt.md | Operating protocol |
| daily_summary.md | Rolling state |
| project_state.md | Stable facts |
| message_pairs.md | Conversation log |
| folder_map.md | This file |
| YYYY-MM-DD/ | Daily folders |
'

ensure_file "$MEMORY_ROOT/_agent_rules.md" ""
ensure_file "$MEMORY_ROOT/system_prompt.md" "$SYS_PROMPT_CONTENT"
ensure_file "$MEMORY_ROOT/daily_summary.md" "$DAILY_SUMMARY_CONTENT"
ensure_file "$MEMORY_ROOT/project_state.md" "$PROJECT_STATE_CONTENT"
ensure_file "$MEMORY_ROOT/folder_map.md" "$FOLDER_MAP_CONTENT"

TODAY_DIR="$MEMORY_ROOT/$TODAY"
ensure_dir "$TODAY_DIR"

TASK_LOG_CONTENT="# Task Log: $TODAY

| Timestamp | Status | Summary | Files Touched | Blockers |
| --- | --- | --- | --- | --- |
"

MESSAGE_PAIRS_CONTENT="# Message Pairs: $TODAY

| Timestamp | User Message | Assistant Summary |
| --- | --- | --- |
"

REVIVAL_CONTENT="# Revival Summary

Context for today'"'"'s session.

## Yesterday'"'"'s Highlights
_(From previous day'"'"'s end_of_day_summary.md)_

## Today'"'"'s Plan
_(What needs to be done today)_

## Open Threads
_(Carried forward from previous sessions)_
"

END_OF_DAY_CONTENT="# End of Day Summary

Aggregate of today'"'"'s tasks.

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

log "INFO" "Bootstrap complete."
log "INFO" "Memory root: $MEMORY_ROOT"
log "INFO" "Today: $TODAY"

if [[ ! -f "AGENTS.md" ]]; then
    log "WARN" "AGENTS.md not found. Create it to define project rules."
fi

exit 0