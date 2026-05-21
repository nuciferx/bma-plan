"""
BMA-Plan Lite — launcher. Picks a free port starting at 8100 (proto uses 8000+),
starts uvicorn on lite's app, and opens the browser. Mirror of proto/launch.py
but for the standalone lite tree.

    python lite/launch_lite.py
"""
import socket
import threading
import webbrowser

import uvicorn


def _free_port(start=8100, tries=50):
    for p in range(start, start + tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port found")


def main():
    port = _free_port()
    url = f"http://127.0.0.1:{port}/"
    print(f"[lite] BMA-Plan Lite -> {url}")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    # import string form so uvicorn can run from this file directly
    uvicorn.run("server_lite:app", host="127.0.0.1", port=port, app_dir=str(__import__("pathlib").Path(__file__).resolve().parent))


if __name__ == "__main__":
    main()
