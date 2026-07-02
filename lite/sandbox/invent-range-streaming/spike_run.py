#!/usr/bin/env python3
"""
Range-streaming spike driver (S3 + S4 + S5).

Boots lite/server_lite.py (READ-ONLY import), adds a runtime-only /spike route
(no file edit), uploads a target PDF, then drives spike.html with Playwright:

  Scenario A  baseline  getDocument({data: fullBuffer})
  Scenario B  streaming getDocument({url, disableAutoFetch, disableStream, rangeChunkSize})
  Scenario T  transport PDFDataRangeTransport over Blob.slice (local-first, S4)

Metrics per scenario:
  - openMs, ttfr (time-to-first-render, page 1)
  - main-thread JS heap after each page (performance.memory)
  - renderer-process RSS (psutil, sum over chromium procs matching our
    user-data-dir) — this INCLUDES the worker heap = the real #10730 target
  - bytes actually transferred over /raw (Playwright requestfinished sizes)
  - heap/RSS after doc.destroy() (#10730 check)

Usage:  py -3 spike_run.py            # RAMA4 then CHH
        py -3 spike_run.py rama4      # just RAMA4
"""
import json, socket, sys, threading, time, uuid, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
LITE = HERE.parents[1]           # .../bma-plan/lite
ROOT = LITE.parent               # .../bma-plan
sys.path.insert(0, str(LITE))

import psutil, requests, uvicorn
from fastapi.responses import FileResponse
from server_lite import app as lite_app
from playwright.sync_api import sync_playwright

RAMA4 = ROOT / "20250616_RAMA4 APARTMENT PERMIT rev 1.pdf"
CHH   = ROOT / "sandbox" / "251121_CHH_Submission_REV2 - Copy.pdf"
SPIKE_HTML = HERE / "spike.html"
NPAGES = 10

# ---- runtime-only route (does NOT edit server_lite.py) --------------------
@lite_app.get("/spike")
def _spike():
    return FileResponse(str(SPIKE_HTML), media_type="text/html")


def free_port(start=8630):
    for p in range(start, start + 80):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p


def _root_pids(udd_token):
    roots = []
    for pr in psutil.process_iter(["cmdline"]):
        try:
            cl = pr.info.get("cmdline") or []
            if any(udd_token in str(a) for a in cl):
                roots.append(pr)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return roots


def rss_mb(udd_token):
    """Sum RSS (MB) of the whole Chromium process tree for our user-data-dir:
    root browser proc + ALL descendants (renderer, GPU, utility). The pdf.js
    worker is a thread inside the renderer process, so renderer RSS captures the
    #10730 worker heap — the real target of this spike."""
    seen = {}
    for root in _root_pids(udd_token):
        procs = [root] + root.children(recursive=True)
        for pr in procs:
            try:
                seen[pr.pid] = pr.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    return round(sum(seen.values()) / 1e6)


def upload(base, pdf_path):
    with open(pdf_path, "rb") as fh:
        up = requests.post(base + "/upload",
                           files={"file": (pdf_path.name, fh, "application/pdf")},
                           timeout=120)
    up.raise_for_status()
    return up.json()["case_id"]


