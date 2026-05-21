// BMA-Plan Lite — vendored measurement engine.
// =====================================================================
// VENDORED VERBATIM from proto/ui.html (Approach A — INV-2026-05-21-001 / LITE-0).
// DO NOT EDIT the math below. Every function here must stay BYTE-IDENTICAL
// (after whitespace strip) to its counterpart in proto/ui.html, so that a
// .bmaplan written by lite cross-opens in proto with identical area values.
//
// Drift is enforced by lite/tests/test_measure_parity.py — it extracts these
// same functions from BOTH files and asserts (a) source lines match and
// (b) numeric output matches on pinned fixtures. If proto ships an area-math
// bugfix, this file must be re-synced and the parity test re-run.
//
// HOST CONTRACT — ui-lite.html MUST provide these globals (in an earlier
// classic <script>) before any area/coord function is CALLED:
//     let curPage;                 // current 1-based page index
//     let pageData;                // { size:{orig_w_pt, orig_h_pt} } | null
//     const canvas = <HTMLCanvasElement>;
//     function getRot(pg){...}          // page rotation in {0,90,180,270}
//     function getScaleForPage(pg){...} // { pts_per_m } | null
// RS and the pure helpers (_PATH_FLATTEN_TOL, segIntersect, _flattenCubicSeg,
// flattenPathToPoints, polySelfIntersects) are OWNED here — do not redeclare
// them in the host.
// =====================================================================

const RS=1.5;
const _PATH_FLATTEN_TOL=0.1;

function segIntersect(x0,y0,x1,y1,x2,y2,x3,y3){const d1x=x1-x0,d1y=y1-y0,d2x=x3-x2,d2y=y3-y2;const cross=d1x*d2y-d1y*d2x;if(Math.abs(cross)<0.5)return null;const dx=x2-x0,dy=y2-y0;const t=(dx*d2y-dy*d2x)/cross;const u=(dx*d1y-dy*d1x)/cross;if(t<0||t>1||u<0||u>1)return null;return{x:x0+t*d1x,y:y0+t*d1y};}

function _flattenCubicSeg(p0,c1,c2,p1,tol,out,depth){if(out.length>=10000)return;if(depth>=20){if(out.length<10000)out.push(p1);return;}const dx=p1.x-p0.x,dy=p1.y-p0.y,lenSq=dx*dx+dy*dy;if(lenSq<1e-8){if(out.length<10000)out.push(p1);return;}const inv=1/Math.sqrt(lenSq);const d1=Math.abs((c1.x-p0.x)*dy*inv-(c1.y-p0.y)*dx*inv);const d2=Math.abs((c2.x-p0.x)*dy*inv-(c2.y-p0.y)*dx*inv);if(d1<=tol&&d2<=tol){if(out.length<10000)out.push(p1);return;}const m01={x:(p0.x+c1.x)/2,y:(p0.y+c1.y)/2},m12={x:(c1.x+c2.x)/2,y:(c1.y+c2.y)/2},m23={x:(c2.x+p1.x)/2,y:(c2.y+p1.y)/2};const m012={x:(m01.x+m12.x)/2,y:(m01.y+m12.y)/2},m123={x:(m12.x+m23.x)/2,y:(m12.y+m23.y)/2};const mid={x:(m012.x+m123.x)/2,y:(m012.y+m123.y)/2};_flattenCubicSeg(p0,m01,m012,mid,tol,out,depth+1);_flattenCubicSeg(mid,m123,m23,p1,tol,out,depth+1);}

function flattenPathToPoints(path,tol=_PATH_FLATTEN_TOL){if(!path||!Array.isArray(path.segments)||!path.segments.length)return[];const out=[];for(let i=0;i<path.segments.length;i++){if(out.length>=10000){console.warn('[BMA] flattenPathToPoints: 10000-point cap');break;}const s=path.segments[i];if(i===0)out.push({x:s.p0.x,y:s.p0.y});if(s.type==='line'){if(out.length<10000)out.push({x:s.p1.x,y:s.p1.y});}else if(s.type==='cubic'){_flattenCubicSeg(s.p0,s.c1,s.c2,s.p1,tol,out,0);}}return out;}

