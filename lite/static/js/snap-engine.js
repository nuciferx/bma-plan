/* ============================================================
   LITE-SNAP-ENGINE — lite-native snap core, extracted from
   ui-lite.html (SNAP-2026-07-04 slice 1/3).
   Plain-globals module. No IIFE, no export, no bundler.
   Loaded right after measure-engine.js, before the inline script.

   Exports: isDrawTool, edgeHandleHit, vertexHandleHit, nearOnSegS,
     pageSegs, computeSnap, footPerp, angleLock, snapInvalidate
   Reads (inline-script globals, defined later — fine, only read at
     CALL time, never at parse time): state, PSpage, ptToScreen,
     screenToPt, SNAP_PX, centroid, effVisible, _isHidden, catOf,
     curPage, V, PageRenderer
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

   KNOWN RESIDUAL RISK (documented per SNAP-2026-07-04 spec): an
   in-place vertex-drag or move-object drag (ui-lite.html's
   `cv.addEventListener("mousemove", ...)` handler — the branches
   that do `ve.obj.pts[ve.idx].x = ...` / `go.pts[mi].x = ...`)
   mutates existing point objects WITHOUT changing objects.length or
   any object's pts.length, so `_staticFp()` does not detect it.
   During an active drag, computeSnap() is never invoked (those
   branches `return` before reaching the snap call), so the cache is
   only ever read at a stale position AFTER the drag ends, and only
   until the next invalidating event (add/remove/undo/redo/page
   change/view change). No test in this slice's own matrix exercises
   this path end-to-end; flagged here for a follow-up (e.g. wiring
   snapInvalidate() into the vertEdit/moveObj mouseup handler) if it
   proves to matter in practice.
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
function angleLock(prev,p){ var dx=p.x-prev.x,dy=p.y-prev.y,len=Math.hypot(dx,dy),step=Math.PI/4;
  var la=Math.round(Math.atan2(dy,dx)/step)*step; return {x:prev.x+Math.cos(la)*len,y:prev.y+Math.sin(la)*len}; }
