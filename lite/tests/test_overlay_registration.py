"""
Raster <-> overlay registration test (render-followups card (e) — the missing
evidence from the 2026-05-28 render-quality spike).

WHAT THIS PROVES (that ptToScreen math alone can't): a measurement drawn at
known PDF-pt coordinates lands ON the raster feature at those coordinates in
the actual rendered canvas bitmap — i.e. the PDF.js raster pipeline
(_offCanvas render + diff-blit in page-renderer.js) and the overlay pipeline
(ptToScreen + ctx.stroke in ui-lite.html draw()) agree, across zoom and
pageRot.

METHOD:
  1. Synthetic PDF: white 300x400 pt page, THICK (3 pt) pure-black rectangle
     border at exactly (60,80)-(240,320), nothing else.
  2. Upload via the real /upload endpoint, open in the live app (Playwright),
     PageRenderer.loadPage(1), inject a poly whose pts are exactly the
     rectangle corners on catId 'ded' (#ff6b6b — red, maximally distinct from
     the black raster), PS[1].scale={pts_per_m:1}.
  3. Wait for the PDF.js render to settle by polling the renderer's own
     up-to-date condition: _pendingRenderTask === null && _cachedKey ===
     _stateKey()  (both are top-level vars in page-renderer.js -> globals).
  4. draw() synchronously, getImageData, then for each of the 4 edges sample
     a perpendicular scan line at t = 0.25 / 0.5 / 0.75 along the edge
     (>=45 pt away from corners so adjacent edges never enter the window).
     Along the scan (+-W device px, 1 px steps) classify pixels:
       black raster  : r,g,b all < 100        (anti-aliased edge grays excluded)
       red overlay   : r > 150 && r-g > 60 && r-b > 60
     The 16%%-alpha red FILL over white is (255,~231,~231) -> NOT classified
     red (r-g = 24); fill over black is (~41,~17,~17) -> classified black.
     Registration metric: |centroid(red) - centroid(red UNION black)|.
     (The opaque red stroke covers the middle of the black band when
     registered, so the union reconstructs the full raster band.)
  5. Assert per sample: red found AND black found in the window (gross
     detachment -> red simply absent -> FAIL), and offset <= N device px.
  6. Repeat at: zoom fit, V.k*2 (zoomCenter(2), re-settled), and
     pageRot[1]=90 + fit() (raster rotates via PDF.js viewport rotation;
     overlay rotates via the vendored pdfToC pgRot branch — they must agree).

TOLERANCE N = 3 + ceil(devicePixelRatio) device px. Justification:
  +-0.5 px quantization on each centroid (red / band)         ~ 1 px
  asymmetric anti-alias misclassification at band/stroke edges ~ 1 px
  PDF.js raster grid vs canvas stroke grid half-pixel phase    ~ 0.5 px
  dpr rounding of the CSS->device mapping                      ~ ceil(dpr)
  headroom so AA jitter never flakes                           ~ 0.5 px
  At headless dpr=1 -> N=4 device px ~= 2.4 pt at fit zoom; the zoom-x2
  scenario tightens the same N to ~1.2 pt. A real misregistration (e.g. a
  pgRot branch mismatch) lands the stroke either outside the +-W window
  (red absent) or several band-widths off — far beyond N.

Emits LITE_OVERLAY_REG_OK on success.

    py -3 lite/tests/test_overlay_registration.py
"""
import math
import socket
import sys
import threading
import time
from pathlib import Path

LITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LITE))

import fitz
import uvicorn
from playwright.sync_api import sync_playwright


def _free_port(start=8720):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


def _make_pdf_bytes():
    """White 300x400 pt page with a 3 pt pure-black rect border at
    (60,80)-(240,320). fitz page space is top-left-origin y-down, which is
    the same frame the app's PDF-pt geometry uses (the old server JPEGs came
    from fitz get_pixmap), so poly pts == draw_rect corners with no flip."""
    doc = fitz.open()
    pg = doc.new_page(width=300, height=400)
    pg.draw_rect(fitz.Rect(60, 80, 240, 320), color=(0, 0, 0), width=3)
    b = doc.tobytes()
    doc.close()
    return b


