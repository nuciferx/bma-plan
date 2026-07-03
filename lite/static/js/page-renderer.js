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
var pageDims     = {};     // n → {w, h}  (PDF-pt dimensions, un-rotated) — tiny, never evicted

/* ---- worker-recycle state (PERF-20260703) ----
 * _docWorker is the explicit pdf.js PDFWorker that owns pdfDoc — created
 * explicitly (rather than letting getDocument spin up an implicit one) so
 * recycleDocWorker() can terminate it deterministically. _docSource retains
 * a cheap re-open handle WITHOUT keeping the big buffer resident: the local
 * File/Blob for the local-first path (zero-network reinit), or just the
 * caseId for the /raw path (reinit = one refetch). See recycleDocWorker()
 * and _reinitDoc() below for the full rationale. */
var _docWorker = null;   // explicit PDFWorker instance owning pdfDoc
var _docSource = null;   // {kind:"blob", blob} | {kind:"url", caseId} | null
var _recycled  = false;  // true after recycleDocWorker(), cleared by _reinitDoc
var _recycling = false;  // guard: a recycle is already in progress

/* ---- page-cache LRU (PERF-20260702) ----
 * PDFPageProxy retains operator lists + decoded images per page; measured
 * ~75 MB/page on a real 91 MB A1 binder (766 MB heap after 10 of 95 pages).
 * Keep only the last MAX_PAGE_CACHE pages hot; evicted proxies get
 * proxy.cleanup() (releases resources; getPage() re-fetches on revisit).
 * curPage (and any alias key pointing at its proxy) is never evicted —
 * a render may be in flight on it. */
var MAX_PAGE_CACHE = 4;
var _pageLru = [];         // cache keys, most-recent last

function _touchPage(key) {
  var i = _pageLru.indexOf(key);
  if (i >= 0) _pageLru.splice(i, 1);
  _pageLru.push(key);
  while (_pageLru.length > MAX_PAGE_CACHE) {
    var idx = -1;
    for (var j = 0; j < _pageLru.length - 1; j++) {           // never the most-recent
      var cand = _pageLru[j];
      if (cand !== curPage && pageCache[cand] !== pageCache[curPage]) { idx = j; break; }
    }
    if (idx < 0) break;                                       // everything protected
    var old = _pageLru.splice(idx, 1)[0];
    var proxy = pageCache[old];
    delete pageCache[old];
    if (proxy) {
      var stillRef = false;
      for (var k in pageCache) { if (pageCache[k] === proxy) { stillRef = true; break; } }
      if (!stillRef) { try { proxy.cleanup(); } catch (_) {} }
    }
  }
}

/* ---- render concurrency guards ---- */
var _pendingRenderTask = null;  // PDF.js RenderTask
var _renderToken       = 0;     // monotonic bump; stale renders self-cancel

/* ---- double-buffer state (anti-flicker + sharper zoom) ----
 * PDF.js renders into _offCanvas (off-screen, cv-sized); ui-lite.html's
 * draw() calls _drawImage which blits _offCanvas to the visible canvas with
 * a diff-transform that tracks pan/zoom in real time.
 *
 * Why not HEADROOM-sized offCanvas? Considered (and tried) — render the
 * cached content at HEADROOM×V.k for zoom-in headroom. Failed because at
 * HEADROOM=1.5, content (≈cv.width × 1.5 already at fit-zoom for A1 PDFs)
 * overflows the bigger offCanvas at any moderate zoom-in, causing clip
 * artifacts. Tile-based rendering would solve this but is over-engineered
 * for lite's single-canvas architecture.
 *
 * Instead: ctx.imageSmoothingQuality = "high" makes Chrome use a cubic-like
 * filter for the diff-blit upscale → noticeably less blur than bilinear
 * during the ~30 ms gap before PDF.js refreshes the cache.
 */
var _offCanvas = (typeof document !== "undefined") ? document.createElement("canvas") : null;
var _cachedV   = null;   // snapshot of V + page + pgRot + cv-dims at last successful render
var _cachedKey = null;   // state key of last successful render

function _stateKey() {
  return curPage + "|" + V.k + "|" + V.rot + "|" + Math.round(V.ox) + "|" +
         Math.round(V.oy) + "|" + (pageRot[curPage] || 0) + "|" +
         cv.width + "x" + cv.height;
}

