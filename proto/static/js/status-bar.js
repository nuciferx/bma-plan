// proto/static/js/status-bar.js
// Status bar + analyse-UI render functions — extracted from proto/ui.html
// in sprint BLOAT-2 (2026-05-19). Mirrors the existing extraction pattern
// of semantic-meta.js + opening-parent.js: plain non-module script, top-level
// function declarations stay global, no namespace wrapper, no bundler.
//
// Reads runtime globals defined in ui.html (resolved at call time):
//   mode, curPage, totalPages, mPolys, mLines, mRefs, mParking, mOpenings,
//   pageNames, pageStore, isDirty, curSiteSemanticTag, curMarkerType,
//   SEMANTIC_TAG_LABELS (semantic-meta.js), MARKER_TYPE_LABELS, currentFileName,
//   scaleLabel, scaleState, buildSnapIndex, updatePageSummary,
//   updateWorkspaceState, updateSiteRibbon, updateCanvasTopBar,
//   _autoSwitchRibbonTabForMode, touchSetupStatus, setStatus,
//   getScaleForPage, redraw.
//
// Writes DOM only: #lbl-mode, #lbl-scale, #lbl-snaps, #lbl-objects,
// #lbl-warnings, #lbl-layer, #lbl-save-state, #bb-page-name, #scale-badge.

function updateAnalyseUI(d){const badge=document.getElementById("scale-badge");const lblS=document.getElementById("lbl-scale");const lblSnap=document.getElementById("lbl-snaps");if(!d){badge.className="warn";badge.textContent="กำลังวิเคราะห์…";lblS.textContent="—";lblSnap.textContent="—";lblSnap.title="";updatePageSummary(curPage);updateWorkspaceState();redraw();return;}buildSnapIndex(d);if(d.scale){badge.className=scaleState(d.scale);badge.textContent=scaleLabel(d.scale);lblS.textContent=scaleLabel(d.scale);/* HT-ACC-3: visible 1:N is rounded; area uses the exact pts_per_m float — surface precise values in a tooltip for expert cross-check. */if(d.scale.pts_per_m){const nExact=1000*(72/25.4)/d.scale.pts_per_m;const tip=`exact 1:${nExact.toFixed(1)} · ${d.scale.pts_per_m.toFixed(4)} pt/m (ค่าที่ใช้คำนวณพื้นที่จริง)`;lblS.title=tip;badge.title=tip;}else{lblS.title="";badge.title="";}}else{badge.className="";badge.textContent="ไม่พบ scale";lblS.textContent="—";lblS.title="";badge.title="";}lblSnap.textContent=d.degraded_mode==="raster"?"manual only":`${d.snaps?.length||0} pts · ${d.lines?.length||0} segs`;const m=d.snap_meta||{};lblSnap.title=m.engine?`engine=${m.engine}, grid=${m.snap_grid_pt}pt, raw EP=${m.raw_ep||0}, MP=${m.raw_mp||0}, CT=${m.raw_ct||0}, lines=${m.raw_lines||0}`:"";updatePageSummary(curPage);updateBottomBar();updateWorkspaceState();redraw();}
function activeLayerLabel(){const sel=document.getElementById("active-layer-select");return sel?.selectedOptions?.[0]?.textContent?.replace(/^Layer:\s*/,"").trim()||"—";}
function currentObjectCount(){return mLines.length+mRefs.length+mParking.length+mPolys.filter(p=>p.closed).length+mOpenings.filter(o=>o.closed).length;}
function currentWarningCount(){let n=0;if(totalPages&&!getScaleForPage(curPage)&&currentObjectCount()>0)n++;for(const p of mPolys){if(p.closed&&!p.name)n++;}for(const o of mOpenings){if(o.closed&&!o.parentId)n++;}return n;}
function updateBottomBar(){const name=pageNames[curPage]||`หน้า ${curPage||"—"}`;document.getElementById("bb-page-name").textContent=name;const obj=document.getElementById("lbl-objects");if(obj)obj.textContent=String(currentObjectCount());const warn=document.getElementById("lbl-warnings");if(warn)warn.textContent=String(currentWarningCount());const lyr=document.getElementById("lbl-layer");if(lyr)lyr.textContent=activeLayerLabel();updateSiteRibbon();updateCanvasTopBar();}

// HT-3: extracted label renderer — site-tag context appears in lbl-mode.
// Called from setMode() and from finishCurrentArea() (to refresh after
// curSiteSemanticTag is cleared on poly commit).
const MODE_BASE_LABELS={pan:"Pan ✋",sel:"↖ เลือก",dist:"วัดระยะ 📏",path:"ระยะต่อเนื่อง 〽",ref:"เส้นอ้างอิง ⌁",north:"ตั้งทิศเหนือ 🧭",parking:"ที่จอด 🚗",area:"วัดพื้นที่ ⬡",calib:"📐 สอบเทียบ",rect:"Rectangle ▭",circle:"Circle ⭕",ellipse:"Ellipse ⬭",ann_comment:"💬 Comment",ann_sticky:"📌 Sticky Note",ann_text:"𝕋 Text",ann_highlight:"🖍 Highlight",ann_rect:"▭ Rect Frame",ann_circle:"◯ Circle Frame",ann_cloud:"☁ Cloud Frame",ann_arrow:"➜ Arrow"};
// SEMANTIC_TAG_LABELS in semantic-meta.js is currently a key→key map (not Thai),
// so we keep a small local Thai map for the site-area tags used in lbl-mode.
// Mirrors the U2_SITE_AREA_TAGS labels.
const SITE_TAG_THAI_LABELS={building_coverage:"ปกคลุมอาคาร",open_space:"ที่ว่าง",permeable_area:"พื้นที่ซึมน้ำ",hardscape:"Hardscape",softscape:"Softscape",parking_area_outdoor:"พื้นที่จอดรถนอกอาคาร",internal_road:"ถนนภายใน"};
function updateModeLabel(m){
  m=m||mode;
  const el=document.getElementById("lbl-mode");if(!el)return;
  let txt=MODE_BASE_LABELS[m]||m;
  if(m==="area"&&curSiteSemanticTag){
    const lbl=SITE_TAG_THAI_LABELS[curSiteSemanticTag]||(typeof SEMANTIC_TAG_LABELS!=="undefined"&&SEMANTIC_TAG_LABELS[curSiteSemanticTag])||curSiteSemanticTag;
    txt+=` (ผังบริเวณ — ${lbl})`;
  }else if(m==="parking"&&curMarkerType&&curMarkerType!=="parking"){
    const lbl=(typeof MARKER_TYPE_LABELS!=="undefined"&&MARKER_TYPE_LABELS[curMarkerType])||curMarkerType;
    txt+=` (${lbl})`;
  }
  el.textContent=txt;
  _autoSwitchRibbonTabForMode(m);
}

function _markSaved(mode){isDirty=false;const ss=document.getElementById("lbl-save-state");if(ss){ss.textContent=mode==="overwrite"?"✓ Saved":"✓ Downloaded";ss.classList.remove("bb-save-dirty");ss.classList.add("bb-save-clean");}touchSetupStatus("บันทึกไฟล์โปรเจกต์แล้ว");setStatus("💾 บันทึกแล้ว");}
function _setDirty(){isDirty=true;const ss=document.getElementById("lbl-save-state");if(ss){if(ss.textContent!=="Manual save required")ss.textContent="● Unsaved changes";ss.classList.remove("bb-save-clean");ss.classList.add("bb-save-dirty");}}
