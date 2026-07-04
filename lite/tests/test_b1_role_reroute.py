"""
INV-20260703-layer-linkage -- approach B, slice B1 acceptance test.

Verifies the B1 reroute: report-vars.js computeReportVars(agg,{useLive:true})
and ui-lite.html openSum()'s new per-floor block now source role totals from
ObjectAgg.byRole()/byFloorRole() (tuple semantics, excludes excluded[] pages)
instead of the legacy computeSummary()-derived agg (which does not skip
excluded pages -- a pre-existing gap documented in object-agg.js's B0/B1
header, resolved for these consumers only in this slice).

Fixture: scale 1 pt/m.
  P1 (floor 1): gfa1 (1200 m2), ded1 (25 m2)
  P2 (floor 2): gfa2 (300 m2), ded2 (40 m2)
  P3 (site):    siteA (5000 m2), openA (1200 m2)
  P4 (floor 3): gfa4 (49 m2)  -- excluded[P4]=true is set AFTER the
                convergence check, to test the exclusion behavior in
                isolation (mirrors test_object_tuples.py's B0 pattern)
  P5 (untagged): a poly on an UNFILED custom layer (role=gfa, 80 m2) --
                tests that a report var referencing that SPECIFIC layer id
                still resolves after the reroute (byRole only groups by
                role, not catId, so layer-id refs must still come from the
                agg param, per the "merge: role keys from byRole, layer
                keys from the passed agg" contract)

Checks:
  convergenceOk       on the no-excluded fixture, computeReportVars(agg,
                      {useLive:true}) v_net/v_far/v_osr == computeReportVars
                      (agg) (legacy, no useLive) -- tuple engine and legacy
                      engine agree when nothing is excluded.
  convergenceValuesOk  those converged values also match independently
                      hand-computed expectations (not just each other).
  excludedOutOk        after excluded[P4]=true and a FRESH computeSummary()
                      -based agg rebuild (mirrors openSum() re-opening the
                      panel): BOTH legacy and live (useLive:true) v_net now
                      drop by exactly gfa4's area (49 m2). Updated for A-4
                      (REVIEW_LITE_LAYER_REPORT_20260704.md ledger A-4):
                      computeSummary() itself was rerouted onto the tuple
                      stream and now skips excluded[] pages too, closing the
                      B0/B1-documented asymmetry this check used to pin
                      (legacy used to stay UNCHANGED on exclusion -- that
                      pre-existing gap is exactly what A-4 fixed).
  perFloorRowsOk       floorReportRows() (post-exclusion) gives floor1.net
                      == gfa1-ded1, floor2.net == gfa2-ded2 (independent
                      per-floor deduction, not a single global pool -- the
                      audit's complaint, solved at display level), and no
                      floor:3 row (its only page is excluded).
  layerRefOk            a report var referencing the unfiled custom layer's
                      id DIRECTLY (not its role) still resolves to its own
                      area after the reroute.

Emits LITE_B1_ROLE_REROUTE_OK on success.

    py -3 lite/tests/test_b1_role_reroute.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8560):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


SETUP_STATE = r"""
var P1=1, P2=2, P3=3, P4=4, P5=5;
PS = {}; excluded = {};
pageTags = {}; pageFloorKind = {}; pageFloorNum = {};

pageTags[P1]='floor'; pageFloorKind[P1]='normal'; pageFloorNum[P1]=1;
pageTags[P2]='floor'; pageFloorKind[P2]='normal'; pageFloorNum[P2]=2;
pageTags[P3]='site';
pageTags[P4]='floor'; pageFloorKind[P4]='normal'; pageFloorNum[P4]=3;
// P5 intentionally untagged -- floorKeyOfPage(P5) === ""

PS[P1]={objects:[], scale:{pts_per_m:1}, annotations:[]};
PS[P2]={objects:[], scale:{pts_per_m:1}, annotations:[]};
PS[P3]={objects:[], scale:{pts_per_m:1}, annotations:[]};
PS[P4]={objects:[], scale:{pts_per_m:1}, annotations:[]};
PS[P5]={objects:[], scale:{pts_per_m:1}, annotations:[]};
curPage=P1;

var customLayer = addLayer('gfa', 'Custom Unfiled', '#8844ff');

