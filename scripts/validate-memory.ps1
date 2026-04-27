<#
.SYNOPSIS
    SimpleMem validator - checks memory system integrity.
.DESCRIPTION
    Validates that:
    - Canonical memory folder exists
    - Required files exist
    - No split-brain (.agent_memories/ vs .codex_memories/)
    - Today's folder exists with required daily files
    - No placeholder text in required files
#>

param(
    [switch]$Fix,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$MemoryRoot = Join-Path $RepoRoot ".codex_memories"
$Today = Get-Date -Format "yyyy-MM-dd"
$Issues = @()

function Write-Validation {
    param([string]$Message, [string]$Level = "INFO")
    if ($Level -eq "ERROR") {
        $script:Issues += $Message
    }
    Write-Host "[$Level] $Message"
}

function Test-PathAndWarn {
    param([string]$Path, [string]$RequiredMessage = "Required")
    if (Test-Path $Path) {
        if ($Verbose) { Write-Validation "Found: $Path" "INFO" }
        return $true
    }
    Write-Validation "$RequiredMessage not found: $Path" "ERROR"
    return $false
}

Write-Validation "Running SimpleMem validation..." "INFO"
Write-Validation "Today: $Today" "INFO"

Write-Validation "=== Checking Memory Root ===" "INFO"
$rootExists = Test-Path $MemoryRoot
if ($rootExists) {
    Write-Validation "Memory root exists: $MemoryRoot" "INFO"
} else {
    Write-Validation "Memory root not found: $MemoryRoot" "ERROR"
    if ($Fix) {
        Write-Validation "Run init script to create: .\$MemoryRoot" "INFO"
    }
}

Write-Validation "=== Checking Split-Brain ===" "INFO"
if (Test-Path (Join-Path $RepoRoot ".agent_memories")) {
    Write-Validation "SPLIT-BRAIN: Both .agent_memories/ and $MemoryRoot/ exist!" "ERROR"
    if ($Fix) {
        Write-Validation "Remove .agent_memories/ to resolve" "INFO"
    }
}

Write-Validation "=== Checking Core Files ===" "INFO"
$coreFiles = @(
    "$MemoryRoot/_agent_rules.md",
    "$MemoryRoot/system_prompt.md",
    "$MemoryRoot/daily_summary.md",
    "$MemoryRoot/project_state.md",
    "$MemoryRoot/folder_map.md"
)

foreach ($file in $coreFiles) {
    $exists = Test-PathAndWarn -Path $file -RequiredMessage "Core file"
    if ($exists) {
        $size = (Get-Item $file).Length
        if ($size -eq 0) {
            Write-Validation "Core file is empty: $file" "ERROR"
        }
    }
}

Write-Validation "=== Checking Today's Folder ===" "INFO"
$todayFolder = "$MemoryRoot/$Today"
if (Test-Path $todayFolder) {
    Write-Validation "Today's folder exists: $todayFolder" "INFO"
    
    $dailyFiles = @(
        "$todayFolder/task_log.md",
        "$todayFolder/message_pairs.md",
        "$todayFolder/revival_summary.md",
        "$todayFolder/end_of_day_summary.md",
        "$todayFolder/artifacts"
    )
    
    foreach ($file in $dailyFiles) {
        $null = Test-PathAndWarn -Path $file -RequiredMessage "Daily file"
    }
} else {
    Write-Validation "Today's folder not found: $todayFolder" "ERROR"
    if ($Fix) {
        Write-Validation "Run init script to create today's folder" "INFO"
    }
}

Write-Validation "=== Checking Project Files ===" "INFO"
$projectFiles = @(
    (Join-Path $RepoRoot "ARCHITECTURE.md"),
    (Join-Path $RepoRoot "DESIGN.md")
)
foreach ($file in $projectFiles) {
    $null = Test-PathAndWarn -Path $file -RequiredMessage "Project file"
}

Write-Validation "=== Checking Placeholders ===" "INFO"
$placeholderPattern = '\[Insert|\[STABLE|placeholder|sample blocker'
$checkFiles = @(
    "$MemoryRoot/project_state.md",
    "$MemoryRoot/system_prompt.md"
)

foreach ($file in $checkFiles) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        if ($content -match $placeholderPattern) {
            Write-Validation "Placeholder text found in: $file" "ERROR"
        }
    }
}

Write-Validation "=== Summary ===" "INFO"
$issueCount = $Issues.Count
if ($issueCount -eq 0) {
    Write-Validation "All checks passed!" "INFO"
} else {
    Write-Validation "Found $issueCount issue(s)" "ERROR"
    foreach ($issue in $Issues) {
        Write-Host "  - $issue"
    }
}

exit $issueCount
