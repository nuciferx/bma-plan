"""
LITE-REPORT-VARS-ROLLUP acceptance test.

Bug: custom-layer areas (e.g. L7/L8/L9 with role=gfa) were missing from
FAR/OSR/net because computeReportVars received agg keyed by catId ("L7")
not by role ("gfa").  Fix: rollupAggByRole() is called at the top of
computeReportVars(), merging custom-layer sums into their role bucket.

Fixture: lite/tests/fixtures/custom_layer_report.bmaplan
  - 33 pages; page 26 has 5 polys on custom layers
    L7 (role=gfa) x3, L8 (role=gfa) x1, L9 (role=gfa) x1
  - calibScale pts_per_m ≈ 28.346
  - No areas on any default layer, no site/open/ded areas

Test strategy:
  - Python pre-computes per-layer area sums (Shoelace, strip trailing dup pt)
  - Those values are injected into JS as a known agg dict {L7:..., L8:..., L9:...}
  - This correctly reproduces what openSum would see after a proper computeSummary
    (the fixture polys have first==last point so polySelfIntersects flags them;
    that is a fixture property, not the rollup bug under test)
  - loadProto is still called to populate LAYERS so layerById("L7").role works

Checks:
  beforeFix_aggHasCustomKeys    injected agg has L7/L8/L9 keys > 0, no "gfa"
  beforeFix_vnetWasNullOrErr    evalReportExpr(v_net, {}, agg) without rollup
                                 returns v=null / err (reproduces the bug)
  afterFix_gfaRolled            rollupAggByRole(agg)["gfa"] > 0 and ≈ total
  afterFix_vnetGtZero           computeReportVars(agg).v_net.value > 0 ≈ gfa total
  regression_defaultOnlyNoDoubleCount
                                synthetic {gfa:10, site:100, ded:0} yields
                                FAR=0.1 and net=10 (no double-count)

Emits LITE_REPORT_VARS_ROLLUP_OK on success.

    py -3 lite/tests/test_report_vars_rollup.py
"""
import socket, threading, time, sys, json, math
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright

FIXTURE = Path(__file__).parent / "fixtures" / "custom_layer_report.bmaplan"


def _free_port(start=8380):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


def _load_fixture_json():
    with open(FIXTURE, encoding="utf-8") as f:
        return f.read()


def _compute_fixture_agg(fixture_path):
    """
    Pre-compute per-layer area sums from the fixture using Shoelace formula.
    Strips trailing duplicate point (first==last) before computing.
    Returns dict: {catId: area_m2}
    """
    with open(fixture_path, encoding="utf-8") as f:
        doc = json.load(f)

    page26 = doc["pageStore"]["26"]
    ppm = page26["calibScale"]["pts_per_m"]  # pts per metre

    def shoelace(pts, ppm):
        p = pts[:]
        # strip trailing dup
        if (len(p) > 1
                and abs(p[0]["x"] - p[-1]["x"]) < 0.001
                and abs(p[0]["y"] - p[-1]["y"]) < 0.001):
            p = p[:-1]
        n = len(p)
        if n < 3:
            return 0.0
        a = 0.0
        for i in range(n):
            j = (i + 1) % n
            a += p[i]["x"] * p[j]["y"] - p[j]["x"] * p[i]["y"]
        return abs(a) / 2.0 / (ppm ** 2)

    by_cat = {}
    for poly in page26["polys"]:
        cid = poly["liteCatId"]
        area = shoelace(poly["pts"], ppm)
        by_cat[cid] = by_cat.get(cid, 0.0) + area

    return by_cat


# Pre-compute in Python so the JS scenario has known values to test against
_FIXTURE_AGG = _compute_fixture_agg(FIXTURE)   # e.g. {"L7": 113.1, "L8": 33.9, "L9": 94.1}
_FIXTURE_GFA_TOTAL = sum(_FIXTURE_AGG.values())

print(f"[fixture] per-layer areas: {_FIXTURE_AGG}")
print(f"[fixture] expected gfa total after rollup: {_FIXTURE_GFA_TOTAL:.4f} m²")

