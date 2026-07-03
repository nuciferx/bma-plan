"""
INV-20260703-layer-redesign follow-up -- undo/redo covers LAYERS + FOLDERS.

The ui-lite undo system (_docSnap/_applyDoc/pushUndo/undo/redo in ui-lite.html)
deep-copies the page store PS (+ pageTags/floor meta + CFSS masters) but had
NEVER covered window.LAYERS / window.FOLDERS. Result: layer add / rename /
recolor / reorder / reparent / floorKey mutations could NOT round-trip under
Ctrl+Z. The user-visible loss: the reconcile-banner [ตามหน้า] button
(layer-target-ui.js _onByPage) pushUndo()'d then cleared a layer's floorKey, but
Ctrl+Z restored nothing (snapshot carried no layers) -> floorKey stayed cleared.

Fix: layer-system.js exposes snapshotLayers()/snapshotFolders() +
restoreLayers()/restoreFolders() (restore mutates the arrays IN PLACE via
splice+push -- ui-lite's `var CATS = LAYERS` captured the array by reference).
_docSnap() carries them under additive `layers`/`folders` keys; _applyDoc()
restores them. Old snapshots (no key) leave LAYERS/FOLDERS untouched (graceful).
pushUndo() added before mutation at every layer/folder UI entry point.

Checks:
  addCustomLayerUndo   _lpDoAddLayer('gfa') -> undo -> layer gone from LAYERS
                       AND from the panel (data-catid absent); redo -> back.
  byPageBannerShown    divergence set up -> reconcile shows banner for the layer.
  byPageCleared        real [ตามหน้า] button click clears layer.floorKey.
  byPageUndoRestored   undo restores floorKey AND byFloorRole() buckets.  <-- RED
                       (pre-fix: snapshot carried no layers, floorKey stayed
                       cleared after undo).
  renameRecolorUndo    rename+recolor a layer in one snapshot -> undo restores
                       BOTH name and color (proves in-place splice keeps id).
  oldSnapGrace         a pre-fix snapshot (no layers/folders keys) + a LAYERS
                       mutation, then undo: no throw, PS restored, LAYERS
                       untouched (custom layer still present).
  plainUndo            plain PS-only undo still works (add poly -> undo -> gone).
  loadSeedingNoUndo    loadProto() rebuilds LAYERS/FOLDERS but pushes no undo
                       entry (undoStack length unchanged).

Emits LITE_UNDO_LAYERS_OK on success.

    py -3 lite/tests/test_undo_layers.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=9400):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# layer modules + layer-target-ui + object-agg load as plain <script>s; poll ready.
JS_WAIT_FOR_MODULES = r"""
async () => {
  for (let i = 0; i < 80; i++) {
    if (typeof window.addLayer === 'function' &&
        typeof window.layerById === 'function' &&
        typeof window._lpDoAddLayer === 'function' &&
        typeof window.seedPageFolders === 'function' &&
        typeof window.snapshotLayers === 'function' &&
        typeof window.restoreLayers === 'function' &&
        typeof window.loadProto === 'function' &&
        window.ObjectAgg && typeof window.ObjectAgg.byFloorRole === 'function' &&
        window.LayerTargetUI && typeof window.LayerTargetUI.reconcile === 'function') break;
    await new Promise(r => setTimeout(r, 50));
  }
  await new Promise(r => setTimeout(r, 80));
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
    for (var k in pageNames) delete pageNames[k];
    window.MASTERS = {};
  }
  function resetUndo() { undoStack.length = 0; redoStack.length = 0; }
  function rect(w, h, ox, oy) { ox = ox || 0; oy = oy || 0; return [{x:ox,y:oy},{x:ox+w,y:oy},{x:ox+w,y:oy+h},{x:ox,y:oy+h}]; }
  function panelHas(id) { return !!document.querySelector('[data-catid="' + id + '"]'); }

  // -----------------------------------------------------------------------
  // (1) add custom layer (production entry _lpDoAddLayer) -> undo removes it
  //     from LAYERS + panel; redo restores.
  // -----------------------------------------------------------------------
  {
    reseed(); resetPS();
    pageCount = 1; curPage = 1;
    PS[1] = {objects: [], scale: {pts_per_m: 1}, annotations: []};
    // Folder-only mode (LFOC-1b) hides orphan root layers, so seed the page-1
    // PF folder and anchor state.activeCat inside it -> the new layer inherits
    // parentId = PF folder and is rendered in the panel (data-catid present).
    pageTags[1] = 'floor'; pageFloorNum[1] = 1; pageFloorKind[1] = 'normal';
    seedPageFolders([1], pageTags, pageFloorNum, pageFloorKind);
    const anchor = LAYERS.filter(function(l) { return l.parentId === 'PF_floor_1' && l.role === 'gfa'; })[0];
    state.activeCat = anchor ? anchor.id : 'gfa';
    resetUndo();  // seeding must not have pushed undo; start clean

    const before = LAYERS.length;
    _lpDoAddLayer('gfa');
    const newId = LAYERS[LAYERS.length - 1].id;
    const seededNoUndo = anchor && LAYERS.filter(function(l){return l.parentId==='PF_floor_1';}).length >= 3;
    const added = LAYERS.length === before + 1 && panelHas(newId);

    undo();
    const goneUndo = LAYERS.length === before && !layerById(newId) && !panelHas(newId);

    let redoOk = false;
    if (typeof redo === 'function') {
      redo();
      redoOk = LAYERS.length === before + 1 && !!layerById(newId) && panelHas(newId);
    }
    out.addCustomLayerUndo = !!(added && goneUndo);
    out.addCustomLayerRedo = !!redoOk;
    out._addDetail = {before: before, newId: newId, added: added, goneUndo: goneUndo, redoOk: redoOk, anchorId: anchor && anchor.id, seededNoUndo: seededNoUndo};
  }

  // -----------------------------------------------------------------------
  // (2) [ตามหน้า] path: layer pinned floor:2 with an object on a floor:1 page
  //     -> banner shows -> click real button clears floorKey -> undo restores
  //     floorKey AND byFloorRole buckets. (RED check pre-fix.)
  // -----------------------------------------------------------------------
  {
    reseed(); resetPS(); resetUndo();
    pageCount = 2; curPage = 1;
    PS[1] = {objects: [], scale: {pts_per_m: 1}, annotations: []};
    PS[2] = {objects: [], scale: {pts_per_m: 1}, annotations: []};
    pageTags[1] = 'floor'; pageFloorNum[1] = 1; pageFloorKind[1] = 'normal';
    pageTags[2] = 'floor'; pageFloorNum[2] = 2; pageFloorKind[2] = 'normal';

    const cust = addLayer('gfa', 'Pinned GFA U', '#4c8dff');  // raw setup (no undo)
    cust.floorKey = 'floor:2';
    PS[1].objects.push({id: 901, kind: 'poly', pts: rect(4, 3), catId: cust.id, counting: false, semanticTag: 'gross_floor_area', dimVisible: true});

    const fkBefore = cust.floorKey;
    const brBefore = JSON.stringify(window.ObjectAgg.byFloorRole());

    window.LayerTargetUI.reconcile();
    const banner = document.getElementById('ltu-banner');
    const bannerShown = !!(banner && banner.classList.contains('show') && banner._ltuRow && banner._ltuRow.layerId === cust.id);

    const btn = document.getElementById('ltu-by-page');
    if (btn) btn.click();  // _onByPage: pushUndo() then delete layer.floorKey

    const fkCleared = !layerById(cust.id).floorKey;

    undo();
    const l2 = layerById(cust.id);
    const fkRestored = l2 && l2.floorKey === fkBefore;
    const brRestored = JSON.stringify(window.ObjectAgg.byFloorRole()) === brBefore;

    out.byPageBannerShown = bannerShown;
    out.byPageCleared = !!fkCleared;
    out.byPageUndoRestored = !!(fkRestored && brRestored);
    out._byPageDetail = {fkBefore: fkBefore, fkCleared: fkCleared, fkRestored: fkRestored, brRestored: brRestored, bannerShown: bannerShown};
  }

  // -----------------------------------------------------------------------
  // (3) rename + recolor in one snapshot -> undo restores both.
  //     (proves restore splices contents in place: layerById('gfa') still
  //     resolves to the restored object.)
  // -----------------------------------------------------------------------
  {
    reseed(); resetPS(); resetUndo();
    pageCount = 1; curPage = 1;
    PS[1] = {objects: [], scale: {pts_per_m: 1}, annotations: []};
    const L = layerById('gfa');
    const origName = L.name, origColor = L.color;
    pushUndo();
    renameLayer('gfa', 'Renamed X');
    recolorLayer('gfa', '#abcdef');
    const mutated = L.name === 'Renamed X' && L.color === '#abcdef';
    undo();
    const L2 = layerById('gfa');
    out.renameRecolorUndo = !!(mutated && L2 && L2.name === origName && L2.color === origColor);
    out._renameDetail = {mutated: mutated, origName: origName, undoName: L2 && L2.name, origColor: origColor, undoColor: L2 && L2.color};
  }

  // -----------------------------------------------------------------------
  // (4) old-snapshot (no layers/folders keys) grace -> undo: no throw, PS
  //     restored, LAYERS untouched (custom layer still present).
  // -----------------------------------------------------------------------
  {
    reseed(); resetPS(); resetUndo();
    pageCount = 1; curPage = 1;
    PS[1] = {objects: [], scale: {pts_per_m: 1}, annotations: []};
    PS[1].objects.push({id: 811, kind: 'poly', pts: rect(2, 2), catId: 'gfa', counting: false, semanticTag: 'gross_floor_area', dimVisible: true});

    const snapObj = JSON.parse(_docSnap());
    delete snapObj.layers; delete snapObj.folders;
    undoStack.push(JSON.stringify(snapObj));

    const cust = addLayer('gfa', 'Ghost L', '#888');
    const custId = cust.id;
    PS[1].objects.push({id: 812, kind: 'poly', pts: rect(3, 3, 20, 20), catId: 'gfa', counting: false, semanticTag: 'gross_floor_area', dimVisible: true});

    let threw = false;
    try { undo(); } catch (err) { threw = true; }
    out.oldSnapGrace = !!(!threw && PS[1].objects.length === 1 && !!layerById(custId));
    out._oldSnapDetail = {threw: threw, psLen: PS[1].objects.length, custStillThere: !!layerById(custId)};
  }

  // -----------------------------------------------------------------------
  // (5) plain PS-only undo still works (regression guard).
  // -----------------------------------------------------------------------
  {
    reseed(); resetPS(); resetUndo();
    pageCount = 1; curPage = 1;
    PS[1] = {objects: [], scale: {pts_per_m: 1}, annotations: []};
    pushUndo();
    PS[1].objects.push({id: 821, kind: 'poly', pts: rect(5, 5), catId: 'gfa', counting: false, semanticTag: 'gross_floor_area', dimVisible: true});
    undo();
    out.plainUndo = PS[1].objects.length === 0;
    out._plainDetail = {psLen: PS[1].objects.length};
  }

  // -----------------------------------------------------------------------
  // (6) load-time seeding does NOT create undo entries.
  // -----------------------------------------------------------------------
  {
    reseed(); resetPS(); resetUndo();
    pageCount = 0;
    const beforeLen = undoStack.length;
    loadProto({version: 1,
      liteLayers: [{id: 'gfa', name: 'A', color: '#111', role: 'gfa', order: 0, parentId: null}],
      liteGroups: [{id: 'F1', name: 'G', color: '#222', parentId: null, order: 0}],
      pageStore: {}});
    out.loadSeedingNoUndo = undoStack.length === beforeLen;
    out._loadDetail = {beforeLen: beforeLen, afterLen: undoStack.length};
  }

  reseed(); resetPS(); resetUndo();
  return out;
}
"""

CHECKS = [
    "addCustomLayerUndo",
    "addCustomLayerRedo",
    "byPageBannerShown",
    "byPageCleared",
    "byPageUndoRestored",
    "renameRecolorUndo",
    "oldSnapGrace",
    "plainUndo",
    "loadSeedingNoUndo",
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
    print("LITE-UNDO-LAYERS checks:")
    for k in CHECKS:
        ok = result.get(k)
        print(f"  {k:20s} -> {ok}")
        if ok is not True:
            failures.append(f"check '{k}' = {ok!r} (expected True)")

    for dk in ("_addDetail", "_byPageDetail", "_renameDetail", "_oldSnapDetail", "_plainDetail", "_loadDetail"):
        if dk in result:
            print(f"  {dk}: {result[dk]}")

    if page_errors:
        failures.append(f"{len(page_errors)} page error(s) during scenario")

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_UNDO_LAYERS_FAIL")
        sys.exit(1)
    else:
        print("LITE_UNDO_LAYERS_OK")


if __name__ == "__main__":
    main()
