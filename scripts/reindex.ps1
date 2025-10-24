param(
  [Parameter(ValueFromRemainingArguments=$true)]
  [string[]]$paths
)

if ($paths.Count -eq 0) {
  Write-Host "Usage: pwsh -NoProfile -File scripts/reindex.ps1 --paths <file1> <file2> ..."
  exit 1
}

# Join and forward to Python ingester
$quoted = $paths | ForEach-Object { '"' + $_.Replace('"','\"') + '"' }
$cmd = "py -3 .\scripts\ingest.py --paths $($quoted -join ' ')"
Write-Host "> $cmd"

# Use cmd.exe to ensure proper argument parsing for quoted paths
& cmd.exe /c $cmd
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
