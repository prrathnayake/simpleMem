<#
.SYNOPSIS
    SimpleMem protocol validator - checks all files match the canonical protocol.
.DESCRIPTION
    Verifies:
    - README.md uses .codex_memories/
    - AGENTS.md points to .codex_memories/
    - _agent_rules.md points to .codex_memories/
    - bootstrap scripts use .codex_memories/
    - required daily files exist
    - .agent_memories/ does not exist
#>

param(
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$MemoryRoot = ".codex_memories"
$Today = Get-Date -Format "yyyy-MM-dd"
$Issues = @()
$Passed = 0

function Test-Protocol {
    param([string]$Name, [scriptblock]$Test)
    $result = & $Test
    if ($result) {
        Write-Host "[PASS] $Name" -ForegroundColor Green
        $script:Passed++
    } else {
        Write-Host "[FAIL] $Name" -ForegroundColor Red
    }
}

Write-Host "=== SimpleMem Protocol Validation ===" -ForegroundColor Cyan
Write-Host "Today: $Today" -ForegroundColor Gray

Test-Protocol "README.md uses .codex_memories/" {
    if (-not (Test-Path "README.md")) { return $false }
    (Get-Content "README.md" -Raw) -match '\.codex_memories/'
}

Test-Protocol "AGENTS.md points to .codex_memories/" {
    if (-not (Test-Path "AGENTS.md")) { return $false }
    (Get-Content "AGENTS.md" -Raw) -match '\.codex_memories/'
}

Test-Protocol "AGENTS.md has memory entrypoint section" {
    if (-not (Test-Path "AGENTS.md")) { return $false }
    $content = Get-Content "AGENTS.md" -Raw
    $content -match 'Agent Memory Entrypoint' -and $content -match '_agent_rules\.md'
}

Test-Protocol "_agent_rules.md uses .codex_memories/" {
    if (-not (Test-Path "$MemoryRoot/_agent_rules.md")) { return $false }
    $content = Get-Content "$MemoryRoot/_agent_rules.md" -Raw
    $content -match '\.codex_memories/' -and $content -notmatch '\.agent_memories/'
}

Test-Protocol "_agent_rules.md matches startup order" {
    if (-not (Test-Path "$MemoryRoot/_agent_rules.md")) { return $false }
    $content = Get-Content "$MemoryRoot/_agent_rules.md" -Raw
    $content -match 'system_prompt\.md' -and $content -match 'daily_summary\.md'
}

Test-Protocol "init-agent-memory.ps1 uses .codex_memories/" {
    if (-not (Test-Path "scripts/init-agent-memory.ps1")) { return $false }
    (Get-Content "scripts/init-agent-memory.ps1" -Raw) -match '"\.codex_memories"'
}

Test-Protocol ".agent_memories/ does not exist" {
    -not (Test-Path ".agent_memories")
}

Test-Protocol "Memory root exists" {
    Test-Path $MemoryRoot
}

Test-Protocol "Core files exist" {
    $coreFiles = @(
        "$MemoryRoot/_agent_rules.md",
        "$MemoryRoot/project_state.md",
        "$MemoryRoot/system_prompt.md",
        "$MemoryRoot/daily_summary.md"
    )
    $allExist = $true
    foreach ($file in $coreFiles) {
        if (-not (Test-Path $file)) { $allExist = $false }
    }
    return $allExist
}

Test-Protocol "Today's folder exists" {
    Test-Path "$MemoryRoot/$Today"
}

Test-Protocol "Daily files exist" {
    $dailyFiles = @(
        "$MemoryRoot/$Today/task_log.md",
        "$MemoryRoot/$Today/message_pairs.md",
        "$MemoryRoot/$Today/revival_summary.md",
        "$MemoryRoot/$Today/end_of_day_summary.md"
    )
    $allExist = $true
    foreach ($file in $dailyFiles) {
        if (-not (Test-Path $file)) { 
            Write-Host "    Missing: $file" -ForegroundColor Gray
            $allExist = $false 
        }
    }
    return $allExist
}

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan
$total = 11
if ($Passed -eq $total) {
    Write-Host "All protocol checks passed!" -ForegroundColor Green
    exit 0
} else {
    $failed = $total - $Passed
    Write-Host "$Passed/$total passed, $failed failed" -ForegroundColor Yellow
    exit 1
}