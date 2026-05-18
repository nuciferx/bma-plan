# PDF Scale Prototype — Handoff Document
> อัปเดต: 2026-03-24

---

## 1. ภาพรวม Project

### เป้าหมาย
สร้างเครื่องมือช่วยตรวจสอบแบบก่อสร้าง (Building Permit Plans) สำหรับกรุงเทพฯ (BMA)
- อ่าน PDF แบบก่อสร้าง → detect scale → วัดระยะ/พื้นที่จริงได้
- ออกแบบมาสำหรับ PDF vector ขนาด A1 หลายสิบหน้า (เช่น 45 หน้า)
- รองรับ snap ไปยัง vector endpoint + สอบเทียบ scale ด้วยมือ

### Project ที่เกี่ยวข้องใน `ai/`
| โฟลเดอร์ | ทำอะไร |
|---|---|
| `bma-plan/` | GAS + index.html เดิม (fabric.js + PDF.js) — annotation tool ใน browser |
| `bma-plan/proto/` | **Prototype ใหม่** FastAPI + fitz — แก้ปัญหาสถาปัตยกรรมของเดิม |
| `bma-system/` | Next.js + Supabase — ต่ออายุใบอนุญาตก่อสร้าง + เปลี่ยนผู้ควบคุมงาน |

---

## 2. สถาปัตยกรรม Prototype ใหม่

```
Browser (vanilla JS + Canvas)
    ↕ HTTP (JSON / JPEG)
FastAPI server (server.py)
    ↕ fitz (PyMuPDF)
PDF file (local)
```

### ทำไมถึงเปลี่ยนจากเดิม
| ปัญหาเดิม (bma-plan/index.html) | แก้ใน Prototype |
|---|---|
| XSS — innerHTML ใส่ user text โดยตรง | ใช้ canvas + JSON API เท่านั้น |
| 3 layer coordinate: PDF.js→fabric.js→canvas | fitz render server-side → ภาพเดียว → CSS transform ชั้นเดียว |
| Render 3 รอบต่อหน้า | Render ครั้งเดียวที่ server |
| VectorEngine ค้าง UI 5+ วินาที | extract ที่ server ครั้งเดียว |
| ไม่มี thumbnail navigation | Thumbnail strip ซ้าย + keyboard nav |
| ไม่มี scale calibration | คลิก 2 จุด + ป้อนระยะ |
| dependency 1.5 MB (fabric+PDF.js+pdf-lib) | vanilla JS เท่านั้น |

---

## 3. ไฟล์ใน `proto/`

| ไฟล์ | หน้าที่ |
|---|---|
| `server.py` | **หลัก** — FastAPI server + HTML frontend ฝังอยู่ใน string `HTML` |
| `pdf_scale.py` | prototype ต้น: อ่าน page size, detect scale text, extract snap candidates |
| `scale_validator.py` | validate scale ด้วย dimension line cross-check |
| `scale_bar_detect.py` | 3-method: title block + scale bar graphic + dimension cross-validate |
| `make_test_pdf.py` | สร้าง test PDF (A1, rooms, title block, scale bar) |
| `patch_html.py` | script แทน HTML block ใน server.py (ใช้ครั้งเดียว) |
| `test_plan_A1.pdf` | test PDF ที่สร้างจาก make_test_pdf.py |

### PDF จริงที่ทดสอบ
```
../20250616_RAMA4 APARTMENT PERMIT rev 1.pdf
```
- 45 หน้า, A1 landscape, rotation=90° (mediabox 1684×2384)
- 43/45 หน้ามี scale text "1:XX"
- page 5 = site plan (มีหมุด ข.ท.ด. 5+ จุด)
- page 7–8 = floor plans (validated 1:98–101 ✅)

---

## 4. server.py — API Endpoints

### รัน
```bash
cd "F:/other computers/my laptop/ai/bma-plan/proto"
python server.py
# เปิด http://localhost:8000
```

### Endpoints
| Method | Path | Params | Returns |
|---|---|---|---|
| POST | `/upload` | form: file | `{pages, name}` |
| GET | `/page/{n}` | `scale=1.5`, `rot=0` | JPEG image |
| GET | `/thumb/{n}` | `rot=0` | JPEG thumbnail (0.18x) |
| GET | `/analyse/{n}` | `rot=0` | JSON: scale, pins, snaps, size |
| GET | `/` | — | HTML frontend |

