/* ============================================================
   LITE-SNAP-ENGINE — lite-native snap core, extracted from
   ui-lite.html (SNAP-2026-07-04 slice 1/3; ray-lock composition
   added in slice 2/3).
   Plain-globals module. No IIFE, no export, no bundler.
   Loaded right after measure-engine.js, before the inline script.

   Exports: isDrawTool, edgeHandleHit, vertexHandleHit, nearOnSegS,
     pageSegs, computeSnap, footPerp, angleLock, snapInvalidate,
     _lockedAngle, computeSnapOnRay
   Reads (inline-script globals, defined later — fine, only read at
     CALL time, never at parse time): state, PSpage, ptToScreen,
     screenToPt, SNAP_PX, centroid, effVisible, _isHidden, catOf,
     curPage, V, PageRenderer, cv
   Calls: segIntersect (vendored VERBATIM in measure-engine.js —
     never copy/modify it here; this module always calls it in
     SCREEN-space coordinates, exactly like the pre-extraction code,
     so its `Math.abs(cross)<0.5` epsilon guard keeps behaving the
     same way it always has).

   ------------------------------------------------------------------
   PERF (the actual point of slice 1): the intersection snap-type
   used to re-run a full O(segCount^2) segIntersect double loop on
   EVERY mousemove, rebuilding `pageSegs()` from scratch each time.
   This module keeps pageSegs()/computeSnap()'s ORIGINAL candidate
   set and ORIGINAL per-pair math untouched, but splits the
   intersection search into:
     - static x static  — segments from committed PSpage().objects
       only. Cached in `_segCache.interStatic` (screen-space points,
       computed with the exact same ptToScreen()+segIntersect() calls
       as before) and reused across calls as long as the page/view/
       object-shape fingerprint is unchanged.
     - static x draft, draft x draft — always recomputed fresh
       (state.draft changes on every click; it is small, so this is
       O(segCount * draftCount) instead of O(segCount^2) — cheap).
   The combined candidate list is identical (same points, computed
   with the same formula) to what the old code would have produced;
   only the WORK is now cached, not the RESULT set semantics.

   Cache invalidation (see _staticFp / snapInvalidate):
     - page switch, object count change, or the current page's last
       object's point-count change: covered automatically — every
       call recomputes the fingerprint (O(1)) and rebuilds if it
       differs.
     - view change (zoom/pan/rotate): included in the fingerprint
       too (V.k/V.ox/V.oy/V.rot) since the cache stores SCREEN-space
       points, not PDF-space — required for correctness, not just
       perf (a stale screen-space cache after a zoom would snap to
       the wrong pixel).
     - undo/redo: `snapInvalidate()` is called from `_afterHistory()`
       in ui-lite.html as a belt-and-braces measure, since undo can
       restore a same-object-count-but-different-shape state that
       the fingerprint's cheap heuristic might miss.

   RESIDUAL RISK FROM SLICE 1 — CLOSED IN SLICE 2: an in-place
   vertex-drag or move-object drag mutates existing point objects
   WITHOUT changing objects.length or any object's pts.length, so
   `_staticFp()` alone could not detect it. As of slice 2, ui-lite.html's
   `mouseup` handler now calls `snapInvalidate()` whenever a vertex-drag
   or move-object drag actually moved something (`.moved===true`),
   closing the gap directly instead of relying on the fingerprint.

   ------------------------------------------------------------------
   SLICE 2 — angle-lock + snap COMPOSITION (computeSnapOnRay):
   When Shift/Ortho angle-lock is active, the user still wants CAD-style
   "apparent intersection" snapping: the point returned is the nearest
   (to the cursor) of — (i) where the LOCKED RAY (from the draft's last
   point, along the locked 45°-stepped direction) crosses an existing
   segment, or (ii) an existing endpoint whose perpendicular distance to
   that ray is within SNAP_PX, projected onto the ray. If nothing
   qualifies, the caller falls back to the plain angleLock() point.
   `_lockedAngle(prev,p)` factors out the exact angle-quantization
   angleLock() has always used (same 45° step, same atan2/round formula)
   so both the pure-lock fallback and the ray composition agree on
   direction — no drift between the two.

   Gating: computeSnapOnRay() is gated on `state.snapOn` ONLY (plus
   PageRenderer.ready()) — NOT subdivided by state.snapTypes.* — because
   apparent-ray-intersection is one composed behavior, not a member of
   the endpoint/midpoint/center/intersection type family; slicing it by
   type would be arbitrary (an "intersection-flavoured" hit that also
   depends on the endpoint set). Slice 3 can revisit this if per-type
   ray gating turns out to be wanted.

   The ray is built as a screen-space segment: origin -> ptToScreen(origin),
   direction derived by transforming a real PDF-space reference point 100pt
   along lockedAngle through ptToScreen (exact under the view's similarity
   transform, not an approximation), length = a generous multiple of the
   current canvas's screen diagonal (per spec wording) so it reaches
   anything visibly relevant regardless of zoom/pan. Both the ray x segment
   and the endpoint-perpendicular-distance checks are done with the SAME
   ptToScreen()+segIntersect()/footPerp() primitives computeSnap() already
   uses, so precision/epsilon behavior stays consistent across the module.
   Degenerate self-touch is filtered explicitly: the draft's own segments
   necessarily meet the ray exactly AT the origin (shared vertex), and the
   origin point itself would otherwise register as a trivial "ray-end" —
   both are excluded on purpose (see ORIGIN_EPS / origin-equality checks).
   ------------------------------------------------------------------ */