var gfa1={id:state._id++, catId:'gfa', semanticTag:'gross_floor_area', kind:'poly',
  counting:false, dimVisible:true, pts:[{x:0,y:0},{x:40,y:0},{x:40,y:30},{x:0,y:30}]};      // 1200 m2
var ded1={id:state._id++, catId:'ded', semanticTag:'deduction_opening', kind:'poly',
  counting:false, dimVisible:true, pts:[{x:100,y:0},{x:105,y:0},{x:105,y:5},{x:100,y:5}]};  // 25 m2
PS[P1].objects.push(gfa1, ded1);

var gfa2={id:state._id++, catId:'gfa', semanticTag:'gross_floor_area', kind:'poly',
  counting:false, dimVisible:true, pts:[{x:0,y:0},{x:20,y:0},{x:20,y:15},{x:0,y:15}]};      // 300 m2
var ded2={id:state._id++, catId:'ded', semanticTag:'deduction_opening', kind:'poly',
  counting:false, dimVisible:true, pts:[{x:0,y:0},{x:8,y:0},{x:8,y:5},{x:0,y:5}]};          // 40 m2
PS[P2].objects.push(gfa2, ded2);

var siteA={id:state._id++, catId:'site', semanticTag:'site_land_area', kind:'poly',
  counting:false, dimVisible:true, pts:[{x:0,y:0},{x:100,y:0},{x:100,y:50},{x:0,y:50}]};    // 5000 m2
var openA={id:state._id++, catId:'open', semanticTag:'legal_open_space', kind:'poly',
  counting:false, dimVisible:true, pts:[{x:0,y:0},{x:40,y:0},{x:40,y:30},{x:0,y:30}]};      // 1200 m2
PS[P3].objects.push(siteA, openA);

var gfa4={id:state._id++, catId:'gfa', semanticTag:'gross_floor_area', kind:'poly',
  counting:false, dimVisible:true, pts:[{x:0,y:0},{x:7,y:0},{x:7,y:7},{x:0,y:7}]};          // 49 m2
PS[P4].objects.push(gfa4);

var custom5={id:state._id++, catId:customLayer.id, semanticTag:'gross_floor_area', kind:'poly',
  counting:false, dimVisible:true, pts:[{x:0,y:0},{x:10,y:0},{x:10,y:8},{x:0,y:8}]};        // 80 m2, unfiled custom layer
