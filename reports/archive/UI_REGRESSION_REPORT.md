# รายงานตรวจสอบ UI ใหม่เทียบเวอร์ชันก่อนหน้า

อัปเดต: 2026-04-25

## สรุปผู้บริหาร

ผลตรวจยืนยันว่า feedback ที่ว่า UI ใหม่สู้ UI เดิมไม่ได้มีมูลจากโค้ดจริง โดยเฉพาะส่วน interaction หลักของงานวัดแบบ:

- UI ใหม่ไม่มี mouse wheel zoom
- UI ใหม่มีปุ่ม `IX` และ `⊥` แต่ logic snap ไม่ทำงานครบ
- UI ใหม่ใช้ snap radius เป็นค่าคงที่ใน canvas ทำให้ความรู้สึก snap เปลี่ยนตาม zoom
- Opening mode มีปุ่ม แต่ logic ปัจจุบันยังผูกกับ `perpMode` ผิดตัว
- Backend ปัจจุบันดีกว่าเวอร์ชัน commit เก่ามาก เพราะมี `case_id`, PDFium, upload guard และ degraded mode แล้ว

ข้อเสนอหลัก: ไม่ควรถอยกลับทั้งระบบไป commit เก่า ให้เอา interaction/UI behavior จาก `server.py.bak` กลับมาเป็นฐาน แล้วคง backend ปัจจุบันใน `server.py` ไว้

## ไฟล์/เวอร์ชันที่ตรวจ

| แหล่ง | สถานะ | หมายเหตุ |
|---|---|---|
| `proto/ui.html` | UI ใหม่ที่รันอยู่ | แยกออกจาก `server.py`, ขนาดเล็กกว่า แต่ตัด interaction สำคัญออก |
| `proto/server.py` | Backend ปัจจุบัน | ใช้ FastAPI + PyMuPDF + PDFium + `CASES[case_id]` |
| `proto/server.py.bak` | UI เดิม/backup ล่าสุด | มี wheel zoom, IX snap, perpendicular snap, UI เดิมสมบูรณ์กว่า |
| `git HEAD:server.py` | commit ก่อนหน้า | มี wheel zoom แต่ backend เก่ากว่า ใช้ global `SESSION` |

## ปัญหาใน UI ใหม่

### 1. ไม่มี mouse wheel zoom

ใน `proto/ui.html` ไม่มี `ws.addEventListener("wheel", ...)`

ผลกระทบ:

- ใช้ scroll mouse ซูมเข้าออกไม่ได้
- workflow วัดแบบ A1 ช้าลงมาก
- ผู้ใช้ต้องกดปุ่ม `+`/`-` แทน ซึ่งไม่เหมาะกับงาน inspect แบบละเอียด

เวอร์ชันก่อนหน้าใน `server.py.bak` มี logic นี้:

```javascript
ws.addEventListener("wheel", e => {
  e.preventDefault();
  const r = ws.getBoundingClientRect(), fx = e.clientX - r.left, fy = e.clientY - r.top;
  const dz = e.deltaY > 0 ? 0.85 : 1.18;
  const nz = Math.max(0.08, Math.min(8, zoom * dz));
  panX = fx - (fx - panX) * (nz / zoom);
  panY = fy - (fy - panY) * (nz / zoom);
  zoom = nz;
  applyT();
}, { passive: false });
```

### 2. Zoom ด้วยปุ่มไม่ดีเท่าเดิม

`adjustZoom()` ใน UI ใหม่ซูมจากกึ่งกลาง workspace เท่านั้น ไม่ใช่ตำแหน่งเมาส์

ผลกระทบ:

- ซูมแล้วตำแหน่งที่กำลัง inspect หลุดจากสายตา
- งานวัดต้อง pan กลับซ้ำ
- ความรู้สึกใช้งานด้อยกว่า PDF viewer มาตรฐาน

### 3. Snap radius ไม่ scale ตาม zoom

UI ใหม่:

```javascript
const R = snapRadius;
```

UI เดิม:

```javascript
const R = snapRadius / zoom;
```

ผลกระทบ:

- ตอนซูมเข้า snap radius บนหน้าจอใหญ่เกินไป
- ตอนซูมออก snap radius เล็ก/จับยาก
- ความแม่นในการเลือก endpoint/line ไม่คงที่

### 4. Close polygon radius ไม่ scale ตาม zoom

UI ใหม่ใช้ `closeRadius` แบบคงที่ใน canvas coordinate

UI เดิมใช้แนวทาง `closeRadius / zoom`

ผลกระทบ:

- ปิด polygon ยาก/ง่ายผิดปกติตามระดับ zoom
- ทำให้การวาดพื้นที่ไม่ predictable

