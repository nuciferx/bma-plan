/* draw-arc.js — Arc-edge polygon mechanic for lite poly tool (LCURVE-1).
 *
 * Owns the arc-draft sub-state for the polygon draw tool.
 * Loaded AFTER measure-engine.js (needs computeArcEdge, centroid).
 * Exposes global functions: arcToggle, arcOnClick, arcCancel,
 *   arcRenderPreview, arcRenderEdge, arcHUDText.
 *
 * State lives in module-scope `_arcDraft`; accessible from ui-lite.html
 * handlers via the exported functions only.
 */

/* _arcDraft.pending  — true when next click should absorb as through-point.
 * _arcDraft.throughPt — PDF-coord through-point once set; null otherwise. */
var _arcDraft = { pending: false, throughPt: null };

/* ---------- helpers ---------- */

/* centroid estimate of an array of PDF-coord points (shared with lite centroid fn). */
function _arcCentroidEst(pts) {
  if (!pts || !pts.length) return { x: 0, y: 0 };
  var x = 0, y = 0;
  for (var i = 0; i < pts.length; i++) { x += pts[i].x; y += pts[i].y; }
  return { x: x / pts.length, y: y / pts.length };
}

/* ---------- public API ---------- */

/**
 * arcToggle() — call when user presses A while actively drawing a poly draft.
 * Flips _arcDraft.pending; clears throughPt if turning off.
 * The HUD hint updates via arcHUDText() on the next draw().
 * Only acts when currently drawing poly (caller must guard).
 */
function arcToggle() {
  if (_arcDraft.pending) {
    /* second A while pending → cancel arc mode, back to straight */
    _arcDraft.pending = false;
    _arcDraft.throughPt = null;
  } else {
    _arcDraft.pending = true;
    _arcDraft.throughPt = null;
  }
}

/**
 * arcOnClick(canvasPt, draft) → { consumed: bool, edgeRecord: object|null }
 *
 * canvasPt: PDF-coord point (already resolved through snap/angle-lock by caller).
 * draft:    state.draft (the live array of PDF-coord points for the in-progress poly).
 *
 * Returns:
 *   { consumed: true }                                  — swallowed as through-point; caller must NOT push vertex.
 *   { consumed: false, edgeRecord: null }               — not in arc mode; normal click flow.
 *   { consumed: false, edgeRecord: {edgeType,arcSweep,arcThrough} } — arc done; caller pushes vertex
 *                                                          AND stores edgeRecord at draft.edges[draft.pts.length-2]
 *                                                          AFTER the push (i.e. the edge from prevPt to newPt).
 */
function arcOnClick(canvasPt, draft) {
  if (!_arcDraft.pending) {
    return { consumed: false, edgeRecord: null };
  }

  if (!_arcDraft.throughPt) {
    /* First click in arc mode → absorb as through-point */
    _arcDraft.throughPt = { x: canvasPt.x, y: canvasPt.y };
    return { consumed: true, edgeRecord: null };
  }

  /* Second click → compute arc edge between prevPt and newPt via throughPt */
  var pts = draft || [];
  var prevPt = pts.length > 0 ? pts[pts.length - 1] : { x: 0, y: 0 };
  /* centroid estimate = existing pts + the incoming newPt */
  var centEst = _arcCentroidEst(pts.concat([canvasPt]));
  var arc = computeArcEdge(prevPt, canvasPt, _arcDraft.throughPt, centEst);
  var edgeRecord = {
    edgeType: 'arc',
    arcSweep: arc.sweep,
    arcThrough: { x: _arcDraft.throughPt.x, y: _arcDraft.throughPt.y }
  };
  /* Reset arc-draft sub-state (not pending anymore; next edge is straight) */
  _arcDraft.pending = false;
  _arcDraft.throughPt = null;
  /* consumed=false so caller still pushes the vertex */
  return { consumed: false, edgeRecord: edgeRecord };
}

/**
 * arcCancel() — called on Esc.
 * If arc draft was in progress (pending set or throughPt set), resets and returns true.
 * Returns false if nothing was active (caller should proceed with normal Esc).
 */
function arcCancel() {
  if (_arcDraft.pending || _arcDraft.throughPt) {
    _arcDraft.pending = false;
    _arcDraft.throughPt = null;
    return true;
  }
  return false;
}

/**
 * arcRenderPreview(ctx, lastPtPDF, cursorPDF)
 *
 * If throughPt is set, draw a curved preview from lastPtPDF through throughPt
 * toward cursorPDF using computeArcEdge.  Otherwise no-op.
 *
 * Both pts are in PDF coordinates. The function converts internally via ptToScreen.
 * ctx must already have save/restore guards where needed (caller's responsibility
 * for dash/color state).
 */