/* --- LITE-SNAP: lite-native snap (endpoint / intersection / nearest-on-edge).
   Re-uses the vendored segIntersect for intersections. Works in SCREEN space. --- */
function isDrawTool(){ return ["scale","poly","dist","path","ref","count"].indexOf(state.tool)>=0; }
function edgeHandleHit(o,sx,sy){ for(var i=0;i<o.pts.length;i++){ var m=ptToScreen({x:(o.pts[i].x+o.pts[(i+1)%o.pts.length].x)/2,y:(o.pts[i].y+o.pts[(i+1)%o.pts.length].y)/2}); if(Math.abs(sx-m.x)<7&&Math.abs(sy-m.y)<7)return i; } return -1; }
function vertexHandleHit(o,sx,sy){ for(var i=0;i<o.pts.length;i++){ var s=ptToScreen(o.pts[i]); if(Math.abs(sx-s.x)<6&&Math.abs(sy-s.y)<6)return i; } return -1; }
function nearOnSegS(px,py,a,b){ var dx=b.x-a.x,dy=b.y-a.y,l2=dx*dx+dy*dy; if(l2<1)return{x:a.x,y:a.y};
  var t=Math.max(0,Math.min(1,((px-a.x)*dx+(py-a.y)*dy)/l2)); return{x:a.x+t*dx,y:a.y+t*dy}; }
function pageSegs(){ var segs=[]; var objs=PSpage().objects.concat(state.draft?[{pts:state.draft,kind:(state.tool==="poly"?"poly":"line"),counting:false}]:[]);
  objs.forEach(function(o){ if(o.counting||!o.pts||o.pts.length<2)return; var n=o.kind==="poly"?o.pts.length:o.pts.length-1;
    for(var i=0;i<n;i++)segs.push([o.pts[i],o.pts[(i+1)%o.pts.length]]); }); return segs; }

