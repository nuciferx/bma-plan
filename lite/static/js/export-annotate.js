/* export-annotate.js — LITE-6 export helpers (XLSX + PDF overlay + report window).
   Globals read: PS, caseId, pdfName, pageTags, PAGE_TAGS, pageFloorKind, pageFloorNum,
   pageNames, FLOOR_KIND_LABELS, excluded, CATS, projectInfo, RS (measure-engine.js),
   polyMetricsAnyShape (measure-engine.js — arc-inclusive), catOf, annStyle, api, closeMenus,
   computeSummary (ui-lite.html inline), computeReportVars (report-vars.js).
   All functions exposed on window.ExportAnnotate for call-sites in ui-lite.html.
   DOM binding (onclick) lives here — runs after all <script> tags in head/body. */

/* LITE-6: export XLSX + PDF overlay */
function buildExportData(){ var rows=[],sum={},cnt={};
  Object.keys(PS).forEach(function(k){ var pg=+k; PS[k].objects.forEach(function(o){
    var cid=(typeof rollupCatId==="function")?rollupCatId(o):o.catId; var cat=catOf(cid); var nm=cat?cat.name:"—";
    if(o.counting){ rows.push({page:pg,category:nm,semanticTag:o.semanticTag,kind:"count",area:null,count:1}); cnt[cid]=(cnt[cid]||0)+1; return; }
    if(o.kind==="instance"){ var ia=(typeof rollupAreaM2==="function")?rollupAreaM2(o,pg):null; var mm=(typeof masterById==="function")?masterById(o.masterId):null;
      rows.push({page:pg,category:nm,semanticTag:(mm&&mm.semanticTag)||null,kind:"area",area:ia==null?null:+ia.toFixed(3),count:null}); if(ia!=null&&cid!=null)sum[cid]=(sum[cid]||0)+ia; return; }
    if(o.kind!=="poly"){ rows.push({page:pg,category:nm,semanticTag:o.semanticTag,kind:o.kind,area:null,count:null}); return; }
    var a=polyMetricsAnyShape(o,pg).area;
    rows.push({page:pg,category:nm,semanticTag:o.semanticTag,kind:"area",area:a==null?null:+a.toFixed(3),count:null});
    if(cid!=null)sum[cid]=(sum[cid]||0)+(a||0); }); });
  var summary=Object.keys(sum).map(function(id){var c=catOf(id);return {category:(c?c.name:"—"),total:+sum[id].toFixed(3)};})
    .concat(Object.keys(cnt).map(function(id){var c=catOf(id);return {category:(c?c.name:"—")+" (จุด)",total:cnt[id]};}));
  return {rows:rows,summary:summary}; }
