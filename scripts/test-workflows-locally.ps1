#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Local Workflow Testing Suite - Test Before You Push!
    
.DESCRIPTION
    Runs all critical workflow validations locally to catch issues before CI runs.
    Prevents round-trip delays and failed CI runs.
    
.PARAMETER TestSuite
    Which test suite to run: 'all', 'docs', 'paths', 'tldl', 'structure'
    
.PARAMETER VerboseOutput
    Enable verbose output for debugging
    
.EXAMPLE
    .\scripts\test-workflows-locally.ps1 -TestSuite all
    .\scripts\test-workflows-locally.ps1 -TestSuite docs -VerboseOutput
    
.NOTES
    The Scribe's local testing forge - test with confidence!
#>

param(
    [Parameter(Position = 0)]
    [ValidateSet('all', 'docs', 'paths', 'tldl', 'structure', 'quick')]
    [string]$TestSuite = 'all',
    
    [switch]$VerboseOutput
)

$ErrorActionPreference = "Continue"
$script:FailedTests = @()
$script:PassedTests = @()
$script:Warnings = @()
$script:StartTime = Get-Date

# Color output functions
function Write-Success {
    param([string]$Message)
    Write-Host "[PASS] " -ForegroundColor Green -NoNewline
    Write-Host $Message
    $script:PassedTests += $Message
}

function Write-Failure {
    param([string]$Message)
    Write-Host "[FAIL] " -ForegroundColor Red -NoNewline
    Write-Host $Message
    $script:FailedTests += $Message
}

function Write-TestWarning {
    param([string]$Message)
    Write-Host "[WARN] " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
    $script:Warnings += $Message
}

function Write-TestInfo {
    param([string]$Message)
    Write-Host "[INFO] " -ForegroundColor Cyan -NoNewline
    Write-Host $Message
}

function Write-TestHeader {
    param([string]$Message)
    Write-Host ""
    Write-Host "=========================================================" -ForegroundColor Magenta
    Write-Host "  $Message" -ForegroundColor Magenta
    Write-Host "=========================================================" -ForegroundColor Magenta
}

# Project root
$ProjectRoot = "E:/Tiny_Walnut_Games/the-seed"
$PackageRoot = "$ProjectRoot/packages/com.twg.the-seed/The Living Dev Agent"

Write-Host ""
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "     LOCAL WORKFLOW TEST SUITE" -ForegroundColor Cyan
Write-Host "     Test Before You Push - Avoid CI Round Trips!" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host ""

Write-TestInfo "Test Suite: $TestSuite"
Write-TestInfo "Project Root: $ProjectRoot"
Write-Host ""

