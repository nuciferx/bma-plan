# BMA-Plan Progress

## สถานะ: ใช้งานได้ ✅

---

## บั๊กที่แก้ (9 รายการ)

| # | บั๊ก | ตำแหน่ง | สถานะ |
|---|------|---------|-------|
| 1 | `_rotate_snaps` 90°/270° สลับกัน | server.py:246-249 | ✅ แก้แล้ว |
| 2 | `_rotate_lines` 90°/270° สลับกัน | server.py:257-262 | ✅ แก้แล้ว |
| 3 | `openCheckPanel` ไม่ sync projectInfo | server.py:2258-2261 | ✅ เพิ่ม `syncProjectInfoFromForm()` |
| 4 | NL snap pre-filter `&&` → `\|\|` | server.py:1659 | ✅ แก้แล้ว |
| 5 | `export-pdf` ไม่แปลงพิกัดตาม rotation | server.py:421-502 | ✅ เพิ่ม `_rot_pt()` |
| 6 | `reqFrontSetback` ไม่ตรงกฎหมาย | server.py:2510-2513 | ✅ ถนน < 6m = 0 |
| 7 | ปุ่ม Opening Mode ไม่สร้าง opening จริง เพราะ logic ไปเช็ก `perpMode` | ui.html | ✅ แยก `openingMode` และเพิ่ม E2E |
| 8 | ซูมด้วยล้อเมาส์ไม่ได้ | ui.html | ✅ เพิ่ม wheel zoom ที่ workspace และล็อกด้วย E2E |
| 9 | Snap `IX`/`⊥` มีปุ่มแต่ logic ยังไม่ครบ และไม่มี preview guide line ชัดเจน | ui.html | ✅ เพิ่ม intersection/perpendicular snap + เส้น preview ตามเคอร์เซอร์ |
| 10 | Snap/ปิด polygon จับยากตอนซูมออก เพราะ radius ใช้หน่วย canvas คงที่ | ui.html | ✅ ปรับ radius ตาม zoom ให้คงที่บนหน้าจอ |
| 11 | เส้น preview ระหว่างต่อ polygon เป็นสีขาว มองไม่เห็นบนแบบบางหน้า | ui.html | ✅ ใช้สีเดียวกับสีวาดที่เลือกอยู่ |
| 12 | Snap หา geometry ด้วยการวนทั้งหน้า ทำให้ไม่ใกล้ CAD/Foxit และเสี่ยงช้าบนหน้าเส้นเยอะ | ui.html | ✅ เพิ่ม spatial grid index ฝั่ง frontend |
| 13 | Backend snap extraction หยาบและอาจลากเส้นข้าม subpath เพราะไม่ใช้ segment type | server.py | ✅ ลด dedupe grid, เพิ่ม cap, ใช้ MOVETO/LINETO/BEZIERTO, ส่ง snap metadata |
| 14 | Polygon ที่ผู้ใช้วาดเองยังไม่กลายเป็น snap source | ui.html | ✅ เพิ่ม endpoint/midpoint/nearest-line snap จาก measurement geometry |

---

## Feature ใหม่

### 1. Export XLSX
- แยกชั้น/หน้า ตามชื่อที่ตั้ง
- มีพื้นที่วัดได้ (polygon)
- มีช่องว่าง (opening) หักลบจากพื้นที่รวม
- มีความยาวเส้น polygon ทุกด้าน
- แปลงเป็นไร่-งาน-วา อัตโนมัติ

### 2. Perpendicular Snap (⊥)
- กดปุ่ม "⊥ ตั้งฉาก" เพื่อเปิด
- จุดถัดจะ snap ตั้งฉากกับเส้นใกล้ๆ อัตโนมัติ

### 3. Opening Mode (🕳)
- กดปุ่ม "🕳 ช่องว่าง" เพื่อเปิด
- วาด polygon สีแดง หักออกจากพื้นที่รวม
- ใช้หักพื้นที่ช่องเปิด หน้าต่าง ประตู

### 4. แสดงความยาวเส้น Polygon
- ทุกด้านของ polygon แสดงความยาว (ม.) กลางเส้น
- อัตโนมัติเมื่อมี scale

### 5. Page Name ใน Setup
- กรอกชื่อหน้า mis. "ชั้น 1", "ชั้น 2"
- ใช้ใน XLSX export

### 6. ช่องว่างใน Summary
- แสดง "(-)ช่องว่าง X ตร.ม." ใน infobar
- คำนวณสุทธิ รวม - ช่องว่าง

