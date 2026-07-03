"""
INV-20260703-layer-linkage -- sprint B4 acceptance test.

Verifies the H1 "wrong-layer draw = delete + redraw" fix: an already-drawn
object (plain poly, CFSS instance, or a multi-selection) can be re-filed
onto a different layer in place via moveObjectToLayer/moveObjectsToLayer
(static/js/layer-move.js), with catId+semanticTag updated and every rollup
(the object-agg tuple engine) instantly consistent.

Checks:
  moveUpdatesCatIdAndTag   moveObjectToLayer(poly, customDedLayer) sets
                            catId+semanticTag to the target layer/role.
  moveShiftsByRole          ObjectAgg.byRole(): gfa loses the object's area,
                            ded gains it (net change == object area).
  moveOracleOk               assertEnginesAgree().ok stays true after the move.
  undoRestores                undo() restores catId+semanticTag+byRole totals
                              to their pre-move values.
  cfssMasterMoves            moveObjectToLayer(instance, layer) retargets the
                              MASTER's catId+semanticTag via updateMaster
                              (confirm() stubbed true).
  cfssBothInstancesShift    byRole() reflects the shift for BOTH instances of
                              the moved master (2 floors) -- rollupCatId makes
                              every instance resolve through the one master.
  cfssOracleOk                assertEnginesAgree().ok stays true after the
                              CFSS master move.
  propsSelectExists           #p-move <select> exists in #props with >1 option
                              after showProps(obj) on a selected object.
  propsSelectMoves            dispatching 'change' on #p-move moves the object.
  objMenuRowExists             right-click objmenu (showObjMenu) contains a
                              "ย้ายไปเลเยอร์" row.
  objMenuDispatchMoves         clicking that row opens a chooser popup; clicking
                              a layer row in it moves the object (full dispatch
                              chain, not just DOM presence).
  multiMovesAll                 moveObjectsToLayer(selSet, layer) with 2 objects
                              in state.selSet moves BOTH (single pushUndo).
  multiMenuLabelShowsCount   the objmenu row label for a multi-selection reads
                              "ย้ายทั้งหมด (2) ไปเลเยอร์ ▸".

Emits LITE_B4_MOVE_LAYER_OK on success.

    py -3 lite/tests/test_b4_move_layer.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=9200):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# Dynamically-loaded modules (layer-move.js via page-folder-layers.js;
# cross-floor-shapes.js also dynamic) -- poll until both are ready.
JS_WAIT_FOR_MODULES = r"""
async () => {
  for (let i = 0; i < 60; i++) {
    if (typeof window.moveObjectToLayer === 'function' && typeof window.addMaster === 'function') break;
    await new Promise(r => setTimeout(r, 50));
  }
  await new Promise(r => setTimeout(r, 50));
}
"""

SCENARIO = r"""
() => {
  const out = {};
  const dummy = document.createElement('canvas'); dummy.width = 400; dummy.height = 400;
  window.curImg = dummy;

  function reseed() {
    LAYERS.length = 0; FOLDERS.length = 0; initLayers();
    ROLE_DEFS.forEach(function(rd) { state.catVis[rd.id] = true; state.catLock[rd.id] = false; });
  }
  function resetPS() {
    for (var k in PS) delete PS[k];
    for (var k in excluded) delete excluded[k];
    for (var k in pageTags) delete pageTags[k];
    for (var k in pageFloorNum) delete pageFloorNum[k];
    for (var k in pageFloorKind) delete pageFloorKind[k];
    if (window.MASTERS) window.MASTERS = {};
  }
  function resetUndo() { undoStack.length = 0; redoStack.length = 0; }
  function rect(w, h, ox, oy) { ox = ox || 0; oy = oy || 0; return [{x:ox,y:oy},{x:ox+w,y:oy},{x:ox+w,y:oy+h},{x:ox,y:oy+h}]; }

  // -----------------------------------------------------------------------
  // (i) plain poly move + byRole shift + oracle, (ii) undo
  // -----------------------------------------------------------------------
  {
    reseed(); resetPS(); resetUndo();
    pageCount = 1; curPage = 1;
    PS[1] = {objects: [], scale: {pts_per_m: 1}, annotations: []};
    const obj = {id: 501, kind: 'poly', pts: rect(10, 10), catId: 'gfa', counting: false, semanticTag: 'gross_floor_area', dimVisible: true};
    PS[1].objects.push(obj);
    const custDed = addLayer('ded', 'Custom Ded', '#ff6b6b');

    const brBefore = window.ObjectAgg.byRole();
    const gfaBefore = (brBefore.gfa && brBefore.gfa.area) || 0;
    const dedBefore = (brBefore.ded && brBefore.ded.area) || 0;

    const n = moveObjectToLayer(obj, custDed.id);
    const catIdOk = PS[1].objects[0].catId === custDed.id;
    const tagOk = PS[1].objects[0].semanticTag === 'deduction_opening';

    const brAfter = window.ObjectAgg.byRole();
    const gfaAfter = (brAfter.gfa && brAfter.gfa.area) || 0;
    const dedAfter = (brAfter.ded && brAfter.ded.area) || 0;
    const shiftedOk = Math.abs((gfaBefore - gfaAfter) - 100) < 1e-6 && Math.abs((dedAfter - dedBefore) - 100) < 1e-6;

    const oracle1 = window.ObjectAgg.assertEnginesAgree();

    out.moveUpdatesCatIdAndTag = !!(n === 1 && catIdOk && tagOk);
    out.moveShiftsByRole = !!shiftedOk;
    out.moveOracleOk = !!oracle1.ok;
    out._moveDetail = {n, catIdOk, tagOk, gfaBefore, gfaAfter, dedBefore, dedAfter, oracleDiffs: oracle1.diffs};

    undo();
    const objAfterUndo = PS[1].objects[0];
    const undoCatOk = objAfterUndo.catId === 'gfa';
    const undoTagOk = objAfterUndo.semanticTag === 'gross_floor_area';
    const brUndo = window.ObjectAgg.byRole();
    const gfaUndo = (brUndo.gfa && brUndo.gfa.area) || 0;
    const dedUndo = (brUndo.ded && brUndo.ded.area) || 0;
    out.undoRestores = !!(undoCatOk && undoTagOk && Math.abs(gfaUndo - gfaBefore) < 1e-6 && Math.abs(dedUndo - dedBefore) < 1e-6);
    out._undoDetail = {undoCatOk, undoTagOk, gfaUndo, dedUndo};
  }

  // -----------------------------------------------------------------------
  // (iii) CFSS instance move -> master catId/tag change, both instances shift
  // -----------------------------------------------------------------------
  {
    reseed(); resetPS(); resetUndo();
    pageCount = 2; curPage = 1;
    PS[1] = {objects: [], scale: {pts_per_m: 1}, annotations: []};
    PS[2] = {objects: [], scale: {pts_per_m: 1}, annotations: []};
    const custDed2 = addLayer('ded', 'Custom Ded 2', '#ff6b6b');

    const mid = addMaster('Shared Core', [{x_m:0,y_m:0},{x_m:4,y_m:0},{x_m:4,y_m:3},{x_m:0,y_m:3}], '#4c8dff',
      {catId: 'gfa', semanticTag: 'gross_floor_area'});
    const inst1 = makeInstance(mid, {x: 0, y: 0});
    const inst2 = makeInstance(mid, {x: 0, y: 0});
    PS[1].objects.push(inst1);
    PS[2].objects.push(inst2);

    const brBefore = window.ObjectAgg.byRole();
    const gfaBefore = (brBefore.gfa && brBefore.gfa.area) || 0;
    const dedBefore = (brBefore.ded && brBefore.ded.area) || 0;

    const origConfirm = window.confirm; window.confirm = () => true;
    const n = moveObjectToLayer(inst1, custDed2.id);
    window.confirm = origConfirm;

    const masterCatOk = masterById(mid).catId === custDed2.id;
    const masterTagOk = masterById(mid).semanticTag === 'deduction_opening';

    const brAfter = window.ObjectAgg.byRole();
    const gfaAfter = (brAfter.gfa && brAfter.gfa.area) || 0;
    const dedAfter = (brAfter.ded && brAfter.ded.area) || 0;
    const expectedShift = 24; // 12 m^2 per instance x 2 instances

    out.cfssMasterMoves = !!(n === 1 && masterCatOk && masterTagOk);
    out.cfssBothInstancesShift = !!(Math.abs((gfaBefore - gfaAfter) - expectedShift) < 1e-6 &&
      Math.abs((dedAfter - dedBefore) - expectedShift) < 1e-6);
    const oracle3 = window.ObjectAgg.assertEnginesAgree();
    out.cfssOracleOk = !!oracle3.ok;
    out._cfssDetail = {n, masterCatOk, masterTagOk, gfaBefore, gfaAfter, dedBefore, dedAfter, oracleDiffs: oracle3.diffs};
  }

  // -----------------------------------------------------------------------
  // (iv) property-panel select + objmenu row exist and both dispatch a move
  // -----------------------------------------------------------------------
  {
    reseed(); resetPS(); resetUndo();
    pageCount = 1; curPage = 1;
    PS[1] = {objects: [], scale: {pts_per_m: 1}, annotations: []};
    const obj4 = {id: 601, kind: 'poly', pts: rect(5, 5), catId: 'gfa', counting: false, semanticTag: 'gross_floor_area', dimVisible: true};
    PS[1].objects.push(obj4);
    const custUse = addLayer('use', 'Custom Use X', '#39d98a');
    const custSite = addLayer('site', 'Custom Site X', '#c084fc');

    state.sel = obj4; state.selSet = [obj4];
    showProps(obj4);
    const selEl = document.getElementById('p-move');
    const selExists = !!selEl;
    const selHasOptions = !!(selEl && selEl.options && selEl.options.length > 1);
    let selectMoveOk = false;
    if (selEl) { selEl.value = custUse.id; selEl.dispatchEvent(new Event('change')); selectMoveOk = obj4.catId === custUse.id; }

    window.showObjMenu(120, 120, obj4);
    const rowEls = Array.from(document.querySelectorAll('.objmenu .objmenu-row'));
    const moveRowEl = rowEls.find(function(r) { return r.textContent.indexOf('ย้ายไปเลเยอร์') >= 0; });
    const objMenuRowExists = !!moveRowEl;
    let dispatchMoveOk = false;
    if (moveRowEl) {
      moveRowEl.click();
      const layerRows = Array.from(document.querySelectorAll('.objmenu .objmenu-row'));
      const targetRow = layerRows.find(function(r) { return r.textContent.indexOf('Custom Site X') >= 0; });
      if (targetRow) targetRow.click();
      dispatchMoveOk = obj4.catId === custSite.id && obj4.semanticTag === 'site_land_area';
    }
    if (typeof window.closeObjMenu === 'function') window.closeObjMenu();

    out.propsSelectExists = !!(selExists && selHasOptions);
    out.propsSelectMoves = !!selectMoveOk;
    out.objMenuRowExists = !!objMenuRowExists;
    out.objMenuDispatchMoves = !!dispatchMoveOk;
    out._ivDetail = {selExists, selHasOptions, selectMoveOk, objMenuRowExists, dispatchMoveOk};
  }

  // -----------------------------------------------------------------------
  // (v) multi-select move moves ALL + objmenu label shows count
  // -----------------------------------------------------------------------
  {
    reseed(); resetPS(); resetUndo();
    pageCount = 1; curPage = 1;
    PS[1] = {objects: [], scale: {pts_per_m: 1}, annotations: []};
    const o1 = {id: 701, kind: 'poly', pts: rect(4, 4), catId: 'gfa', counting: false, semanticTag: 'gross_floor_area', dimVisible: true};
    const o2 = {id: 702, kind: 'poly', pts: rect(6, 6), catId: 'gfa', counting: false, semanticTag: 'gross_floor_area', dimVisible: true};
    PS[1].objects.push(o1, o2);
    const custOpen = addLayer('open', 'Custom Open X', '#ffb454');

    state.selSet = [o1, o2]; state.sel = o1;
    window.showObjMenu(130, 130, o1);
    const rows = Array.from(document.querySelectorAll('.objmenu .objmenu-row')).map(function(r) { return r.textContent; });
    const multiLabelOk = rows.some(function(t) { return t.indexOf('ย้ายทั้งหมด (2)') >= 0; });
    if (typeof window.closeObjMenu === 'function') window.closeObjMenu();

    const n = moveObjectsToLayer(state.selSet, custOpen.id);
    out.multiMovesAll = !!(n === 2 && o1.catId === custOpen.id && o2.catId === custOpen.id &&
      o1.semanticTag === 'legal_open_space' && o2.semanticTag === 'legal_open_space');
    out.multiMenuLabelShowsCount = !!multiLabelOk;
    out._vDetail = {n, o1cat: o1.catId, o2cat: o2.catId, multiLabelOk};
  }

  reseed(); resetPS(); resetUndo();
  return out;
}
"""

CHECKS = [
    "moveUpdatesCatIdAndTag",
    "moveShiftsByRole",
    "moveOracleOk",
    "undoRestores",
    "cfssMasterMoves",
    "cfssBothInstancesShift",
    "cfssOracleOk",
    "propsSelectExists",
    "propsSelectMoves",
    "objMenuRowExists",
    "objMenuDispatchMoves",
    "multiMovesAll",
    "multiMenuLabelShowsCount",
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
        pg.evaluate(JS_WAIT_FOR_MODULES)
        result = pg.evaluate(SCENARIO)
        pg.close()
        b.close()

    server.should_exit = True
    time.sleep(0.4)

    for e in page_errors:
        print("  JS ERROR:", e)

    print()
    print("LITE-B4-MOVE-LAYER checks:")
    for k in CHECKS:
        ok = result.get(k)
        print(f"  {k:26s} -> {ok}")
        if ok is not True:
            failures.append(f"check '{k}' = {ok!r} (expected True)")

    for dk in ("_moveDetail", "_undoDetail", "_cfssDetail", "_ivDetail", "_vDetail"):
        if dk in result:
            print(f"  {dk}: {result[dk]}")

    if page_errors:
        failures.append(f"{len(page_errors)} page error(s) during scenario")

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_B4_MOVE_LAYER_FAIL")
        sys.exit(1)
    else:
        print("LITE_B4_MOVE_LAYER_OK")


if __name__ == "__main__":
    main()
