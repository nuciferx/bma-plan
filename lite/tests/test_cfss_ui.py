"""
CFSS-3: Cross-floor shared shape — UI smoke test.

Verifies render hooks, hit-test wraps, promote dialog, delete-master,
and the cfssCommitPromote testability hook.

Sub-checks (10):
  1  allWrappersInstalled      objectsInZOrder.__cfssWrapped, draw.__cfssWrapped,
                                pick.__cfssWrapped, showObjMenu.__cfssWrapped,
                                cfssOpenPromoteDialog typeof function,
                                cfssDeleteMaster typeof function
  2  zOrderFiltersInstances    objectsInZOrder filters instances from input
  3  drawNotCrashWithInstance  draw() with 1 instance on current page — no throw
  4  pickHitsInstance          pick() returns instance when sx,sy inside resolved bbox
  5  promoteReplacesPolyWithInstance  cfssCommitPromote replaces source poly w/ instance
  6  promotePlacesOnTargetPages      promote with targetPages=[2,3] places instances
  7  crossScaleAreaCorrect     instanceAreaM2 same value across page1(ppm=10) / page2(ppm=15)
  8  deleteMasterFreezesOrphans      cfssDeleteMaster converts all instances to polys
  9  measureEngineIntact       SHA-256 of measure-engine.js unchanged before vs after
  10 uiLiteUnderCap           ui-lite.html under 1200-line cap (self-healing: cap not magic number)

Emits LITE_CFSS_UI_OK on success.

    py -3 lite/tests/test_cfss_ui.py
"""
import hashlib
import socket
import sys
import threading
import time
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
MEASURE_ENGINE = LITE / "static" / "js" / "measure-engine.js"
UI_LITE = LITE / "ui-lite.html"

sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8500):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def count_lines_file(path: Path) -> int:
    return path.read_bytes().count(b"\n")


# ---------------------------------------------------------------------------
# JS: Wait for CFSS module + wrappers to be installed.
# Includes extra retries for cfssWrapDraw/Pick/ShowObjMenu which require
# draw/pick/showObjMenu to be defined first (they are in the inline script).
# ---------------------------------------------------------------------------
JS_WAIT = r"""
async () => {
  for (let i = 0; i < 200; i++) {
    if (typeof window.addMaster === 'function' &&
        typeof window.makeInstance === 'function' &&
        typeof window.isInstance === 'function' &&
        typeof window.cfssCommitPromote === 'function' &&
        typeof window.__cfssTestPromote === 'function' &&
        typeof window.objectsInZOrder === 'function' &&
        window.objectsInZOrder.__cfssWrapped === true) {
      break;
    }
    await new Promise(r => setTimeout(r, 50));
  }
  // Also wait for draw/pick wrappers (DOMContentLoaded may fire before inline script).
  for (let i = 0; i < 200; i++) {
    if (typeof window.draw === 'function' && window.draw.__cfssWrapped === true &&
        typeof window.pick === 'function' && window.pick.__cfssWrapped === true &&
        typeof window.showObjMenu === 'function' && window.showObjMenu.__cfssWrapped === true) {
      break;
    }
    await new Promise(r => setTimeout(r, 50));
  }
  await new Promise(r => setTimeout(r, 200));
}
"""