def run_pdf(page, base, udd, label, pdf_path):
    print(f"\n===== {label}  ({pdf_path.name}) =====")
    case_id = upload(base, pdf_path)
    raw_url = f"{base}/raw?case_id={case_id}"
    res = {"file": pdf_path.name, "size_mb": round(pdf_path.stat().st_size / 1e6, 1)}

    # byte counter for /raw
    counter = {"bytes": 0, "reqs": 0}
    def on_finished(req):
        if "/raw" in req.url:
            try:
                sz = req.sizes().get("responseBodySize", 0)
            except Exception:
                sz = 0
            counter["bytes"] += sz
            counter["reqs"] += 1
    page.on("requestfinished", on_finished)

    page.goto(base + "/spike", wait_until="load")
    page.wait_for_function("window.__ready === true", timeout=15000)
    page.evaluate("window.loadLib()")
    res["baseline_rss_mb"] = rss_mb(udd)

    # ---- Scenario A (baseline, {data: buf}) ----
    counter["bytes"] = 0; counter["reqs"] = 0
    fetched = page.evaluate("(u) => window.fetchFull(u)", raw_url)
    a = page.evaluate("(n) => window.scenarioA(n)", NPAGES)
    a["rss_after_pages_mb"] = rss_mb(udd)
    a["bytes_transferred"] = counter["bytes"]
    a["raw_reqs"] = counter["reqs"]
    d = page.evaluate("window.destroyDoc()")
    a["rss_after_destroy_mb"] = rss_mb(udd)
    a["heap_after_destroy_mb"] = d["heapMB"]
    res["A_baseline"] = a
    res["fetchFull_bytes"] = fetched["bytes"]

    # fresh page to isolate B from A leftovers
    page.close()
    page = page.context.new_page()
    page.on("requestfinished", on_finished)
    page.goto(base + "/spike", wait_until="load")
    page.wait_for_function("window.__ready === true", timeout=15000)
    page.evaluate("window.loadLib()")

    # ---- Scenario B (streaming, {url,...}) ----
    counter["bytes"] = 0; counter["reqs"] = 0
    b = page.evaluate("(a) => window.scenarioB(a[0], a[1])", [raw_url, NPAGES])
    b["rss_after_pages_mb"] = rss_mb(udd)
    b["bytes_transferred"] = counter["bytes"]
    b["raw_reqs"] = counter["reqs"]
    d = page.evaluate("window.destroyDoc()")
    b["rss_after_destroy_mb"] = rss_mb(udd)
    b["heap_after_destroy_mb"] = d["heapMB"]
    res["B_streaming"] = b

    # fresh page for transport (S4)
    page.close()
    page = page.context.new_page()
    page.on("requestfinished", on_finished)
    page.goto(base + "/spike", wait_until="load")
    page.wait_for_function("window.__ready === true", timeout=15000)
    page.evaluate("window.loadLib()")

    # ---- Scenario T (transport, S4) ----
    counter["bytes"] = 0; counter["reqs"] = 0
    page.evaluate("(u) => window.fetchFull(u)", raw_url)  # local File source
    counter["bytes"] = 0; counter["reqs"] = 0  # reset — transport must NOT hit /raw
    t = page.evaluate("(n) => window.scenarioTransport(n)", NPAGES)
    if t.get("opened"):
        t["rss_after_pages_mb"] = rss_mb(udd)
        t["raw_reqs_during"] = counter["reqs"]  # should be 0 (served locally)
        d = page.evaluate("window.destroyDoc()")
        t["rss_after_destroy_mb"] = rss_mb(udd)
        t["heap_after_destroy_mb"] = d["heapMB"]
    res["T_transport"] = t

    page.close()
    return res, page.context


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    targets = []
    if which in ("both", "rama4") and RAMA4.exists():
        targets.append(("RAMA4 19MB", RAMA4))
    if which in ("both", "chh") and CHH.exists():
        targets.append(("CHH 95MB", CHH))
    if not targets:
        print("no target PDFs found"); sys.exit(1)

    port = free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)
    base = f"http://127.0.0.1:{port}"

    udd = tempfile.mkdtemp(prefix="spike_udd_")
    token = "spike_udd_" + Path(udd).name.split("spike_udd_")[-1]
    results = []
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            udd, headless=True,
            args=["--enable-precise-memory-info",
                  "--js-flags=--expose-gc",
                  "--disable-dev-shm-usage"])
        page = ctx.new_page()
        for label, path in targets:
            try:
                res, ctx = run_pdf(page, base, token, label, path)
                results.append(res)
                print(json.dumps(res, indent=2))
            except Exception as e:
                import traceback; traceback.print_exc()
                results.append({"file": path.name, "error": str(e)})
            page = ctx.new_page()
        ctx.close()

    server.should_exit = True
    time.sleep(0.3)
    out = HERE / "results.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("\nwrote", out)


if __name__ == "__main__":
    main()
