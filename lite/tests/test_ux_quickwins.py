#!/usr/bin/env python3
"""
UX-20260703-review-findings — UX quick-wins batch 1 regression guard.

Covers 5 findings fixed together:
  F-7 (real bug): modalOpen() now also covers #sum (summary overlay — has
      text inputs) and #vs-modal (verify-scale result modal, toggled via
      style.display, not classList). ALSO the keydown handler ignores any
      event whose target is INPUT/TEXTAREA/contenteditable (belt+suspenders).
      Before the fix, typing 'n' into the Summary floor-name input fired the
      'n' -> count tool hotkey.
  F-1: Shift+D activates the path (continuous distance) tool, mirroring the
      Distance flyout's "Continuous path (⇧D)" item.
  F-2: F collision resolved — plain F/f stays Fit (Ctrl+0 alias); Focus mode
      gets its own real hotkey, Shift+F. Button label + cheatsheet updated.
  F-3: Page Manager is now discoverable from the Page menu (#mi-pagemgr),
      wired to window.pmOpenManager().
  cheatsheet truth pass: SHORTCUTS content matches the above (⇧D, ⇧F, ⇧S,
      ⇧F12, Ctrl+, Page Setup, Ctrl+D duplicate rows present; no more
      'Focus mode' -> 'F' row).

Emits LITE_UX_QUICKWINS_OK on success.

    py -3 lite/tests/test_ux_quickwins.py
"""
import io
import json
import socket
import sys
import threading
import time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8560):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


def _build_fixture_pdf() -> bytes:
    import fitz
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text(fitz.Point(50, 100), "P1", fontsize=24)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Check 1 (F-7 part a) — typing into the Summary floor-name input must NOT
# fire the 'n' -> count tool hotkey. Opens #sum via the real openSum() path
# after seeding a minimal PS fixture with tag 'floor' (so floorOptsHTML
# renders the .fc-name text input).
# ---------------------------------------------------------------------------
SC1_SUM_INPUT = r"""
() => {
  if (typeof openSum !== 'function') return {pass:false, err:'openSum missing'};
  caseId = 'test-case';
  curPage = 1;
  PS = {}; PS[1] = {objects: [], scale: {pts_per_m: 10}, annotations: []};
  pageTags = {1: 'floor'};
  pageFloorKind = {}; pageFloorNum = {}; pageNames = {}; excluded = {};
  state.tool = 'select';
  openSum();
  var sumEl = document.getElementById('sum');
  var sumOpen = !!sumEl && sumEl.classList.contains('show');
  var inp = document.querySelector('#sum .fc-name');
  if (!inp) return {pass:false, err:'fc-name input not found in #sum', sumOpen};
  inp.focus();
  var toolBefore = state.tool;
  var ev = new KeyboardEvent('keydown', {key:'n', code:'KeyN', bubbles:true, cancelable:true});
  inp.dispatchEvent(ev);
  var toolAfter = state.tool;
  var toolUnchanged = toolAfter === toolBefore;
  sumEl.classList.remove('show');
  caseId = null;
  return {sumOpen, toolBefore, toolAfter, toolUnchanged, pass: sumOpen && toolUnchanged};
}
"""

# ---------------------------------------------------------------------------
# Check 2 (F-7 part b) — a keydown while #vs-modal is visible (style.display
# ==='flex') must be swallowed by modalOpen(), even when the event target is
# NOT an input (so this exercises the modalOpen() vs-modal branch, not the
# target guard from Check 1).
# ---------------------------------------------------------------------------
SC2_VS_MODAL = r"""
() => {
  if (typeof modalOpen !== 'function') return {pass:false, err:'modalOpen missing'};
  state.tool = 'select';
  var stub = document.getElementById('vs-modal');
  if (!stub) { stub = document.createElement('div'); stub.id = 'vs-modal'; document.body.appendChild(stub); }
  stub.style.display = 'flex';
  var modalOpenTrue = modalOpen() === true;
  var toolBefore = state.tool;
  var ev = new KeyboardEvent('keydown', {key:'n', code:'KeyN', bubbles:true, cancelable:true});
  document.body.dispatchEvent(ev);
  var toolAfter = state.tool;
  var toolUnchanged = toolAfter === toolBefore;
  stub.style.display = 'none';
  return {modalOpenTrue, toolBefore, toolAfter, toolUnchanged, pass: modalOpenTrue && toolUnchanged};
}
"""