/* --------------------------------------------------------------------------
   Static-segment intersection cache (the perf layer — see file header).
--------------------------------------------------------------------------- */
var _segCache={fp:null,interStatic:[],rebuildCount:0,hitCount:0};
function snapInvalidate(){ _segCache.fp=null; }
function _staticFp(){
  var objs=PSpage().objects;
  var lastLen = objs.length ? (objs[objs.length-1].pts ? objs[objs.length-1].pts.length : 0) : 0;
  return curPage+"|"+objs.length+"|"+lastLen+"|"+V.k+"|"+V.ox+"|"+V.oy+"|"+V.rot;
}
function _draftSegCount(){
  if(!state.draft||state.draft.length<2)return 0;
  var kind=(state.tool==="poly"?"poly":"line");
  return kind==="poly"?state.draft.length:state.draft.length-1;
}
// staticSegs = the leading slice of pageSegs()'s output that belongs to
// committed objects (pageSegs() always appends the draft pseudo-object's
// segments LAST, so slicing off the trailing _draftSegCount() entries is exact).
function _ensureStaticInterCache(staticSegs){
  var fp=_staticFp();
  if(_segCache.fp===fp){ _segCache.hitCount++; return; }
  var inter=[];
  for(var i=0;i<staticSegs.length;i++)for(var j=i+1;j<staticSegs.length;j++){
    var a0=ptToScreen(staticSegs[i][0]),a1=ptToScreen(staticSegs[i][1]),b0=ptToScreen(staticSegs[j][0]),b1=ptToScreen(staticSegs[j][1]);
    var ix=segIntersect(a0.x,a0.y,a1.x,a1.y,b0.x,b0.y,b1.x,b1.y);   // vendored
    if(ix)inter.push(ix);
  }
  _segCache.fp=fp; _segCache.interStatic=inter; _segCache.rebuildCount++;
}
function _snapIntersections(segs){
  var draftN=_draftSegCount();
  var staticSegs=draftN?segs.slice(0,segs.length-draftN):segs;
  var draftSegs=draftN?segs.slice(segs.length-draftN):[];
  _ensureStaticInterCache(staticSegs);
  var out=_segCache.interStatic.slice();
  for(var i=0;i<staticSegs.length;i++)for(var j=0;j<draftSegs.length;j++){
    var a0=ptToScreen(staticSegs[i][0]),a1=ptToScreen(staticSegs[i][1]),b0=ptToScreen(draftSegs[j][0]),b1=ptToScreen(draftSegs[j][1]);
    var ix=segIntersect(a0.x,a0.y,a1.x,a1.y,b0.x,b0.y,b1.x,b1.y);
    if(ix)out.push(ix);
  }
  for(var p=0;p<draftSegs.length;p++)for(var q=p+1;q<draftSegs.length;q++){
    var c0=ptToScreen(draftSegs[p][0]),c1=ptToScreen(draftSegs[p][1]),d0=ptToScreen(draftSegs[q][0]),d1=ptToScreen(draftSegs[q][1]);
    var ixd=segIntersect(c0.x,c0.y,c1.x,c1.y,d0.x,d0.y,d1.x,d1.y);
    if(ixd)out.push(ixd);
  }
  return out;
}

function computeSnap(sx,sy){
  if(!PageRenderer.ready()||!state.snapOn)return null;
  var ST=state.snapTypes||{endpoint:true,midpoint:true,center:true,intersection:true};
  var objs=PSpage().objects.concat(state.draft?[{pts:state.draft,counting:false}]:[]);
  var best=null,bd=SNAP_PX;
  if(ST.endpoint){ objs.forEach(function(o){ if(o.counting||!o.pts)return; o.pts.forEach(function(p){ var s=ptToScreen(p),d=Math.hypot(s.x-sx,s.y-sy);
    if(d<bd){bd=d;best={pt:p,screen:s,type:"endpoint"};} }); }); if(best)return best; }  // endpoint wins
  var segs=pageSegs();
  if(ST.intersection){ var _ix=_snapIntersections(segs);
    for(var _k=0;_k<_ix.length;_k++){ var ix=_ix[_k]; var d=Math.hypot(ix.x-sx,ix.y-sy); if(d<bd){bd=d;best={pt:screenToPt(ix.x,ix.y),screen:ix,type:"intersection"};} }
  if(best)return best; }                                // intersection next
  if(ST.midpoint){ segs.forEach(function(seg){ var m={x:(seg[0].x+seg[1].x)/2,y:(seg[0].y+seg[1].y)/2},s=ptToScreen(m),d=Math.hypot(s.x-sx,s.y-sy);
    if(d<bd){bd=d;best={pt:m,screen:s,type:"midpoint"};} }); if(best)return best; }  // midpoint
  if(ST.center){ PSpage().objects.forEach(function(o){ if(o.counting||o.kind!=="poly"||!effVisible(o.catId,_isHidden))return; var c=centroid(o.pts),s=ptToScreen(c),d=Math.hypot(s.x-sx,s.y-sy);
    if(d<bd){bd=d;best={pt:c,screen:s,type:"center"};} }); if(best)return best; }    // center
  if(state.draft&&state.draft.length){ var lp=state.draft[state.draft.length-1];
    segs.forEach(function(seg){ var foot=footPerp(lp,seg[0],seg[1]); var s=ptToScreen(foot),d=Math.hypot(s.x-sx,s.y-sy);
      if(d<bd){bd=d;best={pt:foot,screen:s,type:"perp"};} }); }
  if(best)return best;                                  // perpendicular (from last point)
  segs.forEach(function(seg){ var s0=ptToScreen(seg[0]),s1=ptToScreen(seg[1]),np=nearOnSegS(sx,sy,s0,s1),d=Math.hypot(np.x-sx,np.y-sy);
    if(d<bd){bd=d;best={pt:screenToPt(np.x,np.y),screen:np,type:"nearest"};} });
  return best;
}
function footPerp(p,a,b){ var dx=b.x-a.x,dy=b.y-a.y,l2=dx*dx+dy*dy; if(l2<1e-6)return{x:a.x,y:a.y};
  var t=((p.x-a.x)*dx+(p.y-a.y)*dy)/l2; return {x:a.x+t*dx,y:a.y+t*dy}; }   // projection onto infinite line
