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
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$MemoryRoot = Join-Path $RepoRoot ".codex_memories"
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

function Test-ProtocolConsistency {
    $issues = @()
    
    $agentsPath = Join-Path $RepoRoot "AGENTS.md"
    if (Test-Path $agentsPath) {
        $agentsContent = Get-Content $agentsPath -Raw
        if ($agentsContent -notmatch '\.codex_memories/') {
            $issues += "AGENTS.md does not reference .codex_memories/"
        }
    } else {
        $issues += "AGENTS.md not found"
    }
    
    if (Test-Path (Join-Path $RepoRoot ".agent_memories")) {
        $issues += "Found legacy root .agent_memories/. This repo uses .codex_memories/ only."
    }
    
    if (Test-Path "$MemoryRoot/_agent_rules.md") {
        $rulesContent = Get-Content "$MemoryRoot/_agent_rules.md" -Raw
        if ($rulesContent -match '\.agent_memories/') {
            $issues += "_agent_rules.md still references .agent_memories/"
        }
    }
    
    if ($issues.Count -gt 0) {
        Write-BootstrapLog "Protocol consistency issues detected:" -Level "WARN"
        foreach ($issue in $issues) {
            Write-BootstrapLog "  - $issue" -Level "WARN"
        }
        return $false
    }
    return $true
}

$protocolOk = Test-ProtocolConsistency
if (-not $protocolOk) {
    Write-BootstrapLog "Continuing anyway - bootstrap will fix most issues." -Level "INFO"
}

Ensure-Directory $MemoryRoot

$sysPromptContent = @"
# System Prompt

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
"@

$dailySummaryContent = @"
# Daily Summary

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
"@

$projectStateContent = @"
# Project State & Active Context

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
"@

$folderMapContent = @"
# Directory: .codex_memories

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
"@

Ensure-File -Path "$MemoryRoot/_agent_rules.md" -SkipIfExists
Ensure-File -Path "$MemoryRoot/system_prompt.md" -Content $sysPromptContent -SkipIfExists
Ensure-File -Path "$MemoryRoot/daily_summary.md" -Content $dailySummaryContent -SkipIfExists
Ensure-File -Path "$MemoryRoot/project_state.md" -Content $projectStateContent -SkipIfExists
Ensure-File -Path "$MemoryRoot/folder_map.md" -Content $folderMapContent -SkipIfExists

$todayFolder = "$MemoryRoot/$Today"
Ensure-Directory $todayFolder
Ensure-Directory "$todayFolder/artifacts"

$taskLogContent = @"
# Task Log: $Today

Timestamped high-signal task entries for this day.

Keep rows concise. If a topic needs more detail, create an artifact file and reference it.

| Timestamp | Status | Summary | Files Touched | Blockers | Artifact |
| --- | --- | --- | --- | --- | --- |
"@

$messagePairsContent = @"
# Message Pairs: $Today

Compact daily index of user requests and assistant outcomes.

If the exact prompt is long, store it in an artifact file and reference it here.

| Timestamp | Request ID | User Intent | Assistant Summary | Artifact |
| --- | --- | --- | --- | --- |
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
Ensure-File -Path "$todayFolder/artifacts/.gitkeep" -SkipIfExists

Write-BootstrapLog "Bootstrap complete." -Level "INFO"
Write-BootstrapLog "Memory root: $MemoryRoot" -Level "INFO"
Write-BootstrapLog "Today: $Today" -Level "INFO"

if (-not (Test-Path (Join-Path $RepoRoot "AGENTS.md"))) {
    Write-BootstrapLog "WARNING: AGENTS.md not found. Create it to define project rules." -Level "WARN"
}
