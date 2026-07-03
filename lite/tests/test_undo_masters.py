"""
B4 follow-up -- undo/redo covers the CFSS MASTERS registry.

The ui-lite undo system (_docSnap/_applyDoc/pushUndo/undo/redo in ui-lite.html)
deep-copies the page store PS but historically ignored window.MASTERS (the
cross-floor-shapes master registry). Result: promoting a poly to a master, or
retargeting a master's layer via layer-move.js (updateMaster), or editing a
master, could NOT be undone -- Ctrl+Z restored PS while MASTERS kept the mutated
state, so instances (kind:'instance', masterId refs in PS) pointed at a master
whose catId/layer had changed.

Fix: _docSnap() now serialises CFSS.snapshotMasters() under an additive `masters`
key; _applyDoc() calls CFSS.restoreMasters(d.masters). Old snapshots (no key)
restore gracefully (MASTERS left untouched). cfssCommitPromote / cfssCommitEdit
now pushUndo() before their first mutation (layer-move.js already did).

Checks:
  promoteUndo         promote poly -> undo -> master gone from MASTERS AND
                      original poly restored in PS.
  promoteRedo         redo re-applies (master back, instance back).
  masterMoveUndo      move a CFSS master to another layer (updateMaster path,
                      confirm stubbed true) -> undo -> master catId/semanticTag
                      back to original AND ObjectAgg.byRole totals identical to
                      pre-move.  <-- this is the RED check (fails pre-fix).
  oldSnapGrace        a pre-fix snapshot (no `masters` key) + a MASTERS mutation,
                      then undo: no throw, PS restored.
  plainUndo           plain PS-only undo still works (add poly -> undo -> gone).

Emits LITE_UNDO_MASTERS_OK on success.

    py -3 lite/tests/test_undo_masters.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=9300):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# cross-floor-shapes.js + layer-move.js load dynamically -- poll until ready.
JS_WAIT_FOR_MODULES = r"""
async () => {
  for (let i = 0; i < 60; i++) {
    if (typeof window.moveObjectToLayer === 'function' &&
        typeof window.addMaster === 'function' &&
        typeof window.__cfssTestPromote === 'function' &&
        window.CFSS && typeof window.CFSS.snapshotMasters === 'function') break;
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
    window.MASTERS = {};
  }
  function resetUndo() { undoStack.length = 0; redoStack.length = 0; }
  function rect(w, h, ox, oy) { ox = ox || 0; oy = oy || 0; return [{x:ox,y:oy},{x:ox+w,y:oy},{x:ox+w,y:oy+h},{x:ox,y:oy+h}]; }
  function mcount() { return Object.keys(window.MASTERS || {}).length; }

  // -----------------------------------------------------------------------
  // (1) promote poly -> undo restores poly + drops master; redo re-applies
  // -----------------------------------------------------------------------
  {
    reseed(); resetPS(); resetUndo();
    pageCount = 1; curPage = 1;
    PS[1] = {objects: [], scale: {pts_per_m: 1}, annotations: []};
    const poly = {id: 801, kind: 'poly', pts: rect(4, 3), catId: 'gfa', counting: false, semanticTag: 'gross_floor_area', dimVisible: true};
    PS[1].objects.push(poly);

    const mid = window.__cfssTestPromote(poly, 'M-Undo', []);
    const promotedOk = !!mid && mcount() === 1 && PS[1].objects[0].kind === 'instance';

    undo();
    const undoMastersGone = mcount() === 0;
    const undoPolyBack = PS[1].objects.length === 1 && PS[1].objects[0].kind === 'poly';
    out.promoteUndo = !!(promotedOk && undoMastersGone && undoPolyBack);
    out._promoteUndoDetail = {mid: mid, promotedOk: promotedOk, undoMastersGone: undoMastersGone, undoPolyBack: undoPolyBack, kindAfterUndo: PS[1].objects[0] && PS[1].objects[0].kind};

    let redoOk = false;
    if (typeof redo === 'function') {
      redo();
      redoOk = mcount() === 1 && PS[1].objects[0].kind === 'instance';
    }
    out.promoteRedo = !!redoOk;
    out._promoteRedoDetail = {redoOk: redoOk, mcountAfterRedo: mcount(), kindAfterRedo: PS[1].objects[0] && PS[1].objects[0].kind};
  }

  // -----------------------------------------------------------------------
  // (2) move a CFSS master to another layer -> undo restores master + totals
  //     (this is the RED check: pre-fix leaves master.catId on the target)
  // -----------------------------------------------------------------------
  {
    reseed(); resetPS(); resetUndo();
    pageCount = 2; curPage = 1;
    PS[1] = {objects: [], scale: {pts_per_m: 1}, annotations: []};
    PS[2] = {objects: [], scale: {pts_per_m: 1}, annotations: []};
    const custDed = addLayer('ded', 'Custom Ded U', '#ff6b6b');

    const mid = addMaster('Shared Core U', [{x_m:0,y_m:0},{x_m:4,y_m:0},{x_m:4,y_m:3},{x_m:0,y_m:3}], '#4c8dff',
      {catId: 'gfa', semanticTag: 'gross_floor_area'});
    PS[1].objects.push(makeInstance(mid, {x: 0, y: 0}));
    PS[2].objects.push(makeInstance(mid, {x: 0, y: 0}));

    const brBefore = window.ObjectAgg.byRole();
    const gfaBefore = (brBefore.gfa && brBefore.gfa.area) || 0;
    const dedBefore = (brBefore.ded && brBefore.ded.area) || 0;
    const catBefore = masterById(mid).catId;
    const tagBefore = masterById(mid).semanticTag;

    const origConfirm = window.confirm; window.confirm = () => true;
    moveObjectToLayer(PS[1].objects[0], custDed.id);
    window.confirm = origConfirm;

    const movedOk = masterById(mid).catId === custDed.id && masterById(mid).semanticTag === 'deduction_opening';

    undo();
    const catUndo = masterById(mid).catId;
    const tagUndo = masterById(mid).semanticTag;
    const brUndo = window.ObjectAgg.byRole();
    const gfaUndo = (brUndo.gfa && brUndo.gfa.area) || 0;
    const dedUndo = (brUndo.ded && brUndo.ded.area) || 0;

    out.masterMoveUndo = !!(movedOk &&
      catUndo === catBefore && tagUndo === tagBefore &&
      Math.abs(gfaUndo - gfaBefore) < 1e-6 && Math.abs(dedUndo - dedBefore) < 1e-6);
    out._masterMoveUndoDetail = {movedOk: movedOk, catBefore: catBefore, catUndo: catUndo, tagUndo: tagUndo, gfaBefore: gfaBefore, gfaUndo: gfaUndo, dedBefore: dedBefore, dedUndo: dedUndo};
  }

  // -----------------------------------------------------------------------
  // (3) pre-fix snapshot (no `masters` key) + MASTERS mutation -> undo:
  //     no throw, PS restored (MASTERS left untouched = graceful)
  // -----------------------------------------------------------------------
  {
    reseed(); resetPS(); resetUndo();
    pageCount = 1; curPage = 1;
    PS[1] = {objects: [], scale: {pts_per_m: 1}, annotations: []};
    PS[1].objects.push({id: 811, kind: 'poly', pts: rect(2, 2), catId: 'gfa', counting: false, semanticTag: 'gross_floor_area', dimVisible: true});

    // Fabricate an OLD-style snapshot: full doc snap with the `masters` key stripped.
    const snapObj = JSON.parse(_docSnap());
    delete snapObj.masters;
    undoStack.push(JSON.stringify(snapObj));

    // Now mutate: add a master AND add a second poly to PS (the poly should be
    // removed by undo; MASTERS behaviour for old snapshots is "leave untouched").
    addMaster('Ghost', [{x_m:0,y_m:0},{x_m:1,y_m:0},{x_m:1,y_m:1}], '#888');
    PS[1].objects.push({id: 812, kind: 'poly', pts: rect(3, 3, 20, 20), catId: 'gfa', counting: false, semanticTag: 'gross_floor_area', dimVisible: true});

    let threw = false;
    try { undo(); } catch (err) { threw = true; }
    out.oldSnapGrace = !!(!threw && PS[1].objects.length === 1);
    out._oldSnapGraceDetail = {threw: threw, psLen: PS[1].objects.length, mcount: mcount()};
  }

  // -----------------------------------------------------------------------
  // (4) plain PS-only undo still works (regression guard)
  // -----------------------------------------------------------------------
  {
    reseed(); resetPS(); resetUndo();
    pageCount = 1; curPage = 1;
    PS[1] = {objects: [], scale: {pts_per_m: 1}, annotations: []};
    pushUndo();
    PS[1].objects.push({id: 821, kind: 'poly', pts: rect(5, 5), catId: 'gfa', counting: false, semanticTag: 'gross_floor_area', dimVisible: true});
    undo();
    out.plainUndo = PS[1].objects.length === 0;
    out._plainUndoDetail = {psLen: PS[1].objects.length};
  }

  reseed(); resetPS(); resetUndo();
  return out;
}
"""

CHECKS = [
    "promoteUndo",
    "promoteRedo",
    "masterMoveUndo",
    "oldSnapGrace",
    "plainUndo",
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
    print("LITE-UNDO-MASTERS checks:")
    for k in CHECKS:
        ok = result.get(k)
        print(f"  {k:18s} -> {ok}")
        if ok is not True:
            failures.append(f"check '{k}' = {ok!r} (expected True)")

    for dk in ("_promoteUndoDetail", "_promoteRedoDetail", "_masterMoveUndoDetail", "_oldSnapGraceDetail", "_plainUndoDetail"):
        if dk in result:
            print(f"  {dk}: {result[dk]}")

    if page_errors:
        failures.append(f"{len(page_errors)} page error(s) during scenario")

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_UNDO_MASTERS_FAIL")
        sys.exit(1)
    else:
        print("LITE_UNDO_MASTERS_OK")


if __name__ == "__main__":
    main()