JS_JOURNEY = r"""
async (pdfBytes) => {
  var out = {scenarios: [], fatal: null};
  try {
    // ---- upload via the real endpoint ----
    var arr  = new Uint8Array(pdfBytes);
    var blob = new Blob([arr], {type: 'application/pdf'});
    var file = new File([blob], 'overlay-reg-fixture.pdf', {type: 'application/pdf'});
    var fd   = new FormData();
    fd.append('file', file);
    var res  = await fetch('/upload', {method: 'POST', body: fd});
    var json = await res.json();
    if (json.error) return {fatal: 'upload: ' + json.error};

    // Mirror uploadPdf() global setup (same pattern as test_pdfjs_offline.py)
    caseId    = json.case_id;
    pdfName   = json.name;
    pageCount = json.pages;
    PS        = {};
    excluded  = {};
    PageRenderer.resetCache();
    curPage   = 1;

    var alerts = [];
    window.alert = function (m) { alerts.push(String(m)); };
    await PageRenderer.loadPage(1);
    if (alerts.length) return {fatal: 'alert during loadPage: ' + alerts.join('; ')};
    if (!cv.width || !cv.height) PageRenderer.resize();
    if (!cv.width || !cv.height) return {fatal: 'canvas has zero size'};

    // ---- inject overlay poly at EXACTLY the raster rect corners ----
    PS[1] = {
      objects: [{id: 1, catId: 'ded', semanticTag: 'deduction_opening',
                 kind: 'poly', counting: false,
                 pts: [{x:60,y:80},{x:240,y:80},{x:240,y:320},{x:60,y:320}]}],
      scale: {pts_per_m: 1},
      annotations: []
    };

    var dpr = window.devicePixelRatio || 1;

    // Renderer's own up-to-date condition (page-renderer.js globals).
    async function settle() {
      for (var i = 0; i < 120; i++) {
        if (_pendingRenderTask === null && _cachedKey === _stateKey()) return true;
        draw();  // schedules the re-render if the state key drifted
        await new Promise(function (r) { setTimeout(r, 50); });
      }
      return false;
    }

    function isBlack(d, i) { return d[i] < 100 && d[i+1] < 100 && d[i+2] < 100; }
    function isRed(d, i)   { return d[i] > 150 && (d[i] - d[i+1]) > 60 && (d[i] - d[i+2]) > 60; }

    async function sampleScenario(name, settled) {
      draw();  // synchronous: blit settled raster + stroke overlay, then read
      var img = ctx.getImageData(0, 0, cv.width, cv.height);
      var d = img.data, IW = cv.width, IH = cv.height;
      function idx(x, y) {
        x = Math.round(x); y = Math.round(y);
        if (x < 0 || y < 0 || x >= IW || y >= IH) return -1;
        return (y * IW + x) * 4;
      }
      var pts = [{x:60,y:80},{x:240,y:80},{x:240,y:320},{x:60,y:320}];
      // Window: half black band (1.5 pt) + generous slack; nearest OTHER edge
      // is >=160 pt away so the window can never catch a neighbour.
      var W = Math.ceil(3 * RS * V.k * dpr) + 12;
      var samples = [];
      for (var e = 0; e < 4; e++) {
        var a = pts[e], b = pts[(e + 1) % 4];
        for (var ti = 0; ti < 3; ti++) {
          var t = [0.25, 0.5, 0.75][ti];
          var p  = {x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t};
          var sP = ptToScreen(p);
          // At zoom-in the sample point may be OFF-SCREEN (page taller than
          // viewport). Pan it to the canvas center — pan preserves V.k so the
          // scenario still tests the zoomed render — then re-settle + re-read.
          var r = cv.getBoundingClientRect();
          var m = (W + 2) / dpr;  // CSS-px margin so the whole scan window fits
          if (sP.x < m || sP.y < m || sP.x > r.width - m || sP.y > r.height - m) {
            V.ox += (r.width / 2 - sP.x);
            V.oy += (r.height / 2 - sP.y);
            var okPan = await settle();
            if (!okPan) settled = false;
            draw();
            img = ctx.getImageData(0, 0, cv.width, cv.height);
            d = img.data; IW = cv.width; IH = cv.height;
            sP = ptToScreen(p);
          }
          var sA = ptToScreen(a), sB = ptToScreen(b);
          var cX = sP.x * dpr, cY = sP.y * dpr;          // device px
          var ex = sB.x - sA.x, ey = sB.y - sA.y, el = Math.hypot(ex, ey);
          var nx = -ey / el, ny = ex / el;               // unit perpendicular (screen space)
          var redPos = [], featPos = [];
          for (var s = -W; s <= W; s++) {
            var i = idx(cX + nx * s, cY + ny * s);
            if (i < 0) continue;
            var r0 = isRed(d, i), b0 = isBlack(d, i);
            if (r0) redPos.push(s);
            if (r0 || b0) featPos.push(s);
          }
          function mean(a2) { var s2 = 0; a2.forEach(function (v) { s2 += v; }); return s2 / a2.length; }
          var rec = {edge: e, t: t, nRed: redPos.length,
                     nBlack: featPos.length - redPos.length, off: null};
          if (redPos.length && featPos.length) {
            rec.redC  = mean(redPos);
            rec.featC = mean(featPos);
            rec.off   = Math.abs(rec.redC - rec.featC);
          }
          samples.push(rec);
        }
      }
      out.scenarios.push({name: name, dpr: dpr, k: V.k, rot: V.rot,
                          pgRot: pageRot[1] || 0, W: W, settled: settled,
                          cvw: cv.width, cvh: cv.height, samples: samples});
    }

    // ---- Scenario A: zoom fit, rot 0 ----
    var okA = await settle();
    await sampleScenario('fit', okA);

    // ---- Scenario B: V.k *= 2 (re-render settles at the new zoom) ----
    zoomCenter(2);
    var okB = await settle();
    await sampleScenario('zoom2x', okB);

    // ---- Scenario C: pageRot 90 (raster rotates via PDF.js viewport;
    //      overlay must follow via the vendored pdfToC pgRot branch) ----
    pageRot[1] = 90;
    PageRenderer.fit();
    var okC = await settle();
    await sampleScenario('pagerot90', okC);

    return out;
  } catch (ex) {
    return {fatal: String(ex && ex.stack || ex)};
  }
}
"""


