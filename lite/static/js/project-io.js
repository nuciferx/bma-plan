/* ============================================================
   LITE-PROJECT-IO — .bmaplan save/load, extracted verbatim from
   ui-lite.html (EXTRACT-2026-08-10-project-io). Plain-globals
   module. No IIFE, no export, no bundler. Loaded with the other
   static/js modules, before the inline script that used to host
   this region — safe because every top-level statement here is
   either a plain function/var declaration or a document.getElementById(...)
   .onclick / .onchange assignment; none of them READ any global at
   parse time, only at call time (user clicking Save/Load), by which
   point the whole page (inline script + late modules like
   page-manager.js) has already run. cross-floor-shapes.js is
   injected dynamically well after page load and monkey-patches
   window.loadProto / #mi-save.onclick by reference, so it wraps
   whichever function landed there last regardless of file-load
   order (see cross-floor-shapes.js cfssWrapSave/cfssWrapLoad).

   Public API (globals declared here):
     rid, ANN_FWD, ANN_REV, SEM_REV, endpts, annFwd, buildPageStore,
     annRevFn, polyPts, stripClosingDup, loadProto
     (+ #mi-save .onclick, #mi-load .onclick, #file-bma .onchange)

   Depends on (read here, defined elsewhere — inline script globals
   unless noted; all reads happen only inside function bodies, i.e.
   at call time):
     PS, excluded, pdfName, pageCount, pageRot, pageTags, pageNames,
     projectInfo, pageFloorKind, pageFloorNum, caseId, state, LAYERS,
     FOLDERS, ROLE_DEFS, layerById, folderById, roleDef, roleSemanticTag,
     catOf, layersInOrder, foldersInOrder, sweepOrphanCatIds,
     serializeReportVars, loadReportVars, seedReportVars, REPORT_VARS,
     annStyle (static/js/annot-style.js), flattenPathToPoints
     (static/js/measure-engine.js), pushUndo, draw, afterPage,
     gateNoCaseMsg (unused by this region directly but shared naming),
     pageMgr, _pmCommit, _pmuiApplyChanges, _pmSeed
     (static/js/page-manager.js / page-manager-ui.js)

   Invariants:
     - .bmaplan schema is additive-only (CLAUDE.md). This module must
       never rename/remove existing doc fields or change how
       semanticTag drives area math.
     - Global function names (loadProto, buildPageStore, annFwd,
       annRevFn, ...) and the #mi-save / #mi-load / #file-bma DOM
       hookups must stay IDENTICAL in name/shape so cross-floor-
       shapes.js's monkey-patches keep landing correctly.
     - VERBATIM-FIRST extraction: the body below is byte-identical to
       the region that used to live inline in ui-lite.html (lines
       934-1038 pre-extraction). Behavior changes belong in a
       different, explicitly-scoped sprint.
   ============================================================ */

/* LITE-5: save/load in proto's .bmaplan schema (cross-open with proto).
   Lite objects -> proto pageStore[n].{polys,openings,lines,refs,annotations,calibScale};
   count objects -> additive pageStore[n].counts[] (proto ignores unknown arrays). */
