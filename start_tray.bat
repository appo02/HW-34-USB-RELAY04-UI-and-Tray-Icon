@echo off
REM ─── Start USB-RELAY04 tray control (notification area) ───
REM Runs hidden (no console window) via pythonw.
REM If pythonw is not available, falls back to python.

cd /d "%~dp0"

where pythonw >nul 2>&1
if %ERRORLEVEL% equ 0 (
    start "" pythonw relay_tray.py
) else (
    start "" python relay_tray.py
)