# =============================================================================
# TEST 1: Directory Structure Linting (docs-architecture-check workflow)
# =============================================================================
function Test-DirectoryStructure {
    Write-TestHeader "TEST: Directory Structure Linting"
    
    $linterPath = "$PackageRoot/scripts/directory_lint.py"
    
    if (-not (Test-Path $linterPath)) {
        Write-Failure "Directory linter not found at: $linterPath"
        return $false
    }
    
    Write-TestInfo "Running directory_lint.py..."
    
    try {
        $output = python $linterPath 2>&1
        $exitCode = $LASTEXITCODE
        
        if ($VerboseOutput) {
            Write-Host $output
        }
        
        if ($exitCode -eq 0) {
            Write-Success "Directory structure is compliant"
            return $true
        } else {
            Write-Failure "Directory structure violations detected"
            Write-Host $output -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Failure "Failed to run directory linter: $_"
        return $false
    }
}

# =============================================================================
# TEST 2: TLDL Documentation Validation (docs-validation workflow)
# =============================================================================
function Test-TLDLValidation {
    Write-TestHeader "TEST: TLDL Documentation Validation"
    
    $validatorPath = "$PackageRoot/src/SymbolicLinter/validate_docs.py"
    $tldlPath = "$PackageRoot/TLDL/entries/"
    
    if (-not (Test-Path $validatorPath)) {
        Write-Failure "TLDL validator not found at: $validatorPath"
        return $false
    }
    
    if (-not (Test-Path $tldlPath)) {
        Write-TestWarning "TLDL entries directory not found at: $tldlPath"
        Write-TestInfo "Skipping TLDL validation (no entries to validate)"
        return $true
    }
    
    Write-TestInfo "Running validate_docs.py..."
    
    try {
        $args = @("--tldl-path", $tldlPath)
        if ($VerboseOutput) {
            $args += "--verbose"
        }
        
        $output = python $validatorPath @args 2>&1
        $exitCode = $LASTEXITCODE
        
        if ($VerboseOutput -or $exitCode -ne 0) {
            Write-Host $output
        }
        
        if ($exitCode -eq 0) {
            Write-Success "TLDL documentation validation passed"
            return $true
        } else {
            Write-Failure "TLDL documentation validation failed"
            return $false
        }
    } catch {
        Write-Failure "Failed to run TLDL validator: $_"
        return $false
    }
}

# =============================================================================
# TEST 3: Workflow Path Validation (ensure all workflow paths are correct)
# =============================================================================
function Test-WorkflowPaths {
    Write-TestHeader "TEST: Workflow Path Validation"
    
    $workflowDir = "$ProjectRoot/.github/workflows"
    $workflowFiles = Get-ChildItem -Path $workflowDir -Filter "*.yml"
    
    Write-TestInfo "Checking $($workflowFiles.Count) workflow files..."
    
    $pathIssues = @()
    
    # Patterns that indicate old/incorrect paths
    $oldPathPatterns = @(
        'scripts/alchemist-faculty/',
        'scripts/chronicle-keeper/',
        'scripts/cid-faculty/',
        'scripts/cid-schoolhouse/',
        'scripts/directory_lint.py',
        'scripts/validate_mcp_config.py',
        'src/SymbolicLinter/'
    )
    
    foreach ($workflow in $workflowFiles) {
        $content = Get-Content $workflow.FullName -Raw
        
        foreach ($pattern in $oldPathPatterns) {
            # Skip if it's already quoted (likely correct)
            if ($content -match [regex]::Escape($pattern) -and 
                $content -notmatch "packages/com\.twg\.the-seed/The Living Dev Agent.*$([regex]::Escape($pattern))") {
                
                $matches = Select-String -Path $workflow.FullName -Pattern $pattern
                
                foreach ($match in $matches) {
                    # Only report if it's not in a comment
                    if ($match.Line -notmatch '^\s*#') {
                        $pathIssues += @{
                            File = $workflow.Name
                            Line = $match.LineNumber
                            Pattern = $pattern
                            Content = $match.Line.Trim()
                        }
                    }
                }
            }
        }
    }
    
    if ($pathIssues.Count -eq 0) {
        Write-Success "All workflow paths appear correct"
        return $true
    } else {
        Write-Failure "Found $($pathIssues.Count) potential path issues in workflows"
        
        foreach ($issue in $pathIssues) {
            Write-Host "  File: $($issue.File):$($issue.Line)" -ForegroundColor Yellow
            Write-Host "  Pattern: $($issue.Pattern)" -ForegroundColor Gray
            Write-Host "  Line: $($issue.Content)" -ForegroundColor Gray
        }
        
        return $false
    }
}

# =============================================================================
# TEST 4: Required Files Existence
# =============================================================================
function Test-RequiredFiles {
    Write-TestHeader "TEST: Required Files Existence"
    
    $requiredFiles = @(
        @{Path = "README.md"; Critical = $true},
        @{Path = "LICENSE"; Critical = $true},
        @{Path = "CONTRIBUTING.md"; Critical = $false},
        @{Path = ".github/workflows/docs-validation.yml"; Critical = $true},
        @{Path = "packages/com.twg.the-seed/The Living Dev Agent/scripts/directory_lint.py"; Critical = $true},
        @{Path = "packages/com.twg.the-seed/The Living Dev Agent/src/SymbolicLinter/validate_docs.py"; Critical = $true}
    )
    
    $allPassed = $true
    
    foreach ($file in $requiredFiles) {
        $fullPath = Join-Path $ProjectRoot $file.Path
        
        if (Test-Path $fullPath) {
            Write-Success "Found: $($file.Path)"
        } else {
            if ($file.Critical) {
                Write-Failure "Missing critical file: $($file.Path)"
                $allPassed = $false
            } else {
                Write-TestWarning "Missing optional file: $($file.Path)"
            }
        }
    }
    
    return $allPassed
}

# =============================================================================
# TEST 5: Python Dependencies Check
# =============================================================================
function Test-PythonDependencies {
    Write-TestHeader "TEST: Python Dependencies"
    
    Write-TestInfo "Checking Python installation..."
    
    try {
        $pythonVersion = python --version 2>&1
        Write-Success "Python found: $pythonVersion"
    } catch {
        Write-Failure "Python not found or not in PATH"
        return $false
    }
    
    Write-TestInfo "Checking required Python packages..."
    
    $requiredPackages = @('pyyaml', 'requests')
    $allInstalled = $true
    
    foreach ($package in $requiredPackages) {
        $check = python -c "import $package" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Package installed: $package"
        } else {
            Write-TestWarning "Package not installed: $package"
            $allInstalled = $false
        }
    }
    
    if (-not $allInstalled) {
        Write-TestInfo "Install missing packages with: pip install pyyaml requests"
    }
    
    return $true  # Non-critical for most tests
}

