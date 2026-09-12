<#
.SYNOPSIS
    Instantly shares your local Frappe LMS instance with your friend over the public internet
    via a secure Cloudflare Tunnel (HTTPS, zero port forwarding, no account needed).
#>

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BinDir = Join-Path $ScriptDir "bin"
$CloudflaredExe = Join-Path $BinDir "cloudflared.exe"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "    Frappe LMS Instant Public Internet Sharing           " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

if (-not (Test-Path $BinDir)) {
    New-Item -ItemType Directory -Path $BinDir -Force | Out-Null
}

if (-not (Test-Path $CloudflaredExe)) {
    Write-Host "[*] Downloading official Cloudflare Tunnel engine (cloudflared.exe)..." -ForegroundColor Yellow
    $url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    Invoke-WebRequest -Uri $url -OutFile $CloudflaredExe
    Write-Host "[+] Cloudflared downloaded successfully." -ForegroundColor Green
}

Write-Host "[*] Verifying local Frappe LMS service on port 8000..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000" -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue
    Write-Host "[+] Local Frappe LMS is reachable on port 8000." -ForegroundColor Green
} catch {
    Write-Host "[!] Note: Port 8000 is not yet responding. Make sure 'docker compose up' has completed." -ForegroundColor Yellow
}

Write-Host "`n[*] Starting Cloudflare Public Tunnel..." -ForegroundColor Cyan
Write-Host "[*] Creating instant secure HTTPS bridge for your friend..." -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

# Start cloudflared and capture output
& $CloudflaredExe tunnel --url http://localhost:8000