PS[P5].objects.push(custom5);
"""

SC_B1 = r"""
() => {
  if (typeof window.ObjectAgg !== 'object') return {pass: false, err: 'ObjectAgg not loaded'};
  if (typeof computeReportVars !== 'function') return {pass: false, err: 'computeReportVars not loaded'};

  """ + SETUP_STATE + r"""

  function close(a, b, tol) { tol = tol == null ? 1e-6 * Math.max(1, Math.abs(b)) : tol; return Math.abs(a - b) < tol; }
  function find(arr, id) { return arr.filter(function(r) { return r.id === id; })[0]; }
  function buildAgg() {
    var s = computeSummary(); var agg = {};
    Object.keys(s.all).forEach(function(k) { agg[k] = s.all[k]; });
    Object.keys(s.allCnt).forEach(function(k) { agg[k] = s.allCnt[k]; });
    return agg;
  }

  REPORT_VARS.length = 0;
  seedReportVars();

  /* -------------------------------------------------------------- */
  /* (i) convergence -- no excluded pages yet                        */
  /* -------------------------------------------------------------- */
  var agg0 = buildAgg();
  var legacy0 = computeReportVars(agg0);
  var live0 = computeReportVars(agg0, {useLive: true});
  var l0net = find(legacy0, 'v_net'), v0net = find(live0, 'v_net');
  var l0far = find(legacy0, 'v_far'), v0far = find(live0, 'v_far');
  var l0osr = find(legacy0, 'v_osr'), v0osr = find(live0, 'v_osr');
  var convergenceOk = !!(
    l0net && v0net && l0net.err === null && v0net.err === null && close(l0net.value, v0net.value) &&
    l0far && v0far && l0far.err === null && v0far.err === null && close(l0far.value, v0far.value) &&
    l0osr && v0osr && l0osr.err === null && v0osr.err === null && close(l0osr.value, v0osr.value)
  );

  var expGfaTotal = 1200 + 300 + 49 + 80, expDedTotal = 25 + 40, expSite = 5000, expOpen = 1200;
  var expNetBefore = expGfaTotal - expDedTotal;
  var convergenceValuesOk = !!(v0net && v0far && v0osr &&
    close(v0net.value, expNetBefore) &&
    close(v0far.value, expGfaTotal / expSite) &&
    close(v0osr.value, expOpen / expSite * 100));

  /* -------------------------------------------------------------- */
  /* (ii) excluded page -- P4 dropped from live, legacy unaffected   */
  /* -------------------------------------------------------------- */
  excluded[P4] = true;
  var agg1 = buildAgg();                              // fresh rebuild, mirrors openSum() re-opening the panel
  var legacy1 = computeReportVars(agg1);
  var live1 = computeReportVars(agg1, {useLive: true});
  var l1net = find(legacy1, 'v_net'), v1net = find(live1, 'v_net');
  // A-4 (REVIEW_LITE_LAYER_REPORT_20260704 ledger A-4): computeSummary() now
  // also sources from the tuple stream (summaryByCategory), so legacy agg
  // built via buildAgg()/computeSummary() drops P4 too -- both engines agree.
  var legacyDroppedOk = !!l1net && l1net.err === null && close(l1net.value, expNetBefore - 49);
  var liveDroppedOk = !!v1net && v1net.err === null && close(v1net.value, expNetBefore - 49);  // live excludes P4's 49 m2
  var excludedOutOk = legacyDroppedOk && liveDroppedOk;

  /* -------------------------------------------------------------- */
  /* (iii) per-floor rows (post-exclusion)                           */
  /* -------------------------------------------------------------- */
  var frows = window.ObjectAgg.floorReportRows();
  var f1 = frows.filter(function(r) { return r.floorKey === 'floor:1'; })[0];
  var f2 = frows.filter(function(r) { return r.floorKey === 'floor:2'; })[0];
  var f3 = frows.filter(function(r) { return r.floorKey === 'floor:3'; })[0];
  var perFloorRowsOk = !!(f1 && f2 && !f3 &&
    close(f1.gfa, 1200) && close(f1.ded, 25) && close(f1.net, 1200 - 25) &&
    close(f2.gfa, 300) && close(f2.ded, 40) && close(f2.net, 300 - 40));

  /* -------------------------------------------------------------- */
  /* (iv) layer-id ref (not role) still resolves                     */
  /* -------------------------------------------------------------- */
  REPORT_VARS.push({id: 'v_custom', name: 'custom', unit: 'm2', expr: [{ref: customLayer.id}]});
  var live2 = computeReportVars(agg1, {useLive: true});
  var vc = find(live2, 'v_custom');
  var layerRefOk = !!vc && vc.err === null && close(vc.value, 80);

  return {
    convergenceOk, convergenceValuesOk, excludedOutOk, perFloorRowsOk, layerRefOk,
    _l0net: l0net && l0net.value, _v0net: v0net && v0net.value,
    _l1net: l1net && l1net.value, _v1net: v1net && v1net.value,
    _f1: f1, _f2: f2, _f3: f3, _vcVal: vc && vc.value, _vcErr: vc && vc.err,
    pass: convergenceOk && convergenceValuesOk && excludedOutOk && perFloorRowsOk && layerRefOk
  };
}
"""

CHECKS = [
    ("b1RoleReroute", SC_B1, ["pass"]),
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
        print("LITE-B1-ROLE-REROUTE checks:")
        for name, scenario, required_keys in CHECKS:
            try:
                result = pg.evaluate(scenario)
            except Exception as ex:
                print(f"  {name:25s} -> EXCEPTION: {ex}")
                failures.append(f"check '{name}' threw: {ex}")
                continue
            ok = all(result.get(k) is True for k in required_keys)
            status = "PASS" if ok else "FAIL"
            print(f"  {name:25s} -> {status}  {result}")
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
        print("LITE_B1_ROLE_REROUTE_FAIL")
        sys.exit(1)
    else:
        print("LITE_B1_ROLE_REROUTE_OK")


if __name__ == "__main__":
    main()
