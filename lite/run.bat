@echo off
REM ============================================================
REM  BMA-Plan Lite — one-click launcher (Windows).
REM  Double-click this file. It finds Python, installs the few
REM  dependencies if missing, starts the lite server, and opens
REM  your browser. Close this window (or Ctrl+C) to stop.
REM ============================================================
setlocal
cd /d "%~dp0"
title BMA-Plan Lite

REM --- pick a Python 3.11+ interpreter -------------------------
set "PY="
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if not defined PY (
  py -3 --version >nul 2>&1 && set "PY=py -3"
)
if not defined PY set "PY=python"

echo [BMA-Plan Lite] Python: %PY%
%PY% --version
if errorlevel 1 (
  echo.
  echo [!] Python 3.11+ not found. Install from https://www.python.org/downloads/
  echo     ^(tick "Add Python to PATH" during install^), then double-click this file again.
  pause
  exit /b 1
)

REM --- ensure dependencies ------------------------------------
%PY% -c "import fastapi,uvicorn,fitz,aiofiles,multipart" 2>nul
if errorlevel 1 (
  echo [BMA-Plan Lite] installing dependencies ^(one-time^)...
  %PY% -m pip install --quiet --disable-pip-version-check fastapi uvicorn aiofiles python-multipart pymupdf
  if errorlevel 1 (
    echo [!] dependency install failed. Check your internet connection and try again.
    pause
    exit /b 1
  )
)

REM --- launch (opens browser automatically) -------------------
echo [BMA-Plan Lite] starting... a browser tab will open shortly.
%PY% launch_lite.py
echo.
echo [BMA-Plan Lite] server stopped.
pause
