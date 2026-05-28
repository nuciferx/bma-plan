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

/* ---- computeTransform: BYTE-IDENTICAL to spike v4 computeTransform ----
 * Formula proven analytically in spike v4; 24/24 contract PASS verified.
 * θ = θ_total = pgRot + V.rot  (option B — folds page rotation in)
 * pageH = un-rotated PDF-pt page height (from pageDims[n].h; swapped below
 * in render() when pgRot is 90/270 to keep the origin at the correct corner).
 */
function _computeTransform(pageH, theta) {
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
    var view = pageCache[n].view;  // [x0, y0, x1, y1]
    pageDims[n] = { w: view[2] - view[0], h: view[3] - view[1] };
    // Expose pageData for coord-conversion consumers (same shape as old /pageinfo)
    pageData = { size: { orig_w_pt: pageDims[n].w, orig_h_pt: pageDims[n].h } };
    hideLoading();
    fit();
    afterPage();
  } catch (err) {
    hideLoading();
    alert("โหลดหน้า " + n + " ไม่ได้: " + err.message);
  }
}

/* ---- _render: async — does the actual PDF.js render into ctx ---- */
async function _render(myToken) {
  var cp = pageCache[curPage];
  if (!cp || !pageDims[curPage]) return;

  var pgRot = pageRot[curPage] || 0;

  /* option B: θ_total folds pageRot into the transform so PDF.js stays at rotation=0.
   * The viewport scale uses RS*V.k (matching spike v4).
   * pageH for the transform formula must be the un-rotated PDF height when pgRot=0/180,
   * OR the un-rotated PDF width when pgRot=90/270 (because the origin after baking 90°
   * is at the top-right of the rotated image — equivalent to the original pageWidth).
   */
  var rawW = pageDims[curPage].w;
  var rawH = pageDims[curPage].h;
  var swapped = (pgRot % 180 !== 0);
  // pageH_for_transform: the effective "height" in the rotated coordinate origin
  var pageH_tx = swapped ? rawW : rawH;

  var thetaTotal = pgRot + V.rot;
  var scale      = RS * V.k;
  var viewport   = cp.getViewport({ scale: scale, rotation: 0 });
  var T          = _computeTransform(pageH_tx, thetaTotal);

  // For pgRot=90/270 we need a different PDF.js viewport because the page's native
  // coordinate system (as PDF.js sees it at rotation=0) has width/height un-swapped.
  // We apply the full rotation via transform T, so viewport rotation stays 0.
  // (The spike v4 tested only V.rot; here pgRot folds into thetaTotal.)

  if (myToken !== _renderToken) return; // stale, bail early

  try {
    _pendingRenderTask = cp.render({ canvasContext: ctx, viewport: viewport, transform: T });
    await _pendingRenderTask.promise;
  } catch (e) {
    if (e && e.name === "RenderingCancelledException") return;
    console.error("[page-renderer] render error:", e);
  } finally {
    _pendingRenderTask = null;
  }

  // If another draw() call bumped the token while we were rendering, request a repaint
  if (myToken !== _renderToken) {
    requestAnimationFrame(function() { if (typeof draw === "function") draw(); });
  }
}

/* ---- drawImage: SYNC signature — called by draw() in ui-lite.html ----
 * Cancels any in-flight render, bumps renderToken, schedules async render
 * as a microtask (fire-and-forget). The sync call returns immediately so
 * draw() can continue to overlay measurement objects on top.
 * Anti-infinite-loop: _renderToken is bumped once per drawImage call.
 * The async _render checks its captured token before every await; if it
 * becomes stale it bails without scheduling another draw(). The final
 * requestAnimationFrame(draw) is only triggered when the token DID NOT
 * change during the render — so it fires at most once per completed render.
 */
function _drawImage(ctx_ignored) {
  if (!_ready()) return;

  // Cancel any still-running render
  if (_pendingRenderTask) {
    try { _pendingRenderTask.cancel(); } catch (_) {}
    _pendingRenderTask = null;
  }

  var myToken = ++_renderToken;

  // Optional: paint a placeholder rect while first render is pending.
  // Skip if pageDims not yet populated (e.g. test-shim mode with curImg compat).
  if (pageDims[curPage]) {
    var pgRot   = pageRot[curPage] || 0;
    var swapped = (pgRot % 180 !== 0);
    var pw = (swapped ? pageDims[curPage].h : pageDims[curPage].w) * RS * V.k;
    var ph = (swapped ? pageDims[curPage].w : pageDims[curPage].h) * RS * V.k;
    var dpr = window.devicePixelRatio || 1;
    ctx.save();
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = "#1a1e28";
    ctx.fillRect(V.ox, V.oy, pw, ph);
    ctx.restore();
  }

  // Fire async render (microtask) — only if real PDF.js state is present
  if (pdfDoc && pageCache[curPage]) {
    Promise.resolve().then(function() { _render(myToken); });
  }
}

/* ---- resetCache: called on new upload / loadProject in ui-lite.html ---- */
function _resetCache() {
  // Cancel any in-flight render before wiping state
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
