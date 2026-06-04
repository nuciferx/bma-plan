/* centerline-snap.js — vendored from proto INV-2026-05-24-002a 6db0461
 *
 * Section A: algorithm (VERBATIM from proto/static/js/centerline-snap.js).
 *   Do NOT modify — drift-locked with proto per lite-vendoring contract.
 *   Re-sync by copying proto's IIFE body intact whenever proto changes.
 *
 * Section B: lite-specific glue (NEW, lite ONLY).
 *   Provides CL_litePolyClick / CL_litePolyFinish for ui-lite.html hooks.
 *
 * Public API:
 *   [Section A]
 *     window.CL_snapCanvasToCenterline(ctx, cx, cy, opts) -> {x,y,found,cost}
 *     window.CL_refineCornersOnSkeleton(ctx, pts, opts)  -> {pts,cost,refined}
 *     window.CL_otsuThreshold, window.CL_zhangSuenThin   (exposed for tests)
 *     window.CL_VERSION
 *   [Section B]
 *     window.centerlineSnapOn          (bool, persisted to localStorage)
 *     window.CL_litePolyClick(p, screenX, screenY) -> pt|null
 *     window.CL_litePolyFinish(pts)                -> [{x,y}]|null
 */

/* =========================================================================
 * SECTION A — ALGORITHM — VERBATIM FROM PROTO (do not edit)
 * ========================================================================= */
