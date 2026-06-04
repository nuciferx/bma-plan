#!/usr/bin/env python3
"""
BMA-Plan Lite — acceptance test: pdfjs local-first (offline-safe rendering).

Verifies that lite can render a PDF page even when cdn.jsdelivr.net is
completely unreachable.  Playwright intercepts and aborts every request
whose URL contains "cdn.jsdelivr.net" before any page load, simulating
an offline / proxy-blocked environment.

The test then uploads a synthetic 1-page PDF via the real /upload endpoint
and drives PageRenderer.loadPage(1).  Asserts:
  1. pdfDoc is non-null after loadPage (PDF.js resolved from LOCAL vendor).
  2. _pdfjsLib is truthy (module cached).
  3. No error alert fired during the load.
  4. No cdn.jsdelivr.net request succeeded (route aborted them all).

Prints LITE_PDFJS_OFFLINE_OK and exits 0 on success.
Prints a diagnostic and exits 1 on failure.

Requires: playwright, uvicorn, PyMuPDF (fitz).

Run:
    py -3 lite/tests/test_pdfjs_offline.py
"""

import io
import socket
import sys
import threading
import time
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))


# ============================================================
# Synthetic 1-page PDF (A4, minimal content)
# ============================================================

def _build_fixture_pdf() -> bytes:
    import fitz
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text(fitz.Point(50, 100), "offline-test", fontsize=18)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


# ============================================================
# Server boot helper
# ============================================================

def _free_port(start: int = 8490) -> int:
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ============================================================
# Browser-side JS: upload PDF + drive loadPage(1)
# ============================================================

SETUP_AND_LOAD_JS = r"""
async (pdfBytes) => {
  // Upload the fixture PDF
  var arr  = new Uint8Array(pdfBytes);
  var blob = new Blob([arr], {type: 'application/pdf'});
  var file = new File([blob], 'offline-fixture.pdf', {type: 'application/pdf'});
  var fd   = new FormData();
  fd.append('file', file);
  var res  = await fetch('/upload', {method: 'POST', body: fd});
  var json = await res.json();
  if (json.error) return {ok: false, step: 'upload', error: json.error};

  // Mirror uploadPdf() global setup
  caseId    = json.case_id;
  pdfName   = json.name;
  pageCount = json.pages;
  PS        = {};
  excluded  = {};
  if (typeof PageRenderer !== 'undefined') PageRenderer.resetCache();
  curPage   = 1;

  // Capture alerts so we can report them without popping a dialog
  var alertFired = [];
  var _origAlert = window.alert;
  window.alert = function(msg) { alertFired.push(String(msg)); };

  // Drive the real loadPage path
  try {
    await PageRenderer.loadPage(1);
  } catch(e) {
    window.alert = _origAlert;
    return {ok: false, step: 'loadPage', error: e && e.message ? e.message : String(e)};
  }

  window.alert = _origAlert;

  // Give _render one tick to kick off (it's async/rAF-scheduled)
  await new Promise(r => setTimeout(r, 200));

  var pdfDocOk   = (typeof pdfDoc !== 'undefined') && pdfDoc !== null;
  var pdfjsLibOk = (typeof _pdfjsLib !== 'undefined') && _pdfjsLib !== null;
  var noAlert    = alertFired.length === 0;

  return {
    ok: pdfDocOk && pdfjsLibOk && noAlert,
    pdfDocOk:   pdfDocOk,
    pdfjsLibOk: pdfjsLibOk,
    noAlert:    noAlert,
    alerts:     alertFired,
    caseId:     caseId,
    pageCount:  pageCount
  };
}
"""


# ============================================================
# Main
# ============================================================

def main():
    from server_lite import app as lite_app
    import uvicorn
    from playwright.sync_api import sync_playwright

    port = _free_port()
    cfg    = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)

    try:
        pdf_bytes = _build_fixture_pdf()
    except ImportError as ex:
        print(f"SKIP: PyMuPDF not installed — {ex}")
        sys.exit(0)

    cdn_requests_attempted = []   # URLs that were attempted (and aborted)
    page_errors            = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        pg      = browser.new_page()
        pg.on("pageerror", lambda e: page_errors.append(str(e)))

        # --- Block cdn.jsdelivr.net BEFORE navigating ---
        def _abort_cdn(route):
            cdn_requests_attempted.append(route.request.url)
            route.abort()

        pg.route("**/cdn.jsdelivr.net/**", _abort_cdn)

        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(1.5)

        # Upload fixture + drive loadPage(1) under CDN block
        try:
            result = pg.evaluate(SETUP_AND_LOAD_JS, list(pdf_bytes))
        except Exception as ex:
            result = {"ok": False, "step": "evaluate", "error": str(ex)}

        pg.close()
        browser.close()

    server.should_exit = True
    time.sleep(0.4)

    # ---- Report ----
    print(f"  CDN requests attempted (all aborted): {len(cdn_requests_attempted)}")
    for u in cdn_requests_attempted:
        print(f"    blocked: {u}")

    if page_errors:
        print("  JS page errors:")
        for e in page_errors:
            print(f"    {e}")

    print(f"  pdfDocOk:   {result.get('pdfDocOk')}")
    print(f"  pdfjsLibOk: {result.get('pdfjsLibOk')}")
    print(f"  noAlert:    {result.get('noAlert')}")
    if result.get("alerts"):
        print(f"  alerts: {result['alerts']}")
    if not result.get("ok"):
        detail = {k: v for k, v in result.items() if k not in ("ok",)}
        print(f"  DETAIL: {detail}")

    # Acceptance criteria:
    #   A) JS result says ok (pdfDocOk + pdfjsLibOk + noAlert)
    #   B) Local vendor was used — meaning no CDN request succeeded
    #      (all were aborted, yet pdfDoc loaded) — proven by A + cdn_requests_attempted
    #      may be 0 (local worked first) or >0 but all aborted yet result ok.
    ok = result.get("ok", False)

    print()
    if ok:
        print("LITE_PDFJS_OFFLINE_OK")
        sys.exit(0)
    else:
        print("LITE_PDFJS_OFFLINE_FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()
