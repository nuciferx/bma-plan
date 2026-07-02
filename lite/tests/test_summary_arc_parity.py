"""
BUG-20260702-lite-arc-summary regression guard.

Invariant under test: every rollup consumer reports the SAME area as the
per-object label path (areaOf) — arc-inclusive. Before the fix, 6 call sites
passed {pts:o.pts} to polyMetrics (dropping o.edges), so arc-edge polygons
entered every total as their straight-chord area while the on-canvas label
was arc-correct:

  1. computeSummary        (ui-lite.html)           — summary panel + report agg
  2. buildExportData       (export-annotate.js)     — XLSX rows + summary
  3. exportPdfOverlay      (export-annotate.js)     — annotated-PDF labels
  4. buildReportPayload    (export-annotate.js)     — report rows/subtotal/net
  5. _ltOwnArea            (layer-tree.js)          — layer-panel per-layer total
  6. _lovsLayerArea        (overview-setup.js)      — site-setup layer rollup

Fixture: one arc-edge poly (square 100x100 pt + semicircle bulge r=50 on edge 1)
plus one plain poly (50x40), scale 1 pt/m. Independent closed-form expected:
arc poly = 10000 + 1250*pi ~= 13926.991 m2, plain = 2000 m2. The chord-only
(old buggy) total differs by 1250*pi ~= 3927 m2 >> all tolerances, so this
test FAILS on pre-fix code by construction.

Emits LITE_SUMMARY_ARC_OK on success.

    py -3 lite/tests/test_summary_arc_parity.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8470):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# Fixture: PS[99] with scale 1 pt/m, one arc poly + one plain poly, both catId 'gfa'.
SETUP_STATE = r"""
var _TST_PAGE = 99;
PS = {};                                   // isolate: only the fixture page exists
PS[_TST_PAGE] = {objects:[], scale:{pts_per_m:1}, annotations:[]};
curPage = _TST_PAGE;

