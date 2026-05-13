# Plan: Phase H.1 + H.2 + H.0 (45° Lock)

> **Branch:** `feature/phase-h-curves-annotate` (สร้างใหม่จาก `feature/mockup-v3-alignment` หรือจาก `main` หลัง Phase G ถูก merge)
> **Source plan ที่อ้างอิง:** `plans/project-scale-page-measure-curried-seal.md` (Phase G plan — "Out of scope" section)
> **Phase G สถานะ:** ✅ DONE (proto `52167d8`) — Menu Wiring 6 dropdowns, 14 helpers, 11 keyboard shortcuts, per-page layer memory bug fix

---

## Context

หลังจาก Phase G เสร็จ (Menu Wiring + Measure/Layer power-up), งานที่ถูก defer คือ:

- **H.1** — Curves & circles (Polygon curves, Circle, Ellipse, Quick Rectangle)
- **H.2** — Annotate menu (item 14 ใน menu bar)
- **H.3** — File / Edit / View / Review / Export / Workspace / Help dropdowns ที่เหลือ (deferred ต่อ — ไม่ทำใน sprint นี้)

**เพิ่มในรอบนี้ตามคำขอผู้ใช้:**
- **H.0** — 45° Angle Lock — ตอนนี้ Shift / orthoMode ล็อกแค่ 0°/90° ผู้ใช้ต้องการล็อก 45° ด้วย **เพื่อวัด `2h` (ระยะจาก property line ตามเส้นทแยงมุม) ของ road width** ในงานออกแบบ

---

## Hard Forbidden (ห้ามแตะ)

- `proto/server.py`
- `polyMetrics()`, `polyAreaM2()`, `polySelfIntersects()` — ไม่แก้ฟังก์ชั่นเดิม (จะ**เพิ่ม** `circleAreaM2`, `ellipseAreaM2`, `polygonAreaWithArcs` แทน)
- `pdfToC()`, `cToPdf()`, scale math, coordinate conversion
- Snap algorithm core (`buildSnapIndex`, `snap`)
- Export logic, save/load logic core
- `.bmaplan` schema ของ object ปัจจุบัน — เพิ่ม optional fields เท่านั้น (backward compat)
- ห้ามเพิ่ม OCR / AI / Rule Engine / FAR/OSR/setback pass-fail / legal checker

---

## Phase H.0 — 45° Angle Lock 🆕 (ผู้ใช้ขอ)

### Goal

ขยาย angle constrain จาก 2 ทิศ (0°/90°) → **8 ทิศ (0°/45°/90°/135°/180°/225°/270°/315°)** เพื่อรองรับการวัดเส้นทแยงมุม เช่น `2h` ของระยะร่นจากเขตที่ดินตามแนวขวางถนน

### Use case จริง

- กฎควบคุมอาคาร: `setback = 2h` ที่วัดเป็นเส้นทแยงมุมจากเขตที่ดิน — ต้องล็อก 45° ได้
- การวาดเส้นเฉียง ๆ ที่ตรงทแยงมุม (เช่นแนวอาคารทำมุม 45° กับถนน)

### Behavior spec

| State | Constrain |
|---|---|
| ไม่กด Shift, `orthoMode=false` | ฟรี (ไม่ล็อก) |
| กด Shift หรือ `orthoMode=true` | ล็อก 8 ทิศ (0°/45°/90°/135°/180°/225°/270°/315°) — **เปลี่ยนจาก 2 ทิศเดิม** |
| กด Shift+Alt (option) | ล็อก 2 ทิศเดิม (0°/90° เท่านั้น) — backwards compat สำหรับ user เก่า |

### Implementation

**`proto/ui.html` — แก้ฟังก์ชั่น constrain (มี 2 จุด: mousedown line 1288 และ mousemove line 1319):**

เดิม:
```javascript
if((shiftDown||orthoMode)&&mPts.length>0&&["dist","path","ref","area"].includes(mode)){
  const last=mPts[mPts.length-1];
  const lastC=pdfToC(last.x,last.y);
  const sdx=sc.x-lastC.x,sdy=sc.y-lastC.y;
  if(Math.abs(sdx)>=Math.abs(sdy))sc.y=lastC.y;     // ล็อก 0° (แนวนอน)
  else sc.x=lastC.x;                                 // ล็อก 90° (แนวตั้ง)
}
```

