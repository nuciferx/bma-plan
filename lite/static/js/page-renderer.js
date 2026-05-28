/*
 * page-renderer.js — BMA-Plan Lite
 * Slice-1 extraction: page-image loading, caching, fit-to-viewport, raster draw.
 * Slice-2 will swap the img-tag/JPEG path for PDF.js client-side render here.
 *
 * Globals READ (owned elsewhere, never redeclared here):
 *   cv          — <canvas> element           (ui-lite.html inline script)
 *   ctx         — 2D rendering context        (ui-lite.html inline script)
 *   V           — view state {k,ox,oy,rot}    (ui-lite.html inline script)
 *   draw        — full-redraw function        (ui-lite.html inline script)
 *   caseId      — active case id             (ui-lite.html inline script)
 *   curPage     — current page number        (ui-lite.html host-globals block)
 *   pageCount   — total pages                (ui-lite.html inline script)
 *   pageData    — {size:{orig_w_pt,orig_h_pt}} (ui-lite.html host-globals block)
 *   api()       — path→URL with case_id      (ui-lite.html inline script)
 *   showLoading()/hideLoading()              (ui-lite.html inline script)
 *   fit()       — declared below, also read by zoomCenter/actualSize in ui-lite.html
 *   afterPage() — post-load hook             (ui-lite.html inline script)
 *
 * Globals OWNED (declared here, used by ui-lite.html too):
 *   imgCache    — {[pageN]: HTMLImageElement}
 *   curImg      — currently displayed HTMLImageElement | null
 *   pageRot     — {[pageN]: rotation_degrees}  (persisted in .bmaplan)
 *   PageRenderer — public API object
 */

/* ---- owned globals ---- */
var imgCache = {};
var curImg   = null;
var pageRot  = {};

/* ---- resize: canvas physical size ← CSS size × DPR ---- */
function resize() {
  var dpr = window.devicePixelRatio || 1, r = cv.getBoundingClientRect();
  cv.width  = r.width  * dpr;
  cv.height = r.height * dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  draw();
}
window.addEventListener("resize", resize);

/* ---- fit: zoom+pan so curImg fills the viewport comfortably ---- */
function fit() {
  if (!curImg) return;
  var r  = cv.getBoundingClientRect();
  var iw = curImg.width, ih = curImg.height;
  var rot = V.rot % 180 !== 0; var W = rot ? ih : iw, H = rot ? iw : ih;
  V.k = Math.min(r.width / W, r.height / H) * 0.94; V.rot = V.rot || 0;
  // center: compute bounding box of the rotated image at scale V.k
  var corners = [[0,0],[iw,0],[iw,ih],[0,ih]].map(function(p) {
    var th = V.rot * Math.PI / 180, c = Math.cos(th), s = Math.sin(th);
    return { x: (p[0]*c - p[1]*s) * V.k, y: (p[0]*s + p[1]*c) * V.k };
  });
  var xs = corners.map(function(p) { return p.x; });
  var ys = corners.map(function(p) { return p.y; });
  var minx = Math.min.apply(0, xs), miny = Math.min.apply(0, ys);
  var bw   = Math.max.apply(0, xs) - minx, bh = Math.max.apply(0, ys) - miny;
  V.ox = (r.width  - bw) / 2 - minx;
  V.oy = (r.height - bh) / 2 - miny;
  draw();
}

/* ---- loadPage: fetch JPEG from /page/{n}, cache, then call afterPage ---- */
async function loadPage(n) {
  if (!caseId || n < 1 || n > pageCount) return;
  curPage = n;
  var info = await (await fetch(api("/pageinfo/" + n))).json();
  pageData = { size: { orig_w_pt: info.w_pt, orig_h_pt: info.h_pt } };
  if (imgCache[n]) { curImg = imgCache[n]; hideLoading(); fit(); afterPage(); return; }
  showLoading("กำลังโหลดหน้า " + n + " / " + pageCount + "…");
  var img = new Image();
  img.onload  = function() { imgCache[n] = img; curImg = img; hideLoading(); fit(); afterPage(); };
  img.onerror = function() { hideLoading(); alert("โหลดหน้า " + n + " ไม่ได้"); };
  img.src = api("/page/" + n) + "&rot=" + (pageRot[n] || 0);
}

/* ---- drawImage: draw the raster background onto ctx ---- */
/* Called by draw() in ui-lite.html as: PageRenderer.drawImage(ctx) */
function _drawImage(ctx) {
  if (!curImg) return;
  var th = V.rot * Math.PI / 180;
  ctx.save();
  ctx.translate(V.ox, V.oy);
  ctx.rotate(th);
  ctx.scale(V.k, V.k);
  ctx.drawImage(curImg, 0, 0);
  ctx.restore();
}

/* ---- public API ---- */
window.PageRenderer = {
  loadPage:  loadPage,
  drawImage: _drawImage,
  fit:       fit,
  resize:    resize,
  /* accessors used by save/load and upload-reset in ui-lite.html */
  resetCache: function() { imgCache = {}; curImg = null; pageRot = {}; }
};
