"""
INV-2026-05-24-002b: test_centerline_snap.py
Verifies centerline snap for BMA-Plan Lite (mirrors proto INV-2026-05-24-002a).

Six sub-checks (all must be True for PASS):
  1. fnsExist         — CL_snapCanvasToCenterline + CL_refineCornersOnSkeleton present
  2. versionExists    — CL_VERSION is a string
  3. liteFnsExist     — CL_litePolyClick + CL_litePolyFinish present
  4. buttonExists     — #lite-btn-centerline injected into DOM
  5. defaultOff       — centerlineSnapOn === false on fresh load
  6. accuracy         — synthetic dashed-pentagon: max|delta_area| <= 0.5% of GT

Emits LITE_CENTERLINE_SNAP_OK on success.

    py -3 lite/tests/test_centerline_snap.py
"""
import socket
import threading
import time
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8570):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


# ---------------------------------------------------------------------------
# SC1-5: presence + state checks (single evaluate)
# ---------------------------------------------------------------------------
SC_PRESENCE = """
() => {
  return {
    fnsExist:    typeof window.CL_snapCanvasToCenterline === 'function' &&
                 typeof window.CL_refineCornersOnSkeleton === 'function',
    versionExists: typeof window.CL_VERSION === 'string',
    liteFnsExist: typeof window.CL_litePolyClick === 'function' &&
                  typeof window.CL_litePolyFinish === 'function',
    buttonExists: !!document.getElementById('lite-btn-centerline'),
    defaultOff:   window.centerlineSnapOn === false
  };
}
"""

# ---------------------------------------------------------------------------
# SC6: accuracy — synthetic dashed pentagon (mirrors proto E2E test body)
# Creates an offscreen canvas, draws a dashed regular pentagon, then runs
# CL_snapCanvasToCenterline + CL_refineCornersOnSkeleton on GT / outer /
# inner / center vertex traces, computes polygon area, checks max |delta| <=
# 0.5% of GT_AREA.
# ---------------------------------------------------------------------------
SC_ACCURACY = """
() => {
  // ---- helpers ----
  function polyArea(pts) {
    var area = 0, n = pts.length;
    for (var i = 0; i < n; i++) {
      var j = (i + 1) % n;
      area += pts[i][0] * pts[j][1] - pts[j][0] * pts[i][1];
    }
    return Math.abs(area) / 2;
  }

  function snapPoly(ctx, pts) {
    return pts.map(function(p) {
      var r = window.CL_snapCanvasToCenterline(ctx, p[0], p[1]);
      return r.found ? [r.x, r.y] : p;
    });
  }

  function refinePoly(ctx, pts) {
    var res = window.CL_refineCornersOnSkeleton(ctx, pts);
    return res.refined ? res.pts : pts;
  }

  // ---- build offscreen canvas with a dashed pentagon ----
  var W = 800, H = 600;
  var oc = document.createElement('canvas');
  oc.width = W; oc.height = H;
  var octx = oc.getContext('2d');
  octx.fillStyle = '#fff';
  octx.fillRect(0, 0, W, H);

  var cx = W / 2, cy = H / 2;
  var R = 180;   // pentagon circumradius (px)
  var LINE_W = 6;

  // Generate 5 vertices of a regular pentagon.
  var gtPts = [];
  for (var i = 0; i < 5; i++) {
    var angle = (2 * Math.PI * i / 5) - Math.PI / 2;
    gtPts.push([cx + R * Math.cos(angle), cy + R * Math.sin(angle)]);
  }
  var GT_AREA = polyArea(gtPts);

  // Draw the pentagon as a dashed line (to simulate typical dashed plan boundary).
  octx.strokeStyle = '#000';
  octx.lineWidth = LINE_W;
  octx.setLineDash([12, 8]);
  octx.beginPath();
  gtPts.forEach(function(p, i) {
    i === 0 ? octx.moveTo(p[0], p[1]) : octx.lineTo(p[0], p[1]);
  });
  octx.closePath();
  octx.stroke();
  octx.setLineDash([]);

  // ---- test traces: outer (+LINE_W/2), inner (-LINE_W/2), center (GT) ----
  var offset = LINE_W / 2;
  function offsetPoly(pts, d) {
    // simple radial offset from centroid
    var mcx = 0, mcy = 0;
    pts.forEach(function(p) { mcx += p[0]; mcy += p[1]; });
    mcx /= pts.length; mcy /= pts.length;
    return pts.map(function(p) {
      var dx = p[0] - mcx, dy = p[1] - mcy;
      var len = Math.sqrt(dx*dx + dy*dy) || 1;
      return [p[0] + dx/len*d, p[1] + dy/len*d];
    });
  }

  var traces = {
    gt:    gtPts,
    outer: offsetPoly(gtPts,  offset),
    inner: offsetPoly(gtPts, -offset),
    center: gtPts   // same as gt for this test
  };

  var results = {};
  var maxDelta = 0;
  var allPass = true;

  Object.keys(traces).forEach(function(name) {
    var pts = traces[name];
    var snapped  = snapPoly(octx, pts);
    var refined  = refinePoly(octx, snapped);
    var area     = polyArea(refined);
    var delta    = Math.abs(area - GT_AREA) / GT_AREA * 100;  // %
    maxDelta     = Math.max(maxDelta, delta);
    results[name] = { area: area, delta_pct: delta };
    if (delta > 0.5) allPass = false;
  });

  return {
    GT_AREA:  GT_AREA,
    maxDelta: maxDelta,
    results:  results,
    accuracy: allPass
  };
}
"""


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
        base_url = f"http://127.0.0.1:{port}/"
        pg.goto(base_url, wait_until="networkidle")
        time.sleep(0.8)

        print()
        print("INV-2026-05-24-002b centerline snap checks:")

        # ---- SC1-5: presence + state ----
        name = "presence+state (fnsExist/versionExists/liteFnsExist/buttonExists/defaultOff)"
        try:
            r = pg.evaluate(SC_PRESENCE)
            sub_checks = ["fnsExist", "versionExists", "liteFnsExist", "buttonExists", "defaultOff"]
            sub_ok = all(r.get(k) is True for k in sub_checks)
            print(f"  {'presence+state':46s} -> {'PASS' if sub_ok else 'FAIL'}  {r}")
            if not sub_ok:
                for k in sub_checks:
                    if not r.get(k):
                        failures.append(f"sub-check '{k}' = {r.get(k)}")
        except Exception as ex:
            print(f"  {'presence+state':46s} -> EXCEPTION: {ex}")
            failures.append(f"presence+state threw: {ex}")

        # ---- SC6: accuracy ----
        name = "accuracy (dashed-pentagon maxDelta <= 0.5%)"
        try:
            r = pg.evaluate(SC_ACCURACY)
            ok = r.get("accuracy") is True
            print(f"  {name:46s} -> {'PASS' if ok else 'FAIL'}  maxDelta={r.get('maxDelta', '?'):.4f}%  {r.get('results', {})}")
            if not ok:
                failures.append(f"accuracy FAIL: maxDelta={r.get('maxDelta')}% (limit 0.5%)")
        except Exception as ex:
            print(f"  {name:46s} -> EXCEPTION: {ex}")
            failures.append(f"accuracy threw: {ex}")

        pg.close()
        b.close()

    for e in page_errors:
        print("  JS ERROR:", e)

    server.should_exit = True
    time.sleep(0.4)

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_CENTERLINE_SNAP_FAIL")
        sys.exit(1)
    else:
        print("LITE_CENTERLINE_SNAP_OK")


if __name__ == "__main__":
    main()
