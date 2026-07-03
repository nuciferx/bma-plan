"""
INV-20260703-layer-linkage — approach B, slice B0 acceptance test.

Invariant under test (I11 groundwork): ObjectAgg.objectTuples() — the new
flat object-tuple stream (static/js/object-agg.js) — is a faithful, more
granular re-derivation of the SAME data computeSummary() already produces.
Nothing is rerouted to the new stream in this slice (that is B1/B2); this
test is the parity oracle that must hold BEFORE any consumer is touched.

Fixture: 3 floor-tagged pages, scale 1 pt/m, all objects catId 'gfa'/'ded'
unless noted:
  page 1 (floor 1): plain gfa poly (1200 m2), plain ded poly (25 m2),
                     a poly on an UNFILED custom layer (role=gfa, 100 m2,
                     parentId=null — not under any PF_ page-folder; M6
                     semantics: folder-scoped engines like _lovsFolderArea
                     exclude root-unfiled layers from folder totals, but
                     role-based engines — computeSummary, rollupAggByRole,
                     and this tuple stream — do not care about folder
                     membership and DO include it), an arc-edge gfa poly
                     (square 100x100 + semicircle bulge r=50 on one edge,
                     independent closed-form = 10000 + 1250*pi), and one
                     'count' counting marker.
  page 2 (floor 2): plain gfa poly (300 m2) + a poly promoted to a CFSS
                     master/instance via the real promote flow (100 m2).
  page 3 (floor 3): plain gfa poly (49 m2) — marked excluded[] AFTER the
                     oracle check, to test exclusion in isolation (see note
                     below on why exclusion can't run through the oracle).

Checks:
  tupleShapeOk        tuple count == 8 (7 area + 1 counting) and every
                       tuple carries {pg,catId,role,floorKey,area,counting,
                       count}; the counting tuple has area:null, count:1.
  oracleOk             ObjectAgg.assertEnginesAgree(1e-6).ok === true —
                       byRole() role totals == rollupAggByRole(computeSummary
                       ().all) role totals, tuple total == summary total.
                       NOTE: computeSummary() does NOT skip excluded[] pages
                       (pre-existing gap, out of scope for B0) while
                       objectTuples() does (matching _lovsLayerArea) — so
                       this check only runs with NO excluded pages present;
                       exclusion is verified directly below instead.
  floorRoleSeparationOk  byFloorRole() gives independent per-floor gfa/ded
                       buckets — floor:1 gfa != floor:2 gfa != floor:3 gfa,
                       and floor:1 ded is isolated from floor:2 (no 'ded'
                       key present there at all) — the thing no existing
                       engine (computeSummary/_lovsFolderArea/_lovsRoleArea)
                       provides in a single call.
  rootCustomIncludedOk  the unfiled custom-layer object IS present in
                       objectTuples() with role 'gfa' and contributes to
                       byRole().gfa (M6 semantics; document-only, no
                       assertion against the folder-scoped engines here).
  excludedSkippedOk    after excluded[3]=true, objectTuples() drops all
                       page-3 tuples and byRole().gfa shrinks by exactly
                       page 3's area.

Emits LITE_OBJECT_TUPLES_OK on success.

    py -3 lite/tests/test_object_tuples.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8520):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


SETUP_STATE = r"""
var P1 = 1, P2 = 2, P3 = 3;
PS = {};
excluded = {};
pageTags = {}; pageFloorKind = {}; pageFloorNum = {};

pageTags[P1] = 'floor'; pageFloorKind[P1] = 'normal'; pageFloorNum[P1] = 1;
pageTags[P2] = 'floor'; pageFloorKind[P2] = 'normal'; pageFloorNum[P2] = 2;
pageTags[P3] = 'floor'; pageFloorKind[P3] = 'normal'; pageFloorNum[P3] = 3;

PS[P1] = {objects: [], scale: {pts_per_m: 1}, annotations: []};
PS[P2] = {objects: [], scale: {pts_per_m: 1}, annotations: []};
PS[P3] = {objects: [], scale: {pts_per_m: 1}, annotations: []};
curPage = P1;

var rootLayer = addLayer('gfa', 'Root Custom (unfiled)', '#8844ff');  // parentId:null by construction

// --- page 1: floor 1 ---
var gfa1 = {id: state._id++, catId: 'gfa', semanticTag: 'gross_floor_area', kind: 'poly',
  counting: false, dimVisible: true, pts: [{x:0,y:0},{x:40,y:0},{x:40,y:30},{x:0,y:30}]};             // 1200 m2
