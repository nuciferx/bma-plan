#!/usr/bin/env python3
"""
BMA-Plan Lite — invariant-lock guard for lpm-7 (FRICTION).

applyOrderMatchesSimulateFlush: the `order` array posted to /apply-page-mutations
must equal the `order` produced by pageMgr.simulateFlush() mapped to server page
numbers via the same rule serverNum() uses:
  originNum[id] if non-null, else srcServer[id] if present, else null (merged).

Scenarios (s1-s5), each with a fresh upload to guarantee clean state:
  s1: pure reorder (move first page to end)
  s2: delete a middle page
  s3: duplicate a page
  s4: reorder THEN delete
  s5: reorder THEN duplicate

Non-tautological: intercepts the REAL /apply-page-mutations request body via
Playwright page.on("request") and compares its `order` to an INDEPENDENTLY
computed expected order (page.evaluate → simulateFlush().order mapped to
serverNums).  Does NOT re-read the source code.

Run:
    py -3 lite/tests/test_pm_apply_flush_unified.py
Prints LITE_PM_APPLY_UNIFIED_OK (exit 0) when all scenarios pass.
Prints LITE_PM_APPLY_UNIFIED_FAIL: <list> (exit 1) on any failure.

Boot pattern mirrors test_pm_modal_hotkeys.py:
  free port from 8250, uvicorn thread, Playwright sync, PDF upload via SETUP_JS.
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
# Synthetic 6-page PDF fixture (A4, unique text markers P1..P6)
# ============================================================

def _build_fixture_pdf() -> bytes:
    import fitz
    doc = fitz.open()
    for i in range(1, 7):
        page = doc.new_page(width=595, height=842)
        page.insert_text(fitz.Point(50, 100), f"P{i}", fontsize=24)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


# ============================================================
# Server boot helpers
# ============================================================

def _free_port(start: int = 8250) -> int:
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port in range")


# ============================================================
# SETUP_JS: upload PDF, seed pageMgr globals.
# Called with list(pdf_bytes) from Python.
# ============================================================
SETUP_JS = r"""
async (pdfBytes) => {
  var arr  = new Uint8Array(pdfBytes);
  var blob = new Blob([arr], {type: 'application/pdf'});
  var file = new File([blob], 'fixture6p.pdf', {type: 'application/pdf'});
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
# EXPECTED_JS: compute expected order from simulateFlush via page.evaluate.
# Returns array of server page numbers (integers), or null entries for merged.
# ============================================================
EXPECTED_JS = r"""
() => {
  if (!pageMgr) return {ok: false, reason: 'pageMgr null'};
  var sim = pageMgr.simulateFlush();
  var order = [];
  for (var i = 0; i < sim.order.length; i++) {
    var id = sim.order[i];
    var sn = (pageMgr.originNum[id] != null) ? pageMgr.originNum[id]
             : (pageMgr.srcServer[id] != null ? pageMgr.srcServer[id] : null);
    order.push(sn);
  }
  return {ok: true, order: order};
}
"""

# ============================================================
# TRIGGER_JS: call _pmuiApplyChanges() and return immediately.
# The posted request body is captured via page.on("request") in Python.
# Returns {ok, reason}.
# ============================================================
TRIGGER_JS = r"""
async () => {
  if (typeof _pmuiApplyChanges !== 'function')
    return {ok: false, reason: '_pmuiApplyChanges not defined'};
  if (!pageMgr || !caseId)
    return {ok: false, reason: 'pageMgr or caseId falsy'};
  if (pageMgr.pending.length === 0)
    return {ok: false, reason: 'no pending mutations — test setup failed?'};
  try {
    await _pmuiApplyChanges();
    return {ok: true};
  } catch(e) {
    return {ok: false, reason: 'exception: ' + e.message};
  }
}
"""

# ============================================================
# Per-scenario mutation JS (evaluated BEFORE capturing expected + triggering apply).
# Each returns {ok, reason, pendingLen}.
# ============================================================

# s1: pure reorder — move page 1 (0-based idx 0) to end (idx 5, i.e., after the 6th)
# reorder(from, to): from=0 → to=5 means: remove from idx 0, insert at idx 5.
S1_MUTATE_JS = r"""
() => {
  if (!pageMgr) return {ok: false, reason: 'pageMgr null'};
  if (pageMgr.count() < 6) return {ok: false, reason: 'need 6 pages'};
  // move 0-based idx 0 to idx 5 (last position)
  pageMgr.reorder(0, 5);
  return {ok: true, pendingLen: pageMgr.pending.length};
}
"""

# s2: delete the middle page (0-based idx 2 = display page 3)
S2_MUTATE_JS = r"""
() => {
  if (!pageMgr) return {ok: false, reason: 'pageMgr null'};
  if (pageMgr.count() < 4) return {ok: false, reason: 'need at least 4 pages'};
  // del(idx): 0-based index in pageOrder
  pageMgr.del(2);
  return {ok: true, pendingLen: pageMgr.pending.length};
}
"""

# s3: duplicate page at 0-based idx 1 (display page 2)
S3_MUTATE_JS = r"""
() => {
  if (!pageMgr) return {ok: false, reason: 'pageMgr null'};
  if (pageMgr.count() < 2) return {ok: false, reason: 'need at least 2 pages'};
  // duplicate(idx): 0-based index, inserts copy at idx+1
  pageMgr.duplicate(1);
  return {ok: true, pendingLen: pageMgr.pending.length};
}
"""

# s4: reorder (move idx 0 to idx 5) THEN delete what is now idx 1 (originally p2)
S4_MUTATE_JS = r"""
() => {
  if (!pageMgr) return {ok: false, reason: 'pageMgr null'};
  if (pageMgr.count() < 6) return {ok: false, reason: 'need 6 pages'};
  // reorder: move idx 0 to idx 5
  pageMgr.reorder(0, 5);
  // delete idx 1 (now originally p2 — after reorder pageOrder is [p2,p3,p4,p5,p6,p1])
  pageMgr.del(1);
  return {ok: true, pendingLen: pageMgr.pending.length};
}
"""

# s5: reorder (move idx 0 to idx 5) THEN duplicate what is now idx 0 (originally p2)
S5_MUTATE_JS = r"""
() => {
  if (!pageMgr) return {ok: false, reason: 'pageMgr null'};
  if (pageMgr.count() < 6) return {ok: false, reason: 'need 6 pages'};
  // reorder: move idx 0 to idx 5
  pageMgr.reorder(0, 5);
  // duplicate idx 0 (now originally p2)
  pageMgr.duplicate(0);
  return {ok: true, pendingLen: pageMgr.pending.length};
}
"""

SCENARIOS = [
    ("s1_pure_reorder",     S1_MUTATE_JS),
    ("s2_delete_middle",    S2_MUTATE_JS),
    ("s3_duplicate_page",   S3_MUTATE_JS),
    ("s4_reorder_then_del", S4_MUTATE_JS),
    ("s5_reorder_then_dup", S5_MUTATE_JS),
]


# ============================================================
# Run one scenario: upload fresh PDF, apply mutations, capture request,
# compare to independently computed expected order.
# Returns (passed: bool, detail: str)
# ============================================================
def _run_scenario(pg, pdf_bytes: bytes, name: str, mutate_js: str) -> tuple:
    # Fresh upload to guarantee clean state
    try:
        seed = pg.evaluate(SETUP_JS, list(pdf_bytes))
    except Exception as ex:
        return False, f"SETUP exception: {ex}"
    if not seed.get("ok"):
        return False, f"SETUP failed: {seed}"

    # Apply mutations
    try:
        mut = pg.evaluate(mutate_js)
    except Exception as ex:
        return False, f"MUTATE exception: {ex}"
    if not mut.get("ok"):
        return False, f"MUTATE failed: {mut.get('reason')}"
    if mut.get("pendingLen", 0) == 0:
        return False, "no pending mutations after mutate"

    # Compute expected order INDEPENDENTLY via page.evaluate
    try:
        exp_result = pg.evaluate(EXPECTED_JS)
    except Exception as ex:
        return False, f"EXPECTED_JS exception: {ex}"
    if not exp_result.get("ok"):
        return False, f"EXPECTED_JS failed: {exp_result.get('reason')}"
    expected_order = exp_result["order"]

    # Intercept the /apply-page-mutations request body
    posted_order = []
    captured = threading.Event()

    def on_request(request):
        if "/apply-page-mutations" in request.url and request.method == "POST":
            try:
                body = json.loads(request.post_data or "{}")
                posted_order.extend(body.get("order", []))
            except Exception:
                pass
            captured.set()

    pg.on("request", on_request)

    # Trigger _pmuiApplyChanges()
    try:
        trig = pg.evaluate(TRIGGER_JS)
    except Exception as ex:
        pg.remove_listener("request", on_request)
        return False, f"TRIGGER_JS exception: {ex}"

    # Wait for intercept (max 3s)
    captured.wait(timeout=3.0)
    pg.remove_listener("request", on_request)

    if not trig.get("ok"):
        return False, f"TRIGGER failed: {trig.get('reason')}"
    if not posted_order:
        return False, "no /apply-page-mutations request intercepted"

    if posted_order != expected_order:
        return False, (
            f"ORDER MISMATCH:\n"
            f"  expected (simulateFlush-mapped): {expected_order}\n"
            f"  posted   (live _pmuiApplyChanges): {posted_order}"
        )

    return True, f"expected={expected_order} posted={posted_order}"


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
        print("WARN: PyMuPDF not installed — cannot build fixture PDF")
        pdf_bytes = b"%PDF-1.4"

    page_errors = []
    results = {}

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        pg      = browser.new_page()
        pg.on("pageerror", lambda e: page_errors.append(str(e)))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(1.5)

        for name, mutate_js in SCENARIOS:
            passed, detail = _run_scenario(pg, pdf_bytes, name, mutate_js)
            results[name] = (passed, detail)
            status = "[PASS]" if passed else "[FAIL]"
            print(f"  {status} {name}: {detail[:200]}")
            time.sleep(0.3)

        pg.close()
        browser.close()

    server.should_exit = True
    time.sleep(0.4)

    if page_errors:
        print()
        print("JS page errors:")
        for e in page_errors:
            print(f"  {e}")

    failing = [n for n, (ok, _) in results.items() if not ok]
    print()
    if failing:
        print(f"LITE_PM_APPLY_UNIFIED_FAIL: {', '.join(failing)}")
        sys.exit(1)
    else:
        print("LITE_PM_APPLY_UNIFIED_OK")
        sys.exit(0)


if __name__ == "__main__":
    main()