ใหม่:
```javascript
function constrainTo8Directions(lastC, sc, only4=false){
  const dx=sc.x-lastC.x, dy=sc.y-lastC.y;
  const len=Math.hypot(dx,dy);
  if(len<0.001) return sc;
  const ang=Math.atan2(dy,dx);
  const step=only4 ? (Math.PI/2) : (Math.PI/4);  // 4 ทิศ (0/90) vs 8 ทิศ (0/45/90/135)
  const snappedAng=Math.round(ang/step)*step;
  return {
    x: lastC.x + Math.cos(snappedAng)*len,
    y: lastC.y + Math.sin(snappedAng)*len,
    t: sc.t
  };
}

// ที่จุด constrain (mousedown + mousemove):
if((shiftDown||orthoMode)&&mPts.length>0&&["dist","path","ref","area"].includes(mode)){
  const last=mPts[mPts.length-1];
  const lastC=pdfToC(last.x,last.y);
  const only4 = altDown;  // กด Alt = ล็อก 2 ทิศ (เดิม)
  const c=constrainTo8Directions(lastC, sc, only4);
  sc.x=c.x; sc.y=c.y;
}
```

**State variable:** เพิ่ม `let altDown=false;` ใกล้บรรทัด `shiftDown` (line 400).

**Event listener:** ใน keydown/keyup ที่มีอยู่แล้ว เพิ่ม:
```javascript
if(e.key==="Alt"||e.altKey){altDown=true; redraw();}
// และใน keyup:
if(e.key==="Alt"){altDown=false; redraw();}
```

**UI hint:** เพิ่ม status เมื่อ orthoMode toggle:
- เดิม: "⊖ ตั้งฉากเสมอ: เปิด — วาดล็อก 0°/90° ตลอด"
- ใหม่: "⊖ ตั้งฉากเสมอ: เปิด — ล็อก 0°/45°/90° (กด Alt = แค่ 0°/90°)"

**Tooltip on ortho button:** update title attribute

**Guide line render (line 1170-ish ใน redraw):** ตอนนี้วาดเส้น crosshair แนวนอน/แนวตั้งจาก lastPoint เมื่อ shift/ortho on → เปลี่ยนเป็นวาด 8 รังสีจาก lastPoint:
```javascript
if((shiftDown||orthoMode)&&mPts.length>0&&["dist","path","ref","area"].includes(mode)){
  const last=mPts[mPts.length-1];
  const lastC=pdfToC(last.x,last.y);
  ctx.save();
  ctx.strokeStyle="rgba(100,200,255,0.25)";
  ctx.lineWidth=1/zoom;
  ctx.setLineDash([6/zoom,4/zoom]);
  const dirs = altDown ? 4 : 8;  // 4 ทิศ (เดิม) vs 8 ทิศ (ใหม่)
  const step = (Math.PI*2)/dirs;
  const maxR = Math.max(canvas.width, canvas.height) * 1.5;
  for(let i=0;i<dirs;i++){
    const a=i*step;
    ctx.beginPath();
    ctx.moveTo(lastC.x, lastC.y);
    ctx.lineTo(lastC.x+Math.cos(a)*maxR, lastC.y+Math.sin(a)*maxR);
    ctx.stroke();
  }
  ctx.restore();
}
```

### E2E test (เพิ่มใน `_test_menu_power_up()` หรือ `_test_main_measurement_ui_cleanup()`):

```javascript
angleLock45Works: (() => {
  // simulate: lastPoint = {x:0,y:0}, cursor at angle ~50° (sin/cos)
  // expected: snapped to 45° exactly
  const lastC = {x:0, y:0};
  const sc = {x:100, y:120, t:null};  // angle ~50°
  // shift+ortho should snap to 45° (x=y)
  // ใช้ function ใหม่ constrainTo8Directions
  const c = constrainTo8Directions(lastC, sc);
  // length ~= 156.2, snap to 45° → x=110.5, y=110.5
  return Math.abs(c.x - c.y) < 0.5;
})(),
angleLock90WhenAlt: (() => {
  // simulate: same input but with alt → snap to 90° (x=lastC.x)
  const lastC = {x:0, y:0};
  const sc = {x:100, y:120, t:null};
  const c = constrainTo8Directions(lastC, sc, true);
  // angle ~50° rounded to 90° → x=0, y=156.2
  return Math.abs(c.x) < 0.5;
})()
```

