<#
.SYNOPSIS
    SimpleMem bootstrap script - scaffolds memory system for coding agents.
.DESCRIPTION
    Creates the required memory structure without overwriting existing files.
    Idempotent: safe to run multiple times.
#>

param(
    [switch]$Force,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$MemoryRoot = ".codex_memories"
$Today = Get-Date -Format "yyyy-MM-dd"

function Write-BootstrapLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "HH:mm:ss"
    $prefix = "[$timestamp] $Level"
    if ($Verbose -or $Level -eq "WARN" -or $Level -eq "ERROR") {
        Write-Host "$prefix`: $Message"
    }
}

function Ensure-Directory {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Write-BootstrapLog "Created directory: $Path"
        return $true
    }
    return $false
}

function Ensure-File {
    param(
        [string]$Path,
        [string]$Content = "",
        [switch]$SkipIfExists
    )

    $dir = Split-Path $Path -Parent
    if ($dir) { Ensure-Directory $dir }

    if ((Test-Path $Path) -and -not $Force) {
        if ($SkipIfExists) {
            Write-BootstrapLog "Skipping existing file: $Path" -Level "INFO"
            return $false
        }
        Write-BootstrapLog "File exists (use -Force to overwrite): $Path" -Level "WARN"
        return $false
    }

    if ($Content) {
        Set-Content -Path $Path -Value $Content -Force
    } else {
        New-Item -ItemType File -Path $Path -Force | Out-Null
    }
    Write-BootstrapLog "Created file: $Path"
    return $true
}

Write-BootstrapLog "Starting SimpleMem bootstrap..." -Level "INFO"

Ensure-Directory $MemoryRoot

$sysPromptContent = @"
# System Prompt

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
"@

$dailySummaryContent = @"
# Daily Summary

Rolling state for the current working day.

## Active Tasks
_(List current in-progress tasks here)_

## Recent Completions
_(List recently completed tasks here)_

## Blockers
_(List current blockers here)_

## Notes
_(Additional notes for today's session)_
"@

$projectStateContent = @"
# Project State & Active Context

Stable facts and active threads for this project.

## STABLE FACTS
project_name: ""
project_focus: ""
architecture: ""

## ACTIVE CONTEXT
active_threads: {}

## NOTES
_(Add project-specific notes here)_
"@

Ensure-File -Path "$MemoryRoot/_agent_rules.md" -SkipIfExists
Ensure-File -Path "$MemoryRoot/system_prompt.md" -Content $sysPromptContent -SkipIfExists
Ensure-File -Path "$MemoryRoot/daily_summary.md" -Content $dailySummaryContent -SkipIfExists
Ensure-File -Path "$MemoryRoot/project_state.md" -Content $projectStateContent -SkipIfExists
Ensure-File -Path "$MemoryRoot/folder_map.md" -SkipIfExists

$todayFolder = "$MemoryRoot/$Today"
Ensure-Directory $todayFolder

$taskLogContent = @"
# Task Log: $Today

Timestamped task entries for this day.

| Timestamp | Status | Summary | Files Touched | Blockers |
| --- | --- | --- | --- | --- |
"@

$messagePairsContent = @"
# Message Pairs: $Today

Exact user messages and concise assistant responses.

| Timestamp | User Message | Assistant Summary |
| --- | --- | --- |
"@

$revivalContent = @"
# Revival Summary

Context for today's session, bootstrapped from yesterday (if exists).

## Yesterday's Highlights
_(Fill in from previous day's end_of_day_summary.md)_

## Today's Plan
_(What needs to be done today)_

## Open Threads
_(Carried forward from previous sessions)_
"@

$endOfDayContent = @"
# End of Day Summary

Aggregate of today's tasks for tomorrow's revival.

## Completed Tasks
_(List completed tasks)_

## In Progress
_(List in-progress items)_

## Next Steps
_(What tomorrow should pick up)_
"@

Ensure-File -Path "$todayFolder/task_log.md" -Content $taskLogContent -SkipIfExists
Ensure-File -Path "$todayFolder/message_pairs.md" -Content $messagePairsContent -SkipIfExists
Ensure-File -Path "$todayFolder/revival_summary.md" -Content $revivalContent -SkipIfExists
Ensure-File -Path "$todayFolder/end_of_day_summary.md" -Content $endOfDayContent -SkipIfExists

Write-BootstrapLog "Bootstrap complete." -Level "INFO"
Write-BootstrapLog "Memory root: $MemoryRoot" -Level "INFO"
Write-BootstrapLog "Today: $Today" -Level "INFO"

if (-not (Test-Path "AGENTS.md")) {
    Write-BootstrapLog "WARNING: AGENTS.md not found. Create it to define project rules." -Level "WARN"
}