(function () {
  "use strict";

  var DEFAULT_ROI = 140;       // px — research-suggested size to span typical dash gaps
  var DEFAULT_DARK_FALLBACK = 384;  // sum RGB threshold if Otsu fails

  // -------------------- Otsu threshold (adaptive) ----------------------------
  // Inputs: histogram of pixel "darkness" 0..765 (sum of RGB).
  // Returns the threshold that maximizes between-class variance.
  function otsuThreshold(hist, total) {
    var sum = 0;
    for (var i = 0; i < hist.length; i++) sum += i * hist[i];
    var sumB = 0, wB = 0, maxVar = 0, threshold = DEFAULT_DARK_FALLBACK;
    for (var t = 0; t < hist.length; t++) {
      wB += hist[t];
      if (wB === 0) continue;
      var wF = total - wB;
      if (wF === 0) break;
      sumB += t * hist[t];
      var mB = sumB / wB;
      var mF = (sum - sumB) / wF;
      var v = wB * wF * (mB - mF) * (mB - mF);
      if (v > maxVar) { maxVar = v; threshold = t; }
    }
    return threshold;
  }

  // -------------------- Zhang-Suen thinning ----------------------------------
  // Operates on a Uint8Array (0/1) of size w*h, in place. O(n*k) k ~ 5-20.
  function zhangSuenThin(binary, w, h) {
    var get = function (x, y) { return binary[y * w + x] | 0; };
    var total = 0;
    while (true) {
      var removedRound = 0;
      for (var pass = 0; pass < 2; pass++) {
        var toRemove = [];
        for (var y = 1; y < h - 1; y++) {
          for (var x = 1; x < w - 1; x++) {
            if (!get(x, y)) continue;
            var p2 = get(x, y - 1), p3 = get(x + 1, y - 1),
                p4 = get(x + 1, y),     p5 = get(x + 1, y + 1),
                p6 = get(x, y + 1),     p7 = get(x - 1, y + 1),
                p8 = get(x - 1, y),     p9 = get(x - 1, y - 1);
            var B = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9;
            if (B < 2 || B > 6) continue;
            var seq = [p2, p3, p4, p5, p6, p7, p8, p9, p2];
            var A = 0;
            for (var k = 0; k < 8; k++) if (seq[k] === 0 && seq[k + 1] === 1) A++;
            if (A !== 1) continue;
            if (pass === 0) {
              if (p2 * p4 * p6 !== 0) continue;
              if (p4 * p6 * p8 !== 0) continue;
            } else {
              if (p2 * p4 * p8 !== 0) continue;
              if (p2 * p6 * p8 !== 0) continue;
            }
            toRemove.push(y * w + x);
          }
        }
        for (var r = 0; r < toRemove.length; r++) binary[toRemove[r]] = 0;
        removedRound += toRemove.length;
      }
      total += removedRound;
      if (removedRound === 0) break;
      if (total > w * h * 5) break;
    }
  }

  // -------------------- Step 1: per-click ROI centerline snap ----------------
  // Grabs a ROI around (cx,cy), Otsu binarises, thins, returns nearest
  // skeleton pixel to (cx,cy) in canvas coords. If ROI has no foreground (or
  // foreground is too sparse to thin), returns the original (cx,cy).
  function snapCanvasToCenterline(ctxArg, cx, cy, opts) {
    opts = opts || {};
    var R = opts.roi || DEFAULT_ROI;
    var half = R / 2;
    var t0 = (performance && performance.now) ? performance.now() : Date.now();
    var canvasEl = ctxArg.canvas;
    var x0 = Math.max(0, Math.min(canvasEl.width - R, Math.round(cx - half)));
    var y0 = Math.max(0, Math.min(canvasEl.height - R, Math.round(cy - half)));
    var img;
    try { img = ctxArg.getImageData(x0, y0, R, R); }
    catch (e) { return { x: cx, y: cy, found: false, cost: 0, reason: "no-imagedata" }; }
    // Build histogram of darkness for Otsu.
    var hist = new Uint32Array(766);
    var data = img.data;
    var n = R * R;
    for (var i = 0, j = 0; j < n; i += 4, j++) {
      hist[data[i] + data[i + 1] + data[i + 2]]++;
    }
    var thr = otsuThreshold(hist, n);
    // Binarise: dark < threshold = 1.
    var binary = new Uint8Array(n);
    var fgCount = 0;
    for (var ii = 0, jj = 0; jj < n; ii += 4, jj++) {
      if (data[ii] + data[ii + 1] + data[ii + 2] < thr) { binary[jj] = 1; fgCount++; }
    }
    // Sanity: if ROI is solid (>50% foreground) or empty (<0.2%) -> bail.
    var t1 = (performance && performance.now) ? performance.now() : Date.now();
    if (fgCount < n * 0.002 || fgCount > n * 0.5) {
      return { x: cx, y: cy, found: false, cost: t1 - t0, reason: "fg-out-of-range" };
    }
    zhangSuenThin(binary, R, R);
    // Find nearest 1-pixel to ROI centre.
    var localCx = Math.round(cx - x0), localCy = Math.round(cy - y0);
    var bestDist = Infinity, bestLx = -1, bestLy = -1;
    for (var ly = 0; ly < R; ly++) {
      var dyy = ly - localCy;
      for (var lx = 0; lx < R; lx++) {
        if (!binary[ly * R + lx]) continue;
        var dxx = lx - localCx;
        var d = dxx * dxx + dyy * dyy;
        if (d < bestDist) { bestDist = d; bestLx = lx; bestLy = ly; }
      }
    }
    var t2 = (performance && performance.now) ? performance.now() : Date.now();
    if (bestLx < 0) return { x: cx, y: cy, found: false, cost: t2 - t0, reason: "no-skeleton" };
    return { x: x0 + bestLx, y: y0 + bestLy, found: true, cost: t2 - t0 };
  }

  // -------------------- Step 2: post-draw per-edge PCA + corner intersection -
  // For each edge of the (already snapped) polygon, sample N points along it,
  // snap each to the centerline skeleton, then PCA-fit a line through the
  // samples. For each corner, intersect adjacent edges' lines to recover the
  // true corner location. This fixes the systematic "corner-chamfering" bias
  // of nearest-skeleton-pixel snap at corners.
  function refineCornersOnSkeleton(ctxArg, pts, opts) {
    opts = opts || {};
    var nSample = opts.nSample || 5;
    var roi = opts.roi || DEFAULT_ROI;
    var t0 = (performance && performance.now) ? performance.now() : Date.now();
    var n = pts.length;
    if (n < 3) return { pts: pts.slice(), cost: 0, refined: false, reason: "need-3-pts" };
    var lines = [];
    for (var i = 0; i < n; i++) {
      var p0 = pts[i], p1 = pts[(i + 1) % n];
      var samples = [];
      for (var kk = 1; kk <= nSample; kk++) {
        var t = kk / (nSample + 1);
        var sx = p0[0] + (p1[0] - p0[0]) * t;
        var sy = p0[1] + (p1[1] - p0[1]) * t;
        var r = snapCanvasToCenterline(ctxArg, sx, sy, { roi: roi });
        if (r.found) samples.push([r.x, r.y]);
      }
      if (samples.length < 2) { lines.push(null); continue; }
      // PCA to find principal direction.
      var mx = 0, my = 0;
      for (var s = 0; s < samples.length; s++) { mx += samples[s][0]; my += samples[s][1]; }
      mx /= samples.length; my /= samples.length;
      var Sxx = 0, Syy = 0, Sxy = 0;
      for (var ss = 0; ss < samples.length; ss++) {
        var dxs = samples[ss][0] - mx, dys = samples[ss][1] - my;
        Sxx += dxs * dxs; Syy += dys * dys; Sxy += dxs * dys;
      }
      var trace = Sxx + Syy;
      var det1 = Sxx * Syy - Sxy * Sxy;
      var lambda = trace / 2 + Math.sqrt(Math.max(0, (trace / 2) * (trace / 2) - det1));
      var dx, dy;
      if (Math.abs(Sxy) > 1e-6) { dx = lambda - Syy; dy = Sxy; }
      else { dx = (Sxx >= Syy) ? 1 : 0; dy = (Sxx >= Syy) ? 0 : 1; }
      var L = Math.hypot(dx, dy) || 1; dx /= L; dy /= L;
      // Line implicit a*x + b*y + c = 0 with normal (-dy, dx)
      lines.push({ a: -dy, b: dx, c: dy * mx - dx * my });
    }
    var refined = new Array(n);
    for (var ci = 0; ci < n; ci++) {
      var prev = lines[(ci - 1 + n) % n];
      var cur = lines[ci];
      if (!prev || !cur) { refined[ci] = pts[ci].slice(); continue; }
      var det = prev.a * cur.b - cur.a * prev.b;
      if (Math.abs(det) < 1e-6) { refined[ci] = pts[ci].slice(); continue; }
      var x = (prev.b * cur.c - cur.b * prev.c) / det;
      var y = (cur.a * prev.c - prev.a * cur.c) / det;
      // Guard: if refinement moves the vertex more than ROI/2, reject — the
      // line fit is unreliable at this corner (sharp angle / short edge).
      var px = pts[ci][0], py = pts[ci][1];
      if (Math.hypot(x - px, y - py) > roi / 2) refined[ci] = pts[ci].slice();
      else refined[ci] = [x, y];
    }
    var t1 = (performance && performance.now) ? performance.now() : Date.now();
    return { pts: refined, cost: t1 - t0, refined: true };
  }

  // Expose public API.
  window.CL_snapCanvasToCenterline = snapCanvasToCenterline;
  window.CL_refineCornersOnSkeleton = refineCornersOnSkeleton;
  window.CL_otsuThreshold = otsuThreshold;        // exposed for E2E test
  window.CL_zhangSuenThin = zhangSuenThin;        // exposed for E2E test
  window.CL_VERSION = "1.0.0";
})();

