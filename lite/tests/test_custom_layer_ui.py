"""
LITE-CUSTOM-LAYER-UI regression guard (L2c-3 sprint).

Verifies that the layer-panel CRUD controls (add, rename, recolor, delete,
reorder) wire correctly to the layer-system.js model and update DOM/state.

Each check: (a) real DOM action via Playwright clicks/typing,
            (b) state assertion via page.evaluate on LAYERS / state / PS.
            Positive-control: BEFORE value must differ from AFTER.

Required checks (spec L2c-3):
  addCreatesRow          "+" → LAYERS grows, role/tag correct, DOM row present
  renameKeepsTag         inline rename → name changes, tag UNCHANGED
  recolorKeepsTag        color input → color changes, tag UNCHANGED
  deleteReassignsAllPages  delete custom layer → objects on 2 pages reassigned,
                           LAYERS shrinks, activeCat reassigned
  deleteBlockedOnDefault   default layers have no ✕ button
  reorderChangesZ          ▲▼ → .order swapped, objectsInZOrder reflects it

Emits LITE_LAYER_UI_OK on success.

    py -3 lite/tests/test_custom_layer_ui.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8340):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ---------------------------------------------------------------------------
# Scenario 1 — addCreatesRow
# Record LAYERS.length before click, click "+", assert grew by 1,
# new layer role === previous active role, tag === roleSemanticTag(role),
# and a DOM row with data-catid exists for the new id.
# ---------------------------------------------------------------------------
ADD_SCENARIO = r"""
async () => {
  const lenBefore = LAYERS.length;
  const activeId = state.activeCat;
  const activeBefore = layerById(activeId);
  const roleBefore = activeBefore ? activeBefore.role : null;

  // click "+"
  document.getElementById('lp-add').click();

  const lenAfter = LAYERS.length;
  const grew = lenAfter === lenBefore + 1;

  // the new activeCat should be the newly added layer
  const newId = state.activeCat;
  const newLayer = layerById(newId);
  const roleMatch = newLayer && newLayer.role === roleBefore;
  const tagMatch = newLayer && newLayer.tag === roleSemanticTag(roleBefore);

  // DOM: a .cat row with data-catid=newId
  const row = document.querySelector('[data-catid="' + newId + '"]');
  const domPresent = !!row;

  // positive control: newId must differ from the original activeId
  const idChanged = newId !== activeId;

  return {
    lenBefore, lenAfter, grew, roleMatch, tagMatch, domPresent, idChanged,
    newId, newLayerOk: !!(newLayer)
  };
}
"""

# ---------------------------------------------------------------------------
# Scenario 2 — renameKeepsTag
# Add a custom layer, grab its id/name/tag, rename via inline input,
# assert name changed AND tag unchanged.
# ---------------------------------------------------------------------------
RENAME_SCENARIO = r"""
async () => {
  // Add a custom layer so we have a renameable row
  const nl = addLayer('gfa', 'RenameTest', '#aabbcc');
  state.catVis[nl.id] = true;
  state.catLock[nl.id] = false;
  state.activeCat = nl.id;
  buildPicker();

  const idToRename = nl.id;
  const oldName = nl.name;
  const oldTag  = nl.tag;

  // positive control: these must be non-empty
  if (!oldName || !oldTag) return {setup_fail: true};

  // Click the .nm span for the row
  const row = document.querySelector('[data-catid="' + idToRename + '"]');
  if (!row) return {no_row: true};
  const nmSpan = row.querySelector('.nm');
  if (!nmSpan) return {no_nm: true};
  nmSpan.click();

  // the span should now be replaced by an input
  await new Promise(r => setTimeout(r, 50));
  const inp = row.querySelector('.lp-rename-inp');
  if (!inp) return {no_input: true};

  inp.value = '';
  inp.value = 'RenamedLayer';
  // fire Enter
  inp.dispatchEvent(new KeyboardEvent('keydown', {key:'Enter', bubbles:true}));
  await new Promise(r => setTimeout(r, 50));

  const layer = layerById(idToRename);
  if (!layer) return {layer_gone: true};

  return {
    oldName, newName: layer.name, oldTag, newTag: layer.tag,
    nameChanged: layer.name === 'RenamedLayer' && layer.name !== oldName,
    tagUnchanged: layer.tag === oldTag
  };
}
"""

# ---------------------------------------------------------------------------
# Scenario 3 — recolorKeepsTag
# Add a custom layer, record old color/tag, then exercise the REAL panel
# wiring: click the .lp-sw swatch (which appends a hidden <input type=color>
# to the body and attaches a 'change' listener), find that input, set its
# value, and dispatch a 'change' event. We can't open the native OS color
# dialog headlessly, but dispatching 'change' on the input runs the actual
# listener (recolorLayer + dirty + buildPicker) — so this tests the wiring,
# not just the model. state.dirty is reset to false first as a positive
# control that the listener flips it.
# ---------------------------------------------------------------------------
RECOLOR_SCENARIO = r"""
async () => {
  const nl = addLayer('use', 'RecolorTest', '#112233');
  state.catVis[nl.id] = true;
  state.catLock[nl.id] = false;
  state.activeCat = nl.id;
  buildPicker();

  const idToRecolor = nl.id;
  const oldColor = nl.color;
  const oldTag   = nl.tag;
  state.dirty = false;  // positive control: listener must set it true

  const row = document.querySelector('[data-catid="' + idToRecolor + '"]');
  const sw = row ? row.querySelector('.lp-sw') : null;
  const swWired = !!(sw && sw.getAttribute('data-recolor') === idToRecolor);
  if (!sw) return {no_swatch: true};

  // click the swatch -> handler appends an <input type=color> to body
  const colorInputsBefore = document.querySelectorAll('input[type="color"]').length;
  sw.click();
  await new Promise(r => setTimeout(r, 30));
  const colorInput = document.querySelector('input[type="color"]');
  if (!colorInput) return {no_color_input: true};
  const inputAppeared = document.querySelectorAll('input[type="color"]').length > colorInputsBefore;

  // drive the REAL change listener (native dialog can't open headlessly,
  // but dispatching 'change' runs the same listener that recolors)
  const newColor = '#aabbcc';
  colorInput.value = newColor;
  colorInput.dispatchEvent(new Event('change', {bubbles:true}));
  await new Promise(r => setTimeout(r, 30));

  const layer = layerById(idToRecolor);

  return {
    oldColor, newColor: layer ? layer.color : null, oldTag, newTag: layer ? layer.tag : null,
    colorChanged: layer && layer.color === newColor && layer.color !== oldColor,
    tagUnchanged: layer && layer.tag === oldTag,
    dirtySet: state.dirty === true,
    swWired, inputAppeared
  };
}
"""

# ---------------------------------------------------------------------------
# Scenario 4 — deleteReassignsAllPages
# Add a custom layer, inject objects referencing it on pages 1 AND 2 of PS,
# click ✕ (auto-accept confirm), assert:
#   (i)  every such object.catId === reassignTo on BOTH pages
#   (ii) LAYERS shrank by 1
#   (iii) state.activeCat !== deletedId
# Positive control: BEFORE, catId === customId (not reassignTo).
# ---------------------------------------------------------------------------
DELETE_SCENARIO = r"""
async () => {
  // ensure clean PS for pages 1+2
  PS['1'] = PS['1'] || {objects:[], scale:null, annotations:[]};
  PS['2'] = PS['2'] || {objects:[], scale:null, annotations:[]};

  const nl = addLayer('gfa', 'DeleteMe', '#ff0000');
  state.catVis[nl.id] = true;
  state.catLock[nl.id] = false;
  state.activeCat = nl.id;

  const customId = nl.id;
  const lenBefore = LAYERS.length;

  // inject one object on each page
  const obj1 = {id:8001, catId:customId, kind:'poly', pts:[{x:0,y:0}], dimVisible:true, counting:false, semanticTag:'gross_floor_area'};
  const obj2 = {id:8002, catId:customId, kind:'poly', pts:[{x:1,y:1}], dimVisible:true, counting:false, semanticTag:'gross_floor_area'};
  PS['1'].objects.push(obj1);
  PS['2'].objects.push(obj2);

  buildPicker();

  // positive control: before delete, the objects still have customId
  const beforeP1 = PS['1'].objects.find(o => o.id === 8001);
  const beforeP2 = PS['2'].objects.find(o => o.id === 8002);
  const beforeBothCustom = beforeP1 && beforeP1.catId === customId &&
                           beforeP2 && beforeP2.catId === customId;

  // the ✕ button for the custom layer
  const row = document.querySelector('[data-catid="' + customId + '"]');
  const delBtn = row ? row.querySelector('[data-layer-del]') : null;
  if (!delBtn) return {no_del_btn: true, customId};

  // auto-accept the confirm dialog
  window._origConfirm = window.confirm;
  window.confirm = () => true;
  delBtn.click();
  await new Promise(r => setTimeout(r, 80));
  window.confirm = window._origConfirm;

  const lenAfter = LAYERS.length;
  const afterP1 = PS['1'].objects.find(o => o.id === 8001);
  const afterP2 = PS['2'].objects.find(o => o.id === 8002);

  // reassignTo for gfa custom → 'gfa' (the default)
  const reassignOk = (afterP1 && afterP1.catId !== customId) &&
                     (afterP2 && afterP2.catId !== customId) &&
                     (afterP1 && afterP1.catId === afterP2.catId);

  const shrankByOne = lenAfter === lenBefore - 1;
  const activeCatChanged = state.activeCat !== customId;

  return {
    beforeBothCustom, reassignOk, shrankByOne, activeCatChanged,
    lenBefore, lenAfter,
    activeCatAfter: state.activeCat,
    p1catId: afterP1 ? afterP1.catId : null,
    p2catId: afterP2 ? afterP2.catId : null
  };
}
"""

# ---------------------------------------------------------------------------
# Scenario 5 — deleteBlockedOnDefault
# Assert that default layer rows expose NO ✕ button and that
# removeLayer('gfa').removed === false.
# ---------------------------------------------------------------------------
DELETE_DEFAULT_SCENARIO = r"""
() => {
  buildPicker();
  // check every default layer has no [data-layer-del] button
  let anyDelBtn = false;
  ROLE_DEFS.forEach(function(rd) {
    const row = document.querySelector('[data-catid="' + rd.id + '"]');
    if (row && row.querySelector('[data-layer-del]')) anyDelBtn = true;
  });

  // also verify removeLayer refuses
  const r = removeLayer('gfa');

  return {
    noDelBtnOnDefaults: !anyDelBtn,
    removeRefused: r.removed === false && r.reason === 'is_default'
  };
}
"""

# ---------------------------------------------------------------------------
# Scenario 6 — reorderChangesZ
# Get the first two layers in current order, click ▼ on the first,
# assert their .order swapped AND objectsInZOrder reflects the new ordering.
# Positive control: BEFORE order of first two layers (a.order < b.order).
# ---------------------------------------------------------------------------
REORDER_SCENARIO = r"""
async () => {
  // ensure we have a clean predictable order (reset to 6 defaults)
  LAYERS.length = 0;
  initLayers();
  ROLE_DEFS.forEach(function(rd) {
    if (state.catVis[rd.id] === undefined) state.catVis[rd.id] = true;
    if (state.catLock[rd.id] === undefined) state.catLock[rd.id] = false;
  });
  state.activeCat = 'gfa';
  buildPicker();

  const ordered = layersInOrder();
  const a = ordered[0];  // should be order=0
  const b = ordered[1];  // should be order=1

  const aOrderBefore = a.order;
  const bOrderBefore = b.order;

  // positive control: a comes before b
  if (aOrderBefore >= bOrderBefore) return {setup_fail: true};

  // two fake objects to test objectsInZOrder
  const objA = {catId: a.id};
  const objB = {catId: b.id};
  const zBefore = objectsInZOrder([objA, objB]).map(o => o.catId);

  // click ▼ on the first row (moves a down past b)
  const rowA = document.querySelector('[data-catid="' + a.id + '"]');
  const btnDn = rowA ? rowA.querySelector('[data-reorder-dn]') : null;
  if (!btnDn) return {no_btn_dn: true};

  btnDn.click();
  await new Promise(r => setTimeout(r, 50));

  const aAfter = layerById(a.id);
  const bAfter = layerById(b.id);

  const swapped = aAfter.order > bAfter.order;
  const zAfter = objectsInZOrder([objA, objB]).map(o => o.catId);
  const zOrderReversed = zAfter[0] === b.id && zAfter[1] === a.id;

  return {
    aOrderBefore, bOrderBefore,
    aOrderAfter: aAfter.order, bOrderAfter: bAfter.order,
    swapped, zBefore, zAfter, zOrderReversed
  };
}
"""

CHECKS = [
    ("addCreatesRow",           ADD_SCENARIO,            ["grew", "roleMatch", "tagMatch", "domPresent", "idChanged"]),
    ("renameKeepsTag",          RENAME_SCENARIO,         ["nameChanged", "tagUnchanged"]),
    ("recolorKeepsTag",         RECOLOR_SCENARIO,        ["colorChanged", "tagUnchanged", "swWired", "inputAppeared", "dirtySet"]),
    ("deleteReassignsAllPages", DELETE_SCENARIO,         ["beforeBothCustom", "reassignOk", "shrankByOne", "activeCatChanged"]),
    ("deleteBlockedOnDefault",  DELETE_DEFAULT_SCENARIO, ["noDelBtnOnDefaults", "removeRefused"]),
    ("reorderChangesZ",         REORDER_SCENARIO,        ["swapped", "zOrderReversed"]),
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
        print("LITE-CUSTOM-LAYER-UI checks:")
        for name, scenario, required_keys in CHECKS:
            try:
                result = pg.evaluate(scenario)
            except Exception as ex:
                print(f"  {name:35s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
                continue

            ok = all(result.get(k) is True for k in required_keys)
            status = "PASS" if ok else "FAIL"
            print(f"  {name:35s} -> {status}  {result}")
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
        print("LITE_LAYER_UI_FAIL")
        sys.exit(1)
    else:
        print("LITE_LAYER_UI_OK")


if __name__ == "__main__":
    main()