### Risk

- **Low** — เป็น additive change ใน constrain logic เดิม
- ฟังก์ชั่น `constrainTo8Directions` แยกออกมาเป็น utility — testable
- Backward compat: Shift+Alt = ของเดิม 0°/90° เท่านั้น
- **Documentation needed**: บอก user ว่ามี hotkey Alt สำหรับ legacy mode

---

## Phase H.1 — Curves + Circle + Ellipse + Rectangle

### Goal

เพิ่มเครื่องมือวาดเส้นโค้งและรูปทรงพื้นฐาน:

| Tool | Hotkey | Output |
|---|---|---|
| ⭕ Circle | `Shift+C` | center + radius → polygon ตัวประมาณ 32 vertex (สำหรับ render/hit-test) + meta `{shape:"circle", center, radius}` |
| ⬭ Ellipse | `Shift+E` | center + 2 axes → polygon 32 vertex + meta `{shape:"ellipse", center, a, b, rotation}` |
| ⌒ Arc Edge | `Shift+A` (toggle ขณะวาด area) | next polygon segment เก็บ `edgeType:"arc", arcRadius, arcSweep` |
| □ Quick Rectangle | `Shift+R` | 2 จุด → 4-vertex polygon |

### Area math (เพิ่ม **ใหม่** ใน ui.html ตำแหน่งใกล้ `polyAreaM2`):

```javascript
function circleAreaM2(center, radius_pt, pg=curPage){
  const scale=getScaleForPage(pg);
  if(!scale) return null;
  const r_m = radius_pt / scale.pts_per_m;
  return Math.PI * r_m * r_m;
}

function ellipseAreaM2(center, a_pt, b_pt, pg=curPage){
  const scale=getScaleForPage(pg);
  if(!scale) return null;
  const a_m = a_pt / scale.pts_per_m;
  const b_m = b_pt / scale.pts_per_m;
  return Math.PI * a_m * b_m;
}

function arcSegmentArea(chord_pt, sweepRad, pg=curPage){
  // พื้นที่ของส่วนเสริม (segment area) เพิ่ม/ลดจาก polygon ที่ใช้ chord
  const scale=getScaleForPage(pg);
  if(!scale || Math.abs(sweepRad)<0.001) return 0;
  const chord_m = chord_pt / scale.pts_per_m;
  const r_m = chord_m / (2*Math.sin(Math.abs(sweepRad)/2));
  // segment area = r² (θ - sin θ) / 2  (θ in rad)
  const segArea = (r_m*r_m * (Math.abs(sweepRad) - Math.sin(Math.abs(sweepRad)))) / 2;
  return sweepRad > 0 ? segArea : -segArea;  // sweep negative = หักออก
}

function polygonAreaWithArcs(poly, pg=curPage){
  // 1) base polygon area จาก polyAreaM2 (ไม่แตะ)
  let base = polyAreaM2(poly.pts, pg);
  if(base==null) return null;
  // 2) บวก/ลบ arc segment ของแต่ละ edge ที่ edgeType=="arc"
  for(let i=0;i<poly.pts.length;i++){
    const j=(i+1)%poly.pts.length;
    const edge=poly.edges?.[i];
    if(edge?.edgeType==="arc" && edge.arcSweep){
      const chord = Math.hypot(poly.pts[j].x-poly.pts[i].x, poly.pts[j].y-poly.pts[i].y);
      base += arcSegmentArea(chord, edge.arcSweep, pg);
    }
  }
  return base;
}
```

### Schema additions (backward compat — optional fields)

**Polygon object:** เพิ่ม optional fields
```javascript
{
  pts: [{x, y}, ...],           // เดิม
  closed: true,                  // เดิม
  // ใหม่ (optional):
  shape: "polygon" | "circle" | "ellipse",  // default "polygon"
  center: {x, y},                            // circle/ellipse
  radius: pt,                                // circle
  semiAxisA: pt, semiAxisB: pt,              // ellipse
  rotation: rad,                              // ellipse
  edges: [{edgeType:"line"|"arc", arcRadius:pt, arcSweep:rad}]  // per-vertex edge meta
}
```

