/* freehand.js — FREEHAND-LEN: Alt-hold streaming sub-mode for the lite path
 * tool (⇧D). Ports the design SHIPPED in proto (INV-2026-05-17-001, commit
 * 023b988, Approach D): Alt-hold during draw = streaming sample (distance-bin
 * >=6px screen distance), snap/CL bypassed while streaming, release Alt
 * returns to click mode (mixed click+drag in one draft), finish decimates
 * the streamed run via rdpSimplify (kept-exact clicked vertices, decimated
 * only the raw stream — mirrors proto's design).
 *
 * Loaded AFTER measure-engine.js, BEFORE the inline script (needs the inline
 * script's global screenToPt() — called only inside function bodies, at
 * runtime, by which point the inline script has already run; same pattern
 * draw-arc.js uses for ptToScreen/computeArcEdge).
 *
 * Exposes globals: fhStart, fhSample, fhActive, fhCommit, fhTakeMeta,
 *   fhCancel, fhRenderPreview, rdpSimplify.
 * State lives in module-scope _fhDraft / _fhMeta; accessible from
 * ui-lite.html handlers only via the exported functions.
 */

/* ---------- rdpSimplify ----------
 * Ported verbatim from proto ui.html (INV-2026-05-17-001, commit 023b988,
 * proto/ui.html:1665). Ramer-Douglas-Peucker polyline simplification.
 * Pure function — no scale, no state. Caller decides tolerance units
 * (here: screen px, matching the raw stream's own coordinate space). */
function rdpSimplify(pts, tol) {
  if (!Array.isArray(pts) || pts.length < 3) return Array.isArray(pts) ? pts.slice() : [];
  function rec(start, end, out) {
    var maxD = 0, maxI = -1;
    var a = pts[start], b = pts[end];
    var dx = b.x - a.x, dy = b.y - a.y, len2 = dx * dx + dy * dy;
    for (var i = start + 1; i < end; i++) {
      var p = pts[i], d;
      if (len2 === 0) { d = Math.hypot(p.x - a.x, p.y - a.y); }
      else {
        var t = ((p.x - a.x) * dx + (p.y - a.y) * dy) / len2;
        var tt = Math.max(0, Math.min(1, t));
        d = Math.hypot(p.x - (a.x + tt * dx), p.y - (a.y + tt * dy));
      }
      if (d > maxD) { maxD = d; maxI = i; }
    }
    if (maxD > tol && maxI >= 0) { rec(start, maxI, out); out.push(pts[maxI]); rec(maxI, end, out); }
  }
  var out = [pts[0]];
  rec(0, pts.length - 1, out);
  out.push(pts[pts.length - 1]);
  return out;
}

/* _fhDraft: streaming-burst state. raw pts are screen/canvas px (same space
 * as e.offsetX/e.offsetY — the caller never mixes these with PDF coords). */
var _fhDraft = { active: false, raw: [], last: null };
/* _fhMeta: accumulates across ALL bursts within the current draft (a path can
 * mix click + Alt-drag + click + Alt-drag...); consumed once by finishDraft
 * via fhTakeMeta(), or discarded via fhTakeMeta()'s return being ignored. */
var _fhMeta = null;

function fhStart(sx, sy) {
  _fhDraft.active = true;
  _fhDraft.raw = [{ x: sx, y: sy }];
  _fhDraft.last = { x: sx, y: sy };
}

/* fhSample() — distance-bin gate (>=stepPx screen distance since last
 * accepted sample). Returns true iff a new sample was accepted (caller
 * should redraw only then, matching proto's gate). */
function fhSample(sx, sy, stepPx) {
  if (!_fhDraft.active) return false;
  stepPx = stepPx || 6;
  if (_fhDraft.last) {
    var d = Math.hypot(sx - _fhDraft.last.x, sy - _fhDraft.last.y);
    if (d < stepPx) return false;
  }
  _fhDraft.raw.push({ x: sx, y: sy });
  _fhDraft.last = { x: sx, y: sy };
  return true;
}

function fhActive() { return _fhDraft.active; }

/* fhCommit(draft, tolerancePx) — decimates the raw burst via rdpSimplify,
 * converts each simplified point to PDF coords (screenToPt, inline-script
 * global), appends to draft (skipping the first point when draft already
 * has vertices, to avoid a duplicate at the click->drag join — mirrors
 * proto's `startIdx = mPts.length>0?1:0`). Mutates draft in place. */
function fhCommit(draft, tolerancePx) {
  if (!_fhDraft.active) return { count: 0 };
  tolerancePx = tolerancePx || 4;
  var raw = _fhDraft.raw;
  _fhDraft.active = false;
  var rawCount = raw.length;
  if (raw.length < 2) { _fhDraft.raw = []; _fhDraft.last = null; return { count: 0, rawCount: rawCount }; }
  var simplified = rdpSimplify(raw, tolerancePx);
  var startIdx = draft.length > 0 ? 1 : 0;
  var appended = 0;
  for (var i = startIdx; i < simplified.length; i++) {
    draft.push(screenToPt(simplified[i].x, simplified[i].y));
    appended++;
  }
  if (!_fhMeta) _fhMeta = { tolerance: tolerancePx, originalCount: 0 };
  _fhMeta.originalCount += rawCount;
  _fhDraft.raw = [];
  _fhDraft.last = null;
  return { count: appended, rawCount: rawCount, simplifiedCount: simplified.length };
}

/* fhTakeMeta() — pop+reset the accumulated freeform metadata for the current
 * draft. Called once by finishDraft() on success (attach as obj.freeform),
 * or on any draft-discard path (Escape / too-few-points) to avoid leaking
 * metadata into the NEXT drawn object. */
function fhTakeMeta() {
  var m = _fhMeta;
  _fhMeta = null;
  return m;
}

/* fhCancel() — abandon an in-progress burst without committing (Esc while
 * Alt-drag is somehow still held; defensive — mouseup normally commits). */
function fhCancel() {
  _fhDraft.active = false;
  _fhDraft.raw = [];
  _fhDraft.last = null;
}

/* fhRenderPreview(ctx) — live raw-stroke preview while streaming (screen-px,
 * no transform needed — same space ptToScreen() output already uses). */
function fhRenderPreview(ctx) {
  if (!_fhDraft.active || _fhDraft.raw.length < 2) return;
  var raw = _fhDraft.raw;
  ctx.save();
  ctx.beginPath();
  ctx.moveTo(raw[0].x, raw[0].y);
  for (var i = 1; i < raw.length; i++) ctx.lineTo(raw[i].x, raw[i].y);
  ctx.strokeStyle = '#39d98a';
  ctx.lineWidth = 2;
  ctx.globalAlpha = 0.85;
  ctx.stroke();
  ctx.restore();
}
