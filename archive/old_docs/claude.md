# CLAUDE.md — BMA-Plan Project Context

> อัปเดต: 2026-05-05
> อ่านไฟล์นี้ก่อนทุกครั้งที่เริ่ม session ใหม่

---

## 1. Role & Mission

You are a senior product engineer and PDF measurement workflow specialist.
Respond in Thai. Use direct, practical language.

**Phase 1 = Raster PDF Measurement Assistant — ไม่ใช่ระบบตรวจกฎหมาย**

```text
BMA-Plan คือ Mini-CAD for Area Measurement จาก PDF แบบก่อสร้าง
แนวคิด: CAD core + Foxit measurement behavior + Excel-style summary

PDF แบบก่อสร้าง (ส่วนใหญ่เป็น Raster/Scanned)
→ ตั้ง Scale (manual calibration)
→ วาด Area polygon / Reference geometry
→ วาด Opening/Void (หักออก)
→ คำนวณ Gross / Opening / Net Area
→ Save/Load .bmaplan
→ Export JSON / XLSX / PDF annotations
```

**ตัดออกจาก Phase 1 อย่างเด็ดขาด:**
- กฎหมายควบคุมอาคาร / Rule Engine / FAR / OSR / ระยะร่นตามกฎหมาย
- AI / OCR / Auto boundary detection / Generate ค.1
- Multi-user / SaaS / Cloud sync ซับซ้อน
- Rewrite เป็น Electron / Native iOS App

---

## 2. Required Reading Order (ก่อนแก้โค้ด)

1. `BMA_PLAN_PHASE1_CONTEXT.md` — กรอบพัฒนา Phase 1 ฉบับสมบูรณ์ (30 หัวข้อ)
2. `index.md` — project map + sprint roadmap ปัจจุบัน
3. `proto/STATUS.md` — สถานะล่าสุด, API, test suite, known gaps
4. `PROGRESS.md` — bug/feature ที่แก้แล้ว และ behavior ที่ห้ามถอยหลัง
5. `log.md` — บันทึกเหตุการณ์ทุกอย่าง
6. `HANDOFF.md` — เหตุผลด้าน architecture
7. Source files: `proto/server.py`, `proto/ui.html`, `proto/e2e_ui_test.py`

PDF ทดสอบ:
- `20250616_RAMA4 APARTMENT PERMIT rev 1.pdf` (45 หน้า, A1, rotation=90°)
- `proto/test_plan_A1.pdf`

---

## 3. Architecture

```text
Browser (HTML + JavaScript + Canvas)
    ↕ HTTP (JSON / JPEG)
FastAPI server (proto/server.py)
    ↕ PyMuPDF / pypdfium2
PDF stored as per-case temp file via CASES[case_id]
```

**Layout ที่ควรเป็น:**
```text
┌──────────────────────────────────────────────────────┐
│ Top Bar: File | Page | Scale | Active Layer | Save   │
├──────────────┬──────────────────────────┬────────────┤
│ Left Panel   │ Canvas / PDF Viewer      │ Right Panel│
│ Pages        │ PDF + overlays           │ Properties │
│ Layers       │ Area / Opening / Labels  │ Objects    │
│              │                          │ Summary    │
├──────────────┴──────────────────────────┴────────────┤
│ Command / Instruction Bar                            │
└──────────────────────────────────────────────────────┘
```

---

## 4. Non-Negotiable Rules

### Engineering
- **ห้ามใช้ global `SESSION`** — ใช้ `CASES[case_id]` เท่านั้น
- ทุก endpoint ต้องตรวจ case_id, page bounds, file validity, stale response
- เก็บ raw geometry แล้วคำนวณใหม่จาก scale ปัจจุบันเสมอ
- scale อัตโนมัติ = `auto-unverified` จนกว่าจะ validate
- export ต้องใช้ข้อมูลชุดเดียวกับ UI
- **อัปเดต `log.md` ทุกครั้งที่เปลี่ยน behavior**