### 7. Regression Coverage เพิ่ม
- Smoke test วาด opening หลัง manual calibration
- Export XLSX แล้วตรวจ sheet หลัก + ข้อความหักช่องว่าง
- เพิ่ม `XlsxWriter` ใน `proto/requirements.txt`
- Smoke/full test ตรวจ mouse wheel zoom (`WHEEL_OK`)
- Smoke/full test ตรวจ intersection, perpendicular, close snap ตอน zoom ต่ำ, และ snap index (`SNAP_OK`)
- Smoke/full test ตรวจการคงชนิดพื้นที่, เปลี่ยนสี polygon, และเลือก/เปลี่ยนสีช่องว่าง (`SELECT_OK`)
- Smoke/full test ตรวจ user polygon snap และแนวอาคาร/ระยะร่น (`SETBACK_OK`)
- Smoke/full test ตรวจ land edge tagging เก็บ `edgeTags` กับ polygon ที่ดิน
- Smoke/full test ตรวจระยะต่อเนื่อง, เส้นอ้างอิง, parking count, และ tooltip (`EXT_MEASURE_OK`)
- UI แสดงจำนวน snap points/segments และ tooltip debug engine/grid/raw counts ที่ `Snap`

### 8. Area Selection / Type Editing
- Name panel ของพื้นที่ไม่ reset กลับเป็น "ห้อง/อาคาร" ทุกครั้ง แต่ใช้ชนิดพื้นที่ล่าสุดหรือชนิดเดิมของ polygon
- Rename polygon สามารถเปลี่ยนชนิดพื้นที่ระหว่าง "ห้อง/อาคาร" และ "ที่ดิน" ได้
- Polygon และช่องว่างที่วาดแล้วเลือกได้ในโหมดเลือก และเปลี่ยนสี/opacity ได้จาก toolbar หรือ context menu
- Context menu รองรับ rename/delete ของช่องว่าง และ Delete/Backspace อัปเดต summary หลังลบ

### 9. แนวอาคาร / ระยะร่น
- เพิ่มชนิดพื้นที่ "แนวอาคาร" ใน name panel ของ polygon
- ถ้ามี polygon ที่ดิน + polygon แนวอาคาร ระบบวาดเส้นระยะร่นอัตโนมัติจากทุกด้านของแนวอาคาร
- แต่ละด้านแสดง 3 เส้น: ปลายด้าน 2 จุด และจุดกลางด้าน 1 จุด ไปตั้งฉากกับเส้นกรอบที่ดินที่ใกล้ที่สุด
- ระยะร่นคำนวณจาก raw PDF geometry และ scale ปัจจุบัน จึง recalibrate แล้วระยะเปลี่ยนตาม
- Smoke/full test ตรวจ user polygon snap และ setback 12 เส้น (`SETBACK_OK`)

### 10. Reference / Parking / Room Usage
- เพิ่มเครื่องมือ "ระยะต่อเนื่อง" สำหรับวัดเส้นหลายจุด โดยกด Enter เพื่อจบและแสดงระยะรวม + ระยะรายช่วง
- เพิ่มเครื่องมือ "เส้นอ้างอิง" สำหรับแนวถนน แนวคลอง แนวเขตที่ดิน แนวผนัง แนวแกน และเส้นกำหนดเอง
- เส้นอ้างอิงเป็น snap source และเก็บ raw PDF geometry แยกจากเส้นวัดระยะปกติ
- เพิ่มเครื่องมือ "ที่จอด" คลิก 1 ครั้ง = 1 คัน พร้อมชนิด รถยนต์, EV, ผู้พิการ, มอเตอร์ไซค์, บริการ
- Summary ต่อหน้าแสดงจำนวนที่จอดและจำนวนเส้นอ้างอิง
- ขยาย taxonomy ของพื้นที่ห้อง/การใช้งาน: ยูนิตพักอาศัย, ห้องนอน, ทางเดิน, บันได, บันไดหนีไฟ, พื้นที่จอดรถ, บริการ, GFA, non-GFA, OSR
- เพิ่ม tooltip/title + aria-label ให้เครื่องมือหลักและ snap menu
- Export JSON/CSV รวม row ของระยะต่อเนื่อง, เส้นอ้างอิง, และที่จอดรถ
- เส้นอ้างอิงตั้งชื่อได้ และมี toggle แสดงระยะจาก object ที่เลือกไปยังเส้นอ้างอิงที่ใกล้ที่สุด
- Check panel สรุปจำนวนที่จอดรถรวมและแยกตามหน้า/ประเภท
- Export PDF annotation รองรับระยะต่อเนื่องหลายจุด, เส้นอ้างอิง, และ marker ที่จอดรถ
- Export XLSX เพิ่ม sheet "ที่จอดรถ" สำหรับสรุปจำนวน marker ตามหน้า/ประเภท
- โหมดเลือกสามารถลากแก้ vertex ของ line/ref/polygon/opening ได้ทีละจุด โดยไม่เลื่อน object ทั้งชิ้น
- Check panel เพิ่มหน้ารายงานประกอบ: รายงานที่จอดรถตามหน้า/ชั้น และรายงานระยะ object ถึงเส้นอ้างอิง
- Export JSON/CSV เพิ่ม row "ระยะถึงเส้นอ้างอิง" และ Export XLSX เพิ่ม sheet "ระยะอ้างอิง"

