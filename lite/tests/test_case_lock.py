"""
AUDIT-20260702-s2-fitz-lock guard.

PyMuPDF Documents are not thread-safe. /page and /thumb are sync `def`
(Starlette threadpools them) and the client thumb-warm makes concurrent
/thumb + /page routine; /apply-page-mutations closes and swaps case["doc"]
mid-flight. Without serialization, concurrent get_pixmap on the same doc —
or a swap during a render — can corrupt/crash the MuPDF C layer.

Fix: per-case threading.Lock (_case_lock) held around every fitz touch:
/page + /thumb render blocks (double-checked cache), /pageinfo, the whole
/export-pdf-overlay render (now also off the event loop via
run_in_threadpool), and the copy/close/swap critical sections of
/apply-page-mutations + /merge-pages.

Checks (12-page PDF):
  C1 hammer   — 8 threads x 24 mixed /page + /thumb requests: all 200,
                every body a valid JPEG (FFD8 magic), zero 5xx.
  C2 swap     — /apply-page-mutations (reverse order) fired WHILE the hammer
                runs: mutation 200 + renders keep returning 200/valid after.
  C3 overlay  — /export-pdf-overlay concurrent with renders: valid %PDF.
  NOTE: the pre-fix failure is a probabilistic native-layer race — a reliable
  RED proof is not achievable from HTTP; this is a hardening hammer, honest
  per DEVELOPMENT_PILLARS เสา 6.

Emits LITE_CASE_LOCK_OK on success.

    py -3 lite/tests/test_case_lock.py
"""
import concurrent.futures
import socket
import sys
import threading
import time
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))

import fitz
import requests
import uvicorn


def _free_port(start=8950):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


def _make_pdf_bytes(pages=12, w=300, h=400):
    doc = fitz.open()
    for i in range(pages):
        pg = doc.new_page(width=w, height=h)
        pg.insert_text(fitz.Point(70, 200), f"LK {i+1}", fontsize=28)
    b = doc.tobytes()
    doc.close()
    return b


failures = []


def check(label, cond, detail=""):
    if cond:
        print(f"  PASS {label}")
    else:
        msg = f"FAIL {label}" + (f": {detail}" if detail else "")
        failures.append(msg)
        print(f"  {msg}")


def main():
    from server_lite import app as lite_app
    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)
    base = f"http://127.0.0.1:{port}"

    up = requests.post(base + "/upload",
                       files={"file": ("lk.pdf", _make_pdf_bytes(), "application/pdf")},
                       timeout=30)
    cid = up.json().get("case_id")
    check("setup upload 200 + case_id", up.status_code == 200 and bool(cid))

    bad = []

    def hit(i):
        n = (i % 12) + 1
        url = (base + f"/thumb/{n}?case_id={cid}") if i % 2 else \
              (base + f"/page/{n}?case_id={cid}")
        try:
            r = requests.get(url, timeout=30)
            if r.status_code != 200 or r.content[:2] != b"\xff\xd8":
                bad.append((url, r.status_code, r.content[:4]))
        except Exception as ex:
            bad.append((url, "EXC", str(ex)[:80]))

    # C1+C2: hammer renders while a doc swap fires mid-flight
    mut_result = {}

    def mutate():
        time.sleep(0.15)   # let the hammer get going first
        try:
            r = requests.post(base + "/apply-page-mutations",
                              json={"case_id": cid, "order": list(range(12, 0, -1))},
                              timeout=60)
            mut_result["status"] = r.status_code
            mut_result["ok"] = r.json().get("ok")
        except Exception as ex:
            mut_result["status"] = f"EXC {ex}"

    mt = threading.Thread(target=mutate)
    mt.start()
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(hit, range(96)))
    mt.join()

    check("C1 96 concurrent renders all valid JPEG", len(bad) == 0, str(bad[:3]))
    check("C2 mutation during hammer 200+ok",
          mut_result.get("status") == 200 and mut_result.get("ok") is True, str(mut_result))

    # renders still healthy after the swap
    bad.clear()
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(hit, range(48)))
    check("C2b post-swap renders all valid", len(bad) == 0, str(bad[:3]))

    # C3: overlay export concurrent with renders
    ov_result = {}

    def overlay():
        try:
            r = requests.post(base + "/export-pdf-overlay",
                              json={"case_id": cid, "pages": {"1": {
                                  "objects": [{"kind": "poly", "counting": False,
                                               "pts": [{"x": 10, "y": 10}, {"x": 60, "y": 10},
                                                       {"x": 60, "y": 60}, {"x": 10, "y": 60}],
                                               "color": "#f00", "label": "L 1.00 m2"}],
                                  "annotations": []}}},
                              timeout=60)
            ov_result["status"] = r.status_code
            ov_result["pdf"] = r.content[:4] == b"%PDF"
        except Exception as ex:
            ov_result["status"] = f"EXC {ex}"

    ot = threading.Thread(target=overlay)
    ot.start()
    bad.clear()
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(hit, range(48)))
    ot.join()
    check("C3 overlay during hammer -> valid %PDF",
          ov_result.get("status") == 200 and ov_result.get("pdf") is True, str(ov_result))
    check("C3b renders during overlay all valid", len(bad) == 0, str(bad[:3]))

    server.should_exit = True
    time.sleep(0.4)

    if failures:
        print()
        for f in failures:
            print("FAIL:", f)
        print("LITE_CASE_LOCK_FAIL")
        sys.exit(1)
    print()
    print("LITE_CASE_LOCK_OK")


if __name__ == "__main__":
    main()