### 5. ปุ่ม IX มี แต่ snap intersection ไม่ทำงาน

ใน UI ใหม่มี state และปุ่ม `IX`:

```javascript
snapModes = { ep:true, mp:true, ct:true, nl:false, ix:false, off:false }
```

แต่ `snap()` ใน `ui.html` ทำงานแค่:

- EP
- MP
- CT
- NL

ไม่มี block คำนวณ intersection line pairs แบบ UI เดิม

ผลกระทบ:

- ปุ่ม `IX` หลอกผู้ใช้ว่ามี feature
- วัดจุดตัดเส้นแบบก่อสร้างไม่ได้ตามที่ UI แสดง

### 6. ปุ่ม Perpendicular Snap มี แต่ logic ถูกตัดออก

UI ใหม่มี `togglePerp()` และ `perpMode` แต่ `snap()` ไม่มี Tier PERP แล้ว

เวอร์ชัน `server.py.bak` มี logic:

- หาเส้นใกล้เมาส์
- project จุดตั้งฉากจากจุดล่าสุดไปยัง segment
- return snap type `perp`

ผลกระทบ:

- ปุ่ม `⊥` เปิดได้ แต่ไม่ช่วย snap ตั้งฉากจริง
- งานวัดระยะร่น/ระยะตั้งฉากเสียความเร็วและความแม่น

### 7. Opening mode ผูก state ผิด

ปัจจุบัน `toggleOpening()` แค่ toggle class ของปุ่ม แต่ตอนปิด polygon ใช้เงื่อนไขนี้:

```javascript
if (perpMode) {
  // create opening
}
```

ผลคือการสร้าง opening ไปผูกกับ `perpMode` แทนที่จะมี `openingMode`

ผลกระทบ:

- กดปุ่ม `ช่องว่าง` แล้วอาจไม่สร้าง opening ตามที่ผู้ใช้คาด
- กด `⊥` อาจทำให้สร้าง opening ผิดประเภท
- summary และ XLSX อาจหักพื้นที่ผิด workflow

หมายเหตุ: `server.py.bak` ก็มี pattern นี้อยู่ จึงเป็น bug ที่ต้องแก้เมื่อนำ UI เดิมกลับมาใช้ด้วย

### 8. UI ใหม่ compact เกินไปสำหรับงานตรวจแบบ

UI ใหม่ลดข้อความบนปุ่มและย้ายหลายอย่างไปเป็น icon/แถบ compact

ผลกระทบ:

- discoverability ต่ำลง
- ผู้ใช้ไม่รู้ว่าแต่ละ tool ทำอะไร
- งานแบบวิศวกรรมต้องการ toolbar ที่อ่านเร็ว ไม่ใช่ icon-only เยอะเกินไป

## ปัญหาของเวอร์ชัน commit ก่อนหน้า

ถ้าจะถอยกลับไป commit เก่าโดยตรง จะเจอปัญหา backend เหล่านี้:

| ปัญหา | ผลกระทบ |
|---|---|
| ใช้ global `SESSION` | ผู้ใช้/ไฟล์ PDF หลายชุดชนกันได้ |
| `/upload` อ่านไฟล์ทั้งก้อนเข้า memory | PDF ใหญ่เสี่ยงกิน RAM |
| ไม่มี size cap / invalid PDF / encrypted PDF guard ครบ | error handling ไม่ปลอดภัย |
| ไม่มี `case_id` ใน endpoint | stale response และ multi-case workflow เสี่ยงพัง |
| ใช้ PyMuPDF `get_drawings()` เป็นหลัก | snap engine ช้าหรือไม่ครบเท่า PDFium |
| ไม่มี degraded raster mode ชัดเจน | ผู้ใช้ไม่รู้ว่าหน้านั้นวัดได้แค่ manual |

ดังนั้นไม่ควร revert ไป commit เก่าทั้งก้อน

## จุดแข็งของ backend ปัจจุบันที่ควรรักษา

- `CASES[case_id]` แยก PDF ต่อเคส
- TTL cleanup สำหรับเคสเก่า
- upload guard: ขนาดไฟล์, empty file, invalid PDF, encrypted PDF
- `/page`, `/thumb`, `/thumb-md`, `/analyse` ตรวจ page bounds
- ใช้ PDFium เป็น vector snap engine
- fallback ไป PyMuPDF เมื่อ PDFium ไม่เจอ vector
- ส่ง `degraded_mode` และ `warning`
- export PDF + annotations รองรับ rotation

## แนวทางแก้ที่แนะนำ

### ทางเลือกที่ 1: ซ่อม UI ใหม่เฉพาะจุด

งานที่ต้องทำ:

