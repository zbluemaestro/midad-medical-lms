<#
.SYNOPSIS
    Automated environment readiness, Docker engine verification, and Frappe LMS launcher for Windows 11.
#>

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$ComposeFile = Join-Path $ProjectRoot "docker\docker-compose.yml"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "    Frappe LMS SaaS Engine - Windows 11 Launcher         " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Check Docker
$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue

if (-not $dockerCmd) {
    Write-Host "`n[!] Docker is not detected in your system PATH." -ForegroundColor Yellow
    Write-Host "[*] To run containerized Frappe LMS on Windows, Docker Desktop with WSL2 is required." -ForegroundColor White
    Write-Host "`nOptions to install Docker Desktop:" -ForegroundColor Cyan
    Write-Host "  1. Official Direct Download: https://www.docker.com/products/docker-desktop/" -ForegroundColor Green
    Write-Host "  2. Or run in PowerShell (as Administrator):" -ForegroundColor Green
    Write-Host "     wsl --install" -ForegroundColor White
    Write-Host "     winget install Docker.DockerDesktop" -ForegroundColor White
    Write-Host "`nAfter installing Docker Desktop, start it and re-run this script." -ForegroundColor Yellow
    exit 1
}

# 2. Check if Docker daemon is running
Write-Host "[*] Checking Docker daemon status..." -ForegroundColor Yellow
$dockerPing = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Docker Desktop is installed but not running. Please launch Docker Desktop and wait for the engine to start." -ForegroundColor Red
    exit 1
}

Write-Host "[+] Docker engine is running!" -ForegroundColor Green

# 3. Launch Frappe LMS Stack
Write-Host "[*] Launching Frappe LMS Multi-Container Cluster..." -ForegroundColor Cyan
docker compose -f $ComposeFile up -d

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host " Frappe LMS containers have been launched!" -ForegroundColor Green
Write-Host " Container status: docker compose -f docker\docker-compose.yml ps" -ForegroundColor White
Write-Host " To monitor bench initialization logs:" -ForegroundColor White
Write-Host "   docker logs -f lms-frappe-bench" -ForegroundColor Yellow
Write-Host "`n Once ready, access at: http://localhost:8000/lms" -ForegroundColor Cyan
Write-Host " To share over the internet with your friend:" -ForegroundColor Green
Write-Host "   powershell -File windows\share-tunnel.ps1" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Green
