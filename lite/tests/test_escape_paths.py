#!/usr/bin/env python3
"""
BMA-Plan Lite — guard test for BUG-20260811-escape-paths.

Two "exit paths bypass the guard door" regressions found in user field test
2026-08-11:

  (a) page-manager-ui.js tile click called loadPage()+_pmCloseOverlay()
      DIRECTLY, skipping the pending-mutation guard (_pmTryClose()) that
      PM-GUARD (c88a379) built. Dragging/reordering pages then clicking a
      tile silently discarded the pending mutation with zero warning.
  (b) overview-grid.js's wizard dblclick-escape guard checked
      window.__lwizAutoLockActive, which WIZ-UNLOCK (fb9b2af) permanently
      set to false (dead code) -> dblclick always escaped, even with pages
      selected mid-triage.

THE PRINCIPLE both fixes serve: "every exit path routes through one guarded
door, and the door checks for work-in-progress."

4 sub-checks:
  caseA_pmTileClickBlockedByPending   PM: pending mutation exists -> tile
                                       click must NOT navigate/close, must
                                       show the pending warning bar
  caseB_pmTileClickWorksWhenClean     PM: no pending -> tile click still
                                       navigates + closes normally
  caseC_wizDblclickBlockedBySelection wizard: pages selected -> dblclick
                                       must NOT navigate/close, must show a
                                       visible hint (#lwiz-hint)
  caseD_wizDblclickWorksWhenClean     wizard: no selection -> dblclick still
                                       navigates + closes normally

Harness modeled on test_pm_guarded_close.py (same fixture builder / setup
JS / port range convention, offset to avoid collision).

Emits LITE_ESCAPE_PATHS_OK (exit 0) when all sub-checks pass.
Emits LITE_ESCAPE_PATHS_FAIL: <list> (exit 1) otherwise.

Run:
    py -3 lite/tests/test_escape_paths.py
"""

import io
import json
import socket
import sys
import threading
import time
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))


# ============================================================
# Synthetic PDF fixture — 3 pages (same shape as test_pm_guarded_close.py).
# ============================================================

def _build_fixture_pdf() -> bytes:
    import fitz
    doc = fitz.open()
    for i in range(3):
        page = doc.new_page(width=595, height=842)
        page.insert_text(fitz.Point(50, 100), "P%d" % (i + 1), fontsize=24)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


def _free_port(start: int = 8320) -> int:
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port in range")


# ============================================================
# JS: upload PDF, seed globals (same shape as test_pm_guarded_close.py).
# ============================================================
SETUP_JS = r"""
async (pdfBytes) => {
  var arr  = new Uint8Array(pdfBytes);
  var blob = new Blob([arr], {type: 'application/pdf'});
  var file = new File([blob], 'fixture3p.pdf', {type: 'application/pdf'});
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
  pageTags  = {};
  if (typeof PageRenderer !== 'undefined') PageRenderer.resetCache();
  curPage   = 1;

  PS[1] = {objects: [], scale: null, annotations: []};
  PS[2] = {objects: [], scale: null, annotations: []};
  PS[3] = {objects: [], scale: null, annotations: []};

  if (typeof _pmSeed === 'function') _pmSeed(undefined);

  return {ok: true, caseId: caseId, pages: pageCount,
          pmReady: (typeof pageMgr !== 'undefined' && pageMgr !== null && !!caseId)};
}
"""

# ============================================================
# CASE A — PM tile click must be blocked while a pending mutation exists.
# ============================================================
CHECK_CASE_A = r"""
() => {
  if (typeof pmOpenManager !== 'function' || !caseId || !pageMgr)
    return {ok: false, reason: 'pmOpenManager/caseId/pageMgr not ready'};

  pageMgr.pending = [];
  pmOpenManager();
  var ov = document.getElementById('pm-overlay');
  if (!ov || !ov.classList.contains('show'))
    return {ok: false, reason: 'overlay did not open'};

  pageMgr.duplicate(0);   // create a pending mutation
  var pendingBefore = pageMgr.pending.length;
  curPage = 1;
  var curPageBefore = curPage;

  var g = document.getElementById('pm-grid');
  var tile = g ? g.querySelector('.pmui-thumb[data-pmui-idx="1"]') : null;
  var tileFound = !!tile;
  if (tile) tile.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));

  var overlayStillOpen = ov.classList.contains('show');
  var pendingUnchanged  = pageMgr.pending.length === pendingBefore;
  var curPageUnchanged  = curPage === curPageBefore;
  var warn = document.getElementById('pmui-warn');
  var warnVisible = !!warn && warn.style.display !== 'none' &&
                     getComputedStyle(warn).display !== 'none';

  // clean up: discard the pending dup so later cases start clean
  if (typeof _pmDiscardPending === 'function') _pmDiscardPending();
  if (typeof _pmCloseOverlay === 'function') _pmCloseOverlay();

  return {
    tileFound: tileFound,
    pendingBefore: pendingBefore,
    overlayStillOpen: overlayStillOpen,
    pendingUnchanged: pendingUnchanged,
    curPageUnchanged: curPageUnchanged,
    warnVisible: warnVisible,
    ok: tileFound && pendingBefore === 1 && overlayStillOpen &&
        pendingUnchanged && curPageUnchanged && warnVisible
  };
}
"""

