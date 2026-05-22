"""
LITE-LAYER-ZORDER-LOCK regression guard.

Tests two behaviours introduced in the layer-system L2a sprint:

  GROUP A — z-order (objectsInZOrder):
    zRenderOrder   ded object appears AFTER gfa object in objectsInZOrder result
                   (ascending order means ded renders ON TOP of gfa)
    zHitTopWins    pick() at a point inside both overlapping objects returns
                   the ded object (topmost layer, highest .order) not the gfa one
    zNoMutate      calling objectsInZOrder() does not reorder PSpage().objects
                   (insertion order is preserved for save/export)

  GROUP B — lock:
    lockBlocksSelect  state.catLock[catId]=true => pick() returns null at that
                      object's location (locked layer not selectable)
    lockStillRenders  a locked object still appears in objectsInZOrder draw set
                      (lock != hide)
    lockIndependentOfEye  toggling catLock does not change catVis and vice-versa

Emits LITE_ZORDER_OK and LITE_LOCK_OK on success.

    py -3 lite/tests/test_layer_zorder_lock.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8290):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# --------------------------------------------------------------------------
# GROUP A — z-order
# Geometry (PDF points, V default: k=1, ox=0, oy=0, rot=0):
#   gfa  square: (0,0)-(200,0)-(200,200)-(0,200)   screen: (0,0)-(300,0)-(300,300)-(0,300)
#   ded  square: (40,40)-(160,40)-(160,160)-(40,160) screen: (60,60)-(240,60)-(240,240)-(60,240)
#   overlap click at screen (150,150) = PDF pt (100,100) → inside both
# --------------------------------------------------------------------------
SCENARIO_A = r"""
() => {
  const out = {};

  // Setup: page 1 with a dummy canvas image so draw() doesn't bail early
  curPage = 1;
  PS[1] = { objects: [], scale: { pts_per_m: 10 }, annotations: [] };
  const dummy = document.createElement('canvas');
  dummy.width = 600; dummy.height = 600;
  window.curImg = dummy;

  // gfa polygon (lower order = 0) — larger square
  const gfaObj = {
    id: 9001, catId: 'gfa', semanticTag: 'gross_floor_area',
    kind: 'poly', counting: false, dimVisible: false,
    pts: [{x:0,y:0},{x:200,y:0},{x:200,y:200},{x:0,y:200}]
  };
  // ded polygon (higher order = 2) — inner square, overlaps gfa
  const dedObj = {
    id: 9002, catId: 'ded', semanticTag: 'deduction_opening',
    kind: 'poly', counting: false, dimVisible: false,
    pts: [{x:40,y:40},{x:160,y:40},{x:160,y:160},{x:40,y:160}]
  };
  // Push gfa first so insertion order is [gfa, ded]
  PSpage().objects.push(gfaObj, dedObj);

  // Make both layers visible and unlocked for group A
  state.catVis['gfa'] = true;  state.catLock['gfa'] = false;
  state.catVis['ded'] = true;  state.catLock['ded'] = false;
  state.sel = null;

  // --- zRenderOrder: objectsInZOrder result has ded AFTER gfa (higher order = on top) ---
  const zArr = objectsInZOrder(PSpage().objects);
  const zGfaIdx = zArr.indexOf(gfaObj);
  const zDedIdx = zArr.indexOf(dedObj);
  out.zRenderOrder = zGfaIdx !== -1 && zDedIdx !== -1 && zGfaIdx < zDedIdx;

  // --- zHitTopWins: pick() at overlap returns ded (topmost), not gfa ---
  // Screen coords (150,150): RS=1.5, k=1, ox=0 → PDF pt (100,100) inside both polygons
  setTool('select');
  const hit = pick(150, 150);
  out.zHitTopWins = hit === dedObj;

  // --- zNoMutate: original PSpage().objects still has gfa at index 0 ---
  const orig = PSpage().objects;
  out.zNoMutate = orig[0] === gfaObj && orig[1] === dedObj;

  return out;
}
"""

CHECKS_A = ["zRenderOrder", "zHitTopWins", "zNoMutate"]

# --------------------------------------------------------------------------
# GROUP B — lock
# Reuses the same geometry from group A but starts fresh (new PS)
# --------------------------------------------------------------------------
SCENARIO_B = r"""
() => {
  const out = {};

  // Fresh page setup
  curPage = 2;
  PS[2] = { objects: [], scale: { pts_per_m: 10 }, annotations: [] };
  const dummy = document.createElement('canvas');
  dummy.width = 600; dummy.height = 600;
  window.curImg = dummy;

  // One gfa polygon
  const gfaObj = {
    id: 9003, catId: 'gfa', semanticTag: 'gross_floor_area',
    kind: 'poly', counting: false, dimVisible: false,
    pts: [{x:0,y:0},{x:200,y:0},{x:200,y:200},{x:0,y:200}]
  };
  PSpage().objects.push(gfaObj);

  // Reset vis/lock
  state.catVis['gfa'] = true;  state.catLock['gfa'] = false;
  state.catVis['ded'] = true;  state.catLock['ded'] = false;
  state.sel = null;
  setTool('select');

  // Sanity: pick works before locking
  const hitBefore = pick(150, 150);
  const sanityOk = hitBefore === gfaObj;

  // --- lockBlocksSelect: lock gfa => pick returns null ---
  state.catLock['gfa'] = true;
  const hitLocked = pick(150, 150);
  out.lockBlocksSelect = sanityOk && hitLocked === null;

  // --- lockStillRenders: locked object still in objectsInZOrder draw set ---
  const drawSet = objectsInZOrder(PSpage().objects);
  out.lockStillRenders = drawSet.indexOf(gfaObj) !== -1;

  // --- lockIndependentOfEye: toggling lock does not change catVis, and vice versa ---
  // currently: catLock['gfa']=true, catVis['gfa']=true
  const visBefore = state.catVis['gfa'];
  // toggle lock off then on — vis must be unchanged
  state.catLock['gfa'] = false;
  state.catLock['gfa'] = true;
  const visAfterLockToggle = state.catVis['gfa'];

  // toggle vis — lock must be unchanged
  const lockBefore = state.catLock['gfa'];
  state.catVis['gfa'] = false;
  state.catVis['gfa'] = true;
  const lockAfterVisToggle = state.catLock['gfa'];

  out.lockIndependentOfEye = (visBefore === visAfterLockToggle) && (lockBefore === lockAfterVisToggle);

  // --- lockBlocksDraw: drives the REAL app finishDraft() guard, not a copy of it ---
  // Locked active layer => finishDraft() must discard the draft and commit nothing.
  // Positive control (unlocked => commits) proves the assertion is not trivially true.
  setTool('poly');
  state.activeCat = 'gfa';
  state.catLock['gfa'] = true;
  state.draft = [{x:10,y:10},{x:200,y:10},{x:200,y:200}];   // valid 3-pt poly draft
  const lockedBefore = PSpage().objects.length;
  finishDraft();                                            // REAL app function (guard at its top)
  const lockedAfter = PSpage().objects.length;
  const blockedWhenLocked = (lockedAfter === lockedBefore) && (state.draft === null);

  // positive control: unlock => same finishDraft DOES commit (so the test detects the difference)
  state.catLock['gfa'] = false;
  state.draft = [{x:10,y:10},{x:200,y:10},{x:200,y:200}];
  const unlockedBefore = PSpage().objects.length;
  finishDraft();
  const unlockedAfter = PSpage().objects.length;
  const commitsWhenUnlocked = (unlockedAfter === unlockedBefore + 1);

  out.lockBlocksDraw = blockedWhenLocked && commitsWhenUnlocked;

  // cleanup
  state.catLock['gfa'] = false;
  setTool('select');

  return out;
}
"""

CHECKS_B = ["lockBlocksSelect", "lockStillRenders", "lockIndependentOfEye", "lockBlocksDraw"]


def main():
    from server_lite import app as lite_app
    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)

    failures_a = []
    failures_b = []
    page_errors = []

    with sync_playwright() as pw:
        b = pw.chromium.launch()

        # --- GROUP A ---
        pg = b.new_page()
        pg.on("pageerror", lambda e: page_errors.append(f"pageerror: {e}"))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(0.6)
        res_a = pg.evaluate(SCENARIO_A)
        pg.close()

        # --- GROUP B ---
        pg2 = b.new_page()
        pg2.on("pageerror", lambda e: page_errors.append(f"pageerror: {e}"))
        pg2.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(0.6)
        res_b = pg2.evaluate(SCENARIO_B)
        pg2.close()

        b.close()

    server.should_exit = True
    time.sleep(0.4)

    # Report any page-level JS errors
    for e in page_errors:
        print("  JS ERROR:", e)

    # --- Print GROUP A results ---
    print()
    print("GROUP A — z-order:")
    for k in CHECKS_A:
        ok = res_a.get(k)
        print(f"  {k:20s} -> {ok}")
        if ok is not True:
            failures_a.append(f"check '{k}' = {ok!r} (expected True)")

    if failures_a:
        for f in failures_a:
            print("FAIL:", f)
        print("LITE_ZORDER_FAIL")
    else:
        print("LITE_ZORDER_OK")

    # --- Print GROUP B results ---
    print()
    print("GROUP B — lock:")
    for k in CHECKS_B:
        ok = res_b.get(k)
        print(f"  {k:20s} -> {ok}")
        if ok is not True:
            failures_b.append(f"check '{k}' = {ok!r} (expected True)")

    if failures_b:
        for f in failures_b:
            print("FAIL:", f)
        print("LITE_LOCK_FAIL")
    else:
        print("LITE_LOCK_OK")

    if failures_a or failures_b or page_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
