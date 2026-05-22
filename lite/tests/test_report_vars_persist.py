"""
LITE-REPORT-VARS-PERSIST regression guard (LRV-S4 sprint).

Verifies that REPORT_VARS survive a .bmaplan save/load round-trip and that
the schema change is additive (old files without reportVars get fresh defaults).

Checks:
  saveIncludesVars    addReportVar('myKPI') + set expr, build save doc via real
                      fns → doc.reportVars includes 'myKPI' entry with expr
                      preserved AND 3 presets → length >= 4.
  loadRestoresVars    load a crafted doc with reportVars → REPORT_VARS restored;
                      computeReportVars for the single var ≈ 20.
  oldFileSeedsDefaults  load doc WITHOUT reportVars key → REPORT_VARS == 3 presets
                      (v_net, v_osr, v_far).
  roundTrip           serialize → JSON → parse → loadReportVars → serialize again;
                      assert deep-equal (no field loss).

Emits LITE_REPORT_VARS_PERSIST_OK on success.

    py -3 lite/tests/test_report_vars_persist.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8360):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# --------------------------------------------------------------------------
# All checks run in a single page.evaluate() call for speed.
# loadProto() mutates REPORT_VARS; each check resets REPORT_VARS via
# reseedRV() before proceeding.
# --------------------------------------------------------------------------
SCENARIO = r"""
() => {
  const out = {};

  /* Helper: reset REPORT_VARS to the 3 presets */
  function reseedRV() {
    REPORT_VARS.length = 0;
    seedReportVars();
  }

  /* Helper: minimal valid doc skeleton (no reportVars) */
  function minimalDoc(extra) {
    var base = {version:1, app:"bma-plan-lite", pdfName:"test.pdf",
      totalPages:1, pageStore:{}, pageRotations:{}, pageTags:{}, pageNames:{},
      projectInfo:{}, siteOrientation:{}, excludedPages:[], pageFloorKind:{},
      pageFloorNum:{}};
    return Object.assign(base, extra || {});
  }

  // -----------------------------------------------------------------------
  // saveIncludesVars
  //   1. start from 3 presets
  //   2. addReportVar('myKPI') → set expr to [{ref:'gfa'},{op:'*',lit:2}]
  //   3. build save doc using real layersInOrder + serializeReportVars
  //   4. assert doc.reportVars is array, length >= 4
  //      includes entry name==='myKPI' with expr[1].lit===2
  //      AND still has the 3 presets (v_net / v_osr / v_far)
  // -----------------------------------------------------------------------
  reseedRV();
  const kpi = addReportVar('myKPI');
  kpi.expr = [{ref:'gfa'}, {op:'*', lit:2}];

  const liteLayersArr = layersInOrder().map(function(l) {
    return {id:l.id, name:l.name, color:l.color, role:l.role, order:l.order,
            parentId:(l.parentId!==undefined?l.parentId:null)};
  });
  const liteGroupsArr = (typeof foldersInOrder==='function') ? foldersInOrder().map(function(f) {
    return {id:f.id, name:f.name, color:f.color, parentId:(f.parentId!==undefined?f.parentId:null), order:f.order};
  }) : [];

  const saveDoc = {version:1, app:"bma-plan-lite", pdfName:"test.pdf",
    totalPages:1, pageStore:{}, pageRotations:{}, pageTags:{}, pageNames:{},
    projectInfo:{}, siteOrientation:{}, excludedPages:[], pageFloorKind:{},
    pageFloorNum:{}, liteLayers:liteLayersArr, liteGroups:liteGroupsArr,
    reportVars:serializeReportVars()};

  const rv = saveDoc.reportVars;
  const kpiEntry = rv && rv.find(function(v){ return v.name === 'myKPI'; });
  const hasPresets = rv && rv.find(function(v){ return v.id === 'v_net'; })
                  && rv.find(function(v){ return v.id === 'v_osr'; })
                  && rv.find(function(v){ return v.id === 'v_far'; });

  out.saveIncludesVars = !!(
    Array.isArray(rv) &&
    rv.length >= 4 &&
    kpiEntry &&
    kpiEntry.expr &&
    kpiEntry.expr.length === 2 &&
    kpiEntry.expr[1].lit === 2 &&
    hasPresets
  );

  // -----------------------------------------------------------------------
  // loadRestoresVars
  //   Take a crafted doc with a single reportVars entry (KPI-X = open/site*100)
  //   call loadProto → REPORT_VARS.length===1, name==='KPI-X', expr.length===3
  //   computeReportVars({open:60, site:300}) → value ≈ 20
  // -----------------------------------------------------------------------
  reseedRV();
  const craftedDoc = minimalDoc({
    reportVars: [{
      id: 'v_x',
      name: 'KPI-X',
      unit: '%',
      expr: [{ref:'open'}, {op:'/', ref:'site'}, {op:'*', lit:100}]
    }]
  });
  loadProto(craftedDoc);

  const rvAfterLoad = REPORT_VARS;
  const lengthOk = rvAfterLoad.length === 1;
  const nameOk   = lengthOk && rvAfterLoad[0].name === 'KPI-X';
  const exprOk   = lengthOk && rvAfterLoad[0].expr.length === 3;

  var computedVal = null;
  if (lengthOk) {
    var results = computeReportVars({open:60, site:300});
    computedVal = results[0] ? results[0].value : null;
  }
  const computeOk = computedVal !== null && Math.abs(computedVal - 20) < 0.001;

  out.loadRestoresVars = !!(lengthOk && nameOk && exprOk && computeOk);

  // -----------------------------------------------------------------------
  // oldFileSeedsDefaults
  //   load doc WITHOUT reportVars key → REPORT_VARS ends up as 3 presets
  //   (v_net, v_osr, v_far)
  // -----------------------------------------------------------------------
  reseedRV();
  const oldDoc = minimalDoc(); /* no reportVars */
  loadProto(oldDoc);

  const has3 = REPORT_VARS.length === 3;
  const hasVnet = has3 && REPORT_VARS.some(function(v){ return v.id === 'v_net'; });
  const hasVosr = has3 && REPORT_VARS.some(function(v){ return v.id === 'v_osr'; });
  const hasVfar = has3 && REPORT_VARS.some(function(v){ return v.id === 'v_far'; });

  out.oldFileSeedsDefaults = !!(has3 && hasVnet && hasVosr && hasVfar);

  // -----------------------------------------------------------------------
  // roundTrip
  //   start from 3 presets; serialize → JSON.stringify → JSON.parse →
  //   loadReportVars → serialize again; assert deep-equal.
  // -----------------------------------------------------------------------
  reseedRV();
  const ser1 = serializeReportVars();
  const ser1str = JSON.stringify(ser1);
  const parsed = JSON.parse(ser1str);
  loadReportVars(parsed);
  const ser2 = serializeReportVars();
  const ser2str = JSON.stringify(ser2);

  out.roundTrip = (ser1str === ser2str);

  // Restore clean state
  reseedRV();
  return out;
}
"""

CHECKS = [
    "saveIncludesVars",
    "loadRestoresVars",
    "oldFileSeedsDefaults",
    "roundTrip",
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
    print("LITE-REPORT-VARS-PERSIST checks:")
    for k in CHECKS:
        ok = result.get(k)
        print(f"  {k:35s} -> {ok}")
        if ok is not True:
            failures.append(f"check '{k}' = {ok!r} (expected True)")

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_REPORT_VARS_PERSIST_FAIL")
        sys.exit(1)
    else:
        print("LITE_REPORT_VARS_PERSIST_OK")


if __name__ == "__main__":
    main()