// angle-quantization shared by angleLock() and computeSnapOnRay() (SNAP-2026-07-04
// slice 2) — factored out so the two can never drift apart on direction. Same
// 45-degree step, same formula angleLock always used.
function _lockedAngle(prev,p){ var dx=p.x-prev.x,dy=p.y-prev.y,step=Math.PI/4; return Math.round(Math.atan2(dy,dx)/step)*step; }
function angleLock(prev,p){ var dx=p.x-prev.x,dy=p.y-prev.y,len=Math.hypot(dx,dy); var la=_lockedAngle(prev,p);
  return {x:prev.x+Math.cos(la)*len,y:prev.y+Math.sin(la)*len}; }

/* --------------------------------------------------------------------------
   computeSnapOnRay(sx, sy, origin, lockedAngle) — CAD apparent-intersection
   snap along a locked ray. See file header (SLICE 2) for the full rationale.
--------------------------------------------------------------------------- */
function computeSnapOnRay(sx, sy, origin, lockedAngle){
  if(!PageRenderer.ready()||!state.snapOn)return null;
  var originScreen=ptToScreen(origin);
  var refScreen=ptToScreen({x:origin.x+Math.cos(lockedAngle)*100,y:origin.y+Math.sin(lockedAngle)*100});
  var dx=refScreen.x-originScreen.x, dy=refScreen.y-originScreen.y, dlen=Math.hypot(dx,dy);
  if(dlen<1e-9)return null;   // degenerate — should not happen (view transform is non-singular)
  var ux=dx/dlen, uy=dy/dlen;
  var r=cv.getBoundingClientRect(), rayLen=Math.hypot(r.width,r.height)*4+1000;   // generous screen diag + pan margin
  var rayA=originScreen, rayB={x:originScreen.x+ux*rayLen,y:originScreen.y+uy*rayLen};
  var ORIGIN_EPS=0.05;   // screen px — filters the degenerate self-touch at the ray origin (see header)
  var best=null,bd=SNAP_PX;

  // (i) ray x every existing segment (static + fresh draft — same source as computeSnap/pageSegs)
  var segs=pageSegs();
  for(var i=0;i<segs.length;i++){
    var a0=ptToScreen(segs[i][0]),a1=ptToScreen(segs[i][1]);
    var ix=segIntersect(rayA.x,rayA.y,rayB.x,rayB.y,a0.x,a0.y,a1.x,a1.y);   // vendored
    if(!ix)continue;
    if(Math.hypot(ix.x-rayA.x,ix.y-rayA.y)<ORIGIN_EPS)continue;   // shared vertex with the ray's own origin — not a real target
    var d=Math.hypot(ix.x-sx,ix.y-sy); if(d<bd){bd=d;best={pt:screenToPt(ix.x,ix.y),screen:ix,type:"ray-x"};}
  }

  // (ii) endpoints within SNAP_PX perpendicular distance of the ray, projected onto it
  var objs=PSpage().objects.concat(state.draft?[{pts:state.draft,counting:false}]:[]);
  objs.forEach(function(o){ if(o.counting||!o.pts)return; o.pts.forEach(function(p){
    if(p.x===origin.x&&p.y===origin.y)return;   // the lock origin itself — not a real target
    var s=ptToScreen(p), foot=footPerp(s,rayA,rayB);
    var t=(foot.x-rayA.x)*ux+(foot.y-rayA.y)*uy; if(t<0)return;   // behind the origin — unreachable along a forward ray
    var perpD=Math.hypot(s.x-foot.x,s.y-foot.y); if(perpD>=SNAP_PX)return;
    var d=Math.hypot(foot.x-sx,foot.y-sy);
    if(d<bd){bd=d;best={pt:screenToPt(foot.x,foot.y),screen:foot,type:"ray-end"};}
  }); });

  return best;
}
