# AGENT.md — BMA-Plan Development Agent Instructions

> ใช้ไฟล์นี้เป็นกติกาสำหรับ coding agent ทุกตัวก่อนแตะโปรเจกต์ BMA-Plan
> อัปเดต: 2026-05-05

---

## 1. Mission (ภารกิจ)

พัฒนา BMA-Plan Phase 1 ให้เป็น **Mini-CAD for Area Measurement** จาก PDF แบบก่อสร้าง

```text
Phase 1 = Raster PDF Measurement Assistant
ไม่ใช่ระบบตรวจกฎหมาย ไม่ใช่ AI checker ไม่มี Rule Engine
```

โฟกัส: ความถูกต้องของ scale, measurement, layer management, overlapping UX, export, regression safety

---

## 2. Required Reading Order (ลำดับเอกสารที่ต้องอ่าน)

ก่อนแก้โค้ด อ่านตามลำดับนี้:

1. `BMA_PLAN_PHASE1_CONTEXT.md` — **กรอบพัฒนา Phase 1 ฉบับสมบูรณ์ (30 หัวข้อ) อ่านก่อนทุกอย่าง**
2. `index.md` — project map + sprint roadmap ปัจจุบัน
3. `proto/STATUS.md` — สถานะล่าสุด, API, test suite, known gaps
4. `PROGRESS.md` — bug/feature ที่แก้แล้ว และ behavior ที่ห้ามถอยหลัง
5. `log.md` — บันทึกเหตุการณ์ทุกอย่าง อ่านเพื่อรู้ว่าทำอะไรไปแล้ว
6. `HANDOFF.md` — เหตุผลด้าน architecture
7. source ที่เกี่ยวข้องโดยตรง:
   - `proto/server.py`
   - `proto/ui.html`
   - `proto/e2e_ui_test.py`
   - `proto/requirements.txt`

ถ้างานเกี่ยวกับ scale/snap/measurement ต้องเปิด PDF ทดสอบ:

- `20250616_RAMA4 APARTMENT PERMIT rev 1.pdf`
- `proto/test_plan_A1.pdf`

**ห้ามเพิ่ม legal rule จากความจำ** — Phase 1 ไม่มีกฎหมายเลย

---

## 3. Non-Negotiable Rules (กฎห้ามต่อรอง)

### 3.1 Phase 1 Scope Lock

```text
ห้ามเพิ่มใน Phase 1:
- กฎหมาย / Rule Engine / FAR / OSR / ระยะร่นตามกฎหมาย
- AI / OCR / Auto boundary detection
- Generate ค.1
- Multi-user / SaaS / Cloud sync ซับซ้อน
- Rewrite เป็น Electron / Native iOS App
```

PDF จริงเป็นภาพสแกน — ห้าม assume vector geometry หรือ magic trace จาก PDF lines

### 3.2 Engineering (วิศวกรรมระบบ)

- ห้ามใช้ global `SESSION` กลับมาแทน `CASES[case_id]`
- ทุก endpoint ที่แตะ PDF ต้องตรวจ case_id, page bounds, file validity, stale response
- measurement ต้องเก็บ raw geometry แล้วคำนวณใหม่จาก scale ปัจจุบัน
- scale อัตโนมัติต้องมีสถานะ `auto-unverified` จนกว่าจะ validate ได้
- export ต้องใช้ข้อมูลชุดเดียวกับ UI
- **ทุกครั้งที่เปลี่ยน behavior ต้องอัปเดต `log.md`**

### 3.3 Security (ความปลอดภัย)

- ห้าม commit API key, token, password, secret
- ถ้าเจอ secret ใน repo ให้รายงานและเสนอ rotate key
- upload ต้องมี size cap, empty file check, invalid PDF check, encrypted PDF check
- hosted mode ต้องมี TTL cleanup

### 3.4 UX (ประสบการณ์ผู้ใช้)

- งานวัดแบบ A1 ต้องมี mouse wheel zoom ยึดตำแหน่งเมาส์
- snap radius ต้องสัมพันธ์กับ zoom
- Shift-constrain: ล็อก 0°/90° ขณะวาด
- ปุ่มที่มีใน UI ต้องมี logic จริง ห้ามมีปุ่มหลอก
- Locked layer = ยังมองเห็น แต่คลิกเลือกไม่ได้
- Overlapping objects → แสดง picker เสมอ (ห้ามให้ object ใหญ่กิน click ก่อน)

---

## 4. Work Plan Template (แม่แบบแผนก่อนลงมือ)

ก่อนแก้โค้ด ให้เขียนแผนนี้ก่อนเสมอ:

```md
## Plan

Goal:
- ...

Phase 1 scope check:
- [ ] ไม่มีกฎหมาย/AI/OCR/Rule Engine
- [ ] PDF จริงเป็นภาพ — ไม่พึ่ง vector geometry

Files to read:
- ...

Files to edit:
- ...

Contracts to preserve:
- case_id isolation
- raw geometry recalculation
- export/UI consistency
- CAD-like interactions (zoom, snap, Shift-constrain)

Acceptance criteria:
- ...

Tests:
- python -m py_compile proto/server.py proto/e2e_ui_test.py
- python proto/e2e_ui_test.py smoke
- python proto/e2e_ui_test.py full  # if needed

log.md entry:
- [วันที่] — [สิ่งที่เปลี่ยน] — [ผลทดสอบ]
```

---

## 5. Testing Baseline (ฐานการทดสอบ)

รันขั้นต่ำทุกครั้ง:

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py
python proto/e2e_ui_test.py smoke
```

ถ้าแตะเรื่องต่อไปนี้ ต้องรัน full:

- export (CSV/JSON/XLSX/PDF/PDF+annotations)
- rotation
- persistence / save-load
- real permit PDF
- session isolation
- scale/snap engine
- annotation PDF
- layer system

```bash
python proto/e2e_ui_test.py full
```

---

## 6. Sprint Backlog Phase 1

### Sprint 1 — Phase 1 Stabilization (ปัจจุบัน)

```text
[ ] Audit ของเดิม → PHASE1_AUDIT.md
[ ] ซ่อน advanced tools (law check, snap debug, setback panel)
[ ] Layer lock → locked = unselectable
[✅] Overlapping object picker (hitTestAll + showOverlappingPicker)
[ ] Object tree: group by page/floor + layer, parent-child area/opening
[ ] Properties panel: object code, name, type, gross/opening/net, color, label mode
```

### Sprint 2 — Raster Measurement UX

```text
[✅] Loupe magnifier
[✅] Bigger vertex handles
[✅] Shift-constrain 0°/90°
[ ] Orthogonal mode toggle (button)
[ ] Reference line เป็น first-class object (อยู่ใน object tree, lock/hide ได้)
[ ] Visible Finish / Cancel / Undo Point buttons บน canvas
```

### Sprint 3 — QA + Export

```text
[ ] Parent–child opening (auto-link by containment)
[ ] QA warnings: missing scale, unlinked opening, unnamed object, polygon < 3 pts
[ ] Smart XLSX: Cover + Warnings + Audit Log sheets
[ ] Scale record: point1/point2/pixels_per_meter/status
```

### Sprint 4 — Reference Geometry

```text
[ ] reference_line / reference_arc / reference_circle as first-class objects
[ ] Snap source จาก user reference geometry (เพราะ PDF จริงเป็นภาพ)
```

### Sprint 5 — Curved Path

```text
[ ] Path data model (line + arc_3pt)
[ ] Flatten arc → polyline → คำนวณพื้นที่
[ ] Export ระบุ area_method = flattened_arc
```

### Sprint 6 — iPad Support

```text
[ ] Touch UI (44px targets)
[ ] Floating tool palette
[ ] Bottom sheet picker/properties
[ ] Long press menu แทน right click
```

---

## 7. Commit Discipline (วินัยการแก้โค้ด)

หนึ่งงาน = หนึ่งเป้าหมาย

- อย่าผสม UI refactor กับ logic rule ใน commit เดียว
- อย่าผสม export change กับ snap engine change ใน commit เดียว

ทุกครั้งที่แก้ ให้บันทึก **ทั้งใน commit message และใน `log.md`**:

```md
## Change Log
- What changed:
- Why:
- Risk:
- Tests run:
- Known remaining gaps:
```

---

## 8. Stop Conditions (เงื่อนไขที่ต้องหยุด)

หยุดและรายงานทันทีถ้าเจอ:

- scale ไม่รู้ที่มาแต่ถูกใช้เป็นเมตร/ตารางเมตรจริง
- export result ไม่ตรงกับ UI summary
- real permit PDF โหลดแล้วข้อมูลหายหลังเปลี่ยนหน้า/หมุนหน้า
- annotation export ไม่ตรงตำแหน่งหลัง rotation
- secret plaintext ใน project
- กฎหมายถูก hardcode โดยไม่มี source
- มีการเพิ่ม law/AI/OCR/Rule Engine เข้ามาใน Phase 1
- PDF vector dependency ถูก assume โดยไม่มี raster fallback
