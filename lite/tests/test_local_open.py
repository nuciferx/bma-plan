"""
PERF-20260702 local-first open guard.

Problem: uploadPdf() waited for POST /upload (measured ~80 ms/MB — 7.5 s of a
9.6 s cold open on a real 91 MB binder) before PDF.js ever saw a byte.

Fix: PageRenderer.openLocal(buf) opens the user's local bytes immediately
(first paint ~1.2 s flat, any size); the upload runs in the background and
PageRenderer.adoptCase(caseId) binds the already-loaded doc so /raw is never
fetched. Server-dependent features stay gated on caseId (openOv no-op,
exports alert) during the window.

Checks (upload artificially delayed 2.5 s via fetch wrapper):
  C1 paint-before-upload — canvas paints + ready() while caseId is still null.
  C2 gate               — openOv() during the window is a no-op (#ov not shown).
  C3 adopt              — caseId arrives later; loadPage(2) renders with ZERO
                          /raw fetches for the whole flow (local buffer reused).
  C4 state              — pageCount===3, pdfName from local file, pm seeded.

RED pre-fix: openLocal doesn't exist -> evaluate throws; and old flow painted
only AFTER upload (paint-before-upload false).

Emits LITE_LOCAL_OPEN_OK on success.

    py -3 lite/tests/test_local_open.py
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


def _free_port(start=8770):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


def _make_pdf_bytes(pages=3, w=300, h=400):
    doc = fitz.open()
    for i in range(pages):
        pg = doc.new_page(width=w, height=h)
        pg.insert_text(fitz.Point(70, 200), f"LOCAL {i+1}", fontsize=28)
        sh = pg.new_shape()
        sh.draw_rect(fitz.Rect(20, 20, 280, 380))
        sh.finish(color=(0, 0, 0), width=2)
        sh.commit()
    b = doc.tobytes()
    doc.close()
    return b


SC_LOCAL_OPEN = r"""
async () => {
  var UPLOAD_DELAY = 2500;
  var rawFetches = 0;
  var _origFetch = window.fetch;
  window.fetch = function(url, opts) {
    var u = String(url);
    if (u.indexOf("/raw") >= 0) rawFetches++;
    if (u.indexOf("/upload") >= 0) {
      return new Promise(function(res) {
        setTimeout(function(){ res(_origFetch(url, opts)); }, UPLOAD_DELAY);
      });
    }
    return _origFetch(url, opts);
  };

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

  var bytes = new Uint8Array(%PDF_BYTES%);
  var file = new File([bytes], "local-test.pdf", {type: "application/pdf"});

  var t0 = performance.now();
  var uploadDone = uploadPdf(file);   // do NOT await — background flow under test

  // C1: paint before upload completes
  var paintBeforeUpload = false, tPaint = null, caseAtPaint = "unset";
  for (var i = 0; i < 40; i++) {                      // poll up to 2.0 s < UPLOAD_DELAY
    await new Promise(function(r){ setTimeout(r, 50); });
    if (PageRenderer.ready() && painted()) {
      tPaint = Math.round(performance.now() - t0);
      caseAtPaint = caseId;
      paintBeforeUpload = (caseId === null);
      break;
    }
  }

  // C2: server-gated overview is a no-op during the window
  var ovNoop = true;
  if (caseId === null) {
    try { openOv(); ovNoop = !document.getElementById("ov").classList.contains("show"); }
    catch (e) { ovNoop = false; }
  }

  await uploadDone;                                    // let the background upload land
  var caseAfter = caseId;
  var adoptedPageCount = pageCount;
  var nameOk = pdfName !== null && String(pdfName).indexOf("local") >= 0;
  var pmSeeded = (typeof pageMgr !== "undefined") && !!pageMgr;

  // C3: page switch after adoption must reuse the local buffer — zero /raw
  await PageRenderer.loadPage(2);
  await new Promise(function(r){ setTimeout(r, 400); });
  var page2Ok = PageRenderer.ready() && curPage === 2 && painted();

  window.fetch = _origFetch;

  return {
    tPaint, caseAtPaint, paintBeforeUpload, ovNoop,
    caseAfter: !!caseAfter, adoptedPageCount, nameOk, pmSeeded,
    page2Ok, rawFetches,
    pass: paintBeforeUpload && ovNoop && !!caseAfter && adoptedPageCount === 3 &&
          nameOk && pmSeeded && page2Ok && rawFetches === 0
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
    scenario = SC_LOCAL_OPEN.replace("%PDF_BYTES%", "[" + ",".join(str(b) for b in pdf) + "]")

    failures = []
    page_errors = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.on("pageerror", lambda e: page_errors.append(f"pageerror: {e}"))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(0.6)

        print()
        print("LITE-LOCAL-OPEN checks:")
        try:
            result = pg.evaluate(scenario)
            ok = result.get("pass") is True
            print(f"  localFirstOpenFlow                  -> {'PASS' if ok else 'FAIL'}  {result}")
            if not ok:
                failures.append(f"result={result}")
        except Exception as ex:
            print(f"  localFirstOpenFlow                  -> EXCEPTION: {ex}")
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
        print("LITE_LOCAL_OPEN_FAIL")
        sys.exit(1)
    print("LITE_LOCAL_OPEN_OK")


if __name__ == "__main__":
    main()
