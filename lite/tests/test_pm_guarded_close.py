#!/usr/bin/env python3
"""
BMA-Plan Lite — guard test for page-manager-redesign approach D, SLICE 1
(PM-GUARD).  docs/invent/page-manager-redesign.md, GO 2026-08-10.

Verifies #pm-overlay (lite/static/js/page-manager-ui.js) refuses to close
while a pending mutation exists, in-shell (no browser confirm()), and gives
visible feedback when opened with no PDF loaded:

  (a) backdropBlockedByPending   pending exists -> click #pm-overlay backdrop
                                  -> overlay STILL open, warning bar visible,
                                  pending unchanged, curPage unchanged
  (b) escBlockedByPending        same precondition -> Escape -> same asserts
  (c) discardThenCloseWorks      click "ทิ้งการแก้ไข" -> pending emptied ->
                                  a subsequent close (✕) actually closes
  (d) deleteConfirmShowsCount    delete button on a page WITH objects ->
                                  in-shell confirm bar visible, text contains
                                  the live object count (no window.confirm)
  (e) noPdfHintVisible           pmOpenManager() with no PDF loaded -> a
                                  visible hint appears (not a silent return)

Harness modeled exactly on test_pm_modal_hotkeys.py (free port from 8250,
uvicorn thread, Playwright sync, PDF upload via SETUP_JS).

Emits LITE_PM_GUARD_OK (exit 0) when all sub-checks pass.
Emits LITE_PM_GUARD_FAIL: <list> (exit 1) otherwise.

Run:
    py -3 lite/tests/test_pm_guarded_close.py
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
# Synthetic PDF fixture — 3 pages, so duplicate()/delete() have real
# neighbours and page 2 can carry fake "drawn objects" for case (d).
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


def _free_port(start: int = 8250) -> int:
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port in range")


# ============================================================
# JS: upload PDF, seed globals, put 2 fake objects on page 2 (for case d).
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
  if (typeof PageRenderer !== 'undefined') PageRenderer.resetCache();
  curPage   = 1;

  PS[1] = {objects: [], scale: null, annotations: []};
  PS[2] = {objects: [
    {kind: 'poly', catId: 'x', pts: [{x:0,y:0},{x:10,y:0},{x:10,y:10},{x:0,y:10}]},
    {kind: 'poly', catId: 'x', pts: [{x:20,y:0},{x:30,y:0},{x:30,y:10},{x:20,y:10}]},
    {kind: 'poly', catId: 'x', pts: [{x:40,y:0},{x:50,y:0},{x:50,y:10},{x:40,y:10}]}
  ], scale: null, annotations: []};
  PS[3] = {objects: [], scale: null, annotations: []};

  if (typeof _pmSeed === 'function') _pmSeed(undefined);

  return {ok: true, caseId: caseId, pages: pageCount,
          pmReady: (typeof pageMgr !== 'undefined' && pageMgr !== null && !!caseId)};
}
"""

# ============================================================
# Cases (a)+(b): create a pending mutation, then try to close via
# backdrop / Esc — overlay must refuse.
# ============================================================

def _blocked_close_js(trigger):
    """trigger: 'backdrop' or 'esc' — returns the JS scenario string."""
    if trigger == 'backdrop':
        dispatch = "document.getElementById('pm-overlay').dispatchEvent(new MouseEvent('click', {bubbles:true}));"
    else:
        dispatch = "document.dispatchEvent(new KeyboardEvent('keydown', {key:'Escape', code:'Escape', bubbles:true, cancelable:true}));"
    return r"""
() => {
  if (typeof pmOpenManager !== 'function' || !caseId || !pageMgr)
    return {ok: false, reason: 'pmOpenManager/caseId/pageMgr not ready'};

  // Fresh pending mutation: duplicate page 1 -> pending.length===1
  pageMgr.pending = [];
  pmOpenManager();
  var ov = document.getElementById('pm-overlay');
  if (!ov || !ov.classList.contains('show'))
    return {ok: false, reason: 'overlay did not open'};

  pageMgr.duplicate(0);
  var pendingBefore = pageMgr.pending.length;
  var curPageBefore = curPage;

  """ + dispatch + r"""

  var overlayStillOpen = ov.classList.contains('show');
  var pendingUnchanged  = pageMgr.pending.length === pendingBefore;
  var curPageUnchanged  = curPage === curPageBefore;
  var warn = document.getElementById('pmui-warn');
  var warnVisible = !!warn && warn.style.display !== 'none' &&
                     getComputedStyle(warn).display !== 'none';

  // clean up: discard the pending dup so the NEXT case starts clean
  if (typeof _pmDiscardPending === 'function') _pmDiscardPending();

  return {
    pendingBefore: pendingBefore,
    overlayStillOpen: overlayStillOpen,
    pendingUnchanged: pendingUnchanged,
    curPageUnchanged: curPageUnchanged,
    warnVisible: warnVisible,
    ok: pendingBefore === 1 && overlayStillOpen && pendingUnchanged &&
        curPageUnchanged && warnVisible
  };
}
"""


