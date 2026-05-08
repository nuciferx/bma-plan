import sys

with open("proto/ui.html", "r", encoding="utf-8") as f:
    content = f.read()

hit_test_old = """function hitTest(cx,cy){const THR=12/zoom;for(let i=mParking.length-1;i>=0;i--){const p=mParking[i],c=pdfToC(p.x,p.y);if(Math.hypot(cx-c.x,cy-c.y)<THR)return{type:"parking",idx:i};}if(layerState.refs.visible&&!layerState.refs.locked)for(let i=mRefs.length-1;i>=0;i--){for(const seg of lineSegments(mRefs[i])){const a=pdfToC(seg.a.x,seg.a.y),b=pdfToC(seg.b.x,seg.b.y);if(distToSeg(cx,cy,a.x,a.y,b.x,b.y)<THR)return{type:"ref",idx:i};}}if(layerState.openings.visible&&!layerState.openings.locked)for(let i=mOpenings.length-1;i>=0;i--){const op=mOpenings[i];if(!op.closed)continue;const cp=op.pts.map(p=>pdfToC(p.x,p.y));if(ptInPoly(cx,cy,cp))return{type:"opening",idx:i};for(let j=0;j<cp.length;j++){const nj=(j+1)%cp.length;if(distToSeg(cx,cy,cp[j].x,cp[j].y,cp[nj].x,cp[nj].y)<THR)return{type:"opening",idx:i};}}if(layerState.polys.visible&&!layerState.polys.locked)for(let i=mPolys.length-1;i>=0;i--){const poly=mPolys[i];if(!poly.closed)continue;const cp=poly.pts.map(p=>pdfToC(p.x,p.y));if(ptInPoly(cx,cy,cp))return{type:"poly",idx:i};for(let j=0;j<cp.length;j++){const nj=(j+1)%cp.length;if(distToSeg(cx,cy,cp[j].x,cp[j].y,cp[nj].x,cp[nj].y)<THR)return{type:"poly",idx:i};}}if(layerState.lines.visible&&!layerState.lines.locked)for(let i=mLines.length-1;i>=0;i--){for(const seg of lineSegments(mLines[i])){const a=pdfToC(seg.a.x,seg.a.y),b=pdfToC(seg.b.x,seg.b.y);if(distToSeg(cx,cy,a.x,a.y,b.x,b.y)<THR)return{type:"line",idx:i};}}return null;}"""

hit_test_new = """function hitTestAll(cx,cy){
  const THR=12/zoom;
  const hits=[];
  for(let i=mParking.length-1;i>=0;i--){const p=mParking[i],c=pdfToC(p.x,p.y);if(Math.hypot(cx-c.x,cy-c.y)<THR)hits.push({type:"parking",idx:i});}
  if(layerState.refs.visible&&!layerState.refs.locked)for(let i=mRefs.length-1;i>=0;i--){for(const seg of lineSegments(mRefs[i])){const a=pdfToC(seg.a.x,seg.a.y),b=pdfToC(seg.b.x,seg.b.y);if(distToSeg(cx,cy,a.x,a.y,b.x,b.y)<THR){hits.push({type:"ref",idx:i});break;}}}
  if(layerState.openings.visible&&!layerState.openings.locked)for(let i=mOpenings.length-1;i>=0;i--){const op=mOpenings[i];if(!op.closed)continue;const cp=op.pts.map(p=>pdfToC(p.x,p.y));if(ptInPoly(cx,cy,cp)){hits.push({type:"opening",idx:i});continue;}for(let j=0;j<cp.length;j++){const nj=(j+1)%cp.length;if(distToSeg(cx,cy,cp[j].x,cp[j].y,cp[nj].x,cp[nj].y)<THR){hits.push({type:"opening",idx:i});break;}}}
  if(layerState.polys.visible&&!layerState.polys.locked)for(let i=mPolys.length-1;i>=0;i--){const poly=mPolys[i];if(!poly.closed)continue;const cp=poly.pts.map(p=>pdfToC(p.x,p.y));if(ptInPoly(cx,cy,cp)){hits.push({type:"poly",idx:i});continue;}for(let j=0;j<cp.length;j++){const nj=(j+1)%cp.length;if(distToSeg(cx,cy,cp[j].x,cp[j].y,cp[nj].x,cp[nj].y)<THR){hits.push({type:"poly",idx:i});break;}}}
  if(layerState.lines.visible&&!layerState.lines.locked)for(let i=mLines.length-1;i>=0;i--){for(const seg of lineSegments(mLines[i])){const a=pdfToC(seg.a.x,seg.a.y),b=pdfToC(seg.b.x,seg.b.y);if(distToSeg(cx,cy,a.x,a.y,b.x,b.y)<THR){hits.push({type:"line",idx:i});break;}}}
  return hits;
}
function hitTest(cx,cy){const all=hitTestAll(cx,cy);return all.length?all[0]:null;}"""

