@echo off
title Share LMS Online - Cloudflare Tunnel
cd /d "%~dp0"

echo ==================================================================
echo         SHARE LMS ONLINE (FREE PUBLIC HTTPS LINK)
echo ==================================================================

set BIN_DIR=%~dp0bin
set CLOUDFLARED_EXE=%BIN_DIR%\cloudflared.exe

if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"

if not exist "%CLOUDFLARED_EXE%" (
    echo [*] Downloading official standalone Cloudflare Tunnel engine...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile '%CLOUDFLARED_EXE%'"
    echo [+] Download complete.
)

echo [*] Starting Cloudflare Tunnel for http://localhost:8080...
echo [*] Copy the public HTTPS URL (e.g. https://xxx.trycloudflare.com) generated below and send it to your friend!
echo ==================================================================

"%CLOUDFLARED_EXE%" tunnel --url http://localhost:8080
pause
