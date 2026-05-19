// proto/static/js/page-setup.js
// Page Setup modal helpers — extracted from proto/ui.html in sprint BLOAT-5
// (2026-05-20). Mirrors the no-bundler extraction pattern of semantic-meta.js,
// opening-parent.js, status-bar.js, export-save.js, annotations.js.
//
// Covers the three Page-Setup sprints (INV-2026-05-18-001a/b/c):
//   001a — context-sensitive inspector (dashboard ⇄ page-card switch)
//   001b — floor sub-types for plan tag (basement/normal/mechanical/rooftop/custom)
//   001c — permanent delete + renumber-map (client side; server has /rebuild-pdf)
//
// Reads runtime globals from ui.html (resolved at call time):
//   curPage, totalPages, pageStore, pageTags, pageNames, pageRotations,
//   pageFloorKind (state, declared in ui.html), pageFloorNum (same),
//   excludedPages, currentCaseId, docVersion, setupSelectedPage, mPts,
//   AUTO_TEMPLATES, TAG_OPTIONS, getRot, getScaleForPage, escHtml,
//   caseQuery, pushUndo, setStatus, buildSidebar, buildTagGrid (kept in
//   ui.html), touchSetupStatus, loadPage, setPageName, setPageTag,
//   toggleExcludePage.
//
// Writes runtime globals: pageNames, pageFloorKind, pageFloorNum,
// setupSelectedPage, _pendingDeleteN, pageStore / pageTags / pageRotations
// / pageNames / excludedPages (during _reindexPageDicts), isDirty, totalPages
// (during _executeRenumberDelete).

// ── Constants (INV-001b) ──
const FLOOR_KIND_LABELS={basement:"ชั้นใต้ดิน",normal:"ชั้น",mechanical:"ชั้นห้องเครื่อง",rooftop:"ชั้นดาดฟ้า",custom:"(ตั้งเอง)"};
const FLOOR_KIND_OPTIONS=[["","— เลือกประเภทชั้น —"],["basement","ชั้นใต้ดิน"],["normal","ชั้น (ปกติ)"],["mechanical","ชั้นห้องเครื่อง"],["rooftop","ชั้นดาดฟ้า"],["custom","(ตั้งชื่อเอง)"]];

// ── autoNamePage + floor sub-type setters (INV-001b) ──
function autoNamePage(n,tag,force=false){if(!tag||!AUTO_TEMPLATES[tag])return;if(!force&&pageNames[n]&&pageNames[n]!==`หน้า ${n}`)return;
  // INV-2026-05-18-001b — floor sub-types for plan tag
  if(tag==='plan'&&pageFloorKind[n]){
    const k=pageFloorKind[n];
    if(k==='custom')return; // user enters name manually
    if(k==='mechanical'){pageNames[n]=FLOOR_KIND_LABELS.mechanical;return;}
    if(k==='rooftop'){pageNames[n]=FLOOR_KIND_LABELS.rooftop;return;}
    if(k==='basement'){pageNames[n]=`${FLOOR_KIND_LABELS.basement} ${pageFloorNum[n]||1}`;return;}
    if(k==='normal'){pageNames[n]=`${FLOOR_KIND_LABELS.normal} ${pageFloorNum[n]||1}`;return;}
  }
  const count=countTagBefore(n,tag);pageNames[n]=AUTO_TEMPLATES[tag](count);
}
function setPageFloorKind(n,kind){
  pushUndo();/* HT-18 */
  if(!kind){delete pageFloorKind[n];delete pageFloorNum[n];}
  else{pageFloorKind[n]=kind;if((kind==='basement'||kind==='normal')&&!pageFloorNum[n])pageFloorNum[n]=1;if(kind!=='custom')autoNamePage(n,'plan',true);}
  buildSidebar();buildTagGrid();touchSetupStatus();if(typeof _renderSetupInspector==='function')_renderSetupInspector();
}
function setPageFloorNum(n,num){pushUndo();/* HT-18 */pageFloorNum[n]=Math.max(1,parseInt(num,10)||1);autoNamePage(n,'plan',true);buildSidebar();buildTagGrid();touchSetupStatus();if(typeof _renderSetupInspector==='function')_renderSetupInspector();}
function countTagBefore(n,tag){let c=0;for(let i=1;i<=n;i++){if((pageTags[i]||"")===tag&&!excludedPages.has(i))c++;}return c;}