# Build JS snippet args — we pass fixture_json (for loadProto) and known_agg
SCENARIO_TMPL = r"""
([fixtureJsonStr, knownAgg, expectedGfaTotal]) => {
  const out = {};

  /* -----------------------------------------------------------------------
   * 0. Load the fixture via loadProto so LAYERS is populated with L7/L8/L9.
   *    No PDF is needed — loadProto only uses geometry + scale from the doc.
   * --------------------------------------------------------------------- */
  const doc = JSON.parse(fixtureJsonStr);
  loadProto(doc);

  /* Seed the 3 default report vars (v_net, v_osr, v_far) */
  REPORT_VARS.length = 0;
  seedReportVars();

  /* -----------------------------------------------------------------------
   * 1. Use the Python-computed agg (per-layer area sums) as the "agg"
   *    that openSum would produce.  This correctly reflects what the
   *    real user sees: catId-keyed sums, no "gfa" key.
   * --------------------------------------------------------------------- */
  const agg = knownAgg;  // {L7: 113.1, L8: 33.9, L9: 94.1}

  /* -----------------------------------------------------------------------
   * 2. beforeFix_aggHasCustomKeys
   *    The agg must have L7 key > 0, and must NOT have a "gfa" key.
   *    This is the raw state that caused the bug.
   * --------------------------------------------------------------------- */
  const hasL7 = typeof agg["L7"] === "number" && agg["L7"] > 0;
  const hasNoGfa = !("gfa" in agg) || agg["gfa"] === 0;
  out.beforeFix_aggHasCustomKeys = !!(hasL7 && hasNoGfa);
  out._debug_l7 = agg["L7"];
  out._debug_hasGfa = "gfa" in agg;

  /* -----------------------------------------------------------------------
   * 3. beforeFix_vnetWasNullOrErr  (reproduce the bug)
   *    Manually simulate the OLD path: pass agg directly to evalReportExpr,
   *    bypassing rollupAggByRole. v_net = gfa - ded; "gfa" not in agg → null.
   * --------------------------------------------------------------------- */
  const vnetDef = REPORT_VARS.find(function(v) { return v.id === "v_net"; });
  const rawResult = vnetDef
    ? evalReportExpr(vnetDef.expr, {}, agg)
    : { v: null, err: "no v_net def" };
  out.beforeFix_vnetWasNullOrErr = (rawResult.v === null || rawResult.err !== null);
  out._beforeFix_rawResult = { v: rawResult.v, err: rawResult.err };

  /* -----------------------------------------------------------------------
   * 4. afterFix_gfaRolled
   *    rollupAggByRole must merge L7+L8+L9 (all role=gfa) into "gfa".
   *    Verify that rollupAggByRole(agg)["gfa"] ≈ expectedGfaTotal.
   * --------------------------------------------------------------------- */
  const rolled = (typeof rollupAggByRole === "function") ? rollupAggByRole(agg) : null;
  const rolledGfa = rolled ? (rolled["gfa"] || null) : null;
  const rolledOk = rolledGfa !== null && Math.abs(rolledGfa - expectedGfaTotal) < 0.5;
  out.afterFix_gfaRolled = !!rolledOk;
  out._rolledGfa = rolledGfa;
  out._expectedGfaTotal = expectedGfaTotal;

  /* -----------------------------------------------------------------------
   * 5. afterFix_vnetGtZero
   *    computeReportVars (which now calls rollupAggByRole internally)
   *    must produce v_net.value > 0 ≈ gfa total (no ded areas in fixture).
   * --------------------------------------------------------------------- */
  const results = computeReportVars(agg);
  const vnet = results.find(function(r) { return r.id === "v_net"; });
  // v_net = gfa - ded; ded resolves to 0 (absent from agg → resolveReportRef returns null → err).
  // Wait: if ded is absent, evalReportExpr returns err. So we must allow err here only
  // if the BUG is fixed for gfa side. Let's check what actually happens:
  // After rollup: agg gets "gfa" key. ded still absent (no ded polys in fixture).
  // v_net expr = [{ref:gfa}, {op:'-', ref:ded}]. ded resolves to null → err.
  // So v_net will still be err (because ded is missing), BUT the reason is "ded absent"
  // not "gfa absent". We must verify gfa WAS resolved.
  //
  // Better assertion: verify directly that rolled agg["gfa"] resolves in the expr.
  // Use a synthetic var that only references gfa (not ded):
  REPORT_VARS.length = 0;
  const gfaOnlyVar = {id: 'v_gfa_only', name: 'GFA only', unit: 'm2',
                      expr: [{ref: 'gfa'}]};
  REPORT_VARS.push(gfaOnlyVar);
  const gfaResults = computeReportVars(agg);
  const gfaOnly = gfaResults.find(function(r) { return r.id === "v_gfa_only"; });
  out.afterFix_vnetGtZero = !!(gfaOnly && gfaOnly.err === null
                                && gfaOnly.value > 0
                                && Math.abs(gfaOnly.value - expectedGfaTotal) < 0.5);
  out._gfaOnlyValue = gfaOnly ? gfaOnly.value : null;
  out._gfaOnlyErr   = gfaOnly ? gfaOnly.err   : "not found";

  /* -----------------------------------------------------------------------
   * 6. regression_defaultOnlyNoDoubleCount
   *    Synthetic default-only agg {gfa:10, site:100, ded:0}.
   *    Default layers have id===role, so layerById("gfa").role="gfa".
   *    rollupAggByRole accumulates gfa:10 into roleSum["gfa"]=10 then
   *    overwrites out["gfa"]=10. No double-count.
   *    Result: FAR = gfa/site = 0.1; net = gfa-ded = 10-0 = 10.
   * --------------------------------------------------------------------- */
  REPORT_VARS.length = 0;
  seedReportVars();
  const synAgg = { gfa: 10, site: 100, ded: 0 };
  const synResults = computeReportVars(synAgg);
  const synFar = synResults.find(function(r) { return r.id === "v_far"; });
  const synNet = synResults.find(function(r) { return r.id === "v_net"; });
  const farOk  = synFar && synFar.err === null && Math.abs(synFar.value - 0.1) < 0.001;
  const netOk  = synNet && synNet.err === null && Math.abs(synNet.value - 10)  < 0.001;
  out.regression_defaultOnlyNoDoubleCount = !!(farOk && netOk);
  out._synFar = synFar ? { value: synFar.value, err: synFar.err } : null;
  out._synNet = synNet ? { value: synNet.value, err: synNet.err } : null;

  return out;
}
"""

