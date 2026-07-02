"""
Verify-Scale port regression guard (proto INV-2026-05-20-001 -> lite,
lite/static/js/verify-scale.js).

Calibration is a single-sample measurement (~1-2% scale error -> ~2-4%
area error, silently undetected). Verify Scale lets the user cross-check
against a SECOND known dimension. This test checks:

  (a) %dev math + green/yellow/red band boundaries are exact
      (green <0.5%, yellow <2%, red >=2%)
  (b) action 'average' produces the mean of the two pts_per_m samples,
      and areas recompute by the expected factor (raw-geometry contract:
      polyAreaM2 re-derives from the CURRENT scale every call)
  (c) verifyResult persists through the real save/load path
      (buildPageStore() -> loadProto())
  (d) action 'accept' leaves pts_per_m untouched
  (e) menu item + window.verifyScaleStart wiring present

Emits LITE_VERIFY_SCALE_OK on success.

    py -3 lite/tests/test_verify_scale.py
"""
import socket, threading, time, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8500):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ---------------------------------------------------------------------------
# Check 1 — bandBoundaryMathExact
# band() thresholds: green <0.5%, yellow <2%, red >=2%. Test exact boundaries
# plus the computeDeviation() formula against hand-computed values.
# ---------------------------------------------------------------------------
SC1_BAND = r"""
() => {
  if (typeof VerifyScale === 'undefined') return {pass:false, err:'VerifyScale module not loaded'};
  var b = VerifyScale.band;
  var boundaryOk =
    b(0.49) === 'green' && b(0.4999999) === 'green' &&
    b(0.5) === 'yellow' && b(0.5001) === 'yellow' &&
    b(1.9999) === 'yellow' &&
    b(2) === 'red' && b(2.0001) === 'red' && b(50) === 'red';

  // scale 1 pt/m, ptDist=1pt (=1m at current scale), entered 1.02m -> ~1.9608% (yellow, <2)
  var dev1 = VerifyScale.computeDeviation(1, 1, 1.02);
  var dev1Ok = Math.abs(dev1.pct - 1.9607843137254901) < 1e-9 && dev1.band === 'yellow';

  // exact 2% deviation: ptDist=1, ppm=1 (measM=1), enterM such that pct===2 exactly
  // pct = 100*|1-enterM|/enterM = 2  =>  enterM = 1/1.02 (measM undershoots enterM)
  var enterM2 = 1/1.02;
  var dev2 = VerifyScale.computeDeviation(1, 1, enterM2);
  var dev2Ok = Math.abs(dev2.pct - 2) < 1e-9 && dev2.band === 'red';

  return {boundaryOk, dev1pct: dev1.pct, dev1Ok, dev2pct: dev2.pct, dev2Ok,
          pass: boundaryOk && dev1Ok && dev2Ok};
}
"""

# ---------------------------------------------------------------------------
# Check 2 — averageProducesMeanAndAreaScales
# scale pts_per_m=10; verify measurement implies vPpm=20 (2x). average -> 15.
# A poly drawn under ppm=10 with raw pt extents 100x100 -> area=100 m2.
# After average (ppm 10->15), area must re-derive to 100*(10/15)^2 m2
# (raw-geometry contract: polyAreaM2 divides by ppm^2 fresh every call).
# ---------------------------------------------------------------------------
SC2_AVERAGE = r"""
() => {
  if (typeof VerifyScale === 'undefined') return {pass:false, err:'VerifyScale module not loaded'};
  var _P = 77;
  PS = {}; PS[_P] = {objects:[], scale:{pts_per_m:10}, annotations:[]};
  curPage = _P;
  var poly = {id: state._id++, catId:'gfa', semanticTag:'gross_floor_area', kind:'poly',
    counting:false, dimVisible:true, pts:[{x:0,y:0},{x:100,y:0},{x:100,y:100},{x:0,y:100}]};
  PS[_P].objects.push(poly);
  var areaBefore = polyAreaM2(poly.pts);        // 100 m2 at ppm=10

  // simulate a 2nd-reference measurement: ptDist=200pt, entered=10m -> vPpm=20
  var ctx = VerifyScale.__test.computeCtx(_P, 200, 10);
  var ppmBefore = PS[_P].scale.pts_per_m;
  VerifyScale.average();
  var ppmAfter = PS[_P].scale.pts_per_m;
  var expectedAvg = (10 + 20) / 2;              // 15
  var ppmOk = Math.abs(ppmAfter - expectedAvg) < 1e-9;

  var areaAfter = polyAreaM2(poly.pts);         // re-derived fresh from new ppm
  var expectedAreaAfter = 100 * Math.pow(10/15, 2);
  var areaOk = Math.abs(areaAfter - expectedAreaAfter) < 1e-6;

  var vr = PS[_P].scale.verifyResult;
  var vrOk = !!vr && vr.action === 'average' && Math.abs(vr.verifyPts_per_m - 20) < 1e-6;

  return {ppmBefore, ppmAfter, expectedAvg, ppmOk, areaBefore, areaAfter, expectedAreaAfter, areaOk,
          vr, vrOk, pass: ppmOk && areaOk && vrOk};
}
"""

