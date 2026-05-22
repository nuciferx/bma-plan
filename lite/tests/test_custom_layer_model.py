"""
LITE-CUSTOM-LAYER-MODEL regression guard (L2c-1 sprint).

Verifies the runtime CRUD helpers added to layer-system.js:
  addCreatesUnique    addLayer returns a non-role id, in LAYERS, highest order;
                      two addLayers get distinct ids.
  addRejectsBadRole   addLayer('bogus',...) returns null, LAYERS unchanged.
  addTagFromRole      custom gfa layer's .tag === roleSemanticTag('gfa') (not its name).
  renameRecolorDisplay renameLayer + recolorLayer change name/color but .role/.tag intact.
  reorderRewritesOrder reorderLayers() rewrites .order; layersInOrder() and
                        objectsInZOrder() respect the new ordering.
  removeCustomReassigns removeLayer(customId) returns {removed:true, reassignTo:'gfa'};
                        layer is gone from LAYERS.
  removeDefaultRefused  removeLayer('gfa') returns {removed:false, reason:'is_default'};
                        LAYERS unchanged.

Emits LITE_LAYER_MODEL_OK on success.

    py -3 lite/tests/test_custom_layer_model.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8310):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# --------------------------------------------------------------------------
# One scenario: all checks run in a single page evaluate for speed.
# LAYERS is re-seeded between independent checks using initLayers() after
# clearing it, so checks cannot interfere.
# --------------------------------------------------------------------------
SCENARIO = r"""
() => {
  const out = {};

  // Helper: reset LAYERS to the 6 defaults
  function reseed() {
    LAYERS.length = 0;
    initLayers();
  }

  // -----------------------------------------------------------------------
  // addCreatesUnique: addLayer returns a non-role id, is in LAYERS, has
  //   the highest .order value; a second addLayer gets a DIFFERENT id.
  // -----------------------------------------------------------------------
  reseed();
  const roleIds = ROLE_DEFS.map(r => r.id);
  const startLen = LAYERS.length;

  const l1 = addLayer('gfa', 'ชั้น 2', '#80c0ff');
  const l2 = addLayer('gfa', 'ชั้น 3', '#80c0aa');

  const l1InLayers = LAYERS.indexOf(l1) !== -1;
  const l2InLayers = LAYERS.indexOf(l2) !== -1;
  const l1NotRole  = !roleIds.includes(l1.id);
  const l2NotRole  = !roleIds.includes(l2.id);
  const l1MaxOrder = layersInOrder().slice(-1)[0] !== l2   // l1 is not last (l2 is)
                     ? true                                // only valid if l2 was added
                     : true;
  // More precise: l2.order > l1.order > all original orders
  const origMaxOrder = ROLE_DEFS.length - 1; // 0..5 were seeded
  const ordersAscend = l1.order > origMaxOrder && l2.order > l1.order;
  const idsDistinct  = l1.id !== l2.id;

  out.addCreatesUnique = l1InLayers && l2InLayers && l1NotRole && l2NotRole
                       && ordersAscend && idsDistinct;

  // -----------------------------------------------------------------------
  // addRejectsBadRole: returns null, LAYERS length unchanged.
  // -----------------------------------------------------------------------
  reseed();
  const lenBefore = LAYERS.length;
  const badResult = addLayer('bogus', 'X', '#fff');
  out.addRejectsBadRole = (badResult === null) && (LAYERS.length === lenBefore);

  // -----------------------------------------------------------------------
  // addTagFromRole: custom gfa layer's .tag === roleSemanticTag('gfa'),
  //   NOT its display name.
  // -----------------------------------------------------------------------
  reseed();
  const customGfa = addLayer('gfa', 'MyCustomName', '#aabbcc');
  const expectedTag = roleSemanticTag('gfa');  // 'gross_floor_area'
  out.addTagFromRole = customGfa !== null
                    && customGfa.tag === expectedTag
                    && customGfa.tag !== customGfa.name;

  // -----------------------------------------------------------------------
  // renameRecolorDisplayOnly: name/color change; role and tag stay intact.
  // -----------------------------------------------------------------------
  reseed();
  const lx = addLayer('use', 'OrigName', '#111111');
  const origRole = lx.role;
  const origTag  = lx.tag;
  const r1 = renameLayer(lx.id, 'NewName');
  const r2 = recolorLayer(lx.id, '#ff0000');
  out.renameRecolorDisplayOnly = r1 && r2
    && lx.name === 'NewName'
    && lx.color === '#ff0000'
    && lx.role === origRole
    && lx.tag === origTag;

  // -----------------------------------------------------------------------
  // reorderRewritesOrder: after reorderLayers(), layersInOrder() reflects
  //   the new sequence AND objectsInZOrder respects it.
  //
  // Setup: seed 6 layers (gfa order=0 … count order=5).
  //   Add one custom ded layer (order=6) and one custom gfa layer (order=7).
  //   Build a permutation that puts the custom ded BEFORE the default gfa
  //   (swap them), then confirm objectsInZOrder puts a ded-cat object after
  //   a gfa-cat object in draw order when ded-custom has a higher order.
  //
  // Simpler approach: just verify layersInOrder() returns them in new order.
  // -----------------------------------------------------------------------
  reseed();
  const customDed = addLayer('ded', 'DedCustom', '#ff0000');  // order = 6
  const customGfa2= addLayer('gfa', 'GfaCustom', '#0000ff');  // order = 7

  // Build permutation: move customGfa2 to position 0, everything else shifts
  const currentIds = layersInOrder().map(l => l.id);
  // put customGfa2 first, then the rest in original order
  const permutation = [customGfa2.id].concat(currentIds.filter(id => id !== customGfa2.id));
  const roOk = reorderLayers(permutation);

  // After reorder, layersInOrder()[0] must be customGfa2
  const newOrder = layersInOrder();
  const firstIsCustomGfa2 = newOrder[0].id === customGfa2.id;

  // objectsInZOrder: create two objects on customGfa2 (low order=0) and customDed (high order=N)
  // customDed is somewhere after customGfa2 in the new order, so a ded-cat object should
  // appear AFTER a gfa-cat object that uses customGfa2's id.
  const gfaO = { id: 8001, catId: customGfa2.id, kind: 'poly', pts: [] };
  const dedO = { id: 8002, catId: customDed.id,  kind: 'poly', pts: [] };
  // customGfa2 is at index 0, customDed is somewhere after — ded renders on top (later in array)
  const zArr = objectsInZOrder([dedO, gfaO]);  // input: ded first, gfa second
  // After z-sort: gfa (lower order) should be index 0, ded (higher order) index 1
  const gfaCat2Order = customGfa2.order;
  const dedCatOrder  = customDed.order;
  const zRespects    = gfaCat2Order < dedCatOrder
                     ? zArr[0].id === 8001 && zArr[1].id === 8002
                     : zArr[0].id === 8002 && zArr[1].id === 8001;

  out.reorderRewritesOrder = roOk && firstIsCustomGfa2 && zRespects;

  // -----------------------------------------------------------------------
  // removeCustomReassigns: removeLayer(customId) returns {removed:true,
  //   reassignTo:'gfa'} and the layer is gone from LAYERS.
  // -----------------------------------------------------------------------
  reseed();
  const toRemove = addLayer('gfa', 'Temp', '#999999');
  const removeId = toRemove.id;
  const lenBeforeRemove = LAYERS.length;
  const res = removeLayer(removeId);
  const goneFromLayers = layerById(removeId) === null;
  const lenAfterRemove = LAYERS.length;
  out.removeCustomReassigns = res.removed === true
    && res.reassignTo === 'gfa'
    && goneFromLayers
    && lenAfterRemove === lenBeforeRemove - 1;

  // -----------------------------------------------------------------------
  // removeDefaultRefused: removeLayer('gfa') → {removed:false, reason:'is_default'}
  //   and LAYERS is unchanged.
  // -----------------------------------------------------------------------
  reseed();
  const lenBeforeDefault = LAYERS.length;
  const resDefault = removeLayer('gfa');
  const lenAfterDefault = LAYERS.length;
  out.removeDefaultRefused = resDefault.removed === false
    && resDefault.reason === 'is_default'
    && lenAfterDefault === lenBeforeDefault;

  // Restore clean state
  reseed();

  return out;
}
"""

CHECKS = [
    "addCreatesUnique",
    "addRejectsBadRole",
    "addTagFromRole",
    "renameRecolorDisplayOnly",
    "reorderRewritesOrder",
    "removeCustomReassigns",
    "removeDefaultRefused",
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
        result = pg.evaluate(SCENARIO)
        pg.close()
        b.close()

    server.should_exit = True
    time.sleep(0.4)

    for e in page_errors:
        print("  JS ERROR:", e)

    print()
    print("LITE-CUSTOM-LAYER-MODEL checks:")
    for k in CHECKS:
        ok = result.get(k)
        print(f"  {k:30s} -> {ok}")
        if ok is not True:
            failures.append(f"check '{k}' = {ok!r} (expected True)")

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_LAYER_MODEL_FAIL")
        sys.exit(1)
    else:
        print("LITE_LAYER_MODEL_OK")


if __name__ == "__main__":
    main()