/* ---- lazy PDF.js loader ---- */
var _pdfjsLib    = null;
var _pdfjsPromise = null;

var PDFJS_VER  = "4.0.379";
var LOCAL_BASE = "/static/js/vendor/pdfjs";

async function _loadPdfjsLib() {
  if (_pdfjsPromise) return _pdfjsPromise;
  _pdfjsPromise = (async function() {
    // 1. Try local vendored copy first (works offline / no CDN)
    try {
      var lib = await import(LOCAL_BASE + "/pdf.min.mjs");
      lib.GlobalWorkerOptions.workerSrc = LOCAL_BASE + "/pdf.worker.min.mjs";
      _pdfjsLib = lib;
      console.info("[page-renderer] pdfjs loaded from local vendor");
      return lib;
    } catch (err) {
      console.warn("[page-renderer] local pdfjs failed, falling back to CDN:", err);
    }
    // 2. CDN fallback
    try {
      var lib = await import(
        "https://cdn.jsdelivr.net/npm/pdfjs-dist@" + PDFJS_VER + "/build/pdf.min.mjs"
      );
      lib.GlobalWorkerOptions.workerSrc =
        "https://cdn.jsdelivr.net/npm/pdfjs-dist@" + PDFJS_VER + "/build/pdf.worker.min.mjs";
      _pdfjsLib = lib;
      return lib;
    } catch (err2) {
      // Both paths failed — reset so next page navigation can retry
      _pdfjsPromise = null;
      throw new Error("ไม่สามารถโหลดตัวแสดงผล PDF (pdfjs) ได้ — ทั้งจากเครื่องและ CDN");
    }
  })();
  return _pdfjsPromise;
}

/* ---- raster fallback (render-followups (a)) ----
 * If PDF.js is unavailable (both local vendor and CDN fail, or the doc is
 * one PyMuPDF opens but PDF.js rejects), fall back to the server JPEG path
 * instead of a blank canvas + alert. curImg (HTMLImageElement) holds the
 * server-rendered raster; _drawImage gets a dedicated branch for it.
 * Measurement stays fully functional — only zoom sharpness is raster-limited. */
var _forceRasterFallback = false;   // test hook via PageRenderer._test_forceRasterFallback

async function _rasterFallbackLoad(n, sn) {
  if (!caseId) throw new Error("no case for raster fallback");
  var info = await (await fetch(api("/pageinfo/" + sn))).json();
  if (!info || !info.w_pt) throw new Error("pageinfo failed");
  var rot = pageRot[n] || 0;
  var img = new Image();
  await new Promise(function (res, rej) {
    img.onload = res;
    img.onerror = function () { rej(new Error("raster fetch failed")); };
    img.src = api("/page/" + sn) + "&rot=" + rot;
  });
  curImg = img;
  pageDims[n] = { w: info.w_pt, h: info.h_pt };
  pageData = { size: { orig_w_pt: info.w_pt, orig_h_pt: info.h_pt } };
  console.warn("[page-renderer] pdfjs unavailable — raster fallback for page " + n);
}

/* ---- scanned-page detection + re-render scale cap (render-followups (c)) ----
 * Image-only pages gain no sharpness from PDF.js re-render beyond the embedded
 * image's native resolution — but they DO pay the full re-raster CPU at every
 * zoom. Detect image-only pages from the (already cached post-render) operator
 * list and cap the render scale; the transform compensates (up = want/use) so
 * raster↔overlay registration is unchanged, only resolution is capped. */
var _scanned = {};                          // n -> true | false | null(pending)
var _scannedHinted = {};
var SCANNED_MAX_SCALE = RS * 4;             // ≈ 432 DPI — above typical 300 DPI scans