# ---------------------------------------------------------------------------
# Check 3 — verifyResultPersistsThroughSaveLoad
# buildPageStore() -> loadProto() round trip must carry verifyResult
# additively (never lose/rename pts_per_m or verifyResult fields).
# ---------------------------------------------------------------------------
SC3_PERSIST = r"""
() => {
  if (typeof VerifyScale === 'undefined') return {pass:false, err:'VerifyScale module not loaded'};
  var _P = 78;
  PS = {}; excluded = {};  // pageCount stays 0 (falsy) so loadProto skips _pmSeed/PageModel machinery — out of scope here
  PS[_P] = {objects:[], scale:{pts_per_m:12}, annotations:[]};
  curPage = _P;
  var ctx = VerifyScale.__test.computeCtx(_P, 240, 18);   // vPpm ~13.33
  VerifyScale.accept();  // accept = record only, pts_per_m untouched
  var vrBefore = PS[_P].scale.verifyResult;

  var ps = buildPageStore();
  var calibScale = ps[_P] && ps[_P].calibScale;
  var carriedInStore = !!calibScale && !!calibScale.verifyResult &&
    calibScale.verifyResult.action === 'accept';

  // round-trip through loadProto with a minimal doc
  var doc = {version:1, pdfName:'x.pdf', pageStore: ps, pageTags:{}, pageRotations:{},
    pageNames:{}, pageFloorKind:{}, pageFloorNum:{}, excludedPages:[]};
  loadProto(doc);
  var vrAfter = PS[_P] && PS[_P].scale && PS[_P].scale.verifyResult;
  var ppmAfter = PS[_P] && PS[_P].scale && PS[_P].scale.pts_per_m;

  var roundTripOk = !!vrAfter && vrAfter.action === 'accept' &&
    Math.abs(vrAfter.pct - vrBefore.pct) < 1e-9 &&
    Math.abs(vrAfter.verifyPts_per_m - vrBefore.verifyPts_per_m) < 1e-9 &&
    Math.abs(ppmAfter - 12) < 1e-9;   // pts_per_m itself untouched by accept, and survives round trip

  return {vrBefore, carriedInStore, vrAfter, ppmAfter, roundTripOk,
          pass: carriedInStore && roundTripOk};
}
"""

# ---------------------------------------------------------------------------
# Check 4 — acceptLeavesPtsPerMUntouched
# ---------------------------------------------------------------------------
SC4_ACCEPT = r"""
() => {
  if (typeof VerifyScale === 'undefined') return {pass:false, err:'VerifyScale module not loaded'};
  var _P = 79;
  PS = {}; PS[_P] = {objects:[], scale:{pts_per_m:7.5}, annotations:[]};
  curPage = _P;
  var ppmBefore = PS[_P].scale.pts_per_m;
  var ctx = VerifyScale.__test.computeCtx(_P, 90, 11);  // some deviation, doesn't matter
  VerifyScale.accept();
  var ppmAfter = PS[_P].scale.pts_per_m;
  var vr = PS[_P].scale.verifyResult;
  var untouchedOk = ppmBefore === ppmAfter;
  var vrOk = !!vr && vr.action === 'accept';
  return {ppmBefore, ppmAfter, untouchedOk, vr, vrOk, pass: untouchedOk && vrOk};
}
"""

