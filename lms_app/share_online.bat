@echo off
title Share Midad Academy LMS Online
cd /d "%~dp0"

echo ==================================================================
echo         SHARE MIDAD ACADEMY LMS ONLINE (FOR OTHER ADMINS)
echo ==================================================================
echo [*] Checking local LMS server status...
powershell -Command "$p = Get-Process python -ErrorAction SilentlyContinue; if (!$p) { Write-Host '[*] Starting LMS Server in background...'; Start-Process python -ArgumentList 'app.py' -WindowStyle Minimized; Start-Sleep -Seconds 2 }"

set BIN_DIR=%~dp0bin
set CLOUDFLARED_EXE=%BIN_DIR%\cloudflared.exe

if exist "%CLOUDFLARED_EXE%" (
    echo [*] Starting Cloudflare Tunnel for http://localhost:8080...
    echo [*] Copy the public HTTPS URL (e.g. https://xxx.trycloudflare.com) and send it to other admins!
    echo ==================================================================
    "%CLOUDFLARED_EXE%" tunnel --url http://localhost:8080
    goto end
)

:loop
echo [*] Launching secure tunnel via SSH...
echo [*] Copy the public HTTPS URL (e.g. https://xxx.lhr.life) below and send it to other admins!
echo ==================================================================
ssh -R 80:127.0.0.1:8080 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 nokey@localhost.run
echo [!] Connection dropped or interrupted. Automatically reconnecting in 3 seconds...
timeout /t 3 /nobreak >nul
goto loop
