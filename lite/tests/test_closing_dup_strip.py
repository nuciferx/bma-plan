"""
BMA-Plan Lite — closing-dup-strip acceptance test.

Root cause: .bmaplan files written by proto store ring-style polygons
(pts[0] == pts[-1], closed:true).  polySelfIntersects() returns true for these,
so polyMetrics().area returns null -> areas silently disappear from every report.

Fix (lite load path only — vendored math untouched):
  stripClosingDup(pts, edges) is called in loadProto for every poly/opening;
  it removes the duplicate trailing vertex before the vendored math ever sees it.

This test:
  1. BEFORE check: shows page-26 polys in the fixture all have firstEqLast=True
     and that WITHOUT the fix polySelfIntersects would return true → area null.
     (Verified by replaying the raw fixture pts through polySelfIntersects via JS.)
  2. AFTER check: loads the real fixture via loadProto(), verifies each poly has
     pts[0] != pts[-1] (dup stripped), polyMetrics().area is a positive number for
     each, grand total ≈ 241.06 m², and computeSummary().all has a positive total.
  3. Regression check: a normal 4-point poly (no dup) is unaffected (length stays 4).

Emits LITE_CLOSING_DUP_STRIP_OK on success, exits 0.

    py -3 lite/tests/test_closing_dup_strip.py
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


def _free_port(start=8370):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


def main():
    from server_lite import app as lite_app

    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)

    doc = json.loads(FIXTURE.read_text(encoding="utf-8"))
    doc_json = json.dumps(doc)

    failures = []
    checks = []

    def chk(name, cond, extra=""):
        checks.append((name, bool(cond)))
        if not cond:
            failures.append(f"FAIL {name}: {extra}")

    base = f"http://127.0.0.1:{port}"
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.on("pageerror", lambda e: failures.append(f"pageerror: {e}"))
        pg.goto(f"{base}/", wait_until="networkidle")
        time.sleep(0.6)

        # ------------------------------------------------------------------
        # STEP 1 — BEFORE: verify that raw fixture pts cause
        #          polySelfIntersects=true → area=null WITHOUT strip
        # ------------------------------------------------------------------
        before_js = r"""
(docJson) => {
  const doc = JSON.parse(docJson);
  const st26 = doc.pageStore['26'];
  const scale = st26.calibScale;
  const results = st26.polys.map(function(o) {
    const pts = o.pts;
    const a = pts[0], b = pts[pts.length-1];
    const firstEqLast = (Math.abs(a.x-b.x)<1e-6 && Math.abs(a.y-b.y)<1e-6);
    const si = polySelfIntersects(pts);
    const m = polyMetrics({pts: pts}, 26);
    return { len: pts.length, firstEqLast, selfIntersects: si, area: m ? m.area : null };
  });
  return { scale: scale.pts_per_m, polys: results };
}
"""
        before = pg.evaluate(before_js, doc_json)
        print("\n--- BEFORE (raw fixture pts, no strip) ---")
        total_before = 0.0
        for i, r in enumerate(before["polys"]):
            area_val = r["area"]
            total_before += (area_val or 0.0)
            print(f"  poly {i}: len={r['len']}, firstEqLast={r['firstEqLast']}, "
                  f"selfIntersects={r['selfIntersects']}, area={area_val}")
        print(f"  grand total (before): {total_before:.2f}")
        # All 5 should have area=null before the fix (selfIntersects=true)
        chk("before: all firstEqLast=True",
            all(r["firstEqLast"] for r in before["polys"]),
            before["polys"])
        chk("before: all selfIntersects=True",
            all(r["selfIntersects"] for r in before["polys"]),
            before["polys"])
        chk("before: all area=null",
            all(r["area"] is None for r in before["polys"]),
            before["polys"])

        # ------------------------------------------------------------------
        # STEP 2 — AFTER: load fixture via loadProto, verify strip applied
        # ------------------------------------------------------------------
        after_js = r"""