### 12. UX Sprint — Overlapping Picker + Layer Lock + Loupe + Ortho + Draw Bar

**Overlapping Object Picker**
- `hitTestAll()` รวบรวม hit ทุกชิ้น เรียงจาก polygon เล็กสุด → ใหญ่สุด (sub_area ก่อน base_area)
- คลิกเดียว 2+ object ซ้อนกัน → popup picker แสดง icon/ชื่อ/พื้นที่ เลือกได้ถูกตัว
- คลิกเดียว 1 object → drag ตรงไม่ผ่าน picker

**Layer Visibility + Lock**
- toggle ซ่อน/แสดง 4 layer: 🏗 หลัก (base_area) / 📐 ย่อย (sub_area) / 🕳 ช่องว่าง (deduction) / 🏷 ป้าย (labels)
- ปุ่ม 🔓/🔒 ข้างแต่ละ layer — lock = มองเห็นแต่ `hitTest`/`hitTestAll` ข้ามออบเจกต์ในเลเยอร์นั้น
- ล็อกขณะมี object ถูกเลือก → clear selection อัตโนมัติ

**Loupe Magnifier**
- ปุ่ม 🔍 แว่น toggle เปิด/ปิด (default: ปิด)
- ปุ่ม − / + ปรับขนาด 50–160px (ทีละ 20px) พร้อม label แสดงขนาด
- crosshair สีดำ (white outline 3px + black stroke 1.5px) — readable บนทุก background
- ปรากฏเฉพาะขณะวาดใน mode dist/path/ref/area/calib/parking เมื่อ loupeEnabled=true

**Shift-constrain + Orthogonal Mode**
- Shift ค้างขณะวาด → constrain 0°/90° ชั่วคราว + แสดง guide line สีฟ้า
- ปุ่ม ⊖ ตั้งฉาก → `orthoMode` toggle = constrain ตลอดโดยไม่ต้องค้าง Shift

**Draw Bar (Finish / Cancel / Undo buttons)**
- `#draw-bar` ปรากฏอัตโนมัติขณะวาดค้าง (mPts.length > 0) สำหรับ mode dist/path/ref/area
- ✓ จบ: disabled ถ้าจุดไม่พอ (path/ref < 2, area < 3) — เมื่อ enable กด = finishPathLike หรือ finishCurrentArea
- ↩ ลบจุด: pop จุดล่าสุดออกจาก mPts
- ✗ ยกเลิก: ล้าง mPts ทั้งหมด
- แสดง "N จุด" นับจุดปัจจุบัน
- `finishCurrentArea()` extracted จาก mousedown handler — ใช้ร่วมระหว่าง Draw Bar และ close-click

**Ctrl+Z per-point**
- Ctrl+Z ขณะ mPts.length > 0 → `mPts.pop()` (ลบจุดล่าสุด)
- Ctrl+Z เมื่อ mPts ว่าง → `undo()` ปกติ (undo committed object)

**ห้ามถอยหลัง:**
- Draw Bar ต้องซ่อนทันทีเมื่อ mode เปลี่ยน หรือ mPts ถูก clear
- layerLock ต้อง apply ทั้งใน hitTest และ hitTestAll
- orthoMode ต้อง apply ใน handleMouseMove, mousedown, และ redraw guide
- `updateDrawBar()` ถูก call ที่ท้าย `redraw()` ทุกครั้ง

