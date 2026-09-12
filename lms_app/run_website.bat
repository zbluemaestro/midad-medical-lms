@echo off
title Pulse Academy LMS Server
cd /d "%~dp0"

echo ==================================================================
echo               PULSE ACADEMY LMS - LOCAL LAUNCHER
echo ==================================================================
echo [*] Starting Python Flask LMS Server...
echo [*] URL: http://localhost:8080
echo [*] Master Super Admin: admin@lms.local (Password: AdminPass2026!)
echo [*] Press Ctrl+C in this window to stop the server.
echo ==================================================================
python app.py
pause
