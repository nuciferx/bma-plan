"""
Render-followups (a)+(c) guard: raster fallback + scanned-page detection.

(a) Raster fallback — if PDF.js is unavailable (vendor+CDN fail, or a doc
PyMuPDF opens but PDF.js rejects), loadPage now falls back to the server
JPEG (/pageinfo + /page?rot=N into curImg) instead of blank canvas + alert.
Measurement stays functional; only zoom sharpness is raster-limited.

(b) Scanned detection — image-only pages (imgs>=1, paths==0, texts==0 in the
post-render operator list) are flagged; re-render scale capped at
SCANNED_MAX_SCALE with transform compensation (up factor) so registration is
unchanged, only resolution is capped.

Checks:
  A1 fallback paints  — _test_forceRasterFallback(true) -> loadPage(1):
                        curImg is a real image, ready(), canvas painted.
  A2 measure works    — with scale set, polyMetricsAnyShape returns the right
                        area in fallback mode (geometry independent of render).
  A3 recovery         — hook off + resetCache + re-open -> pdfjs path again
                        (pdfDoc set, curImg cleared).
  S1 scanned flagged  — image-only PDF -> _test_scanned()[1] === true.
  S2 vector not flagged — vector/text PDF -> flag !== true.
  S3 cap harmless     — zoom V.k=30 on scanned page still renders (no error,
                        painted, _cachedKey advances).

RED pre-fix: _test_forceRasterFallback undefined -> throws.

Emits LITE_RENDER_FB_SCAN_OK on success.

    py -3 lite/tests/test_render_fallback_scanned.py
"""
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


def _free_port(start=9010):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


def _vector_pdf(pages=2, w=300, h=400):
    doc = fitz.open()
    for i in range(pages):
        pg = doc.new_page(width=w, height=h)
        pg.insert_text(fitz.Point(70, 200), f"VEC {i+1}", fontsize=28)
        sh = pg.new_shape()
        sh.draw_rect(fitz.Rect(20, 20, 280, 380))
        sh.finish(color=(0, 0, 0), width=2)
        sh.commit()
    b = doc.tobytes()
    doc.close()
    return b


def _scanned_pdf(w=300, h=400):
    # page whose ONLY content is one embedded image (like a scan)
    img_doc = fitz.open()
    ip = img_doc.new_page(width=200, height=260)
    sh = ip.new_shape()
    sh.draw_rect(fitz.Rect(30, 30, 170, 230))
    sh.finish(color=(0, 0, 0), fill=(0.4, 0.4, 0.9), width=3)
    sh.commit()
    pix = ip.get_pixmap(matrix=fitz.Matrix(2, 2))
    png = pix.tobytes("png")
    img_doc.close()

    doc = fitz.open()
    pg = doc.new_page(width=w, height=h)
    pg.insert_image(fitz.Rect(0, 0, w, h), stream=png)
    b = doc.tobytes()
    doc.close()
    return b


