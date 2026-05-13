# Plan: Loupe Magnifier + Shift-constrain + Full Undo

## Context

BMA-Plan Phase 1 — UI/UX sprint สำหรับ 3 feature ที่ยังไม่มีจริงใน code:

1. **แว่นขยาย (Loupe magnifier)** — เคยระบุว่า ✅ ใน index.md แต่ไม่มีใน ui.html จริง
2. **Shift-constrain 0°/90°** — ไม่มีเลย (shiftKey ใช้แค่ใน page manager)
3. **Undo ครอบคลุมทุก tool** — undo stack มีแล้ว แต่:
   - ขณะวาดค้าง Ctrl+Z ไม่ได้ลบจุดล่าสุดออก — ไป undo อันที่ commit แล้วแทน
   - ctxColor/ctxOpacity/ctxRename/applyColor/applyOpacity ไม่ pushUndo ก่อน

## ไฟล์ที่แก้

- `proto/ui.html` (948 บรรทัด) — ไฟล์เดียวที่ต้องแก้

## ข้อมูลสถาปัตยกรรมที่สำคัญ

| สิ่งที่ต้องรู้ | รายละเอียด |
|---|---|
| Canvas | `#canvas` ใน `#cc` (CSS transform: translate+scale) |
| Zoom/Pan | `zoom`, `panX`, `panY` — CSS บน `#cc` |
| Render scale | `RS=1.5` — canvas pixel per PDF point |
| PDF↔canvas | `pdfToC(px,py)`, `cToPdf(cx,cy)`, `cXY(e)` |
| guidePoint | canvas coords — จุด rubber band |
| undo stack | `undoStack[]` max 60, `pushUndo()`, `undo()` |
| In-progress pts | `mPts[]` — จุดที่กำลังวาดแต่ยังไม่ commit |
| Mode detection | `mode` variable (pan/sel/dist/path/ref/area/calib/parking) |

---

## Feature 1: Loupe Magnifier

### HTML เพิ่ม (ก่อน `</body>`)
```html
<canvas id="loupe" style="display:none;position:fixed;border-radius:50%;
  border:2px solid #636366;box-shadow:0 4px 20px rgba(0,0,0,.8);
  pointer-events:none;z-index:9999;"></canvas>
```

### JS — state variables (เพิ่มแถว ~line 368)
```javascript
const LOUPE_R = 80;  // px radius
const loupeEl = document.getElementById("loupe");
const loupeCtx = loupeEl.getContext("2d");
loupeEl.width = LOUPE_R * 2;
loupeEl.height = LOUPE_R * 2;
loupeEl.style.width = LOUPE_R*2 + "px";
loupeEl.style.height = LOUPE_R*2 + "px";
```

### JS — `updateLoupe(e)` function (เพิ่มก่อน handleMouseMove)
```javascript
function updateLoupe(e) {
  const drawingMode = ["dist","path","ref","area","calib","parking"].includes(mode);
  if (!drawingMode || !bgImg) { loupeEl.style.display = "none"; return; }

  const {x: cx, y: cy} = cXY(e);
  // source window: ~50 screen-px worth of canvas content
  const SW = Math.max(40, Math.min(180, 60 / Math.max(zoom, 0.2)));
  const sx = cx - SW/2, sy = cy - SW/2;

  // Draw magnified canvas region
  loupeCtx.clearRect(0, 0, LOUPE_R*2, LOUPE_R*2);
  loupeCtx.save();
  loupeCtx.beginPath();
  loupeCtx.arc(LOUPE_R, LOUPE_R, LOUPE_R, 0, Math.PI*2);
  loupeCtx.clip();
  loupeCtx.drawImage(canvas, sx, sy, SW, SW, 0, 0, LOUPE_R*2, LOUPE_R*2);
  loupeCtx.restore();

  // Crosshair + snap dot
  const mag = LOUPE_R*2 / SW;
  loupeCtx.save();
  loupeCtx.strokeStyle = "rgba(255,255,255,0.7)";
  loupeCtx.lineWidth = 1;
  loupeCtx.setLineDash([3, 3]);
  loupeCtx.beginPath();
  loupeCtx.moveTo(LOUPE_R, LOUPE_R - 14); loupeCtx.lineTo(LOUPE_R, LOUPE_R + 14);
  loupeCtx.moveTo(LOUPE_R - 14, LOUPE_R); loupeCtx.lineTo(LOUPE_R + 14, LOUPE_R);
  loupeCtx.stroke();
  // Snap dot (colored per snap type)
  if (snapTarget?.t) {
    const col = SNAP_COLORS[snapTarget.t] || "#fff";
    const lx = (snapTarget.x - sx) * mag;
    const ly = (snapTarget.y - sy) * mag;
    loupeCtx.beginPath();
    loupeCtx.arc(lx, ly, 4, 0, Math.PI*2);
    loupeCtx.fillStyle = col;
    loupeCtx.fill();
  }
  loupeCtx.restore();

  // Position loupe: top-right of cursor, flip if near edges
  const wsR = ws.getBoundingClientRect();
  const scx = cx * zoom + panX + wsR.left;
  const scy = cy * zoom + panY + wsR.top;
  let lLeft = scx + 20, lTop = scy - LOUPE_R*2 - 10;
  if (lLeft + LOUPE_R*2 > window.innerWidth - 10) lLeft = scx - LOUPE_R*2 - 20;
  if (lTop < 10) lTop = scy + 20;
  loupeEl.style.left = lLeft + "px";
  loupeEl.style.top = lTop + "px";
  loupeEl.style.display = "block";
}
```