function polySelfIntersects(pts){if(pts.length<4)return false;for(let i=0;i<pts.length;i++){const a1=pts[i],a2=pts[(i+1)%pts.length];for(let j=i+1;j<pts.length;j++){if(Math.abs(i-j)<=1)continue;if(i===0&&j===pts.length-1)continue;const b1=pts[j],b2=pts[(j+1)%pts.length];if(segIntersect(a1.x,a1.y,a2.x,a2.y,b1.x,b1.y,b2.x,b2.y))return true;}}return false;}

function origSize(){if(pageData?.size?.orig_w_pt)return{W:pageData.size.orig_w_pt,H:pageData.size.orig_h_pt};return{W:canvas.width/RS,H:canvas.height/RS};}
function pdfToC(px,py){const{W,H}=origSize(),rot=getRot(curPage);if(rot===0)return{x:px*RS,y:py*RS};if(rot===90)return{x:(H-py)*RS,y:px*RS};if(rot===180)return{x:(W-px)*RS,y:(H-py)*RS};return{x:py*RS,y:(W-px)*RS};}
function cToPdf(cx,cy){const{W,H}=origSize(),rot=getRot(curPage);if(rot===0)return{x:cx/RS,y:cy/RS};if(rot===90)return{x:cy/RS,y:H-cx/RS};if(rot===180)return{x:W-cx/RS,y:H-cy/RS};return{x:W-cy/RS,y:cx/RS};}

function polyAreaM2(pts){const scale=getScaleForPage(curPage);if(!scale)return null;let a=0;for(let i=0;i<pts.length;i++){const j=(i+1)%pts.length;a+=pts[i].x*pts[j].y-pts[j].x*pts[i].y;}return Math.abs(a)/(2*scale.pts_per_m**2);}
function polyMetrics(poly,pg=curPage){const pts=poly.pts||[];if(pts.length<3||polySelfIntersects(pts))return{area:null,scale:getScaleForPage(pg)};const scale=getScaleForPage(pg);let a=0;for(let i=0;i<pts.length;i++){const j=(i+1)%pts.length;a+=pts[i].x*pts[j].y-pts[j].x*pts[i].y;}const ptArea=Math.abs(a)/2;return{area:scale?ptArea/(scale.pts_per_m**2):null,scale};}
function pathAreaM2(path,pg=curPage){if(!path||!Array.isArray(path.segments))return null;const pts=flattenPathToPoints(path,_PATH_FLATTEN_TOL);if(pts.length<3)return null;return polyAreaM2(pts);}