### `/analyse/{n}` response
```json
{
  "page": 5,
  "size": {"w_pt": 2384.0, "h_pt": 1684.0, "w_mm": 841.0, "h_mm": 594.0},
  "scale": {"N": 100, "label": "1:100", "pts_per_m": 28.3465},
  "pins": [{"cx": 234.5, "cy": 891.2, "id": "4289", "label": "ข5-4289"}],
  "snaps": [{"x": 100.0, "y": 200.0}, ...],
  "render_scale": 1.5
}
```

---

## 5. Frontend Features (JavaScript ใน HTML string)

### Mode
| Mode | ปุ่ม | การใช้งาน |
|---|---|---|
| Pan ✋ | default | drag เพื่อเลื่อน, scroll wheel zoom |
| ระยะ 📏 | btn-dist | click 2 จุด → แสดงระยะ (ม. หรือ pt ถ้าไม่มี scale) |
| พื้นที่ ⬡ | btn-area | click หลายจุด → click จุดแรกอีกครั้งเพื่อปิด → แสดงตร.ม. + ไร่-งาน-วา |
| สอบเทียบ 📐 | btn-calib | click 2 จุด + ป้อนระยะ → คำนวณ pts_per_m |

### Keyboard
| Key | Action |
|---|---|
| `F` | Fit to window |
| `←` `→` | เปลี่ยนหน้า |
| `Escape` | กลับ Pan mode |

### Snap
- ดึง snap points จาก `/analyse/{n}` (vector endpoints จาก fitz)
- radius 20px (in canvas coords)
- แสดง visual indicator: วงกลม snap cursor ลอยตาม mouse
- snap สีเหลือง (dist mode) / สีเขียว (area mode)

### Rotation
- ปุ่ม ↺ ↻ หมุน 90° ต่อครั้ง
- เก็บ rotation per-page ใน `pageRotations = {page: deg}`
- server rotate pixmap + rotate snap coords พร้อมกัน

### Thumbnail Strip
- แถบซ้าย 130px, lazy load จาก `/thumb/{n}`
- แสดง scale badge (1:100 สีเขียว / no scale สีแดง) ต่อหน้า
- scroll to active page อัตโนมัติ

---

## 6. Scale Detection Logic (server.py)

```python
# อ่าน scale จาก text ใน PDF
SCALE_RE = re.compile(r'1\s*[:/]\s*(\d{2,5})', re.IGNORECASE)

def detect_scale(page):
    # ดึง spans ทั้งหน้า, match regex, เลือก font ใหญ่สุด
    # return: {N, label, pts_per_m} หรือ None
    pts_per_m = (1000 / N) * (72 / 25.4)  # pt ใน PDF ต่อ 1m จริง
```

### Scale validation (scale_bar_detect.py — ยังไม่ต่อเข้า server)
- Method 1: Title block text (confidence 90)
- Method 2: Graphical scale bar + tick + label (confidence 80)
- Method 3: Dimension line cross-validate (confidence 50–95)

---

## 7. หมุด ข.ท.ด. Detection (server.py)

```python
def detect_pins(page):
    # หา rect ขนาด 4–20pt ที่มี cross (H-line + V-line) ผ่านจุดกึ่งกลาง
    # + text ใกล้ๆ ที่มี "ข.ท.ด." หรือ "ข5" + ตัวเลข 4–6 หลัก
    # deduplicate: merge จุดที่ห่าง < 12pt
```

**หมายเหตุ**: ใช้ได้เฉพาะ PDF ที่มี vector หมุด (เช่น RAMA4 PDF) ไม่แสดงใน UI แล้ว แต่ยังอยู่ใน snap logic

---

## 8. Coordinate System

```
PDF space (fitz)     → pts, origin top-left (fitz), 72 pt = 1 inch
render_scale = 1.5   → canvas px = PDF pt × 1.5
CSS transform        → translate(panX,panY) scale(zoom), transform-origin:0 0
```

### cXY() — แปลง screen click → canvas px
```javascript
function cXY(e) {
    const r = canvas.getBoundingClientRect(); // accounts for CSS transform
    return {
        x: (e.clientX - r.left) * (canvas.width / r.width),
        y: (e.clientY - r.top) * (canvas.height / r.height)
    };
}
```

### ptsToM() — canvas px → เมตร
```javascript
function ptsToM(x1,y1,x2,y2) {
    // Math.hypot((x2-x1)/RS, (y2-y1)/RS) / pageData.scale.pts_per_m
}
```

---

## 9. Bugs ที่แก้ไปแล้ว

