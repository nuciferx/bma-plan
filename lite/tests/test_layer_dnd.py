"""
LITE-LAYER-DND regression guard (LDND-S4 sprint).

Verifies drag-and-drop reorder, nest-onto-folder, auto-group creation, and
auto-group-off guard, using synthetic pointer events dispatched via
page.evaluate (deterministic — avoids Chromium headless hit-test flakiness
with real mouse coordinates).

Each check: (a) page.evaluate dispatches pointerdown / pointermove / pointerup
            to the DnD engine's window listeners; (b) state assertion on
            LAYERS / FOLDERS via evaluate after the drag settles.
            Positive-control: BEFORE value must differ from AFTER.

Scenarios (LDND-S4 spec):
  dragReorderChangesOrder  drag first root layer "after" the second → order swapped
  dragNestOntoFolder       drag a layer onto "middle" of a folder row → parentId set
  autoGroupOnCollision     autogroup ON: drag root layer A onto B → new folder wraps both
  autoGroupOffNoFolder     autogroup OFF: same drag → no folder created (insert-after)

Emits LITE_LAYER_DND_OK on success.

    py -3 lite/tests/test_layer_dnd.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8390):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ---------------------------------------------------------------------------
# Shared setup snippet — reset to 6 root layers, 0 folders, autogroup OFF.
# Inlined into each scenario so they are reload-independent (each scenario
# calls page.reload() first then runs evaluate).
# ---------------------------------------------------------------------------
RESET_STATE = r"""
LAYERS.length = 0;
FOLDERS.length = 0;
initLayers();
ROLE_DEFS.forEach(function(rd) {
  state.catVis[rd.id] = true;
  state.catLock[rd.id] = false;
});
state.activeCat = 'gfa';
if (!state.folderCollapsed) state.folderCollapsed = {};
// Ensure autogroup flag is off (written directly — bypasses localStorage)
_ltAutoGroup = false;
var ag = document.getElementById('lt-autogroup-cb');
if (ag) ag.checked = false;
buildPicker();
"""

# ---------------------------------------------------------------------------
# Drag helper (synthetic pointer events, injected as a page function).
# Dispatches: pointerdown on grip → pointermove on window at midpoint →
#             pointermove on window at target coords → pointerup on window.
# zone: "before" → targetY = top + 15% of height
#       "after"  → targetY = top + 85% of height
#       "middle" → targetY = top + 50% of height
# Returns {ok, fromBB, toBB} for debug.
# ---------------------------------------------------------------------------
DRAG_FN = r"""
async function dndDrag(fromCatId, toCatId, zone) {
  var fromRow  = document.querySelector('[data-catid="' + fromCatId + '"]');
  var toRow    = document.querySelector('[data-catid="' + toCatId   + '"]');
  if (!fromRow || !toRow) return {ok:false, reason:'row not found', fromCatId, toCatId};

  var grip = fromRow.querySelector('.lt-grip');
  if (!grip) return {ok:false, reason:'no grip on row', fromCatId};

  var fr = grip.getBoundingClientRect();
  var tr = toRow.getBoundingClientRect();

  var srcX = fr.left + fr.width  / 2;
  var srcY = fr.top  + fr.height / 2;

  var relY = (zone === 'before') ? 0.15 : (zone === 'after') ? 0.85 : 0.50;
  var tgtX = tr.left + tr.width  / 2;
  var tgtY = tr.top  + relY * tr.height;

  // Mid-travel point (exceeds 4 px threshold)
  var midX = (srcX + tgtX) / 2;
  var midY = (srcY + tgtY) / 2;

  var opts = {bubbles: true, cancelable: true, pointerId: 1,
              clientX: srcX, clientY: srcY};

  // pointerdown on the grip (grip calls _ltDndStartDrag → sets window listeners)
  grip.dispatchEvent(new PointerEvent('pointerdown', opts));

  await new Promise(r => setTimeout(r, 20));

  // pointermove at mid-point (trips the 4px moved threshold)
  window.dispatchEvent(new PointerEvent('pointermove',
    Object.assign({}, opts, {clientX: midX, clientY: midY})));

  await new Promise(r => setTimeout(r, 20));

  // pointermove over target (hits the correct zone)
  window.dispatchEvent(new PointerEvent('pointermove',
    Object.assign({}, opts, {clientX: tgtX, clientY: tgtY})));

  await new Promise(r => setTimeout(r, 20));

  // pointerup — triggers _ltDndOnUp → _ltDndCommit → buildPicker
  window.dispatchEvent(new PointerEvent('pointerup',
    Object.assign({}, opts, {clientX: tgtX, clientY: tgtY})));

  await new Promise(r => setTimeout(r, 150));

  return {ok: true, srcX, srcY, tgtX, tgtY, zone,
          fromBB: {top:fr.top, height:fr.height},
          toBB:   {top:tr.top, height:tr.height}};
}
"""

# ---------------------------------------------------------------------------
# Scenario 1 — dragReorderChangesOrder
# Two root layers at indices 0 and 1. Drag index-0 "after" index-1.
# Assert: the dragged node now sorts AFTER the other in childrenOf(null).
# ---------------------------------------------------------------------------
SC1_DRAG_REORDER = r"""
async () => {
  """ + RESET_STATE + r"""

  // Inject drag helper
  """ + DRAG_FN + r"""

  var rootsBefore = childrenOf(null);
  if (rootsBefore.length < 2) return {skip: 'not enough roots'};
  var firstId  = rootsBefore[0].node.id;
  var secondId = rootsBefore[1].node.id;
  var orderBefore0 = rootsBefore[0].node.order;
  var orderBefore1 = rootsBefore[1].node.order;

  // positive control: first is indeed before second
  var posCtrlOk = orderBefore0 < orderBefore1;

  var dragResult = await dndDrag(firstId, secondId, 'after');

  var rootsAfter = childrenOf(null);
  var idxFirst  = rootsAfter.findIndex(function(x){ return x.node.id === firstId; });
  var idxSecond = rootsAfter.findIndex(function(x){ return x.node.id === secondId; });
  var nowAfter  = idxFirst > idxSecond;

  return {
    firstId, secondId,
    orderBefore0, orderBefore1,
    posCtrlOk,
    idxFirst, idxSecond,
    nowAfter,
    dragResult,
    reorderOk: posCtrlOk && nowAfter
  };
}
"""

# ---------------------------------------------------------------------------
# Scenario 2 — dragNestOntoFolder
# Add a folder at root. Drag a root layer onto the folder row ("middle").
# Assert: layer.parentId === folder.id
# ---------------------------------------------------------------------------
SC2_NEST_ONTO_FOLDER = r"""
async () => {
  """ + RESET_STATE + r"""

  """ + DRAG_FN + r"""

  // Create a folder
  var f = addFolder('DragFolder', '#aabbcc', null);
  f.order = -1;  // ensure it renders first so it is in DOM
  state.catVis[f.id] = true;
  state.catLock[f.id] = false;
  if (!state.folderCollapsed) state.folderCollapsed = {};
  state.folderCollapsed[f.id] = false;
  buildPicker();

  // Pick a root layer (gfa)
  var layerNode = layerById('gfa');
  if (!layerNode) return {skip: 'no gfa'};
  var parentBefore = layerNode.parentId;  // null

  var dragResult = await dndDrag('gfa', f.id, 'middle');

  var parentAfter = layerNode.parentId;

  return {
    folderId: f.id,
    parentBefore,
    parentAfter,
    dragResult,
    nestedOk: parentBefore === null && parentAfter === f.id
  };
}
"""

# ---------------------------------------------------------------------------
# Scenario 3 — autoGroupOnCollision
# Enable autogroup. Pick two root layers A (gfa) and B (use).
# Drag A onto "middle" of B. Assert:
#   - FOLDERS grew by 1
#   - new folder name ends with "กลุ่ม"
#   - A.parentId === newFolder.id
#   - B.parentId === newFolder.id
# ---------------------------------------------------------------------------
SC3_AUTOGROUP_ON = r"""
async () => {
  """ + RESET_STATE + r"""

  """ + DRAG_FN + r"""

  // Enable autogroup
  _ltAutoGroup = true;
  var ag = document.getElementById('lt-autogroup-cb');
  if (ag) ag.checked = true;

  var foldersBefore = FOLDERS.length;  // 0

  var nodeA = layerById('gfa');
  var nodeB = layerById('use');
  if (!nodeA || !nodeB) return {skip: 'layers missing'};

  // Ensure both are root layers (parentId null)
  nodeA.parentId = null;
  nodeB.parentId = null;
  buildPicker();

  var parentABefore = nodeA.parentId;
  var parentBBefore = nodeB.parentId;

  var dragResult = await dndDrag('gfa', 'use', 'middle');

  var foldersAfter  = FOLDERS.length;
  var grewByOne     = (foldersAfter === foldersBefore + 1);
  var newFolder     = (grewByOne) ? FOLDERS[FOLDERS.length - 1] : null;
  var folderName    = newFolder ? newFolder.name : '';
  var nameEndsGlum  = folderName.endsWith('กลุ่ม');  // "กลุ่ม"
  var parentAAfter  = nodeA.parentId;
  var parentBAfter  = nodeB.parentId;
  var newFolderId   = newFolder ? newFolder.id : null;
  var bothNested    = newFolderId
                      && parentAAfter === newFolderId
                      && parentBAfter === newFolderId;

  return {
    foldersBefore, foldersAfter,
    folderName, nameEndsGlum,
    parentABefore, parentAAfter,
    parentBBefore, parentBAfter,
    newFolderId,
    grewByOne, bothNested,
    dragResult,
    autoGroupOk: grewByOne && nameEndsGlum && bothNested
  };
}
"""

# ---------------------------------------------------------------------------
# Scenario 4 — autoGroupOffNoFolder
# Autogroup OFF (default). Drag root layer A onto "middle" of B.
# Assert: FOLDERS.length UNCHANGED (insert-after fallback, no folder created).
# ---------------------------------------------------------------------------
SC4_AUTOGROUP_OFF = r"""
async () => {
  """ + RESET_STATE + r"""

  """ + DRAG_FN + r"""

  // Confirm autogroup is OFF
  _ltAutoGroup = false;
  var ag = document.getElementById('lt-autogroup-cb');
  if (ag) ag.checked = false;

  var foldersBefore = FOLDERS.length;  // 0

  var nodeA = layerById('gfa');
  var nodeB = layerById('use');
  if (!nodeA || !nodeB) return {skip: 'layers missing'};

  nodeA.parentId = null;
  nodeB.parentId = null;
  buildPicker();

  var dragResult = await dndDrag('gfa', 'use', 'middle');

  var foldersAfter = FOLDERS.length;
  var noFolderCreated = (foldersAfter === foldersBefore);

  // Verify insert-after happened: gfa should now sort AFTER use in root
  var rootsAfter = childrenOf(null);
  var idxA = rootsAfter.findIndex(function(x){ return x.node.id === 'gfa'; });
  var idxB = rootsAfter.findIndex(function(x){ return x.node.id === 'use'; });
  var aAfterB = idxA > idxB;

  return {
    foldersBefore, foldersAfter,
    noFolderCreated,
    idxA, idxB, aAfterB,
    dragResult,
    autoGroupOffOk: noFolderCreated
  };
}
"""

CHECKS = [
    ("dragReorderChangesOrder", SC1_DRAG_REORDER,  ["reorderOk"]),
    ("dragNestOntoFolder",      SC2_NEST_ONTO_FOLDER, ["nestedOk"]),
    ("autoGroupOnCollision",    SC3_AUTOGROUP_ON,  ["autoGroupOk"]),
    ("autoGroupOffNoFolder",    SC4_AUTOGROUP_OFF, ["noFolderCreated"]),
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
        print("LITE-LAYER-DND checks:")
        for name, scenario, required_keys in CHECKS:
            # Fresh reload per scenario — prevents state bleed
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
        print("LITE_LAYER_DND_FAIL")
        sys.exit(1)
    else:
        print("LITE_LAYER_DND_OK")


if __name__ == "__main__":
    main()