**`polyMetrics()` ไม่แก้** — แต่เพิ่ม wrapper:
```javascript
function objectArea(obj, pg=curPage){
  if(obj.shape==="circle") return circleAreaM2(obj.center, obj.radius, pg);
  if(obj.shape==="ellipse") return ellipseAreaM2(obj.center, obj.semiAxisA, obj.semiAxisB, pg);
  if(obj.edges?.some(e=>e.edgeType==="arc")) return polygonAreaWithArcs(obj, pg);
  return polyAreaM2(obj.pts, pg);  // fallback เดิม
}
```

### Render

**`redraw()` extension:** หลัง `mPolys.forEach(...)` block:
```javascript
// Render circle/ellipse แทน polygon-32-vertex (smoother)
mPolys.forEach((poly,pi)=>{
  if(poly.shape==="circle"){
    const cC = pdfToC(poly.center.x, poly.center.y);
    const r = poly.radius * (Math.hypot(pdfToC(1,0).x-pdfToC(0,0).x, 0));  // scale to canvas
    ctx.beginPath();
    ctx.arc(cC.x, cC.y, r, 0, Math.PI*2);
    ctx.strokeStyle=poly.color||"#30d158";
    ctx.lineWidth=lw;
    ctx.stroke();
  }
  // ellipse: ctx.ellipse(...)
  // arc edges: ใช้ ctx.arcTo() ระหว่าง vertex
});
```

### Hit-test

- Circle: distance from center vs radius (with snap radius tolerance)
- Ellipse: parametric distance check
- Arc edge: nearest point on arc

### Menu integration

ใน Measure dropdown (สร้างใน Phase G แล้ว) เพิ่ม items:
- ⭕ Circle Tool — Shift+C
- ⬭ Ellipse Tool — Shift+E
- ⌒ Toggle Arc Edge — Shift+A (active เฉพาะตอน mode=area, mPts.length>=1)
- □ Quick Rectangle — Shift+R

### E2E tests (เพิ่มใน `_test_menu_power_up`)

```javascript
circleAreaCalculates: (() => {
  const a = circleAreaM2({x:0,y:0}, 100, curPage);  // r=100pt
  // ที่ scale ปัจจุบัน ของ test_plan_A1.pdf
  return typeof a === "number" && a > 0;
})(),
ellipseAreaCalculates: (() => {
  const a = ellipseAreaM2({x:0,y:0}, 100, 50, curPage);
  return typeof a === "number" && a > 0;
})(),
quickRectangleCreatesPolygon: (() => {
  // simulate 2-click rectangle workflow
  // expect: mPolys.length increments by 1, last poly has 4 vertices
}),
arcEdgeToggleWorks: (() => {
  // ตรวจ Shift+A toggle ตอนวาด area
})
```

### Risk

- **Medium** — area math + render + hit-test ใหม่
- **Mitigation**: ทำใน function แยก (`circleAreaM2`, etc.) ไม่แตะ `polyAreaM2`
- **Backward compat**: polygon เก่าที่ไม่มี `shape` field default = "polygon" → ใช้ `polyAreaM2` เดิม

---

## Phase H.2 — Annotate Menu (Item 14)

### Goal

เพิ่ม menu item ที่ 14 ใน menu bar ระหว่าง "Layer" และ "Review" (**ไม่ rename Workspace**)

Mockup ระบุ Annotate menu มี 8 items:

| Item | Action |
|---|---|
| 💬 Comment | คลิกวางจุด comment + textarea popup |
| 🖍 Highlight | drag-region → ใส่สี semi-transparent overlay |
| ▭ Rectangle Frame | 2 corners → rectangle annotation |
| ◯ Circle Frame | center + radius → circle annotation |
| ☁ Cloud Frame | polygon-like → SVG cloud path render |
| ➜ Arrow Pointer | 2 points (tail→head) → arrow annotation |
| 𝕋 Free Text Label | คลิกวาง text บนตำแหน่งใดก็ได้ |
| 🗑 Clear Annotations | ลบ annotations ทั้งหน้า (มี confirmation) |

