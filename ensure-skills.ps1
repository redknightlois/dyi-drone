#Requires -Version 5.1
<#
.SYNOPSIS
    Project-level skill bootstrap for the drone project.
.DESCRIPTION
    Creates symlinks in .claude\skills\ and .agents\skills\ so that
    Claude Code and Codex discover skills defined in support\skills\.
    Idempotent — safe to run repeatedly.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

$SkillSource = Join-Path $ScriptDir 'support\skills'

$Targets = @(
    Join-Path $ScriptDir '.claude\skills'
    Join-Path $ScriptDir '.agents\skills'
)

$created = 0
$skipped = 0
$warnings = 0

if (-not (Test-Path $SkillSource -PathType Container)) {
    Write-Host "No skills directory found at $SkillSource"
    exit 0
}

foreach ($skillDir in (Get-ChildItem -Path $SkillSource -Directory)) {
    $skillMd = Join-Path $skillDir.FullName 'SKILL.md'
    if (-not (Test-Path $skillMd)) { continue }

    $skillName = $skillDir.Name
    $sourceReal = (Resolve-Path $skillDir.FullName).Path

    foreach ($targetBase in $Targets) {
        $target = Join-Path $targetBase $skillName

        if (-not (Test-Path $targetBase)) {
            New-Item -ItemType Directory -Path $targetBase -Force | Out-Null
        }

        if (Test-Path $target) {
            $item = Get-Item $target -Force
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                $existingTarget = (Resolve-Path $target).Path
                if ($existingTarget -eq $sourceReal) {
                    $skipped++
                    continue
                }
            }
            Write-Warning "$target exists but points elsewhere, skipping"
            $warnings++
            continue
        }

        try {
            New-Item -ItemType SymbolicLink -Path $target -Target $skillDir.FullName -Force | Out-Null
        } catch {
            try {
                cmd /c mklink /J "$target" "$($skillDir.FullName)" | Out-Null
            } catch {
                Write-Warning "Failed to create link: $target -> $($skillDir.FullName): $_"
                $warnings++
                continue
            }
        }
        Write-Host "  created: $target -> $($skillDir.FullName)"
        $created++
    }
}

Write-Host "`nDone: created=$created  skipped=$skipped  warnings=$warnings"
