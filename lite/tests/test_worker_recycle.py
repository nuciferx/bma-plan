"""
PERF-20260703 pdf.js worker-recycle guard.

Problem (spike-proven, docs/invent/lite-range-streaming.md + artifacts in
lite/sandbox/invent-range-streaming/results.md, 2026-07-03): the pdf.js
worker heap holds ~1.5 GB RSS on a 95 MB customer binder. pdfDoc.destroy()
frees the MAIN-THREAD heap only — pdf.js bug #10730 confirmed on 4.0.379:
the worker thread's commonObjs/render heap survives destroy(). Only
terminating the worker itself reclaims it. Range-streaming was spiked as an
alternative and rejected (-10% RSS vs the -50% GO bar).

Fix: page-renderer.js now owns an EXPLICIT pdf.js PDFWorker (`_docWorker`)
per document and can tear both down via recycleDocWorker() — triggered by
idle (>=5 min, pageCount>20) or tab-hidden (>=60 s), or manually via
PageRenderer.recycleNow(). A cheap re-open handle (`_docSource`) is retained
WITHOUT keeping the big buffer resident: the original File/Blob for the
local-first path (zero-network reinit) or just the caseId for the /raw path.
loadPage() lazily reinitializes transparently on the next page visit.

Checks (real 12-page PDF through the real uploadPdf() local-first path, so
_docSource is the retained File blob):
  C1 docSource   — _docSource.kind === "blob" after local-first open.
  C2 guard       — recycleNow() returns false (no-op) while a render is
                   simulated in flight (_pendingRenderTask set); pdfDoc stays
                   non-null. Documented behavior: SKIPPED, not deferred —
                   caller may retry; recycle never interrupts a live render.
  C3 torn down   — after a real recycleNow(): pdfDoc === null AND
                   Object.keys(pageCache).length === 0.
  C4 reinit      — loadPage(3) after recycle is transparent: ready() true,
                   curPage === 3, canvas painted.
  C5 zero refetch— zero "/raw" fetches happen for the whole recycle+reinit
                   cycle (the retained File blob is reused — the whole point
                   of local-first).
  C6 metadata    — pageRot[3], _scanned, and pageDims survive the recycle
                   byte-for-byte (cheap metadata is deliberately NOT cleared).
  C7 heap smoke  — performance.memory.usedJSHeapSize does not INCREASE more
                   than 10% across recycle (honest: this is MAIN-THREAD heap
                   only; the real ~50% RSS reduction needs the full worker
                   process tree and was measured by the spike's psutil
                   harness, not available here — this is a "did we make it
                   worse" regression guard, not a re-run of the spike).

RED pre-fix: PageRenderer.recycleNow is undefined -> evaluate throws.

Emits LITE_WORKER_RECYCLE_OK on success.

    py -3 lite/tests/test_worker_recycle.py
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


def _free_port(start=9070):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


def _make_pdf_bytes(pages=12, w=300, h=400):
    doc = fitz.open()
    for i in range(pages):
        pg = doc.new_page(width=w, height=h)
        pg.insert_text(fitz.Point(70, 200), f"RECYCLE {i+1}", fontsize=26)
        sh = pg.new_shape()
        sh.draw_rect(fitz.Rect(20, 20, 280, 380))
        sh.finish(color=(0, 0, 0), width=2)
        sh.commit()
    b = doc.tobytes()
    doc.close()
    return b


SC_RECYCLE = r"""
async () => {
  function painted() {
    try {
      var c = document.getElementById("cv");
      var g = c.getContext("2d").getImageData(Math.floor(c.width/4), Math.floor(c.height/4),
                                              Math.floor(c.width/2), Math.floor(c.height/2)).data;
      var mn = 255, mx = 0;
      for (var i = 0; i < g.length; i += 4) { if (g[i] < mn) mn = g[i]; if (g[i] > mx) mx = g[i]; }
      return (mx - mn) > 20;
    } catch (e) { return false; }
  }

  var rawFetches = 0;
  var _origFetch = window.fetch;
  window.fetch = function(url, opts) {
    var u = String(url);
    if (u.indexOf("/raw") >= 0) rawFetches++;
    return _origFetch(url, opts);
  };

  // real local-first open path -> openLocal(buf, file) -> _docSource kind "blob"
  var bytes = new Uint8Array(%PDF_BYTES%);
  var file = new File([bytes], "recycle-test.pdf", {type: "application/pdf"});
  await uploadPdf(file);
  await new Promise(function(r){ setTimeout(r, 400); });   // let background upload/adopt land

  // visit pages 1..6
  for (var n = 1; n <= 6; n++) {
    await PageRenderer.loadPage(n);
    await new Promise(function(r){ setTimeout(r, 200); });
  }
  await PageRenderer.loadPage(3);
  await new Promise(function(r){ setTimeout(r, 300); });

  // let scanned-detection settle on the visited pages (best-effort, not required)
  for (var w = 0; w < 20; w++) {
    if (_scanned[1] !== undefined && _scanned[1] !== null) break;
    await new Promise(function(r){ setTimeout(r, 100); });
  }

  pageRot[3] = 90;                                 // metadata to check survives recycle
  var scannedBefore   = JSON.stringify(_scanned);
  var pageDimsBefore  = JSON.stringify(pageDims);
  var docSourceKind   = _docSource ? _docSource.kind : null;   // C1: expect "blob"

  if (window.gc) { try { window.gc(); } catch (e) {} }
  var heapBefore = (performance.memory && performance.memory.usedJSHeapSize) || null;

  // ---- C2: recycle must be a no-op while a render is (simulated) in flight ----
  _pendingRenderTask = { _fakeInFlight: true };
  var skippedResult = await PageRenderer.recycleNow();
  var skippedOk = (skippedResult === false) && (pdfDoc !== null);
  _pendingRenderTask = null;

  // ---- real recycle ----
  var rawFetchesBeforeRecycle = rawFetches;
  var recycleResult = await PageRenderer.recycleNow();

  // C3: torn down
  var afterRecyclePdfDocNull      = (pdfDoc === null);
  var afterRecyclePageCacheEmpty  = (Object.keys(pageCache).length === 0);

  // C6: metadata survived
  var pageRotSurvived  = pageRot[3] === 90;
  var scannedSurvived  = JSON.stringify(_scanned) === scannedBefore;
  var pageDimsSurvived = JSON.stringify(pageDims) === pageDimsBefore;

  await new Promise(function(r){ setTimeout(r, 80); });
  if (window.gc) { try { window.gc(); } catch (e) {} }
  var heapAfterRecycle = (performance.memory && performance.memory.usedJSHeapSize) || null;

  // ---- C4: transparent reinit ----
  await PageRenderer.loadPage(3);
  await new Promise(function(r){ setTimeout(r, 600); });
  var reinitReady    = PageRenderer.ready() === true;
  var reinitCurPage  = (curPage === 3);
  var reinitPainted  = painted();

  // C5: zero /raw fetches across the whole recycle+reinit cycle
  var rawFetchesDuringReinit = rawFetches - rawFetchesBeforeRecycle;

  window.fetch = _origFetch;

  var heapOk = true, heapDetail = "performance.memory unavailable in this browser context";
  if (heapBefore !== null && heapAfterRecycle !== null && heapBefore > 0) {
    var growth = (heapAfterRecycle - heapBefore) / heapBefore;
    heapOk = growth <= 0.10;
    heapDetail = "before=" + heapBefore + " afterRecycle=" + heapAfterRecycle +
                 " growth=" + (growth * 100).toFixed(1) + "%";
  }

  return {
    docSourceKind, skippedOk, recycleResult,
    afterRecyclePdfDocNull, afterRecyclePageCacheEmpty,
    reinitReady, reinitCurPage, reinitPainted, rawFetchesDuringReinit,
    pageRotSurvived, scannedSurvived, pageDimsSurvived,
    heapOk, heapDetail,
    pass: docSourceKind === "blob" &&
          skippedOk && recycleResult === true &&
          afterRecyclePdfDocNull && afterRecyclePageCacheEmpty &&
          reinitReady && reinitCurPage && reinitPainted &&
          rawFetchesDuringReinit === 0 &&
          pageRotSurvived && scannedSurvived && pageDimsSurvived &&
          heapOk
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
    scenario = SC_RECYCLE.replace("%PDF_BYTES%", "[" + ",".join(str(b) for b in pdf) + "]")

    failures = []
    page_errors = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(
            args=["--enable-precise-memory-info", "--js-flags=--expose-gc"]
        )
        pg = b.new_page()
        pg.on("pageerror", lambda e: page_errors.append(f"pageerror: {e}"))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(0.6)

        print()
        print("LITE-WORKER-RECYCLE checks:")
        try:
            result = pg.evaluate(scenario)
            ok = result.get("pass") is True
            print(f"  workerRecycleLifecycle              -> {'PASS' if ok else 'FAIL'}  {result}")
            if not ok:
                failures.append(f"result={result}")
        except Exception as ex:
            print(f"  workerRecycleLifecycle              -> EXCEPTION: {ex}")
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
        print("LITE_WORKER_RECYCLE_FAIL")
        sys.exit(1)
    print("LITE_WORKER_RECYCLE_OK")


if __name__ == "__main__":
    main()
