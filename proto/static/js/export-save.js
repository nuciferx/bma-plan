// proto/static/js/export-save.js
// Save + export functions — extracted from proto/ui.html in sprint BLOAT-3
// (2026-05-20). Mirrors the existing semantic-meta.js / opening-parent.js /
// status-bar.js extraction pattern: plain non-module classic script, top-level
// function declarations stay global, no namespace wrapper, no bundler.
//
// Includes: column / type constants for export rows, the rowBase + buildRows
// helpers, JSON / CSV / XLSX / SummaryXLSX / PDF / PNG-ZIP export functions,
// project save (_makeProjBlob / _writeToHandle / _fallbackDownload /
// saveProject / saveProjectAs), and Save-Source-PDF-in-place. Schema unchanged
// (still version 1; same 12 fields).
//
// Reads runtime globals from ui.html (resolved at call time):
//   totalPages, pageStore, pageRotations, pageTags, pageNames, projectInfo,
//   siteOrientation, excludedPages, pageFloorKind, pageFloorNum,
//   currentFileName, currentCaseId, currentProjectHandle,
//   currentSourcePdfHandle, curPage, selectedPages, isDirty,
//   syncProjectInfoFromForm, normalizeAllObjects, saveCurrentPage,
//   getScaleForPage, scaleLabel, scaleState, lineMetrics, polyMetrics,
//   polyMetricsAnyShape, defaultSemanticTag, deriveMeasurementMeta,
//   isAreaSemanticTag, collectRefDistanceReport, collectSummaryData,
//   collectAreas, phase1Warnings, REF_LABELS, PARKING_LABELS, toRNW,
//   getPref, setStatus, _markSaved.
//
// Writes runtime globals (mutation):
//   currentProjectHandle (saveProjectAs sets it), currentSourcePdfHandle
//   (saveSourcePdfInPlace nulls it on write failure).

