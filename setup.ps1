# Dotfiles Setup Script for Windows
# Run: powershell -ExecutionPolicy Bypass -File setup.ps1

$ErrorActionPreference = "Stop"

Write-Host "=== Dotfiles Setup ===" -ForegroundColor Cyan

# Get current user's home directory
$UserHome = $env:USERPROFILE

# 1. Setup SenseVoice
$sensevoiceDir = "$UserHome\tools\SenseVoice"
if (-not (Test-Path $sensevoiceDir)) {
    Write-Host "[1/3] Creating SenseVoice directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $sensevoiceDir -Force | Out-Null
}

Write-Host "[1/3] Copying SenseVoice files..." -ForegroundColor Yellow
Copy-Item "$PSScriptRoot\tools\SenseVoice\*" $sensevoiceDir -Force

# 2. Setup Claude skills
$skillDir = "$UserHome\.claude\skills\talk"
if (-not (Test-Path $skillDir)) {
    Write-Host "[2/3] Creating skill directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $skillDir -Force | Out-Null
}

Write-Host "[2/3] Copying /talk skill..." -ForegroundColor Yellow
Copy-Item "$PSScriptRoot\.claude\skills\talk\*" $skillDir -Force

# 3. Setup Python venv (if not exists)
$venvDir = "$sensevoiceDir\.venv"
if (-not (Test-Path $venvDir)) {
    Write-Host "[3/3] Creating Python venv..." -ForegroundColor Yellow
    Push-Location $sensevoiceDir
    python -m venv .venv

    Write-Host "[3/3] Installing dependencies..." -ForegroundColor Yellow
    & ".venv\Scripts\pip" install --upgrade pip
    # Install pre-built torch (auto-detect latest compatible version)
    & ".venv\Scripts\pip" install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
    # Install other dependencies
    & ".venv\Scripts\pip" install numpy funasr sounddevice soundfile pyperclip pywin32 keyboard
    Pop-Location
} else {
    Write-Host "[3/3] Python venv already exists, skipping..." -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host "Usage: /talk in Claude Code to start SenseVoice"
Write-Host "Hotkey: Backtick (`) to record/stop"
