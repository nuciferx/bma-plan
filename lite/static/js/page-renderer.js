/*
 * page-renderer.js — BMA-Plan Lite
 * Slice-2: PDF.js viewport-clipped client-side renderer.
 * Replaces the JPEG-raster path; keeps ALL coordinate math (ptToScreen /
 * screenToPt / V.ox / V.oy / V.k / V.rot / RS) UNCHANGED.
 *
 * Globals READ (owned elsewhere — never redeclared here):
 *   cv          — <canvas> element           (ui-lite.html inline script)
 *   ctx         — 2D rendering context        (ui-lite.html inline script)
 *   V           — view state {k,ox,oy,rot}    (ui-lite.html inline script)
 *   RS          — render scale 1.5            (measure-engine.js)
 *   draw        — full-redraw function        (ui-lite.html inline script)
 *   caseId      — active case id             (ui-lite.html inline script)
 *   curPage     — current page number        (ui-lite.html host-globals block)
 *   pageCount   — total pages                (ui-lite.html inline script)
 *   pageData    — {size:{orig_w_pt,orig_h_pt}} (ui-lite.html host-globals block)
 *   api()       — path→URL with case_id      (ui-lite.html inline script)
 *   showLoading()/hideLoading()              (ui-lite.html inline script)
 *   afterPage() — post-load hook             (ui-lite.html inline script)
 *
 * Globals OWNED (declared here, used by ui-lite.html and page-rotate.js too):
 *   pageRot     — {[pageN]: rotation_degrees}  (persisted in .bmaplan)
 *   PageRenderer — public API object
 *
 * NOTE: imgCache and curImg are intentionally removed (PDF.js replaces them).
 * Callers in ui-lite.html that tested `curImg` now call PageRenderer.ready().
 *
 * pageRot strategy (option B — composed θ_total):
 *   PDF.js rotation=0. pageRot is folded into the render transform as
 *   θ_total = pgRot + V.rot.  This exactly matches the old JPEG path where
 *   the server baked pgRot into the JPEG and drawImage then applied V.rot.
 *   When pgRot is 90/270 we swap pageW/pageH for fit() (because the pre-rotated
 *   raster has swapped dimensions that the old code received from curImg).
 */

/* ---- owned globals ---- */
var pageRot = {};

/* curImg: kept as a writable global (null in production) so test shims that
 * set `window.curImg = dummy` continue to pass PageRenderer.ready() guards.
 * In production this stays null; readiness is determined by pdfDoc/pageCache.
 */
var curImg = null;

/* ---- PDF.js state ---- */
var pdfDoc       = null;   // PDFDocumentProxy
var pdfDocCaseId = null;   // caseId for which pdfDoc was loaded
var pageCache    = {};     // n → PDFPageProxy
var pageDims     = {};     // n → {w, h}  (PDF-pt dimensions, un-rotated)

/* ---- render concurrency guards ---- */
var _pendingRenderTask = null;  // PDF.js RenderTask
var _renderToken       = 0;     // monotonic bump; stale renders self-cancel

/* ---- double-buffer state (anti-flicker, smooth pan/zoom) ----
 * PDF.js renders into _offCanvas (off-screen); ui-lite.html's draw() calls
 * _drawImage which blits _offCanvas to the visible canvas. During pan/zoom
 * the cached image is blitted with a "diff transform" so the PDF appears to
 * follow the cursor in real time; a fresh PDF.js render runs in background
 * and replaces the cache when ready.
 */
var _offCanvas = (typeof document !== "undefined") ? document.createElement("canvas") : null;
var _cachedV   = null;   // snapshot of V at last successful render
var _cachedKey = null;   // state key of last successful render

function _stateKey() {
  return curPage + "|" + V.k + "|" + V.rot + "|" + Math.round(V.ox) + "|" +
         Math.round(V.oy) + "|" + (pageRot[curPage] || 0) + "|" +
         cv.width + "x" + cv.height;
}

/* ---- lazy PDF.js loader ---- */
var _pdfjsLib    = null;
var _pdfjsPromise = null;

var PDFJS_VER = "4.0.379";

function _loadPdfjsLib() {
  if (_pdfjsPromise) return _pdfjsPromise;
  _pdfjsPromise = import(
    "https://cdn.jsdelivr.net/npm/pdfjs-dist@" + PDFJS_VER + "/build/pdf.min.mjs"
  ).then(function(lib) {
    lib.GlobalWorkerOptions.workerSrc =
      "https://cdn.jsdelivr.net/npm/pdfjs-dist@" + PDFJS_VER + "/build/pdf.worker.min.mjs";
    _pdfjsLib = lib;
    return lib;
  });
  return _pdfjsPromise;
}