// ── Export column / type constants (Thai labels) ──
const COL_PAGE="หน้า";
const COL_TYPE="ประเภท";
const COL_NAME="ชื่อ";
const COL_VALUE="ค่า";
const COL_UNIT="หน่วย";
const COL_RNW="ไร่-งาน-วา";
const TYPE_DISTANCE="ระยะ";
const TYPE_PATH="ระยะต่อเนื่อง";
const TYPE_REF="เส้นอ้างอิง";
const TYPE_PARKING="ที่จอดรถ";
const TYPE_AREA="พื้นที่";
const TYPE_OPENING="ช่องว่าง";
const TYPE_REF_DISTANCE="ระยะถึงเส้นอ้างอิง";
function rowBase(pg,type,name,value,unit,scale){return{[COL_PAGE]:pg,[COL_TYPE]:type,[COL_NAME]:name||"",[COL_VALUE]:value,[COL_UNIT]:unit,[COL_RNW]:"",scale:scaleLabel(scale),scale_source:scale?.source||"-",scale_verified:!!scale?.verified};}
function buildRows(){
  normalizeAllObjects();
  const rows=[];
  for(const[pgStr,data]of Object.entries(pageStore)){
    const pg=+pgStr;
    const scale=getScaleForPage(pg);
    const scl=scaleLabel(scale);
    for(const l of(data.lines||[])){
      const metrics=lineMetrics(l,pg);
      const lSem=l.semanticTag||defaultSemanticTag("line",l);rows.push({...rowBase(pg,l.kind==="path"?TYPE_PATH:TYPE_DISTANCE,l.name||"",metrics.dist!=null?+metrics.dist.toFixed(4):+metrics.ptDist.toFixed(4),metrics.dist!=null?"ม.":"pt",scale),object_id:l.id,segments:metrics.segments.length,semanticTag:lSem,useCategory:null,...deriveMeasurementMeta(lSem)});
    }
    for(const r of(data.refs||[])){
      const metrics=lineMetrics(r,pg);
      const rSem=r.semanticTag||defaultSemanticTag("ref",r);rows.push({...rowBase(pg,TYPE_REF,r.name||REF_LABELS[r.refType]||"",metrics.dist!=null?+metrics.dist.toFixed(4):+metrics.ptDist.toFixed(4),metrics.dist!=null?"ม.":"pt",scale),object_id:r.id,ref_type:r.refType||"custom",label_mode:r.label?.mode||"auto",semanticTag:rSem,useCategory:null,...deriveMeasurementMeta(rSem)});
    }
    for(const p of(data.parking||[])){
      const pkSem=p.semanticTag||defaultSemanticTag("parking",p);rows.push({...rowBase(pg,TYPE_PARKING,PARKING_LABELS[p.parkingType]||p.parkingType||"รถยนต์",p.count||1,"คัน",scale),object_id:p.id,parking_type:p.parkingType||"car",semanticTag:pkSem,useCategory:null,...deriveMeasurementMeta(pkSem)});
    }
    for(const p of(data.polys||[])){
      if(!p.closed)continue;
      const metrics=polyMetricsAnyShape(p,pg);
      const sem=p.semanticTag||defaultSemanticTag("poly",p);
      const row={...rowBase(pg,TYPE_AREA,p.name||"",metrics.area!=null?+metrics.area.toFixed(4):null,"ตร.ม.",scale),object_id:p.id,area_type:p.areaType||"room",label_mode:p.label?.mode||"auto",semanticTag:sem,useCategory:isAreaSemanticTag(sem)?(p.useCategory||null):null,...deriveMeasurementMeta(sem)};
      row[COL_RNW]=p.areaType==="land"?toRNW(metrics.area):"";
      rows.push(row);
    }
    for(const op of(data.openings||[])){
      if(!op.closed)continue;
      const area=polyMetrics({pts:op.pts,closed:true},pg).area;
      const opSem=op.semanticTag||defaultSemanticTag("opening",op);rows.push({...rowBase(pg,TYPE_OPENING,op.name||"",area!=null?+area.toFixed(4):null,"ตร.ม.",scale),object_id:op.id,parent_id:op.parentId||"",label_mode:op.label?.mode||"auto",semanticTag:opSem,useCategory:null,...deriveMeasurementMeta(opSem)});
    }
  }
  for(const r of collectRefDistanceReport()){
    const scale=getScaleForPage(r.pg);
    rows.push({...rowBase(r.pg,TYPE_REF_DISTANCE,`${r.objectName} -> ${r.refName}`,+(r.dist!=null?r.dist:r.distPt).toFixed(4),r.unit,scale),ref_type:r.refType,object_type:r.objectType,point_role:r.pointRole,semanticTag:"dimension_line",useCategory:null,...deriveMeasurementMeta("dimension_line")});
  }
  return rows.sort((a,b)=>a[COL_PAGE]-b[COL_PAGE]);
}
function dlBlob(blob,name){const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),5000);}
function exportJSON(){
  const rows=buildRows();
  dlBlob(new Blob([JSON.stringify(rows,null,2)],{type:"application/json"}),"measurements.json");
}
function exportCSV(){
  const rows=buildRows();
  if(!rows.length){alert("ยังไม่มีข้อมูล");return;}
  // INV-2026-05-18-002 — Settings v2 export prefs (csvSeparator, includeLawBasis)
  const sep=(typeof getPref==='function')?getPref('export.csvSeparator',','):',';
  const includeLaw=(typeof getPref==='function')?getPref('export.includeLawBasis',true):true;
  const cols=[COL_PAGE,"object_id","parent_id",COL_TYPE,COL_NAME,COL_VALUE,COL_UNIT,COL_RNW,"scale","scale_source","scale_verified","area_type","ref_type","object_type","point_role","parking_type","segments","label_mode","semanticTag","useCategory"];
  if(includeLaw)cols.push("lawBasis");
  const sepRe=new RegExp(`[${sep.replace(/[\t]/g,'\\t').replace(/[-[\]{}()*+?.,\\^$|#\s]/g,'\\$&')}"\r\n]`);
  const esc=v=>{const s=String(v??"").replace(/"/g,'""');return sepRe.test(s)?`"${s}"`:s;};
  const csv="﻿"+[cols.join(sep),...rows.map(r=>cols.map(c=>esc(r[c])).join(sep))].join("\r\n");
  dlBlob(new Blob([csv],{type:"text/csv;charset=utf-8"}),"measurements.csv");
}
async function exportSummaryXLSX(){
  if(!totalPages){alert("เปิด PDF ก่อน");return false;}
  const summary=collectSummaryData();
  const body={
    case_id:currentCaseId,
    pdfName:currentFileName,
    projectInfo,
    generatedAt:new Date().toISOString(),
    summary
  };
  setStatus("กำลังสร้าง 1-page summary…");
  try{
    const r=await fetch("/export-xlsx-summary",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
    if(!r.ok){
      const d=await r.json().catch(()=>({}));
      setStatus("export summary ล้มเหลว: "+(d.error||r.status));
      if(r.status===501)alert("ติดตั้ง xlsxwriter ก่อน: pip install xlsxwriter");
      return false;
    }
    const blob=await r.blob();
    const safe=currentFileName.replace(/\.pdf$/i,"")||"export";
    dlBlob(blob,safe+"_summary.xlsx");
    setStatus("✅ export 1-page summary แล้ว ("+(blob.size||0)+" bytes)");
    return true;
  }catch(e){setStatus("export summary ล้มเหลว: "+e.message);return false;}
}
async function exportXLSX(){if(!totalPages){alert("เปิด PDF ก่อน");return;}syncProjectInfoFromForm();normalizeAllObjects();const report=collectAreas(),warnings=phase1Warnings(report);const scales={};for(let pg=1;pg<=totalPages;pg++){const pgStr=String(pg);const sc=getScaleForPage(pg);scales[pgStr]=sc?{label:scaleLabel(sc),pts_per_m:sc.pts_per_m,source:sc.source||"",verified:!!sc.verified,calibrated:!!sc.calibrated,status:scaleState(sc)}:null;}const body={case_id:currentCaseId,pageStore,pageTags,pageNames,projectInfo,siteOrientation,pageScales:scales,pdfName:currentFileName,pageCount:totalPages,warnings,auditMeta:{generatedAt:new Date().toISOString(),areaCount:report.areaRows.length,openingCount:report.openingRows.length,lineCount:report.lineCount,refCount:report.refCount,parkingCount:report.parkingCount,grossArea:report.measuredArea+report.landArea,openingArea:report.totalOpenings,netArea:report.netArea,warningCount:warnings.length}};setStatus("กำลัง export XLSX…");const r=await fetch("/export-xlsx",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});if(!r.ok){const d=await r.json().catch(()=>({}));setStatus("export XLSX ล้มเหลว: "+(d.error||""));if(r.status===501)alert("ติดตั้ง xlsxwriter ก่อน: pip install xlsxwriter");return;}const blob=await r.blob();const safe=currentFileName.replace(/\.pdf$/i,"");dlBlob(blob,(safe||"export")+"_report.xlsx");setStatus("✅ export XLSX แล้ว");}
async function exportAllPagesAnnotatedPDF(){if(!totalPages){alert("เปิด PDF ก่อน");return;}saveCurrentPage();const pages=[];for(let i=1;i<=totalPages;i++)if(!excludedPages.has(i))pages.push(i);if(!pages.length){alert("ไม่มีหน้าให้ export");return;}const body={case_id:currentCaseId,pages,pdfName:currentFileName,rotations:pageRotations,annotations:pageStore};setStatus("กำลัง export ทุกหน้า...");try{const r=await fetch("/export-pdf",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});if(!r.ok){setStatus("export ล้มเหลว");return;}const blob=await r.blob();const safe=currentFileName.replace(/\.pdf$/i,"")||"export";dlBlob(blob,safe+"_all_annotated.pdf");setStatus(`✅ export ${pages.length} หน้าแล้ว`);}catch(e){setStatus("export ล้มเหลว: "+e.message);}}
async function exportCurrentPageAnnotatedPDF(){if(!totalPages){alert("เปิด PDF ก่อน");return;}saveCurrentPage();const body={case_id:currentCaseId,pages:[curPage],pdfName:currentFileName,rotations:pageRotations,annotations:pageStore};setStatus("กำลัง export หน้าปัจจุบัน...");try{const r=await fetch("/export-pdf",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});if(!r.ok){setStatus("export ล้มเหลว");return;}const blob=await r.blob();const safe=currentFileName.replace(/\.pdf$/i,"")||"export";dlBlob(blob,safe+`_page${curPage}_annotated.pdf`);setStatus(`✅ export หน้า ${curPage} แล้ว`);}catch(e){setStatus("export ล้มเหลว: "+e.message);}}
async function exportPngZip(){
  if(!totalPages){alert("เปิด PDF ก่อน");return;}
  saveCurrentPage();
  const sel=selectedPages.size>0
    ?[...selectedPages].filter(n=>!excludedPages.has(n)).sort((a,b)=>a-b)
    :(function(){const all=[];for(let i=1;i<=totalPages;i++)if(!excludedPages.has(i))all.push(i);return all;})();
  if(!sel.length){alert("ไม่มีหน้าให้ export");return;}
  const dpi=200;
  const body={case_id:currentCaseId,pages:sel,pdfName:currentFileName,rotations:pageRotations,annotations:pageStore,dpi};
  setStatus(`🖼 กำลังสร้าง PNG ${sel.length} หน้า (DPI ${dpi})…`);
  try{
    const r=await fetch("/export-png",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
    if(r.status===413){const j=await r.json().catch(()=>({}));alert(`หน้าที่เลือกเกินขีดจำกัด (${j.max||"max"} หน้า)`);setStatus("export PNG ยกเลิก — เกิน MAX_EXPORT_PAGES");return;}
    if(!r.ok){const j=await r.json().catch(()=>({}));setStatus("export PNG ล้มเหลว: "+(j.error||r.status));return;}
    const blob=await r.blob();
    const safe=currentFileName.replace(/\.pdf$/i,"")||"export";
    dlBlob(blob,`${safe}_pages_dpi${dpi}.zip`);
    setStatus(`✅ export PNG ZIP ${sel.length} หน้าแล้ว`);
  }catch(e){setStatus("export PNG ล้มเหลว: "+e.message);}
}

// ── Save / Load project ──
// .bmaplan schema (version 1, 12 fields) is unchanged — additive only.
function _makeProjBlob(){syncProjectInfoFromForm();normalizeAllObjects();const proj={version:1,pdfName:currentFileName,totalPages,pageStore,pageRotations,pageTags,pageNames,projectInfo,siteOrientation,excludedPages:[...excludedPages],pageFloorKind,pageFloorNum};return new Blob([JSON.stringify(proj,null,2)],{type:"application/json"});}
async function _writeToHandle(h){const wr=await h.createWritable();await wr.write(_makeProjBlob());await wr.close();}
function _fallbackDownload(){const safe=currentFileName.replace(/\.pdf$/i,"")||"project";dlBlob(_makeProjBlob(),safe+".bmaplan");_markSaved("download");}
async function saveProjectAs(){if(!totalPages){alert("เปิด PDF ก่อน");return;}if(window.showSaveFilePicker){try{const safe=currentFileName.replace(/\.pdf$/i,"")||"project";const handle=await window.showSaveFilePicker({suggestedName:safe+".bmaplan",types:[{description:"BMA-Plan Project",accept:{"application/json":[".bmaplan"]}}]});currentProjectHandle=handle;await _writeToHandle(handle);_markSaved("overwrite");}catch(e){if(e.name!=="AbortError")_fallbackDownload();}}else{_fallbackDownload();}}
async function saveProject(){if(!totalPages){alert("เปิด PDF ก่อน");return;}if(currentProjectHandle){try{await _writeToHandle(currentProjectHandle);_markSaved("overwrite");return;}catch(e){currentProjectHandle=null;}}await saveProjectAs();}
async function saveSourcePdfInPlace(){
  if(!totalPages){alert("เปิด PDF ก่อน");return;}
  saveCurrentPage();
  const pages=[];for(let i=1;i<=totalPages;i++)if(!excludedPages.has(i))pages.push(i);
  if(!pages.length){alert("ไม่มีหน้าให้บันทึก");return;}
  const body={case_id:currentCaseId,pages,pdfName:currentFileName,rotations:pageRotations,annotations:pageStore};
  const hasHandle=!!currentSourcePdfHandle;
  setStatus(hasHandle?"กำลังบันทึก PDF ทับไฟล์เดิม…":"กำลังสร้าง PDF + annotations…");
  try{
    const r=await fetch("/export-pdf",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
    if(!r.ok){setStatus("บันทึก PDF ไม่สำเร็จ");return false;}
    const blob=await r.blob();
    if(currentSourcePdfHandle){
      try{
        const perm=await currentSourcePdfHandle.queryPermission?.({mode:"readwrite"});
        if(perm&&perm!=="granted"){const req=await currentSourcePdfHandle.requestPermission({mode:"readwrite"});if(req!=="granted")throw new Error("permission denied");}
        const wr=await currentSourcePdfHandle.createWritable();
        await wr.write(blob);
        await wr.close();
        setStatus(`✅ บันทึก PDF ทับ ${currentFileName} แล้ว`);
        return true;
      }catch(e){
        setStatus("เขียนทับไฟล์ไม่สำเร็จ — ดาวน์โหลดแทน ("+(e.message||e.name||"unknown")+")");
        currentSourcePdfHandle=null;
      }
    }
    const safe=currentFileName.replace(/\.pdf$/i,"")||"export";
    dlBlob(blob,safe+"_annotated.pdf");
    setStatus("✅ ดาวน์โหลด PDF + annotations แล้ว ("+pages.length+" หน้า)");
    return true;
  }catch(e){setStatus("บันทึก PDF ไม่สำเร็จ: "+e.message);return false;}
}