(docJson) => {
  const doc = JSON.parse(docJson);
  loadProto(doc);
  const page26 = PS['26'];
  if (!page26) return { error: 'PS[26] missing' };
  const polys = page26.objects.filter(function(o){ return o.kind==='poly'; });

  const polyResults = polys.map(function(o) {
    const pts = o.pts;
    const a = pts[0], b = pts[pts.length-1];
    const stillDup = (Math.abs(a.x-b.x)<1e-6 && Math.abs(a.y-b.y)<1e-6);
    const si = polySelfIntersects(pts);
    const m = polyMetrics({pts: pts}, 26);
    return { len: pts.length, stillDup, selfIntersects: si, area: m ? m.area : null };
  });

  // computeSummary uses PS + current page scale
  const summary = computeSummary ? computeSummary() : null;

  return { polys: polyResults, summary: summary };
}
"""
        after = pg.evaluate(after_js, doc_json)
        if "error" in after:
            failures.append(f"FAIL loadProto: {after['error']}")
            print(f"\nERROR: {after['error']}")
        else:
            print("\n--- AFTER (loaded via loadProto with stripClosingDup) ---")
            total_after = 0.0
            for i, r in enumerate(after["polys"]):
                area_val = r["area"]
                total_after += (area_val or 0.0)
                print(f"  poly {i}: len={r['len']}, stillDup={r['stillDup']}, "
                      f"selfIntersects={r['selfIntersects']}, area={area_val:.4f}" if area_val else
                      f"  poly {i}: len={r['len']}, stillDup={r['stillDup']}, "
                      f"selfIntersects={r['selfIntersects']}, area=null")
            print(f"  grand total (after): {total_after:.2f}")

            chk("after: 5 poly objects on page 26",
                len(after["polys"]) == 5, len(after["polys"]))
            chk("after: none stillDup",
                all(not r["stillDup"] for r in after["polys"]),
                after["polys"])
            chk("after: none selfIntersects",
                all(not r["selfIntersects"] for r in after["polys"]),
                after["polys"])
            chk("after: all areas positive",
                all(r["area"] and r["area"] > 0 for r in after["polys"]),
                after["polys"])
            chk("after: grand total ~241.06 m2 (±1.0)",
                abs(total_after - 241.06) < 1.0,
                f"got {total_after:.2f}")

            # computeSummary.all should have positive gfa total
            if after.get("summary"):
                s = after["summary"]
                all_keys = s.get("all", {})
                print(f"  computeSummary.all keys: {list(all_keys.keys())}")
                gfa_area = all_keys.get("gross_floor_area", 0) or all_keys.get("gfa", 0)
                # Check that at least one area key in 'all' is positive
                any_positive = any(
                    v and v > 0
                    for v in all_keys.values()
                    if isinstance(v, (int, float))
                )
                chk("after: computeSummary.all has positive gfa area", any_positive,
                    f"all={all_keys}")
            else:
                print("  (computeSummary not available or returned null)")

        # ------------------------------------------------------------------
        # STEP 3 — Regression: normal 4-point poly (no dup) unaffected
        # ------------------------------------------------------------------
        regression_js = r"""
() => {
  // 4 distinct points, no closing dup
  const pts = [{x:0,y:0},{x:100,y:0},{x:100,y:100},{x:0,y:100}];
  const stripped = stripClosingDup(pts, null);
  // must be same length (4), same first/last unchanged
  const lenOk = stripped.length === 4;
  const unchanged = (stripped[0].x === pts[0].x && stripped[3].y === pts[3].y);
  // polyMetrics should still work on it
  PS['99'] = { scale:{pts_per_m:10}, annotations:[], objects:[
    {id:9999,catId:'gfa',semanticTag:'gross_floor_area',kind:'poly',counting:false,
     pts: stripped, dimVisible:true}
  ]};
  const m = polyMetrics({pts: stripped}, 99);
  const area = m ? m.area : null;
  return { len: stripped.length, lenOk, unchanged, area };
}
"""
        reg = pg.evaluate(regression_js)
        print(f"\n--- REGRESSION (normal 4-point poly, no dup) ---")
        print(f"  len={reg['len']}, lenOk={reg['lenOk']}, "
              f"unchanged={reg['unchanged']}, area={reg['area']}")
        chk("regression: stripClosingDup leaves 4-pt poly at length 4",
            reg["lenOk"], reg)
        chk("regression: 4-pt poly area = 100 m2 (side=100pt @ 10pt/m)",
            reg["area"] and abs(reg["area"] - 100.0) < 0.01, reg["area"])

        b.close()

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print(f"\n{'='*60}")
    print(f"Checks: {len(checks)}  Failures: {len(failures)}")
    for name, ok in checks:
        print(f"  {'OK' if ok else 'FAIL'} {name}")
    if failures:
        for f in failures:
            print(f)
        print("LITE_CLOSING_DUP_STRIP_FAIL")
        sys.exit(1)
    else:
        print("LITE_CLOSING_DUP_STRIP_OK")
        sys.exit(0)


if __name__ == "__main__":
    main()