### JS — เรียก `updateLoupe` ใน `handleMouseMove` (ท้ายฟังก์ชัน ~line 829)
```javascript
// เพิ่มบรรทัดสุดท้ายของ handleMouseMove ก่อน closing }
updateLoupe(e);
```

### JS — ซ่อน loupe เมื่อ mouseleave (line 833)
เพิ่ม `loupeEl.style.display="none";` ใน mouseleave handler

### JS — ซ่อน loupe เมื่อ setMode (line 837)
เพิ่ม `loupeEl.style.display="none";` ใน `setMode()` function

---

## Feature 2: Shift-constrain 0°/90°

### State variable (เพิ่มแถว ~line 369)
```javascript
let shiftDown = false;
```

### keydown handler (line 905) — เพิ่มต้น handler
```javascript
if (e.key === "Shift") { shiftDown = true; return; }
```

### keyup handler (line 906) — เพิ่ม
```javascript
document.addEventListener("keyup", e => {
  if (e.key === " " && spaceDown) { /* existing */ }
  if (e.key === "Shift") { shiftDown = false; redraw(); }
});
```

### `handleMouseMove` — apply constrain หลัง snap (line 829)
แทรกหลัง `snapTarget = s;` และก่อน `guidePoint = ...`:
```javascript
let constrainedSnap = s;
if (shiftDown && mPts.length > 0 &&
    ["dist","path","ref","area"].includes(mode)) {
  const last = mPts[mPts.length - 1];
  const lastC = pdfToC(last.x, last.y);
  const dx = s.x - lastC.x, dy = s.y - lastC.y;
  if (Math.abs(dx) >= Math.abs(dy)) {
    constrainedSnap = { x: s.x, y: lastC.y, t: s.t };  // horizontal
  } else {
    constrainedSnap = { x: lastC.x, y: s.y, t: s.t };  // vertical
  }
}
snapTarget = constrainedSnap;
guidePoint = (mPts.length && ...) ? { x: constrainedSnap.x, y: constrainedSnap.y, t: constrainedSnap.t } : null;
```
(แก้บรรทัด `guidePoint = ...` เดิมให้ใช้ `constrainedSnap`)

### `mousedown` handler — apply constrain เมื่อวางจุด (line 804)
หลัง `const sc = snap(cx, cy);` เพิ่ม:
```javascript
if (shiftDown && mPts.length > 0 && ["dist","path","ref","area"].includes(mode)) {
  const last = mPts[mPts.length - 1];
  const lastC = pdfToC(last.x, last.y);
  const dx = sc.x - lastC.x, dy = sc.y - lastC.y;
  if (Math.abs(dx) >= Math.abs(dy)) sc.y = lastC.y;
  else sc.x = lastC.x;
}
```

