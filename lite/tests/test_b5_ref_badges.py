"""
INV-20260703-layer-linkage -- approach B, slice B5 acceptance test.

Verifies the B5 fix (closes M4): the report-var editor's operand dropdown
now distinguishes ROLE refs ("gfa" = rollup of every layer whose role is
gfa) from LAYER refs ("L1" = one specific layer's own area) instead of
rendering both identically.

report-vars.js `_rvOperandOptions()` / `_rvOperandWidget()` now group the
<select> into two <optgroup>s:
  "หมวดรวม (ทุกเลเยอร์ใน role)" -- the 6 ROLE_DEFS, each option prefixed "Σ ".
  "เลเยอร์เดี่ยว"                -- CUSTOM layers only (id !== role id,
                                    e.g. addLayer()-created "L1"), each
                                    option prefixed "▸ " + layer name +
                                    "(role name)". Default per-role layers
                                    are NOT re-listed here (their ref string
                                    is identical to their role's -- listing
                                    them would just duplicate the role
                                    option, re-adding the very ambiguity
                                    this sprint removes).

Checks:
  dropdownGrouped     the operand <select> for a var contains exactly 2
                      <optgroup> elements labelled as above; every option
                      inside the role optgroup starts with "Σ "; every
                      option inside the layer optgroup starts with "▸ ".
  roleRefShowsSigma   a var whose token references a ROLE id ('gfa') has
                      its <select> showing (selected option) a label that
                      starts with "Σ".
  layerRefShowsTri    a var whose token references a CUSTOM layer id
                      (addLayer()'s returned id, not a role id) has its
                      <select> showing (selected option) a label that
                      starts with "▸" and contains the layer's own name.
  evalUnchanged       computeReportVars()'s numeric results for both ref
                      kinds are unchanged from pre-B5 semantics: the role
                      ref rolls up ALL layers of that role (default +
                      custom), the layer ref resolves to ONLY that layer's
                      own agg value -- proves the display-only change did
                      not touch evalReportExpr / resolveReportRef /
                      rollupAggByRole.
  roundTripOk         serializeReportVars() -> loadReportVars() preserves
                      both ref strings verbatim (persisted expr format is
                      untouched by this sprint -- display-only).

Emits LITE_B5_REF_BADGES_OK on success.

    py -3 lite/tests/test_b5_ref_badges.py
"""
import socket, threading, time, sys
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8580):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