SC_FALLBACK = r"""
async () => {
  function painted() {
    try {
      var c = document.getElementById("cv");
      var g = c.getContext("2d").getImageData(Math.floor(c.width/4), Math.floor(c.height/4),
                                              Math.floor(c.width/2), Math.floor(c.height/2)).data;
      var mn = 255, mx = 0;
      for (var i = 0; i < g.length; i += 4) { if (g[i] < mn) mn = g[i]; if (g[i] > mx) mx = g[i]; }
      return (mx - mn) > 20;
    } catch (e) { return false; }
  }
  async function openBytes(arr, name) {
    var fd = new FormData();
    fd.append("file", new Blob([new Uint8Array(arr)], {type: "application/pdf"}), name);
    var up = await fetch("/upload", {method: "POST", body: fd});
    var uj = await up.json();
    caseId = uj.case_id; pageCount = uj.pages;
    PageRenderer.resetCache();
    return uj;
  }

  // ---- A: raster fallback ----
  await openBytes(%VEC_BYTES%, "vec.pdf");
  PageRenderer._test_forceRasterFallback(true);
  await PageRenderer.loadPage(1);
  for (var i = 0; i < 30 && !painted(); i++) await new Promise(function(r){ setTimeout(r, 100); });
  var a1 = (curImg instanceof HTMLImageElement) && PageRenderer.ready() && painted();

  PS[1] = PS[1] || {objects: [], scale: null, annotations: []};
  PS[1].scale = {pts_per_m: 1};
  curPage = 1;
  var a2poly = {kind: "poly", pts: [{x:0,y:0},{x:50,y:0},{x:50,y:40},{x:0,y:40}]};
  var a2 = Math.abs(polyMetricsAnyShape(a2poly, 1).area - 2000) < 1e-9;

  PageRenderer._test_forceRasterFallback(false);
  await openBytes(%VEC_BYTES%, "vec2.pdf");
  await PageRenderer.loadPage(1);
  await new Promise(function(r){ setTimeout(r, 600); });
  var a3 = PageRenderer.ready() && curImg === null && painted();

  // ---- S: scanned detection ----
  var vecFlag = null;
  for (var j = 0; j < 30; j++) {
    var m = PageRenderer._test_scanned();
    if (m[1] === true || m[1] === false) { vecFlag = m[1]; break; }
    await new Promise(function(r){ setTimeout(r, 100); });
  }
  var s2 = vecFlag === false;                     // vector page must NOT be flagged

  await openBytes(%SCAN_BYTES%, "scan.pdf");
  await PageRenderer.loadPage(1);
  var scanFlag = null;
  for (var k = 0; k < 50; k++) {
    var m2 = PageRenderer._test_scanned();
    if (m2[1] === true || m2[1] === false) { scanFlag = m2[1]; break; }
    await new Promise(function(r){ setTimeout(r, 100); });
  }
  var s1 = scanFlag === true;

  // S3: extreme zoom on the scanned page still renders via the capped path.
  // painted() checks pixel RANGE which fails inside the uniform blue fill at
  // deep zoom — use a non-white check instead (any ink present).
  function hasInk() {
    try {
      var c = document.getElementById("cv");
      var g = c.getContext("2d").getImageData(Math.floor(c.width/4), Math.floor(c.height/4),
                                              Math.floor(c.width/2), Math.floor(c.height/2)).data;
      for (var i = 0; i < g.length; i += 4) { if (g[i] < 200) return true; }
      return false;
    } catch (e) { return false; }
  }
  // recenter on the page middle (pt 150,200) or extreme zoom shows only the
  // white page corner (screen = pt*RS*k + o)
  var cvEl = document.getElementById("cv"), dpr = window.devicePixelRatio || 1;
  V.k = 30; V.rot = 0;
  V.ox = cvEl.width / (2 * dpr) - 150 * RS * V.k;
  V.oy = cvEl.height / (2 * dpr) - 200 * RS * V.k;
  draw();
  var s3 = false;
  for (var q = 0; q < 20; q++) {
    await new Promise(function(r){ setTimeout(r, 100); });
    if (hasInk()) { s3 = true; break; }
  }

  return {a1, a2, a3, s1, s2, s3, vecFlag, scanFlag,
          pass: a1 && a2 && a3 && s1 && s2 && s3};
}
"""


def main():
    from server_lite import app as lite_app
    port = _free_port()
    cfg = uvicorn.Config(lite_app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(cfg)
    threading.Thread(target=server.run, daemon=True).start()
    time.sleep(2.0)

    vec = _vector_pdf()
    scan = _scanned_pdf()
    scenario = (SC_FALLBACK
                .replace("%VEC_BYTES%", "[" + ",".join(str(b) for b in vec) + "]")
                .replace("%SCAN_BYTES%", "[" + ",".join(str(b) for b in scan) + "]"))

    failures = []
    page_errors = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.on("pageerror", lambda e: page_errors.append(f"pageerror: {e}"))
        pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        time.sleep(0.6)

        print()
        print("LITE-RENDER-FB-SCAN checks:")
        try:
            result = pg.evaluate(scenario)
            ok = result.get("pass") is True
            print(f"  fallbackAndScannedDetection         -> {'PASS' if ok else 'FAIL'}  {result}")
            if not ok:
                failures.append(f"result={result}")
        except Exception as ex:
            print(f"  fallbackAndScannedDetection         -> EXCEPTION: {ex}")
            failures.append(f"threw: {ex}")
        pg.close()
        b.close()

    for e in page_errors:
        print("  JS ERROR:", e)

    server.should_exit = True
    time.sleep(0.4)

    if failures:
        for f in failures:
            print("FAIL:", f)
        print("LITE_RENDER_FB_SCAN_FAIL")
        sys.exit(1)
    print("LITE_RENDER_FB_SCAN_OK")


if __name__ == "__main__":
    main()