// ── Inspector dashboard/page-card + renumber/delete (INV-001a/c) ──
function selectSetupPage(n){setupSelectedPage=n;document.querySelectorAll(".tag-cell").forEach(c=>c.classList.toggle("selected",+c.dataset.page===n));_renderSetupInspector();}
// INV-2026-05-18-001a — context-sensitive inspector (dashboard ⇄ page-card) + readiness chips
function _pageReadiness(n){if(excludedPages.has(n))return"gray";const tag=pageTags[n]||"";if(!tag)return"red";const sc=typeof getScaleForPage==="function"?getScaleForPage(n):null;if(!sc)return"amber";return"green";}
function _setupCountObjects(n){const s=pageStore&&pageStore[n];if(!s)return 0;return(s.polys?.filter(p=>p.closed).length||0)+(s.lines?.length||0)+(s.openings?.filter(o=>o.closed).length||0);}
function _renderSetupDashboard(){let nLive=0,nTag=0,nName=0,nScale=0,nMeas=0;const issues=[];for(let i=1;i<=totalPages;i++){if(excludedPages.has(i))continue;nLive++;const tag=pageTags[i]||"";if(tag)nTag++;if(pageNames[i])nName++;const sc=typeof getScaleForPage==="function"?getScaleForPage(i):null;if(sc)nScale++;if(_setupCountObjects(i)>0)nMeas++;if(!tag)issues.push({n:i,cls:"red",msg:"ยังไม่จัดหมวด"});else if(!sc)issues.push({n:i,cls:"amber",msg:"ยังไม่ตั้ง scale"});}const stat=(label,v,total)=>{const pct=total?(v/total*100):0;const done=v===total&&total>0;return`<div class="psi-stat ${done?"complete":""}"><div class="psi-stat-row"><span>${label}</span><span class="v">${v}/${total}</span></div><div class="psi-bar"><div class="fill" style="width:${pct}%"></div></div></div>`;};const issuesHtml=issues.length===0?'<div class="empty">✓ พร้อมวัดทุกหน้าที่เปิดอยู่</div>':issues.slice(0,6).map(i=>`<div class="psi-issue ${i.cls==="red"?"red":""}" onclick="selectSetupPage(${i.n})"><span class="icon">${i.cls==="red"?"●":"◐"}</span><span class="pg">หน้า ${i.n}</span><span class="msg">${i.msg}</span></div>`).join("")+(issues.length>6?`<div class="more">+ ${issues.length-6} อื่นๆ</div>`:"");return`<div class="psi-block"><h3>📊 Project Readiness</h3>${stat("จัดหมวดหน้า",nTag,nLive)}${stat("ตั้งชื่อหน้า",nName,nLive)}${stat("ตั้ง scale",nScale,nLive)}${stat("มีการวัด",nMeas,nLive)}<div class="psi-issues"><h4>⚠ Top issues</h4>${issuesHtml}</div></div>`;}
function _renderSetupPageCard(n){const tag=pageTags[n]||"",name=pageNames[n]||"",rot=(typeof getRot==="function"?getRot(n):0),sc=(typeof getScaleForPage==="function"?getScaleForPage(n):null),objs=_setupCountObjects(n),layers=((pageStore&&pageStore[n]&&pageStore[n].layers)||[]).length,excl=excludedPages.has(n);const scaleTxt=sc?'<span style="color:#30d158">●</span> manual':'<span style="color:#ff453a">●</span> ยังไม่ตั้ง';const optHtml=TAG_OPTIONS.map(o=>`<option value="${o.value}"${tag===o.value?" selected":""}>${escHtml(o.label)}</option>`).join("");return`<button class="psi-back" onclick="_setupBack()">← กลับไปภาพรวม</button><div class="psi-card-preview"><span class="pgno-tag">หน้า ${n}</span>${rot?`<span class="rot-tag">${rot}°</span>`:""}<img src="/thumb-md/${n}?${caseQuery()}&rot=${rot}&v=${docVersion}" loading="lazy"></div><div class="psi-block"><div class="pf-row"><label>หมวดหมู่ (tag)</label><select onchange="setPageTag(${n},this.value)">${optHtml}</select></div>${tag==='plan'?`<div class="pf-row"><label>ประเภทชั้น (INV-001b)</label><div style="display:flex;gap:6px"><select style="flex:1" onchange="setPageFloorKind(${n},this.value)">${FLOOR_KIND_OPTIONS.map(([v,l])=>`<option value="${v}"${(pageFloorKind[n]||'')===v?' selected':''}>${escHtml(l)}</option>`).join('')}</select>${(pageFloorKind[n]==='basement'||pageFloorKind[n]==='normal')?`<input type="number" min="1" step="1" value="${pageFloorNum[n]||1}" style="width:64px" onchange="setPageFloorNum(${n},this.value)" title="เลขชั้น">`:''}</div>${pageFloorKind[n]==='custom'?'<div style="font-size:10.5px;color:#ffcc00;margin-top:3px">⌨ ตั้งชื่อในช่องด้านล่าง (จะไม่ถูก template ทับ)</div>':''}</div>`:''}<div class="pf-row"><label>ชื่อหน้า</label><input type="text" value="${escHtml(name)}" placeholder="หน้า ${n}" onchange="setPageName(${n},this.value)"></div></div><div class="psi-card-meta"><div class="cell"><div class="k">Rotation</div><div class="v">${rot}°</div></div><div class="cell"><div class="k">Scale</div><div class="v">${scaleTxt}</div></div><div class="cell"><div class="k">Objects</div><div class="v">${objs}</div></div><div class="cell"><div class="k">Layers</div><div class="v">${layers}</div></div></div><div class="psi-danger"><div class="ttl">⚠ ลบ / ซ่อนหน้า</div><div class="hint">${excl?"หน้านี้ถูกซ่อนแล้ว — คลิกเพื่อคืน":"ซ่อน = soft-hide (export ตัดออก) / ลบถาวร = รีบิวต์ PDF (ไม่ย้อนกลับหลังบันทึก)"}</div><button onclick="toggleExcludePage(${n})">${excl?"↺ คืนหน้า":"🚫 ซ่อนหน้านี้"}</button> <button onclick="_openRenumberDialog(${n})" title="ลบหน้าถาวร + renumber ผ่าน /rebuild-pdf">🗑 ลบถาวร...</button></div>`;}
function _setupBack(){setupSelectedPage=null;document.querySelectorAll(".tag-cell").forEach(c=>c.classList.remove("selected"));_renderSetupInspector();}
function _renderSetupInspector(){const el=document.getElementById("setup-inspector-content");if(!el)return;if(setupSelectedPage==null||excludedPages.has(setupSelectedPage)){el.innerHTML=_renderSetupDashboard();}else{el.innerHTML=_renderSetupPageCard(setupSelectedPage);}}
// INV-2026-05-18-001c — Permanent delete with renumber-map (research Q1-Q4 locked)
let _pendingDeleteN=null;
function _openRenumberDialog(targetN){
  // Q4 hard-block: refuse during draw (HT-7 pattern)
  if(typeof mPts!=='undefined'&&Array.isArray(mPts)&&mPts.length>0){
    setStatus("วาดอยู่ — กด Enter จบหรือ Esc ยกเลิกก่อนลบหน้า");
    return;
  }
  if(totalPages<=1){setStatus("ต้องมีอย่างน้อย 1 หน้า — ลบไม่ได้");return;}
  _pendingDeleteN=targetN;
  const tbl=document.getElementById("rebuild-table");
  let newN=0;
  const rows=[];
  for(let i=1;i<=totalPages;i++){
    if(i===targetN){rows.push(`<tr class="gone"><td class="from">หน้า ${i}</td><td class="arr">→</td><td class="del">ลบ</td></tr>`);}
    else{newN++;rows.push(`<tr><td class="from">หน้า ${i}</td><td class="arr">→</td><td class="to">หน้า ${newN}</td></tr>`);}
  }
  tbl.innerHTML=`<thead><tr><th>เดิม</th><th></th><th>ใหม่</th></tr></thead><tbody>${rows.join("")}</tbody>`;
  document.getElementById("rebuild-overlay").classList.add("open");
}
function closeRebuildDialog(){document.getElementById("rebuild-overlay").classList.remove("open");_pendingDeleteN=null;}
async function _executeRenumberDelete(){
  if(_pendingDeleteN==null){closeRebuildDialog();return;}
  const targetN=_pendingDeleteN;
  const btn=document.getElementById("rebuild-confirm-btn");
  if(btn){btn.disabled=true;btn.textContent="กำลังลบ...";}
  try{
    const r=await fetch("/rebuild-pdf",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({case_id:currentCaseId,delete_numbers:[targetN]})});
    if(!r.ok){const err=await r.json().catch(()=>({error:"unknown"}));throw new Error(err.error||"server error");}
    const j=await r.json();
    if(typeof pushUndo==='function')pushUndo(); // session-scoped undo
    _reindexPageDicts(j.renumberMap,j.deletedNumbers||[]);
    totalPages=j.totalPages;
    docVersion++; // invalidate thumbnail URL cache
    // If curPage was deleted or out of range, redirect
    if(curPage>totalPages||((j.deletedNumbers||[]).includes(curPage))){
      const next=Math.min(curPage,totalPages)||1;
      if(typeof loadPage==='function')await loadPage(next);
    }
    setupSelectedPage=null;
    isDirty=true;
    if(typeof buildSidebar==='function')buildSidebar();
    if(typeof buildTagGrid==='function')buildTagGrid();
    setStatus(`✅ ลบหน้า ${targetN} แล้ว — เหลือ ${totalPages} หน้า`);
    closeRebuildDialog();
  }catch(e){
    setStatus("ลบหน้าไม่สำเร็จ: "+(e.message||e));
    if(btn){btn.disabled=false;btn.textContent="ยืนยันลบและรีบิวต์";}
  }
}
function _reindexPageDicts(renumberMap,deletedNumbers){
  // Walk every per-page dict and rebuild with new keys per server's authoritative renumberMap.
  // renumberMap: {oldN: newN} for surviving pages (1-indexed both sides).
  // deletedNumbers: list of old page numbers that were removed.
  const reindexDict=(d)=>{const out={};for(const[oldStr,v]of Object.entries(d)){const oldN=+oldStr;const newN=renumberMap[String(oldN)];if(newN!=null)out[newN]=v;}return out;};
  pageStore=reindexDict(pageStore);
  pageTags=reindexDict(pageTags);
  pageNames=reindexDict(pageNames);
  pageRotations=reindexDict(pageRotations);
  pageFloorKind=reindexDict(pageFloorKind);
  pageFloorNum=reindexDict(pageFloorNum);
  // excludedPages is a Set of ints
  const newExcl=new Set();
  for(const oldN of excludedPages){const newN=renumberMap[String(oldN)];if(newN!=null)newExcl.add(newN);}
  excludedPages=newExcl;
}