SCENARIO = r"""
() => {
  const out = {};

  // Custom layer, role=gfa, distinct id (e.g. "L1") -- never equal to a role id.
  var customLayer = addLayer('gfa', 'ชั้น1', '#8844ff');

  // Two vars: one referencing the ROLE id, one referencing the CUSTOM LAYER id.
  REPORT_VARS.length = 0;
  REPORT_VARS.push({id: 'v_role',  name: 'RoleRef',  unit: 'm2', expr: [{ref: 'gfa'}]});
  REPORT_VARS.push({id: 'v_layer', name: 'LayerRef', unit: 'm2', expr: [{ref: customLayer.id}]});

  // agg: default "gfa" layer has 1000 m2 of its own; the custom layer has 250 m2.
  // Both share role=gfa, so the ROLE ref should roll up to 1250; the LAYER
  // ref should resolve to just 250 (untouched by the role rollup).
  var agg = {}; agg['gfa'] = 1000; agg[customLayer.id] = 250;

  var host = document.createElement('div');
  host.id = '__b5_test_host';
  document.body.appendChild(host);
  renderReportVarsEditor(host, agg);   // default (legacy/pure) path -- no useLive

  var rows = host.querySelectorAll('.rv-row');
  out.rowCount = rows.length;

  // -----------------------------------------------------------------------
  // dropdownGrouped: row[0]'s operand select has 2 optgroups, correctly
  // labelled + prefixed.
  // -----------------------------------------------------------------------
  var sel0 = rows[0] ? rows[0].querySelector('select') : null;
  if (!sel0) {
    out.dropdownGrouped = false;
  } else {
    var groups = sel0.querySelectorAll('optgroup');
    out.optgroupCount = groups.length;
    var roleGroup  = groups[0];
    var layerGroup = groups[1];
    var labelsOk = !!(roleGroup && layerGroup &&
      roleGroup.label.indexOf('หมวดรวม') !== -1 &&
      layerGroup.label.indexOf('เลเยอร์เดี่ยว') !== -1);

    var roleOptsOk = true;
    (roleGroup ? roleGroup.querySelectorAll('option') : []).forEach(function(o) {
      if (o.textContent.indexOf('Σ ') !== 0) roleOptsOk = false;
    });
    var roleOptCount = roleGroup ? roleGroup.querySelectorAll('option').length : 0;

    var layerOptsOk = true;
    (layerGroup ? layerGroup.querySelectorAll('option') : []).forEach(function(o) {
      if (o.textContent.indexOf('▸ ') !== 0) layerOptsOk = false;
    });
    var layerOptCount = layerGroup ? layerGroup.querySelectorAll('option').length : 0;

    out.roleOptCount = roleOptCount;
    out.layerOptCount = layerOptCount;
    out.dropdownGrouped = labelsOk && roleOptsOk && layerOptsOk &&
      roleOptCount === 6 && layerOptCount >= 1;
  }

  // -----------------------------------------------------------------------
  // roleRefShowsSigma: row[0] (ref:'gfa') selected option starts with Σ.
  // -----------------------------------------------------------------------
  if (sel0) {
    var selOpt0 = sel0.options[sel0.selectedIndex];
    out.roleRefShowsSigma = !!selOpt0 && selOpt0.textContent.indexOf('Σ') === 0;
    out.roleRefSelectedText = selOpt0 ? selOpt0.textContent : null;
  } else {
    out.roleRefShowsSigma = false;
  }

  // -----------------------------------------------------------------------
  // layerRefShowsTri: row[1] (ref:customLayer.id) selected option starts
  // with ▸ and contains the layer's own name.
  // -----------------------------------------------------------------------
  var sel1 = rows[1] ? rows[1].querySelector('select') : null;
  if (sel1) {
    var selOpt1 = sel1.options[sel1.selectedIndex];
    out.layerRefShowsTri = !!selOpt1 &&
      selOpt1.textContent.indexOf('▸') === 0 &&
      selOpt1.textContent.indexOf('ชั้น1') !== -1;
    out.layerRefSelectedText = selOpt1 ? selOpt1.textContent : null;
  } else {
    out.layerRefShowsTri = false;
  }

  // -----------------------------------------------------------------------
  // evalUnchanged: numeric semantics untouched by the display-only change.
  // -----------------------------------------------------------------------
  var results = computeReportVars(agg);
  var rRole  = results.filter(function(r) { return r.id === 'v_role'; })[0];
  var rLayer = results.filter(function(r) { return r.id === 'v_layer'; })[0];
  out.roleVal = rRole ? rRole.value : null;
  out.layerVal = rLayer ? rLayer.value : null;
  out.evalUnchanged = !!(rRole && rLayer &&
    rRole.err === null && rLayer.err === null &&
    Math.abs(rRole.value - 1250) < 1e-9 &&
    Math.abs(rLayer.value - 250) < 1e-9);

  // -----------------------------------------------------------------------
  // roundTripOk: serialize -> load preserves both ref strings verbatim.
  // -----------------------------------------------------------------------
  var saved = serializeReportVars();
  REPORT_VARS.length = 0;
  loadReportVars(saved);
  var rt0 = REPORT_VARS.filter(function(v) { return v.id === 'v_role'; })[0];
  var rt1 = REPORT_VARS.filter(function(v) { return v.id === 'v_layer'; })[0];
  out.roundTripOk = !!(rt0 && rt1 &&
    rt0.expr[0].ref === 'gfa' &&
    rt1.expr[0].ref === customLayer.id);

  // Restore clean state.
  REPORT_VARS.length = 0;
  seedReportVars();

  return out;
}
"""

CHECKS = [
    "dropdownGrouped",
    "roleRefShowsSigma",
    "layerRefShowsTri",
    "evalUnchanged",
    "roundTripOk",
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

    no_page_error = len(page_errors) == 0
    result["noPageError"] = no_page_error
    CHECKS.append("noPageError")

    for e in page_errors:
        print("  JS ERROR:", e)

    print()
    print("LITE-B5-REF-BADGES checks:")
    for k in CHECKS:
        ok = result.get(k)
        print(f"  {k:25s} -> {ok}")
        if ok is not True:
            failures.append(f"check '{k}' = {ok!r} (expected True)")

    diag_keys = [
        "rowCount", "optgroupCount", "roleOptCount", "layerOptCount",
        "roleRefSelectedText", "layerRefSelectedText",
        "roleVal", "layerVal",
    ]
    print()
    print("  Diagnostics:")
    for k in diag_keys:
        if k in result:
            print(f"    {k}: {result[k]}")

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_B5_REF_BADGES_FAIL")
        sys.exit(1)
    else:
        print("LITE_B5_REF_BADGES_OK")


if __name__ == "__main__":
    main()