### `redraw()` — visual guide เมื่อ shift constrain active
ใน `redraw()` หลัง draw snap indicators เพิ่ม:
```javascript
if (shiftDown && mPts.length > 0 && ["dist","path","ref","area"].includes(mode)) {
  const last = mPts[mPts.length - 1];
  const lastC = pdfToC(last.x, last.y);
  ctx.save();
  ctx.strokeStyle = "rgba(100,200,255,0.5)";
  ctx.lineWidth = 1/zoom;
  ctx.setLineDash([6/zoom, 4/zoom]);
  // Horizontal guide
  ctx.beginPath(); ctx.moveTo(0, lastC.y); ctx.lineTo(canvas.width, lastC.y); ctx.stroke();
  // Vertical guide
  ctx.beginPath(); ctx.moveTo(lastC.x, 0); ctx.lineTo(lastC.x, canvas.height); ctx.stroke();
  ctx.restore();
}
```

---

## Feature 3: Undo ครอบคลุมทุก tool

### 3a. Ctrl+Z ขณะวาดค้าง — ลบจุดล่าสุดก่อน
ใน `keydown` handler แก้ส่วน Ctrl+Z (line 905):
```javascript
if ((e.ctrlKey || e.metaKey) && e.key === "z") {
  e.preventDefault();
  if (mPts.length > 0) {
    // ขณะวาดอยู่: ลบจุดล่าสุด
    mPts.pop();
    if (mPts.length === 0) setStatus("ยกเลิกจุดทั้งหมด — กด Ctrl+Z อีกครั้งเพื่อ undo");
    else setStatus(`↩ ลบจุดที่ ${mPts.length + 1} — เหลือ ${mPts.length} จุด`);
    redraw();
  } else {
    undo();
  }
  return;
}
```

### 3b. pushUndo ก่อน applyColor/applyOpacity (toolbar)
เพิ่ม `mousedown` listener บน color/opacity input elements (ก่อน HTML input definitions หรือใน initTooltips):
```javascript
document.getElementById("inp-color").addEventListener("mousedown", () => {
  if (selItem) pushUndo();
});
document.getElementById("inp-opacity").addEventListener("mousedown", () => {
  if (selItem) pushUndo();
});
```

### 3c. pushUndo ใน context menu functions
เพิ่ม `pushUndo();` ที่ต้นของ:
- `ctxColor(c)` — line 808
- `ctxOpacity(v)` — line 809  
- `ctxRename()` — line 811 (ก่อน openNamePanel)

---

## Acceptance Criteria

- [ ] แว่นขยาย (loupe) ปรากฏขณะวาดในทุก mode (dist/path/ref/area/calib/parking)
- [ ] Loupe หายเมื่อ mouse ออกนอก canvas, หายเมื่อเปลี่ยนเป็น pan/sel mode
- [ ] Loupe แสดง snap dot สีตรงกับ snap type
- [ ] Shift ขณะวาด → เส้น guide สีฟ้าบาง แสดง axis ที่ lock อยู่
- [ ] จุดที่วางขณะ Shift held → snap ตาม 0° หรือ 90° จากจุดก่อน
- [ ] Ctrl+Z ขณะ mPts.length > 0 → ลบจุดล่าสุดออก (ไม่ใช่ undo committed)
- [ ] Ctrl+Z เมื่อ mPts ว่าง → undo ปกติ
- [ ] เปลี่ยนสี/opacity object ผ่าน context menu → undo กลับมาสีเดิมได้
- [ ] Rename object ผ่าน context menu → undo กลับมาชื่อเดิมได้
- [ ] เปลี่ยนสี/opacity ผ่าน toolbar (selItem) → undo กลับได้

## Tests

```bash
# Syntax check
python -m py_compile proto/server.py proto/e2e_ui_test.py

# Regression
python proto/e2e_ui_test.py smoke
```

จากนั้น manual browser test:
1. เปิด PDF → วาด polygon → ตรวจว่า loupe ปรากฏตามเมาส์
2. Shift ค้างขณะวาด → ตรวจว่าเส้น guide ปรากฏ และจุดที่วางล็อกตั้งฉาก
3. วาด polygon 3 จุด → Ctrl+Z × 3 ครั้ง → ตรวจว่าจุดหายทีละตัว
4. เลือก polygon → เปลี่ยนสีผ่าน context menu → Ctrl+Z → ตรวจว่าสีกลับมา

## log.md entry

```
[2026-05-05] — เพิ่ม Loupe magnifier, Shift-constrain 0°/90°, Undo ขณะวาดค้าง + pushUndo ก่อน ctxColor/ctxOpacity/ctxRename — [ผลทดสอบ: รอ run]
```
