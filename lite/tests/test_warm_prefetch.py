"""
PERF-20260702 warm-up + adjacent-prefetch guard.

Warm-up: pdf.js library + worker boot cost a flat ~1.2 s on the first open;
page-renderer now preloads both at app idle (window.__pdfjsWarmed flag).

Prefetch: after loadPage(n) lands, the n±1 PDFPageProxy is fetched at idle so
the next page switch skips the worker getPage round-trip. Prefetched pages
count toward MAX_PAGE_CACHE (LRU bound must hold).

Checks (real 5-page PDF through the live app):
  C1 warm    — __pdfjsWarmed becomes true without any PDF opened.
  C2 prefetch— after loadPage(2) + idle, pageCache[1] and pageCache[3] exist
               without loadPage having been called for them.
  C3 bound   — LRU bound still holds (keys <= MAX_PAGE_CACHE).
  C4 switch  — loadPage(3) renders correctly (prefetched proxy reused).

RED pre-fix: no __pdfjsWarmed flag, no prefetch -> C1/C2 fail.

Emits LITE_WARM_PREFETCH_OK on success.

    py -3 lite/tests/test_warm_prefetch.py
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


def _free_port(start=8830):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


def _make_pdf_bytes(pages=5, w=300, h=400):
    doc = fitz.open()
    for i in range(pages):
        pg = doc.new_page(width=w, height=h)
        pg.insert_text(fitz.Point(70, 200), f"PF {i+1}", fontsize=28)
    b = doc.tobytes()
    doc.close()
    return b


SC_WARM_PREFETCH = r"""
async () => {
  // C1: warm-up flag (no PDF opened yet)
  var warmed = false;
  for (var i = 0; i < 100; i++) {                 // up to 5 s
    if (window.__pdfjsWarmed === true) { warmed = true; break; }
    await new Promise(function(r){ setTimeout(r, 50); });
  }

  // open a 5-page PDF via the direct-HTTP path (upload-first fallback flow)
  var bytes = new Uint8Array(%PDF_BYTES%);
  var fd = new FormData();
  fd.append("file", new Blob([bytes], {type: "application/pdf"}), "pf-test.pdf");
  var up = await fetch("/upload", {method: "POST", body: fd});
  if (!up.ok) return {pass: false, err: "upload " + up.status};
  var uj = await up.json();
  caseId = uj.case_id; pageCount = uj.pages;

  await PageRenderer.loadPage(2);
  // C2: wait for idle prefetch of pages 1 and 3
  var prefetched = false;
  for (var j = 0; j < 60; j++) {                  // up to 3 s
    if (pageCache[1] && pageCache[3]) { prefetched = true; break; }
    await new Promise(function(r){ setTimeout(r, 50); });
  }

  // C3: LRU bound still holds
  var boundOk = Object.keys(pageCache).length <= MAX_PAGE_CACHE &&
                _pageLru.length <= MAX_PAGE_CACHE;

  // C4: switching to the prefetched page works
  await PageRenderer.loadPage(3);
  await new Promise(function(r){ setTimeout(r, 400); });
  var switchOk = PageRenderer.ready() && curPage === 3;

  return {
    warmed, prefetched, boundOk, switchOk,
    keys: Object.keys(pageCache).length, MAX: MAX_PAGE_CACHE,
    pass: warmed && prefetched && boundOk && switchOk
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
    scenario = SC_WARM_PREFETCH.replace("%PDF_BYTES%", "[" + ",".join(str(b) for b in pdf) + "]")

    failures = []
    page_errors = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.on("pageerror", lambda e: page_errors.append(f"pageerror: {e}"))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(0.6)

        print()
        print("LITE-WARM-PREFETCH checks:")
        try:
            result = pg.evaluate(scenario)
            ok = result.get("pass") is True
            print(f"  warmupAndAdjacentPrefetch           -> {'PASS' if ok else 'FAIL'}  {result}")
            if not ok:
                failures.append(f"result={result}")
        except Exception as ex:
            print(f"  warmupAndAdjacentPrefetch           -> EXCEPTION: {ex}")
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
        print("LITE_WARM_PREFETCH_FAIL")
        sys.exit(1)
    print("LITE_WARM_PREFETCH_OK")


if __name__ == "__main__":
    main()
