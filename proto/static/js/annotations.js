// proto/static/js/annotations.js
// Annotation helpers — extracted from proto/ui.html in sprint BLOAT-4 (2026-05-20).
// 13 functions covering 7 annotation types (comment/text/highlight/rect/circle/cloud/arrow)
// + sticky-note HTML overlay (INV-2026-05-19-005). Mirrors the no-bundler extraction
// pattern of semantic-meta.js / opening-parent.js / status-bar.js / export-save.js.
//
// Reads runtime globals from ui.html (resolved at call time):
//   curPage, curColor, totalPages, zoom, ws, canvas, ctx, pageStore, getStore,
//   pdfToC, cToPdf, redraw, saveCurrentPage, setStatus, pushUndo, _setDirty,
//   escHtml.
//
// Writes runtime globals (mutation):
//   pageStore[pg].annotations (array — additive items; field name unchanged from
//   schema), DOM (#ann-edit-overlay, #sticky-layer .sticky-card).

function ensureAnnotations(pg=curPage){const s=getStore(pg);if(!Array.isArray(s.annotations))s.annotations=[];return s.annotations;}
function newAnnotationId(type){return"ann_"+type+"_"+Date.now().toString(36)+"_"+Math.random().toString(36).slice(2,6);}
function addAnnotation(ann){const arr=ensureAnnotations(curPage);arr.push(ann);saveCurrentPage();redraw();if(ann.type==="sticky")renderStickyCards();return ann;}

/* INV-2026-05-19-005: Sticky note (post-it) HTML overlay renderer.
   Approach B (from invent pipeline): new ann_sticky type rendered as HTML div
   positioned via pdfToC(). Browser-native textarea = correct Thai IME, selection,
   line-wrap. Other 6 annotation types (comment/text/highlight/rect/circle/cloud/arrow)
   stay on canvas via drawAnnotations(); sticky skips that path entirely. */