/* =========================================================================
 * SECTION B — LITE-SPECIFIC GLUE (new, lite only)
 * ========================================================================= */
(function () {
  "use strict";

  // ---- State + persistence ----
  window.centerlineSnapOn = localStorage.getItem("lite.centerlineSnap") === "1";

  // ---- Boot self-install (deferred until DOM ready) ----
  function installCenterlineBtn() {
    var cvEl = document.getElementById("cv");
    if (!cvEl || !window.screenToPt || !window.ptToScreen) {
      setTimeout(installCenterlineBtn, 100);
      return;
    }

    // Inject inline CSS for .active state (visible feedback) ONCE.
    if (!document.getElementById("lite-btn-centerline-css")) {
      var st = document.createElement("style");
      st.id = "lite-btn-centerline-css";
      // BUG-20260525-lite-cl-position: place inside #hud-br ABOVE zoomctl,
      // styled to match zoom buttons. Stacked via flex-column on the hud
      // container's first child. `.active` = green pill.
      st.textContent = [
        "#hud-br{display:flex;flex-direction:column;gap:4px;align-items:flex-end;}",
        "#lite-btn-centerline{background:#222a37;color:#ccc;border:1px solid var(--line,#555);height:24px;padding:0 6px;border-radius:5px;cursor:pointer;font-size:12px;line-height:1;}",
        "#lite-btn-centerline:hover{background:#2d3848;}",
        "#lite-btn-centerline.active{background:#1f6b3a !important;color:#fff !important;border-color:#3acc77 !important;box-shadow:0 0 0 2px rgba(58,204,119,.25);}"
      ].join("");
      document.head.appendChild(st);
    }

    // Place button inside #hud-br (bottom-right HUD) so it stacks above the
    // zoom controls instead of overlapping them. Fallback to floating top-right
    // if #hud-br is missing for some reason.
    var btn = document.getElementById("lite-btn-centerline");
    if (!btn) {
      btn = document.createElement("button");
      btn.id = "lite-btn-centerline";
      btn.textContent = "⊙ CL";
      btn.title = "Centerline snap (เส้นปะหนา → กลางเส้น). คลิกเพื่อเปิด/ปิด — สีเขียว=เปิด, เทา=ปิด.";
      var hudBr = document.getElementById("hud-br");
      if (hudBr) {
        // Prepend so it sits ABOVE the existing zoomctl.
        hudBr.insertBefore(btn, hudBr.firstChild);
      } else {
        // Fallback: top-right floating (far from zoom in bottom-right).
        btn.style.cssText = "position:fixed;top:48px;right:10px;z-index:9999;";
        document.body.appendChild(btn);
      }
    }

    // Reflect initial state.
    if (window.centerlineSnapOn) btn.classList.add("active");

    btn.addEventListener("click", function () {
      window.centerlineSnapOn = !window.centerlineSnapOn;
      localStorage.setItem("lite.centerlineSnap", window.centerlineSnapOn ? "1" : "0");
      btn.classList.toggle("active", window.centerlineSnapOn);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", installCenterlineBtn);
  } else {
    installCenterlineBtn();
  }

  // ---- DPR (devicePixelRatio) bridge ----
  // Lite's canvas uses `cv.width = clientWidth * dpr` (line 260 of ui-lite.html)
  // so canvas BITMAP coords differ from CSS coords by a factor of dpr.
  // `getImageData` is bitmap-space; mouse offsetX/Y + ptToScreen/screenToPt
  // are all CSS-space. We must bridge.
  function _dpr() { return window.devicePixelRatio || 1; }

  // ---- Visual click feedback (BUG-20260525-lite-cl-misses observability) ----
  // Field report 2026-05-25: "บางจุดถูก บางจุดผิด" on real cadastral PDF.
  // Without feedback the user can't tell which clicks snapped vs fell back.
  // Show a tiny green dot at the snap location for success, red X at cursor
  // for miss. ~600ms fade. Pure DOM, no canvas touch.
  function _flashFeedback(screenX, screenY, snappedScreenX, snappedScreenY, ok) {
    var cvEl = document.getElementById("cv");
    if (!cvEl) return;
    var r = cvEl.getBoundingClientRect();
    var dot = document.createElement("div");
    var px = (ok ? snappedScreenX : screenX);
    var py = (ok ? snappedScreenY : screenY);
    dot.style.cssText = [
      "position:fixed",
      "left:" + (r.left + px - 6) + "px",
      "top:" + (r.top + py - 6) + "px",
      "width:12px", "height:12px",
      "border-radius:50%",
      "pointer-events:none",
      "z-index:9998",
      "background:" + (ok ? "rgba(58,204,119,.9)" : "rgba(220,80,80,.9)"),
      "box-shadow:0 0 6px " + (ok ? "rgba(58,204,119,.6)" : "rgba(220,80,80,.6)"),
      "transition:opacity .5s ease-out, transform .5s ease-out"
    ].join(";");
    document.body.appendChild(dot);
    setTimeout(function () {
      dot.style.opacity = "0";
      dot.style.transform = "scale(2)";
    }, 50);
    setTimeout(function () { try { dot.remove(); } catch (_) {} }, 700);
  }

  // ---- Click-hook helper: called per mousedown point in poly tool ----
  // Inputs:  p ({x,y} PDF pt, already computed by caller)
  //          screenX/screenY (CSS pixels — e.offsetX/e.offsetY from mousedown)
  // Returns: corrected {x,y} PDF pt, or null (caller falls back to original p).
  //
  // Retry ladder (BUG-20260525-lite-cl-misses): if ROI 140 fails (cursor
  // in a dash gap or ROI captures too few/many dark pixels), retry with
  // 200 and then 280. Cost ladder: 4ms / 8ms / 16ms — still within budget
  // even on the slowest retry. Improves hit-rate on real cadastral scans.
  window.CL_litePolyClick = function (p, screenX, screenY) {
    if (!window.centerlineSnapOn) return null;
    if (typeof window.CL_snapCanvasToCenterline !== "function") return null;
    var cvEl = document.getElementById("cv");
    if (!cvEl) return null;
    var ctx2d = cvEl.getContext("2d");
    var dpr = _dpr();
    var bx = screenX * dpr, by = screenY * dpr;
    var roiLadder = [140, 200, 280];
    var result = null;
    for (var i = 0; i < roiLadder.length; i++) {
      result = window.CL_snapCanvasToCenterline(ctx2d, bx, by, { roi: roiLadder[i] });
      if (result && result.found) break;
    }
    if (!result || !result.found) {
      _flashFeedback(screenX, screenY, screenX, screenY, false);
      return null;
    }
    if (typeof window.screenToPt !== "function") return null;
    var snappedScreenX = result.x / dpr, snappedScreenY = result.y / dpr;
    _flashFeedback(screenX, screenY, snappedScreenX, snappedScreenY, true);
    // Algorithm returns bitmap coords; convert back to CSS for screenToPt.
    return window.screenToPt(snappedScreenX, snappedScreenY);
  };

  // ---- Finish-hook helper: called post-Enter on poly draft ----
  window.CL_litePolyFinish = function (pts) {
    if (!window.centerlineSnapOn) return null;
    if (!pts || pts.length < 3) return null;
    if (typeof window.CL_refineCornersOnSkeleton !== "function") return null;
    if (typeof window.ptToScreen !== "function") return null;
    if (typeof window.screenToPt !== "function") return null;
    var cvEl = document.getElementById("cv");
    if (!cvEl) return null;
    var ctx2d = cvEl.getContext("2d");
    var dpr = _dpr();

    // Convert {x,y} PDF pts -> CSS canvas coords -> bitmap coords for algorithm.
    var canvasPts = pts.map(function (p) {
      var sp = window.ptToScreen(p);
      return [sp.x * dpr, sp.y * dpr];
    });

    var res = window.CL_refineCornersOnSkeleton(ctx2d, canvasPts);
    if (!res || !res.refined) return null;

    // Convert bitmap pts back -> CSS coords -> PDF pts.
    var refined = res.pts.map(function (cp) {
      return window.screenToPt(cp[0] / dpr, cp[1] / dpr);
    });
    return refined;
  };
})();
