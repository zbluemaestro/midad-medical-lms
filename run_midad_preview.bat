@echo off
title Midad Medical LMS - Preview Server
echo ==========================================================
echo    Starting Midad Medical LMS Preview Server...
echo ==========================================================
cd /d "%~dp0"
start http://localhost:8080
python preview_server\server.py
pause
