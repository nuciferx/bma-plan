"""
LROTATE-1: test_page_rotate.py — verifies render-rotation per page.

Four checks (all driven via Playwright / real DOM events):

  rotateRightAccumulates  — call rotatePage(90) four times; after the 4th call
                            pageRot[curPage] wraps back to 0.
  rotateLeftWraps         — from 0, call rotatePage(-90) once;
                            pageRot[curPage] === 270.
  rotationPersistsRoundTrip — set page rotation to 90, build .bmaplan JSON via
                            buildPageStore/pageRotations path, clear state,
                            restore via loadProto, assert pageRot[curPage] === 90.
  shiftLDoesNotRotate     — dispatch Shift+L -> rotation UNCHANGED (loupe may
                            toggle but rotation must stay the same); dispatch
                            Shift+R -> rotation UNCHANGED; plain L -> loupe
                            toggles; plain R -> tool becomes 'ref'.

Emits LITE_PAGE_ROTATE_OK on success.

    py -3 lite/tests/test_page_rotate.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8510):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ---------------------------------------------------------------------------
# Shared setup: fake pageCount + curPage so rotatePage guard passes.
# loadPage is stubbed to avoid network call (no real PDF).
# ---------------------------------------------------------------------------
SETUP_STATE = r"""
pageCount = 5;
curPage = 1;
pageRot = {};
// Stub loadPage so rotatePage doesn't try to fetch a real URL
window._origLoadPage = window.loadPage;
window.loadPage = function(n) { /* stub — no PDF */ };
"""

TEARDOWN = r"""
if (window._origLoadPage) window.loadPage = window._origLoadPage;
"""


# ---------------------------------------------------------------------------
# SC1 — rotateRightAccumulates
# rotatePage(90) four times starting from 0 must wrap to 0.
# Drive via real menu-click on mi-rot-right for the FIRST call, then direct
# for the rest (spec requires at least one menu-click check).
# ---------------------------------------------------------------------------
SC1 = r"""
async () => {
  """ + SETUP_STATE + r"""
  pageRot[curPage] = 0;
  var before = pageRot[curPage];

  // First rotation via real menu click on mi-rot-right
  document.getElementById('mi-rot-right').click();
  var after1 = pageRot[curPage];   // expect 90

  // Remaining three via direct function call
  rotatePage(90);
  var after2 = pageRot[curPage];   // expect 180
  rotatePage(90);
  var after3 = pageRot[curPage];   // expect 270
  rotatePage(90);
  var after4 = pageRot[curPage];   // expect 0 (wrapped)

  """ + TEARDOWN + r"""
  var pass = (before === 0) && (after1 === 90) && (after2 === 180) && (after3 === 270) && (after4 === 0);
  return { before, after1, after2, after3, after4, pass };
}
"""


# ---------------------------------------------------------------------------
# SC2 — rotateLeftWraps
# From 0, one rotatePage(-90) must give 270.
# Drive via real menu click on mi-rot-left.
# ---------------------------------------------------------------------------
SC2 = r"""
async () => {
  """ + SETUP_STATE + r"""
  pageRot[curPage] = 0;

  document.getElementById('mi-rot-left').click();
  var result = pageRot[curPage];   // expect 270

  """ + TEARDOWN + r"""
  var pass = (result === 270);
  return { result, pass };
}
"""


# ---------------------------------------------------------------------------
# SC3 — rotationPersistsRoundTrip
# Set pageRot[curPage]=90, build .bmaplan JSON (pageRotations = pageRot),
# clear state, loadProto, assert pageRot[curPage]===90.
# ---------------------------------------------------------------------------
SC3 = r"""
async () => {
  """ + SETUP_STATE + r"""
  var pg = curPage;
  pageRot[pg] = 90;

  // Build a minimal .bmaplan doc (mirrors the save button path)
  var doc = {
    version: 1, app: 'bma-plan-lite', pdfName: 'test.pdf', totalPages: 5,
    pageStore: buildPageStore(),
    pageRotations: pageRot,
    pageTags: {}, pageNames: {}, projectInfo: {name:''},
    siteOrientation: {}, excludedPages: [],
    pageFloorKind: {}, pageFloorNum: {},
    liteLayers: (typeof layersInOrder === 'function') ?
      layersInOrder().map(function(l){ return {id:l.id,name:l.name,color:l.color,role:l.role,order:l.order,parentId:l.parentId!==undefined?l.parentId:null}; }) : [],
    liteGroups: (typeof foldersInOrder === 'function') ?
      foldersInOrder().map(function(f){ return {id:f.id,name:f.name,color:f.color,parentId:f.parentId!==undefined?f.parentId:null,order:f.order}; }) : [],
    reportVars: []
  };
  var docJson = JSON.stringify(doc);

  // Clear rotation state
  pageRot = {};
  var before = pageRot[pg];  // undefined / 0 — cleared

  // Restore via loadProto
  loadProto(JSON.parse(docJson));

  var after = pageRot[pg];   // expect 90

  """ + TEARDOWN + r"""
  var pass = (after === 90);
  return { before, after, pass };
}
"""


# ---------------------------------------------------------------------------
# SC4 — shiftLDoesNotRotate (formerly keyboardShiftLAndShiftR)
# After the Shift+L conflict fix: Shift+L must NOT rotate the page — it falls
# through to the plain-L branch which toggles loupe.  Shift+R must also NOT
# rotate — it falls through to the plain-R / tool map ('ref').
# plain L (no shift) -> state.loupe toggles (NOT rotation).
# plain R (no shift) -> tool='ref' (NOT rotation).
# ---------------------------------------------------------------------------
SC4 = r"""
async () => {
  """ + SETUP_STATE + r"""
  pageRot[curPage] = 180;   // sentinel — must stay 180 throughout
  state.tool = 'select';    // neutral start

  // --- Shift+L -> loupe toggles, rotation MUST NOT change ---
  var loupeBefore = state.loupe;
  var rotBefore = pageRot[curPage];
  window.dispatchEvent(new KeyboardEvent('keydown', {bubbles:true, cancelable:true, key:'L', shiftKey:true}));
  var loupeAfterShiftL = state.loupe;
  var rotAfterShiftL = pageRot[curPage];
  // loupe toggled (Shift is down but the handler only checks key, not shiftKey for loupe)
  // rotation must be unchanged
  var shiftLNoRotate = (rotAfterShiftL === rotBefore);

  // --- Shift+R -> tool switches to 'ref', rotation MUST NOT change ---
  var rotBefore2 = pageRot[curPage];
  window.dispatchEvent(new KeyboardEvent('keydown', {bubbles:true, cancelable:true, key:'R', shiftKey:true}));
  var rotAfterShiftR = pageRot[curPage];
  var shiftRNoRotate = (rotAfterShiftR === rotBefore2);

  // --- Plain L (no shift) -> loupe toggle (NOT rotation) ---
  var loupeBefore2 = state.loupe;
  var rotBefore3 = pageRot[curPage];
  window.dispatchEvent(new KeyboardEvent('keydown', {bubbles:true, cancelable:true, key:'l', shiftKey:false}));
  var loupeAfter = state.loupe;
  var rotAfterL = pageRot[curPage];
  var loupeOk = (loupeAfter !== loupeBefore2) && (rotAfterL === rotBefore3);

  // --- Plain R (no shift) -> tool='ref' (NOT rotation) ---
  var rotBefore4 = pageRot[curPage];
  window.dispatchEvent(new KeyboardEvent('keydown', {bubbles:true, cancelable:true, key:'r', shiftKey:false}));
  var toolAfterR = state.tool;
  var rotAfterR = pageRot[curPage];
  var refOk = (toolAfterR === 'ref') && (rotAfterR === rotBefore4);

  """ + TEARDOWN + r"""
  var pass = shiftLNoRotate && shiftRNoRotate && loupeOk && refOk;
  return { rotAfterShiftL, rotAfterShiftR, shiftLNoRotate, shiftRNoRotate, loupeAfter, loupeOk, toolAfterR, refOk, pass };
}
"""


CHECKS = [
    ("rotateRightAccumulates",      SC1, ["pass"]),
    ("rotateLeftWraps",             SC2, ["pass"]),
    ("rotationPersistsRoundTrip",   SC3, ["pass"]),
    ("shiftLDoesNotRotate",          SC4, ["pass"]),
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
        time.sleep(0.6)

        print()
        print("LROTATE-1 checks:")
        for name, scenario, required_keys in CHECKS:
            pg.reload(wait_until="networkidle")
            time.sleep(0.4)

            try:
                result = pg.evaluate(scenario)
            except Exception as ex:
                print(f"  {name:40s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
                continue

            if result and result.get("skip"):
                print(f"  {name:40s} -> SKIP  ({result['skip']})")
                failures.append(f"check '{name}' skipped: {result['skip']}")
                continue

            ok = all(result.get(k) is True for k in required_keys)
            status = "PASS" if ok else "FAIL"
            print(f"  {name:40s} -> {status}  {result}")
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
        print("LITE_PAGE_ROTATE_FAIL")
        sys.exit(1)
    else:
        print("LITE_PAGE_ROTATE_OK")


if __name__ == "__main__":
    main()