### Schema additive

```javascript
// ใน pageStore[pg] (backward compat — เพิ่ม field ใหม่)
pageStore[pg].annotations = [
  {
    id: "ann_" + uuid,
    type: "comment" | "highlight" | "rect_frame" | "circle_frame" | "cloud_frame" | "arrow" | "text",
    pts: [{x,y}, ...],         // type-specific
    text: "string",            // comment / text
    color: "#hex",
    opacity: 0.5,
    fontSize: 12,              // text only
    rotation: 0,               // text/arrow
    createdAt: "ISO date"
  }
]
```

**Old `.bmaplan` files without `annotations`:** load empty array (backward compat in `applyLoadedProject`).

### Render

ใหม่ `drawAnnotations()` ใน `redraw()` หลัง overlay ของ polys/openings (annotations อยู่ on top):
```javascript
function drawAnnotations(){
  const anns = (getStore(curPage).annotations) || [];
  anns.forEach(ann => {
    switch(ann.type){
      case "comment": drawCommentMarker(ann); break;
      case "highlight": drawHighlightRegion(ann); break;
      case "rect_frame": drawRectFrame(ann); break;
      case "circle_frame": drawCircleFrame(ann); break;
      case "cloud_frame": drawCloudFrame(ann); break;
      case "arrow": drawArrow(ann); break;
      case "text": drawTextLabel(ann); break;
    }
  });
}
```

### Modes (เพิ่มใน `setMode`)

- `"ann_comment"`, `"ann_highlight"`, `"ann_rect"`, `"ann_circle"`, `"ann_cloud"`, `"ann_arrow"`, `"ann_text"`
- Click handler ใน mousedown มี case สำหรับแต่ละ mode

### Export integration

- **XLSX:** เพิ่ม sheet "Annotations" — columns: page, type, text, color, position
- **PDF (annotated export):** include annotations layer in `exportCurrentPageAnnotatedPDF()` / `exportAllPagesAnnotatedPDF()`
  - แก้ที่ `proto/server.py`? **NO** — server ห้ามแตะ
  - ใช้ canvas → PNG → PDF approach (เดิมก็ render ผ่าน canvas อยู่แล้ว) → annotation จะ include อัตโนมัติ

### Menu bar overflow risk

ปัจจุบัน menu bar มี 13 items + app-logo + phase-badge

- Viewport ≥ 1280px: ใส่ 14 items ได้ (ทดสอบใน mockup)
- Viewport < 1280px: ตรวจว่า menu bar overflow ไม่ตัดท้าย — อาจต้อง responsive

**Mitigation:** ใน `@media (max-width: 1280px)` ลด font-size ของ menu-item เป็น 11px, ลด padding

### Files to modify

| File | Changes |
|---|---|
| `proto/ui.html` | + menu-item 14 ("Annotate") + 8 dd-items, + 7 new mode handlers, + drawAnnotations() + 7 draw helpers, + Annotate popup form, + applyLoadedProject backward compat |
| `proto/static/css/app.css` | + .annotation-* render styles (cloud SVG path, arrow head, text label background), + responsive menu-bar at <1280px |
| `proto/e2e_ui_test.py` | + `_test_annotations()` (8 assertions for each annotation type create + render + persist) |

### E2E tests

```javascript
annotateMenuExists: !!document.querySelector(".menu-item[data-menu='annotate']"),
annotateMenuHasEightItems: document.querySelectorAll(".menu-item[data-menu='annotate'] .dd-item").length === 8,
commentAnnotationCreates: (() => {
  setMode("ann_comment");
  // simulate canvas click + text input
  // expect: pageStore[curPage].annotations.length === 1, type==="comment"
}),
annotationsPersistAfterReload: (() => {
  // create annotation, save .bmaplan, reload, expect array preserved
}),
annotationsAppearInXLSXSheet: (() => {
  // export XLSX, expect sheet "Annotations" exists with rows
}),
clearAnnotationsButton: (() => {
  // click 🗑 Clear → expect annotations array emptied with confirmation
})
```

### Risk