CHECK_BACKDROP_BLOCKED = _blocked_close_js('backdrop')
CHECK_ESC_BLOCKED = _blocked_close_js('esc')

# ============================================================
# Case (c): discard clears pending; a SUBSEQUENT close attempt then works.
# ============================================================
CHECK_DISCARD_THEN_CLOSE = r"""
() => {
  if (typeof pmOpenManager !== 'function' || !caseId || !pageMgr)
    return {ok: false, reason: 'pmOpenManager/caseId/pageMgr not ready'};

  pageMgr.pending = [];
  pmOpenManager();
  var ov = document.getElementById('pm-overlay');
  pageMgr.duplicate(0);

  // Trigger the warning bar (backdrop click, blocked)
  ov.dispatchEvent(new MouseEvent('click', {bubbles: true}));
  var blockedFirst = ov.classList.contains('show') && pageMgr.pending.length === 1;

  var discardBtn = document.getElementById('pmui-discard');
  var discardBtnFound = !!discardBtn;
  if (discardBtn) discardBtn.click();

  var pendingAfterDiscard = pageMgr.pending.length;

  // Now close should actually work (click the X button)
  var closeBtn = document.getElementById('pm-close');
  var closeBtnFound = !!closeBtn;
  if (closeBtn) closeBtn.click();

  var overlayClosedAfter = !ov.classList.contains('show');

  return {
    blockedFirst: blockedFirst,
    discardBtnFound: discardBtnFound,
    pendingAfterDiscard: pendingAfterDiscard,
    closeBtnFound: closeBtnFound,
    overlayClosedAfter: overlayClosedAfter,
    ok: blockedFirst && discardBtnFound && pendingAfterDiscard === 0 &&
        closeBtnFound && overlayClosedAfter
  };
}
"""

# ============================================================
# Case (d): delete confirm bar shows the live object count (no confirm()).
# ============================================================
CHECK_DELETE_CONFIRM_COUNT = r"""
() => {
  if (typeof pmOpenManager !== 'function' || !caseId || !pageMgr)
    return {ok: false, reason: 'pmOpenManager/caseId/pageMgr not ready'};

  pageMgr.pending = [];
  var _origConfirm = window.confirm;
  var confirmCalls = 0;
  window.confirm = function() { confirmCalls++; return true; };

  pmOpenManager();
  var g = document.getElementById('pm-grid');
  // page 2 (display idx 1) carries 3 fake objects — data-pmui-idx="1"
  var delBtn = g ? g.querySelector('.pmui-del[data-pmui-idx="1"]') : null;
  var delBtnFound = !!delBtn;
  if (delBtn) delBtn.click();

  window.confirm = _origConfirm;

  var bar = document.querySelector('[id^="pmui-delcfm"], #pmui-delcfm');
  var cfmVisible = !!bar && bar.style.display !== 'none' &&
                    getComputedStyle(bar).display !== 'none';
  var cfmText = bar ? bar.textContent : '';
  var hasCount = cfmText.indexOf('3') >= 0;

  return {
    delBtnFound: delBtnFound,
    confirmCalls: confirmCalls,
    cfmVisible: cfmVisible,
    cfmText: cfmText,
    hasCount: hasCount,
    ok: delBtnFound && confirmCalls === 0 && cfmVisible && hasCount
  };
}
"""

