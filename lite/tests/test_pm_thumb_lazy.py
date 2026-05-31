#!/usr/bin/env python3
"""
BMA-Plan Lite — guard test for lpm-8 (FRICTION).

Verifies that opening the page manager on a 50-page PDF uses lazy loading:
  (a) renders all 50 tiles immediately (grid structure is instant),
  (b) after a PARTIAL scroll (30% of grid height), fires FEWER than all 50
      /thumb requests — proves IntersectionObserver gates fetches per tile.
      FAILS with the bug: loading="lazy" alone fires ALL 50 on the first
      scroll event (Chromium un-defers all lazy images at once when the
      scroll container moves from position 0).
  (c) after scrolling to 100%, /thumb count INCREASES from the 30% checkpoint
      — proves tiles below 30% were NOT pre-fetched.

EVOLT contract: RED BEFORE FIX, GREEN AFTER FIX.

Why (b) is the sentinel:
  loading="lazy" fires 0 on open (overlay was display:none → deferred), then
  fires ALL remaining tiles on the first scroll event (Chromium un-defers all
  at once). With IO root=#pm-grid-wrap, only tiles entering the scroll container's
  visible viewport fire — partial scroll fires only the newly-visible rows.

Run:
    py -3 lite/tests/test_pm_thumb_lazy.py
Prints LITE_PM_THUMB_LAZY_OK (exit 0) when all sub-checks pass.
Prints LITE_PM_THUMB_LAZY_FAIL: <list> (exit 1) otherwise.

Boot pattern mirrors test_pm_modal_hotkeys.py:
  free port from 8240, uvicorn thread, Playwright sync, fixture PDF via SETUP_JS.
  50-page fixture at 900x600 viewport so grid overflows the scroll container
  (wrapHeight ~413px, gridHeight ~1779px at 6-per-row × 50 tiles).
  /thumb requests counted via page.on("request") — NOT by inspecting source.
"""

import io
import json
import os
import socket
import sys
import threading
import time
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(LITE))


# ============================================================
# Synthetic PDF fixture — 50 pages A4.
# At 900x600 viewport, grid overflows wrap (wrapH ~413 < gridH ~1779).
# ============================================================

NUM_PAGES  = 50
VIEWPORT_W = 900
VIEWPORT_H = 600


def _build_fixture_pdf(num_pages: int = NUM_PAGES) -> bytes:
    import fitz
    doc = fitz.open()
    for i in range(num_pages):
        page = doc.new_page(width=595, height=842)
        page.insert_text(fitz.Point(50, 100), f"P{i+1}", fontsize=24)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


# ============================================================
# Server boot helpers (mirror test_pm_modal_hotkeys.py)
# ============================================================

def _free_port(start: int = 8240) -> int:
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port in range")


# ============================================================
# JS: upload PDF, seed globals so caseId && pageMgr are truthy.
# ============================================================
SETUP_JS = r"""
async (pdfBytes) => {
  var arr  = new Uint8Array(pdfBytes);
  var blob = new Blob([arr], {type: 'application/pdf'});
  var file = new File([blob], 'fixture50p.pdf', {type: 'application/pdf'});
  var fd   = new FormData();
  fd.append('file', file);
  var res  = await fetch('/upload', {method: 'POST', body: fd});
  var json = await res.json();
  if (json.error) return {ok: false, error: json.error};

  caseId    = json.case_id;
  pdfName   = json.name;
  pageCount = json.pages;
  PS        = {};
  excluded  = {};
  if (typeof PageRenderer !== 'undefined') PageRenderer.resetCache();
  curPage   = 1;

  PS[1] = PS[1] || {objects: [], scale: null, annotations: []};
  if (typeof _pmSeed === 'function') _pmSeed(undefined);

  return {ok: true, caseId: caseId, pages: pageCount,
          pmReady: (typeof pageMgr !== 'undefined' && pageMgr !== null && !!caseId)};
}
"""

# ============================================================
# JS: open the manager, return tile count + overflow state.
# ============================================================
OPEN_MANAGER_JS = r"""
() => {
  if (typeof pmOpenManager !== 'function')
    return {ok: false, reason: 'pmOpenManager not defined'};
  if (!caseId || !pageMgr)
    return {ok: false, reason: 'caseId or pageMgr falsy'};

  pmOpenManager();

  var ov = document.getElementById('pm-overlay');
  if (!ov || !ov.classList.contains('show'))
    return {ok: false, reason: 'pm-overlay did not gain .show'};

  var grid = document.getElementById('pm-grid');
  var wrap = document.getElementById('pm-grid-wrap');
  var tileCount = grid ? grid.querySelectorAll('.pmui-thumb').length : 0;
  var overflows = wrap ? (wrap.scrollHeight > wrap.clientHeight) : false;

  return {ok: true, tileCount: tileCount, overflows: overflows};
}
"""

# ============================================================
# JS: scroll pm-grid-wrap to a fraction of its scroll height.
# ============================================================
SCROLL_FRAC_JS = r"""
(frac) => {
  var wrap = document.getElementById('pm-grid-wrap');
  if (!wrap) return {ok: false, reason: 'pm-grid-wrap not found'};
  wrap.scrollTop = wrap.scrollHeight * frac;
  return {ok: true, scrollTop: wrap.scrollTop, scrollHeight: wrap.scrollHeight};
}
"""


# ============================================================
# Main test driver
# ============================================================

