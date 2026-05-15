param(
  [string]$Date = "",
  [string]$Symbol = "SPY",
  [string]$IbHost = "127.0.0.1",
  [int]$IbPort = 4001,
  [int]$ClientId = 51402,
  [int]$StaticLimit = 10,
  [string]$StrategyFamilies = "v3,v4,v5",
  [switch]$SkipLocalBuild,
  [switch]$NoPush
)

$ErrorActionPreference = "Stop"

$repo = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $repo "backend"
$frontend = Join-Path $repo "frontend"
$symbolUpper = $Symbol.ToUpperInvariant()

function Invoke-Step {
  param(
    [string]$Name,
    [scriptblock]$Command
  )
  Write-Host ""
  Write-Host "==> $Name" -ForegroundColor Cyan
  & $Command
}

function Get-LatestCompletedMarketDate {
  $etZone = [System.TimeZoneInfo]::FindSystemTimeZoneById("Eastern Standard Time")
  $etNow = [System.TimeZoneInfo]::ConvertTime([DateTimeOffset]::UtcNow, $etZone)
  $candidate = $etNow.Date
  if ($etNow.TimeOfDay -lt ([TimeSpan]::FromHours(20))) {
    $candidate = $candidate.AddDays(-1)
  }
  while ($candidate.DayOfWeek -eq [DayOfWeek]::Saturday -or $candidate.DayOfWeek -eq [DayOfWeek]::Sunday) {
    $candidate = $candidate.AddDays(-1)
  }
  return $candidate.ToString("yyyy-MM-dd")
}

if ([string]::IsNullOrWhiteSpace($Date)) {
  $Date = Get-LatestCompletedMarketDate
}

Invoke-Step "Check clean git state" {
  Push-Location $repo
  try {
    $status = git status --porcelain --untracked-files=all
    if ($status) {
      throw "Working tree is not clean. Commit, stash, or clear local changes before publishing.`n$status"
    }
  } finally {
    Pop-Location
  }
}

Invoke-Step "Fetch $symbolUpper $Date from IB Gateway" {
  Push-Location $backend
  try {
    $env:PYTHONPATH = "."
    python scripts\fetch_ib_live_extended.py --symbol $symbolUpper --date $Date --host $IbHost --port $IbPort --client-id $ClientId
  } finally {
    Pop-Location
  }
}

Invoke-Step "Rebuild SQLite DB" {
  Push-Location $backend
  try {
    $env:PYTHONPATH = "."
    python scripts\rebuild_live_extended_db.py
  } finally {
    Pop-Location
  }
}

Invoke-Step "Export static review payloads for local validation" {
  Push-Location $backend
  try {
    $env:PYTHONPATH = "."
    python scripts\export_static_reviews.py --output ..\frontend\public\reviews --limit $StaticLimit --ticker $symbolUpper --strategy-families $StrategyFamilies
  } finally {
    Pop-Location
  }
}

if (-not $SkipLocalBuild) {
  Invoke-Step "Build static review app locally" {
    Push-Location $frontend
    try {
      $env:VITE_STATIC_REVIEWS = "true"
      npm run build:static-reviews
    } finally {
      Pop-Location
    }
  }
}

Invoke-Step "Clean temporary local static payloads" {
  $publicReviews = Join-Path $frontend "public\reviews"
  if (Test-Path $publicReviews) {
    Remove-Item -LiteralPath $publicReviews -Recurse -Force
  }
}

Invoke-Step "Commit runtime DB update" {
  Push-Location $repo
  try {
    git add data/sqlite/tang_strategy_live_extended.db
    $cached = git diff --cached --name-only
    if (-not $cached) {
      Write-Host "No DB changes to commit."
      return
    }
    git commit -m "chore: update live extended db for $Date"
  } finally {
    Pop-Location
  }
}

if (-not $NoPush) {
  Invoke-Step "Push main and wait for Pages workflow" {
    Push-Location $repo
    try {
      $branch = git branch --show-current
      git push origin $branch
      Start-Sleep -Seconds 5
      $runJson = gh run list --repo TUSKIJAY/tang-strategy --workflow "Publish static reviews" --branch $branch --limit 1 --json databaseId,status,conclusion | ConvertFrom-Json
      if ($runJson.Count -gt 0) {
        gh run watch $runJson[0].databaseId --repo TUSKIJAY/tang-strategy --exit-status
      }
    } finally {
      Pop-Location
    }
  }
}

Write-Host ""
Write-Host "Done: https://tuskijay.github.io/tang-strategy/#$($symbolUpper.ToLowerInvariant())-$Date-extended" -ForegroundColor Green
