"""
Spike wrapper entry for PyInstaller one-file build of BMA-Plan Lite (Artifact A).

Why this exists (instead of using lite/launch_lite.py directly):
  lite/launch_lite.py resolves app_dir via Path(__file__).resolve().parent.
  Under a PyInstaller one-file exe the entry script runs from the bootloader
  with __file__ pointing inside sys._MEIPASS, and server_lite.py itself is
  bundled as a *data* file (not a frozen module) so uvicorn's import-string
  form can import it from disk. This wrapper re-implements the same launch
  logic (identical port selection, identical uvicorn call) but resolves the
  lite/ directory correctly in both frozen and non-frozen runs.

  lite/launch_lite.py is NOT modified (hard rule).

Extras over the original:
  - BMA_LITE_NO_BROWSER=1 suppresses webbrowser.open (original has no flag;
    needed for automated eval).
"""
import os
import socket
import sys
import threading
import webbrowser
from pathlib import Path

import uvicorn


def _lite_dir() -> Path:
    if getattr(sys, "frozen", False):
        # one-file: datas extracted to sys._MEIPASS/lite/
        return Path(sys._MEIPASS) / "lite"
    # dev run from the sandbox: lite/sandbox/invent-lite-packaging -> lite/
    return Path(__file__).resolve().parents[2]


def _free_port(start=8100, tries=50):
    # identical to lite/launch_lite.py
    for p in range(start, start + tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port found")


def main():
    lite = _lite_dir()
    port = _free_port()
    url = f"http://127.0.0.1:{port}/"
    print(f"[lite] BMA-Plan Lite (packaged A) -> {url}", flush=True)
    if os.environ.get("BMA_LITE_NO_BROWSER") != "1":
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    uvicorn.run("server_lite:app", host="127.0.0.1", port=port, app_dir=str(lite))


if __name__ == "__main__":
    main()