async function _detectScanned(n) {
  if (!pageCache[n] || !_pdfjsLib) { _scanned[n] = undefined; return; }
  try {
    var ops = await pageCache[n].getOperatorList();   // cached after first render
    var OPS = _pdfjsLib.OPS;
    var imgs = 0, paths = 0, texts = 0;
    for (var i = 0; i < ops.fnArray.length; i++) {
      var f = ops.fnArray[i];
      if (f === OPS.paintImageXObject || f === OPS.paintInlineImageXObject ||
          f === OPS.paintJpegXObject) imgs++;
      else if (f === OPS.constructPath) paths++;
      else if (f === OPS.showText || f === OPS.showSpacedText) texts++;
    }
    _scanned[n] = (imgs >= 1 && paths === 0 && texts === 0);
    if (_scanned[n] && !_scannedHinted[n]) {
      _scannedHinted[n] = true;
      showLoading("หน้านี้เป็นภาพสแกน — ความคมจำกัดที่ความละเอียดต้นฉบับ");
      setTimeout(hideLoading, 2200);
    }
  } catch (_) { _scanned[n] = false; }
}

/* ---- warm-up: preload pdf.js + spin the worker at idle (PERF-20260702) ----
 * The first real open pays a flat ~1.2 s for library import + worker fetch/
 * compile. Firing it at app-idle moves that cost off the user's open action.
 * Fire-and-forget; failures are ignored (the real open path retries loading).
 * window.__pdfjsWarmed is a test observability flag only. */
function _warmup() {
  _loadPdfjsLib().then(function(lib) {
    try {
      var w = new lib.PDFWorker({ name: "bma-warmup" });
      return w.promise.then(function() {
        try { w.destroy(); } catch (_) {}
        window.__pdfjsWarmed = true;
      });
    } catch (_) { window.__pdfjsWarmed = true; }
  }).catch(function () {});
}
if (typeof requestIdleCallback === "function") requestIdleCallback(_warmup, { timeout: 3000 });
else setTimeout(_warmup, 500);

/* ---- adjacent-page prefetch (PERF-20260702) ----
 * After a page lands, fetch the n±1 PDFPageProxy at idle so the next page
 * switch skips the worker getPage round-trip. Respects the LRU: prefetched
 * pages count toward MAX_PAGE_CACHE and curPage stays protected. */
function _prefetchAdjacent(n) {
  if (!pdfDoc) return;
  [n + 1, n - 1].forEach(function (m) {
    if (m < 1 || m > pageCount || pageCache[m]) return;
    var sn = (typeof pageMgr !== "undefined" && pageMgr) ? pageMgr.serverNum(m) : m;
    if (sn === null) return;
    if (pageCache[sn]) { pageCache[m] = pageCache[sn]; _touchPage(m); return; }
    pdfDoc.getPage(sn).then(function (p) {
      if (!pdfDoc) return;                    // reset while in flight
      if (!pageCache[sn]) { pageCache[sn] = p; _touchPage(sn); }
      if (m !== sn && !pageCache[m]) { pageCache[m] = pageCache[sn]; _touchPage(m); }
    }).catch(function () {});
  });
}

/* ---- worker recycle: PERF-20260703 memory release ----
 * Spike (docs/invent/lite-range-streaming.md, 2026-07-03; artifacts in
 * lite/sandbox/invent-range-streaming/) confirmed pdf.js bug #10730 on
 * 4.0.379: pdfDoc.destroy() frees the MAIN-THREAD heap only — the worker
 * thread's commonObjs/render heap (~1.5 GB measured on a 95 MB binder)
 * survives destroy() and is reclaimed ONLY by terminating the worker
 * itself. Range-streaming was spiked as the memory fix and rejected
 * (-10% RSS vs the -50% GO bar; see results.md) — this is the named
 * RESHAPE fallback: recycle pdfDoc + the explicit worker on idle / tab-away,
 * then lazily reinit via _reinitDoc() on the next page visit.
 *
 * recycleDocWorker() KEEPS pageDims/pageRot/_scanned — cheap metadata, not
 * pdf.js-owned memory — so fit()/registration/scanned-cap stay correct
 * across a recycle with no re-detection needed. It does NOT touch
 * measurement state (PS lives in ui-lite.html).
 *
 * Guards (all return false / no-op, never throw): a render in flight
 * (_pendingRenderTask — never interrupts a live paint), a recycle already
 * running, nothing loaded, or no _docSource to reinit from later (recycling
 * would strand the app with no way back).
 */