# ---------------------------------------------------------------------------
# Check 3 (F-1) — Shift+D sets the path (continuous distance) tool.
# ---------------------------------------------------------------------------
SC3_SHIFT_D = r"""
() => {
  closeOverlays();
  document.getElementById('setupModal').style.display = 'none';
  var vs = document.getElementById('vs-modal'); if (vs) vs.style.display = 'none';
  var pm = document.getElementById('pm-overlay'); if (pm) pm.classList.remove('show');
  state.tool = 'select';
  var ev = new KeyboardEvent('keydown', {key:'D', code:'KeyD', shiftKey:true, bubbles:true, cancelable:true});
  document.body.dispatchEvent(ev);
  return {tool: state.tool, pass: state.tool === 'path'};
}
"""

# ---------------------------------------------------------------------------
# Check 4 (F-2) — Shift+F toggles Focus mode (document.body.classList
# 'focus', same state btn-focus's onclick flips) while plain F/f still
# calls fit() (spy: wrap window.fit and count invocations).
# ---------------------------------------------------------------------------
SC4_SHIFT_F = r"""
() => {
  document.body.classList.remove('focus');
  var fitCalled = 0;
  var origFit = window.fit;
  window.fit = function () { fitCalled++; return origFit.apply(this, arguments); };
  var ev1 = new KeyboardEvent('keydown', {key:'F', code:'KeyF', shiftKey:true, bubbles:true, cancelable:true});
  document.body.dispatchEvent(ev1);
  var focusOnAfterShiftF = document.body.classList.contains('focus');
  var fitCalledOnShiftF = fitCalled > 0;
  var ev2 = new KeyboardEvent('keydown', {key:'f', code:'KeyF', bubbles:true, cancelable:true});
  document.body.dispatchEvent(ev2);
  var fitCalledOnF = fitCalled > 0;
  window.fit = origFit;
  document.body.classList.remove('focus');
  return {focusOnAfterShiftF, fitCalledOnShiftF, fitCalledOnF,
    pass: focusOnAfterShiftF && !fitCalledOnShiftF && fitCalledOnF};
}
"""

# ---------------------------------------------------------------------------
# Check 5 (F-3) — #mi-pagemgr exists in the Page menu; clicking it opens
# #pm-overlay (.show). Requires a real caseId + pageMgr (pmOpenManager()
# guards on both), so this check runs AFTER the fixture PDF upload below.
# ---------------------------------------------------------------------------
SC5_PAGEMGR_MENU = r"""
() => {
  var mi = document.getElementById('mi-pagemgr');
  if (!mi) return {pass:false, err:'mi-pagemgr not found'};
  var inPageMenu = !!mi.closest('.menu[data-m="page"]');
  if (!caseId || !pageMgr) return {pass:false, err:'caseId/pageMgr not seeded', inPageMenu};
  mi.click();
  var ov = document.getElementById('pm-overlay');
  var opened = !!ov && ov.classList.contains('show');
  if (ov) ov.classList.remove('show');
  return {inPageMenu, opened, pass: inPageMenu && opened};
}
"""