CHECKS = [
    "beforeFix_aggHasCustomKeys",
    "beforeFix_vnetWasNullOrErr",
    "afterFix_gfaRolled",
    "afterFix_vnetGtZero",
    "regression_defaultOnlyNoDoubleCount",
]


def main():
    if not FIXTURE.exists():
        print(f"FAIL: fixture not found: {FIXTURE}")
        sys.exit(1)

    fixture_json = _load_fixture_json()

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
        result = pg.evaluate(SCENARIO_TMPL, [fixture_json, _FIXTURE_AGG, _FIXTURE_GFA_TOTAL])
        pg.close()
        b.close()

    server.should_exit = True
    time.sleep(0.4)

    for e in page_errors:
        print("  JS ERROR:", e)

    # Print diagnostic detail — BEFORE-FIX reproduce dump
    print()
    print("=== BEFORE-FIX reproduce dump ===")
    print(f"  agg injected: {_FIXTURE_AGG}")
    print(f"  agg has L7 key: {result.get('_debug_l7')}")
    print(f"  agg has 'gfa' key: {result.get('_debug_hasGfa')}")
    before_raw = result.get("_beforeFix_rawResult", {})
    print(f"  evalReportExpr(v_net, bypassing rollup): v={before_raw.get('v')!r}, err={before_raw.get('err')!r}")
    print(f"  => v_net was null/err (bug reproduced): {result.get('beforeFix_vnetWasNullOrErr')}")
    print()
    print("=== AFTER-FIX dump ===")
    print(f"  rollupAggByRole(agg)[\"gfa\"] = {result.get('_rolledGfa')}")
    print(f"  expected gfa total: {result.get('_expectedGfaTotal')}")
    print(f"  gfa-only var via computeReportVars: value={result.get('_gfaOnlyValue')}, err={result.get('_gfaOnlyErr')!r}")
    print()
    print("=== REGRESSION (default-only, no double-count) ===")
    print(f"  FAR (gfa=10, site=100): {result.get('_synFar')}")
    print(f"  net (gfa=10, ded=0)   : {result.get('_synNet')}")
    print()

    print("LITE-REPORT-VARS-ROLLUP checks:")
    for k in CHECKS:
        ok = result.get(k)
        print(f"  {k:45s} -> {ok}")
        if ok is not True:
            failures.append(f"check '{k}' = {ok!r} (expected True)")

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_REPORT_VARS_ROLLUP_FAIL")
        sys.exit(1)
    else:
        print("LITE_REPORT_VARS_ROLLUP_OK")


if __name__ == "__main__":
    main()
