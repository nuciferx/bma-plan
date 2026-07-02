import socket, sys, threading, time
from pathlib import Path
LITE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LITE))
import requests, uvicorn
from server_lite import app as lite_app

def free_port(start=8610):
    for p in range(start, start+80):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p

RAMA4 = r"F:\My Drive\01 project\ai\bma-plan\20250616_RAMA4 APARTMENT PERMIT rev 1.pdf"
port = free_port()
cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
server = uvicorn.Server(cfg)
threading.Thread(target=server.run, daemon=True).start()
time.sleep(2.0)
base = f"http://127.0.0.1:{port}"
with open(RAMA4,'rb') as fh:
    up = requests.post(base+"/upload", files={"file":("rama4.pdf", fh, "application/pdf")}, timeout=60)
cid = up.json()["case_id"]
print("upload:", up.status_code, "case_id ok:", bool(cid), "pages:", up.json().get("pages"))

# Full GET (baseline headers)
r_full = requests.get(base+f"/raw?case_id={cid}", timeout=30)
print("\n[FULL GET /raw]")
print("  status:", r_full.status_code)
print("  Accept-Ranges:", r_full.headers.get("Accept-Ranges"))
print("  Content-Length:", r_full.headers.get("Content-Length"))

# Range GET
r = requests.get(base+f"/raw?case_id={cid}", headers={"Range":"bytes=0-1023"}, timeout=30)
print("\n[RANGE GET /raw  bytes=0-1023]")
print("  status:", r.status_code, "(206=partial supported, 200=not)")
print("  Content-Range:", r.headers.get("Content-Range"))
print("  Accept-Ranges:", r.headers.get("Accept-Ranges"))
print("  Content-Length:", r.headers.get("Content-Length"))
print("  bytes returned:", len(r.content))

# Mid-file range (simulate xref tail fetch)
r2 = requests.get(base+f"/raw?case_id={cid}", headers={"Range":"bytes=1000000-1065535"}, timeout=30)
print("\n[RANGE GET /raw  bytes=1000000-1065535]")
print("  status:", r2.status_code, "Content-Range:", r2.headers.get("Content-Range"), "bytes:", len(r2.content))

server.should_exit = True
time.sleep(0.3)