1. เพิ่ม `wheel` handler กลับเข้า `ui.html`
2. เปลี่ยน snap radius เป็น `snapRadius / zoom`
3. เปลี่ยน close radius เป็น `closeRadius / zoom`
4. เพิ่ม IX snap block กลับจาก `server.py.bak`
5. เพิ่ม PERP snap block และ `perpFoot()`
6. แยก `openingMode` ออกจาก `perpMode`
7. ทดสอบ manual กับ real permit PDF

ข้อดี:

- แตะไฟล์น้อย
- รักษาโครงสร้างแยก `server.py` / `ui.html`

ข้อเสีย:

- UI ใหม่ยัง compact และใช้งานไม่คุ้นมือ
- อาจยังมี regression ย่อยที่ยังไม่เจอ

### ทางเลือกที่ 2: เอา UI เดิมจาก `server.py.bak` กลับมาเป็นฐาน

งานที่ต้องทำ:

1. ดึง HTML/JS เดิมจาก `server.py.bak` มาเป็น `ui.html`
2. คง backend ปัจจุบันใน `server.py`
3. แก้ opening mode ให้มี `openingMode` จริง
4. ตรวจทุก endpoint ให้ใช้ `case_id`
5. เพิ่ม `xlsxwriter` ใน `requirements.txt`
6. รัน smoke/full E2E

ข้อดี:

- ได้ UX เดิมที่ผู้ใช้บอกว่าดีกว่า
- wheel zoom, IX, PERP มี logic อยู่แล้ว
- ลดความเสี่ยงเรื่อง interaction ที่หาย

ข้อเสีย:

- ต้องจัดระเบียบ HTML/JS ก้อนใหญ่
- ต้องแก้ bug opening mode ที่ติดมากับ backup

## Recommendation

แนะนำเลือกทางเลือกที่ 2:

> ใช้ UI เดิมจาก `server.py.bak` เป็นฐาน แล้ว keep backend ปัจจุบันไว้

เหตุผล:

- ปัญหาหลักที่ผู้ใช้เจอเป็น interaction regression ไม่ใช่ backend regression
- backend ปัจจุบันดีกว่า commit เก่าและไม่ควรถอย
- UI เดิมมี behavior งานวัดแบบที่ถูกต้องกว่า โดยเฉพาะ scroll zoom, snap radius, IX และ PERP
- การซ่อม UI ใหม่อาจใช้เวลาพอ ๆ กับย้าย UI เดิมกลับ แต่ยังไม่ได้ UX ที่ผู้ใช้พอใจ

## Acceptance Criteria สำหรับรอบแก้ถัดไป

ต้องผ่านรายการนี้ก่อนถือว่า UI กลับมาใช้งานได้:

- เปิด PDF จริง `20250616_RAMA4 APARTMENT PERMIT rev 1.pdf` ได้
- scroll mouse zoom เข้า/ออกที่ตำแหน่ง cursor ได้
- drag pan ทำงานลื่น
- Fit to window ทำงาน
- EP/MP/CT/NL/IX snap ใช้งานได้จริง
- Perpendicular snap ใช้งานได้จริง
- Opening mode สร้างช่องว่างและหักพื้นที่จริง
- เปลี่ยนหน้าแล้ว measurement ไม่หาย
- หมุนหน้าแล้ว snap/measurement/export ไม่ผิดพิกัด
- Export JSON/CSV/PDF/PDF annotations/XLSX ใช้ได้
- `python -m py_compile proto/server.py proto/e2e_ui_test.py` ผ่าน
- `python proto/e2e_ui_test.py smoke` ผ่าน
- ถ้าแตะ export/rotation/session ให้ `python proto/e2e_ui_test.py full` ผ่าน

## หมายเหตุเรื่อง repository

ตอนตรวจพบสถานะนี้ใน `proto`:

- `server.py` ถูกแก้แล้ว
- `ui.html` เป็นไฟล์ใหม่ที่ยังไม่ถูก track ใน git
- ถ้า commit/deploy โดยไม่เพิ่ม `ui.html` เว็บจะขึ้น `ui.html not found`
- `requirements.txt` ยังไม่มี `xlsxwriter` แต่ backend มี `/export-xlsx`
- `server.py` รันที่ port `8001` แต่เอกสารบางจุดยังอ้าง `8000`

## สรุปสุดท้าย

UI ใหม่ควรถูกถือเป็น regression สำหรับงานใช้งานจริงตอนนี้ โดยเฉพาะ zoom และ snap workflow

ทิศทางที่ถูกต้องคือ:

1. รักษา backend ปัจจุบัน
2. นำ interaction/UI เดิมจาก `server.py.bak` กลับมา
3. แก้ bug opening/perp แยก state
4. ทดสอบด้วย real permit PDF และ E2E ก่อนส่งให้ใช้งาน
