param(
    [string]$Root = ".",
    [string]$Date = (Get-Date -Format "yyyy-MM-dd")
)

$resolvedRoot = (Resolve-Path $Root).Path
$memoryRoot = Join-Path $resolvedRoot ".codex_memories"
$templateRoot = Join-Path $memoryRoot "_templates"
$dayRoot = Join-Path $memoryRoot $Date

if (-not (Test-Path $memoryRoot)) {
    New-Item -ItemType Directory -Path $memoryRoot | Out-Null
}

if (-not (Test-Path $dayRoot)) {
    New-Item -ItemType Directory -Path $dayRoot | Out-Null
}

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"

$filesToSeed = @(
    @{
        Source = Join-Path $templateRoot "task_log.template.md"
        Target = Join-Path $dayRoot "task_log.md"
    },
    @{
        Source = Join-Path $templateRoot "revival_summary.template.md"
        Target = Join-Path $dayRoot "revival_summary.md"
    },
    @{
        Source = Join-Path $templateRoot "request_artifact.template.md"
        Target = Join-Path $dayRoot "request_notes.md"
    }
)

foreach ($file in $filesToSeed) {
    if (-not (Test-Path $file.Source)) {
        Write-Warning "Missing template: $($file.Source)"
        continue
    }

    if (Test-Path $file.Target) {
        continue
    }

    $content = Get-Content $file.Source -Raw
    $content = $content.Replace("{{DATE}}", $Date)
    $content = $content.Replace("{{TIMESTAMP}}", $timestamp)
    Set-Content -Path $file.Target -Value $content
}

Write-Output "Codex memory initialized for $Date at $dayRoot"