# ============================================================
# CASE B — PM tile click with NOTHING pending still navigates + closes.
# ============================================================
CHECK_CASE_B = r"""
() => {
  if (typeof pmOpenManager !== 'function' || !caseId || !pageMgr)
    return {ok: false, reason: 'pmOpenManager/caseId/pageMgr not ready'};

  pageMgr.pending = [];
  curPage = 1;
  pmOpenManager();
  var ov = document.getElementById('pm-overlay');
  if (!ov || !ov.classList.contains('show'))
    return {ok: false, reason: 'overlay did not open'};

  // page 3 -> display idx 2
  var g = document.getElementById('pm-grid');
  var tile = g ? g.querySelector('.pmui-thumb[data-pmui-idx="2"]') : null;
  var tileFound = !!tile;
  if (tile) tile.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));

  var overlayClosed = !ov.classList.contains('show');
  var navigatedCorrectly = curPage === 3;

  return {
    tileFound: tileFound,
    overlayClosed: overlayClosed,
    curPage: curPage,
    navigatedCorrectly: navigatedCorrectly,
    ok: tileFound && overlayClosed && navigatedCorrectly
  };
}
"""

# ============================================================
# CASE C — wizard dblclick must be blocked while pages are selected.
# ============================================================
CHECK_CASE_C = r"""
async () => {
  if (typeof openOv !== 'function')
    return {ok: false, reason: 'openOv not defined'};

  curPage = 1;
  _lovsSelected.clear();
  var h0 = document.getElementById('lwiz-hint'); if (h0) h0.remove();

  openOv();
  await new Promise(r => setTimeout(r, 300));
  var ov = document.getElementById('ov');
  if (!ov || !ov.classList.contains('show'))
    return {ok: false, reason: 'wizard overlay did not open'};

  // single click on a tile -> selects it (BUT NOT curPage navigation)
  var tile = document.querySelector('#grid-classify .ov-tile[data-pg="2"]');
  var tileFound = !!tile;
  if (tile) tile.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));

  var selCountAfterClick = _lovsSelected.size;
  var curPageBefore = curPage;

  if (tile) tile.dispatchEvent(new MouseEvent('dblclick', {bubbles: true, cancelable: true}));
  await new Promise(r => setTimeout(r, 150));

  var wizardStillOpen = ov.classList.contains('show');
  var curPageUnchanged = curPage === curPageBefore;
  var hintVisible = !!document.getElementById('lwiz-hint');

  return {
    tileFound: tileFound,
    selCountAfterClick: selCountAfterClick,
    wizardStillOpen: wizardStillOpen,
    curPageUnchanged: curPageUnchanged,
    hintVisible: hintVisible,
    ok: tileFound && selCountAfterClick > 0 && wizardStillOpen &&
        curPageUnchanged && hintVisible
  };
}
"""

# ============================================================
# CASE D — wizard dblclick with NO selection still navigates + closes.
# ============================================================
CHECK_CASE_D = r"""
async () => {
  if (typeof openOv !== 'function')
    return {ok: false, reason: 'openOv not defined'};

  curPage = 1;
  _lovsSelected.clear();

  openOv();
  await new Promise(r => setTimeout(r, 300));
  var ov = document.getElementById('ov');
  if (!ov || !ov.classList.contains('show'))
    return {ok: false, reason: 'wizard overlay did not open'};

  var selCountBefore = _lovsSelected.size;

  var tile = document.querySelector('#grid-classify .ov-tile[data-pg="3"]');
  var tileFound = !!tile;
  if (tile) tile.dispatchEvent(new MouseEvent('dblclick', {bubbles: true, cancelable: true}));
  await new Promise(r => setTimeout(r, 150));

  var wizardClosed = !ov.classList.contains('show');
  var navigatedCorrectly = curPage === 3;

  return {
    tileFound: tileFound,
    selCountBefore: selCountBefore,
    wizardClosed: wizardClosed,
    curPage: curPage,
    navigatedCorrectly: navigatedCorrectly,
    ok: tileFound && selCountBefore === 0 && wizardClosed && navigatedCorrectly
  };
}
"""

CHECKS = [
    ("caseA_pmTileClickBlockedByPending", CHECK_CASE_A),
    ("caseB_pmTileClickWorksWhenClean", CHECK_CASE_B),
    ("caseC_wizDblclickBlockedBySelection", CHECK_CASE_C),
    ("caseD_wizDblclickWorksWhenClean", CHECK_CASE_D),
]


def main():
    from server_lite import app as lite_app
    import uvicorn
    from playwright.sync_api import sync_playwright

    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
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
        pg = browser.new_page()
        pg.on("pageerror", lambda e: page_errors.append(str(e)))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(1.5)

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

        for name, js in CHECKS:
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
                    print(f"         detail: {json.dumps(detail, default=str)[:500]}")

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
        print(f"LITE_ESCAPE_PATHS_FAIL: {', '.join(failing)}")
        sys.exit(1)
    else:
        print("LITE_ESCAPE_PATHS_OK")
        sys.exit(0)


if __name__ == "__main__":
    main()