async function dlPost(url,payload,fname){ var res=await fetch(url,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
  if(!res.ok){alert("export ล้มเหลว ("+res.status+")");return;} var blob=await res.blob();
  var a=document.createElement("a"); a.href=URL.createObjectURL(blob); a.download=fname; a.click(); }
function baseName(){ return (pdfName||"export").replace(/\.pdf$/i,""); }
function exportXlsx(){ if(!caseId){alert("เปิด PDF ก่อน");return;} dlPost("/export-xlsx",buildExportData(),baseName()+".xlsx"); closeMenus(); }
function exportPdfOverlay(){ if(!caseId){alert("เปิด PDF ก่อน");return;}
  var pages={}; Object.keys(PS).forEach(function(k){ var ppm=(PS[k].scale&&PS[k].scale.pts_per_m>0)?PS[k].scale.pts_per_m:null;
    var objs=PS[k].objects.map(function(o){
    var cid=(typeof rollupCatId==="function")?rollupCatId(o):o.catId; var cat=catOf(cid); var col=cat?cat.color:"#888";
    if(o.kind==="instance"){ var rs=(typeof resolveInstancePts==="function"&&ppm)?resolveInstancePts(o,ppm):null; if(!rs)return null;
      var mm=(typeof masterById==="function")?masterById(o.masterId):null; var ia=(typeof rollupAreaM2==="function")?rollupAreaM2(o,+k):null;
      var mlab=((mm&&(mm.semanticTag||mm.name))||"")+(ia==null?"":" "+ia.toFixed(2)+" m2");
      return {kind:"poly",counting:false,pts:rs.pts,color:col,label:mlab}; }
    var label=null; if(o.kind==="poly"&&!o.counting){ var a=polyMetricsAnyShape(o,+k).area; label=o.semanticTag+(a==null?"":" "+a.toFixed(2)+" m2"); }
    return {kind:o.kind,counting:o.counting,pts:o.pts,color:col,label:label}; }).filter(function(x){return x!==null;});
    var anns=(PS[k].annotations||[]).map(function(a){ var st=annStyle(a); return {type:a.type,pt:a.pt,pts:a.pts,text:a.text,color:st.color,opacity:st.opacity,fontSize:st.fontSize}; });
    if(objs.length||anns.length)pages[k]={objects:objs,annotations:anns}; });
  dlPost("/export-pdf-overlay",{case_id:caseId,pages:pages},baseName()+"-overlay.pdf"); closeMenus(); }

/* LITE-REPORT: editable web report — opens /report in a new window, hands off
   precomputed measure results via sessionStorage. Reads polyMetrics/PS/catOf
   read-only; touches no area-math / coordinate / schema surface. Approach A
   (INV-2026-05-21-002). */
function reportPageTitle(pg){
  if(pageNames[pg]) return pageNames[pg];
  var fk=pageFloorKind[pg];
  if(fk){ var lbl=FLOOR_KIND_LABELS[fk]||""; var num=pageFloorNum[pg]; return (lbl+(num?(" "+num):"")).trim()||("หน้า "+pg); }
  var tg=pageTags[pg]; if(tg&&PAGE_TAGS[tg]) return PAGE_TAGS[tg];
  return "หน้า "+pg;
}
function buildReportPayload(){
  var pages=[];
  Object.keys(PS).map(Number).filter(function(n){return !excluded[n];}).sort(function(a,b){return a-b;})
  .forEach(function(pg){
    var objs=(PS[pg]&&PS[pg].objects)||[];
    var areaObjs=objs.filter(function(o){ if(o.kind==="poly"&&!o.counting) return true;
      if(o.kind==="instance"){ var c=(typeof rollupCatId==="function")?rollupCatId(o):null; return c!=null; } return false; });
    if(!areaObjs.length) return;
    var groups=[], overlays=[], net=0, badgeN=0;
    CATS.forEach(function(c){
      if(c.counting) return;
      var inCat=areaObjs.filter(function(o){var cc=(typeof rollupCatId==="function")?rollupCatId(o):o.catId; return cc===c.id;});
      if(!inCat.length) return;
      var sub=0;
      var rows=inCat.map(function(o){
        var a,rpts,rname;
        if(o.kind==="instance"){ var ppm=(PS[pg].scale&&PS[pg].scale.pts_per_m>0)?PS[pg].scale.pts_per_m:null;
          a=(typeof rollupAreaM2==="function")?rollupAreaM2(o,pg):null; a=(a==null?0:a);
          var rs=(typeof resolveInstancePts==="function"&&ppm)?resolveInstancePts(o,ppm):null; rpts=rs?rs.pts:[];
          var mm=(typeof masterById==="function")?masterById(o.masterId):null; rname=(o.name||(mm&&mm.name)||c.name);
        } else { a=polyMetricsAnyShape(o,pg).area; a=(a==null?0:a); rpts=o.pts||[]; rname=(o.name||c.name); }
        sub+=a; badgeN++;
        overlays.push({pts:rpts.map(function(p){return {x:+(p.x*RS).toFixed(1),y:+(p.y*RS).toFixed(1)};}),color:c.color,badge:badgeN});
        return {name:rname, area:+a.toFixed(2), badge:badgeN};
      });
      var sign=(c.id==="ded")?-1:1; net+=sign*sub;
      groups.push({label:c.name,color:c.color,rows:rows,subtotal:+sub.toFixed(2),sign:sign});
    });
    if(!groups.length) return;
    pages.push({idx:pg,title:reportPageTitle(pg),tag:(pageTags[pg]?(PAGE_TAGS[pageTags[pg]]||""):""),
      imgUrl:api("/page/"+pg),scaleSet:!!(PS[pg]&&PS[pg].scale), // LPM slice 4+: route through pageMgr.serverNum(pg) once mutations exist
      overlays:overlays,groups:groups,net:+net.toFixed(2)});
  });
  var _s=computeSummary(); var _agg={}; Object.keys(_s.all).forEach(function(k){_agg[k]=_s.all[k];}); Object.keys(_s.allCnt).forEach(function(k){_agg[k]=_s.allCnt[k];});
  var _rv=computeReportVars(_agg).map(function(v){return {name:v.name,unit:v.unit,value:v.value,err:v.err};});
  return {project:projectInfo.name||"",date:new Date().toLocaleDateString("th-TH"),generated:Date.now(),pages:pages,reportVars:_rv};
}
function openReport(){
  if(!caseId){alert("เปิด PDF ก่อน");return;}
  var payload=buildReportPayload();
  if(!payload.pages.length){alert("ยังไม่มีพื้นที่ที่วัด — วาดพื้นที่ (polygon) ก่อนสร้างรายงาน");return;}
  try{ sessionStorage.setItem("bmaReportPayload",JSON.stringify(payload)); }
  catch(err){ alert("เตรียมรายงานไม่สำเร็จ (ข้อมูลใหญ่เกิน): "+err.message); return; }
  window.open("/report","_blank");
  closeMenus();
}

/* DOM bindings — safe here because this script loads after the HTML body */
window.ExportAnnotate = { buildExportData:buildExportData, dlPost:dlPost, baseName:baseName,
  exportXlsx:exportXlsx, exportPdfOverlay:exportPdfOverlay,
  reportPageTitle:reportPageTitle, buildReportPayload:buildReportPayload, openReport:openReport };
