"""
PERF-20260702 page-cache LRU guard.

Problem: PDFPageProxy entries in page-renderer.js pageCache were kept forever
(~75 MB/page on a real 91 MB A1 binder -> 766 MB heap after visiting 10 of 95
pages; worker heap excluded, so true usage higher). Crash risk on customer
machines long before any speed concern.

Fix: MAX_PAGE_CACHE(=4) LRU — oldest evictable entry is dropped and its proxy
gets .cleanup() (releases operator lists/images; getPage() re-fetches on
revisit). curPage (and alias keys sharing its proxy) is never evicted because
a render may be in flight on it.

Checks (real 12-page PDF through the live app):
  C1 bound      — after visiting pages 1..12, pageCache keys and _pageLru
                  length are both <= MAX_PAGE_CACHE. RED pre-fix (was 12).
  C2 hot        — curPage (12) is still cached and PageRenderer.ready() true.
  C3 revisit    — loadPage(1) after eviction re-fetches: pageCache[1] present
                  again, ready() true, canvas paints non-blank.
  C4 reset      — resetCache() empties both structures.

Emits LITE_PAGECACHE_LRU_OK on success.

    py -3 lite/tests/test_pagecache_lru.py
"""
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
from playwright.sync_api import sync_playwright


def _free_port(start=8710):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


def _make_pdf_bytes(pages=12, w=300, h=400):
    doc = fitz.open()
    for i in range(pages):
        pg = doc.new_page(width=w, height=h)
        pg.insert_text(fitz.Point(80, 200), f"PAGE {i+1}", fontsize=30)
        sh = pg.new_shape()
        sh.draw_rect(fitz.Rect(20, 20, 280, 380))
        sh.finish(color=(0, 0, 0), width=2)
        sh.commit()
    b = doc.tobytes()
    doc.close()
    return b


SC_LRU = r"""
async () => {
  // upload a 12-page PDF through the app's own open path
  var bytes = new Uint8Array(%PDF_BYTES%);
  var fd = new FormData();
  fd.append("file", new Blob([bytes], {type: "application/pdf"}), "lru-test.pdf");
  var up = await fetch("/upload", {method: "POST", body: fd});
  if (!up.ok) return {pass: false, err: "upload " + up.status};
  var uj = await up.json();
  caseId = uj.case_id;
  pageCount = uj.pages;
  if (typeof PageRenderer === "undefined") return {pass: false, err: "no PageRenderer"};

  // visit pages 1..12 sequentially through the real loadPage path
  for (var n = 1; n <= 12; n++) {
    await PageRenderer.loadPage(n);
  }

  var keys1   = Object.keys(pageCache).length;
  var lru1    = _pageLru.length;
  var boundOk = keys1 <= MAX_PAGE_CACHE && lru1 <= MAX_PAGE_CACHE;

  var hotOk = !!pageCache[12] && PageRenderer.ready() === true && curPage === 12;

  // revisit an evicted page — must re-fetch and become ready again
  var evictedBefore = !pageCache[1];
  await PageRenderer.loadPage(1);
  await new Promise(function(r){ setTimeout(r, 400); });   // let the async render land
  var revisitOk = evictedBefore && !!pageCache[1] && PageRenderer.ready() === true && curPage === 1;

  // canvas should show content (non-uniform pixels) after revisit
  var painted = false;
  try {
    var c = document.getElementById("cv");
    var g = c.getContext("2d").getImageData(Math.floor(c.width/4), Math.floor(c.height/4),
                                            Math.floor(c.width/2), Math.floor(c.height/2)).data;
    var min = 255, max = 0;
    for (var i = 0; i < g.length; i += 4) { if (g[i] < min) min = g[i]; if (g[i] > max) max = g[i]; }
    painted = (max - min) > 20;
  } catch (e) { painted = false; }

  PageRenderer.resetCache();
  var resetOk = Object.keys(pageCache).length === 0 && _pageLru.length === 0;

  return {
    keys1, lru1, MAX: MAX_PAGE_CACHE, evictedBefore,
    boundOk, hotOk, revisitOk, painted, resetOk,
    pass: boundOk && hotOk && revisitOk && painted && resetOk
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
    scenario = SC_LRU.replace("%PDF_BYTES%", "[" + ",".join(str(b) for b in pdf) + "]")

    failures = []
    page_errors = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.on("pageerror", lambda e: page_errors.append(f"pageerror: {e}"))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(0.6)

        print()
        print("LITE-PAGECACHE-LRU checks:")
        try:
            result = pg.evaluate(scenario)
            ok = result.get("pass") is True
            print(f"  lruBoundAndRevisit                  -> {'PASS' if ok else 'FAIL'}  {result}")
            if not ok:
                failures.append(f"result={result}")
        except Exception as ex:
            print(f"  lruBoundAndRevisit                  -> EXCEPTION: {ex}")
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
        print("LITE_PAGECACHE_LRU_FAIL")
        sys.exit(1)
    print("LITE_PAGECACHE_LRU_OK")


if __name__ == "__main__":
    main()