var ded1 = {id: state._id++, catId: 'ded', semanticTag: 'deduction_opening', kind: 'poly',
  counting: false, dimVisible: true, pts: [{x:100,y:0},{x:105,y:0},{x:105,y:5},{x:100,y:5}]};         // 25 m2
var root1 = {id: state._id++, catId: rootLayer.id, semanticTag: 'gross_floor_area', kind: 'poly',
  counting: false, dimVisible: true, pts: [{x:200,y:0},{x:210,y:0},{x:210,y:10},{x:200,y:10}]};       // 100 m2, unfiled layer
var v0 = {x:300,y:0}, v1 = {x:400,y:0}, v2 = {x:400,y:100}, v3 = {x:300,y:100};
var tp = {x:450,y:50};
var arcInfo = computeArcEdge(v1, v2, tp, {x:350,y:50});
var arc1 = {id: state._id++, catId: 'gfa', semanticTag: 'gross_floor_area', kind: 'poly',
  counting: false, dimVisible: true, pts: [v0, v1, v2, v3],
  edges: [null, {edgeType:'arc', arcSweep: arcInfo.sweep, arcThrough:{x:tp.x,y:tp.y}}, null, null]};  // 10000 + 1250*pi m2
var count1 = {id: state._id++, catId: 'count', semanticTag: 'count_marker', kind: 'count',
  counting: true, dimVisible: false, pts: [{x:1,y:1}]};
PS[P1].objects.push(gfa1, ded1, root1, arc1, count1);

// --- page 2: floor 2 ---
var gfa2 = {id: state._id++, catId: 'gfa', semanticTag: 'gross_floor_area', kind: 'poly',
  counting: false, dimVisible: true, pts: [{x:0,y:0},{x:20,y:0},{x:20,y:15},{x:0,y:15}]};             // 300 m2
var promo2 = {id: state._id++, catId: 'gfa', semanticTag: 'gross_floor_area', kind: 'poly',
  counting: false, dimVisible: true, pts: [{x:50,y:0},{x:60,y:0},{x:60,y:10},{x:50,y:10}]};           // 100 m2, promoted below
PS[P2].objects.push(gfa2, promo2);

// --- page 3: floor 3 (excluded LATER in this scenario, after the oracle check) ---
var gfa3 = {id: state._id++, catId: 'gfa', semanticTag: 'gross_floor_area', kind: 'poly',
  counting: false, dimVisible: true, pts: [{x:0,y:0},{x:7,y:0},{x:7,y:7},{x:0,y:7}]};                 // 49 m2