# ---------------------------------------------------------------------------
# Check 5 — recalibrateReplacesPpmAndZerosDeviation
# ---------------------------------------------------------------------------
SC5_RECAL = r"""
() => {
  if (typeof VerifyScale === 'undefined') return {pass:false, err:'VerifyScale module not loaded'};
  var _P = 80;
  PS = {}; PS[_P] = {objects:[], scale:{pts_per_m:5}, annotations:[]};
  curPage = _P;
  var ctx = VerifyScale.__test.computeCtx(_P, 100, 25);  // vPpm = 4
  VerifyScale.recalibrate();
  var ppmAfter = PS[_P].scale.pts_per_m;
  var vr = PS[_P].scale.verifyResult;
  var ppmOk = Math.abs(ppmAfter - 4) < 1e-9;
  var vrOk = !!vr && vr.action === 'recalibrate' && vr.pct === 0;
  return {ppmAfter, vr, ppmOk, vrOk, pass: ppmOk && vrOk};
}
"""

# ---------------------------------------------------------------------------
# Check 6 — menuItemAndHandlersWired (UI wiring presence, not full click drive)
# ---------------------------------------------------------------------------
SC6_WIRING = r"""
() => {
  var mi = document.getElementById('mi-verify-scale');
  var startFn = typeof window.verifyScaleStart === 'function';
  var moduleFns = typeof VerifyScale === 'object' &&
    typeof VerifyScale.onTwoPoints === 'function' &&
    typeof VerifyScale.accept === 'function' &&
    typeof VerifyScale.recalibrate === 'function' &&
    typeof VerifyScale.average === 'function';
  var miFound = !!mi;
  var miInMeasureMenu = !!mi && !!mi.closest('.menu[data-m="measure"]');
  return {miFound, miInMeasureMenu, startFn, moduleFns,
          pass: miFound && miInMeasureMenu && startFn && moduleFns};
}
"""

# ---------------------------------------------------------------------------
# Check 7 — startGuardsMissingScale (no scale on page -> alert, no crash)
# ---------------------------------------------------------------------------
SC7_GUARD = r"""
() => {
  var _P = 81;
  caseId = 'test-case';  // bypass the "open a PDF first" guard so this exercises the scale-missing guard specifically
  PS = {}; PS[_P] = {objects:[], scale:null, annotations:[]};
  curPage = _P;
  var alertMsg = null, _oa = window.alert;
  window.alert = function(msg){ alertMsg = msg; };
  var threw = false;
  try { VerifyScale.start(); } catch(e) { threw = true; }
  window.alert = _oa;
  caseId = null;
  var alerted = alertMsg != null;
  var verifyModeNotSet = state.verifyMode !== true;
  return {alertMsg, alerted, threw, verifyModeNotSet, pass: alerted && !threw && verifyModeNotSet};
}
"""


CHECKS = [
    ("bandBoundaryMathExact",             SC1_BAND,   ["pass"]),
    ("averageProducesMeanAndAreaScales",  SC2_AVERAGE, ["pass"]),
    ("verifyResultPersistsThroughSaveLoad", SC3_PERSIST, ["pass"]),
    ("acceptLeavesPtsPerMUntouched",      SC4_ACCEPT, ["pass"]),
    ("recalibrateReplacesPpmAndZerosDeviation", SC5_RECAL, ["pass"]),
    ("menuItemAndHandlersWired",          SC6_WIRING, ["pass"]),
    ("startGuardsMissingScale",           SC7_GUARD,  ["pass"]),
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
        print("VERIFY-SCALE checks:")
        for name, scenario, required_keys in CHECKS:
            pg.reload(wait_until="networkidle")
            time.sleep(0.4)

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
        print("LITE_VERIFY_SCALE_FAIL")
        sys.exit(1)
    else:
        print("LITE_VERIFY_SCALE_OK")


if __name__ == "__main__":
    main()