- **Medium-high** — touches multiple subsystems: render, save/load, export, mode handling
- **Mitigation 1:** annotations เป็น additive field, ไม่กระทบ measurement objects
- **Mitigation 2:** XLSX sheet "Annotations" แยกออก ไม่กระทบ sheet "สรุปพื้นที่"
- **Mitigation 3:** PDF annotation มาฟรีจาก canvas render — ไม่ต้องแก้ server

---

## Phase H.3 — Deferred to next sprint

H.3 (File / Edit / View / Review / Export / Workspace / Help dropdowns) — **ไม่ทำใน sprint นี้** เพราะ scope ใหญ่และ critical workflow ไม่ depend on them ตอนนี้

---

## Critical files (สรุป)

| File | Phase H.0 | Phase H.1 | Phase H.2 |
|---|---|---|---|
| `proto/ui.html` | ~30 lines (constrain function + state + guide render) | ~250 lines (Circle/Ellipse/Arc/Rect tools + objectArea wrapper + render + hit-test) | ~400 lines (Annotate menu items + 7 mode handlers + drawAnnotations + 7 draw helpers + popup form) |
| `proto/static/css/app.css` | 0 | ~20 lines (cursor + tool button highlight) | ~60 lines (annotation styles + responsive menu-bar) |
| `proto/e2e_ui_test.py` | 2 assertions | 4-5 assertions | 8 assertions |

**Total estimate:** 30 + 250 + 400 = ~680 lines เพิ่ม + tests

---

## Reused Functions (ไม่แตะ)

| Function | Purpose |
|---|---|
| `polyMetrics(poly, pg)` | Polygon area (เดิม) |
| `polyAreaM2(pts, pg)` | Raw polygon area math |
| `polySelfIntersects(pts)` | Self-intersection check |
| `pdfToC`, `cToPdf` | Coordinate conversion |
| `getScaleForPage(pg)` | Scale lookup |
| `setMode(m)` | Mode switching |
| `saveProject`, `applyLoadedProject` | Save/load .bmaplan (ใส่ backward compat สำหรับ annotations array) |
| `redraw()` | Canvas redraw (extension only) |
| `pushUndo`, `undo`, `redo` | Undo/redo |
| `toggleMenu`, `closeAllMenus` | Menu dropdown (Phase G) |

---

## Verification (End-to-end Test Plan)

### Phase H.0 (45° lock)
1. `python -m py_compile proto/server.py proto/e2e_ui_test.py` → PASS
2. `python proto/e2e_ui_test.py smoke` → PASS + new markers `angleLock45Works`, `angleLock90WhenAlt`
3. Manual: เปิด PDF, set scale, mode=area, click 1 จุด, hold Shift, move mouse → guide line วาดเป็น 8 รังสี (ไม่ใช่ 2 รังสี), cursor snap ที่ 0/45/90/135/180/225/270/315°
4. Manual: hold Shift+Alt → snap ที่ 0/90° เท่านั้น

### Phase H.1 (Curves)
1. `python proto/e2e_ui_test.py smoke` → PASS + `circleAreaCalculates`, `ellipseAreaCalculates`, `quickRectangleCreatesPolygon`, `arcEdgeToggleWorks`
2. Manual: วาด circle 5m radius → ตรวจ area = π·25 ≈ 78.54 ตร.ม.
3. Manual: วาด rectangle 5m × 4m → area = 20.0 ตร.ม.
4. Manual: วาด polygon ด้วย arc edges → area คำนวณรวม arc segments
5. Manual: save .bmaplan → reload → circle/ellipse/arc วาดกลับมาเหมือนเดิม
6. `python proto/e2e_ui_test.py full` → measurement results เดิมไม่เปลี่ยน (regression check)

### Phase H.2 (Annotate)
1. `python proto/e2e_ui_test.py smoke` → PASS + `_test_annotations()` markers
2. Manual: คลิก Annotate menu → 8 dd-items, click "Comment" → mode=ann_comment, คลิก canvas → popup
3. Manual: สร้าง 1 ของแต่ละ annotation type → ทั้งหมด render ถูก z-order on top of polygons
4. Manual: save .bmaplan → reload → annotations persist
5. Manual: Export XLSX → sheet "Annotations" exists with correct rows
6. Manual: Export Current Page + Annotations → PDF includes both polygons + annotations
7. Viewport test: 1280px และ 1024px — menu bar ไม่ overflow viewport
8. Regression: VECTOR_OK, RECAL_OK, XLSX_OK, PROJECT_OK ค่าเท่าเดิม