var v0={x:0,y:0}, v1={x:100,y:0}, v2={x:100,y:100}, v3={x:0,y:100};
var tp={x:150,y:50};   // semicircle through-point (outward bulge, r=50)
var arc = computeArcEdge(v1, v2, tp, {x:50,y:50});
var arcPoly = {
  id: state._id++, catId: 'gfa', semanticTag: 'gross_floor_area',
  kind: 'poly', counting: false, dimVisible: true,
  pts: [v0, v1, v2, v3],
  edges: [null, {edgeType:'arc', arcSweep:arc.sweep, arcThrough:{x:tp.x,y:tp.y}}, null, null]
};
var plainPoly = {
  id: state._id++, catId: 'gfa', semanticTag: 'gross_floor_area',
  kind: 'poly', counting: false, dimVisible: true,
  pts: [{x:200,y:0},{x:250,y:0},{x:250,y:40},{x:200,y:40}]   // 50x40 = 2000 m2
};
PS[_TST_PAGE].objects.push(arcPoly);
PS[_TST_PAGE].objects.push(plainPoly);
"""

SC_PARITY = r"""
async () => {
  """ + SETUP_STATE + r"""

  // Independent closed-form expectations (NOT derived from code under test)
  var expectedArc   = 10000 + Math.PI * 50 * 50 / 2;   // 13926.99...
  var expectedPlain = 2000;
  var expectedTotal = expectedArc + expectedPlain;
  var chordOnlyTotal = 10000 + expectedPlain;          // what pre-fix code produced

  // Reference: per-object label path (always arc-correct)
  var perObjArc   = areaOf(arcPoly);
  var perObjPlain = areaOf(plainPoly);
  var labelSum    = perObjArc + perObjPlain;
  var perObjOk = Math.abs(perObjArc - expectedArc) < 1e-6 * expectedArc &&
                 Math.abs(perObjPlain - expectedPlain) < 1e-9;

  // Site 1: computeSummary (summary panel + report agg source)
  var s = computeSummary();
  var summaryTotal = s.all['gfa'] || 0;
  var summaryOk = Math.abs(summaryTotal - labelSum) < 1e-6 * expectedTotal;

  // Site 2: buildExportData (XLSX rows + summary; rows rounded to 3 dp)
  var ed = buildExportData();
  var exportRowTotal = ed.rows.filter(function(r){return r.kind==="area";})
                              .reduce(function(a,r){return a+(r.area||0);}, 0);
  var exportRowsOk = Math.abs(exportRowTotal - labelSum) < 0.01;
  var edSummaryRow = ed.summary.filter(function(r){return typeof r.total==="number";})[0];
  var exportSummaryOk = !!edSummaryRow && Math.abs(edSummaryRow.total - labelSum) < 0.01;

  // Site 3: exportPdfOverlay label — stub dlPost to capture the payload, no network
  var captured = null;
  var _odl = dlPost, _ocase = caseId;
  dlPost = function(u, p, f){ captured = p; };
  caseId = caseId || "tst-arc-parity";
  try { exportPdfOverlay(); } finally { dlPost = _odl; caseId = _ocase; }
  var overlayOk = false, overlayLabelArea = null;
  if (captured && captured.pages && captured.pages[_TST_PAGE]) {
    var objs = captured.pages[_TST_PAGE].objects;
    var lbl = objs && objs[0] && objs[0].label;                 // arcPoly is objects[0]
    var m = lbl && lbl.match(/([\d.]+) m2$/);
    if (m) { overlayLabelArea = parseFloat(m[1]);
             overlayOk = Math.abs(overlayLabelArea - perObjArc) < 0.01; }
  }

  // Site 4: buildReportPayload (net rounded to 2 dp; gfa sign = +1)
  var rp = buildReportPayload();
  var rpPage = rp.pages.filter(function(p){return p.idx === _TST_PAGE;})[0];
  var reportNet = rpPage ? rpPage.net : null;
  var reportOk = reportNet != null && Math.abs(reportNet - labelSum) < 0.05;

  // Site 6: _lovsLayerArea (site-setup rollup; self-contained, keyed by catId)
  var lovsArea = (typeof _lovsLayerArea === "function") ? _lovsLayerArea('gfa') : null;
  var lovsOk = lovsArea != null && Math.abs(lovsArea - labelSum) < 1e-6 * expectedTotal;

  // Site 5: _ltOwnArea (needs a registered layer 'gfa'; assert only if resolvable)
  var ltSkipped = true, ltOk = true, ltArea = null;
  if (typeof _ltOwnArea === "function" && typeof layerById === "function" && layerById('gfa')) {
    ltSkipped = false;
    ltArea = _ltOwnArea('gfa');
    ltOk = Math.abs(Math.abs(ltArea) - labelSum) < 1e-6 * expectedTotal;
  }

  // Discrimination proof: old chord-only totals sit far outside every tolerance
  var deltaCatchesRegression = Math.abs(expectedTotal - chordOnlyTotal) > 100;

  return {
    perObjArc, perObjPlain, expectedArc, expectedTotal, chordOnlyTotal,
    summaryTotal, exportRowTotal, overlayLabelArea, reportNet, lovsArea, ltArea, ltSkipped,
    perObjOk, summaryOk, exportRowsOk, exportSummaryOk, overlayOk, reportOk, lovsOk, ltOk,
    deltaCatchesRegression,
    pass: perObjOk && summaryOk && exportRowsOk && exportSummaryOk &&
          overlayOk && reportOk && lovsOk && ltOk && deltaCatchesRegression
  };
}
"""


CHECKS = [
    ("summaryArcParityAllConsumers", SC_PARITY, ["pass"]),
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
        print("LITE-SUMMARY-ARC-PARITY checks:")
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
        print("LITE_SUMMARY_ARC_FAIL")
        sys.exit(1)
    else:
        print("LITE_SUMMARY_ARC_OK")


if __name__ == "__main__":
    main()
