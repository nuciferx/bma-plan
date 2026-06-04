#!/bin/bash
# ============================================================
#  BMA-Plan Lite — one-click launcher (macOS).
#  Double-click this file from Finder. It finds Python 3.11+,
#  installs the few dependencies if missing, starts the lite
#  server, and opens your browser. Close the Terminal window
#  (or Ctrl+C) to stop.
#
#  First-time setup (one command in Terminal):
#      chmod +x "$(dirname "$0")/run.command"
# ============================================================
set -e
cd "$(dirname "$0")"

echo "[BMA-Plan Lite] locating Python 3.11+..."

PY=""
for candidate in python3.12 python3.11 python3; do
  if command -v "$candidate" >/dev/null 2>&1; then
    ver=$("$candidate" -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || echo "0.0")
    major=${ver%.*}
    minor=${ver#*.}
    if [ "$major" = "3" ] && [ "$minor" -ge 11 ] 2>/dev/null; then
      PY="$candidate"
      break
    fi
  fi
done

if [ -z "$PY" ]; then
  echo
  echo "[!] Python 3.11+ not found."
  echo "    Install with one of:"
  echo "      brew install python@3.12"
  echo "      or download from https://www.python.org/downloads/"
  echo "    Then double-click this file again."
  echo
  read -r -p "Press Enter to close..." _
  exit 1
fi

echo "[BMA-Plan Lite] Python: $PY ($("$PY" --version))"

# --- ensure dependencies ------------------------------------
if ! "$PY" -c "import fastapi, uvicorn, fitz, aiofiles, multipart, openpyxl" >/dev/null 2>&1; then
  echo "[BMA-Plan Lite] installing dependencies (one-time)..."
  if ! "$PY" -m pip install --quiet --disable-pip-version-check \
      fastapi uvicorn aiofiles python-multipart pymupdf openpyxl; then
    echo "[!] dependency install failed. Check your internet connection and try again."
    read -r -p "Press Enter to close..." _
    exit 1
  fi
fi

# --- launch (opens browser automatically) -------------------
echo "[BMA-Plan Lite] starting... a browser tab will open shortly."
"$PY" launch_lite.py
echo
echo "[BMA-Plan Lite] server stopped."
read -r -p "Press Enter to close..." _
