param(
  [string] $Repo = "https://github.com/TheOneironaut/aws-cli.git",
  [string] $InstallDir = "$env:USERPROFILE\.awsctl\aws-cli",
  [string] $BinDir = "$env:USERPROFILE\bin",
  [switch] $Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Ensure-Dir([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path)) { New-Item -ItemType Directory -Path $Path | Out-Null }
}

# Prefer using local repo if script is executed from within the repo
$localRepoRoot = try { (Resolve-Path (Join-Path $PSScriptRoot '..')).Path } catch { $null }
$usingLocal = ($localRepoRoot -and (Test-Path (Join-Path $localRepoRoot 'Dockerfile')))

if (-not $usingLocal) {
  Ensure-Dir (Split-Path $InstallDir -Parent)
  if (Test-Path -LiteralPath $InstallDir) {
    Write-Host "Updating existing repo at $InstallDir" -ForegroundColor Cyan
    Push-Location $InstallDir
    try { git pull --rebase } finally { Pop-Location }
  } else {
    Write-Host "Cloning $Repo to $InstallDir" -ForegroundColor Cyan
    git clone $Repo $InstallDir
  }
  $repoDir = $InstallDir
} else {
  $repoDir = $localRepoRoot
}

# Build Docker image
Push-Location $repoDir
try {
  Write-Host "Building Docker image awsctl:latest" -ForegroundColor Cyan
  docker build -t awsctl:latest .
} finally { Pop-Location }

# Determine BinDir and ensure it exists
if (-not (Test-Path -LiteralPath $BinDir)) {
  $altBin = "$env:USERPROFILE\.local\bin"
  if (-not (Test-Path -LiteralPath $altBin)) { Ensure-Dir $altBin }
  $BinDir = $altBin
}
Ensure-Dir $BinDir

# Copy wrapper
$srcWrapper = Join-Path $repoDir 'scripts/awsctl.ps1'
$dstWrapper = Join-Path $BinDir 'awsctl.ps1'
Copy-Item -Force $srcWrapper $dstWrapper

# Add BinDir to User PATH if missing
$userPath = [Environment]::GetEnvironmentVariable('Path','User')
if (-not $userPath) { $userPath = '' }
if ($userPath -notlike "*${BinDir}*") {
  $newPath = if ($userPath) { $userPath + ';' + $BinDir } else { $BinDir }
  [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
  Write-Host "Added $BinDir to your User PATH. Open a new PowerShell window to pick it up." -ForegroundColor Yellow
}

# Suggest execution policy if needed
Write-Host "If you encounter script execution restrictions, run:" -ForegroundColor Yellow
Write-Host "  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force" -ForegroundColor Yellow

Write-Host "Installation complete." -ForegroundColor Green
Write-Host "Try: awsctl --help" -ForegroundColor Green
