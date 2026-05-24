/* centerline-snap.js — INV-2026-05-24-002a (centerline snap for area tool)
 *
 * Shipped from /bma-invent 2026-05-24-22-14 spike (Approach A enhanced with
 * post-draw per-edge PCA + corner intersection). Verified ±0.185% accuracy on
 * synthetic dashed-pentagon (target ±0.5%) at <10ms/vertex (target ≤16ms).
 *
 * Source artifact: docs/invent/centerline-snap-dashed-boundary.md
 * Spike:           proto/sandbox/invent-centerline-snap-dashed-boundary.html
 *
 * Public API (window.CL_*):
 *   CL_snapCanvasToCenterline(ctx, cx, cy, opts)
 *     -> {x, y, found, cost}    // step 1, per-click / per-mousemove
 *   CL_refineCornersOnSkeleton(ctx, pts, opts)
 *     -> {pts, cost, refined}   // step 2, post-draw polygon-level
 *
 * No CDN dependency — Zhang-Suen + Otsu threshold inline.
 * Does NOT touch polyAreaM2 / pdfToC / cToPdf / RS / snap engine.
 */
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