/* ---- ready(): true when current page is available for rendering ----
 * Production: pdfDoc loaded + page in pageCache.
 * Test-shim compat: if a test sets window.curImg to a truthy dummy value,
 * accept that as well so existing tests that do `window.curImg = dummy` still
 * satisfy the `if(!PageRenderer.ready())return` guards.
 */
function _ready() {
  if (curImg) return true;  // test-shim compat
  return !!(pdfDoc && pdfDocCaseId === caseId && curPage && pageCache[curPage]);
}

/* ---- _computeTransform: deprecated post-PDFJS-ANTIFLICKER+MIRROR-FIX ----
 *
 * spike v4's analytical T derived a Y-flip (`-cR*dpr` in the 4th matrix slot)
 * to compensate for PDF.js's PDF-Y-up → screen-Y-down flip. The derivation
 * assumed PDF.js's `transform` was applied to a NON-rotated viewport.
 *
 * REAL PDF.js behaviour: `getViewport({rotation:R})` returns a viewport whose
 * `transform` already encodes intrinsic /Rotate + R + scale + Y-flip. Then
 * `render({transform:our_T})` composes our_T on top. Spike v4 was correct only
 * when intrinsic /Rotate=0; for /Rotate=90 PDFs (e.g. RAMA4 A1), intrinsic
 * adds a rotation that v4's T didn't anticipate → content rendered upside-down
 * AND mirrored. Reported by user 2026-05-28.
 *
 * Fix: don't compute T analytically. Pass rotation=(V.rot+pgRot) to getViewport
 * (PDF.js handles intrinsic + user/page rotation), then T = translate-only to
 * (V.ox, V.oy). Visual output is correct for any /Rotate value. Function kept
 * (unused) for spike v4 reference / future re-derivation if needed.
 */
function _computeTransform(pageH, theta) {  /* eslint-disable-line no-unused-vars */
  var dpr = window.devicePixelRatio || 1;
  var s   = RS * V.k;
  var th  = theta * Math.PI / 180;
  var cR  = Math.cos(th);
  var sR  = Math.sin(th);
  return [
    cR * dpr,
    sR * dpr,
    sR * dpr,
    -cR * dpr,
    (V.ox - pageH * s * sR) * dpr,
    (V.oy + pageH * s * cR) * dpr
  ];
}

/* ---- resize: canvas physical size ← CSS size × DPR ---- */
function resize() {
  var dpr = window.devicePixelRatio || 1, r = cv.getBoundingClientRect();
  cv.width  = r.width  * dpr;
  cv.height = r.height * dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  draw();
}
window.addEventListener("resize", resize);

/* ---- fit: zoom+pan so the page fills the viewport comfortably ----
 * Mirrors old fit() logic but uses pageDims instead of curImg.width/height.
 * When pgRot is 90 or 270 the rendered raster is dimension-swapped vs the
 * original PDF — we replicate that by swapping iw/ih here.
 */
function fit() {
  if (!_ready()) return;
  var r  = cv.getBoundingClientRect();
  var pgRot = pageRot[curPage] || 0;
  // Test-shim compat: pageDims may be empty when curImg dummy is set
  var rawW, rawH;
  if (pageDims[curPage]) {
    rawW = pageDims[curPage].w * RS;
    rawH = pageDims[curPage].h * RS;
  } else if (curImg) {
    rawW = curImg.width;
    rawH = curImg.height;
  } else {
    return;
  }
  // When page is rotated 90 or 270, rendered dimensions are swapped
  var swapped = (pgRot % 180 !== 0);
  var iw = swapped ? rawH : rawW;
  var ih = swapped ? rawW : rawH;
  var rot = V.rot % 180 !== 0;
  var W = rot ? ih : iw, H = rot ? iw : ih;
  V.k = Math.min(r.width / W, r.height / H) * 0.94;
  V.rot = V.rot || 0;
  var corners = [[0,0],[iw,0],[iw,ih],[0,ih]].map(function(p) {
    var th = V.rot * Math.PI / 180, c = Math.cos(th), s = Math.sin(th);
    return { x: (p[0]*c - p[1]*s) * V.k, y: (p[0]*s + p[1]*c) * V.k };
  });
  var xs = corners.map(function(p) { return p.x; });
  var ys = corners.map(function(p) { return p.y; });
  var minx = Math.min.apply(0, xs), miny = Math.min.apply(0, ys);
  var bw   = Math.max.apply(0, xs) - minx;
  var bh   = Math.max.apply(0, ys) - miny;
  V.ox = (r.width  - bw) / 2 - minx;
  V.oy = (r.height - bh) / 2 - miny;
  draw();
}

