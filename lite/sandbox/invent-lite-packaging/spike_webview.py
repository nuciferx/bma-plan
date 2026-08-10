"""Side-check E: does a WebView2 window open on the lite URL on this machine?
uvicorn (lite server) in a thread + webview.create_window. Auto-closes ~8s in
so automation never hangs. Run: python spike_webview.py
"""
import sys
import threading
from pathlib import Path

import uvicorn
import webview

LITE = Path(__file__).resolve().parents[2]  # -> <repo>/lite
PORT = 8177

def serve():
    uvicorn.run("server_lite:app", host="127.0.0.1", port=PORT, app_dir=str(LITE))

threading.Thread(target=serve, daemon=True).start()

win = webview.create_window("BMA-Plan Lite (webview spike)",
                            f"http://127.0.0.1:{PORT}/", width=1280, height=800)

def close_soon():
    print("WEBVIEW_SHOWN", flush=True)   # reached only after GUI loop started
    threading.Timer(8.0, win.destroy).start()

webview.start(close_soon, gui="edgechromium")
print("WEBVIEW_EXITED_CLEANLY", flush=True)