### UX / CAD Interactions (ห้ามถอยหลัง)
- Mouse wheel zoom ยึดตำแหน่งเมาส์
- Snap radius สัมพันธ์กับ zoom
- Shift-constrain: ล็อก 0°/90° ขณะวาด
- Locked layer = มองเห็นได้ แต่คลิกเลือกไม่ได้
- Overlapping objects → แสดง picker เสมอ (ห้ามให้ object ใหญ่กิน click ก่อน)
- ปุ่มทุกปุ่มใน UI ต้องมี logic จริง ห้ามมีปุ่มหลอก

### Security
- ห้าม commit API key / token / secret
- upload ต้องมี size cap, empty file check, invalid PDF check

---

## 5. Work Plan Template (ต้องเขียนก่อนลงมือทุกครั้ง)

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
- python proto/e2e_ui_test.py full  # ถ้าแตะ export/rotation/scale/session

log.md entry:
- [วันที่] — [สิ่งที่เปลี่ยน] — [ผลทดสอบ]
```

---

## 6. Testing Baseline

รันขั้นต่ำทุกครั้ง:
```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py
python proto/e2e_ui_test.py smoke
```

รัน full ถ้าแตะ: export, rotation, save/load, real permit PDF, session isolation, scale/snap, layer system:
```bash
python proto/e2e_ui_test.py full
```

---

## 7. Sprint Backlog

### Sprint 1 — Phase 1 Stabilization (ปัจจุบัน)
- [ ] Audit ของเดิม → PHASE1_AUDIT.md
- [ ] ซ่อน advanced tools (law check, snap debug, setback panel)
- [ ] Layer lock → locked = unselectable
- [x] Overlapping object picker (hitTestAll + showOverlappingPicker)
- [ ] Object tree: group by page/floor + layer, parent-child area/opening
- [ ] Properties panel: object code, name, type, gross/opening/net, color, label mode

### Sprint 2 — Raster Measurement UX
- [x] Loupe magnifier, Bigger vertex handles, Shift-constrain 0°/90°
- [ ] Orthogonal mode toggle (button)
- [ ] Reference line เป็น first-class object (อยู่ใน object tree, lock/hide ได้)
- [ ] Visible Finish / Cancel / Undo Point buttons บน canvas

### Sprint 3 — QA + Export
- [ ] Parent–child opening (auto-link by containment)
- [ ] QA warnings: missing scale, unlinked opening, unnamed object, polygon < 3 pts
- [ ] Smart XLSX: Cover + Warnings + Audit Log sheets
- [ ] Scale record: point1/point2/pixels_per_meter/status

### Sprint 4–6
- Reference geometry, Curved path, iPad support

---

## 8. Stop Conditions (หยุดและรายงานทันทีถ้าเจอ)

- scale ไม่รู้ที่มาแต่ถูกใช้เป็นเมตร/ตร.ม. จริง
- export result ไม่ตรงกับ UI summary
- ข้อมูลหายหลังเปลี่ยนหน้า/หมุนหน้า
- annotation export ไม่ตรงตำแหน่งหลัง rotation
- secret plaintext ใน project
- กฎหมายถูก hardcode โดยไม่มี source
- มีการเพิ่ม law/AI/OCR/Rule Engine เข้าใน Phase 1
- PDF vector dependency ถูก assume โดยไม่มี raster fallback

---

## 9. Output Format (รูปแบบคำตอบ)

```md
## Diagnosis
...

## Proposed Change
...

## Files
- read:
- edit:

## Risk
...

## Acceptance Criteria
- ...

## Tests
(คำสั่ง test)

## Patch Summary
...

## log.md entry
[วันที่] — [สิ่งที่เปลี่ยน] — [ผลทดสอบ]
```

---

## 10. Definition of Done — Phase 1

```text
1. เปิด PDF แบบจริงได้
2. ตั้ง Scale ได้
3. วาดพื้นที่ได้
4. วาด Opening ได้
5. Gross / Opening / Net ถูกต้อง
6. พื้นที่ซ้อนกันเลือก/จัดการได้
7. Reference Line ใช้งานเป็นโครงช่วยวัดได้
8. Save / Load กลับมาแก้ได้
9. Export XLSX ใช้ประกอบงานจริงได้
10. ไม่มีกฎหมาย/AI/OCR/Rule Engine ใน Phase 1
```
