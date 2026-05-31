#!/usr/bin/env python3
"""
BMA-Plan Lite — guard test for lpm-9 (FRICTION).

Verifies that while #pm-overlay is open, app-level hotkeys do NOT leak through:
  - pmBlocksToolHotkey: pressing 'n' must NOT switch the underlying tool.
  - pmEscClosesOnce:    pressing Escape closes the overlay and does NOT
                        additionally fire the app Escape branch (state.vertMode
                        sentinel stays untouched).

EVOLT contract: write this test BEFORE the fix so it FAILS (RED) against the
unfixed code, then apply the fix to make it GREEN.

Run:
    py -3 lite/tests/test_pm_modal_hotkeys.py
Prints LITE_PM_MODAL_OK (exit 0) when all sub-checks pass.
Prints LITE_PM_MODAL_FAIL: <list> (exit 1) otherwise.

Boot pattern mirrors test_metamorphic_pages.py:
  free port from 8240, uvicorn thread, Playwright sync, PDF upload via SETUP_JS.
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
# Synthetic PDF fixture (1-page A4 — just enough to satisfy
# caseId && pageMgr guard inside pmOpenManager).
# ============================================================

def _build_fixture_pdf() -> bytes:
    import fitz
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text(fitz.Point(50, 100), "P1", fontsize=24)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


# ============================================================
# Server boot helpers (mirror test_metamorphic_pages.py)
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
  var file = new File([blob], 'fixture1p.pdf', {type: 'application/pdf'});
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
# Sub-check 1: pmBlocksToolHotkey
#
# 1. Open pm-overlay via pmOpenManager().
# 2. Record state.tool before dispatch.
# 3. Dispatch a real 'keydown' for key:'n' on window
#    (the same event that setTool('count') would intercept).
# 4. Assert: state.tool is UNCHANGED and #pm-overlay still has .show.
#
# Why non-tautological: we dispatch the real event; the app keydown listener
# reads modalOpen() at L1096 and either returns early (fix applied) or falls
# through to map['n'] → setTool('count') (bug present).  The test observes
# state.tool — it does NOT re-implement modalOpen().
# ============================================================
TOOL_HOTKEY_JS = r"""
() => {
  // Open the manager (requires caseId && pageMgr)
  if (typeof pmOpenManager !== 'function')
    return {ok: false, reason: 'pmOpenManager not defined'};
  if (!caseId || !pageMgr)
    return {ok: false, reason: 'caseId or pageMgr falsy — PDF not loaded?'};

  pmOpenManager();

  var ov = document.getElementById('pm-overlay');
  if (!ov || !ov.classList.contains('show'))
    return {ok: false, reason: 'pm-overlay did not gain .show after pmOpenManager()'};

  // Record tool before
  var toolBefore = state.tool;

  // Dispatch a real keydown 'n' on window (not calling setTool directly)
  var ev = new KeyboardEvent('keydown', {
    key: 'n', code: 'KeyN', bubbles: true, cancelable: true
  });
  window.dispatchEvent(ev);

  var toolAfter   = state.tool;
  var overlayOpen = ov.classList.contains('show');

  // Close overlay for next sub-check
  ov.classList.remove('show');

  var toolUnchanged = (toolAfter === toolBefore);
  var pass = toolUnchanged && overlayOpen;
  return {
    ok: pass,
    toolBefore:   toolBefore,
    toolAfter:    toolAfter,
    toolUnchanged: toolUnchanged,
    overlayOpen:  overlayOpen,
    reason: pass ? '' : ('tool changed ' + toolBefore + ' -> ' + toolAfter +
                         '; overlayOpen=' + overlayOpen)
  };
}
"""

# ============================================================
# Sub-check 2: pmEscClosesOnce
#
# Tests that when Escape is dispatched on WINDOW (the path the app keydown
# handler guards via modalOpen()), the app Escape branch does NOT run while
# pm-overlay is open.
#
# Why dispatch on window: the app listener is window.addEventListener('keydown').
# The pm-overlay Esc listener is document.addEventListener('keydown').
# These are independent registrations on different targets.
# We test the window-handler path directly:
#   1. Open overlay (pm-overlay has .show).
#   2. Plant sentinel: state.vertMode = truthy string.
#   3. Dispatch Escape on window → app window handler fires:
#      - WITH fix: modalOpen() returns true → early return → sentinel intact,
#        overlay still has .show (pm-overlay doc listener did NOT fire because
#        the event was dispatched on window, not document).
#      - WITHOUT fix: modalOpen() returns false → Escape branch fires →
#        sentinel cleared.
#   4. Assert: sentinel intact (app branch did not run).
#   5. Clean up: manually close overlay.
#
# The fallback per spec: if sentinel approach is impractical, assert
# overlay closed + state.tool unchanged. We use the window-dispatch approach
# which is fully deterministic.
# ============================================================
ESC_ONCE_JS = r"""
() => {
  if (typeof pmOpenManager !== 'function')
    return {ok: false, reason: 'pmOpenManager not defined'};
  if (!caseId || !pageMgr)
    return {ok: false, reason: 'caseId or pageMgr falsy'};

  // Plant sentinel: the app Escape branch at L1109 does
  //   if(state.vertMode){state.vertMode=null; ...}
  // So set it truthy; if app Escape branch fires, it clears it.
  var SENTINEL = '__esc_test__';
  var prevVertMode = state.vertMode;
  state.vertMode = SENTINEL;

  // Also record tool (secondary check: tool must not change)
  var toolBefore = state.tool;

  // Open overlay
  pmOpenManager();
  var ov = document.getElementById('pm-overlay');
  if (!ov || !ov.classList.contains('show')) {
    state.vertMode = prevVertMode;
    return {ok: false, reason: 'pm-overlay did not open for Esc test'};
  }

  // Dispatch Escape on WINDOW (tests the window.addEventListener path,
  // which is guarded by modalOpen()).  The pm-overlay doc listener is on
  // document and does NOT fire for window-dispatched events.
  var ev = new KeyboardEvent('keydown', {
    key: 'Escape', code: 'Escape', bubbles: true, cancelable: true
  });
  // Dispatch on DOCUMENT (bubbles:true) so the event traverses the REAL path
  // document -> window, exactly like a physical Esc press. The pm-overlay
  // Esc listener (on document) fires first; with the fix it calls
  // stopPropagation() so the window app handler never receives it.
  document.dispatchEvent(ev);

  // With fix: pm-ui doc listener closes overlay + stopPropagation() →
  //           window app Escape branch never runs → sentinel intact.
  // Without fix: doc listener closes overlay, event bubbles to window,
  //           modalOpen()=false (overlay now closed) → app Escape branch
  //           runs → sentinel cleared (double-fire).
  var overlayClosed  = !ov.classList.contains('show');
  var sentinelIntact = (state.vertMode === SENTINEL);
  var toolUnchanged  = (state.tool === toolBefore);

  // Clean up
  ov.classList.remove('show');
  state.vertMode = prevVertMode;

  // Esc must close the manager exactly once: overlay closed AND the app
  // Escape branch did NOT also fire (sentinel intact). tool also unchanged.
  var pass = overlayClosed && sentinelIntact && toolUnchanged;
  return {
    ok: pass,
    overlayClosed:  overlayClosed,
    sentinelIntact: sentinelIntact,
    toolUnchanged:  toolUnchanged,
    toolBefore:     toolBefore,
    toolAfter:      state.tool,
    reason: pass ? '' : ('overlayClosed=' + overlayClosed +
                         '; sentinelIntact=' + sentinelIntact +
                         '; toolUnchanged=' + toolUnchanged)
  };
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
    except ImportError:
        print("WARN: PyMuPDF not installed — cannot build fixture PDF; test will fail at setup")
        pdf_bytes = b"%PDF-1.4"

    page_errors = []
    results = {}

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        pg      = browser.new_page()
        pg.on("pageerror", lambda e: page_errors.append(str(e)))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(1.5)

        # Upload fixture
        try:
            seed = pg.evaluate(SETUP_JS, list(pdf_bytes))
            if not seed.get("ok"):
                print(f"  SETUP FAILED: {seed}")
            else:
                print(f"  Setup OK: caseId={seed.get('caseId')}, "
                      f"pmReady={seed.get('pmReady')}")
        except Exception as ex:
            print(f"  SETUP EXCEPTION: {ex}")

        time.sleep(0.5)

        # Run sub-checks
        checks = [
            ("pmBlocksToolHotkey", TOOL_HOTKEY_JS),
            ("pmEscClosesOnce",    ESC_ONCE_JS),
        ]
        for name, js in checks:
            try:
                result = pg.evaluate(js)
            except Exception as ex:
                result = {"ok": False, "reason": f"JS exception: {ex}"}
            results[name] = result
            status = "[PASS]" if result.get("ok") else "[FAIL]"
            print(f"  {status} {name}")
            if not result.get("ok"):
                print(f"         reason: {result.get('reason', '')}")
                detail = {k: v for k, v in result.items()
                          if k not in ("ok", "reason")}
                if detail:
                    print(f"         detail: {json.dumps(detail, default=str)[:400]}")

        pg.close()
        browser.close()

    server.should_exit = True
    time.sleep(0.4)

    if page_errors:
        print()
        print("JS page errors:")
        for e in page_errors:
            print(f"  {e}")

    failing = [n for n, r in results.items() if not r.get("ok")]
    print()
    if failing:
        print(f"LITE_PM_MODAL_FAIL: {', '.join(failing)}")
        sys.exit(1)
    else:
        print("LITE_PM_MODAL_OK")
        sys.exit(0)


if __name__ == "__main__":
    main()
