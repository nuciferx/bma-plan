"""
LITE-TREE-UI regression guard (LST-3a sprint).

Verifies that the sublayer-tree panel renders correctly, supports folder
CRUD, nest/un-nest, collapse, visibility/lock inheritance, and custom
layer delete through the new tree buildPicker().

Each check: (a) real DOM action via Playwright clicks/evaluate,
            (b) state/model assertion via page.evaluate on LAYERS / FOLDERS
                / state / DOM.
            Positive-control: BEFORE value must differ from AFTER.

Required checks (spec LST-3a):
  defaultLayersFlat       fresh load: 6 layer rows, no folder rows (regression)
  addFolderRenders        click #lp-add-folder → folder row appears, FOLDERS.length===1
  nestLayerIndent         click → on layer after folder → parentId===folder.id, depth>0
  collapseHidesChildren   collapse folder → child row absent; expand → reappears
  folderHideInheritsToCanvas  folder eye off → effVisible(child,_isHidden)===false
  outdentToRoot           nested layer click ← → parentId===null at root depth
  folderDeleteReparents   delete folder → folder gone, child layer still present (reparented)
  customLayerDeleteStillWorks  delete custom layer → objects reassigned to default

Emits LITE_TREE_UI_OK on success.

    py -3 lite/tests/test_tree_ui.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8360):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ---------------------------------------------------------------------------
# Scenario 1 — defaultLayersFlat
# Fresh load: #catlist must have exactly 6 rows with data-nodekind="layer"
# and zero rows with data-nodekind="folder". FOLDERS.length===0.
# ---------------------------------------------------------------------------
DEFAULT_LAYERS_FLAT = r"""
() => {
  // Ensure clean default state
  LAYERS.length = 0;
  FOLDERS.length = 0;
  initLayers();
  ROLE_DEFS.forEach(function(rd) {
    state.catVis[rd.id] = true;
    state.catLock[rd.id] = false;
  });
  state.activeCat = 'gfa';
  buildPicker();

  const allRows = document.querySelectorAll('#catlist [data-catid]');
  const layerRows = document.querySelectorAll('#catlist [data-nodekind="layer"]');
  const folderRows = document.querySelectorAll('#catlist [data-nodekind="folder"]');

  return {
    totalRows: allRows.length,
    layerRowCount: layerRows.length,
    folderRowCount: folderRows.length,
    foldersArrayEmpty: FOLDERS.length === 0,
    sixLayerRows: layerRows.length === 6,
    noFolderRows: folderRows.length === 0
  };
}
"""

# ---------------------------------------------------------------------------
# Scenario 2 — addFolderRenders
# Click #lp-add-folder → FOLDERS.length===1, a folder row with
# data-nodekind="folder" appears in #catlist.
# ---------------------------------------------------------------------------
ADD_FOLDER_RENDERS = r"""
async () => {
  // Reset to clean defaults
  LAYERS.length = 0;
  FOLDERS.length = 0;
  initLayers();
  ROLE_DEFS.forEach(function(rd) {
    state.catVis[rd.id] = true;
    state.catLock[rd.id] = false;
  });
  buildPicker();

  const foldersBefore = FOLDERS.length;  // 0

  document.getElementById('lp-add-folder').click();
  await new Promise(r => setTimeout(r, 50));

  const foldersAfter = FOLDERS.length;
  const folderRow = document.querySelector('#catlist [data-nodekind="folder"]');

  return {
    foldersBefore,
    foldersAfter,
    grewByOne: foldersAfter === foldersBefore + 1,
    folderRowPresent: !!folderRow,
    folderRowHasIcon: folderRow ? folderRow.textContent.includes('📁') : false
  };
}
"""

# ---------------------------------------------------------------------------
# Scenario 3 — nestLayerIndent
# With a folder at order 0 (root), get the first layer (gfa, order 0).
# Because childrenOf(null) sorts folders-before-layers at equal order,
# we need the layer to have order=1 so it's the immediate sibling AFTER
# the folder. Then click → on that layer → parentId===folder.id.
# Also check the DOM row has marginLeft > 0 (depth > 0).
# ---------------------------------------------------------------------------
NEST_LAYER_INDENT = r"""
async () => {
  // Clean state
  LAYERS.length = 0;
  FOLDERS.length = 0;
  initLayers();
  ROLE_DEFS.forEach(function(rd) {
    state.catVis[rd.id] = true;
    state.catLock[rd.id] = false;
  });

  // Add a folder at order 0; gfa layer should already be at order 0.
  // Give folder order -1 so it renders first (before gfa).
  const f = addFolder('TestFolder', '#ff0000', null);
  f.order = -1;

  // gfa is at order 0, so it is immediately after f in childrenOf(null)
  const gfa = layerById('gfa');

  state.activeCat = 'gfa';
  buildPicker();

  // find the gfa row and press ArrowRight (indent keyboard fallback)
  const gfaRow = document.querySelector('[data-catid="gfa"]');
  if (!gfaRow) return {no_gfa_row: true};

  const parentIdBefore = gfa.parentId;  // should be null

  gfaRow.focus();
  gfaRow.dispatchEvent(new KeyboardEvent('keydown', {key: 'ArrowRight', shiftKey: false, bubbles: true}));
  await new Promise(r => setTimeout(r, 50));

  const parentIdAfter = gfa.parentId;

  // check row depth: marginLeft should be "16px" (depth=1)
  const gfaRowAfter = document.querySelector('[data-catid="gfa"]');
  const marginLeft = gfaRowAfter ? gfaRowAfter.style.marginLeft : '0px';
  const depth = parseInt(marginLeft) || 0;

  return {
    parentIdBefore,
    parentIdAfter,
    folderId: f.id,
    nestedCorrectly: parentIdAfter === f.id,
    depthPositive: depth > 0,
    parentIdChangedFromNull: parentIdBefore === null && parentIdAfter !== null
  };
}
"""

# ---------------------------------------------------------------------------
# Scenario 4 — collapseHidesChildren
# Create folder, nest a layer under it. Verify the layer row is in DOM.
# Click the ▾ toggle → layer row should NOT be in DOM.
# Click again ▸ → layer row reappears.
# ---------------------------------------------------------------------------
COLLAPSE_HIDES_CHILDREN = r"""
async () => {
  LAYERS.length = 0;
  FOLDERS.length = 0;
  initLayers();
  if (!state.folderCollapsed) state.folderCollapsed = {};
  ROLE_DEFS.forEach(function(rd) {
    state.catVis[rd.id] = true;
    state.catLock[rd.id] = false;
  });

  const f = addFolder('CollapseFolder', '#00ff00', null);
  f.order = -1;
  state.catVis[f.id] = true;
  state.catLock[f.id] = false;

  const gfa = layerById('gfa');
  gfa.parentId = f.id;

  state.folderCollapsed[f.id] = false;  // start expanded
  buildPicker();

  // gfa row visible initially
  const gfaRowBefore = document.querySelector('[data-catid="gfa"]');
  const visibleBefore = !!gfaRowBefore;

  // click collapse toggle on the folder row
  const folderRow = document.querySelector('[data-catid="' + f.id + '"]');
  if (!folderRow) return {no_folder_row: true};
  const toggle = folderRow.querySelector('.lt-collapse-toggle');
  if (!toggle) return {no_toggle: true};

  toggle.click();
  await new Promise(r => setTimeout(r, 50));

  const gfaRowAfterCollapse = document.querySelector('[data-catid="gfa"]');
  const hiddenAfterCollapse = !gfaRowAfterCollapse;

  // click again to expand
  const folderRow2 = document.querySelector('[data-catid="' + f.id + '"]');
  const toggle2 = folderRow2 ? folderRow2.querySelector('.lt-collapse-toggle') : null;
  if (toggle2) { toggle2.click(); await new Promise(r => setTimeout(r, 50)); }

  const gfaRowAfterExpand = document.querySelector('[data-catid="gfa"]');
  const visibleAfterExpand = !!gfaRowAfterExpand;

  // cleanup: restore
  gfa.parentId = null;

  return {
    visibleBefore,
    hiddenAfterCollapse,
    visibleAfterExpand,
    collapseWorks: visibleBefore && hiddenAfterCollapse && visibleAfterExpand
  };
}
"""

# ---------------------------------------------------------------------------
# Scenario 5 — folderHideInheritsToCanvas
# Nest gfa under a folder. Toggle folder eye off →
# effVisible(gfa, _isHidden) === false.
# Toggle back on → effVisible === true.
# ---------------------------------------------------------------------------
FOLDER_HIDE_INHERITS = r"""
async () => {
  LAYERS.length = 0;
  FOLDERS.length = 0;
  initLayers();
  ROLE_DEFS.forEach(function(rd) {
    state.catVis[rd.id] = true;
    state.catLock[rd.id] = false;
  });

  const f = addFolder('HideFolder', '#0000ff', null);
  f.order = -1;
  state.catVis[f.id] = true;
  state.catLock[f.id] = false;

  const gfa = layerById('gfa');
  gfa.parentId = f.id;

  buildPicker();

  // Before: visible
  const visibleBefore = effVisible('gfa', _isHidden);

  // Click folder eye off
  const folderRow = document.querySelector('[data-catid="' + f.id + '"]');
  if (!folderRow) return {no_folder_row: true};
  const eyeBtn = folderRow.querySelector('[data-eye="' + f.id + '"]');
  if (!eyeBtn) return {no_eye_btn: true};

  eyeBtn.click();
  await new Promise(r => setTimeout(r, 50));

  const hiddenAfter = !effVisible('gfa', _isHidden);

  // Click folder eye on again
  const folderRow2 = document.querySelector('[data-catid="' + f.id + '"]');
  const eyeBtn2 = folderRow2 ? folderRow2.querySelector('[data-eye="' + f.id + '"]') : null;
  if (eyeBtn2) { eyeBtn2.click(); await new Promise(r => setTimeout(r, 50)); }

  const visibleAgain = effVisible('gfa', _isHidden);

  // cleanup
  gfa.parentId = null;

  return {
    visibleBefore,
    hiddenAfter,
    visibleAgain,
    inheritanceWorks: visibleBefore && hiddenAfter && visibleAgain
  };
}
"""

# ---------------------------------------------------------------------------
# Scenario 6 — outdentToRoot
# Nest gfa under a folder. Click ← outdent → parentId===null, row at depth 0.
# ---------------------------------------------------------------------------
OUTDENT_TO_ROOT = r"""
async () => {
  LAYERS.length = 0;
  FOLDERS.length = 0;
  initLayers();
  ROLE_DEFS.forEach(function(rd) {
    state.catVis[rd.id] = true;
    state.catLock[rd.id] = false;
  });

  const f = addFolder('OutdentFolder', '#ff00ff', null);
  f.order = -1;
  state.catVis[f.id] = true;
  state.catLock[f.id] = false;

  const gfa = layerById('gfa');
  gfa.parentId = f.id;

  buildPicker();

  const parentIdBefore = gfa.parentId;  // f.id

  // press ArrowLeft on gfa row (outdent keyboard fallback)
  const gfaRow = document.querySelector('[data-catid="gfa"]');
  if (!gfaRow) return {no_gfa_row: true};

  gfaRow.focus();
  gfaRow.dispatchEvent(new KeyboardEvent('keydown', {key: 'ArrowLeft', shiftKey: false, bubbles: true}));
  await new Promise(r => setTimeout(r, 50));

  const parentIdAfter = gfa.parentId;
  const gfaRowAfter = document.querySelector('[data-catid="gfa"]');
  const marginLeft = gfaRowAfter ? gfaRowAfter.style.marginLeft : '0px';
  const depth = parseInt(marginLeft) || 0;

  return {
    parentIdBefore,
    parentIdAfter,
    movedToRoot: parentIdAfter === null,
    depthZero: depth === 0,
    outdentWorks: parentIdBefore !== null && parentIdAfter === null && depth === 0
  };
}
"""

# ---------------------------------------------------------------------------
# Scenario 7 — folderDeleteReparents
# Create folder, nest gfa under it, delete folder → folder gone,
# gfa.parentId moved up (to null since folder was at root),
# gfa still present in LAYERS and in DOM.
# ---------------------------------------------------------------------------
FOLDER_DELETE_REPARENTS = r"""
async () => {
  LAYERS.length = 0;
  FOLDERS.length = 0;
  initLayers();
  ROLE_DEFS.forEach(function(rd) {
    state.catVis[rd.id] = true;
    state.catLock[rd.id] = false;
  });

  const f = addFolder('DelFolder', '#aaaaaa', null);
  f.order = -1;
  state.catVis[f.id] = true;
  state.catLock[f.id] = false;

  const gfa = layerById('gfa');
  gfa.parentId = f.id;

  buildPicker();

  const folderId = f.id;
  const foldersBefore = FOLDERS.length;
  const layersBefore = LAYERS.length;

  // find and click ✕ on the folder row
  const folderRow = document.querySelector('[data-catid="' + folderId + '"]');
  if (!folderRow) return {no_folder_row: true};
  const delBtn = folderRow.querySelector('[data-folder-del="' + folderId + '"]');
  if (!delBtn) return {no_del_btn: true};

  // auto-accept confirm
  window._origConfirm = window.confirm;
  window.confirm = () => true;
  delBtn.click();
  await new Promise(r => setTimeout(r, 80));
  window.confirm = window._origConfirm;

  const foldersAfter = FOLDERS.length;
  const layersAfter = LAYERS.length;
  const folderGone = !folderById(folderId);
  const gfaStillPresent = !!layerById('gfa');
  const gfaRow = document.querySelector('[data-catid="gfa"]');
  const gfaInDom = !!gfaRow;

  // gfa should be reparented to folder's parent = null
  const gfaParentAfter = layerById('gfa') ? layerById('gfa').parentId : 'MISSING';

  return {
    foldersBefore, foldersAfter,
    layersBefore, layersAfter,
    folderGone,
    gfaStillPresent,
    gfaInDom,
    gfaParentAfter,
    reparentedToRoot: gfaParentAfter === null,
    reparentsCorrectly: folderGone && gfaStillPresent && gfaInDom && gfaParentAfter === null
  };
}
"""

# ---------------------------------------------------------------------------
# Scenario 8 — customLayerDeleteStillWorks
# Add a custom layer (role gfa), inject an object on page 1 with that catId,
# delete via ✕ → object reassigned to 'gfa', LAYERS shrinks by 1.
# Regression: L2c-3 behavior through the new tree render.
# ---------------------------------------------------------------------------
CUSTOM_LAYER_DELETE = r"""
async () => {
  LAYERS.length = 0;
  FOLDERS.length = 0;
  initLayers();
  ROLE_DEFS.forEach(function(rd) {
    state.catVis[rd.id] = true;
    state.catLock[rd.id] = false;
  });
  state.activeCat = 'gfa';

  const nl = addLayer('gfa', 'CustomDeleteTest', '#ff0000');
  state.catVis[nl.id] = true;
  state.catLock[nl.id] = false;
  state.activeCat = nl.id;

  const customId = nl.id;
  const lenBefore = LAYERS.length;

  // inject object on page 1
  PS['1'] = PS['1'] || {objects:[], scale:null, annotations:[]};
  const obj = {id:9901, catId:customId, kind:'poly', pts:[{x:0,y:0}], dimVisible:true, counting:false, semanticTag:'gross_floor_area'};
  PS['1'].objects.push(obj);

  buildPicker();

  // positive control: object has customId
  const beforeObj = PS['1'].objects.find(o => o.id === 9901);
  const beforeHasCustomId = !!(beforeObj && beforeObj.catId === customId);

  // click ✕ on the custom layer row
  const row = document.querySelector('[data-catid="' + customId + '"]');
  const delBtn = row ? row.querySelector('[data-layer-del="' + customId + '"]') : null;
  if (!delBtn) return {no_del_btn: true, customId, rowPresent: !!row};

  window._origConfirm = window.confirm;
  window.confirm = () => true;
  delBtn.click();
  await new Promise(r => setTimeout(r, 80));
  window.confirm = window._origConfirm;

  const lenAfter = LAYERS.length;
  const afterObj = PS['1'].objects.find(o => o.id === 9901);
  const reassignedToDefault = !!(afterObj && afterObj.catId === 'gfa');
  const shrankByOne = lenAfter === lenBefore - 1;
  const activeCatNotCustom = state.activeCat !== customId;

  return {
    beforeHasCustomId,
    reassignedToDefault,
    shrankByOne,
    activeCatNotCustom,
    lenBefore, lenAfter,
    activeCatAfter: state.activeCat,
    deleteWorksViaTree: beforeHasCustomId && reassignedToDefault && shrankByOne && activeCatNotCustom
  };
}
"""

# ---------------------------------------------------------------------------
# Scenario 9 — customLayerDeleteReparentsChildren  (reviewer-added, LST-3a orphan fix)
# Custom parent layer P (role gfa) with a sub-layer C nested under it.
# Delete P → C must move up to P's parent (null here), C still present & rendered
# at root. Without the reparent-up fix, C orphans (parentId points at the deleted
# P) and vanishes from the tree until reload.
# ---------------------------------------------------------------------------
CUSTOM_LAYER_DELETE_REPARENTS = r"""
async () => {
  LAYERS.length = 0;
  FOLDERS.length = 0;
  initLayers();
  ROLE_DEFS.forEach(function(rd) { state.catVis[rd.id] = true; state.catLock[rd.id] = false; });
  state.activeCat = 'gfa';

  const P = addLayer('gfa', 'ParentCustom', '#ff0000');
  state.catVis[P.id] = true; state.catLock[P.id] = false;
  const C = addLayer('use', 'ChildCustom', '#00ff00');
  state.catVis[C.id] = true; state.catLock[C.id] = false;
  C.parentId = P.id;                 // nest C under P
  const pParent = (P.parentId !== undefined) ? P.parentId : null;  // null (root)

  state.activeCat = P.id;
  buildPicker();

  const childParentBefore = C.parentId;            // === P.id
  const row = document.querySelector('[data-catid="' + P.id + '"]');
  const delBtn = row ? row.querySelector('[data-layer-del="' + P.id + '"]') : null;
  if (!delBtn) return {no_del_btn: true};

  window._origConfirm = window.confirm; window.confirm = () => true;
  delBtn.click();
  await new Promise(r => setTimeout(r, 80));
  window.confirm = window._origConfirm;

  const pGone = !layerById(P.id);
  const cStillPresent = !!layerById(C.id);
  const childParentAfter = layerById(C.id) ? layerById(C.id).parentId : 'MISSING';
  const cRendered = !!document.querySelector('[data-catid="' + C.id + '"]');

  return {
    childParentBefore, childParentAfter,
    pGone, cStillPresent, cRendered,
    reparentedUp: childParentBefore === P.id && pGone && cStillPresent
                  && childParentAfter === pParent && cRendered
  };
}
"""

CHECKS = [
    ("defaultLayersFlat",           DEFAULT_LAYERS_FLAT,    ["sixLayerRows", "noFolderRows", "foldersArrayEmpty"]),
    ("customLayerDeleteReparentsChildren", CUSTOM_LAYER_DELETE_REPARENTS, ["reparentedUp"]),
    ("addFolderRenders",            ADD_FOLDER_RENDERS,     ["grewByOne", "folderRowPresent"]),
    ("nestLayerIndent",             NEST_LAYER_INDENT,      ["nestedCorrectly", "depthPositive", "parentIdChangedFromNull"]),
    ("collapseHidesChildren",       COLLAPSE_HIDES_CHILDREN,["collapseWorks"]),
    ("folderHideInheritsToCanvas",  FOLDER_HIDE_INHERITS,   ["inheritanceWorks"]),
    ("outdentToRoot",               OUTDENT_TO_ROOT,        ["outdentWorks"]),
    ("folderDeleteReparents",       FOLDER_DELETE_REPARENTS,["reparentsCorrectly"]),
    ("customLayerDeleteStillWorks", CUSTOM_LAYER_DELETE,    ["deleteWorksViaTree"]),
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
        print("LITE-TREE-UI checks:")
        for name, scenario, required_keys in CHECKS:
            try:
                result = pg.evaluate(scenario)
            except Exception as ex:
                print(f"  {name:40s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
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
        print("LITE_TREE_UI_FAIL")
        sys.exit(1)
    else:
        print("LITE_TREE_UI_OK")


if __name__ == "__main__":
    main()
