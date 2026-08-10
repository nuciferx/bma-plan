@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: BMA-Plan Lite - Portable Build (produces lite\dist-portable\BMA-Plan-Lite\)
:: ============================================================================
:: Ships Artifact B from the lite-zero-install-packaging invent spike
:: (docs\invent\lite-zero-install-packaging.md, GO 2026-08-10): an embeddable
:: Python 3.11.9 + installed site-packages + a verbatim copy of the lite
:: runtime + a run.bat launcher. The result folder needs ZERO Python / pip /
:: internet on the TARGET machine - copy the folder and double-click run.bat.
:: (Building it here still needs internet the first time, to install deps.)
::
:: IDEMPOTENCY: this script always wipes and rebuilds the output folder
:: (dist-portable\BMA-Plan-Lite) from scratch on every run. Re-running is
:: therefore safe but NOT incremental - every run reinstalls dependencies.
:: This matches the proven spike recipe (SPIKE_RESULTS.md) and avoids stale
:: site-packages after a dependency bump. For a faster incremental rebuild
:: while iterating, delete only the "lite\" subfolder inside the output dir
:: and re-run - python-embed + site-packages will be reused as-is.
::
:: Usage:   lite\build_portable.bat
:: Reuses the cached python-3.11.9-embed-amd64.zip and get-pip.py already in
:: lite\sandbox\invent-lite-packaging\ (from the spike) if present; otherwise
:: downloads them with curl.
:: ============================================================================

set "SCRIPT_DIR=%~dp0"
set "SANDBOX_DIR=%SCRIPT_DIR%sandbox\invent-lite-packaging"
set "OUT_ROOT=%SCRIPT_DIR%dist-portable"
set "OUT_DIR=%OUT_ROOT%\BMA-Plan-Lite"
set "EMBED_ZIP=python-3.11.9-embed-amd64.zip"
set "EMBED_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
set "GETPIP_URL=https://bootstrap.pypa.io/get-pip.py"

if not exist "%SCRIPT_DIR%server_lite.py" (
    echo [build_portable] ERROR: run this script from inside lite\ - server_lite.py not found next to it.
    exit /b 1
)

echo [build_portable] Output: %OUT_DIR%

if exist "%OUT_DIR%" (
    echo [build_portable] Removing previous build...
    rmdir /s /q "%OUT_DIR%"
)
mkdir "%OUT_DIR%\python-embed" || goto :error

:: --- 1. Get embeddable Python zip (reuse cached spike copy if present) ---
set "ZIP_SRC=%SANDBOX_DIR%\%EMBED_ZIP%"
if exist "%ZIP_SRC%" (
    echo [build_portable] Reusing cached embed zip: %ZIP_SRC%
) else (
    echo [build_portable] Cached embed zip not found - downloading...
    set "ZIP_SRC=%TEMP%\%EMBED_ZIP%"
    curl -L -o "!ZIP_SRC!" "%EMBED_URL%" || goto :error
)

echo [build_portable] Extracting embeddable Python...
powershell -NoProfile -Command "Expand-Archive -LiteralPath '%ZIP_SRC%' -DestinationPath '%OUT_DIR%\python-embed' -Force" || goto :error

:: --- 2. Enable site-packages in the embeddable interpreter ---
echo [build_portable] Enabling site-packages (python311._pth)...
(
echo python311.zip
echo .
echo Lib\site-packages
echo import site
) > "%OUT_DIR%\python-embed\python311._pth"

:: --- 3. Bootstrap pip inside the embedded interpreter ---
set "GETPIP_SRC=%SANDBOX_DIR%\get-pip.py"
if not exist "%GETPIP_SRC%" (
    echo [build_portable] get-pip.py not found in sandbox - downloading...
    set "GETPIP_SRC=%TEMP%\get-pip.py"
    curl -L -o "!GETPIP_SRC!" "%GETPIP_URL%" || goto :error
)
echo [build_portable] Bootstrapping pip...
"%OUT_DIR%\python-embed\python.exe" "%GETPIP_SRC%" --no-warn-script-location || goto :error

:: --- 4. Install runtime dependencies ---
echo [build_portable] Installing dependencies (fastapi uvicorn aiofiles python-multipart pymupdf openpyxl)...
"%OUT_DIR%\python-embed\python.exe" -m pip install --no-warn-script-location fastapi uvicorn aiofiles python-multipart pymupdf openpyxl || goto :error

:: --- 5. Copy the lite runtime (verbatim, no modification) ---
echo [build_portable] Copying lite runtime files...
mkdir "%OUT_DIR%\lite" || goto :error
copy /y "%SCRIPT_DIR%server_lite.py" "%OUT_DIR%\lite\" >nul || goto :error
copy /y "%SCRIPT_DIR%launch_lite.py" "%OUT_DIR%\lite\" >nul || goto :error
copy /y "%SCRIPT_DIR%ui-lite.html" "%OUT_DIR%\lite\" >nul || goto :error
copy /y "%SCRIPT_DIR%lite-report.html" "%OUT_DIR%\lite\" >nul || goto :error
xcopy /e /i /y "%SCRIPT_DIR%static" "%OUT_DIR%\lite\static\" >nul || goto :error

:: --- 6. Write run.bat (CRLF; sets BMA_LITE_NO_BROWSER only if caller wants it) ---
(
echo @echo off
echo setlocal
echo :: BMA-Plan Lite - portable launcher ^(Artifact B^).
echo :: Uses the embedded Python next to this file; no system Python needed.
echo :: PYTHONHOME/PYTHONPATH cleared so a machine-level Python cannot interfere.
echo set "PYTHONHOME="
echo set "PYTHONPATH="
echo "%%~dp0python-embed\python.exe" "%%~dp0lite\launch_lite.py"
) > "%OUT_DIR%\run.bat"

echo.
echo [build_portable] DONE. Portable build at: %OUT_DIR%
echo [build_portable] To run: double-click %OUT_DIR%\run.bat
echo [build_portable] To skip the auto-opened browser: set BMA_LITE_NO_BROWSER=1 first.
exit /b 0

:error
echo [build_portable] FAILED (see errors above).
exit /b 1
