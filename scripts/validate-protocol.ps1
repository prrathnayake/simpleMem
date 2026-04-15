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
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$MemoryRoot = Join-Path $RepoRoot ".codex_memories"
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
    $path = Join-Path $RepoRoot "README.md"
    if (-not (Test-Path $path)) { return $false }
    (Get-Content $path -Raw) -match '\.codex_memories/'
}

Test-Protocol "AGENTS.md points to .codex_memories/" {
    $path = Join-Path $RepoRoot "AGENTS.md"
    if (-not (Test-Path $path)) { return $false }
    (Get-Content $path -Raw) -match '\.codex_memories/'
}

Test-Protocol "AGENTS.md has memory entrypoint section" {
    $path = Join-Path $RepoRoot "AGENTS.md"
    if (-not (Test-Path $path)) { return $false }
    $content = Get-Content $path -Raw
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

Test-Protocol "_agent_rules.md includes small-file guidance" {
    if (-not (Test-Path "$MemoryRoot/_agent_rules.md")) { return $false }
    $content = Get-Content "$MemoryRoot/_agent_rules.md" -Raw
    $content -match 'artifacts/' -and $content -match 'Split Early'
}

Test-Protocol "init-agent-memory.ps1 uses .codex_memories/" {
    $path = Join-Path $RepoRoot "scripts/init-agent-memory.ps1"
    if (-not (Test-Path $path)) { return $false }
    (Get-Content $path -Raw) -match '\.codex_memories'
}

Test-Protocol ".agent_memories/ does not exist" {
    -not (Test-Path (Join-Path $RepoRoot ".agent_memories"))
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
        "$MemoryRoot/$Today/end_of_day_summary.md",
        "$MemoryRoot/$Today/artifacts"
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
$total = 12
if ($Passed -eq $total) {
    Write-Host "All protocol checks passed!" -ForegroundColor Green
    exit 0
} else {
    $failed = $total - $Passed
    Write-Host "$Passed/$total passed, $failed failed" -ForegroundColor Yellow
    exit 1
}
