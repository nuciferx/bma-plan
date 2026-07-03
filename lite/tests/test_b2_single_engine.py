"""
INV-20260703-layer-linkage -- approach B, slice B2 acceptance test
(final structural slice -- retires the second folder-scoped aggregation
engine).

Verifies:
  (i) threeWayF1 / threeWayF2   Review-row net per floor (Section 3, GFA
                      Breakdown ต่อชั้น) == Summary per-floor block rows
                      (openSum's floorReportRows()) == ObjectAgg.byFloorRole()
                      -- all three now read the same tuple bucket
                      (structural convergence, H2 closed).
      rootIncludedInReview / rootIncludedInSummary / rootIncludedInTuple
                      a gfa-role custom layer that is NEVER filed into its
                      PF_floor_1 folder (root-unfiled) is nonetheless
                      counted in floor 1's gross/net in ALL THREE places
                      -- the "M6" fix (deliberate: old folder-membership
                      sum silently dropped it).
  (ii) ltOwnAreaRegressionOk  _ltOwnArea(layerId) (tuple-sourced, B2)
                      returns the SAME number as _ltOwnAreaLegacyLoop(layerId)
                      (pre-B2 PS-iteration loop) for ordinary filed layers
                      -- regression guard, no excluded pages in this fixture
                      so the two paths must agree exactly.
  (iii) oracleOk       ObjectAgg.assertEnginesAgree() (extended in B2 with a
                      floorRole-partition check) returns ok:true end-to-end
                      against this fixture.

Fixture (scale 1 pt/m, page-folder mode ON, PF_floor_1 + PF_floor_2 seeded):
  P1 (floor 1): f1Gfa (filed under PF_floor_1, 500 m2), rootGfa (custom
                gfa-role layer, parentId=null -- NEVER filed, 80 m2)
  P2 (floor 2): f2Gfa (filed under PF_floor_2, 300 m2),
                f2Ded (filed under PF_floor_2, ded role, 40 m2)
  Expected floor:1 net = 500 + 80 - 0 = 580  (root layer INCLUDED, M6)
  Expected floor:2 net = 300 - 40 = 260

Emits LITE_B2_SINGLE_ENGINE_OK on success.

    py -3 lite/tests/test_b2_single_engine.py
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


SC_B2 = r"""
async () => {
  await new Promise(r => setTimeout(r, 300));
  if (typeof window.ObjectAgg !== 'object') return {pass: false, err: 'ObjectAgg not loaded'};
  if (typeof seedPageFolders !== 'function') return {pass: false, err: 'seedPageFolders not loaded'};
  if (typeof openOv !== 'function') return {pass: false, err: 'overview-setup.js (openOv) not loaded'};
  if (typeof _ltOwnArea !== 'function' || typeof _ltOwnAreaLegacyLoop !== 'function') {
    return {pass: false, err: '_ltOwnArea / _ltOwnAreaLegacyLoop not loaded'};
  }

  /* ---- fixture ---- */
  for (var k in pageTags) delete pageTags[k];
  for (var k in pageFloorNum) delete pageFloorNum[k];
  for (var k in pageFloorKind) delete pageFloorKind[k];
  for (var k in PS) delete PS[k];
  for (var k in excluded) delete excluded[k];
  pageCount = 2;
  pageTags[1] = 'floor'; pageFloorKind[1] = 'normal'; pageFloorNum[1] = 1;
  pageTags[2] = 'floor'; pageFloorKind[2] = 'normal'; pageFloorNum[2] = 2;
  for (var n = 1; n <= 2; n++) PS[n] = {objects: [], scale: {pts_per_m: 1}, annotations: []};
  curPage = 1;

  LAYERS.length = 0; FOLDERS.length = 0; initLayers();
  state.pageFolderMode = true;
  seedPageFolders([1, 2], pageTags, pageFloorNum, pageFloorKind);

  var f1Gfa = null, f2Gfa = null, f2Ded = null;
  LAYERS.forEach(function(l) {
    if (l.parentId === 'PF_floor_1' && l.role === 'gfa') f1Gfa = l;
    if (l.parentId === 'PF_floor_2' && l.role === 'gfa') f2Gfa = l;
    if (l.parentId === 'PF_floor_2' && l.role === 'ded' && !f2Ded) f2Ded = l;
  });
  var rootGfa = addLayer('gfa', 'Root Unfiled GFA', '#00ff88');  // parentId stays null -- NEVER filed

  function rect(w, h, ox, oy) { ox = ox || 0; oy = oy || 0; return [{x:ox,y:oy},{x:ox+w,y:oy},{x:ox+w,y:oy+h},{x:ox,y:oy+h}]; }

  PS[1].objects.push({id: 1, kind: 'poly', pts: rect(25, 20, 0, 0),   catId: f1Gfa.id,   counting: false});  // 500
  PS[1].objects.push({id: 2, kind: 'poly', pts: rect(10, 8, 100, 0),  catId: rootGfa.id, counting: false});  // 80 (root-unfiled)
  PS[2].objects.push({id: 3, kind: 'poly', pts: rect(20, 15, 0, 0),   catId: f2Gfa.id,   counting: false});  // 300
  PS[2].objects.push({id: 4, kind: 'poly', pts: rect(8, 5, 0, 0),     catId: f2Ded.id,   counting: false});  // 40

  var expF1Gross = 580, expF1Ded = 0, expF1Net = 580;
  var expF2Gross = 300, expF2Ded = 40, expF2Net = 260;

  function close(a, b, tol) { tol = tol == null ? 1e-6 : tol; return Math.abs(a - b) < tol; }
  function numFrom(txt) { var m = String(txt).replace(/,/g, '').match(/[\d.]+/); return m ? parseFloat(m[0]) : NaN; }

  /* ---- open wizard, jump to Step 3 (Review) ---- */
  var _origCaseId = (typeof caseId !== 'undefined') ? caseId : undefined;
  caseId = 'test-mock-b2';
  openOv();
  var step3 = document.querySelector('#ov-steps .step[data-step="3"]');
  if (step3) step3.click();
  await new Promise(r => setTimeout(r, 200));

  var reportEl = document.getElementById('report');
  var table = Array.prototype.filter.call(
    document.querySelectorAll('#report table'),
    function(t) { return t.innerHTML.indexOf('Gross') >= 0; }
  )[0];
  var rowEls = table ? Array.prototype.filter.call(table.querySelectorAll('tr'), function(tr) {
    return tr.querySelectorAll('td').length === 6;
  }) : [];
  var reviewRows = rowEls.map(function(tr) {
    var tds = tr.querySelectorAll('td');
    return {
      page: tds[1].textContent.trim(),
      gross: numFrom(tds[2].textContent),
      ded: numFrom(tds[3].textContent),
      net: numFrom(tds[4].textContent)
    };
  });
  var rF1 = reviewRows.filter(function(r) { return r.page === 'p1'; })[0];
  var rF2 = reviewRows.filter(function(r) { return r.page === 'p2'; })[0];

  var frows = window.ObjectAgg.floorReportRows();
  var sF1 = frows.filter(function(r) { return r.floorKey === 'floor:1'; })[0];
  var sF2 = frows.filter(function(r) { return r.floorKey === 'floor:2'; })[0];

  var bfr = window.ObjectAgg.byFloorRole();
  var bF1gfa = (bfr['floor:1'] && bfr['floor:1'].gfa && bfr['floor:1'].gfa.area) || 0;
  var bF1ded = (bfr['floor:1'] && bfr['floor:1'].ded && bfr['floor:1'].ded.area) || 0;
  var bF2gfa = (bfr['floor:2'] && bfr['floor:2'].gfa && bfr['floor:2'].gfa.area) || 0;
  var bF2ded = (bfr['floor:2'] && bfr['floor:2'].ded && bfr['floor:2'].ded.area) || 0;

  /* ---- (i) three-way convergence + M6 root-layer inclusion ---- */
  var rootIncludedInReview  = !!(rF1 && close(rF1.gross, expF1Gross) && close(rF1.net, expF1Net));
  var rootIncludedInSummary = !!(sF1 && close(sF1.gfa, expF1Gross) && close(sF1.net, expF1Net));
  var rootIncludedInTuple   = close(bF1gfa, expF1Gross) && close(bF1ded, expF1Ded);

  var threeWayF1 = !!(rF1 && sF1 &&
    close(rF1.gross, sF1.gfa) && close(rF1.gross, bF1gfa) &&
    close(rF1.ded, sF1.ded)   && close(rF1.ded, bF1ded) &&
    close(rF1.net, sF1.net)   && close(rF1.net, expF1Net));
  var threeWayF2 = !!(rF2 && sF2 &&
    close(rF2.gross, sF2.gfa) && close(rF2.gross, bF2gfa) && close(rF2.gross, expF2Gross) &&
    close(rF2.ded, sF2.ded)   && close(rF2.ded, bF2ded)   && close(rF2.ded, expF2Ded) &&
    close(rF2.net, sF2.net)   && close(rF2.net, expF2Net));

  /* ---- (ii) _ltOwnArea regression guard (tuple path vs legacy loop) ----
     _ltOwnAreaLegacyLoop() itself is UNSIGNED (sign is applied by the
     caller, _ltOwnArea) -- so the comparator must apply the same
     role==='ded' -> -1 sign rule the real _ltOwnArea uses internally. */
  function signOf(id) { return (layerById(id).role === 'ded') ? -1 : 1; }
  var ownF1GfaNew = _ltOwnArea(f1Gfa.id),   ownF1GfaOld = signOf(f1Gfa.id)   * _ltOwnAreaLegacyLoop(f1Gfa.id);
  var ownF2DedNew = _ltOwnArea(f2Ded.id),   ownF2DedOld = signOf(f2Ded.id)   * _ltOwnAreaLegacyLoop(f2Ded.id);
  var ownRootNew  = _ltOwnArea(rootGfa.id), ownRootOld  = signOf(rootGfa.id) * _ltOwnAreaLegacyLoop(rootGfa.id);
  var ltOwnAreaRegressionOk = !!(
    close(ownF1GfaNew, ownF1GfaOld) && close(ownF1GfaNew, 500) &&
    close(ownF2DedNew, ownF2DedOld) && close(ownF2DedNew, -40) &&
    close(ownRootNew, ownRootOld)   && close(ownRootNew, 80)
  );

  /* ---- (iii) oracle end-to-end ---- */
  var oracle = window.ObjectAgg.assertEnginesAgree();
  var oracleOk = !!(oracle && oracle.ok);

  if (_origCaseId !== undefined) caseId = _origCaseId;

  return {
    rootIncludedInReview, rootIncludedInSummary, rootIncludedInTuple,
    threeWayF1, threeWayF2, ltOwnAreaRegressionOk, oracleOk,
    _rF1: rF1, _sF1: sF1, _bF1gfa: bF1gfa, _bF1ded: bF1ded,
    _rF2: rF2, _sF2: sF2, _bF2gfa: bF2gfa, _bF2ded: bF2ded,
    _oracleDiffs: oracle && oracle.diffs,
    _ownF1GfaNew: ownF1GfaNew, _ownF1GfaOld: ownF1GfaOld,
    _ownF2DedNew: ownF2DedNew, _ownF2DedOld: ownF2DedOld,
    _ownRootNew: ownRootNew, _ownRootOld: ownRootOld,
    pass: rootIncludedInReview && rootIncludedInSummary && rootIncludedInTuple &&
      threeWayF1 && threeWayF2 && ltOwnAreaRegressionOk && oracleOk
  };
}
"""

CHECKS = [
    ("b2SingleEngine", SC_B2, ["pass"]),
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
        time.sleep(0.8)

        print()
        print("LITE-B2-SINGLE-ENGINE checks:")
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
        print("LITE_B2_SINGLE_ENGINE_FAIL")
        sys.exit(1)
    else:
        print("LITE_B2_SINGLE_ENGINE_OK")


if __name__ == "__main__":
    main()