# ============================================================
# Case (e): pmOpenManager() with no PDF -> visible hint (not silent).
# ============================================================
CHECK_NO_PDF_HINT = r"""
() => {
  if (typeof pmOpenManager !== 'function')
    return {ok: false, reason: 'pmOpenManager not defined'};

  var savedCaseId = caseId, savedPageMgr = pageMgr;
  caseId = null; pageMgr = null;

  // Close any residual overlay so we can prove pmOpenManager does NOT show it
  var ov = document.getElementById('pm-overlay');
  if (ov) ov.classList.remove('show');

  var threw = false;
  try { pmOpenManager(); } catch (e) { threw = true; }

  var overlayOpened = !!(ov && ov.classList.contains('show'));

  // Find SOME visible hint element mentioning the PDF requirement.
  var hintVisible = false;
  var candidates = document.querySelectorAll('[id*="hint"], [id*="toast"], [id*="nopdf"]');
  for (var i = 0; i < candidates.length; i++) {
    var el = candidates[i];
    var vis = el.style.display !== 'none' && getComputedStyle(el).display !== 'none' &&
              parseFloat(getComputedStyle(el).opacity || '1') > 0;
    if (vis && el.textContent && el.textContent.indexOf('PDF') >= 0) { hintVisible = true; break; }
  }

  caseId = savedCaseId; pageMgr = savedPageMgr;

  return {
    threw: threw,
    overlayOpened: overlayOpened,
    hintVisible: hintVisible,
    ok: !threw && !overlayOpened && hintVisible
  };
}
"""

# ============================================================
# Case (f) — SLICE 3 add-on (WIZ-UNLOCK, page-manager-redesign approach D):
# after a fresh upload with zero pages tagged, Shift+F12 must open the PM
# overlay. This was BUG-20260810 — previously swallowed by wiz-auto.js's
# document-wide hard lock (now retired). Fixture upload never tags any
# page, so "zero pages tagged" already holds here.
# ============================================================
CHECK_SHIFT_F12_OPENS_PM = r"""
() => {
  var ov = document.getElementById('pm-overlay');
  if (ov) ov.classList.remove('show');

  var zeroTagged = !pageTags || Object.keys(pageTags).length === 0;

  document.dispatchEvent(new KeyboardEvent('keydown', {
    key: 'F12', shiftKey: true, bubbles: true, cancelable: true
  }));

  var ov2 = document.getElementById('pm-overlay');
  var opened = !!ov2 && ov2.classList.contains('show');

  // clean up for any later checks
  if (ov2) ov2.classList.remove('show');

  return {
    zeroTagged: zeroTagged,
    opened: opened,
    lockActive: window.__lwizAutoLockActive === true,
    ok: zeroTagged && opened && window.__lwizAutoLockActive !== true
  };
}
"""

# ============================================================
# Case (g) — SLICE 3 add-on: measure-tool discipline is still enforced,
# just by tag-jit.js's JIT banner now (slice 2), not by wiz-auto's removed
# lock. Arm a measure tool on the untagged fixture page -> banner shows.
# ============================================================
CHECK_JIT_BANNER_STILL_GATES = r"""
() => {
  if (typeof setTool !== 'function' || typeof jitGuardTool !== 'function')
    return {ok: false, reason: 'setTool/jitGuardTool not ready'};

  if (typeof _jitHideBanner === 'function') _jitHideBanner();
  state.tool = 'select';   // known starting tool, distinct from the gated 'poly'
  var toolBefore = state.tool;

  setTool('poly');   // curPage (1) is untagged in the fixture

  var toolAfter = state.tool;
  var toolBlocked = toolAfter === toolBefore && toolAfter !== 'poly';
  var banner = document.getElementById('jit-banner');
  var bannerShown = !!banner && banner.style.display !== 'none';

  return {
    toolBefore: toolBefore,
    toolAfter: toolAfter,
    toolBlocked: toolBlocked,
    bannerShown: bannerShown,
    ok: toolBlocked && bannerShown
  };
}
"""

CHECKS = [
    ("backdropBlockedByPending", CHECK_BACKDROP_BLOCKED),
    ("escBlockedByPending", CHECK_ESC_BLOCKED),
    ("discardThenCloseWorks", CHECK_DISCARD_THEN_CLOSE),
    ("deleteConfirmShowsCount", CHECK_DELETE_CONFIRM_COUNT),
    ("noPdfHintVisible", CHECK_NO_PDF_HINT),
    ("shiftF12OpensPmZeroTagged", CHECK_SHIFT_F12_OPENS_PM),
    ("jitBannerStillGatesMeasure", CHECK_JIT_BANNER_STILL_GATES),
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
        print(f"LITE_PM_GUARD_FAIL: {', '.join(failing)}")
        sys.exit(1)
    else:
        print("LITE_PM_GUARD_OK")
        sys.exit(0)


if __name__ == "__main__":
    main()