// ── Arc-polygon math (VENDORED VERBATIM from proto/ui.html — INV-001 kernel) ──
function arcSegmentAreaM2(chordPt,sweepRad,pg=curPage){const scale=getScaleForPage(pg);if(!scale||Math.abs(sweepRad)<0.001||!(chordPt>0))return 0;const chordM=chordPt/scale.pts_per_m;const half=Math.abs(sweepRad)/2;const sinHalf=Math.sin(half);if(Math.abs(sinHalf)<1e-9)return 0;const rM=chordM/(2*sinHalf);const segArea=(rM*rM*(Math.abs(sweepRad)-Math.sin(Math.abs(sweepRad))))/2;return sweepRad>0?segArea:-segArea;}
function polygonAreaWithArcsM2(poly,pg=curPage){if(!poly?.pts||poly.pts.length<3)return null;const base=polyAreaM2(poly.pts);if(base==null)return null;const edges=poly.edges||[];let extra=0;for(let i=0;i<poly.pts.length;i++){const j=(i+1)%poly.pts.length;const e=edges[i];if(e?.edgeType==="arc"&&typeof e.arcSweep==="number"){const chord=Math.hypot(poly.pts[j].x-poly.pts[i].x,poly.pts[j].y-poly.pts[i].y);extra+=arcSegmentAreaM2(chord,e.arcSweep,pg)||0;}}return base+extra;}
function _arcCircumcenter(A,P,B){const ax=A.x,ay=A.y,px=P.x,py=P.y,bx=B.x,by=B.y;const D=2*(ax*(py-by)+px*(by-ay)+bx*(ay-py));if(Math.abs(D)<1e-9)return null;const ax2=ax*ax+ay*ay,px2=px*px+py*py,bx2=bx*bx+by*by;return{x:(ax2*(py-by)+px2*(by-ay)+bx2*(ay-py))/D,y:(ax2*(bx-px)+px2*(ax-bx)+bx2*(px-ax))/D};}
function _arcPolygonCentroid(pts){if(!pts?.length)return{x:0,y:0};let cx=0,cy=0;for(const p of pts){cx+=p.x;cy+=p.y;}return{x:cx/pts.length,y:cy/pts.length};}
function computeArcEdge(A,B,P,polygonCentroid){const C=_arcCircumcenter(A,P,B);if(!C)return{sweep:0,center:null,radius:0};const r=Math.hypot(A.x-C.x,A.y-C.y);const chord=Math.hypot(B.x-A.x,B.y-A.y);if(chord<1e-9)return{sweep:0,center:C,radius:r};const mid={x:(A.x+B.x)/2,y:(A.y+B.y)/2};const ux=(B.x-A.x)/chord,uy=(B.y-A.y)/chord;const nx=-uy,ny=ux;const sag=(P.x-mid.x)*nx+(P.y-mid.y)*ny;if(Math.abs(sag)<0.5)return{sweep:0,center:C,radius:r};let sweepMag;if(Math.abs(sag)<=r){sweepMag=2*Math.atan2(chord/2,r-Math.abs(sag));}else{sweepMag=2*Math.PI-2*Math.atan2(chord/2,Math.abs(sag)-r);}const cen=polygonCentroid||{x:mid.x,y:mid.y};const centroidSide=(cen.x-mid.x)*nx+(cen.y-mid.y)*ny;const sameSide=(sag>0)===(centroidSide>0);return{sweep:sameSide?-sweepMag:sweepMag,center:C,radius:r};}
function polyMetricsAnyShape(poly,pg=curPage){if(Array.isArray(poly?.edges)&&poly.edges.some(e=>e?.edgeType==="arc")){const pts=poly.pts||[];const scale=getScaleForPage(pg);if(pts.length<3||polySelfIntersects(pts))return{area:null,scale};return{area:polygonAreaWithArcsM2(poly,pg),scale};}return polyMetrics(poly,pg);}

// ── lite-owned (NOT vendored): simplified objectAreaM2. Lite has only polygon
// + path tools (no circle/ellipse/arc generators), so the dispatcher needs just
// the path and base-polygon branches. This is allowed to differ from proto's
// objectAreaM2 because lite never produces circle/ellipse/arc objects.
function objectAreaM2Lite(obj,pg=curPage){if(!obj)return null;if(obj.geometryType==='path'&&Array.isArray(obj.segments))return pathAreaM2(obj,pg);return polyAreaM2(obj.pts||[]);}

// Export for Node test harness; harmless in browser (module not defined there).
if(typeof module!=='undefined'&&module.exports){module.exports={RS,_PATH_FLATTEN_TOL,segIntersect,_flattenCubicSeg,flattenPathToPoints,polySelfIntersects,origSize,pdfToC,cToPdf,polyAreaM2,polyMetrics,pathAreaM2,arcSegmentAreaM2,polygonAreaWithArcsM2,_arcCircumcenter,_arcPolygonCentroid,computeArcEdge,polyMetricsAnyShape,objectAreaM2Lite};}