PS[P3].objects.push(gfa3);
"""

SC_OBJECT_TUPLES = r"""
async () => {
  if (typeof window.ObjectAgg !== 'object') return {pass: false, err: 'ObjectAgg not loaded'};

  // cross-floor-shapes.js is dynamically injected — wait for the promote hook
  for (var i = 0; i < 80 && typeof window.__cfssTestPromote !== 'function'; i++) {
    await new Promise(function(r) { setTimeout(r, 50); });
  }
  if (typeof window.__cfssTestPromote !== 'function') return {pass: false, err: 'cfss module not loaded'};

  """ + SETUP_STATE + r"""

  var mid = window.__cfssTestPromote(promo2, 'Lift2', []);
  if (!mid) return {pass: false, err: 'promote failed'};

  function close(a, b) { return Math.abs(a - b) < 1e-6 * Math.max(1, Math.abs(b)); }

  var expectedArcArea = 10000 + Math.PI * 50 * 50 / 2;              // 13926.99...
  var expFloor1Gfa = 1200 + 100 + expectedArcArea;
  var expFloor1Ded = 25;
  var expFloor2Gfa = 300 + 100;
  var expFloor3Gfa = 49;
  var expTotalGfa = expFloor1Gfa + expFloor2Gfa + expFloor3Gfa;

  /* -------------------------------------------------------------- */
  /* (i) tuple count/shape                                          */
  /* -------------------------------------------------------------- */
  var tuples = window.ObjectAgg.objectTuples();
  var lenOk = tuples.length === 8;                                  // 7 area + 1 counting
  var shapeOk = tuples.every(function(t) {
    return ('pg' in t) && ('catId' in t) && ('role' in t) &&
           ('floorKey' in t) && ('area' in t) && ('counting' in t) && ('count' in t);
  });
  var countTuple = tuples.filter(function(t) { return t.counting === true; })[0];
  var countShapeOk = !!countTuple && countTuple.area === null && countTuple.count === 1 &&
                      countTuple.role === 'count' && countTuple.pg === P1;
  var tupleShapeOk = lenOk && shapeOk && countShapeOk;

  /* -------------------------------------------------------------- */
  /* (ii) oracle: byRole() vs computeSummary()+rollupAggByRole()     */
  /*      (run BEFORE any exclusion — computeSummary() does not      */
  /*      skip excluded[] pages, see file docstring)                 */
  /* -------------------------------------------------------------- */
  var oracle = window.ObjectAgg.assertEnginesAgree(1e-6);
  var oracleOk = oracle.ok === true;

  /* -------------------------------------------------------------- */
  /* (iii) per-floor role separation                                 */
  /* -------------------------------------------------------------- */
  var bfr = window.ObjectAgg.byFloorRole(tuples);
  var f1 = bfr['floor:1'] || {}, f2 = bfr['floor:2'] || {}, f3 = bfr['floor:3'] || {};
  var floor1GfaOk = !!f1.gfa && close(f1.gfa.area, expFloor1Gfa);
  var floor1DedOk = !!f1.ded && close(f1.ded.area, expFloor1Ded);
  var floor2GfaOk = !!f2.gfa && close(f2.gfa.area, expFloor2Gfa);
  var floor3GfaOk = !!f3.gfa && close(f3.gfa.area, expFloor3Gfa);
  var floor2HasNoDedOk = !f2.ded;                                   // isolation: ded on floor1 must not leak to floor2
  var floorRoleSeparationOk = floor1GfaOk && floor1DedOk && floor2GfaOk && floor3GfaOk && floor2HasNoDedOk;

  /* -------------------------------------------------------------- */
  /* (iv) unfiled root custom-layer object included (M6 semantics)   */
  /* -------------------------------------------------------------- */
  var rootTuple = tuples.filter(function(t) { return t.catId === rootLayer.id; })[0];
  var rootCustomIncludedOk = !!rootTuple && rootTuple.role === 'gfa' && close(rootTuple.area, 100);

  /* -------------------------------------------------------------- */
  /* (v) excluded page skipped                                       */
  /* -------------------------------------------------------------- */
  excluded[P3] = true;
  var tuplesAfterExcl = window.ObjectAgg.objectTuples();
  var noP3TuplesOk = !tuplesAfterExcl.some(function(t) { return t.pg === P3; });
  var afterLenOk = tuplesAfterExcl.length === 7;
  var brAfter = window.ObjectAgg.byRole(tuplesAfterExcl);
  var gfaAfterOk = !!brAfter.gfa && close(brAfter.gfa.area, expTotalGfa - expFloor3Gfa);
  var excludedSkippedOk = noP3TuplesOk && afterLenOk && gfaAfterOk;

  return {
    tupleShapeOk, oracleOk, floorRoleSeparationOk, rootCustomIncludedOk, excludedSkippedOk,
    _tupleCount: tuples.length,
    _oracleDiffs: oracle.diffs,
    _floor1Gfa: f1.gfa ? f1.gfa.area : null, _expFloor1Gfa: expFloor1Gfa,
    _floor2Gfa: f2.gfa ? f2.gfa.area : null, _expFloor2Gfa: expFloor2Gfa,
    _floor3Gfa: f3.gfa ? f3.gfa.area : null, _expFloor3Gfa: expFloor3Gfa,
    _gfaAfterExcl: brAfter.gfa ? brAfter.gfa.area : null,
    pass: tupleShapeOk && oracleOk && floorRoleSeparationOk && rootCustomIncludedOk && excludedSkippedOk
  };
}
"""

CHECKS = [
    ("objectTuplesB0", SC_OBJECT_TUPLES, ["pass"]),
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
        print("LITE-OBJECT-TUPLES checks:")
        for name, scenario, required_keys in CHECKS:
            pg.reload(wait_until="networkidle")
            time.sleep(0.4)

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
        print("LITE_OBJECT_TUPLES_FAIL")
        sys.exit(1)
    else:
        print("LITE_OBJECT_TUPLES_OK")


if __name__ == "__main__":
    main()