failures = []


def check(label, cond, detail=""):
    if cond:
        print(f"  PASS {label}")
    else:
        msg = f"FAIL {label}" + (f": {detail}" if detail else "")
        failures.append(msg)
        print(f"  {msg}")


def main():
    from server_lite import app as lite_app
    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)
    base = f"http://127.0.0.1:{port}"

    pdf_bytes = _make_pdf_bytes()
    page_errors = []

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.on("pageerror", lambda e: page_errors.append(f"pageerror: {e}"))
        pg.goto(base + "/", wait_until="networkidle")
        time.sleep(0.8)

        print()
        print("LITE-OVERLAY-REGISTRATION checks:")
        try:
            result = pg.evaluate(JS_JOURNEY, list(pdf_bytes))
        except Exception as ex:
            result = {"fatal": f"evaluate threw: {ex}", "scenarios": []}

        pg.close()
        b.close()

    server.should_exit = True

    if result.get("fatal"):
        check("journey", False, result["fatal"])
    else:
        check("3 scenarios sampled", len(result["scenarios"]) == 3,
              f"got {len(result['scenarios'])}")
        for sc in result["scenarios"]:
            name = sc["name"]
            n_tol = 3 + math.ceil(sc["dpr"])  # see module docstring for justification
            check(f"{name}: render settled", sc["settled"] is True)
            offs = [s["off"] for s in sc["samples"] if s["off"] is not None]
            bad = []
            for s in sc["samples"]:
                where = f"edge{s['edge']}@t={s['t']}"
                if s["nRed"] == 0:
                    bad.append(f"{where}: overlay stroke NOT FOUND in +-{sc['W']}px window")
                elif s["nBlack"] == 0:
                    bad.append(f"{where}: raster band NOT FOUND in +-{sc['W']}px window")
                elif s["off"] > n_tol:
                    bad.append(f"{where}: off={s['off']:.2f}px > N={n_tol} "
                               f"(redC={s['redC']:.2f}, featC={s['featC']:.2f})")
            max_off = max(offs) if offs else float("nan")
            detail = "; ".join(bad[:6])
            check(f"{name}: 12/12 samples registered "
                  f"(k={sc['k']:.3f} dpr={sc['dpr']} pgRot={sc['pgRot']} "
                  f"maxOff={max_off:.2f}px N={n_tol})",
                  not bad, detail)

    for e in page_errors:
        print("  JS ERROR:", e)
        failures.append(e)

    time.sleep(0.4)

    if failures:
        print()
        for f in failures:
            print("FAIL:", f)
        print("LITE_OVERLAY_REG_FAIL")
        sys.exit(1)
    print()
    print("LITE_OVERLAY_REG_OK")


if __name__ == "__main__":
    main()
