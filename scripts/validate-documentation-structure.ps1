#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Validates documentation structure against AI_INSTRUCTIONS.md rules

.DESCRIPTION
    Ensures:
    - No .md files in root (except config files)
    - All documentation in canonical docs/ directory
    - TLDA/SEED/BRIDGES separation maintained
    - Proper file organization

.PARAMETER Path
    Repository root path (default: current directory)

.PARAMETER Strict
    Exit with error on any violation (default: warnings only)

.EXAMPLE
    ./scripts/validate-documentation-structure.ps1 -Strict
#>

param(
    [string]$Path = (Get-Location),
    [switch]$Strict = $false
)

$ErrorCount = 0
$WarningCount = 0

Write-Host "🔍 Validating Documentation Structure..." -ForegroundColor Cyan
Write-Host ""

# RULE 1: Check for .md files in root
Write-Host "Rule 1: Checking for .md files in root directory..."
$RootMarkdownFiles = Get-ChildItem -Path $Path -MaxDepth 1 -Filter "*.md" -ErrorAction SilentlyContinue

$AllowedRootFiles = @(
    "README.md",
    "CHANGELOG.md",
    "SECURITY.md",
    ".ai-instructions.md"
)

foreach ($File in $RootMarkdownFiles) {
    if ($File.Name -notin $AllowedRootFiles) {
        Write-Host "  ❌ VIOLATION: $($File.Name)" -ForegroundColor Red
        Write-Host "     Root-level .md files violate AI_INSTRUCTIONS.md" -ForegroundColor Red
        Write-Host "     Move to: docs/API/, docs/SEED/, docs/DEVELOPMENT/, or docs/BRIDGES/" -ForegroundColor Yellow
        Write-Host ""
        $ErrorCount++
    }
}

# RULE 2: Check docs/ structure
Write-Host "Rule 2: Checking docs/ directory structure..."
$DocsPath = Join-Path $Path "docs"

if (Test-Path $DocsPath) {
    $RequiredDirs = @("SEED", "TLDA", "BRIDGES", "DEVELOPMENT", "API")
    
    foreach ($Dir in $RequiredDirs) {
        $DirPath = Join-Path $DocsPath $Dir
        if (-not (Test-Path $DirPath)) {
            Write-Host "  ⚠️  WARNING: Missing docs/$Dir/ directory" -ForegroundColor Yellow
            Write-Host "     Create: $DirPath" -ForegroundColor Yellow
            Write-Host ""
            $WarningCount++
        } else {
            Write-Host "  ✅ docs/$Dir/ exists" -ForegroundColor Green
        }
    }
} else {
    Write-Host "  ❌ VIOLATION: docs/ directory does not exist" -ForegroundColor Red
    $ErrorCount++
}

# RULE 3: Check for scattered seed documentation
Write-Host ""
Write-Host "Rule 3: Checking for scattered Seed documentation..."
$ScatteredSeedDocs = Get-ChildItem -Path (Join-Path $Path "packages/com.twg.the-seed/seed") -Recurse -Filter "*.md" -ErrorAction SilentlyContinue | Where-Object {
    $_.FullName -notlike "*/docs/*"
}

if ($ScatteredSeedDocs.Count -gt 0) {
    Write-Host "  ⚠️  WARNING: Found $($ScatteredSeedDocs.Count) Seed docs outside docs/SEED/" -ForegroundColor Yellow
    foreach ($Doc in $ScatteredSeedDocs | Select-Object -First 5) {
        Write-Host "     - $($Doc.Name)" -ForegroundColor Yellow
    }
    if ($ScatteredSeedDocs.Count -gt 5) {
        Write-Host "     ... and $($ScatteredSeedDocs.Count - 5) more" -ForegroundColor Yellow
    }
    Write-Host ""
    $WarningCount++
} else {
    Write-Host "  ✅ No scattered Seed documentation found" -ForegroundColor Green
}

# RULE 4: Check for code files in root
Write-Host ""
Write-Host "Rule 4: Checking for code files in root directory..."
$RootCodeFiles = Get-ChildItem -Path $Path -MaxDepth 1 -Filter "*.*" -ErrorAction SilentlyContinue | Where-Object {
    $_.Extension -in @(".py", ".js", ".ts", ".cs")
}

foreach ($File in $RootCodeFiles) {
    Write-Host "  ❌ VIOLATION: $($File.Name)" -ForegroundColor Red
    Write-Host "     Code files should not be in root. Move to appropriate packages/ subdirectory" -ForegroundColor Red
    Write-Host ""
    $ErrorCount++
}

# RULE 5: Check canonical docs exist
Write-Host ""
Write-Host "Rule 5: Checking for canonical documentation files..."
$CanonicalFiles = @(
    "docs/SEED/README.md",
    "docs/TLDA/README.md",
    "docs/BRIDGES/README.md",
    "docs/DEVELOPMENT/README.md",
    "docs/API/README.md"
)

foreach ($File in $CanonicalFiles) {
    $FilePath = Join-Path $Path $File
    if (Test-Path $FilePath) {
        Write-Host "  ✅ $File exists" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  MISSING: $File" -ForegroundColor Yellow
        $WarningCount++
    }
}

# Summary
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  Errors:   $ErrorCount" -ForegroundColor $(if ($ErrorCount -gt 0) { "Red" } else { "Green" })
Write-Host "  Warnings: $WarningCount" -ForegroundColor $(if ($WarningCount -gt 0) { "Yellow" } else { "Green" })
Write-Host ""

if ($ErrorCount -gt 0) {
    Write-Host "❌ VALIDATION FAILED" -ForegroundColor Red
    Write-Host ""
    Write-Host "Fix the above errors to maintain AI_INSTRUCTIONS.md compliance." -ForegroundColor Red
    exit 1
}

if ($Strict -and $WarningCount -gt 0) {
    Write-Host "⚠️  STRICT MODE: Treating warnings as errors" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ VALIDATION PASSED" -ForegroundColor Green
exit 0