# =============================================================================
# Execute Test Suite
# =============================================================================

Write-TestInfo "Starting test execution..."
Write-Host ""

$allTestsPassed = $true

switch ($TestSuite) {
    'quick' {
        Write-TestInfo "Running quick test suite (structure + paths)..."
        $allTestsPassed = (Test-DirectoryStructure) -and $allTestsPassed
        $allTestsPassed = (Test-WorkflowPaths) -and $allTestsPassed
    }
    
    'docs' {
        Write-TestInfo "Running documentation test suite..."
        $allTestsPassed = (Test-TLDLValidation) -and $allTestsPassed
        $allTestsPassed = (Test-RequiredFiles) -and $allTestsPassed
    }
    
    'paths' {
        Write-TestInfo "Running path validation test suite..."
        $allTestsPassed = (Test-WorkflowPaths) -and $allTestsPassed
    }
    
    'tldl' {
        Write-TestInfo "Running TLDL validation test suite..."
        $allTestsPassed = (Test-TLDLValidation) -and $allTestsPassed
    }
    
    'structure' {
        Write-TestInfo "Running structure validation test suite..."
        $allTestsPassed = (Test-DirectoryStructure) -and $allTestsPassed
    }
    
    'all' {
        Write-TestInfo "Running complete test suite..."
        $allTestsPassed = (Test-PythonDependencies) -and $allTestsPassed
        $allTestsPassed = (Test-RequiredFiles) -and $allTestsPassed
        $allTestsPassed = (Test-DirectoryStructure) -and $allTestsPassed
        $allTestsPassed = (Test-WorkflowPaths) -and $allTestsPassed
        $allTestsPassed = (Test-TLDLValidation) -and $allTestsPassed
    }
}

# =============================================================================
# Test Summary
# =============================================================================

$duration = (Get-Date) - $script:StartTime

Write-Host ""
Write-Host "=========================================================" -ForegroundColor Magenta
Write-Host "  TEST SUMMARY" -ForegroundColor Magenta
Write-Host "=========================================================" -ForegroundColor Magenta
Write-Host ""

Write-Host "Passed: " -ForegroundColor Green -NoNewline
Write-Host "$($script:PassedTests.Count) tests"

if ($script:FailedTests.Count -gt 0) {
    Write-Host "Failed: " -ForegroundColor Red -NoNewline
    Write-Host "$($script:FailedTests.Count) tests"
}

if ($script:Warnings.Count -gt 0) {
    Write-Host "Warnings: " -ForegroundColor Yellow -NoNewline
    Write-Host "$($script:Warnings.Count) issues"
}

Write-Host ""
Write-Host "Duration: " -NoNewline
Write-Host "$([int]$duration.TotalSeconds)s"
Write-Host ""

if ($allTestsPassed -and $script:FailedTests.Count -eq 0) {
    Write-Host "=================================================================" -ForegroundColor Green
    Write-Host "  ALL TESTS PASSED! Safe to push!" -ForegroundColor Green
    Write-Host "=================================================================" -ForegroundColor Green
    exit 0
} else {
    Write-Host "=================================================================" -ForegroundColor Red
    Write-Host "  TESTS FAILED - Fix issues before pushing!" -ForegroundColor Red
    Write-Host "=================================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Tip: Run with -VerboseOutput flag for more details" -ForegroundColor Cyan
    exit 1
}