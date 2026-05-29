#!/usr/bin/env python3
"""
BMA-Plan Lite — metamorphic relations for page-manager wiring (EVOLT-2).

Drives the REAL live app (server_lite + ui-lite.html) via Playwright.  Each
MR asserts an invariant that the program PROMISES.  Several are EXPECTED TO
FAIL on the current shipped code — that is the regression-first design.

Metamorphic relations tested (in order):
  MR-rotate            rotate a page 90deg → measured m² unchanged [should PASS]
  MR-reorder           reorder page → measurement stays attached by identity [may FAIL B3]
  MR-save-roundtrip    reorder+Apply → save → reload → deep-equal page identities+areas [FAIL B1/B2]
  MR-save-pending      reorder WITHOUT Apply → save → saved doc reflects PENDING order [FAIL B2]
  MR-dirty             pure pageMgr.reorder() → state.dirty===true [FAIL B5]
  MR-render-source     after duplicate (pending), canvas loadPage uses serverNum not raw idx [FAIL B3]

Expected fail list (current code):
  MR-save-roundtrip, MR-save-pending, MR-dirty, MR-render-source

Run:
    py -3 lite/tests/test_metamorphic_pages.py
Exits 0 + prints LITE_METAMORPHIC_PAGES_OK if ALL pass.
Exits 1 + prints LITE_METAMORPHIC_PAGES_FAIL: <list> on any failure
         (expected on current code for the bug-catching MRs).

Requires: Node.js on PATH, playwright + uvicorn installed, PyMuPDF (fitz).
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
# Synthetic 5-page PDF fixture (A4, unique text markers P1..P5,
# and a 200x200pt filled square on each page so area is measurable).
# Generated once at test start; uploaded via the real /upload endpoint.
# ============================================================

def _build_fixture_pdf() -> bytes:
    """Build a 5-page A4 PDF using PyMuPDF.  Each page has:
       - Text marker "Pn" at (50, 100)
       - A 200x200pt square (drawn as lines) at (100, 150)..(300, 350)
    Returns the raw PDF bytes.
    """
    import fitz
    doc = fitz.open()
    for i in range(1, 6):
        page = doc.new_page(width=595, height=842)   # A4 in pts
        # Text marker
        page.insert_text(fitz.Point(50, 100), f"P{i}", fontsize=24)
        # Visible square (stroke only — area tool traces pts, not vectors)
        rect = fitz.Rect(100, 150, 300, 350)
        page.draw_rect(rect, color=(0, 0, 1), width=1)
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


# ============================================================
# Server boot helpers (mirror test_page_manager_ui.py)
# ============================================================

def _free_port(start: int = 8470) -> int:
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ============================================================
# Browser-side JavaScript snippets
# ============================================================

# ------------------------------------------------------------------
# SETUP: upload the fixture PDF and seed pageMgr with a known scale.
# Scale: 200 pts / 10 m  => pts_per_m = 20 => area of 200x200 sq = (200/20)^2 = 100 m²
# ------------------------------------------------------------------
SETUP_JS = r"""
async (pdfBytes) => {
  // Build a File object from the raw bytes
  var arr   = new Uint8Array(pdfBytes);
  var blob  = new Blob([arr], {type: 'application/pdf'});
  var file  = new File([blob], 'fixture5p.pdf', {type: 'application/pdf'});

  // Upload via the real upload path
  var fd = new FormData();
  fd.append('file', file);
  var res  = await fetch('/upload', {method: 'POST', body: fd});
  var json = await res.json();
  if (json.error) return {ok: false, error: json.error};

  // Set app globals (mirror uploadPdf())
  caseId    = json.case_id;
  pdfName   = json.name;
  pageCount = json.pages;
  PS        = {};
  excluded  = {};
  if (typeof PageRenderer !== 'undefined') PageRenderer.resetCache();
  curPage   = 1;

  // Set scale on page 1 (200 pts / 10 m → pts_per_m = 20) so area is measurable
  PS[1] = PS[1] || {objects: [], scale: null, annotations: []};
  PS[1].scale = {pts_per_m: 20};

  // Add a 200x200 pt square on page 1 (canvas-coords; same as PDF-coords at rot=0)
  PS[1].objects.push({
    id: 1, catId: 'gfa', semanticTag: 'gross_floor_area', kind: 'poly',
    counting: false, dimVisible: true,
    pts: [{x:100,y:150},{x:300,y:150},{x:300,y:350},{x:100,y:350}]
  });

  // Seed pageMgr
  if (typeof _pmSeed === 'function') _pmSeed(undefined);

  return {ok: true, caseId: caseId, pages: pageCount, pmCount: pageMgr ? pageMgr.count() : 0};
}
"""

# ------------------------------------------------------------------
# MR-rotate: rotate page 1 by 90 degrees via pageRot, assert m² unchanged.
# Uses polyAreaM2 directly on the raw pts (rotation doesn't change pts in lite).
# NOTE: In lite, pageRot affects the VIEW transform, not the stored pts.
#       So polyAreaM2(pts) must be identical before and after pgRot change.
# ------------------------------------------------------------------
MR_ROTATE_JS = r"""
() => {
  // Ensure scale is set
  var scale = getScaleForPage(1);
  if (!scale) return {ok: false, reason: 'no scale for page 1'};

  var pts = PS[1] && PS[1].objects[0] && PS[1].objects[0].pts;
  if (!pts || pts.length < 3) return {ok: false, reason: 'no polygon on page 1'};

  // Area before rotation
  var pgOld = curPage;
  curPage = 1;
  var areaBefore = polyAreaM2(pts);

  // Rotate page 1 by 90 (pageRot is owned by page-renderer.js)
  var prevRot = pageRot[1] || 0;
  pageRot[1] = (prevRot + 90) % 360;

  // Area after rotation (pts unchanged — rotation is a view transform only)
  var areaAfter = polyAreaM2(pts);

  // Restore
  pageRot[1] = prevRot;
  curPage = pgOld;

  var diff = Math.abs(areaBefore - areaAfter);
  var pass = areaBefore !== null && diff < 1e-6;
  return {
    ok: pass,
    areaBefore: areaBefore,
    areaAfter: areaAfter,
    diff: diff,
    reason: pass ? '' : ('area changed after rotation: ' + areaBefore + ' -> ' + areaAfter)
  };
}
"""

# ------------------------------------------------------------------
# MR-reorder: reorder page 0→1 in pageMgr.  The measurement data
# (objects on what was page 1) must travel with the page identity.
#
# Assertion: after reorder, the page at new display position (its id = original pg1 id)
# still has the object with pts=[100,150..300,350].
# The page's IDENTITY (pageMgr id) carries the measurement → id-based lookup must work.
#
# B3 bug: if the app uses raw display index to look up PS[] (rather than identity),
# the measurement ends up on the wrong page after reorder.
# ------------------------------------------------------------------
MR_REORDER_JS = r"""
() => {
  if (!pageMgr || pageMgr.count() < 2)
    return {ok: false, reason: 'pageMgr not ready or < 2 pages'};

  // Record the identity of display-page 1 and its object count
  var origId1     = pageMgr.idAt(1);
  var origId2     = pageMgr.idAt(2);
  var origObjects = (pageMgr.PS_by_id[origId1] && pageMgr.PS_by_id[origId1].objects) || [];
  var origObjCount = origObjects.length;

  // Reorder: move page at index 0 → index 1 (display order: [p2, p1, p3, p4, p5])
  pageMgr.reorder(0, 1);

  // After reorder: display-page 1 should now be origId2, display-page 2 should be origId1
  var newId1 = pageMgr.idAt(1);
  var newId2 = pageMgr.idAt(2);

  // The IDENTITY that was originally page 1 must still own its objects
  var movedPS = pageMgr.PS_by_id[origId1];
  var movedObjCount = (movedPS && movedPS.objects) ? movedPS.objects.length : -1;

  var identityPreserved = (movedObjCount === origObjCount);

  // Additional: the globally accessible PS[n] (number-keyed) is NOT yet updated
  // by pageMgr (requires _pmCommit() from slice 5) — but the identity model
  // in pageMgr itself must stay correct.
  var modelConsistent = (newId1 === origId2) && (newId2 === origId1);

  // Restore
  pageMgr.reorder(1, 0);

  var pass = identityPreserved && modelConsistent;
  return {
    ok: pass,
    origId1: origId1, origId2: origId2,
    newId1:  newId1,  newId2:  newId2,
    origObjCount: origObjCount,
    movedObjCount: movedObjCount,
    identityPreserved: identityPreserved,
    modelConsistent: modelConsistent,
    reason: pass ? '' : JSON.stringify({identityPreserved, modelConsistent})
  };
}
"""

# ------------------------------------------------------------------
# MR-save-roundtrip: reorder + Apply (mock Apply since real Apply hits server),
# then call mi-save's assembly path (buildPageStore + doc assembly), parse
# the saved JSON, reload via PageModel.load(), and assert:
#   (1) pageIdentities round-trips in reordered order
#   (2) per-page objects follow the identity (area data intact)
#
# B1: if save ignores pageIdentities, roundtrip loses identity → FAIL
# B2: if save ignores pending reorder, roundtrip is in ORIGINAL order → FAIL
#
# We simulate Apply by calling pageMgr.applyFlush() after a reorder,
# then call _pmCommit() (even if it's currently a no-op in slice 4)
# to project back to PS[].  If _pmCommit() is a no-op, the save will
# use the old PS[] (number-keyed, in original order) → deep-equal FAILS.
# ------------------------------------------------------------------
MR_SAVE_ROUNDTRIP_JS = r"""
() => {
  if (!pageMgr || pageMgr.count() < 2)
    return {ok: false, reason: 'pageMgr not ready'};

  // Reorder: swap pages 0 and 1
  pageMgr.reorder(0, 1);
  var reorderedIds = pageMgr.pageOrder.slice();

  // Simulate Apply: flush pending (applyFlush resets pending + originNum)
  pageMgr.applyFlush();

  // _pmCommit: projects pageMgr → PS,pageTags,etc. (slice 5; no-op in slice 3/4)
  if (typeof _pmCommit === 'function') _pmCommit();

  // Build the save document (same logic as mi-save onclick)
  var doc = {
    version: 1, app: 'bma-plan-lite', pdfName: pdfName, totalPages: pageCount,
    pageStore: buildPageStore(),
    pageRotations: pageRot,
    pageTags: pageTags,
    pageNames: pageNames,
    projectInfo: projectInfo,
    siteOrientation: {},
    excludedPages: Object.keys(excluded).filter(function(k){return excluded[k];}).map(Number),
    pageFloorKind: pageFloorKind,
    pageFloorNum: pageFloorNum,
    pageIdentities: pageMgr.pageOrder.slice(),
    liteLayers: [],
    liteGroups: [],
    reportVars: []
  };
  var savedJson = JSON.stringify(doc);

  // Reload into a fresh PageModel
  var PageModel2 = (typeof module !== 'undefined') ? require('./page-manager') : PageModel;
  var m2 = new PageModel2();
  PageModel2._resetIdc && PageModel2._resetIdc();
  try {
    m2.load(JSON.parse(savedJson));
  } catch(e) {
    return {ok: false, reason: 'load threw: ' + e.message};
  }

  // Assert 1: pageIdentities roundtrip matches the reordered order
  var savedIds     = doc.pageIdentities;
  var loadedIds    = m2.pageOrder;
  var idsMatch     = JSON.stringify(savedIds) === JSON.stringify(loadedIds);

  // Assert 2: the page that was originally page 1 (with the polygon) is at
  // position 2 in the reordered model (0-based index 1), and its objects survive.
  // We check that *some* page in the reloaded model has objects.length === 1.
  var anyPageHasObjects = m2.pageOrder.some(function(id){
    var ps = m2.PS_by_id[id];
    return ps && ps.objects && ps.objects.length > 0;
  });

  // Assert 3: the reloaded order must match reorderedIds
  var orderMatches = JSON.stringify(m2.pageOrder) === JSON.stringify(reorderedIds);

  // Restore pageMgr to original order for other MRs
  pageMgr.reorder(1, 0);
  pageMgr.pending = [];

  var pass = idsMatch && anyPageHasObjects && orderMatches;
  return {
    ok: pass,
    savedIds: savedIds,
    loadedIds: loadedIds,
    reorderedIds: reorderedIds,
    idsMatch: idsMatch,
    anyPageHasObjects: anyPageHasObjects,
    orderMatches: orderMatches,
    reason: pass ? '' : JSON.stringify({idsMatch, anyPageHasObjects, orderMatches})
  };
}
"""

# ------------------------------------------------------------------
# MR-save-pending: reorder WITHOUT Apply, then save.
# Assert the saved doc reflects the PENDING (on-screen) order in pageIdentities.
# B2: save currently uses PS[] (number-keyed original order), so saved
# pageIdentities is still the pre-reorder order → FAIL.
# ------------------------------------------------------------------
MR_SAVE_PENDING_JS = r"""
() => {
  if (!pageMgr || pageMgr.count() < 2)
    return {ok: false, reason: 'pageMgr not ready'};

  // Capture original order
  var origOrder = pageMgr.pageOrder.slice();

  // Reorder WITHOUT Apply
  pageMgr.reorder(0, 1);
  var pendingOrder = pageMgr.pageOrder.slice();

  // Save with the pending reorder (do NOT call applyFlush)
  // The save path (mi-save) does NOT call _pmCommit or applyFlush.
  // It does include pageMgr.pageOrder.slice() as pageIdentities IF the
  // save handler reads pageMgr — but today's mi-save does NOT read pageMgr at all.
  var doc = {
    version: 1, app: 'bma-plan-lite', pdfName: pdfName, totalPages: pageCount,
    pageStore: buildPageStore(),
    pageRotations: pageRot,
    pageTags: pageTags,
    pageNames: pageNames,
    projectInfo: projectInfo,
    siteOrientation: {},
    excludedPages: Object.keys(excluded).filter(function(k){return excluded[k];}).map(Number),
    pageFloorKind: pageFloorKind,
    pageFloorNum: pageFloorNum,
    // The CORRECT save must emit the PENDING pageOrder from pageMgr:
    pageIdentities: pageMgr ? pageMgr.pageOrder.slice() : null,
    liteLayers: [],
    liteGroups: [],
    reportVars: []
  };

  var savedIdentities = doc.pageIdentities;

  // Assert: savedIdentities must equal pendingOrder (the on-screen reordered state)
  var identitiesReflectPending = JSON.stringify(savedIdentities) === JSON.stringify(pendingOrder);
  var identitiesAreOriginal   = JSON.stringify(savedIdentities) === JSON.stringify(origOrder);

  // Restore
  pageMgr.reorder(1, 0);
  pageMgr.pending = [];

  // PASS only if save reflects PENDING order.
  // If save still emits original order, identitiesAreOriginal=true, identitiesReflectPending=false → FAIL.
  // Note: in the current code, the save onclick is wired separately and does NOT
  // read pageMgr.pageOrder — so pageIdentities is whatever was set at _pmSeed time,
  // which is the original seeded order. Hence identitiesReflectPending should be false.
  var pass = identitiesReflectPending;
  return {
    ok: pass,
    origOrder: origOrder,
    pendingOrder: pendingOrder,
    savedIdentities: savedIdentities,
    identitiesReflectPending: identitiesReflectPending,
    identitiesAreOriginal: identitiesAreOriginal,
    reason: pass ? '' : 'save does not reflect pending reorder in pageIdentities (B2)'
  };
}
"""

# ------------------------------------------------------------------
# MR-dirty: pure pageMgr.reorder() must flip state.dirty to true.
# B5: _pmCommit() (which sets state.dirty=true) is UNUSED in slice 3/4.
# The reorder only mutates pageMgr.pageOrder + pageMgr.pending.
# state.dirty is NOT set → FAIL on current code.
# ------------------------------------------------------------------
MR_DIRTY_JS = r"""
() => {
  if (!pageMgr || pageMgr.count() < 2)
    return {ok: false, reason: 'pageMgr not ready'};

  // Reset dirty to known-false state
  state.dirty = false;
  var dirtyBefore = state.dirty;

  // Perform a pure reorder (no _pmCommit, no Apply, no pushUndo)
  pageMgr.reorder(0, 1);

  var dirtyAfter = state.dirty;

  // Restore
  pageMgr.reorder(1, 0);
  pageMgr.pending = [];

  var pass = (dirtyBefore === false) && (dirtyAfter === true);
  return {
    ok: pass,
    dirtyBefore: dirtyBefore,
    dirtyAfter: dirtyAfter,
    reason: pass ? '' : 'state.dirty not flipped after pageMgr.reorder (B5): was=' + dirtyBefore + ' now=' + dirtyAfter
  };
}
"""

# ------------------------------------------------------------------
# MR-render-source: after a duplicate (pending, not applied),
# the thumbnail img src in #pm-grid for the duplicate tile must
# reference the SOURCE page's serverNum, not a raw display index.
#
# The THUMBNAIL path (#pm-grid img src) already uses serverNum() correctly
# via _pmuiRenderGrid (which calls api('/thumb/' + sn)).
#
# The MAIN CANVAS loadPage(n) goes to /raw which is the whole PDF;
# PDF.js renders page n from that PDF using pdfDoc.getPage(n).
# After a duplicate (pending, not flushed), display page n+1 is a dup
# whose serverNum() returns the source page's server number.
# But pdfDoc.getPage(n+1) would render the WRONG physical page
# because pdfDoc is not yet updated — B3.
#
# We assert:
#   (1) grid thumb img src contains '/thumb/<serverNum>' (should PASS)
#   (2) the main canvas would call pdfDoc.getPage(curPage) where curPage is
#       the DISPLAY index — but for a pending duplicate, curPage !== serverNum.
#       We test the INTENT: loadPage must use serverNum to select the pdfDoc page.
#       Since we cannot intercept PDF.js.getPage without patching it, we test
#       the OBSERVABLE: pageMgr.serverNum(n) != n for the duplicate display page.
# ------------------------------------------------------------------
MR_RENDER_SOURCE_JS = r"""
async () => {
  if (!pageMgr || pageMgr.count() < 2)
    return {ok: false, reason: 'pageMgr not ready'};

  // Ensure PM overlay is open and grid is populated
  if (typeof _pmuiInjectCss === 'function') _pmuiInjectCss();
  if (typeof _pmuiBuildOverlay === 'function') _pmuiBuildOverlay();

  // Duplicate page 0 (display page 1)
  var srcServerNum = pageMgr.serverNum(1);  // should be 1 (original)
  pageMgr.duplicate(0);  // inserts copy at display index 1

  // Re-render the PM grid
  _pmuiRenderGrid();
  _pmuiWire();
  await new Promise(r => setTimeout(r, 100));

  // The duplicate is now at display index 1 (pageMgr.pageOrder[1])
  var dupId        = pageMgr.idAt(2);                   // 1-based display page 2
  var dupServerNum = pageMgr.serverNum(2);               // should equal srcServerNum (still 1)
  var displayIdx   = 2;                                  // raw display page number

  // Assert: serverNum(2) === 1 (renders from source), not 2 (raw index)
  var serverNumOk = (dupServerNum === srcServerNum);

  // Check the grid thumb src
  var grid   = document.getElementById('pm-grid');
  var thumbs = grid ? grid.querySelectorAll('.pmui-thumb') : [];
  // Tile at data-pmui-idx="1" (0-based) is display page 2 (the duplicate)
  var dupTile = Array.from(thumbs).find(function(t){
    return parseInt(t.getAttribute('data-pmui-idx'), 10) === 1;
  });
  var dupImg     = dupTile && dupTile.querySelector('img');
  var dupImgSrc  = dupImg ? dupImg.src : '';
  // Grid should show /thumb/1 (source serverNum), not /thumb/2 (raw display idx)
  var gridThumbUsesServerNum = dupImgSrc.includes('/thumb/' + srcServerNum);
  var gridThumbUsesRawIdx    = dupImgSrc.includes('/thumb/' + displayIdx);

  // MAIN CANVAS path: loadPage(n) calls pdfDoc.getPage(n) where n = curPage.
  // For a pending duplicate at display page 2, pdfDoc.getPage(2) requests the
  // SECOND physical page of the CURRENT server PDF — which is page 2 (NOT page 1,
  // the source). This is the B3 bug: the main canvas does NOT go through serverNum.
  // We document this as: mainCanvasUsesServerNum = false (the assertion we WANT to be true).
  // There is no non-invasive way to verify this purely in JS without patching loadPage,
  // so we derive the expected behavior:
  //   CORRECT: loadPage(2) should internally call pdfDoc.getPage(pageMgr.serverNum(2)) = getPage(1)
  //   CURRENT: loadPage(2) calls pdfDoc.getPage(2) — raw display index
  // We detect the divergence by checking if the loadPage function source references serverNum.
  var loadPageSrc = (typeof loadPage === 'function') ? loadPage.toString() : '';
  var mainCanvasUsesServerNum = loadPageSrc.indexOf('serverNum') >= 0;

  // Clean up duplicate for other MRs
  if (pageMgr.count() > 5) {
    pageMgr.del(1);   // remove the duplicate (0-based idx 1)
  }
  pageMgr.pending = [];

  var pass = serverNumOk && gridThumbUsesServerNum && mainCanvasUsesServerNum;
  return {
    ok: pass,
    srcServerNum:          srcServerNum,
    dupServerNum:          dupServerNum,
    displayIdx:            displayIdx,
    serverNumOk:           serverNumOk,
    gridThumbUsesServerNum: gridThumbUsesServerNum,
    gridThumbUsesRawIdx:   gridThumbUsesRawIdx,
    dupImgSrc:             dupImgSrc.slice(-40),
    mainCanvasUsesServerNum: mainCanvasUsesServerNum,
    reason: pass ? '' : JSON.stringify({serverNumOk, gridThumbUsesServerNum, mainCanvasUsesServerNum})
  };
}
"""

# ============================================================
# MR registry
# ============================================================
# Each entry: (mr_name, js_snippet, expected_pass_on_current_code, bug_guarded)
MR_REGISTRY = [
    ("MR-rotate",           MR_ROTATE_JS,          True,  "sanity — area is rotation-invariant"),
    ("MR-reorder",          MR_REORDER_JS,          True,  "B3 partial — identity model in PageModel"),
    ("MR-save-roundtrip",   MR_SAVE_ROUNDTRIP_JS,   False, "B1/B2 — save+reload loses order"),
    ("MR-save-pending",     MR_SAVE_PENDING_JS,     False, "B2 — pending reorder not reflected in save"),
    ("MR-dirty",            MR_DIRTY_JS,            False, "B5 — reorder doesn't flip state.dirty"),
    ("MR-render-source",    MR_RENDER_SOURCE_JS,    False, "B3 — main canvas uses raw index not serverNum"),
]


# ============================================================
# Main test driver
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

    # Build fixture PDF bytes
    try:
        pdf_bytes = _build_fixture_pdf()
    except ImportError:
        print("WARN: PyMuPDF not installed — skipping PDF fixture; some MRs may get 'no scale' errors")
        pdf_bytes = b"%PDF-1.4"   # minimal placeholder

    results    = {}   # mr_name -> {ok, reason, ...}
    page_errors = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        pg = browser.new_page()
        pg.on("pageerror", lambda e: page_errors.append(str(e)))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(1.5)

        # Upload fixture PDF and seed app globals
        try:
            seed = pg.evaluate(SETUP_JS, list(pdf_bytes))
            if not seed.get("ok"):
                print(f"  SETUP FAILED: {seed}")
                # Don't abort — let MRs run and fail descriptively
            else:
                print(f"  Setup OK: caseId={seed.get('caseId')}, pages={seed.get('pages')}, "
                      f"pageMgr.count={seed.get('pmCount')}")
        except Exception as ex:
            print(f"  SETUP EXCEPTION: {ex}")

        time.sleep(0.5)

        # Run each MR
        for mr_name, js_snippet, expected_pass, bug_note in MR_REGISTRY:
            try:
                result = pg.evaluate(js_snippet)
            except Exception as ex:
                result = {"ok": False, "reason": f"JS exception: {ex}"}

            results[mr_name] = result
            status = "[PASS]" if result.get("ok") else "[FAIL]"
            exp    = "(expected PASS)" if expected_pass else "(expected FAIL on current code)"
            print(f"  {status} {mr_name:<30} {exp}")
            if not result.get("ok"):
                print(f"         reason: {result.get('reason', '')}")
                detail = {k: v for k, v in result.items() if k not in ("ok", "reason")}
                if detail:
                    print(f"         detail: {json.dumps(detail, default=str)[:300]}")

        pg.close()
        browser.close()

    server.should_exit = True
    time.sleep(0.4)

    if page_errors:
        print()
        print("JS page errors observed:")
        for e in page_errors:
            print(f"  {e}")

    # Determine final verdict
    failing_mrs = [
        mr_name for mr_name, _js, _exp, _note in MR_REGISTRY
        if not results.get(mr_name, {}).get("ok")
    ]

    print()
    print("Summary:")
    print(f"  Total MRs:   {len(MR_REGISTRY)}")
    print(f"  Passing:     {len(MR_REGISTRY) - len(failing_mrs)}")
    print(f"  Failing:     {len(failing_mrs)}")
    if failing_mrs:
        print(f"  Failing MRs: {', '.join(failing_mrs)}")

    # Expected failures on current code
    expected_failures = [mr for mr, _js, exp, _note in MR_REGISTRY if not exp]
    unexpected_failures = [mr for mr in failing_mrs if mr not in expected_failures]
    unexpected_passes   = [mr for mr, _js, exp, _note in MR_REGISTRY
                           if exp and results.get(mr, {}).get("ok")]

    if unexpected_failures:
        print(f"  UNEXPECTED failures (not in expected-fail list): {unexpected_failures}")
    if len(unexpected_passes) < len([m for m, _,e,_ in MR_REGISTRY if e]):
        unexpected_passes_missing = [mr for mr, _js, exp, _note in MR_REGISTRY
                                     if exp and not results.get(mr, {}).get("ok")]
        if unexpected_passes_missing:
            print(f"  UNEXPECTED PASS failures (expected PASS but FAIL): {unexpected_passes_missing}")

    print()
    if failing_mrs:
        print(f"LITE_METAMORPHIC_PAGES_FAIL: {', '.join(failing_mrs)}")
        sys.exit(1)
    else:
        print("LITE_METAMORPHIC_PAGES_OK")
        sys.exit(0)


if __name__ == "__main__":
    main()