/* ---- loadPage: fetch PDF via /raw, render with PDF.js, call afterPage ---- */
async function loadPage(n) {
  if (!caseId || n < 1 || n > pageCount) return;
  curPage = n;
  showLoading("กำลังโหลดหน้า " + n + " / " + pageCount + "…");
  try {
    var lib = await _loadPdfjsLib();
    // Reload PDF document if case changed or not yet loaded
    if (!pdfDoc || pdfDocCaseId !== caseId) {
      var resp = await fetch("/raw?case_id=" + caseId);
      if (!resp.ok) throw new Error("HTTP " + resp.status);
      var buf  = await resp.arrayBuffer();
      pdfDoc       = await lib.getDocument({ data: buf }).promise;
      pdfDocCaseId = caseId;
      pageCache    = {};
      pageDims     = {};
    }
    // Cache the PDFPageProxy
    if (!pageCache[n]) {
      pageCache[n] = await pdfDoc.getPage(n);
    }
    // pageDims = POST-INTRINSIC-ROTATION dims (the orientation server JPEG used to deliver).
    // page.view gives NATIVE pre-rotation dims — wrong for PDFs with /Rotate metadata.
    // PDF.js viewport at rotation=0 already applies intrinsic /Rotate, so its
    // width/height reflect the visually-correct landscape (e.g. RAMA4 A1 /Rotate=90).
    var natVp = pageCache[n].getViewport({ scale: 1, rotation: 0 });
    pageDims[n] = { w: natVp.width, h: natVp.height };
    pageData = { size: { orig_w_pt: pageDims[n].w, orig_h_pt: pageDims[n].h } };
    hideLoading();
    fit();
    afterPage();
  } catch (err) {
    hideLoading();
    alert("โหลดหน้า " + n + " ไม่ได้: " + err.message);
  }
}

/* ---- _render: async — PDF.js renders into _offCanvas (off-screen) ----
 * On success, updates _cachedV / _cachedKey, then requests a repaint so the
 * fresh cache gets blitted to the visible canvas.
 *
 * pageRot strategy (option B): θ_total = pgRot + V.rot folded into the
 * transform; PDF.js viewport rotation stays 0. pageH for the transform = the
 * un-rotated PDF height (or width when pgRot is 90/270, because the origin
 * shifts to what would be the top-right corner of the un-rotated page).
 */
async function _render(myToken) {
  var cp = pageCache[curPage];
  if (!cp || !pageDims[curPage] || !_offCanvas) return;

  // Snapshot V at render-start so the cache reflects this exact state.
  var Vsnap = { k: V.k, ox: V.ox, oy: V.oy, rot: V.rot };
  var pgRot = pageRot[curPage] || 0;

  // Strategy (post spike-v4): let PDF.js handle ALL rotation in its viewport
  // (intrinsic /Rotate via rotation=0 default; user pgRot+V.rot via rotation arg).
  // Our `transform` is then TRANSLATE-ONLY — places the rendering at canvas
  // (V.ox, V.oy). spike v4's analytical T mis-rotated PDFs with intrinsic
  // /Rotate ≠ 0 (e.g. RAMA4 A1 /Rotate=90 came out upside-down).
  //
  // ptToScreen alignment: since pageDims already reflects post-intrinsic dims,
  // lite's p ∈ [0, pageW] × [0, pageH] is in "visual orientation" coords. At
  // V.rot=0, pgRot=0: ptToScreen(p)=(p.x*RS*V.k+V.ox, p.y*RS*V.k+V.oy), which
  // matches PDF.js's content drawn at (V.ox, V.oy) with scale RS*V.k.
  var thetaUser = ((Vsnap.rot + pgRot) % 360 + 360) % 360;
  var scale     = RS * Vsnap.k;
  var viewport  = cp.getViewport({ scale: scale, rotation: thetaUser });

  var dpr = window.devicePixelRatio || 1;
  var T = [dpr, 0, 0, dpr, Vsnap.ox * dpr, Vsnap.oy * dpr];

  if (myToken !== _renderToken) return; // stale

  // Resize off-canvas to match visible canvas dims (only when changed — setting
  // .width clears the canvas even if value is the same).
  if (_offCanvas.width  !== cv.width)  _offCanvas.width  = cv.width;
  if (_offCanvas.height !== cv.height) _offCanvas.height = cv.height;
  var offCtx = _offCanvas.getContext("2d");
  offCtx.setTransform(1, 0, 0, 1, 0, 0);
  offCtx.clearRect(0, 0, _offCanvas.width, _offCanvas.height);

  try {
    _pendingRenderTask = cp.render({ canvasContext: offCtx, viewport: viewport, transform: T });
    await _pendingRenderTask.promise;
  } catch (e) {
    if (e && e.name === "RenderingCancelledException") return;
    console.error("[page-renderer] render error:", e);
    return;
  } finally {
    _pendingRenderTask = null;
  }

  if (myToken !== _renderToken) return; // stale after await

  // Commit the snapshot — _drawImage now blits this with diff-transform.
  _cachedV   = Vsnap;
  _cachedKey = curPage + "|" + Vsnap.k + "|" + Vsnap.rot + "|" +
               Math.round(Vsnap.ox) + "|" + Math.round(Vsnap.oy) + "|" +
               pgRot + "|" + cv.width + "x" + cv.height;

  requestAnimationFrame(function() { if (typeof draw === "function") draw(); });
}

