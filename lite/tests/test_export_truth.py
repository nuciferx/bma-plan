"""
LITE report-truth slice A/4 (REVIEW_LITE_LAYER_REPORT_20260704.md ledger A-4)
acceptance test -- "one aggregation truth".

Verifies buildExportData() (export-annotate.js) and computeSummary()
(ui-lite.html) were both rerouted onto the SAME ObjectAgg tuple stream
(object-agg.js's objectTuples()/byCategory()) that report-vars/
buildReportPayload already consume, and that "a page is excluded" now means
the SAME thing everywhere: dropped from XLSX detail rows, XLSX summary,
the Sum-modal category table, and the report payload -- all at once,
reacting live to excluded[] toggles (no stale/cached totals).

Fixture: lite/tests/fixtures/custom_layer_report.bmaplan (reused from ledger
row A-1 / test_report_vars_rollup.py) -- 33 pages, calibScale pts_per_m on
page 14 and 26 only.
  page 1  (site, excludedPages:[1] baked into the fixture): no objects.
  page 14 (floor 1): 1 gfa poly on custom layer L4 (role=gfa).
  page 26 (floor 1): 5 gfa polys (L7 x3, L8 x1, L9 x1, all role=gfa) +
                      1 deduction opening (L5, role=ded).
This test additionally injects one counting object (catId 'count', the
fixture's built-in counting layer) on page 14 (kept) and one on page 26,
then sets excluded[26]=true mid-test to exercise the exclusion path on a
page that actually HAS data (the fixture's own excluded page 1 is empty).

Independent ground truth: Python pre-computes page14's poly area and
page26's 5-poly + 1-opening areas via Shoelace (same technique as
test_report_vars_rollup.py / test_closing_dup_strip.py), giving absolute
expected gfa/ded totals to check the tuple stream against -- not just
"the paths agree with each other" but "they agree with an area computed by
a from-scratch geometry routine".

Checks (LITE_EXPORT_TRUTH_OK on 5/5):
  (a) noExcludedRowsOk       buildExportData().rows has ZERO rows for any
                              excluded page (both the fixture's own page 1,
                              and page 26 after excluded[26]=true is set),
                              for every kind (area/count) of row.
  (b) xlsxRoleTotalsOk        buildExportData().summary, regrouped by role
                              via CATS lookup, matches ObjectAgg.byRole()
                              role totals -- before AND after excluding
                              page 26.
  (c) summaryDeepCompareOk    computeSummary()'s per-catId cur/all/curCnt/
                              allCnt entries deep-match ObjectAgg.
                              byCategory(objectTuples()) entry-for-entry --
                              before AND after excluding page 26.
  (d) netConsistencyOk        buildReportPayload()'s summed net (already
                              tuple-side, unaffected by this slice) equals
                              the role-signed net computed from BOTH the
                              XLSX summary and the raw tuple byRole() totals
                              -- after excluding page 26.
  (e) countingDropOk          the page-26 counting object's contribution
                              (count) is present pre-exclusion and vanishes
                              post-exclusion from computeSummary().allCnt,
                              buildExportData()'s summary, AND its detail
                              row -- while page 14's counting object is
                              unaffected throughout.

Also asserts the independently Python-Shoelace-computed gfa/ded totals
against ObjectAgg.byRole() (ground truth, not just cross-engine parity).

    py -3 lite/tests/test_export_truth.py
"""
import json
import socket
import sys
import threading
import time
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixtures" / "custom_layer_report.bmaplan"
sys.path.insert(0, str(LITE))

import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8600):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


def _shoelace(pts, ppm):
    p = pts[:]
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


def _compute_expected(doc):
    p14 = doc["pageStore"]["14"]
    ppm14 = p14["calibScale"]["pts_per_m"]
    gfa14 = sum(_shoelace(poly["pts"], ppm14) for poly in p14["polys"])

    p26 = doc["pageStore"]["26"]
    ppm26 = p26["calibScale"]["pts_per_m"]
    gfa26 = sum(_shoelace(poly["pts"], ppm26) for poly in p26["polys"])
    ded26 = sum(_shoelace(o["pts"], ppm26) for o in p26["openings"])

    return {
        "gfaTotalBefore": gfa14 + gfa26,
        "dedTotalBefore": ded26,
        "gfaTotalAfterExcl26": gfa14,       # page 26 (all its gfa) dropped
        "dedTotalAfterExcl26": 0.0,          # page 26's only ded dropped
    }