# ---------------------------------------------------------------------------
# Check 6 (cheatsheet truth pass) — SHORTCUTS content includes ⇧D, ⇧F, ⇧S,
# ⇧F12 rows and no longer claims F=Focus.
# ---------------------------------------------------------------------------
SC6_CHEATSHEET = r"""
() => {
  if (typeof SHORTCUTS === 'undefined') return {pass:false, err:'SHORTCUTS missing'};
  var allPairs = [];
  Object.keys(SHORTCUTS).forEach(function (k) {
    SHORTCUTS[k].forEach(function (p) { allPairs.push(p); });
  });
  var hasShiftD = allPairs.some(function (p) { return String(p[1]).indexOf('⇧D') >= 0; });
  var hasShiftF = allPairs.some(function (p) { return p[1] === '⇧F'; });
  var hasShiftS = allPairs.some(function (p) { return String(p[1]).indexOf('⇧S') >= 0; });
  var hasShiftF12 = allPairs.some(function (p) { return String(p[1]).indexOf('⇧F12') >= 0; });
  var noFocusEqualsF = !allPairs.some(function (p) { return p[0] === 'Focus mode' && p[1] === 'F'; });
  return {hasShiftD, hasShiftF, hasShiftS, hasShiftF12, noFocusEqualsF,
    pass: hasShiftD && hasShiftF && hasShiftS && hasShiftF12 && noFocusEqualsF};
}
"""

# ---------------------------------------------------------------------------
# Setup JS for the fixture-PDF-backed check (mirrors test_pm_modal_hotkeys.py)
# ---------------------------------------------------------------------------
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


CHECKS_NO_PDF = [
    ("summaryInputBlocksToolHotkey", SC1_SUM_INPUT, ["pass"]),
    ("vsModalStubBlocksToolHotkey",  SC2_VS_MODAL,  ["pass"]),
    ("shiftDSetsPathTool",           SC3_SHIFT_D,   ["pass"]),
    ("shiftFTogglesFocusFStillFits", SC4_SHIFT_F,   ["pass"]),
    ("cheatsheetRowsUpdated",        SC6_CHEATSHEET, ["pass"]),
]


def main():
    from server_lite import app as lite_app
    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)

    try:
        pdf_bytes = _build_fixture_pdf()
    except ImportError:
        print("WARN: PyMuPDF not installed — cannot build fixture PDF; pagemgr-menu check will fail")
        pdf_bytes = b"%PDF-1.4"

    failures = []
    page_errors = []

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.on("pageerror", lambda e: page_errors.append(f"pageerror: {e}"))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(0.6)

        print()
        print("UX quick-wins batch 1 checks:")
        for name, scenario, required_keys in CHECKS_NO_PDF:
            try:
                result = pg.evaluate(scenario)
            except Exception as ex:
                print(f"  {name:34s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
                continue
            ok = all(result.get(k) is True for k in required_keys)
            status = "PASS" if ok else "FAIL"
            print(f"  {name:34s} -> {status}  {result}")
            if not ok:
                bad = [k for k in required_keys if result.get(k) is not True]
                failures.append(f"check '{name}' failed keys: {bad}  result={result}")

        # Check 5 needs a real caseId + pageMgr — upload the fixture PDF first.
        try:
            seed = pg.evaluate(SETUP_JS, list(pdf_bytes))
            if not seed.get("ok"):
                print(f"  SETUP FAILED: {seed}")
                failures.append(f"fixture PDF setup failed: {seed}")
            else:
                print(f"  Setup OK: caseId={seed.get('caseId')}, pmReady={seed.get('pmReady')}")
        except Exception as ex:
            print(f"  SETUP EXCEPTION: {ex}")
            failures.append(f"fixture PDF setup threw: {ex}")

        time.sleep(0.3)
        name, scenario, required_keys = ("pagemgrMenuItemOpensOverlay", SC5_PAGEMGR_MENU, ["pass"])
        try:
            result = pg.evaluate(scenario)
        except Exception as ex:
            print(f"  {name:34s} -> EXCEPTION: {ex}")
            failures.append(f"check '{name}' threw: {ex}")
        else:
            ok = all(result.get(k) is True for k in required_keys)
            status = "PASS" if ok else "FAIL"
            print(f"  {name:34s} -> {status}  {result}")
            if not ok:
                bad = [k for k in required_keys if result.get(k) is not True]
                failures.append(f"check '{name}' failed keys: {bad}  result={result}")

        pg.close()
        b.close()

    for e in page_errors:
        print("  JS ERROR:", e)

    server.should_exit = True
    time.sleep(0.4)

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_UX_QUICKWINS_FAIL")
        sys.exit(1)
    else:
        print("LITE_UX_QUICKWINS_OK")


if __name__ == "__main__":
    main()