async function recycleDocWorker() {
  if (_recycling) return false;
  if (_pendingRenderTask) return false;      // never interrupt a live render
  if (!pdfDoc && !_docWorker) return false;  // nothing loaded to recycle
  if (!_docSource) return false;             // no way to reinit later — skip
  _recycling = true;
  try {
    if (pdfDoc) { try { await pdfDoc.destroy(); } catch (_) {} }
    if (_docWorker) { try { _docWorker.destroy(); } catch (_) {} }
    pdfDoc       = null;
    _docWorker   = null;
    pdfDocCaseId = null;
    pageCache    = {};
    _pageLru     = [];
    _cachedV     = null;
    _cachedKey   = null;
    _recycled    = true;
    if (_offCanvas) _offCanvas.width = 0;   // drop the stale bitmap too
    _clearIdleTimer();
    _clearHiddenTimer();
  } finally {
    _recycling = false;
  }
  return true;
}

/* ---- recycle triggers ----
 * (a) tab hidden ≥60 s        — a background/minimized tab gains nothing
 *     from holding the worker heap.
 * (b) idle ≥5 min AND pageCount>20 — small docs aren't worth the reinit
 *     cost; only worth it on the big binders the spike targeted.
 * Timers are armed lazily (only while pdfDoc is loaded) and cancelled on
 * real activity/visibility events rather than polling — cheap by design.
 */
var IDLE_RECYCLE_MS   = 5 * 60 * 1000;   // 5 min
var HIDDEN_RECYCLE_MS = 60 * 1000;       // 60 s
var IDLE_MIN_PAGES    = 20;              // small docs not worth recycling

var _idleTimer   = null;
var _hiddenTimer = null;

function _clearIdleTimer() { if (_idleTimer) { clearTimeout(_idleTimer); _idleTimer = null; } }
function _clearHiddenTimer() { if (_hiddenTimer) { clearTimeout(_hiddenTimer); _hiddenTimer = null; } }

function _armIdleTimer() {
  _clearIdleTimer();
  if (!pdfDoc || pageCount <= IDLE_MIN_PAGES) return;
  _idleTimer = setTimeout(function () { recycleDocWorker(); }, IDLE_RECYCLE_MS);
}

// loadPage()/_render() call this on real activity — re-arms the idle timer.
function _touchActivity() { _armIdleTimer(); }

if (typeof document !== "undefined") {
  document.addEventListener("visibilitychange", function () {
    if (document.hidden) {
      _clearHiddenTimer();
      _hiddenTimer = setTimeout(function () { recycleDocWorker(); }, HIDDEN_RECYCLE_MS);
    } else {
      _clearHiddenTimer();
      _touchActivity();
    }
  });
}

/* ---- thumbnail warm (PERF-20260702 companion 6) ----
 * After the case lands on the server, fetch thumbs SEQUENTIALLY at low
 * priority so the overview opens hot (measured ~200 ms/thumb cold, instant
 * warm). Sequential on purpose: avoids concurrent get_pixmap on the shared
 * fitz doc (S2 per-case lock not yet in place) and the 95-parallel burst
 * that lpm-8 fixed. Token-cancelled on reset/new upload. */