---

## Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| 45° lock เปลี่ยน behavior ของ user เก่า | Low | Shift+Alt = legacy 0°/90° |
| Circle/Ellipse area math ผิด | Medium | ทำใน function แยก, unit test ผ่าน reference values (π×r²) |
| Arc segment area คำนวณผิด → polygon area เพี้ยน | Medium | Backward compat: ถ้าไม่มี `edgeType:"arc"` ใช้ `polyAreaM2` เดิม |
| `applyLoadedProject` ไม่ handle annotations field ที่ขาดในไฟล์เก่า | High | `pageStore[pg].annotations = pageStore[pg].annotations || []` |
| XLSX export `Annotations` sheet หาย → PROJECT_OK fail | High | เพิ่ม sheet แบบ optional — ไม่มี annotation = sheet empty (ไม่ throw) |
| Menu bar 14 items overflow ที่ viewport < 1280px | Medium | Responsive `@media` rule + scrollable menu fallback |
| `setMode` ใหม่ 7 ตัว conflict กับ existing modes | Low | Prefix `ann_*` ทั้งหมด — unique namespace |

---

## Implementation Order (recommended)

1. **Branch:** `git checkout -b feature/phase-h-curves-annotate` จาก `feature/mockup-v3-alignment` (หรือ main ถ้า merge แล้ว)
2. **Phase H.0** (45° lock) — เล็กที่สุด, ทดสอบเร็ว → commit + smoke
3. **Phase H.1** step 1: `circleAreaM2`, `ellipseAreaM2`, `arcSegmentArea`, `objectArea` wrapper → smoke pass
4. **Phase H.1** step 2: Circle/Ellipse tool (no arc/rect yet) → smoke + manual
5. **Phase H.1** step 3: Quick Rectangle + Arc Edge → smoke + full
6. **Phase H.2** step 1: Annotate menu DOM + closed mode handlers → smoke
7. **Phase H.2** step 2: drawAnnotations + per-type draw helpers → smoke + manual
8. **Phase H.2** step 3: save/load backward compat + XLSX sheet + PDF render → smoke + full
9. **Phase F-equivalent** docs: PATCH_SUMMARY, TEST_RESULT, UI_MANUAL_TEST, FINAL_REPORT, CURRENT_STATUS, log.md

**Each step ต้อง:** smoke pass, no measurement regression, commit แยก

---

## Stop conditions (ห้าม PASS ถ้าเจอ)

- Existing polygon area math เปลี่ยน (regression on VECTOR_OK, XLSX_OK, PERSIST_OK, REAL_OK)
- Save / load .bmaplan ของไฟล์เก่าเสีย
- Existing Shift/orthoMode 0°/90° lock พังเมื่อกด Shift+Alt
- Menu bar overflow viewport ที่ 1280px
- Annotations ทำให้ measurement objects หายไป (z-order ผิด)
- Export XLSX sheet เดิมหายหรือ rows เปลี่ยน
- PDF annotated export ตำแหน่ง annotation ไม่ตรงกับ canvas

---

## Notes from user (2026-05-12)

> "ตอนนี้มี ล็อกมุม 0 และ 90 ควรมีมุม 45 ด้วย เพื่อวัด 2h ของความกว้างถนน"

ตีความ:
- "2h" = ระยะร่นจากเขตที่ดิน = `2 × ความสูงอาคาร` ตามกฎควบคุมอาคาร — มักวัดเส้นทแยงมุม 45° จากแนวเขตที่ดิน
- หรือ "2h" = double-h = ความสูง 2 เท่า ที่วัดเฉียง = `h × √2` ในกรณีมุม 45°
- ทั้งสองกรณี → ต้องการ angle lock 45° **เพื่อให้วัดได้แม่นยำขณะวาด distance / path / ref**

Phase H.0 ครอบคลุมเคสนี้ครับ — ใส่เป็น **prerequisite ก่อน H.1/H.2** เพราะเล็กและทำเร็ว
