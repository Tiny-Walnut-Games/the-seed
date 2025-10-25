param(
  [string]$Path = ".",
  [string]$ReindexCmd = "pwsh -NoProfile -File .\scripts\reindex.ps1",
  [string]$Include = "*.*",
  [string]$ExcludePattern = "(^|\\)(bin|obj|Library|Temp|.git|.vs|.idea|node_modules)(\\|$)"
)

Add-Type -AssemblyName System.IO.FileSystemWatcher

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = (Resolve-Path $Path)
$watcher.Filter = $Include
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true
$queue = New-Object System.Collections.Concurrent.ConcurrentQueue[string]
$lastRun = Get-Date 0
$debounceMs = 1000

function ShouldIgnore($fullPath) {
  if ($fullPath -match $ExcludePattern) { return $true }
  try {
    $fi = Get-Item -LiteralPath $fullPath -ErrorAction SilentlyContinue
    if ($fi -and $fi.Length -gt 5MB) {
      # allow Logs/ oversize text
      if ($fullPath -match "(^|\\)Logs(\\|$)") { return $false }
      return $true
    }
  } catch {}
  return $false
}

$handler = {
  param($sender, $e)
  if (-not [string]::IsNullOrWhiteSpace($e.FullPath) -and -not (ShouldIgnore $e.FullPath)) {
    $queue.Enqueue($e.FullPath) | Out-Null
  }
}

Register-ObjectEvent $watcher Changed -Action $handler | Out-Null
Register-ObjectEvent $watcher Created -Action $handler | Out-Null
Register-ObjectEvent $watcher Deleted -Action $handler | Out-Null
Register-ObjectEvent $watcher Renamed -Action $handler | Out-Null

Write-Host "Watching $($watcher.Path). Press Ctrl+C to stop."

try {
  while ($true) {
    Start-Sleep -Milliseconds 250
    $now = Get-Date
    if (($now - $lastRun).TotalMilliseconds -lt $debounceMs) { continue }

    # Drain queue and dedupe by path
    $pending = @{}
    while ($queue.TryDequeue([ref]$p)) { $pending[$p] = $true }
    if ($pending.Count -eq 0) { continue }

    $lastRun = $now
    $pathsArg = ($pending.Keys | ForEach-Object { '"' + $_.Replace('"','\"') + '"' }) -join ' '
    Write-Host "Reindexing changed files (count=$($pending.Count))..."

    $cmd = "$ReindexCmd --paths $pathsArg"
    Write-Host "> $cmd"
    try {
      & cmd.exe /c $cmd
    } catch {
      Write-Warning "Reindex command failed: $_"
    }
  }
} finally {
  Unregister-Event -SourceIdentifier * -ErrorAction SilentlyContinue
  $watcher.Dispose()
}
