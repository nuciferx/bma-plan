"""
BUG-20260702-lite-cfss-summary regression guard.

Invariant under test: CFSS shared-shape instances participate in every area
rollup with instanceAreaM2 as ground truth (the same value the canvas label
renders via cfssRenderInstanceLabel), bucketed by the master's catId captured
at promote time. Before the fix:

  - masters never captured catId (cfssCommitPromote called addMaster without
    opts) -> instances had no resolvable category;
  - all 6 rollup consumers skipped instances (kind!=="poly" guards) ->
    promoting a poly silently REMOVED its area from every total;
  - buildExportData / exportPdfOverlay CRASHED outright on instances
    (catOf(undefined).name/.color TypeError before the kind guard).

Fixture (scale 1 pt/m, catId 'gfa'): plain poly 50x40 = 2000 m2 + a 10x10
= 100 m2 poly promoted to a CFSS master/instance via the real promote flow
(__cfssTestPromote). Ground truth total = 2100 m2. Pre-fix code: totals =
2000 (source area lost at promote) and both export builders throw ->
discriminates RED/GREEN cleanly.

Emits LITE_SUMMARY_CFSS_OK on success.

    py -3 lite/tests/test_summary_cfss_parity.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8490):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


SETUP_STATE = r"""
var _P = 99;
PS = {};
PS[_P] = {objects:[], scale:{pts_per_m:1}, annotations:[]};
curPage = _P;
window.MASTERS = {};

// plain poly 50x40 = 2000 m2
var plainPoly = {id: state._id++, catId:'gfa', semanticTag:'gross_floor_area',
  kind:'poly', counting:false, dimVisible:true,
  pts:[{x:200,y:0},{x:250,y:0},{x:250,y:40},{x:200,y:40}]};
// promotable poly 10x10 = 100 m2, same catId -> becomes master + instance
var promo = {id: state._id++, catId:'gfa', semanticTag:'gross_floor_area',
  kind:'poly', counting:false, dimVisible:true,
  pts:[{x:0,y:0},{x:10,y:0},{x:10,y:10},{x:0,y:10}]};
PS[_P].objects.push(plainPoly);
PS[_P].objects.push(promo);
"""

SC_CFSS_PARITY = r"""
async () => {
  // cross-floor-shapes.js is dynamically injected — wait for it
  for (var i=0; i<80 && typeof window.__cfssTestPromote!=='function'; i++){
    await new Promise(function(r){ setTimeout(r,50); });
  }
  if (typeof window.__cfssTestPromote!=='function')
    return {pass:false, err:'cfss module not loaded'};
  """ + SETUP_STATE + r"""

  // Real promote flow — the user-visible data-loss moment pre-fix
  var mid = window.__cfssTestPromote(promo, 'Lift', []);
  if (!mid) return {pass:false, err:'promote failed'};
  var master = masterById(mid);
  var master_has_catId = !!(master && master.catId === 'gfa');   // proves FIX A

  var inst = PS[_P].objects.filter(function(o){return o.kind==='instance';})[0];
  if (!inst) return {pass:false, err:'no instance after promote'};

  // Ground truth: instanceAreaM2 (same source as the canvas label path);
  // areaOf stays null for instances by design.
  var instTruth = instanceAreaM2(inst);                          // 100
  var areaOfInst = areaOf(inst);                                 // null by design
  var plainTruth = areaOf(plainPoly);                            // 2000
  var GT = plainTruth + instTruth;                               // 2100

  // Site 1: computeSummary
  var s = computeSummary();
  var summaryTotal = s.all['gfa'] || 0;
  var summaryOk = Math.abs(summaryTotal - GT) < 1e-6 * GT;

  // Site 2: buildExportData — must not throw, totals include instance
  var edThrew=false, ed=null;
  try { ed = buildExportData(); } catch(e) { edThrew = true; }
  var edSum = ed && ed.summary.filter(function(r){return typeof r.total==='number';})[0];
  var edRowInst = ed && ed.rows.filter(function(r){
    return r.kind==='area' && r.area!=null && Math.abs(r.area-100)<0.01; })[0];
  var edOk = !edThrew && !!edSum && Math.abs(edSum.total - GT) < 0.01 && !!edRowInst;

  // Site 3: exportPdfOverlay — must not throw; instance emitted with resolved
  // pts + area label (stub dlPost, no network)
  var ovThrew=false, cap=null, _odl=dlPost, _oc=caseId;
  dlPost = function(u,p,f){ cap = p; };
  caseId = caseId || 'tst-cfss';
  try { exportPdfOverlay(); } catch(e) { ovThrew = true; }
  finally { dlPost = _odl; caseId = _oc; }
  var ovObjs = cap && cap.pages && cap.pages[_P] && cap.pages[_P].objects;
  var ovInst = ovObjs && ovObjs.filter(function(o){
    return o.label && o.label.indexOf('100.00 m2') >= 0 && o.pts && o.pts.length === 4; })[0];
  var ovOk = !ovThrew && !!ovObjs && ovObjs.length === 2 && !!ovInst;

  // Site 4: buildReportPayload — net includes instance
  var rpThrew=false, rp=null;
  try { rp = buildReportPayload(); } catch(e) { rpThrew = true; }
  var rpPage = rp && rp.pages.filter(function(p){return p.idx===_P;})[0];
  var reportOk = !rpThrew && !!rpPage && Math.abs(rpPage.net - GT) < 0.05;

  // Site 6: _lovsLayerArea
  var lovsArea = (typeof _lovsLayerArea==='function') ? _lovsLayerArea('gfa') : null;
  var lovsOk = lovsArea != null && Math.abs(lovsArea - GT) < 1e-6 * GT;

  // Site 5: _ltOwnArea (assert only if the 'gfa' layer is registered)
  var ltSkipped=true, ltOk=true, ltArea=null;
  if (typeof _ltOwnArea==='function' && typeof layerById==='function' && layerById('gfa')) {
    ltSkipped=false; ltArea=_ltOwnArea('gfa');
    ltOk = Math.abs(Math.abs(ltArea) - GT) < 1e-6 * GT;
  }

  return {
    master_has_catId, instTruth, areaOfInst, plainTruth, GT,
    summaryTotal, edThrew, ovThrew, rpThrew,
    edSumTotal: edSum ? edSum.total : null,
    reportNet: rpPage ? rpPage.net : null,
    lovsArea, ltArea, ltSkipped,
    summaryOk, edOk, ovOk, reportOk, lovsOk, ltOk,
    pass: master_has_catId && instTruth === 100 && areaOfInst === null &&
          summaryOk && edOk && ovOk && reportOk && lovsOk && ltOk
  };
}
"""


CHECKS = [
    ("cfssInstanceRollupParity", SC_CFSS_PARITY, ["pass"]),
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
        print("LITE-SUMMARY-CFSS-PARITY checks:")
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
        print("LITE_SUMMARY_CFSS_FAIL")
        sys.exit(1)
    else:
        print("LITE_SUMMARY_CFSS_OK")


if __name__ == "__main__":
    main()