/* ---- drawImage: SYNC — blit cached offCanvas to ctx + schedule re-render ----
 *
 * ANTI-FLICKER strategy:
 *   ui-lite.html's draw() calls ctx.clearRect THEN PageRenderer.drawImage THEN
 *   draws overlay objects. If we render PDF.js directly into ctx here, the
 *   await holds for ~30 ms during which the canvas is BLANK (already cleared)
 *   → visible flicker. Worse during pan because mousemove fires draw() per
 *   frame, each scheduling a new clear+await cycle.
 *
 *   Fix: PDF.js renders into _offCanvas (off-screen, async). _drawImage just
 *   BLITS the (possibly stale) _offCanvas onto ctx with a diff-transform that
 *   accounts for the pan/zoom delta between the cached state and current V.
 *   The PDF visually tracks the cursor during pan; a fresh render starts in
 *   the background and replaces the cache when ready. Same idea as Google
 *   Maps tile rendering.
 *
 *   Anti-infinite-loop: render is scheduled ONLY when current state key
 *   differs from _cachedKey AND no render is in flight. Once render completes
 *   it sets _cachedKey to its rendered state → next _drawImage with same
 *   state won't re-schedule. requestAnimationFrame(draw) at the end of
 *   _render fires at most once per completed render.
 */
function _drawImage(ctx_ignored) {
  if (!_ready()) return;
  var dpr = window.devicePixelRatio || 1;

  // ---- Phase 1: blit cached _offCanvas (smooth) ----
  if (_cachedV && _offCanvas && _offCanvas.width > 0) {
    ctx.save();
    if (V.rot === _cachedV.rot) {
      // Pan + zoom diff (no rotation change) → scale + translate the blit
      // so PDF tracks user's pan/zoom in real time.
      // ptToScreen(p, V) - ptToScreen(p, _cachedV) collapses to:
      //   sx_new = s*(sx_old - _cachedV.ox) + V.ox,   where s = V.k/_cachedV.k
      // in CSS-px; multiply by dpr for the device-px ctx.
      var ss = V.k / _cachedV.k;
      ctx.setTransform(ss, 0, 0, ss,
        (V.ox - ss * _cachedV.ox) * dpr,
        (V.oy - ss * _cachedV.oy) * dpr);
    } else {
      // Rotation diff — skip diff transform; one-frame mismatch acceptable
      // (rotation is a discrete click, fresh render arrives within ~30 ms).
      ctx.setTransform(1, 0, 0, 1, 0, 0);
    }
    ctx.drawImage(_offCanvas, 0, 0);
    ctx.restore();
  } else if (pageDims[curPage]) {
    // No cached image yet (first render pending) → placeholder rect so the
    // user sees the page bounds rather than blank canvas.
    var pgRot   = pageRot[curPage] || 0;
    var swapped = (pgRot % 180 !== 0);
    var pw = (swapped ? pageDims[curPage].h : pageDims[curPage].w) * RS * V.k;
    var ph = (swapped ? pageDims[curPage].w : pageDims[curPage].h) * RS * V.k;
    ctx.save();
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = "#1a1e28";
    ctx.fillRect(V.ox, V.oy, pw, ph);
    ctx.restore();
  }

  // ---- Phase 2: schedule re-render if state changed ----
  if (!pdfDoc || !pageCache[curPage]) return;
  var key = _stateKey();
  if (key === _cachedKey && _pendingRenderTask === null) return;  // up-to-date

  // State drifted from cache → kick off fresh render in background
  if (_pendingRenderTask) {
    try { _pendingRenderTask.cancel(); } catch (_) {}
    _pendingRenderTask = null;
  }
  var myToken = ++_renderToken;
  Promise.resolve().then(function() { _render(myToken); });
}

/* ---- resetCache: called on new upload / loadProject in ui-lite.html ---- */
function _resetCache() {
  if (_pendingRenderTask) {
    try { _pendingRenderTask.cancel(); } catch (_) {}
    _pendingRenderTask = null;
  }
  _renderToken++;
  pdfDoc       = null;
  pdfDocCaseId = null;
  pageCache    = {};
  pageDims     = {};
  pageRot      = {};
  _cachedV     = null;
  _cachedKey   = null;
  if (_offCanvas) {
    _offCanvas.width = 0;  // also clears
  }
}

/* ---- public API ---- */
window.PageRenderer = {
  loadPage:   loadPage,
  drawImage:  _drawImage,
  fit:        fit,
  resize:     resize,
  resetCache: _resetCache,
  ready:      _ready
};