SCENARIO = r"""
([fixtureJsonStr, exp]) => {
  const out = {};
  if (typeof window.ObjectAgg !== 'object') return {pass: false, err: 'ObjectAgg not loaded'};
  if (typeof buildExportData !== 'function') return {pass: false, err: 'buildExportData not loaded'};
  if (typeof buildReportPayload !== 'function') return {pass: false, err: 'buildReportPayload not loaded'};

  function close(a, b, tol) { tol = tol == null ? 1e-6 * Math.max(1, Math.abs(b)) : tol; return Math.abs(a - b) < tol; }

  const doc = JSON.parse(fixtureJsonStr);
  loadProto(doc);

  // Inject one counting object on page 14 (kept) and one on page 26 (excluded later).
  PS[14].objects.push({id: state._id++, catId: 'count', semanticTag: 'count_marker',
    kind: 'count', counting: true, dimVisible: false, pts: [{x: 1, y: 1}]});
  PS[26].objects.push({id: state._id++, catId: 'count', semanticTag: 'count_marker',
    kind: 'count', counting: true, dimVisible: false, pts: [{x: 2, y: 2}]});

  function roleTotalsFromEdSummary(summary) {
    var res = {};
    summary.forEach(function(row) {
      var isCount = / \(จุด\)$/.test(row.category);
      var name = isCount ? row.category.replace(/ \(จุด\)$/, '') : row.category;
      var layer = CATS.filter(function(c) { return c.name === name; })[0];
      var role = layer ? layer.role : null;
      if (!role) return;
      if (!res[role]) res[role] = {area: 0, count: 0};
      if (isCount) res[role].count += row.total; else res[role].area += row.total;
    });
    return res;
  }

  function deepCompareCategory(s, byCat) {
    var keys = {};
    Object.keys(byCat).forEach(function(k) { keys[k] = true; });
    Object.keys(s.all || {}).forEach(function(k) { keys[k] = true; });
    Object.keys(s.allCnt || {}).forEach(function(k) { keys[k] = true; });
    var bad = [];
    Object.keys(keys).forEach(function(k) {
      var ent = byCat[k];
      if (!ent) { bad.push({k: k, reason: 'missing in byCategory'}); return; }
      if (ent.count > 0) {
        if (!close(s.allCnt[k] || 0, ent.count, 1e-9)) bad.push({k: k, reason: 'cnt mismatch', s: s.allCnt[k], t: ent.count});
      } else {
        if (!close(s.all[k] || 0, ent.area, 1e-6 * Math.max(1, ent.area))) bad.push({k: k, reason: 'area mismatch', s: s.all[k], t: ent.area});
      }
    });
    return bad;
  }

  /* ---------------------------------------------------------------- */
  /* BASELINE: only the fixture's own excluded[1] (empty page)         */
  /* ---------------------------------------------------------------- */
  var tuples0 = window.ObjectAgg.objectTuples();
  var byCat0 = window.ObjectAgg.byCategory(tuples0);
  var byRole0 = window.ObjectAgg.byRole(tuples0);
  var ed0 = buildExportData();
  var s0 = computeSummary();

  out._gfa0 = byRole0.gfa ? byRole0.gfa.area : null;
  out._ded0 = byRole0.ded ? byRole0.ded.area : null;
  var groundTruthBeforeOk = !!(byRole0.gfa && close(byRole0.gfa.area, exp.gfaTotalBefore, 0.5) &&
                                byRole0.ded && close(byRole0.ded.area, exp.dedTotalBefore, 0.5));

  var noP1RowsOk = !ed0.rows.some(function(r) { return r.page === 1; });
  var cntRowsBefore = ed0.rows.filter(function(r) { return r.kind === 'count'; });
  var cntBeforeOk = cntRowsBefore.length === 2 &&
    cntRowsBefore.some(function(r) { return r.page === 14; }) &&
    cntRowsBefore.some(function(r) { return r.page === 26; });

  // NOTE: ed.summary rounds each category's area to 3dp (toFixed(3)) before
  // summing per role here, so compare with a fixed 0.01 tolerance (not the
  // default 1e-6-relative one used for the exact/undounded comparisons).
  var rt0 = roleTotalsFromEdSummary(ed0.summary);
  var xlsxRoleTotalsBeforeOk = !!(rt0.gfa && close(rt0.gfa.area, byRole0.gfa.area, 0.01) &&
                                   rt0.ded && close(rt0.ded.area, byRole0.ded.area, 0.01) &&
                                   rt0.count && rt0.count.count === (byRole0.count ? byRole0.count.count : -1));

  var summaryDeepCompareBeforeBad = deepCompareCategory(s0, byCat0);
  var summaryDeepCompareBeforeOk = summaryDeepCompareBeforeBad.length === 0;

  /* ---------------------------------------------------------------- */
  /* EXCLUDE page 26 (has real gfa/ded/count data)                     */
  /* ---------------------------------------------------------------- */
  excluded[26] = true;

  var tuples1 = window.ObjectAgg.objectTuples();
  var byCat1 = window.ObjectAgg.byCategory(tuples1);
  var byRole1 = window.ObjectAgg.byRole(tuples1);
  var ed1 = buildExportData();
  var s1 = computeSummary();
  var payload1 = buildReportPayload();

  out._gfa1 = byRole1.gfa ? byRole1.gfa.area : null;
  out._ded1 = byRole1.ded ? byRole1.ded.area : null;
  var groundTruthAfterOk = !!(byRole1.gfa && close(byRole1.gfa.area, exp.gfaTotalAfterExcl26, 0.5) &&
                               !byRole1.ded);   // page26 was the ONLY ded source -> role disappears entirely

  /* (a) no excluded-page rows at all, of any kind */
  var no26RowsOk = !ed1.rows.some(function(r) { return r.page === 26; });
  var noExcludedRowsOk = noP1RowsOk && no26RowsOk;

  /* (b) XLSX summary role totals == tuple byRole() totals, after exclusion */
  var rt1 = roleTotalsFromEdSummary(ed1.summary);
  var xlsxRoleTotalsAfterOk = !!(rt1.gfa && close(rt1.gfa.area, byRole1.gfa.area, 0.01) &&
                                  !rt1.ded &&
                                  rt1.count && rt1.count.count === (byRole1.count ? byRole1.count.count : -1));
  var xlsxRoleTotalsOk = xlsxRoleTotalsBeforeOk && xlsxRoleTotalsAfterOk;

  /* (c) computeSummary() deep-matches byCategory(), per catId, after exclusion too */
  var summaryDeepCompareAfterBad = deepCompareCategory(s1, byCat1);
  var summaryDeepCompareAfterOk = summaryDeepCompareAfterBad.length === 0;
  var summaryDeepCompareOk = summaryDeepCompareBeforeOk && summaryDeepCompareAfterOk;

  /* (d) buildReportPayload net vs XLSX-role-signed net vs raw tuple net, after exclusion */
  var payloadNoP26Ok = !payload1.pages.some(function(p) { return p.idx === 26; });
  var payloadNetSum = 0; payload1.pages.forEach(function(p) { payloadNetSum += p.net; });
  var xlsxNet = (rt1.gfa ? rt1.gfa.area : 0) - (rt1.ded ? rt1.ded.area : 0);
  var tupleNet = (byRole1.gfa ? byRole1.gfa.area : 0) - (byRole1.ded ? byRole1.ded.area : 0);
  var netConsistencyOk = payloadNoP26Ok &&
    close(payloadNetSum, xlsxNet, 0.05) && close(payloadNetSum, tupleNet, 0.05) && close(xlsxNet, tupleNet, 0.05);

  /* (e) counting: page26's counting object drops, page14's survives, everywhere */
  var cntAfterAllCnt = (s1.allCnt && s1.allCnt.count) || 0;
  var cntRowsAfter = ed1.rows.filter(function(r) { return r.kind === 'count'; });
  var countingDropOk = cntBeforeOk &&
    (s0.allCnt.count === 2) && (cntAfterAllCnt === 1) &&
    cntRowsAfter.length === 1 && cntRowsAfter[0].page === 14 &&
    (rt1.count && rt1.count.count === 1);

  out.groundTruthBeforeOk = groundTruthBeforeOk;
  out.groundTruthAfterOk = groundTruthAfterOk;
  out.noExcludedRowsOk = noExcludedRowsOk;
  out.xlsxRoleTotalsOk = xlsxRoleTotalsOk;
  out.summaryDeepCompareOk = summaryDeepCompareOk;
  out.netConsistencyOk = netConsistencyOk;
  out.countingDropOk = countingDropOk;
  out._summaryDeepCompareBeforeBad = summaryDeepCompareBeforeBad;
  out._summaryDeepCompareAfterBad = summaryDeepCompareAfterBad;
  out._payloadNetSum = payloadNetSum; out._xlsxNet = xlsxNet; out._tupleNet = tupleNet;
  out._rt0 = rt0; out._rt1 = rt1;

  out.pass = groundTruthBeforeOk && groundTruthAfterOk && noExcludedRowsOk &&
    xlsxRoleTotalsOk && summaryDeepCompareOk && netConsistencyOk && countingDropOk;

  return out;
}
"""