function rid(){return Math.random().toString(36).slice(2,10);}
var ANN_FWD={ann_text:"text",ann_comment:"comment",ann_arrow:"arrow",ann_highlight:"highlight",ann_rect:"rect_frame",ann_circle:"circle_frame",ann_cloud:"cloud_frame"};
var ANN_REV={text:"ann_text",comment:"ann_comment",arrow:"ann_arrow",highlight:"ann_highlight",rect_frame:"ann_rect",circle_frame:"ann_circle",cloud_frame:"ann_cloud",sticky:"ann_text"};
var SEM_REV={gross_floor_area:"gfa",use_area:"use",floor_area:"use",deduction_opening:"ded","void":"ded",site_land_area:"site",building_footprint:"site",legal_open_space:"open",open_space:"open",permeable_area:"open",hardscape:"open",parking_area:"gfa",count_marker:"count"};
function endpts(o){var p=o.pts;return {x0:p[0].x,y0:p[0].y,x1:p[p.length-1].x,y1:p[p.length-1].y};}
function annFwd(a){ var st=annStyle(a); var o={id:"ann_"+rid(),type:ANN_FWD[a.type]||"text",pts:a.pt?[a.pt]:(a.pts||[]),text:a.text||"",color:st.color,opacity:st.opacity,createdAt:new Date().toISOString()}; if(a.type==="ann_text"||a.type==="ann_comment")o.fontSize=st.fontSize; if(a.label){o.label=a.label;o.labelPt=a.labelPt;} return o; }
function buildPageStore(){ var ps={};
  Object.keys(PS).forEach(function(k){ var p=PS[k]; var st={lines:[],polys:[],openings:[],refs:[],parking:[],counts:[],calibScale:p.scale||null,annotations:[]};
    p.objects.forEach(function(o){ var col=(catOf(o.catId)||{color:"#888"}).color;
      if(o.counting){ st.counts.push({x:o.pts[0].x,y:o.pts[0].y,catId:o.catId,semanticTag:o.semanticTag,liteCatId:o.catId,count:1}); return; }
      if(o.kind==="ref"){ st.refs.push(Object.assign({pts:o.pts,kind:"ref",id:"ref-"+rid(),color:col,opacity:1,semanticTag:"reference_line",useCategory:null,refType:"custom",name:"เส้นอ้างอิง",liteCatId:o.catId},endpts(o))); return; }
      if(o.kind==="line"){ var lineObj=Object.assign({pts:o.pts,kind:(o.pts.length>2?"path":"line"),id:"line-"+rid(),color:col,opacity:1,semanticTag:"dimension_line",useCategory:null,liteCatId:o.catId},endpts(o));
        /* CURVE-LEN/FREEHAND-LEN: additive-only — edges/freeform were previously dropped entirely on save (a lossiness pre-dating this sprint). */
        if(o.edges)lineObj.edges=o.edges; if(o.freeform)lineObj.freeform=o.freeform;
        st.lines.push(lineObj); return; }
      var poly={pts:o.pts,closed:true,name:"",areaType:(o.catId==="site"?"land":"room"),id:(o.catId==="ded"?"opening":"area")+"-"+rid(),color:col,opacity:0.18,semanticTag:o.semanticTag,useCategory:null,liteCatId:o.catId};
      if(o.edges)poly.edges=o.edges;
      if(o.catId==="ded")st.openings.push(poly); else st.polys.push(poly); });
    (p.annotations||[]).forEach(function(a){ st.annotations.push(annFwd(a)); });
    ps[k]=st; });
  return ps; }
document.getElementById("mi-save").onclick=async function(){
  if(!caseId){alert("ยังไม่ได้เปิด PDF\nกด Ctrl+O เพื่อเปิดไฟล์ PDF ก่อน");return;}
  // FIX-B2: if there are pending page mutations, flush them to the server first
  // so the on-disk PDF matches the client page order before we serialise.
  if(pageMgr&&pageMgr.pending&&pageMgr.pending.length>0){
    try{ await _pmuiApplyChanges(); }
    catch(err){ alert("บันทึกล้มเหลว — Apply page changes ไม่สำเร็จ: "+err.message+"\nเปิด 'จัดการหน้า' (⇧F12) แล้วกด 'บันทึกการแก้ไขหน้า' อีกครั้ง"); return; }
    // If pending is still non-empty after apply (server error path), abort.
    if(pageMgr.pending&&pageMgr.pending.length>0){ alert("บันทึกล้มเหลว — ยังมี page changes ค้างอยู่\nเปิด 'จัดการหน้า' (⇧F12) กด 'บันทึกการแก้ไขหน้า' ให้เสร็จก่อน แล้วบันทึกโปรเจกต์ใหม่"); return; }
  }
  // FIX-B1: call _pmCommit() to project current pageMgr order → PS/globals,
  // then include pageIdentities in the saved doc (additive field).
  if(pageMgr)_pmCommit();
  var doc={version:1,app:"bma-plan-lite",pdfName:pdfName,totalPages:pageCount,pageStore:buildPageStore(),
    pageRotations:pageRot,pageTags:pageTags,pageNames:pageNames,projectInfo:projectInfo,siteOrientation:{},
    excludedPages:Object.keys(excluded).filter(function(k){return excluded[k];}).map(Number),pageFloorKind:pageFloorKind,pageFloorNum:pageFloorNum,
    pageIdentities:(pageMgr?pageMgr.pageOrder.slice():undefined),
    liteLayers:layersInOrder().map(function(l){return {id:l.id,name:l.name,color:l.color,role:l.role,order:l.order,parentId:(l.parentId!==undefined?l.parentId:null),floorKey:(l.floorKey!==undefined?l.floorKey:undefined)};}),
    liteGroups:foldersInOrder().map(function(f){return {id:f.id,name:f.name,color:f.color,parentId:(f.parentId!==undefined?f.parentId:null),order:f.order,kind:f.kind,pages:f.pages};}),
    reportVars:serializeReportVars()};
  var blob=new Blob([JSON.stringify(doc,null,2)],{type:"application/json"});
  var a=document.createElement("a"); a.href=URL.createObjectURL(blob);
  a.download=(pdfName||"project").replace(/\.pdf$/i,"")+".bmaplan"; a.click();
  state.dirty=false; draw();
};
/* LITE-6 + LITE-REPORT: export/report helpers live in static/js/export-annotate.js */
document.getElementById("mi-xlsx").onclick=function(){ ExportAnnotate.exportXlsx(); };
document.getElementById("mi-pdfov").onclick=function(){ ExportAnnotate.exportPdfOverlay(); };
document.getElementById("mi-report").onclick=function(){ ExportAnnotate.openReport(); };

