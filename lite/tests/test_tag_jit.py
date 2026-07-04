"""
INV-2026-07-04-002 slice 4/4: JIT tag banner + per-page gate — integration proof.

Verifies the wizard's SET gate (blocked Step-1 Next at 0 tagged pages) has
been REPLACED, in the same diff, by a per-page JIT gate on the measure
tools themselves (lite/static/js/tag-jit.js): pressing a measure tool
(poly/dist/path/ref/count) on an untagged page refuses to arm and shows a
1-tap banner instead (tag chips, floor gets an auto kind+number so ONE tap
is always enough); non-measure tools (select/scale/annotations) and
pan/zoom/navigation are never gated. Also proves the underlying real
page-folder remap engine (reseedActivePageFolders / seedPageFolders /
_pflFolderHasUserDrawnObjects prune-guard) handles a floor->mezzanine
retag on a page with real drawn objects with zero object loss, and that
a single undo() fully reverses a retag.

6 sub-checks:
  untaggedBlocksAndBanner   setTool('poly') on an untagged page -> state.tool
                            unchanged + banner visible with all 6 tag chips
  bannerOneTapArmsAndSeeds  tapping the 'floor' chip -> tool arms (the
                            originally-requested tool), page gets tag+kind+
                            number in one tap, and the resulting PF_floor_<N>
                            folder is real (asserted via pageFolderIdFor +
                            folderById — not a mock)
  taggedArmsDirectly        setTool('poly') on an already-tagged page arms
                            immediately, banner never shown
  nonMeasureNeverBlocked    select tool / pan ('h' key) / zoom button all
                            work on an untagged page, banner stays hidden
  setGateIsGone             wizard Step-1 Next proceeds at 0 tagged pages,
                            window.confirm is never called
  realEngineRetagZeroLoss   page with 2 REAL PS objects retagged
                            floor(normal,3) -> mezzanine(2) via the real
                            writers: new PF_mezz_2 folder created, OLD
                            PF_floor_3 folder PRESERVED (prune guard fires
                            because it still owns user-drawn objects),
                            objects keep their original catId (zero loss),
                            and ONE undo() fully restores the pre-retag state

Emits LITE_TAG_JIT_OK on success.

    py -3 lite/tests/test_tag_jit.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8600):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


SETUP_GLOBALS = r"""
async () => {
  await new Promise(r => setTimeout(r, 400));  // let all dynamic scripts (incl. tag-jit.js) load
  return {done: true, wrapInstalled: window.__jitWrapped === true};
}
"""

# ---------------------------------------------------------------------------
# Sub-check 1 — untaggedBlocksAndBanner
# ---------------------------------------------------------------------------
CHECK_UNTAGGED_BLOCKS = r"""
() => {
  caseId = 'test'; pageCount = 5; pageTags = {}; excluded = {};
  curPage = 3; state.tool = 'select';
  PS = { 3: { objects: [], scale: null, annotations: [] } };
  _jitHideBanner();

  var before = state.tool;
  setTool('poly');
  var after = state.tool;
  var toolBlocked = (after === before) && (after !== 'poly');

  var banner = document.getElementById('jit-banner');
  var bannerShown = !!banner && banner.style.display !== 'none';
  var chipCount = banner ? banner.querySelectorAll('[data-jit-tag]').length : 0;

  return {
    wrapInstalled: window.__jitWrapped === true, before, after, toolBlocked,
    bannerShown, chipCount,
    pass: window.__jitWrapped === true && toolBlocked && bannerShown && chipCount === 6
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 2 — bannerOneTapArmsAndSeeds
# ---------------------------------------------------------------------------
CHECK_BANNER_ONE_TAP = r"""
() => {
  caseId = 'test'; pageCount = 5;
  pageTags = {}; excluded = {}; pageFloorNum = {}; pageFloorKind = {};
  curPage = 4; state.tool = 'select'; state.pageFolderMode = true;
  PS = { 4: { objects: [], scale: null, annotations: [] } };
  _jitHideBanner();

  setTool('dist');                        // blocked -> banner shown, pending tool = 'dist'
  var blockedFirst = state.tool !== 'dist';

  var banner = document.getElementById('jit-banner');
  var floorChip = banner ? banner.querySelector('[data-jit-tag="floor"]') : null;
  var chipFound = !!floorChip;
  if (floorChip) floorChip.click();       // the "1 tap"

  var toolArmed = state.tool === 'dist';
  var tagIsFloor = pageTags[4] === 'floor';
  var floorNumIsNumber = typeof pageFloorNum[4] === 'number';

  var folderId = (typeof pageFolderIdFor === 'function')
    ? pageFolderIdFor(4, 'floor', pageFloorNum[4], pageFloorKind[4]) : null;
  var folderExists = !!folderId && typeof folderById === 'function' && !!folderById(folderId);
  var folderIsRealFloorFolder = folderId && /^PF_floor_\d+$/.test(folderId);

  var bannerHidden = banner ? banner.style.display === 'none' : true;

  return {
    blockedFirst, chipFound, toolArmed, tagIsFloor, floorNumIsNumber,
    folderId, folderExists, folderIsRealFloorFolder, bannerHidden,
    pass: blockedFirst && chipFound && toolArmed && tagIsFloor && floorNumIsNumber &&
          folderExists && folderIsRealFloorFolder && bannerHidden
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 3 — taggedArmsDirectly
# ---------------------------------------------------------------------------
CHECK_TAGGED_ARMS_DIRECTLY = r"""
() => {
  caseId = 'test'; pageCount = 5; pageTags = { 2: 'site' }; excluded = {};
  curPage = 2; state.tool = 'select';
  PS = { 2: { objects: [], scale: null, annotations: [] } };
  _jitHideBanner();

  setTool('poly');
  var armed = state.tool === 'poly';
  var banner = document.getElementById('jit-banner');
  var bannerHidden = !banner || banner.style.display === 'none';

  return { armed, bannerHidden, pass: armed && bannerHidden };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 4 — nonMeasureNeverBlocked (select / pan / zoom, all on an
# UNTAGGED page)
# ---------------------------------------------------------------------------
CHECK_NON_MEASURE_UNBLOCKED = r"""
() => {
  caseId = 'test'; pageCount = 5; pageTags = {}; excluded = {};
  curPage = 3; state.tool = 'poly'; state.panTool = false;
  PS = { 3: { objects: [], scale: null, annotations: [] } };
  _jitHideBanner();

  // select: not a measure tool -> arms directly even on an untagged page
  setTool('select');
  var selectArmed = state.tool === 'select';

  // pan: toggled directly via the 'h' keydown handler, never goes through setTool
  var panBefore = state.panTool;
  document.dispatchEvent(new KeyboardEvent('keydown', { key: 'h', bubbles: true }));
  var panToggled = state.panTool !== panBefore;

  // zoom: onclick handlers never call setTool at all
  var zinBtn = document.getElementById('zin');
  var zoomThrew = false;
  if (zinBtn) { try { zinBtn.onclick(); } catch (e) { zoomThrew = true; } }

  var banner = document.getElementById('jit-banner');
  var bannerHidden = !banner || banner.style.display === 'none';

  return {
    selectArmed, panToggled, zoomThrew, bannerHidden,
    pass: selectArmed && panToggled && !zoomThrew && bannerHidden
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 5 — setGateIsGone (wizard Step-1 Next proceeds at 0 tagged)
# ---------------------------------------------------------------------------
CHECK_SET_GATE_GONE = r"""
() => {
  caseId = 'test'; pageCount = 3; pageTags = {}; excluded = {};
  if (typeof openOv !== 'function') return { pass: false, err: 'openOv missing' };
  openOv();
  var startStep = _lovsCurStep;
  var next = document.getElementById('ov-next');
  if (!next) return { pass: false, err: 'ov-next missing' };

  var _oc = window.confirm; var confirmCalls = 0;
  window.confirm = function() { confirmCalls++; return false; };
  next.click();
  var stepAfter = _lovsCurStep;
  window.confirm = _oc;

  var ov = document.getElementById('ov'); if (ov) ov.classList.remove('show');
  caseId = null;

  return {
    startStep, stepAfter, confirmCalls,
    pass: startStep === 1 && stepAfter === 2 && confirmCalls === 0
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 6 — realEngineRetagZeroLoss (floor -> mezzanine, real objects,
# real writers, real reseed, one undo)
# ---------------------------------------------------------------------------
CHECK_RETAG_ZERO_LOSS = r"""
() => {
  LAYERS.length = 0; FOLDERS.length = 0; initLayers();
  pageCount = 8; pageTags = {}; pageFloorNum = {}; pageFloorKind = {};
  PS = { 5: { objects: [], scale: null, annotations: [] } };
  state.pageFolderMode = true; caseId = 'test'; curPage = 5;

  // Establish the BEFORE state via the real writers: floor #3, kind=normal.
  liteSetTag(5, 'floor');
  liteSetFloorKind(5, 'normal');
  liteSetFloorNum(5, 3);
  reseedActivePageFolders();

  var gfaLayer = null;
  if (typeof childrenOf === 'function') {
    childrenOf('PF_floor_3').forEach(function(c) {
      if (c.kind === 'layer' && c.node.role === 'gfa') gfaLayer = c.node;
    });
  }
  var gfaLayerFound = !!gfaLayer;
  var gfaId = gfaLayer ? gfaLayer.id : 'MISSING';

  // 2 REAL objects (state objects, not mocks) drawn under that gfa layer.
  PS[5].objects.push(
    { kind: 'poly', catId: gfaId, pts: [{x:0,y:0},{x:100,y:0},{x:100,y:100},{x:0,y:100}] },
    { kind: 'poly', catId: gfaId, pts: [{x:200,y:0},{x:260,y:0},{x:260,y:60},{x:200,y:60}] }
  );

  var snapBefore = JSON.stringify({
    kind: pageFloorKind[5], num: pageFloorNum[5], tag: pageTags[5],
    objs: PS[5].objects, folderExists: !!folderById('PF_floor_3')
  });
  var undoStackBefore = (typeof undoStack !== 'undefined') ? undoStack.length : null;

  // -- RETAG: floor(normal,3) -> mezzanine(2). ONE pushUndo covers both writer calls.
  pushUndo();
  liteSetFloorKind(5, 'mezzanine');   // real writer — deletes pageFloorNum[5] internally
  liteSetFloorNum(5, 2);              // real writer — re-establishes a mezz floor#
  reseedActivePageFolders();

  var undoStackAfterRetag = (typeof undoStack !== 'undefined') ? undoStack.length : null;
  var pushedExactlyOne = undoStackAfterRetag === undoStackBefore + 1;

  var newFolderExists = !!folderById('PF_mezz_2');
  var oldFolderPreserved = !!folderById('PF_floor_3'); // prune guard: still owns user-drawn objects
  var objectsIntact = PS[5].objects.length === 2 &&
    PS[5].objects[0].catId === gfaId && PS[5].objects[1].catId === gfaId;

  // -- ONE undo() must fully restore the pre-retag state.
  undo();
  var snapAfterUndo = JSON.stringify({
    kind: pageFloorKind[5], num: pageFloorNum[5], tag: pageTags[5],
    objs: PS[5].objects, folderExists: !!folderById('PF_floor_3')
  });
  var fullyRestored = snapAfterUndo === snapBefore;
  var mezzGoneAfterUndo = !folderById('PF_mezz_2');

  return {
    gfaLayerFound, newFolderExists, oldFolderPreserved, objectsIntact,
    pushedExactlyOne, fullyRestored, mezzGoneAfterUndo,
    pass: gfaLayerFound && newFolderExists && oldFolderPreserved && objectsIntact &&
          pushedExactlyOne && fullyRestored && mezzGoneAfterUndo
  };
}
"""

CHECKS = [
    ("untaggedBlocksAndBanner",  CHECK_UNTAGGED_BLOCKS,          ["pass"]),
    ("bannerOneTapArmsAndSeeds", CHECK_BANNER_ONE_TAP,           ["pass"]),
    ("taggedArmsDirectly",       CHECK_TAGGED_ARMS_DIRECTLY,     ["pass"]),
    ("nonMeasureNeverBlocked",   CHECK_NON_MEASURE_UNBLOCKED,    ["pass"]),
    ("setGateIsGone",            CHECK_SET_GATE_GONE,            ["pass"]),
    ("realEngineRetagZeroLoss",  CHECK_RETAG_ZERO_LOSS,          ["pass"]),
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
        time.sleep(2.0)  # allow dynamic script load + setTimeout bootstrap

        try:
            setup_result = pg.evaluate(SETUP_GLOBALS)
            print(f"  SETUP: {setup_result}")
        except Exception as ex:
            print(f"  SETUP FAILED: {ex}")
            failures.append(f"setup threw: {ex}")

        print()
        print("LITE-TAG-JIT checks:")
        for name, scenario, required_keys in CHECKS:
            try:
                result = pg.evaluate(scenario)
            except Exception as ex:
                print(f"  {name:28s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
                continue

            ok = all(result.get(k) is True for k in required_keys)
            status = "PASS" if ok else "FAIL"
            print(f"  {name:28s} -> {status}  {result}")
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
        print("LITE_TAG_JIT_FAIL")
        sys.exit(1)
    else:
        print("LITE_TAG_JIT_OK")


if __name__ == "__main__":
    main()