| Bug | สาเหตุ | Fix |
|---|---|---|
| Measurements ตามข้ามหน้า | loadPage ล้างแค่ mPts | เพิ่ม `mLines=[];mPolys=[];calibPts=[]` |
| วัดระยะไม่เห็นผล | ptsToM() return null → ไม่แสดงอะไร | แสดง pt + hint "สอบเทียบก่อน" |
| PDF ไม่กลางจอ | fitToWindow() คำนวณ panX/panY ผิด | `panX=(W-canvas.width*zoom)/2` |
| ไม่มี thumbnail nav | — | เพิ่ม #thumb-strip + lazy load |
| snap ไม่มี visual | — | เพิ่ม #snap-cur floating div |
| หมุดแสดงทุกไฟล์ | — | เอา pin render ออก ใช้แค่ใน snap logic |

---

## 10. Comparison กับ Foxit / Bluebeam

| Feature | Foxit Editor | Bluebeam Revu | Prototype นี้ |
|---|---|---|---|
| Auto detect scale | ❌ ต้อง set เอง | ❌ | ✅ อ่านจาก PDF text |
| Export format | XFDF/FDF (string) | CSV + XML structured | **ยังไม่ทำ** |
| ค่าตัวเลข float จริง | ❌ ต้อง parse string | ✅ | ✅ |
| Batch export ข้ามหน้า | ❌ | ✅ | ❌ |
| Live Excel link | ❌ | ✅ | ❌ |
| ไร่-งาน-วา | ❌ | ❌ | ✅ |
| Snap to หมุด ข.ท.ด. | ❌ | ❌ | ✅ (เฉพาะไฟล์มี) |
| ราคา | ~$150/year | ~$350/year | Free (self-hosted) |

---

## 11. งานที่ยังค้างอยู่ (TODO)

### ง่าย / เร็ว
- [ ] **Per-page measurement store** — เก็บ `pageMeasures = {page: {lines, polys}}` ไม่ให้หายตอนเปลี่ยนหน้า
- [ ] **Export CSV/JSON** — รวม measurements ทุกหน้า export ได้
- [ ] **Summary panel** — แสดงรวม area/distance ทุก polygon ทุกหน้า

### กลาง
- [ ] **Scale validation UI** — ต่อ scale_bar_detect.py เข้า `/analyse/{n}` แสดง confidence
- [ ] **Save annotation เข้า PDF** — fitz ใส่ annotation layer ได้ (`page.add_line_annot()` ฯลฯ)
- [ ] **Multi-user session** — ตอนนี้ SESSION เป็น global dict (single user only)

### ยาก / ต้องคิดเพิ่ม
- [ ] **BOQ integration** — เชื่อม measurement → รายการวัสดุ/ราคา
- [ ] **ค.1 draft** — เชื่อมข้อมูลพื้นที่กับ docx template (มีใน bma-system แล้ว)
- [ ] **PDF scanned** — ตอนนี้ใช้ได้เฉพาะ vector PDF

---

## 12. Dependencies

```bash
pip install fastapi uvicorn python-multipart pymupdf
# PyMuPDF = fitz
```

```
Python 3.11+
uvicorn (ASGI server)
fastapi
pymupdf (fitz)
python-multipart (for file upload)
```

---

## 13. เรื่องที่คุยกัน (Context)

1. **เริ่มจาก** review GAS program (`bma-plan/index.html.txt`) → พบ bugs สำคัญ (XSS, memory, coordinate)
2. **ตัดสินใจ** สร้าง Python prototype แทน — เร็วกว่า, แม่นกว่า, แก้ปัญหาสถาปัตยกรรม
3. **ทดสอบกับ** RAMA4 PDF จริง — scale detection ทำงานได้ 43/45 หน้า
4. **หมุด ข.ท.ด.** detect ได้ 5/9 จุด บน page 5 — ระยะ 7.71m ตรงกับในแบบ ✅
5. **User feedback**: PDF ไม่กลางจอ + ไม่มี navigator → แก้แล้ว
6. **Snap** เพิ่ม visual indicator (วงกลมลอยตาม mouse)
7. **Scale calibration** คลิก 2 จุด + ป้อนระยะ (Option B)
8. **Rotation** ปุ่ม ↺ ↻ server-side rotate
9. **Foxit research**: export ได้แค่ XFDF/FDF (parse string) — Bluebeam ดีกว่า แต่ $350/year

---

*Generated: 2026-03-24*