document.getElementById("mi-load").onclick=function(){document.getElementById("file-bma").click();};
function annRevFn(a){ var t=ANN_REV[a.type]||"ann_text"; var o={id:state._id++,type:t};
  if(t==="ann_text"||t==="ann_comment"){ o.pt=(a.pts&&a.pts[0])||a.pt||{x:0,y:0}; o.text=a.text||""; } else { o.pts=a.pts||[]; }
  if(a.color)o.color=a.color; if(a.opacity!=null)o.opacity=a.opacity; if(a.fontSize)o.fontSize=a.fontSize; if(a.label){o.label=a.label;o.labelPt=a.labelPt;} return o; }
function polyPts(o){ if(o.pts&&o.pts.length)return o.pts; if(o.geometryType==="path"&&Array.isArray(o.segments))return flattenPathToPoints(o,1.0); return []; }
function stripClosingDup(pts,edges){ if(!pts||pts.length<4)return pts; var a=pts[0],b=pts[pts.length-1]; if(a&&b&&Math.abs(a.x-b.x)<1e-6&&Math.abs(a.y-b.y)<1e-6){ if(edges&&edges.length===pts.length)edges.length=pts.length-1; return pts.slice(0,-1); } return pts; }
function loadProto(doc){ PS={}; excluded={};
  /* LST-2: rebuild FOLDERS in-place from doc.liteGroups (additive — absent = old file) */
  FOLDERS.length=0;
  (doc.liteGroups||[]).forEach(function(g){ if(g&&g.id) FOLDERS.push({id:g.id,name:g.name,color:g.color,
    parentId:(g.parentId!==undefined?g.parentId:null),order:(g.order!==undefined?g.order:FOLDERS.length),kind:g.kind,pages:g.pages}); });
  /* L2c-2: rebuild LAYERS in-place from doc.liteLayers (additive — absent = old file) */
  if(doc.liteLayers&&doc.liteLayers.length){
    LAYERS.length=0;
    doc.liteLayers.forEach(function(e){ if(!roleDef(e.role))return; // skip unknown role
      LAYERS.push({id:e.id,name:e.name,color:e.color,role:e.role,
        tag:roleSemanticTag(e.role),counting:!!(roleDef(e.role).counting),subTag:"",order:e.order,groupId:null,
        parentId:(e.parentId!==undefined?e.parentId:null),floorKey:e.floorKey}); }); /* floorKey additive: undefined on old saves */
    /* ensure every role's default layer exists (fallback target) */
    ROLE_DEFS.forEach(function(rd){ if(!layerById(rd.id)){
      LAYERS.push({id:rd.id,name:rd.name,color:rd.color,role:rd.id,
        tag:rd.tag,counting:!!rd.counting,subTag:"",order:rd.order||0,groupId:null,parentId:null}); } });
  }
  /* LRV-S4: restore report vars — new files restore saved vars; old files reseed defaults */
  if(doc.reportVars&&doc.reportVars.length){loadReportVars(doc.reportVars);}
  else{REPORT_VARS.length=0;seedReportVars();}
  /* LST-2: integrity pass — orphan any layer/folder whose parentId resolves to nothing */
  LAYERS.forEach(function(l){ if(l.parentId!==null&&!folderById(l.parentId)&&!layerById(l.parentId))l.parentId=null; });
  FOLDERS.forEach(function(f){ if(f.parentId!==null&&!folderById(f.parentId)&&!layerById(f.parentId))f.parentId=null; });
  /* re-seed visibility/lock for any layer id that doesn't have a flag yet */
  LAYERS.forEach(function(l){ if(state.catVis[l.id]===undefined)state.catVis[l.id]=true;
    if(state.catLock[l.id]===undefined)state.catLock[l.id]=false; });
  FOLDERS.forEach(function(f){ if(state.catVis[f.id]===undefined)state.catVis[f.id]=true;
    if(state.catLock[f.id]===undefined)state.catLock[f.id]=false; });
  if(doc.pageStore){ Object.keys(doc.pageStore).forEach(function(k){ var st=doc.pageStore[k]||{}; var objs=[];
    (st.polys||[]).forEach(function(o){ var cid=(o.liteCatId&&layerById(o.liteCatId))?o.liteCatId:(SEM_REV[o.semanticTag]||(o.areaType==="land"?"site":"gfa")); objs.push({id:state._id++,catId:cid,semanticTag:o.semanticTag||"gross_floor_area",kind:"poly",counting:false,pts:stripClosingDup(polyPts(o),o.edges),dimVisible:true,edges:o.edges}); });
    (st.openings||[]).forEach(function(o){ var cid=(o.liteCatId&&layerById(o.liteCatId))?o.liteCatId:"ded"; objs.push({id:state._id++,catId:cid,semanticTag:o.semanticTag||"deduction_opening",kind:"poly",counting:false,pts:stripClosingDup(polyPts(o),o.edges),dimVisible:true,edges:o.edges}); });
    (st.lines||[]).forEach(function(o){ var cid=(o.liteCatId&&layerById(o.liteCatId))?o.liteCatId:"gfa"; var lo={id:state._id++,catId:cid,semanticTag:"dimension_line",kind:"line",counting:false,pts:o.pts||[{x:o.x0,y:o.y0},{x:o.x1,y:o.y1}],dimVisible:true};
      if(o.edges)lo.edges=o.edges; if(o.freeform)lo.freeform=o.freeform; objs.push(lo); });
    (st.refs||[]).forEach(function(o){ var cid=(o.liteCatId&&layerById(o.liteCatId))?o.liteCatId:"gfa"; objs.push({id:state._id++,catId:cid,semanticTag:"reference_line",kind:"ref",counting:false,pts:o.pts||[{x:o.x0,y:o.y0},{x:o.x1,y:o.y1}],dimVisible:true}); });
    (st.counts||[]).forEach(function(o){ var cid=(o.liteCatId&&layerById(o.liteCatId))?o.liteCatId:(o.catId||"count"); objs.push({id:state._id++,catId:cid,semanticTag:o.semanticTag||"count_marker",kind:"count",counting:true,pts:[{x:o.x,y:o.y}],dimVisible:false}); });
    PS[k]={objects:objs,scale:st.calibScale||null,annotations:(st.annotations||[]).map(annRevFn)}; }); }
  else if(doc.pages){ Object.keys(doc.pages).forEach(function(n){ var p=doc.pages[n];
    PS[n]={scale:p.scale||null,objects:(p.objects||[]).map(function(o){o.id=state._id++;return o;}),annotations:(p.annotations||[]).map(function(a){a.id=state._id++;return a;})}; }); }
  (doc.excludedPages||[]).forEach(function(n){excluded[n]=true;});
  if(doc.projectInfo)projectInfo=doc.projectInfo; if(doc.pageTags)pageTags=doc.pageTags; if(doc.pageRotations)pageRot=doc.pageRotations;
  pageNames=doc.pageNames||{}; pageFloorKind=doc.pageFloorKind||{}; pageFloorNum=doc.pageFloorNum||{};
  if(pageCount)_pmSeed(doc.pageIdentities); // LPM slice 3: seed pageMgr after load (pass pageIdentities if present)
  sweepOrphanCatIds(); } // B3 (H3): heal any catId that doesn't resolve to a loaded layer
document.getElementById("file-bma").onchange=function(e){var f=e.target.files[0];if(!f)return;
  var rd=new FileReader(); rd.onload=function(){ try{ var doc=JSON.parse(rd.result);
    if(doc.version!==1)throw new Error("version");
    loadProto(doc);
    alert("โหลดโปรเจกต์แล้ว ("+Object.keys(PS).length+" หน้ามีข้อมูล)"); state.dirty=false; afterPage();
    }catch(err){alert("ไฟล์ .bmaplan ไม่ถูกต้อง: "+err.message+"\nตรวจว่าเลือกไฟล์ .bmaplan ที่บันทึกจากโปรแกรมนี้ (ไม่ใช่ไฟล์ PDF)");} }; rd.readAsText(f); e.target.value=""; };