mousedown_old = """if(mode==="sel"){const hit=hitVertex(cx,cy)||hitTest(cx,cy);if(hit){selItem={type:hit.type,idx:hit.idx};syncColorBar(selItem);const pStart=cToPdf(cx,cy);let origData;if(hit.type==="line"||hit.type==="ref"){origData=linePts(selectedObj(selItem)).map(p=>({...p}));}else if(hit.type==="parking"){const p=selectedObj(selItem);origData={x:p.x,y:p.y};}else{origData=selectedObj(selItem).pts.map(p=>({...p}));}pushUndo();dragState={...hit,startPdf:pStart,origData};ws.style.cursor=hit.vertex!=null?"crosshair":"move";setStatus(hit.vertex!=null?`ลากจุด ${hit.vertex+1} ของ object`:"ลาก object ทั้งชิ้น");}else{selItem=null;dragState=null;}redraw();return;}"""

mousedown_new = """if(mode==="sel"){
  let hit=hitVertex(cx,cy);
  if(!hit){
    const hits=hitTestAll(cx,cy);
    if(hits.length>1){showOverlappingPicker(e.clientX,e.clientY,hits);return;}
    hit=hits.length?hits[0]:null;
  }
  if(hit){selItem={type:hit.type,idx:hit.idx};syncColorBar(selItem);buildRightPanel();const pStart=cToPdf(cx,cy);let origData;if(hit.type==="line"||hit.type==="ref"){origData=linePts(selectedObj(selItem)).map(p=>({...p}));}else if(hit.type==="parking"){const p=selectedObj(selItem);origData={x:p.x,y:p.y};}else{origData=selectedObj(selItem).pts.map(p=>({...p}));}pushUndo();dragState={...hit,startPdf:pStart,origData};ws.style.cursor=hit.vertex!=null?"crosshair":"move";setStatus(hit.vertex!=null?`ลากจุด ${hit.vertex+1} ของ object`:"ลาก object ทั้งชิ้น");}else{selItem=null;dragState=null;buildRightPanel();}redraw();return;
}"""

picker_func = """function showOverlappingPicker(clientX, clientY, hits) {
  let menu = document.getElementById("overlap-picker");
  if(menu) menu.remove();
  menu = document.createElement("div");
  menu.id = "overlap-picker";
  menu.style.cssText = "position:fixed;background:var(--surface);border:1px solid var(--border);border-radius:9px;z-index:700;min-width:180px;box-shadow:0 4px 20px rgba(0,0,0,.6);overflow:hidden;padding:4px 0";
  const mw=200,mh=25*hits.length;
  menu.style.left = Math.min(clientX, window.innerWidth-mw) + "px";
  menu.style.top = Math.min(clientY, window.innerHeight-mh) + "px";
  
  let html = `<div style="font-size:11px;font-weight:600;color:var(--text2);padding:4px 14px">เลือก Object ที่ซ้อนทับกัน</div><div class="ctx-sep"></div>`;
  hits.forEach(hit => {
     const obj = selectedObj(hit);
     let name = obj.name || "";
     if(!name) {
        if(hit.type === 'poly') name = 'พื้นที่ ' + (hit.idx+1);
        else if(hit.type === 'opening') name = 'ช่องว่าง ' + (hit.idx+1);
        else if(hit.type === 'line') name = 'ระยะ ' + (hit.idx+1);
        else if(hit.type === 'ref') name = 'เส้นอ้างอิง ' + (hit.idx+1);
     }
     html += `<div class="ctx-item" onclick="this.parentElement.remove();selectObjectFromTree('${hit.type}', ${hit.idx})">${name}</div>`;
  });
  menu.innerHTML = html;
  document.body.appendChild(menu);
  setTimeout(()=>document.addEventListener("click",()=>menu.remove(),{once:true}),10);
}
"""

if hit_test_old in content:
    content = content.replace(hit_test_old, hit_test_new)
    print("Patched hitTest")
else:
    print("NOT FOUND: hitTest")

if mousedown_old in content:
    content = content.replace(mousedown_old, mousedown_new)
    print("Patched mousedown")
else:
    print("NOT FOUND: mousedown")

# Insert picker_func right before updatePageSummary
if "function updatePageSummary" in content:
    content = content.replace("function updatePageSummary", picker_func + "\nfunction updatePageSummary")
    print("Inserted showOverlappingPicker")

with open("proto/ui.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Done patching overlapping picker")
