@echo off
setlocal
:: Spike build — BMA-Plan Lite one-file exe (Artifact A)
:: workpath goes to local %TEMP% (Google Drive is too slow for the build churn);
:: only the final exe lands in dist\ here.
cd /d "%~dp0"
python -m PyInstaller spike_onefile.spec --noconfirm --distpath "%~dp0dist" --workpath "%TEMP%\bma_lite_build_a"
if exist "%~dp0dist\BMA-Plan-Lite-A.exe" (
    echo BUILD OK: dist\BMA-Plan-Lite-A.exe
) else (
    echo BUILD FAILED
    exit /b 1
)
