"""
BMA-Plan Lite — page-manager-ui.js real-path regression test (INV-2026-05-29-LPM).

Drives the REAL user path: pmOpenManager() / Shift+F12 opens #pm-overlay
(NOT #ov-grid, NOT the LOVS wizard).  Asserts the management grid is
reachable and functional.

4 sub-checks:
  pmOverlay       after pmOpenManager(), #pm-overlay has class "show" AND
                  #pm-grid contains N .pmui-thumb tiles === pageCount.
                  THIS is the real-reachability assertion — independent of
                  #ov-grid and raw openOv.
  dupButtons      every tile has exactly one .pmui-dup button.
  reorderPending  programmatic pageMgr.reorder(1,0) + _pmuiRenderGrid()/_pmuiWire()
                  → first tile data-pmui-idx===0, pageMgr.pending.length===1,
                  #pmui-apply visible.
  deleteGuard     reduce to 1 page in model + re-render → 0 .pmui-del shown.

Emits LITE_PAGE_MANAGER_UI_OK on success, exits 0.
Emits LITE_PAGE_MANAGER_UI_FAIL + failing checks, exits 1 on any failure.

Run:
    py -3 lite/tests/test_page_manager_ui.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8460):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ---------------------------------------------------------------------------
# Seed: build a 3-page pageMgr in the browser context without uploading a PDF.
# ---------------------------------------------------------------------------
SEED_GLOBALS = r"""
async () => {
  await new Promise(r => setTimeout(r, 300));

  pageCount = 3;
  curPage   = 1;
  caseId    = 'pmui-test-mock';

  PS = {
    1: {objects: [], scale: null, annotations: []},
    2: {objects: [], scale: null, annotations: []},
    3: {objects: [], scale: null, annotations: []}
  };
  pageTags      = {};
  pageFloorNum  = {};
  pageFloorKind = {};
  pageNames     = {};
  pageRot       = {};
  excluded      = {};

  if (typeof _pmSeed === 'function') {
    _pmSeed(null);
  } else {
    pageMgr = new PageModel();
    for (var i = 1; i <= 3; i++) {
      var id = 'pg' + (i - 1);
      pageMgr.pageOrder.push(id);
      pageMgr.PS_by_id[id]    = {objects: [], scale: null, annotations: []};
      pageMgr.meta_by_id[id]  = {tag: '', rot: 0, excl: false, floorKind: '', floorNum: null, name: ''};
      pageMgr.originNum[id]   = i;
      pageMgr._initialIds.push(id);
    }
  }

  // Stub api() so thumb src is predictable (no real server needed)
  window._realApi = window.api;
  window.api = function(path) { return '/stub' + path; };

  return {done: true, pmCount: pageMgr ? pageMgr.count() : 0};
}
"""

# ---------------------------------------------------------------------------
# Sub-check 1 — pmOverlay
# Call pmOpenManager() and assert #pm-overlay.show + #pm-grid tile count.
# This is the real-reachability check — independent of #ov-grid / LOVS wizard.
# Also verify via Shift+F12 dispatch.
# ---------------------------------------------------------------------------
CHECK_PM_OVERLAY = r"""
async () => {
  // Close any residual overlay
  if (typeof _pmCloseOverlay === 'function') _pmCloseOverlay();
  await new Promise(r => setTimeout(r, 30));

  // Call the real public entry
  pmOpenManager();
  await new Promise(r => setTimeout(r, 200));

  var ov     = document.getElementById('pm-overlay');
  var isShow = ov && ov.classList.contains('show');
  var grid   = document.getElementById('pm-grid');
  var pmThumbs = grid ? grid.querySelectorAll('.pmui-thumb') : [];

  // Every tile must have a .pmui-dup
  var allHaveDup = Array.from(pmThumbs).every(function(t){
    return t.querySelector('.pmui-dup') !== null;
  });
  // 3-page model: every tile must have .pmui-del
  var allHaveDel = Array.from(pmThumbs).every(function(t){
    return t.querySelector('.pmui-del') !== null;
  });
  // Action bar
  var barExists = !!document.getElementById('pmui-bar');

  // Also verify Shift+F12 opens it (close first, then dispatch)
  _pmCloseOverlay();
  await new Promise(r => setTimeout(r, 30));
  document.dispatchEvent(new KeyboardEvent('keydown', {key:'F12', shiftKey:true, bubbles:true}));
  await new Promise(r => setTimeout(r, 100));
  var ov2 = document.getElementById('pm-overlay');
  var shiftF12Works = ov2 && ov2.classList.contains('show');

  // #ov-grid must NOT be the host — pm-grid is separate
  var usesOwnGrid = !!(grid && grid.id === 'pm-grid');

  return {
    overlayExists:   !!ov,
    overlayShow:     !!isShow,
    pmThumbCount:    pmThumbs.length,
    allHaveDup:      allHaveDup,
    allHaveDel:      allHaveDel,
    barExists:       barExists,
    shiftF12Works:   shiftF12Works,
    usesOwnGrid:     usesOwnGrid,
    allOk: !!isShow && pmThumbs.length === 3 && allHaveDup && allHaveDel &&
           barExists && shiftF12Works && usesOwnGrid
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 2 — dupButtons: each tile has exactly 1 .pmui-dup
# ---------------------------------------------------------------------------
CHECK_DUP_BUTTONS = r"""
() => {
  var g = document.getElementById('pm-grid');
  var thumbs = g ? Array.from(g.querySelectorAll('.pmui-thumb')) : [];
  var counts = thumbs.map(function(t){ return t.querySelectorAll('.pmui-dup').length; });
  var allOne = counts.every(function(c){ return c === 1; });
  return {
    dupCounts: counts,
    allExactlyOne: allOne,
    allOk: allOne && counts.length === 3
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 3 — reorderPending
# Reorder page index 1 → position 0; re-render grid; assert pending+apply.
# ---------------------------------------------------------------------------
CHECK_REORDER_PENDING = r"""
async () => {
  // Re-seed pageMgr to clean 3-page state
  _pmSeed(null);
  pageMgr.pending   = [];
  pageMgr.undoStack = [];

  // Ensure overlay is open and grid exists
  pmOpenManager();
  await new Promise(r => setTimeout(r, 100));

  // Reorder display-position 1 → 0
  pageMgr.reorder(1, 0);

  // Re-render (what drop handler does)
  _pmuiRenderGrid();
  _pmuiWire();
  await new Promise(r => setTimeout(r, 50));

  var g = document.getElementById('pm-grid');
  var thumbs = g ? Array.from(g.querySelectorAll('.pmui-thumb')) : [];
  var firstIdx = thumbs.length > 0 ? parseInt(thumbs[0].getAttribute('data-pmui-idx'), 10) : -1;
  var firstIdxOk = firstIdx === 0;
  var pendingCount = pageMgr.pending.length;
  var applyBtn = document.getElementById('pmui-apply');
  var applyVisible = applyBtn && applyBtn.style.display !== 'none';

  return {
    pendingCount:  pendingCount,
    firstIdx:      firstIdx,
    firstIdxOk:    firstIdxOk,
    applyVisible:  !!applyVisible,
    thumbCount:    thumbs.length,
    allOk: pendingCount === 1 && firstIdxOk && !!applyVisible && thumbs.length === 3
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 4 — deleteGuard
# Reduce pageMgr to 1 page; re-render; assert 0 .pmui-del buttons.
# ---------------------------------------------------------------------------
CHECK_DELETE_GUARD = r"""
async () => {
  _pmSeed(null);
  var firstId = pageMgr.pageOrder[0];
  pageMgr.pageOrder = [firstId];
  pageMgr.pending   = [];

  // Overlay must be open
  pmOpenManager();
  await new Promise(r => setTimeout(r, 100));

  // Re-render into the already-open overlay
  _pmuiRenderGrid();
  _pmuiWire();
  await new Promise(r => setTimeout(r, 50));

  var g       = document.getElementById('pm-grid');
  var thumbs  = g ? g.querySelectorAll('.pmui-thumb') : [];
  var delBtns = g ? g.querySelectorAll('.pmui-del')   : [];
  var dupBtns = g ? g.querySelectorAll('.pmui-dup')   : [];

  return {
    thumbCount: thumbs.length,
    delCount:   delBtns.length,
    dupCount:   dupBtns.length,
    allOk: thumbs.length === 1 && delBtns.length === 0 && dupBtns.length === 1
  };
}
"""

CHECKS = [
    ("pmOverlay",      CHECK_PM_OVERLAY,      ["allOk"]),
    ("dupButtons",     CHECK_DUP_BUTTONS,     ["allOk"]),
    ("reorderPending", CHECK_REORDER_PENDING, ["allOk"]),
    ("deleteGuard",    CHECK_DELETE_GUARD,    ["allOk"]),
]


def main():
    from server_lite import app as lite_app
    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)

    failures = []
    page_errors = []

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.on("pageerror", lambda e: page_errors.append(f"pageerror: {e}"))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(2.0)

        # Seed globals
        try:
            seed_result = pg.evaluate(SEED_GLOBALS)
            print(f"  Seed OK: {seed_result}")
        except Exception as ex:
            print(f"  SEED FAILED: {ex}")
            failures.append(f"seed threw: {ex}")

        print()
        print("LITE-PAGE-MANAGER-UI checks:")
        for name, scenario, required_keys in CHECKS:
            try:
                result = pg.evaluate(scenario)
            except Exception as ex:
                print(f"  {name:30s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
                continue

            ok = all(result.get(k) is True for k in required_keys)
            status = "PASS" if ok else "FAIL"
            print(f"  {name:30s} -> {status}  {result}")
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
        print("LITE_PAGE_MANAGER_UI_FAIL")
        sys.exit(1)
    else:
        print("LITE_PAGE_MANAGER_UI_OK")
        sys.exit(0)


if __name__ == "__main__":
    main()
