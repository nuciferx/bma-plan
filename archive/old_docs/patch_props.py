import sys

with open("proto/ui.html", "r", encoding="utf-8") as f:
    content = f.read()

old_func = """function buildRightPanel(){
  const content=document.getElementById("rp-content");
  if(!content)return;
  let html=`<div style="font-size:12px;font-weight:700;color:var(--text2);margin-bottom:4px">Layers</div>`;
  for(const [k,v] of Object.entries(layerState)){
    html+=`<div style="display:flex;align-items:center;gap:6px;font-size:12px;padding:4px 0">
      <span style="flex:1;color:${v.visible?'var(--text)':'var(--text3)'}">${v.label}</span>
      <button class="tb" onclick="toggleLayer('${k}','visible')" title="แสดง/ซ่อน" style="border:none;background:transparent;color:${v.visible?'var(--text)':'var(--text3)'}">${v.visible?'👁':'👁‍🗨'}</button>
      <button class="tb" onclick="toggleLayer('${k}','locked')" title="ล็อค/ปลดล็อค" style="border:none;background:transparent;color:${v.locked?'var(--red)':'var(--text3)'}">${v.locked?'🔒':'🔓'}</button>
      <button class="tb" onclick="toggleLayer('${k}','snap')" title="เปิด/ปิด Snap" style="border:none;background:transparent;color:${v.snap?'var(--green)':'var(--text3)'}">${v.snap?'🧲':'❌'}</button>
    </div>`;
  }
  html+=`<div style="font-size:12px;font-weight:700;color:var(--text2);margin:12px 0 4px">Object Tree</div>`;
  
  const types = [{key:'polys', list:mPolys, type:'poly'}, {key:'openings', list:mOpenings, type:'opening'}, {key:'lines', list:mLines, type:'line'}, {key:'refs', list:mRefs, type:'ref'}];
  for(const t of types) {
     if(!t.list.length) continue;
     html += `<div style="font-size:11px;font-weight:600;color:var(--text3);margin-top:6px">${layerState[t.key].label}</div>`;
     t.list.forEach((obj, idx) => {
        const isSel = selItem && selItem.type === t.type && selItem.idx === idx;
        let name = obj.name || "";
        if(!name) {
           if(t.type === 'poly') name = 'พื้นที่ ' + (idx+1);
           else if(t.type === 'opening') name = 'ช่องว่าง ' + (idx+1);
           else if(t.type === 'line') name = 'ระยะ ' + (idx+1);
           else if(t.type === 'ref') name = 'เส้นอ้างอิง ' + (idx+1);
        }
        html += `<div onclick="selectObjectFromTree('${t.type}', ${idx})" style="padding:4px 6px;margin-bottom:2px;font-size:11px;cursor:pointer;border-radius:4px;color:${isSel?'#fff':'var(--text)'};background:${isSel?'var(--blue)':'var(--surface2)'};white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${name}</div>`;
     });
  }
  
  content.innerHTML=html;
}"""

new_func = """function buildRightPanel(){
  const content=document.getElementById("rp-content");
  if(!content)return;
  let html=`<div style="font-size:12px;font-weight:700;color:var(--text2);margin-bottom:4px">Layers</div>`;
  for(const [k,v] of Object.entries(layerState)){
    html+=`<div style="display:flex;align-items:center;gap:6px;font-size:12px;padding:4px 0">
      <span style="flex:1;color:${v.visible?'var(--text)':'var(--text3)'}">${v.label}</span>
      <button class="tb" onclick="toggleLayer('${k}','visible')" title="แสดง/ซ่อน" style="border:none;background:transparent;color:${v.visible?'var(--text)':'var(--text3)'}">${v.visible?'👁':'👁‍🗨'}</button>
      <button class="tb" onclick="toggleLayer('${k}','locked')" title="ล็อค/ปลดล็อค" style="border:none;background:transparent;color:${v.locked?'var(--red)':'var(--text3)'}">${v.locked?'🔒':'🔓'}</button>
      <button class="tb" onclick="toggleLayer('${k}','snap')" title="เปิด/ปิด Snap" style="border:none;background:transparent;color:${v.snap?'var(--green)':'var(--text3)'}">${v.snap?'🧲':'❌'}</button>
    </div>`;
  }
  
  if(selItem) {
     const obj = selectedObj(selItem);
     if(obj) {
       html += `<div style="font-size:12px;font-weight:700;color:var(--text2);margin:12px 0 4px">Properties</div>`;
       html += `<div style="font-size:11px;color:var(--text);padding:4px;background:var(--surface2);border-radius:6px;line-height:1.6">`;
       html += `<div><b>Type:</b> ${selItem.type}</div>`;
       if(obj.name) html += `<div><b>Name:</b> ${obj.name}</div>`;
       if(obj.areaType) html += `<div><b>Area Type:</b> ${AREA_LABELS[obj.areaType]||obj.areaType}</div>`;
       if(obj.color) html += `<div><b>Color:</b> <span style="display:inline-block;width:10px;height:10px;background:${obj.color};border:1px solid #000"></span></div>`;
       if(selItem.type==='poly'||selItem.type==='opening') {
         const metrics = polyMetrics(obj, curPage);
         if(metrics.area!=null) html += `<div><b>Area:</b> ${metrics.area.toFixed(2)} ตร.ม.</div>`;
       } else if (selItem.type==='line'||selItem.type==='ref') {
         const metrics = lineMetrics(obj, curPage);
         if(metrics.dist!=null) html += `<div><b>Length:</b> ${metrics.dist.toFixed(2)} ม.</div>`;
       }
       html += `</div>`;
     }
  }
  
  html+=`<div style="font-size:12px;font-weight:700;color:var(--text2);margin:12px 0 4px">Object Tree</div>`;
  
  const types = [{key:'polys', list:mPolys, type:'poly'}, {key:'openings', list:mOpenings, type:'opening'}, {key:'lines', list:mLines, type:'line'}, {key:'refs', list:mRefs, type:'ref'}];
  for(const t of types) {
     if(!t.list.length) continue;
     html += `<div style="font-size:11px;font-weight:600;color:var(--text3);margin-top:6px">${layerState[t.key].label}</div>`;
     t.list.forEach((obj, idx) => {
        const isSel = selItem && selItem.type === t.type && selItem.idx === idx;
        let name = obj.name || "";
        if(!name) {
           if(t.type === 'poly') name = 'พื้นที่ ' + (idx+1);
           else if(t.type === 'opening') name = 'ช่องว่าง ' + (idx+1);
           else if(t.type === 'line') name = 'ระยะ ' + (idx+1);
           else if(t.type === 'ref') name = 'เส้นอ้างอิง ' + (idx+1);
        }
        html += `<div onclick="selectObjectFromTree('${t.type}', ${idx})" style="padding:4px 6px;margin-bottom:2px;font-size:11px;cursor:pointer;border-radius:4px;color:${isSel?'#fff':'var(--text)'};background:${isSel?'var(--blue)':'var(--surface2)'};white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${name}</div>`;
     });
  }
  
  content.innerHTML=html;
}"""

if old_func in content:
    content = content.replace(old_func, new_func)
    print("Patched properties panel")
else:
    print("NOT FOUND: properties panel old block")

with open("proto/ui.html", "w", encoding="utf-8") as f:
    f.write(content)