### 11. Land Edge Tagging
- หลังวาด polygon ชนิด "ที่ดิน" ระบบเปิด panel ให้กำหนดชนิดด้านของแต่ละ edge
- คลิก edge บน canvas แล้วเลือก ด้านหน้า/ถนน, ซ้าย, ขวา, หลัง, ที่ดินข้างเคียง, คลอง/แหล่งน้ำ หรือ ไม่ใช้ตรวจ
- edge tag ถูกเก็บไว้กับ polygon ใน `edgeTags` จึงติดไปกับ save/load `.bmaplan`
- canvas แสดง label ชนิดด้านและ note/ความกว้างถนนบน edge เพื่อเตรียมต่อยอด rule ตรวจระยะร่นรายด้าน
- เพิ่มเมนู context "กำหนดด้านที่ดิน" และปุ่ม toolbar "ด้านที่ดิน" สำหรับกลับมาแก้ภายหลัง
- เพิ่มปุ่ม toolbar "ระยะร่น" สำหรับแสดง/ซ่อนเส้นระยะระหว่าง polygon ที่ดินกับแนวอาคาร โดยค่าเริ่มต้นยังแสดงเหมือนเดิม

---

## Performance

- `will-change: transform` บน canvas container
- RAF throttle สำหรับ mousemove (ลด 60fps → เท่าที่จำเป็น)

---

## วิธีติดตั้ง

```bash
cd /Users/nucifer/Library/CloudStorage/GoogleDrive-ideaplanstudio@gmail.com/ไดรฟ์ของฉัน/01\ project/ai/bma-plan/proto
pip install xlsxwriter
python server.py
```

เปิด: http://localhost:8000

---

## หมายเหตุ

- ต้องติดตั้ง `xlsxwriter` ก่อนถึงจะใช้ Export XLSX ได้
- ถ้าไม่ติดตั้ง ระบบจะแจ้ง error และบอกให้ติดตั้งเอง

## ผลทดสอบล่าสุด

รันเมื่อ 2026-04-26 ด้วย `python3`:

```text
python3 -m py_compile proto/server.py proto/e2e_ui_test.py
python3 proto/e2e_ui_test.py smoke
python3 proto/e2e_ui_test.py full
```

ผลลัพธ์สำคัญ:

```text
XLSX_OK {'summary': 'อาคาร/ห้อง 0.75 · (-)ช่องว่าง 0.10 · สุทธิ 0.65 ตร.ม.', 'xlsx_file': 'measurements_report.xlsx'}
WHEEL_OK {'zoom': '38%->81%'}
SNAP_OK {'ix': {'x': 100, 'y': 100, 't': 'ix'}, 'perp': {'x': 100, 'y': 100, 't': 'perp'}, 'close': {'x': 100, 'y': 100, 't': 'close'}, 'indexed': True, 'userEp': {'x': 210, 'y': 210, 't': 'ep'}, 'userMp': {'x': 235, 'y': 210, 't': 'mp'}, 'userNl': {'x': 233, 'y': 210, 't': 'nl'}}
SELECT_OK {'before': 'land', 'cbType': 'land', 'landSelected': True, 'renameKeepsLand': True, 'polyType': 'room', 'polyColor': '#ff00ff', 'polyOpacity': 0.4, 'openingColor': '#00ffff', 'openingOpacity': 0.35, 'hit': {'type': 'opening', 'idx': 0}, 'nearest': {'type': 'opening', 'idx': 0}}
SETBACK_OK {'buildingSelected': True, 'count': 12, 'distances': [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], 'allPerp': True}
EXT_MEASURE_OK {'lineCount': 1, 'linePts': 3, 'beforeVertex': 20, 'afterVertex': 30, 'total': 5.848, 'segments': 2, 'refs': 1, 'refType': 'road', 'parking': 2, 'refDistance': 4.667, 'parkingSummary': 2, 'parkingTypeRows': 2, 'refReportRows': 5, 'parkingRows': 2, 'refDistanceRows': 5, 'pathRows': 1, 'reportHasSections': True, 'tooltips': ['วัดระยะต่อเนื่องหลายจุด กด Enter เพื่อจบ', 'วาดเส้นอ้างอิง เช่น ถนน คลอง ผนัง', 'แสดงระยะจาก object ที่เลือกไปหาเส้นอ้างอิง', 'คลิกนับช่องจอดรถ 1 ครั้ง = 1 คัน', 'Snap endpoint ปลายเส้น']}
ANNOT_OK {'annotated_file': 'annotated_export.pdf', 'label': 'E2E_ROOM_A'}
REAL_OK {'page_label': '1 / 45', 'page_label_2': '2 / 45', 'rotation': '90°', 'export_pages': 2}
```