CHECKS = [
    "noExcludedRowsOk",
    "xlsxRoleTotalsOk",
    "summaryDeepCompareOk",
    "netConsistencyOk",
    "countingDropOk",
]


def main():
    if not FIXTURE.exists():
        print(f"FAIL: fixture not found: {FIXTURE}")
        sys.exit(1)

    doc = json.loads(FIXTURE.read_text(encoding="utf-8"))
    fixture_json = json.dumps(doc)
    expected = _compute_expected(doc)
    print(f"[fixture] independent Shoelace ground truth: {expected}")

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

        try:
            result = pg.evaluate(SCENARIO, [fixture_json, expected])
        except Exception as ex:
            print(f"EXCEPTION: {ex}")
            failures.append(f"scenario threw: {ex}")
            result = {}

        pg.close()
        b.close()

    server.should_exit = True
    time.sleep(0.4)

    for e in page_errors:
        print("  JS ERROR:", e)

    print()
    print("=== ground truth (independent Shoelace) ===")
    print(f"  gfa before={result.get('_gfa0')} (expected ~{expected['gfaTotalBefore']:.2f})")
    print(f"  ded before={result.get('_ded0')} (expected ~{expected['dedTotalBefore']:.2f})")
    print(f"  gfa after excl26={result.get('_gfa1')} (expected ~{expected['gfaTotalAfterExcl26']:.2f})")
    print(f"  ded after excl26={result.get('_ded1')} (expected ~{expected['dedTotalAfterExcl26']:.2f})")
    print()
    print("=== net consistency ===")
    print(f"  payload net sum={result.get('_payloadNetSum')}  xlsx net={result.get('_xlsxNet')}  tuple net={result.get('_tupleNet')}")
    print()
    print(f"  rt0={result.get('_rt0')}")
    print(f"  rt1={result.get('_rt1')}")
    print()
    if result.get("_summaryDeepCompareBeforeBad"):
        print("  deep-compare BEFORE mismatches:", result["_summaryDeepCompareBeforeBad"])
    if result.get("_summaryDeepCompareAfterBad"):
        print("  deep-compare AFTER mismatches:", result["_summaryDeepCompareAfterBad"])

    print()
    print("LITE-EXPORT-TRUTH checks:")
    if not result.get("groundTruthBeforeOk"):
        failures.append(f"groundTruthBeforeOk failed: {result}")
    if not result.get("groundTruthAfterOk"):
        failures.append(f"groundTruthAfterOk failed: {result}")
    for k in CHECKS:
        ok = result.get(k)
        print(f"  {k:25s} -> {'PASS' if ok else 'FAIL'}")
        if ok is not True:
            failures.append(f"check '{k}' = {ok!r} (expected True)")

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_EXPORT_TRUTH_FAIL")
        sys.exit(1)
    else:
        print("LITE_EXPORT_TRUTH_OK")


if __name__ == "__main__":
    main()