function arcRenderPreview(ctx, lastPtPDF, cursorPDF) {
  if (!_arcDraft.throughPt || !lastPtPDF || !cursorPDF) return;
  /* Build a temporary arc from lastPtPDF → cursorPDF via throughPt */
  var centEst = {
    x: (lastPtPDF.x + _arcDraft.throughPt.x + cursorPDF.x) / 3,
    y: (lastPtPDF.y + _arcDraft.throughPt.y + cursorPDF.y) / 3
  };
  var arc = computeArcEdge(lastPtPDF, cursorPDF, _arcDraft.throughPt, centEst);
  if (!arc.center || Math.abs(arc.sweep) < 0.001) return;
  /* Convert to screen coords */
  var A = ptToScreen(lastPtPDF);
  var B = ptToScreen(cursorPDF);
  var Cc = ptToScreen(arc.center);
  var Rc = Math.hypot(A.x - Cc.x, A.y - Cc.y);
  if (Rc < 0.5) return;
  var aA = Math.atan2(A.y - Cc.y, A.x - Cc.x);
  var aB = Math.atan2(B.y - Cc.y, B.x - Cc.x);
  /* Determine winding from through-point side */
  var Pc = ptToScreen(_arcDraft.throughPt);
  var aP = Math.atan2(Pc.y - Cc.y, Pc.x - Cc.x);
  var sw = (aB - aA + 2 * Math.PI) % (2 * Math.PI);
  var op = (aP - aA + 2 * Math.PI) % (2 * Math.PI);
  var ccw = op > sw;
  ctx.save();
  ctx.beginPath();
  ctx.arc(Cc.x, Cc.y, Rc, aA, aB, ccw);
  ctx.strokeStyle = '#ffd60a'; /* gold to distinguish from straight line preview */
  ctx.setLineDash([5, 4]);
  ctx.lineWidth = 1.5;
  ctx.globalAlpha = 0.85;
  ctx.stroke();
  /* Draw through-point marker */
  ctx.beginPath();
  ctx.arc(Pc.x, Pc.y, 5, 0, 2 * Math.PI);
  ctx.fillStyle = '#ffd60a';
  ctx.globalAlpha = 0.9;
  ctx.fill();
  ctx.restore();
}

/**
 * arcRenderEdge(ctx, A_pdf, B_pdf, edgeRecord)
 *
 * Draw a saved arc edge from A to B using edgeRecord.arcThrough.
 * A_pdf, B_pdf are PDF-coord points (same source as o.pts[i], o.pts[j]).
 * edgeRecord: { edgeType:'arc', arcSweep: number, arcThrough: {x,y} }
 *
 * The context must already have strokeStyle/lineWidth set by the caller;
 * this fn calls beginPath + arc + stroke internally.
 */
function arcRenderEdge(ctx, A_pdf, B_pdf, edgeRecord) {
  if (!edgeRecord || edgeRecord.edgeType !== 'arc' || !edgeRecord.arcThrough) return;
  if (Math.abs(edgeRecord.arcSweep || 0) < 0.001) return;
  /* Recompute geometry from saved through-point (no stored center needed) */
  var cent = { x: (A_pdf.x + B_pdf.x) / 2, y: (A_pdf.y + B_pdf.y) / 2 };
  var arc = computeArcEdge(A_pdf, B_pdf, edgeRecord.arcThrough, cent);
  if (!arc.center) return;
  var A = ptToScreen(A_pdf);
  var B = ptToScreen(B_pdf);
  var Cc = ptToScreen(arc.center);
  var Rc = Math.hypot(A.x - Cc.x, A.y - Cc.y);
  if (Rc < 0.5) return;
  var aA = Math.atan2(A.y - Cc.y, A.x - Cc.x);
  var aB = Math.atan2(B.y - Cc.y, B.x - Cc.x);
  var Pc = ptToScreen(edgeRecord.arcThrough);
  var aP = Math.atan2(Pc.y - Cc.y, Pc.x - Cc.x);
  var sw = (aB - aA + 2 * Math.PI) % (2 * Math.PI);
  var op = (aP - aA + 2 * Math.PI) % (2 * Math.PI);
  var ccw = op > sw;
  ctx.beginPath();
  ctx.arc(Cc.x, Cc.y, Rc, aA, aB, ccw);
  ctx.stroke();
}

/**
 * arcHUDText() → string (may be empty)
 * Returns a short status line for the HUD while arc sub-mode is active.
 */
function arcHUDText() {
  if (!_arcDraft.pending) return '';
  if (_arcDraft.throughPt) return ' · <b style="color:#ffd60a">Arc: คลิกจุดปลาย arc</b>';
  return ' · <b style="color:#ffd60a">Arc: คลิก through-point</b>';
}