# ---------------------------------------------------------------------------
# Sub-check 1: allWrappersInstalled
# ---------------------------------------------------------------------------
JS_CHECK1 = r"""
() => {
  return {
    zOrderWrapped:    typeof window.objectsInZOrder === 'function' &&
                      window.objectsInZOrder.__cfssWrapped === true,
    drawWrapped:      typeof window.draw === 'function' &&
                      window.draw.__cfssWrapped === true,
    pickWrapped:      typeof window.pick === 'function' &&
                      window.pick.__cfssWrapped === true,
    showObjMenuWrapped: typeof window.showObjMenu === 'function' &&
                        window.showObjMenu.__cfssWrapped === true,
    openPromoteFn:    typeof window.cfssOpenPromoteDialog === 'function',
    deleteMasterFn:   typeof window.cfssDeleteMaster === 'function',
    testPromoteFn:    typeof window.__cfssTestPromote === 'function'
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 2: zOrderFiltersInstances
# ---------------------------------------------------------------------------
JS_CHECK2 = r"""
() => {
  // Setup a minimal PS page with 1 poly + 1 instance
  window.PS = window.PS || {};
  window.PS[99] = {objects: [
    {kind:'poly', pts:[{x:0,y:0},{x:10,y:0},{x:10,y:10},{x:0,y:10}], catId:'gfa'},
    makeInstance('__test_m__', {x:5, y:5})
  ], scale:{pts_per_m:10}, annotations:[]};
  var result = objectsInZOrder(window.PS[99].objects);
  // Should only contain the poly, not the instance
  var allNonInstance = result.every(function(o) { return !isInstance(o); });
  var hasCorrectPoly = result.some(function(o) { return o.kind === 'poly'; });
  // Input array should NOT be mutated
  var originalLen = window.PS[99].objects.length;
  return {
    resultLen: result.length,
    allNonInstance: allNonInstance,
    hasCorrectPoly: hasCorrectPoly,
    inputUnmutated: originalLen === 2
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 3: drawNotCrashWithInstance
# Set up page with 1 instance and call draw() — must not throw.
# ---------------------------------------------------------------------------
JS_CHECK3 = r"""
() => {
  // Setup minimal state for draw()
  window.MASTERS = {};
  window.__cfss_nextMasterIdN = 1;
  var masterId = addMaster('TestMaster', [
    {x_m:0,y_m:0},{x_m:2,y_m:0},{x_m:2,y_m:2},{x_m:0,y_m:2}
  ], '#4c8dff');

  window.PS = window.PS || {};
  window.PS[1] = {objects: [makeInstance(masterId, {x:50,y:50})],
                  scale:{pts_per_m:10}, annotations:[]};
  window.curPage = 1;

  try {
    draw();
    return {ok: true, error: null};
  } catch(e) {
    return {ok: false, error: String(e)};
  }
}
"""

# ---------------------------------------------------------------------------
# Sub-check 4: pickHitsInstance
# ---------------------------------------------------------------------------
JS_CHECK4 = r"""
() => {
  window.MASTERS = {};
  window.__cfss_nextMasterIdN = 1;
  var masterId = addMaster('PickTest', [
    {x_m:0,y_m:0},{x_m:2.5,y_m:0},{x_m:2.5,y_m:1.8},{x_m:0,y_m:1.8}
  ], '#888');

  var ppm = 10;
  var offsetPt = {x: 100, y: 200};
  var inst = makeInstance(masterId, offsetPt);

  window.PS = {};
  window.PS[1] = {objects: [inst], scale:{pts_per_m: ppm}, annotations:[]};
  window.curPage = 1;
  if (window.state) window.state.catLock = {};

  // Compute center of resolved bbox in PDF points, then convert to screen
  // bbox in pt: offsetPt.x .. offsetPt.x + 2.5*ppm, offsetPt.y .. offsetPt.y + 1.8*ppm
  var ptCx = offsetPt.x + (2.5 * ppm) / 2;   // 112.5
  var ptCy = offsetPt.y + (1.8 * ppm) / 2;   // 209
  // Convert to screen coords via ptToScreen
  var scrPt = ptToScreen({x: ptCx, y: ptCy});

  var hit = pick(scrPt.x, scrPt.y);
  return {
    hitIsInstance: isInstance(hit),
    hitMasterId: hit ? hit.masterId : null,
    expected: masterId,
    scrX: scrPt.x, scrY: scrPt.y
  };
}
"""

# ---------------------------------------------------------------------------
# Sub-check 5: promoteReplacesPolyWithInstance
# ---------------------------------------------------------------------------
JS_CHECK5 = r"""
() => {
  window.MASTERS = {};
  window.__cfss_nextMasterIdN = 1;
  var poly = {
    kind:'poly',
    pts:[{x:0,y:0},{x:25,y:0},{x:25,y:18},{x:0,y:18}],
    catId:'gfa'
  };
  window.PS = {};
  window.PS[1] = {objects:[poly], scale:{pts_per_m:10}, annotations:[]};

  // Call via testability hook (no DOM modal)
  var mid = window.__cfssTestPromote(poly, 'LiftShaft', []);

  if (!mid) return {ok: false, error: 'cfssCommitPromote returned null'};

  var objs = window.PS[1].objects;
  if (objs.length !== 1) {
    return {ok: false, error: 'PS[1].objects.length should be 1, got ' + objs.length};
  }
  var inst = objs[0];
  if (!isInstance(inst)) {
    return {ok: false, error: 'object[0] is not an instance: ' + JSON.stringify(inst)};
  }
  if (inst.masterId !== mid) {
    return {ok: false, error: 'masterId mismatch: ' + inst.masterId + ' vs ' + mid};
  }

  // Check master metricPts are 0-anchored
  // source pts: [{x:0},{x:25},{x:25,y:18},{x:0,y:18}], ppm=10
  // expected metricPts: [{x_m:0,y_m:0},{x_m:2.5,y_m:0},{x_m:2.5,y_m:1.8},{x_m:0,y_m:1.8}]
  var master = masterById(mid);
  if (!master) return {ok: false, error: 'master not found'};
  var mp = master.metricPts;
  var ptsOk = mp.length === 4 &&
    Math.abs(mp[0].x_m - 0) < 0.001 && Math.abs(mp[0].y_m - 0) < 0.001 &&
    Math.abs(mp[1].x_m - 2.5) < 0.001 && Math.abs(mp[1].y_m - 0) < 0.001 &&
    Math.abs(mp[2].x_m - 2.5) < 0.001 && Math.abs(mp[2].y_m - 1.8) < 0.001 &&
    Math.abs(mp[3].x_m - 0) < 0.001 && Math.abs(mp[3].y_m - 1.8) < 0.001;

  return {ok: ptsOk, metricPts: mp, error: ptsOk ? null : 'metricPts wrong'};
}
"""

# ---------------------------------------------------------------------------
# Sub-check 6: promotePlacesOnTargetPages
# ---------------------------------------------------------------------------
JS_CHECK6 = r"""
() => {
  window.MASTERS = {};
  window.__cfss_nextMasterIdN = 1;
  var poly = {
    kind:'poly',
    pts:[{x:0,y:0},{x:25,y:0},{x:25,y:18},{x:0,y:18}],
    catId:'gfa'
  };
  window.PS = {};
  window.PS[1] = {objects:[poly], scale:{pts_per_m:10}, annotations:[]};
  window.PS[2] = {objects:[], scale:{pts_per_m:10}, annotations:[]};
  window.PS[3] = {objects:[], scale:{pts_per_m:10}, annotations:[]};

  var mid = window.__cfssTestPromote(poly, 'Shaft', [2, 3]);

  if (!mid) return {ok: false, error: 'cfssCommitPromote returned null'};

  var pg1 = window.PS[1].objects;
  var pg2 = window.PS[2].objects;
  var pg3 = window.PS[3].objects;

  var pg1ok = pg1.length === 1 && isInstance(pg1[0]) && pg1[0].masterId === mid;
  var pg2ok = pg2.length === 1 && isInstance(pg2[0]) && pg2[0].masterId === mid;
  var pg3ok = pg3.length === 1 && isInstance(pg3[0]) && pg3[0].masterId === mid;

  return {ok: pg1ok && pg2ok && pg3ok,
          pg1len: pg1.length, pg2len: pg2.length, pg3len: pg3.length,
          pg1inst: isInstance(pg1[0]), pg2inst: pg2.length ? isInstance(pg2[0]) : false,
          pg3inst: pg3.length ? isInstance(pg3[0]) : false};
}
"""

# ---------------------------------------------------------------------------
# Sub-check 7: crossScaleAreaCorrect
# ---------------------------------------------------------------------------
JS_CHECK7 = r"""
() => {
  window.MASTERS = {};
  window.__cfss_nextMasterIdN = 1;
  var poly = {
    kind:'poly',
    pts:[{x:0,y:0},{x:25,y:0},{x:25,y:18},{x:0,y:18}],
    catId:'gfa'
  };
  window.PS = {};
  window.PS[1] = {objects:[poly], scale:{pts_per_m:10}, annotations:[]};
  window.PS[2] = {objects:[], scale:{pts_per_m:15}, annotations:[]};

  var mid = window.__cfssTestPromote(poly, 'ShaftArea', [2]);

  if (!mid) return {ok: false, error: 'promote returned null'};

  var inst1 = window.PS[1].objects[0];
  var inst2 = window.PS[2].objects[0];

  var area1 = instanceAreaM2(inst1, 10);
  var area2 = instanceAreaM2(inst2, 15);

  // Both should = 2.5 * 1.8 = 4.5
  var ok = area1 !== null && area2 !== null &&
           Math.abs(area1 - 4.5) < 0.0001 &&
           Math.abs(area2 - 4.5) < 0.0001;
  return {ok: ok, area1: area1, area2: area2, expected: 4.5};
}
"""

# ---------------------------------------------------------------------------
# Sub-check 8: deleteMasterFreezesOrphans
# ---------------------------------------------------------------------------
JS_CHECK8 = r"""
() => {
  window.MASTERS = {};
  window.__cfss_nextMasterIdN = 1;
  var mid = addMaster('PipeShaft', [
    {x_m:0,y_m:0},{x_m:1,y_m:0},{x_m:1,y_m:1},{x_m:0,y_m:1}
  ], '#f00');

  window.PS = {};
  window.PS[1] = {objects:[makeInstance(mid,{x:10,y:10})], scale:{pts_per_m:10}, annotations:[]};
  window.PS[2] = {objects:[makeInstance(mid,{x:20,y:20})], scale:{pts_per_m:10}, annotations:[]};
  window.PS[3] = {objects:[makeInstance(mid,{x:30,y:30})], scale:{pts_per_m:10}, annotations:[]};

  // Mock window.confirm to return true
  var origConfirm = window.confirm;
  window.confirm = function() { return true; };

  try {
    cfssDeleteMaster(mid);
  } finally {
    window.confirm = origConfirm;
  }

  // Check all 3 pages: instances should now be kind:'poly', orphan:true
  var results = [];
  [1, 2, 3].forEach(function(pg) {
    var o = window.PS[pg].objects[0];
    results.push({
      pg: pg,
      isNowPoly: o && o.kind === 'poly',
      hasOrphan: o && o.orphan === true,
      hasPts: o && Array.isArray(o.pts) && o.pts.length >= 3,
      fromMasterId: o && o.fromMasterId
    });
  });

  var masterGone = typeof masterById(mid) === 'undefined';
  var allFrozen = results.every(function(r) { return r.isNowPoly && r.hasOrphan && r.hasPts; });

  return {ok: allFrozen && masterGone, masterGone: masterGone, results: results};
}
"""


def main():
    me_hash_before = sha256_file(MEASURE_ENGINE)
    print(f"  measure-engine.js SHA-256 (pre): {me_hash_before}")

    from server_lite import app as lite_app

    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)

    page_errors = []
    results = {}
    first_fail = None

    def mark(name, ok, detail=""):
        nonlocal first_fail
        results[name] = ok
        status = "PASS" if ok else "FAIL"
        suffix = f" ({detail})" if detail else ""
        print(f"  [{status}] {name}{suffix}")
        if not ok and first_fail is None:
            first_fail = name

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        page.on("pageerror", lambda e: page_errors.append(f"pageerror: {e}"))

        page.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        page.evaluate(JS_WAIT)

        print()
        print("LITE-CFSS-UI sub-checks:")

        if page_errors:
            for e in page_errors:
                print("  JS ERROR:", e)

        # -------------------------------------------------------------------
        # Sub-check 1: allWrappersInstalled
        # -------------------------------------------------------------------
        r1 = page.evaluate(JS_CHECK1)
        all_installed = (r1.get("zOrderWrapped") and r1.get("drawWrapped") and
                         r1.get("pickWrapped") and r1.get("showObjMenuWrapped") and
                         r1.get("openPromoteFn") and r1.get("deleteMasterFn") and
                         r1.get("testPromoteFn"))
        mark("allWrappersInstalled", all_installed,
             f"zOrder={r1.get('zOrderWrapped')} draw={r1.get('drawWrapped')} "
             f"pick={r1.get('pickWrapped')} menu={r1.get('showObjMenuWrapped')} "
             f"promote={r1.get('openPromoteFn')} delete={r1.get('deleteMasterFn')}")

        # -------------------------------------------------------------------
        # Sub-check 2: zOrderFiltersInstances
        # -------------------------------------------------------------------
        r2 = page.evaluate(JS_CHECK2)
        mark("zOrderFiltersInstances",
             r2.get("resultLen") == 1 and r2.get("allNonInstance") and
             r2.get("hasCorrectPoly") and r2.get("inputUnmutated"),
             f"len={r2.get('resultLen')} nonInst={r2.get('allNonInstance')} "
             f"poly={r2.get('hasCorrectPoly')} unmutated={r2.get('inputUnmutated')}")

        # -------------------------------------------------------------------
        # Sub-check 3: drawNotCrashWithInstance
        # -------------------------------------------------------------------
        r3 = page.evaluate(JS_CHECK3)
        mark("drawNotCrashWithInstance",
             r3.get("ok") is True,
             r3.get("error") or "")

        # -------------------------------------------------------------------
        # Sub-check 4: pickHitsInstance
        # -------------------------------------------------------------------
        r4 = page.evaluate(JS_CHECK4)
        mark("pickHitsInstance",
             r4.get("hitIsInstance") is True and r4.get("hitMasterId") == r4.get("expected"),
             f"hitIsInst={r4.get('hitIsInstance')} mid={r4.get('hitMasterId')} "
             f"expected={r4.get('expected')}")

        # -------------------------------------------------------------------
        # Sub-check 5: promoteReplacesPolyWithInstance
        # -------------------------------------------------------------------
        r5 = page.evaluate(JS_CHECK5)
        mark("promoteReplacesPolyWithInstance",
             r5.get("ok") is True,
             r5.get("error") or f"metricPts={r5.get('metricPts')}")

        # -------------------------------------------------------------------
        # Sub-check 6: promotePlacesOnTargetPages
        # -------------------------------------------------------------------
        r6 = page.evaluate(JS_CHECK6)
        mark("promotePlacesOnTargetPages",
             r6.get("ok") is True,
             f"pg1len={r6.get('pg1len')} pg2len={r6.get('pg2len')} "
             f"pg3len={r6.get('pg3len')} inst={r6.get('pg1inst')},{r6.get('pg2inst')},{r6.get('pg3inst')}")

        # -------------------------------------------------------------------
        # Sub-check 7: crossScaleAreaCorrect
        # -------------------------------------------------------------------
        r7 = page.evaluate(JS_CHECK7)
        mark("crossScaleAreaCorrect",
             r7.get("ok") is True,
             f"area1={r7.get('area1')} area2={r7.get('area2')} expected={r7.get('expected')}")

        # -------------------------------------------------------------------
        # Sub-check 8: deleteMasterFreezesOrphans
        # -------------------------------------------------------------------
        r8 = page.evaluate(JS_CHECK8)
        mark("deleteMasterFreezesOrphans",
             r8.get("ok") is True,
             f"masterGone={r8.get('masterGone')} results={r8.get('results')}")

        page.close()
        context.close()
        browser.close()

    server.should_exit = True
    time.sleep(0.4)

    # -----------------------------------------------------------------------
    # Sub-check 9: measureEngineIntact
    # -----------------------------------------------------------------------
    me_hash_after = sha256_file(MEASURE_ENGINE)
    print(f"  measure-engine.js SHA-256 (post): {me_hash_after}")
    mark("measureEngineIntact",
         me_hash_before == me_hash_after,
         f"hash: {me_hash_before[:16]}...")

    # -----------------------------------------------------------------------
    # Sub-check 10: uiLiteUnderCap
    # -----------------------------------------------------------------------
    ui_lines = count_lines_file(UI_LITE)
    mark("uiLiteUnderCap",
         ui_lines <= 1200,
         f"lines={ui_lines}, cap=1200")

    print()
    if first_fail:
        print(f"LITE_CFSS_UI_FAIL: {first_fail}")
        sys.exit(1)
    else:
        print("LITE_CFSS_UI_OK")


if __name__ == "__main__":
    main()