function renderStickyCards(){
  const layer=document.getElementById("sticky-layer");if(!layer)return;
  const arr=(getStore(curPage)?.annotations)||[];
  const stickyIds=new Set();
  arr.forEach(ann=>{if(ann.type==="sticky")stickyIds.add(ann.id);});
  /* Remove cards whose annotation no longer exists (deleted or page-switched) */
  layer.querySelectorAll(".sticky-card").forEach(card=>{
    if(!stickyIds.has(card.dataset.id))card.remove();
  });
  /* Create or update each sticky */
  arr.forEach(ann=>{
    if(ann.type!=="sticky"||!ann.pts?.[0])return;
    let card=layer.querySelector(`.sticky-card[data-id="${ann.id}"]`);
    if(!card)card=_createStickyCard(ann,layer);
    /* Position update via pdfToC (survives pan/zoom) */
    const c=pdfToC(ann.pts[0].x,ann.pts[0].y);
    card.style.left=c.x+"px";
    card.style.top=c.y+"px";
    /* Sync text from data (in case it was changed by undo/redo) */
    const ta=card.querySelector("textarea");
    if(ta&&document.activeElement!==ta&&ta.value!==(ann.text||""))ta.value=ann.text||"";
  });
}
function _createStickyCard(ann,layer){
  const card=document.createElement("div");
  card.className="sticky-card";
  card.dataset.id=ann.id;
  card.style.width=(ann.width||120)+"px";
  card.style.minHeight=(ann.height||80)+"px";
  const header=document.createElement("div");
  header.className="sticky-header";
  header.innerHTML='<span class="sticky-drag-handle">⋮⋮</span><span class="sticky-delete-btn" title="ลบ post-it">×</span>';
  card.appendChild(header);
  const body=document.createElement("textarea");
  body.className="sticky-body";
  body.value=ann.text||"";
  body.placeholder="เขียน note…";
  body.spellcheck=false;
  card.appendChild(body);
  /* Edit — input event updates ann.text + marks dirty */
  body.addEventListener("input",()=>{
    const arr=getStore(curPage)?.annotations||[];
    const obj=arr.find(a=>a.id===ann.id);
    if(obj){obj.text=body.value;_setDirty();}
  });
  body.addEventListener("keydown",e=>{
    if(e.key==="Escape"){e.stopPropagation();body.blur();}
  });
  /* Stop pan/zoom hijacking the textarea */
  body.addEventListener("wheel",e=>e.stopPropagation(),{passive:true});
  /* Delete */
  header.querySelector(".sticky-delete-btn").addEventListener("click",e=>{
    e.stopPropagation();
    pushUndo();
    const st=getStore(curPage);
    if(st?.annotations){st.annotations=st.annotations.filter(a=>a.id!==ann.id);saveCurrentPage();}
    card.remove();
  });
  /* Drag by header */
  let dragSt=null;
  header.addEventListener("pointerdown",e=>{
    if(e.target.classList.contains("sticky-delete-btn"))return;
    pushUndo();
    const startC=cToPdf(e.clientX-ws.getBoundingClientRect().left,e.clientY-ws.getBoundingClientRect().top);
    dragSt={origX:ann.pts[0].x,origY:ann.pts[0].y,startX:startC.x,startY:startC.y};
    header.setPointerCapture(e.pointerId);
    e.preventDefault();
  });
  header.addEventListener("pointermove",e=>{
    if(!dragSt)return;
    const wsR=ws.getBoundingClientRect();
    const cur=cToPdf(e.clientX-wsR.left,e.clientY-wsR.top);
    ann.pts[0]={x:dragSt.origX+(cur.x-dragSt.startX),y:dragSt.origY+(cur.y-dragSt.startY)};
    const c=pdfToC(ann.pts[0].x,ann.pts[0].y);
    card.style.left=c.x+"px";
    card.style.top=c.y+"px";
  });
  header.addEventListener("pointerup",e=>{if(dragSt){dragSt=null;saveCurrentPage();}});
  layer.appendChild(card);
  return card;
}
function clearAnnotations(){if(!totalPages){alert("เปิด PDF ก่อน");return;}const arr=ensureAnnotations(curPage);if(arr.length===0){setStatus("ไม่มี annotation บนหน้านี้");return;}if(!confirm(`ลบ ${arr.length} annotation(s) บนหน้านี้?`))return;arr.length=0;saveCurrentPage();redraw();setStatus("ลบ annotation ทั้งหมดแล้ว");}
// HT-11: per-annotation edit + delete. Per user-test 2026-05-17 "ทำให้แก้ไขได้ทุกอัน".
// Hit-test for annotation at canvas coords. Returns index on curPage or -1.
function annotationHitTest(cx,cy){
  const arr=(getStore(curPage)||{}).annotations||[];
  const tol=8/Math.max(zoom,0.1);
  for(let i=arr.length-1;i>=0;i--){
    const ann=arr[i];
    if(!ann||!ann.pts||!ann.pts.length)continue;
    if(ann.type==="comment"||ann.type==="text"){
      const p=pdfToC(ann.pts[0].x,ann.pts[0].y);
      const r=ann.type==="comment"?Math.max(8,10/zoom):14;
      if(Math.hypot(p.x-cx,p.y-cy)<=r+tol)return i;
    }else if(ann.type==="highlight"||ann.type==="rect_frame"){
      if(ann.pts.length<2)continue;
      const a=pdfToC(ann.pts[0].x,ann.pts[0].y),b=pdfToC(ann.pts[1].x,ann.pts[1].y);
      const x0=Math.min(a.x,b.x)-tol,y0=Math.min(a.y,b.y)-tol,x1=Math.max(a.x,b.x)+tol,y1=Math.max(a.y,b.y)+tol;
      if(cx>=x0&&cx<=x1&&cy>=y0&&cy<=y1)return i;
    }else if(ann.type==="circle_frame"){
      if(ann.pts.length<2)continue;
      const c=pdfToC(ann.pts[0].x,ann.pts[0].y),e=pdfToC(ann.pts[1].x,ann.pts[1].y);
      const r=Math.hypot(e.x-c.x,e.y-c.y);
      const d=Math.hypot(cx-c.x,cy-c.y);
      if(Math.abs(d-r)<=tol*2)return i;
    }else if(ann.type==="arrow"){
      if(ann.pts.length<2)continue;
      const a=pdfToC(ann.pts[0].x,ann.pts[0].y),b=pdfToC(ann.pts[1].x,ann.pts[1].y);
      const dx=b.x-a.x,dy=b.y-a.y,len2=dx*dx+dy*dy;
      if(len2<1e-6)continue;
      const t=Math.max(0,Math.min(1,((cx-a.x)*dx+(cy-a.y)*dy)/len2));
      const px=a.x+t*dx,py=a.y+t*dy;
      if(Math.hypot(cx-px,cy-py)<=tol*2)return i;
    }else if(ann.type==="cloud_frame"){
      if(ann.pts.length<3)continue;
      const cp=ann.pts.map(p=>pdfToC(p.x,p.y));
      const xs=cp.map(p=>p.x),ys=cp.map(p=>p.y);
      const x0=Math.min.apply(null,xs)-tol,y0=Math.min.apply(null,ys)-tol;
      const x1=Math.max.apply(null,xs)+tol,y1=Math.max.apply(null,ys)+tol;
      if(cx>=x0&&cx<=x1&&cy>=y0&&cy<=y1)return i;
    }
  }
  return -1;
}
function deleteAnnotation(idx){
  const arr=(getStore(curPage)||{}).annotations||[];
  if(idx<0||idx>=arr.length)return false;
  pushUndo();
  arr.splice(idx,1);
  saveCurrentPage();
  redraw();
  setStatus("ลบ annotation แล้ว");
  return true;
}
function openAnnotationEditModal(idx){
  const arr=(getStore(curPage)||{}).annotations||[];
  const ann=arr[idx];
  if(!ann)return;
  let ov=document.getElementById("ann-edit-overlay");
  if(!ov){
    ov=document.createElement("div");
    ov.id="ann-edit-overlay";
    ov.style.cssText="position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:9003;display:none;align-items:center;justify-content:center";
    document.body.appendChild(ov);
    ov.addEventListener("click",e=>{if(e.target===ov)closeAnnotationEditModal();});
  }
  const hasText=ann.text!==undefined||["comment","text","highlight","rect_frame","circle_frame","cloud_frame","arrow"].includes(ann.type);
  const typeLabel=({comment:"💬 Comment",text:"𝕋 Text Label",highlight:"🖍 Highlight",rect_frame:"▭ Rect Frame",circle_frame:"◯ Circle Frame",cloud_frame:"☁ Cloud Frame",arrow:"➜ Arrow"})[ann.type]||ann.type;
  ov.innerHTML=`<div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;width:min(420px,92vw);padding:18px;color:var(--text);box-shadow:0 8px 32px rgba(0,0,0,.6)">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px"><strong style="font-size:14px">✎ แก้ไข ${escHtml(typeLabel)}</strong><button onclick="closeAnnotationEditModal()" style="background:none;border:0;color:var(--text2);font-size:18px;cursor:pointer">✕</button></div>
    ${hasText?`<label style="display:block;font-size:11px;color:var(--text2);margin-bottom:4px">ข้อความ / Subject</label><textarea id="ann-edit-text" placeholder="เช่น 'ระยะถอยร่นน้อยไป'" style="width:100%;min-height:64px;padding:8px;background:var(--surface2);color:var(--text);border:1px solid var(--border);border-radius:6px;font-family:inherit;font-size:13px;resize:vertical;margin-bottom:12px;box-sizing:border-box">${escHtml(ann.text||"")}</textarea>`:""}
    <label style="display:block;font-size:11px;color:var(--text2);margin-bottom:4px">สี</label>
    <input type="color" id="ann-edit-color" value="${escHtml(ann.color||"#ffd60a")}" style="width:60px;height:32px;cursor:pointer;border:1px solid var(--border);border-radius:4px;background:var(--surface2);padding:2px">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-top:18px;gap:8px">
      <button id="ann-edit-delete-btn" onclick="if(confirm('ลบ annotation นี้?')){deleteAnnotation(${idx});closeAnnotationEditModal();}" style="background:rgba(255,69,58,.15);color:var(--red,#dc2626);border:1px solid var(--red,#dc2626);border-radius:6px;padding:6px 12px;font-size:12px;cursor:pointer;font-weight:600">🗑 ลบ annotation นี้</button>
      <div style="display:flex;gap:6px">
        <button onclick="closeAnnotationEditModal()" style="background:var(--surface3);color:var(--text);border:1px solid var(--border);border-radius:6px;padding:6px 12px;font-size:12px;cursor:pointer">ยกเลิก</button>
        <button id="ann-edit-save-btn" onclick="saveAnnotationEdit(${idx})" style="background:var(--blue,#2563eb);color:#fff;border:0;border-radius:6px;padding:6px 14px;font-size:12px;font-weight:700;cursor:pointer">บันทึก</button>
      </div>
    </div>
  </div>`;
  ov.style.display="flex";
  setTimeout(()=>{const ta=document.getElementById("ann-edit-text");if(ta)ta.focus();},50);
}
function closeAnnotationEditModal(){const ov=document.getElementById("ann-edit-overlay");if(ov)ov.style.display="none";}
function saveAnnotationEdit(idx){
  const arr=(getStore(curPage)||{}).annotations||[];
  const ann=arr[idx];
  if(!ann)return;
  const ta=document.getElementById("ann-edit-text");
  const cp=document.getElementById("ann-edit-color");
  pushUndo();
  if(ta)ann.text=ta.value;
  if(cp)ann.color=cp.value;
  saveCurrentPage();
  redraw();
  closeAnnotationEditModal();
  setStatus("บันทึก annotation แล้ว");
}
function _annColor(){return curColor||"#ffd60a";}
function drawAnnotations(){const arr=getStore(curPage).annotations;if(!arr||!arr.length)return;const lw=Math.max(1,2/zoom);ctx.save();arr.forEach(ann=>{const col=ann.color||"#ffd60a",opa=ann.opacity??0.8;ctx.globalAlpha=opa;ctx.strokeStyle=col;ctx.fillStyle=col;ctx.lineWidth=lw;ctx.setLineDash([]);if(ann.type==="comment"&&ann.pts?.[0]){const c=pdfToC(ann.pts[0].x,ann.pts[0].y);const r=Math.max(8,10/zoom);ctx.beginPath();ctx.arc(c.x,c.y,r,0,Math.PI*2);ctx.fill();ctx.fillStyle="#000";ctx.font=`bold ${Math.max(10,12/zoom)}px sans-serif`;ctx.fillText("💬",c.x-r*0.5,c.y+r*0.4);if(ann.text){ctx.fillStyle=col;ctx.font=`${Math.max(10,11/zoom)}px sans-serif`;ctx.fillText(ann.text,c.x+r+4/zoom,c.y+4/zoom);}}else if(ann.type==="text"&&ann.pts?.[0]){const c=pdfToC(ann.pts[0].x,ann.pts[0].y);const fs=ann.fontSize||Math.max(10,12/zoom);ctx.font=`${fs}px sans-serif`;ctx.fillStyle=col;ctx.fillText(ann.text||"",c.x,c.y);}else if(ann.type==="highlight"&&ann.pts?.length>=2){const a=pdfToC(ann.pts[0].x,ann.pts[0].y),b=pdfToC(ann.pts[1].x,ann.pts[1].y);ctx.globalAlpha=opa*0.35;ctx.fillRect(Math.min(a.x,b.x),Math.min(a.y,b.y),Math.abs(b.x-a.x),Math.abs(b.y-a.y));}else if(ann.type==="rect_frame"&&ann.pts?.length>=2){const a=pdfToC(ann.pts[0].x,ann.pts[0].y),b=pdfToC(ann.pts[1].x,ann.pts[1].y);ctx.strokeRect(Math.min(a.x,b.x),Math.min(a.y,b.y),Math.abs(b.x-a.x),Math.abs(b.y-a.y));}else if(ann.type==="circle_frame"&&ann.pts?.length>=2){const c=pdfToC(ann.pts[0].x,ann.pts[0].y),e=pdfToC(ann.pts[1].x,ann.pts[1].y);const r=Math.hypot(e.x-c.x,e.y-c.y);ctx.beginPath();ctx.arc(c.x,c.y,r,0,Math.PI*2);ctx.stroke();}else if(ann.type==="cloud_frame"&&ann.pts?.length>=3){const cp=ann.pts.map(p=>pdfToC(p.x,p.y));ctx.beginPath();for(let i=0;i<cp.length;i++){const j=(i+1)%cp.length;const mx=(cp[i].x+cp[j].x)/2,my=(cp[i].y+cp[j].y)/2;const dx=cp[j].x-cp[i].x,dy=cp[j].y-cp[i].y;const len=Math.hypot(dx,dy);const bulge=Math.min(len*0.2,20/zoom);const nx=-dy/len*bulge,ny=dx/len*bulge;ctx.moveTo(cp[i].x,cp[i].y);ctx.quadraticCurveTo(mx+nx,my+ny,cp[j].x,cp[j].y);}ctx.stroke();}else if(ann.type==="arrow"&&ann.pts?.length>=2){const a=pdfToC(ann.pts[0].x,ann.pts[0].y),b=pdfToC(ann.pts[1].x,ann.pts[1].y);ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();const ang=Math.atan2(b.y-a.y,b.x-a.x),hd=Math.max(10,12/zoom);ctx.beginPath();ctx.moveTo(b.x,b.y);ctx.lineTo(b.x-Math.cos(ang-Math.PI/6)*hd,b.y-Math.sin(ang-Math.PI/6)*hd);ctx.lineTo(b.x-Math.cos(ang+Math.PI/6)*hd,b.y-Math.sin(ang+Math.PI/6)*hd);ctx.closePath();ctx.fill();}});ctx.restore();}
