"""
BUG-20260704-lite-native-rotate regression test.

Bug: the PDF.js render path (page-renderer.js) discarded native /Rotate
metadata baked into the PDF (page.set_rotation / /Rotate dict entry) — pages
with intrinsic rotation opened SIDEWAYS. Root cause: pdf.js's
`getViewport({rotation})` uses `this.rotate` (the page's intrinsic rotation)
ONLY when the `rotation` param is OMITTED; passing an EXPLICIT value (even 0)
REPLACES intrinsic rotation entirely rather than composing with it. Two call
sites passed an explicit value that ignored intrinsic /Rotate:
  - loadPage(): natVp = getViewport({scale:1, rotation:0})  -> returned the
    PRE-rotation mediabox dims for pageDims/origSize()/fit(), wrong whenever
    /Rotate != 0.
  - _render():  thetaUser = (Vsnap.rot + pgRot)              -> the actual
    raster was rendered with intrinsic /Rotate ignored (sideways), while the
    raster-fallback path (server fitz get_pixmap(), which applies /Rotate by
    default) rendered correctly — the two paths silently disagreed.

Fix: fold cp.rotate (intrinsic) into every composed rotation —
thetaTotal = cp.rotate + pgRot (user page-delta) + V.rot — and natVp uses
rotation: cp.rotate so pageDims reflects the POST-intrinsic-rotation dims,
matching the server's /pageinfo w_pt/h_pt (fitz page.rect, already
post-native-rotation, confirmed empirically below).

METHOD: fixture PDF = 300x400 pt page with a light-gray full-page background
fill (aspect/orientation proxy) + a solid black 60x60 pt marker near the
TOP-LEFT corner in the page's OWN un-rotated-authoring coordinate space
(quadrant proxy), with page.set_rotation(90) applied (native /Rotate=90).
Uploaded via the real /upload endpoint, opened via PageRenderer.loadPage in
the live app, canvas pixels sampled after the renderer's own settle
condition. Expected numbers below were independently verified via a raw
fitz get_pixmap() render of the identical fixture (see scratch calc in this
sprint's self-check) BEFORE writing the JS assertions, so this is not
guesswork:

  native90 fixture, pgRot=0 (total=90)   -> bbox LANDSCAPE (aspect~1.34>1),
                                             marker TOP-RIGHT (cxFrac~0.88,
                                             cyFrac~0.16). FAILS pre-fix:
                                             bbox portrait (aspect~0.75<1),
                                             marker TOP-LEFT (cxFrac~0.16).
  raster fallback (forced), same fixture -> AGREES with the PDF.js path.
  rotatePage(90) -> pgRot=90, total=180   -> bbox back to portrait
                                             (aspect<1, unswapped dims),
                                             marker BOTTOM-RIGHT
                                             (cxFrac~0.84, cyFrac~0.88).
  rotatePage(-90) -> pgRot=0, total=90    -> back to the native90 baseline.
  plain (non-rotated) fixture, pgRot=0   -> UNCHANGED: portrait bbox,
                                             marker TOP-LEFT (regression
                                             guard — fix must not alter
                                             /Rotate=0 PDFs; cp.rotate=0 is a
                                             no-op).
  pageDims[1] (PDF.js path) equals server /pageinfo w_pt/h_pt for the
                                             native90 fixture.

Emits LITE_NATIVE_ROTATE_OK on success.

    py -3 lite/tests/test_native_rotate.py
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


def _free_port(start=8760):
    for p in range(start, start + 60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    raise RuntimeError("no free port")


def _make_pdf_bytes(rotate=0):
    """300x400 pt page, light-gray full-page bg fill + solid black 60x60 pt
    marker near the TOP-LEFT corner (in the page's own un-rotated-authoring
    space). Optionally applies native page.set_rotation(rotate)."""
    doc = fitz.open()
    pg = doc.new_page(width=300, height=400)
    pg.draw_rect(fitz.Rect(0, 0, 300, 400), color=None, fill=(0.85, 0.85, 0.85))
    pg.draw_rect(fitz.Rect(20, 20, 80, 80), fill=(0, 0, 0))
    if rotate:
        pg.set_rotation(rotate)
    b = doc.tobytes()
    doc.close()
    return b


JS_JOURNEY = r"""
async ([native90Bytes, plainBytes]) => {
  var out = {stages: {}, fatal: null};
  try {
    // alpha>200 excludes the canvas's transparent margins (outside the fitted
    // page rect) — those read back as RGBA(0,0,0,0), which would otherwise be
    // misclassified as the black marker.
    function isBlack(d, i) { return d[i+3] > 200 && d[i] < 60 && d[i+1] < 60 && d[i+2] < 60; }
    function isGrayBg(d, i) {
      return d[i+3] > 200 && d[i] >= 180 && d[i] <= 245 &&
             Math.abs(d[i] - d[i+1]) < 15 && Math.abs(d[i] - d[i+2]) < 15;
    }

    async function uploadAndOpen(bytes, name) {
      var arr  = new Uint8Array(bytes);
      var blob = new Blob([arr], {type: 'application/pdf'});
      var file = new File([blob], name, {type: 'application/pdf'});
      var fd   = new FormData();
      fd.append('file', file);
      var res  = await fetch('/upload', {method: 'POST', body: fd});
      var json = await res.json();
      if (json.error) throw new Error('upload: ' + json.error);
      caseId    = json.case_id;
      pdfName   = json.name;
      pageCount = json.pages;
      PS = {}; excluded = {};
      PageRenderer.resetCache();
      curPage = 1;
      window.alert = function () {};
      await PageRenderer.loadPage(1);
      if (!cv.width || !cv.height) PageRenderer.resize();
      return json;
    }

    async function settle() {
      for (var i = 0; i < 120; i++) {
        if (!pdfDoc && curImg) return true;                        // raster-fallback ready
        if (_pendingRenderTask === null && _cachedKey === _stateKey()) return true;
        draw();
        await new Promise(function (r) { setTimeout(r, 50); });
      }
      return false;
    }

    function minMax(arr) {
      var lo = Infinity, hi = -Infinity;
      for (var i = 0; i < arr.length; i++) { if (arr[i] < lo) lo = arr[i]; if (arr[i] > hi) hi = arr[i]; }
      return [lo, hi];
    }

    function sampleMarker() {
      draw();
      var img = ctx.getImageData(0, 0, cv.width, cv.height);
      var d = img.data, IW = cv.width, IH = cv.height;
      var bgxs = [], bgys = [], mkxs = [], mkys = [];
      for (var y = 0; y < IH; y += 2) {
        for (var x = 0; x < IW; x += 2) {
          var i = (y * IW + x) * 4;
          var blk = isBlack(d, i), gray = isGrayBg(d, i);
          if (blk || gray) { bgxs.push(x); bgys.push(y); }
          if (blk) { mkxs.push(x); mkys.push(y); }
        }
      }
      if (!bgxs.length || !mkxs.length) return null;
      var bx = minMax(bgxs), by = minMax(bgys);
      var minx = bx[0], maxx = bx[1], miny = by[0], maxy = by[1];
      var bw = maxx - minx, bh = maxy - miny;
      var mx = minMax(mkxs), my = minMax(mkys);
      var mcx = (mx[0] + mx[1]) / 2, mcy = (my[0] + my[1]) / 2;
      return {
        aspect: bw / bh,
        cxFrac: (mcx - minx) / bw,
        cyFrac: (mcy - miny) / bh,
        nBg: bgxs.length, nMarker: mkxs.length
      };
    }

    // ---- Stage 1: native90 fixture, pgRot=0 (total=90) — the actual bug ----
    await uploadAndOpen(native90Bytes, 'native90.pdf');
    var pinfo = await (await fetch(api('/pageinfo/1'))).json();
    var okS1 = await settle();
    var s1 = sampleMarker();
    out.stages.s1_native90 = { settled: okS1, sample: s1,
      pageDims1: pageDims[1] ? {w: pageDims[1].w, h: pageDims[1].h} : null,
      pageinfo: {w: pinfo.w_pt, h: pinfo.h_pt} };

    // ---- Stage 2: raster fallback forced, SAME native90 case ----
    PageRenderer._test_forceRasterFallback(true);
    PageRenderer.resetCache();
    curPage = 1;
    await PageRenderer.loadPage(1);
    if (!cv.width || !cv.height) PageRenderer.resize();
    var okS2 = await settle();
    var s2 = sampleMarker();
    PageRenderer._test_forceRasterFallback(false);
    out.stages.s2_raster_fallback = { settled: okS2, sample: s2, usedRaster: !pdfDoc && !!curImg };

    // ---- Stage 3: re-open native90 via PDF.js, then rotatePage(90) (total=180) ----
    await uploadAndOpen(native90Bytes, 'native90.pdf');
    await settle();
    rotatePage(90);
    var okS3 = await settle();
    var s3 = sampleMarker();
    out.stages.s3_rotate90_total180 = { settled: okS3, sample: s3, pgRot: pageRot[1] };

    // ---- Stage 4: rotatePage(-90) back to pgRot=0 (total=90) ----
    rotatePage(-90);
    var okS4 = await settle();
    var s4 = sampleMarker();
    out.stages.s4_rotate_back = { settled: okS4, sample: s4, pgRot: pageRot[1] };

    // ---- Stage 5: plain (non-rotated) fixture — regression guard ----
    await uploadAndOpen(plainBytes, 'plain.pdf');
    var okS5 = await settle();
    var s5 = sampleMarker();
    out.stages.s5_plain_unrotated = { settled: okS5, sample: s5 };

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

    native90_bytes = _make_pdf_bytes(rotate=90)
    plain_bytes = _make_pdf_bytes(rotate=0)
    page_errors = []

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.on("pageerror", lambda e: page_errors.append(f"pageerror: {e}"))
        pg.goto(base + "/", wait_until="networkidle")
        time.sleep(0.8)

        print()
        print("LITE-NATIVE-ROTATE checks:")
        try:
            result = pg.evaluate(JS_JOURNEY, [list(native90_bytes), list(plain_bytes)])
        except Exception as ex:
            result = {"fatal": f"evaluate threw: {ex}", "stages": {}}

        pg.close()
        b.close()

    server.should_exit = True

    if result.get("fatal"):
        check("journey", False, result["fatal"])
    else:
        st = result["stages"]

        # ---- Stage 1: native90 fixture opens upright (the core bug) ----
        s1 = st.get("s1_native90", {})
        check("S1 settled", s1.get("settled") is True)
        d1 = s1.get("pageDims1") or {}
        pi = s1.get("pageinfo") or {}
        check("S1 pageDims[1] matches server /pageinfo (w_pt/h_pt)",
              bool(d1) and bool(pi) and abs(d1.get("w", -1) - pi.get("w", -2)) < 1.0
              and abs(d1.get("h", -1) - pi.get("h", -2)) < 1.0,
              f"pageDims={d1} pageinfo={pi}")
        smp1 = s1.get("sample")
        check("S1 sample found (bg+marker pixels)", smp1 is not None, str(s1))
        if smp1:
            check("S1 landscape aspect (native /Rotate=90 applied)", smp1["aspect"] > 1.05,
                  f"aspect={smp1['aspect']:.3f} (expect ~1.34 landscape; <1 = BUG: sideways/unrotated)")
            check("S1 marker top-right quadrant", smp1["cxFrac"] > 0.6 and smp1["cyFrac"] < 0.4,
                  f"cxFrac={smp1['cxFrac']:.3f} cyFrac={smp1['cyFrac']:.3f} (expect ~0.88,~0.16)")

        # ---- Stage 2: raster fallback agrees with PDF.js path ----
        s2 = st.get("s2_raster_fallback", {})
        check("S2 used raster fallback", s2.get("usedRaster") is True)
        check("S2 settled", s2.get("settled") is True)
        smp2 = s2.get("sample")
        check("S2 sample found", smp2 is not None, str(s2))
        if smp2:
            check("S2 landscape aspect (raster path agrees)", smp2["aspect"] > 1.05,
                  f"aspect={smp2['aspect']:.3f}")
            check("S2 marker top-right quadrant (raster path agrees)",
                  smp2["cxFrac"] > 0.6 and smp2["cyFrac"] < 0.4,
                  f"cxFrac={smp2['cxFrac']:.3f} cyFrac={smp2['cyFrac']:.3f}")

        # ---- Stage 3: rotatePage(90) composes to total=180 ----
        s3 = st.get("s3_rotate90_total180", {})
        check("S3 settled", s3.get("settled") is True)
        check("S3 pgRot=90", s3.get("pgRot") == 90, str(s3.get("pgRot")))
        smp3 = s3.get("sample")
        check("S3 sample found", smp3 is not None, str(s3))
        if smp3:
            check("S3 portrait aspect (total=180, unswapped dims)", smp3["aspect"] < 0.95,
                  f"aspect={smp3['aspect']:.3f} (expect ~0.75)")
            check("S3 marker bottom-right quadrant (180 rotation)",
                  smp3["cxFrac"] > 0.6 and smp3["cyFrac"] > 0.6,
                  f"cxFrac={smp3['cxFrac']:.3f} cyFrac={smp3['cyFrac']:.3f} (expect ~0.84,~0.88)")

        # ---- Stage 4: rotatePage(-90) back to native90 baseline ----
        s4 = st.get("s4_rotate_back", {})
        check("S4 settled", s4.get("settled") is True)
        check("S4 pgRot=0", s4.get("pgRot") == 0, str(s4.get("pgRot")))
        smp4 = s4.get("sample")
        check("S4 sample found", smp4 is not None, str(s4))
        if smp4:
            check("S4 back to landscape aspect", smp4["aspect"] > 1.05, f"aspect={smp4['aspect']:.3f}")
            check("S4 back to top-right quadrant",
                  smp4["cxFrac"] > 0.6 and smp4["cyFrac"] < 0.4,
                  f"cxFrac={smp4['cxFrac']:.3f} cyFrac={smp4['cyFrac']:.3f}")

        # ---- Stage 5: rot-0 PDFs unchanged (regression guard) ----
        s5 = st.get("s5_plain_unrotated", {})
        check("S5 settled", s5.get("settled") is True)
        smp5 = s5.get("sample")
        check("S5 sample found", smp5 is not None, str(s5))
        if smp5:
            check("S5 portrait aspect unchanged (no native rotation)", smp5["aspect"] < 0.95,
                  f"aspect={smp5['aspect']:.3f} (expect ~0.75)")
            check("S5 marker top-left quadrant unchanged",
                  smp5["cxFrac"] < 0.4 and smp5["cyFrac"] < 0.4,
                  f"cxFrac={smp5['cxFrac']:.3f} cyFrac={smp5['cyFrac']:.3f} (expect ~0.16,~0.12)")

    for e in page_errors:
        print("  JS ERROR:", e)
        failures.append(e)

    time.sleep(0.4)

    if failures:
        print()
        for f in failures:
            print("FAIL:", f)
        print("LITE_NATIVE_ROTATE_FAIL")
        sys.exit(1)
    print()
    print("LITE_NATIVE_ROTATE_OK")


if __name__ == "__main__":
    main()