def main():
    from server_lite import app as lite_app
    import uvicorn
    from playwright.sync_api import sync_playwright

    port   = _free_port()
    cfg    = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)

    try:
        pdf_bytes = _build_fixture_pdf()
        print(f"  Fixture: {NUM_PAGES}-page PDF ({len(pdf_bytes)} bytes)")
    except ImportError:
        print("WARN: PyMuPDF not installed — cannot build fixture PDF; test will fail at setup")
        pdf_bytes = b"%PDF-1.4"

    page_errors = []
    results     = {}

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        pg      = browser.new_page()
        pg.set_viewport_size({"width": VIEWPORT_W, "height": VIEWPORT_H})
        pg.on("pageerror", lambda e: page_errors.append(str(e)))

        # ---- count /thumb/ requests via network event ----
        thumb_requests_total = []

        def on_request(req):
            if "/thumb/" in req.url:
                thumb_requests_total.append(req.url)

        pg.on("request", on_request)

        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(1.5)

        # Upload fixture
        try:
            seed = pg.evaluate(SETUP_JS, list(pdf_bytes))
            if not seed.get("ok"):
                print(f"  SETUP FAILED: {seed}")
            else:
                print(f"  Setup OK: caseId={seed.get('caseId')}, "
                      f"pages={seed.get('pages')}, pmReady={seed.get('pmReady')}")
        except Exception as ex:
            print(f"  SETUP EXCEPTION: {ex}")

        time.sleep(0.5)

        # ---- Open manager ----
        thumb_baseline = len(thumb_requests_total)

        try:
            open_result = pg.evaluate(OPEN_MANAGER_JS)
        except Exception as ex:
            open_result = {"ok": False, "reason": f"JS exception: {ex}"}

        time.sleep(0.5)   # brief settle after open

        tile_count = open_result.get("tileCount", 0)    if open_result.get("ok") else 0
        overflows  = open_result.get("overflows", False) if open_result.get("ok") else False
        print(f"  Grid overflows: {overflows}, tileCount: {tile_count}")

        # (a) All 50 tiles rendered immediately (grid structure is instant)
        check_a_pass = (tile_count == NUM_PAGES)
        print(f"  (a) tiles rendered immediately: {tile_count}/{NUM_PAGES} "
              f"-> {'[PASS]' if check_a_pass else '[FAIL]'}")
        results["tilesRendered"] = check_a_pass

        # ---- Scroll to 30% of grid ----
        try:
            pg.evaluate(SCROLL_FRAC_JS, 0.3)
        except Exception as ex:
            print(f"  SCROLL 30% EXCEPTION: {ex}")

        time.sleep(1.0)
        thumb_at_30pct = len(thumb_requests_total) - thumb_baseline

        # ---- Scroll to 100% ----
        try:
            pg.evaluate(SCROLL_FRAC_JS, 1.0)
        except Exception as ex:
            print(f"  SCROLL 100% EXCEPTION: {ex}")

        time.sleep(1.5)
        thumb_at_100pct = len(thumb_requests_total) - thumb_baseline
        thumb_delta_30_to_100 = thumb_at_100pct - thumb_at_30pct

        # (b) After partial scroll (30%), far fewer than all 50 fired.
        #     FAILS with bug: loading="lazy" fires ALL 50 on first scroll (30% = 50).
        #     PASSES with fix: IO fires only newly-visible tiles (30% → ~10-20 tiles).
        #
        # Threshold: at 30% of ~1779px grid with ~413px wrap, we expect ~2 extra rows
        # to enter view.  With rootMargin="200px", up to 4 rows ≈ 24 tiles visible.
        # We set threshold at < 40 (80% of 50) to give ample margin.
        PARTIAL_BURST_THRESHOLD = 40
        if overflows:
            check_b_pass = (thumb_at_30pct < PARTIAL_BURST_THRESHOLD)
            print(f"  (b) /thumb after 30% scroll: {thumb_at_30pct} "
                  f"(must be < {PARTIAL_BURST_THRESHOLD}; loading=lazy fires all {NUM_PAGES} at once) "
                  f"-> {'[PASS]' if check_b_pass else '[FAIL]'}")
        else:
            check_b_pass = False
            print(f"  (b) FAIL: grid does NOT overflow — test fixture/viewport mismatch, "
                  f"cannot distinguish burst vs lazy.")
        results["noBurstOnPartialScroll"] = check_b_pass

        # (c) Scrolling from 30% to 100% fires MORE requests.
        #     Only meaningful when (b) passed (not all tiles fired at 30%).
        if check_b_pass and thumb_at_30pct < NUM_PAGES:
            check_c_pass = (thumb_delta_30_to_100 > 0)
            print(f"  (c) /thumb 30%→100% scroll: +{thumb_delta_30_to_100} "
                  f"-> {'[PASS]' if check_c_pass else '[FAIL]'}")
        else:
            check_c_pass = True
            print(f"  (c) skipped — preconditions not met (b={check_b_pass}, "
                  f"at_30pct={thumb_at_30pct})")
        results["lazyOnFurtherScroll"] = check_c_pass

        print(f"  Summary: at_30pct={thumb_at_30pct}, at_100pct={thumb_at_100pct}, "
              f"delta_30_to_100={thumb_delta_30_to_100}")

        pg.close()
        browser.close()

    server.should_exit = True
    time.sleep(0.4)

    if page_errors:
        print()
        print("JS page errors:")
        for e in page_errors:
            print(f"  {e}")

    failing = [n for n, ok in results.items() if not ok]
    print()
    if failing:
        print(f"LITE_PM_THUMB_LAZY_FAIL: {', '.join(failing)}")
        sys.exit(1)
    else:
        print("LITE_PM_THUMB_LAZY_OK")
        sys.exit(0)


if __name__ == "__main__":
    main()