var _thumbWarmToken = 0;
async function _warmThumbs() {
  var tok = ++_thumbWarmToken;
  if (!caseId || !pageCount) return;
  for (var n = 1; n <= pageCount; n++) {
    if (tok !== _thumbWarmToken || !caseId) return;
    try { await fetch(api("/thumb/" + n)); } catch (_) { return; }
    await new Promise(function (r) { setTimeout(r, 120); });
  }
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

/* ---- openLocal / adoptCase: PERF-20260702 local-first open ----
 * openLocal(buf) renders from the user's local file bytes IMMEDIATELY —
 * first paint no longer waits for the server upload (measured 80 ms/MB;
 * 7.5 s of a 9.6 s cold open on a 91 MB binder). caseId may still be null
 * during the background-upload window; loadPage's guard accepts a loaded
 * pdfDoc as ready. adoptCase(cid) binds the already-loaded doc to the case
 * id once the upload completes so the next loadPage does NOT refetch /raw. */
async function _openLocal(buf, srcBlob) {
  var lib = await _loadPdfjsLib();
  _resetCache();
  _docWorker   = new lib.PDFWorker({ name: "bma-doc" });
  pdfDoc       = await lib.getDocument({ data: buf, worker: _docWorker }).promise;
  pdfDocCaseId = caseId || null;   // null while the background upload is in flight
  // srcBlob (the original File) lets a later recycle reinit with ZERO network
  // fetch. Backward-compat: callers that omit srcBlob still recycle fine once
  // adoptCase(cid) supplies a caseId to fall back to /raw for reinit.
  _docSource   = srcBlob ? { kind: "blob", blob: srcBlob }
               : (caseId ? { kind: "url", caseId: caseId } : null);
  _recycled    = false;
  return pdfDoc.numPages;
}
function _adoptCase(cid) {
  if (pdfDoc) pdfDocCaseId = cid;
  if (!_docSource) _docSource = { kind: "url", caseId: cid };
  else if (_docSource.kind === "url") _docSource.caseId = cid;
}

/* ---- _reinitDoc: (re)build pdfDoc + a fresh explicit worker (PERF-20260703) ----
 * Used both for the FIRST /raw load and to lazily reinit after
 * recycleDocWorker() tore the worker down. Prefers the retained local Blob
 * (_docSource.kind==="blob" — zero network, the whole point of local-first)
 * and falls back to a /raw refetch when only a caseId is known. Deliberately
 * does NOT touch pageDims/pageRot/_scanned — those are cheap metadata kept
 * across a recycle so fit()/registration stay correct without a re-fetch.
 */
async function _reinitDoc(lib) {
  _docWorker = new lib.PDFWorker({ name: "bma-doc" });
  var buf;
  if (_docSource && _docSource.kind === "blob") {
    buf = await _docSource.blob.arrayBuffer();
  } else {
    var cid = (_docSource && _docSource.kind === "url") ? _docSource.caseId : caseId;
    var resp = await fetch("/raw?case_id=" + cid);
    if (!resp.ok) throw new Error("HTTP " + resp.status);
    buf = await resp.arrayBuffer();
  }
  pdfDoc       = await lib.getDocument({ data: buf, worker: _docWorker }).promise;
  pdfDocCaseId = caseId;
  pageCache    = {};
  _pageLru     = [];
  _recycled    = false;
  if (!_docSource) _docSource = caseId ? { kind: "url", caseId: caseId } : null;
}

/* ---- loadPage: fetch PDF via /raw, render with PDF.js, call afterPage ----
 * FIX-B3: display index n maps to server page via pageMgr.serverNum(n) when
 * pending mutations exist (duplicate/reorder not yet flushed to server).
 * After applyFlush(), serverNum(n)===n for all pages → steady-state unchanged.
 * If serverNum returns null (merged page not yet flushed), show placeholder.
 */
async function loadPage(n) {
  if ((!caseId && !pdfDoc) || n < 1 || n > pageCount) return;  // pdfDoc-only = local-first window
  curPage = n;
  // FIX-B3: resolve display index to server page number
  var sn = (typeof pageMgr !== 'undefined' && pageMgr) ? pageMgr.serverNum(n) : n;
  if (sn === null) {
    // Merged page not yet flushed — show placeholder, skip PDF.js fetch
    showLoading("หน้า " + n + " (pending merge — Apply ก่อน)");
    setTimeout(hideLoading, 1500);
    afterPage();
    return;
  }
  showLoading("กำลังโหลดหน้า " + n + " / " + pageCount + "…");
  try {
    if (_forceRasterFallback) throw new Error("forced raster fallback (test hook)");
    var lib = await _loadPdfjsLib();
    // Reload PDF document if case changed, recycled away, or not yet loaded.
    // _reinitDoc prefers the retained local blob (zero /raw fetch) and only
    // falls back to a /raw refetch when no blob was kept — see _docSource.
    if (!pdfDoc || pdfDocCaseId !== caseId) {
      await _reinitDoc(lib);
    }
    // Cache the PDFPageProxy — keyed by SERVER page number (sn), not display index
    if (!pageCache[sn]) {
      pageCache[sn] = await pdfDoc.getPage(sn);
    }
    // Store dims keyed by display index n (matches curPage usage elsewhere)
    // pageDims = POST-INTRINSIC-ROTATION dims (the orientation server JPEG used to deliver).
    // page.view gives NATIVE pre-rotation dims — wrong for PDFs with /Rotate metadata.
    // PDF.js viewport at rotation=0 already applies intrinsic /Rotate, so its
    // width/height reflect the visually-correct landscape (e.g. RAMA4 A1 /Rotate=90).
    var natVp = pageCache[sn].getViewport({ scale: 1, rotation: 0 });
    pageDims[n] = { w: natVp.width, h: natVp.height };
    // Also alias under sn so _render can find the proxy via curPage if needed
    pageCache[n] = pageCache[sn];
    _touchPage(sn);
    if (n !== sn) _touchPage(n);
    pageData = { size: { orig_w_pt: pageDims[n].w, orig_h_pt: pageDims[n].h } };
    _touchActivity();  // PERF-20260703: page visits reset the idle-recycle timer
    hideLoading();
    fit();
    afterPage();
    if (typeof requestIdleCallback === "function")
      requestIdleCallback(function () { _prefetchAdjacent(n); }, { timeout: 2000 });
    else setTimeout(function () { _prefetchAdjacent(n); }, 250);
  } catch (err) {
    try {
      await _rasterFallbackLoad(n, sn);
      hideLoading();
      fit();
      afterPage();
      showLoading("โหมดภาพสำรอง (ตัวแสดงผล PDF หลักใช้ไม่ได้) — วัดได้ตามปกติ");
      setTimeout(hideLoading, 2000);
      return;
    } catch (err2) {
      hideLoading();
      alert("โหลดหน้า " + n + " ไม่ได้\n" + (err && err.message ? err.message : err));
    }
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
  _touchActivity();  // PERF-20260703: renders reset the idle-recycle timer

  var Vsnap = { k: V.k, ox: V.ox, oy: V.oy, rot: V.rot };
  var pgRot = pageRot[curPage] || 0;

  // PDF.js handles ALL rotation: intrinsic /Rotate via default rotation=0,
  // user/page rotation via the rotation arg. T is translate-only — places
  // the rendering at canvas (V.ox, V.oy).
  var thetaUser = ((Vsnap.rot + pgRot) % 360 + 360) % 360;
  var want      = RS * Vsnap.k;
  // Scanned pages: cap the raster scale; compensate in T (up) so geometry/
  // registration is IDENTICAL — only resolution is capped (it's a scan).
  var scale     = (_scanned[curPage] === true && want > SCANNED_MAX_SCALE) ? SCANNED_MAX_SCALE : want;
  var up        = want / scale;
  var viewport  = cp.getViewport({ scale: scale, rotation: thetaUser });

  var dpr = window.devicePixelRatio || 1;
  var T = [dpr * up, 0, 0, dpr * up, Vsnap.ox * dpr, Vsnap.oy * dpr];

  if (myToken !== _renderToken) return; // stale

  if (_offCanvas.width  !== cv.width)  _offCanvas.width  = cv.width;
  if (_offCanvas.height !== cv.height) _offCanvas.height = cv.height;
  var offCtx = _offCanvas.getContext("2d");
  // High-quality rasterization for the diff-blit downstream.
  offCtx.imageSmoothingEnabled = true;
  offCtx.imageSmoothingQuality = "high";
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

  _cachedV = { k: Vsnap.k, ox: Vsnap.ox, oy: Vsnap.oy, rot: Vsnap.rot, pgRot: pgRot, page: curPage };
  _cachedKey = _stateKey();

  if (_scanned[curPage] === undefined) {
    _scanned[curPage] = null;                       // pending — no re-entry
    _detectScanned(curPage);
  }

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

  // Raster-fallback branch: server JPEG in curImg (image px = pt*RS with pgRot
  // baked via ?rot) drawn with the same view transform ptToScreen uses.
  // instanceof guard keeps legacy test shims (curImg = dummy truthy) harmless.
  if (!pdfDoc && typeof HTMLImageElement !== "undefined" && curImg instanceof HTMLImageElement) {
    ctx.save();
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.translate(V.ox, V.oy);
    ctx.rotate(V.rot * Math.PI / 180);
    ctx.scale(V.k, V.k);
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = "high";
    ctx.drawImage(curImg, 0, 0);
    ctx.restore();
    return;
  }

  // ---- Phase 1: blit cached _offCanvas with diff-transform (smooth) ----
  //
  // offCanvas is cv-sized; content was rendered with translate to
  // (V.ox_cached*dpr, V.oy_cached*dpr) at scale=RS*V.k_cached. For PDF-pt p:
  //   cached offCanvas device-px = (p.x*RS*V.k_cached + V.ox_cached) * dpr
  //   target ctx device-px        = (p.x*RS*V.k + V.ox) * dpr
  //
  // Compose affine: ss = V.k / V.k_cached, translate = V.ox - ss*V.ox_cached.
  //   At V.k = V.k_cached: ss = 1, blit at 1:1 (sharp).
  //   At V.k < V.k_cached: ss < 1 → downscale (always sharp).
  //   At V.k > V.k_cached: ss > 1 → upscale (bilinear blur). We mitigate via
  //     imageSmoothingQuality="high" (cubic in Chrome) which produces noticeably
  //     less blur than browser default.
  if (_cachedV && _offCanvas && _offCanvas.width > 0 &&
      V.rot === _cachedV.rot && curPage === _cachedV.page &&
      (pageRot[curPage] || 0) === _cachedV.pgRot) {
    var ss = V.k / _cachedV.k;
    ctx.save();
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = "high";
    ctx.setTransform(ss, 0, 0, ss,
      (V.ox - ss * _cachedV.ox) * dpr,
      (V.oy - ss * _cachedV.oy) * dpr);
    ctx.drawImage(_offCanvas, 0, 0);
    ctx.restore();
  } else if (pageDims[curPage]) {
    // No usable cache yet (first render pending, or rotation/page just changed)
    // → placeholder rect so the user sees the page bounds rather than blank.
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

  // ---- Phase 2: schedule re-render when cache key drifts from current state ----
  // The diff-blit handles the visual immediately; PDF.js refreshes the cache
  // ~30 ms later. Token-based stale guard prevents infinite loops.
  if (!pdfDoc || !pageCache[curPage]) return;
  var key = _stateKey();
  if (key === _cachedKey && _pendingRenderTask === null) return;  // up-to-date

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
  _thumbWarmToken++;
  // PERF-20260703: we now own an explicit worker per doc — tear it down here
  // too, or every new upload/loadProject would orphan one (worse than the
  // implicit-worker leak this whole sprint exists to fix).
  if (pdfDoc) { try { pdfDoc.destroy(); } catch (_) {} }
  if (_docWorker) { try { _docWorker.destroy(); } catch (_) {} }
  pdfDoc       = null;
  pdfDocCaseId = null;
  _docWorker   = null;
  _docSource   = null;
  _recycled    = false;
  pageCache    = {};
  pageDims     = {};
  _pageLru     = [];
  pageRot      = {};
  curImg       = null;
  _scanned     = {};
  _scannedHinted = {};
  _cachedV     = null;
  _cachedKey   = null;
  _clearIdleTimer();
  _clearHiddenTimer();
  if (_offCanvas) {
    _offCanvas.width = 0;  // also clears
  }
}

/* ---- UX batch2 F-6: local-first gate message ----
 * With local-first open, pdfDoc is loaded (PDF visibly open) while caseId is
 * still null during the background upload. Server-gated actions must NOT say
 * "เปิด PDF ก่อน" then — that's wrong/confusing. gateNoCaseMsg() returns the
 * upload-in-progress message when a local doc IS open but caseId is pending,
 * and the original "open a PDF" message when nothing is open at all. Call sites
 * replace  alert("เปิด PDF ก่อน")  with  alert(gateNoCaseMsg()). */
function gateNoCaseMsg() {
  if (typeof caseId !== "undefined" && !caseId && pdfDoc)
    return "กำลังอัปโหลดไฟล์ขึ้นเซิร์ฟเวอร์ รอสักครู่แล้วลองใหม่";
  return "เปิด PDF ก่อน";
}
window.gateNoCaseMsg = gateNoCaseMsg;

/* ---- public API ---- */
window.PageRenderer = {
  hasDoc:     function () { return !!pdfDoc; },
  loadPage:   loadPage,
  drawImage:  _drawImage,
  fit:        fit,
  resize:     resize,
  resetCache: _resetCache,
  ready:      _ready,
  openLocal:  _openLocal,
  adoptCase:  _adoptCase,
  warmThumbs: _warmThumbs,
  recycleNow: recycleDocWorker,   // PERF-20260703: manual/test trigger for worker recycle
  _test_forceRasterFallback: function (v) { _forceRasterFallback = !!v; },
  _test_scanned: function () { return _scanned; }
};
