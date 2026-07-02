"""
PERF-20260702 thumbnail-warm guard.

After upload lands, PageRenderer.warmThumbs() fetches /thumb/1..N
SEQUENTIALLY (never a parallel burst — the lpm-8 lesson; and no concurrent
get_pixmap pressure on the shared fitz doc while the S2 per-case lock is
still queued) so the overview opens against a hot browser/server cache.
Token-cancelled by resetCache/new upload.

Checks (4-page PDF):
  C1 all-warmed  — every /thumb/n (n=1..4) requested exactly once.
  C2 sequential  — request timestamps strictly increasing with >=60 ms gaps
                   (proves not a parallel burst).
  C3 cancel      — a second warm run is cancelled by resetCache after the
                   first request (<4 additional requests).

RED pre-fix: warmThumbs does not exist.

Emits LITE_THUMB_WARM_OK on success.

    py -3 lite/tests/test_thumb_warm.py
"""
import socket
import sys
import threading
import time
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))

import fitz
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8890):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


def _make_pdf_bytes(pages=4, w=300, h=400):
    doc = fitz.open()
    for i in range(pages):
        pg = doc.new_page(width=w, height=h)
        pg.insert_text(fitz.Point(70, 200), f"TW {i+1}", fontsize=28)
    b = doc.tobytes()
    doc.close()
    return b


SC_THUMB_WARM = r"""
async () => {
  var thumbHits = [];
  var _origFetch = window.fetch;
  window.fetch = function(url, opts) {
    var u = String(url);
    var m = u.match(/\/thumb\/(\d+)/);
    if (m) thumbHits.push({n: +m[1], t: performance.now()});
    return _origFetch(url, opts);
  };

  var bytes = new Uint8Array(%PDF_BYTES%);
  var fd = new FormData();
  fd.append("file", new Blob([bytes], {type: "application/pdf"}), "tw-test.pdf");
  var up = await _origFetch("/upload", {method: "POST", body: fd});
  var uj = await up.json();
  caseId = uj.case_id; pageCount = uj.pages;

  // C1+C2: run a warm to completion
  await PageRenderer.warmThumbs();
  var firstRun = thumbHits.slice();
  var ns = firstRun.map(function(h){ return h.n; }).sort();
  var allWarmed = JSON.stringify(ns) === JSON.stringify([1,2,3,4]);
  var sequential = true;
  for (var i = 1; i < firstRun.length; i++) {
    if (firstRun[i].t - firstRun[i-1].t < 60) { sequential = false; break; }
  }

  // C3: cancel mid-run — start a warm, reset after the first request lands
  thumbHits.length = 0;
  var run2 = PageRenderer.warmThumbs();
  for (var j = 0; j < 40 && thumbHits.length === 0; j++) {
    await new Promise(function(r){ setTimeout(r, 25); });
  }
  var cid = caseId;
  PageRenderer.resetCache();          // bumps the warm token
  caseId = cid;                       // keep case valid; only the token cancels
  await run2;
  var cancelled = thumbHits.length < 4;

  window.fetch = _origFetch;
  return {
    firstRunCount: firstRun.length, ns, allWarmed, sequential,
    secondRunCount: thumbHits.length, cancelled,
    pass: allWarmed && sequential && cancelled
  };
}
"""


def main():
    from server_lite import app as lite_app
    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)

    pdf = _make_pdf_bytes()
    scenario = SC_THUMB_WARM.replace("%PDF_BYTES%", "[" + ",".join(str(b) for b in pdf) + "]")

    failures = []
    page_errors = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.on("pageerror", lambda e: page_errors.append(f"pageerror: {e}"))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(0.6)

        print()
        print("LITE-THUMB-WARM checks:")
        try:
            result = pg.evaluate(scenario)
            ok = result.get("pass") is True
            print(f"  sequentialWarmAndCancel             -> {'PASS' if ok else 'FAIL'}  {result}")
            if not ok:
                failures.append(f"result={result}")
        except Exception as ex:
            print(f"  sequentialWarmAndCancel             -> EXCEPTION: {ex}")
            failures.append(f"threw: {ex}")
        pg.close()
        b.close()

    for e in page_errors:
        print("  JS ERROR:", e)

    server.should_exit = True
    time.sleep(0.4)

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_THUMB_WARM_FAIL")
        sys.exit(1)
    print("LITE_THUMB_WARM_OK")


if __name__ == "__main__":
    main()
