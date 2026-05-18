# AGENTS.md — BMA-Plan Development Agent Instructions

> ใช้ไฟล์นี้เป็นกติกาสำหรับ coding agent ทุกตัวก่อนแตะโปรเจกต์ BMA-Plan
> อัปเดต: 2026-05-07

---

## 1. Mission (ภารกิจ)

พัฒนา BMA-Plan Phase 1 ให้เป็น **Mini-CAD for Area Measurement** จาก PDF แบบก่อสร้าง

```text
Phase 1 = Raster PDF Measurement Assistant
ไม่ใช่ระบบตรวจกฎหมาย ไม่ใช่ AI checker ไม่มี Rule Engine
```

โฟกัส: ความถูกต้องของ scale, measurement, layer management, overlapping UX, export, regression safety

---

## BMA-Plan Agent Operating Loop — GTM Infinite Loop

ทุก sprint และ agent role ต้องทำงานตาม GTM Infinite Loop ก่อนตัดสินใจแก้ไฟล์ สรุปผล หรือส่งต่อ งานนี้เป็น operating method ของ agent ทั้งหมด ไม่ใช่ feature ใหม่ของ product

### 1. Understanding Condition

Agent ต้องเข้าใจ condition ปัจจุบันก่อน patch:
- สถานะล่าสุดจาก `log.md`, `index.md`, `CURRENT_STATUS.md`/report ล่าสุด
- Phase scope และ stop conditions
- ไฟล์ที่จะอ่าน/แก้
- test state ล่าสุดและ command baseline
- defect/gap ที่ต้องแก้จริง
- contracts ที่ห้ามถอยหลัง เช่น case isolation, raw geometry recalculation, export/UI consistency, overlapping picker, layer lock

ห้ามเริ่ม patch จาก assumption หรือจากความจำล้วน

### 2. Restoration

ถ้า workflow หลักเสีย ต้อง restore ก่อนทำ improvement ใด ๆ

Core workflow ที่ต้องรักษา:
- app opens
- PDF upload
- Project Setup
- Start Measuring
- set scale
- draw area/opening
- overlapping picker
- layer lock/visibility
- save/load
- XLSX export

ถ้า core workflow ข้างต้น fail ให้ถือว่าเป็น restoration task ก่อน ไม่ใช่ sprint เพิ่ม feature

### 3. Defect Factors Analysis

ก่อนแก้ ให้ระบุ defect factor ที่เป็น root cause หรือ likely root cause:
- layout/responsive issue
- event lifecycle issue
- duplicated state
- missing serialization field
- missing regression test
- unclear UX flow
- export mismatch
- stale documentation
- scope leakage
- environment mismatch

ถ้ายังไม่รู้ defect factor ให้ตรวจเพิ่มก่อน patch

### 4. Eliminating Factors of Defect

แก้ root cause ให้แคบที่สุด และเพิ่ม regression guard เมื่อทำได้:
- patch เฉพาะไฟล์ใน scope
- รักษา behavior เดิมที่ไม่เกี่ยวข้อง
- ไม่เพิ่ม abstraction ถ้าไม่จำเป็น
- ไม่แก้เอกสารให้ดูผ่านแทนการแก้ defect จริง
- เพิ่ม/ปรับ test เมื่อ defect มี blast radius ต่อ workflow

### 5. Setting Condition

หลังแก้ ต้อง lock standard ใหม่ไว้ใน condition artifacts:
- `PATCH_SUMMARY.md`
- `TEST_RESULT.md` หรือ no-test rationale สำหรับ docs-only
- `UI_MANUAL_TEST.md` เมื่อแตะ UI หรือ UX workflow
- `FINAL_REPORT_FOR_CHATGPT.md`
- `log.md`
- `CURRENT_STATUS.md` หรือ `index.md` เมื่อ operating condition หรือ roadmap เปลี่ยน

เอกสารต้องบอกว่าเปลี่ยนอะไร ทำไม test อะไรผ่าน และ known gaps เหลืออะไร

### 6. Condition Kaizen

Agent อาจปรับ UX/code/docs ให้ดีขึ้นเฉพาะใน sprint scope เท่านั้น:
- ทำให้ workflow ชัดขึ้น
- ลด defect factor ที่พบจริง
- เพิ่ม regression safety
- ทำให้ report/status อ่านต่อได้ง่ายขึ้น

ห้ามใช้ kaizen เป็นข้ออ้างเพิ่ม feature นอก Phase 1 หรือขยาย scope

### 7. Condition Management

ก่อนจบงานต้องบันทึกและจัดการ condition:
- PASS/FAIL ชัดเจน
- test หรือ verification ชัดเจน
- source files ที่แตะชัดเจน
- known gaps และ next action ชัดเจน
- ถ้าเป็น docs-only ต้องยืนยันว่า source code ไม่เปลี่ยน
- ถ้ามี failure ต้องระบุ stop point และเหตุผล

### 8. Pre-Release Gate (sandbox)

ก่อนปล่อยรุ่นใหม่ใดก็ตามที่ผู้ใช้ภายนอกจะสัมผัส (PyInstaller build, demo ให้ stakeholder, hand-off ไฟล์ install, customer pilot):

- ต้องมี PDF ลูกค้า / ไฟล์ที่เคยมีปัญหาอยู่ใน `sandbox/` (gitignored)
- รัน `/bma-sandbox-test` ก่อนปล่อย
  - PASS = ทุกไฟล์ผ่าน Tier 1 + Tier 2 — release ได้
  - ISSUES = มี BROKEN/FRICTION/COSMETIC แต่ไม่มี CRASH — release ได้ก็ต่อเมื่อ BROKEN ระดับ blocker ถูก triage หรือ accept ลายลักษณ์อักษรแล้ว
  - CRASH = ห้าม release จนกว่าจะแก้ — เป็น loop stop-condition ของ `/bma-dev-loop` เช่นกัน
- ทุก finding ที่ filed ลง `PHASE_INDEX.md → Discovered backlog → sandbox YYYY-MM-DD` ต้องมี source PDF filename ติดอยู่เพื่อให้ reproduce ได้
- ถ้า triager เสนอ new skill/subagent → ห้ามสร้างไฟล์ `.claude/` เอง — เป็น sprint แยกผ่าน `/bma-dev-loop`

หลักการ: "ห้ามให้ลูกค้าเจอปัญหาที่เราเคยมีไฟล์ตัวอย่างอยู่แต่ไม่ได้รัน"

### Agent 0–4 Role Mapping

- Agent 0 = Planner / Orchestrator: อ่าน condition, ระบุ scope, stop conditions, acceptance criteria และแผน
- Agent 1 = Coder: ทำ patch หรือ docs update แบบแคบตาม defect factor
- Agent 2 = Reviewer / Tester: ตรวจ regression, source scope, acceptance criteria และผล test
- Agent 3 = Docs / Condition Setting: อัปเดต report/status/log ให้ lock condition ใหม่
- Agent 4 = Final Reporter / Condition Management: สรุป PASS/FAIL, files changed, tests, known gaps, next action

### Mandatory Sprint Outputs

ทุก sprint ต้องมี output อย่างน้อย:
- plan / scope statement
- files read และ files edited
- Phase 1 scope check
- verification result
- `PATCH_SUMMARY.md`
- `TEST_RESULT.md` หรือเหตุผลที่ไม่รัน test
- `FINAL_REPORT_FOR_CHATGPT.md`
- `log.md` entry

ถ้าเป็น UI sprint ต้องมี `UI_MANUAL_TEST.md` หรือเหตุผลที่ไม่ทำ manual UI check

### Phase 1 / Phase 2 Rule

Phase 1 ต้องผลิต usable measurement/output workflow ก่อน:
- PDF measurement
- Project Setup
- save/reopen
- Excel export
- annotated PDF export

Phase 2 เป็น legal/building-control skill สำหรับช่วย manual review เท่านั้น ไม่ใช่ automatic legal pass/fail

Legal/building-control skill ต้องแยกข้อมูลเป็น:
1. facts
2. law sources/effective dates
3. exceptions/transitional provisions
4. guidelines/circulars/case discussions
5. human judgment notes

ห้ามผสม legal conclusion เข้ากับ Phase 1 measurement engine และห้ามใช้ภาษา/logic ที่ทำให้ระบบดูเหมือนตัดสินผ่าน/ไม่ผ่านตามกฎหมายอัตโนมัติ

---

## 2. Required Reading Order (ลำดับเอกสารที่ต้องอ่าน)

ก่อนแก้โค้ด อ่านตามลำดับนี้:

**ทุกครั้งที่เริ่ม session ใหม่ ต้องอ่าน `log.md` เสมอ** แม้งานจะเป็นงานเล็ก งานเอกสาร หรือแค่รัน server/test เพื่อให้รู้กิจกรรมล่าสุด สถานะล่าสุด และสิ่งที่เพิ่งเปลี่ยนก่อนตัดสินใจทำงานต่อ

1. `BMA_PLAN_PHASE1_CONTEXT.md` — **กรอบพัฒนา Phase 1 ฉบับสมบูรณ์ (30 หัวข้อ) อ่านก่อนทุกอย่าง**
2. `index.md` — project map + sprint roadmap ปัจจุบัน
3. `proto/STATUS.md` — สถานะล่าสุด, API, test suite, known gaps
4. `PROGRESS.md` — bug/feature ที่แก้แล้ว และ behavior ที่ห้ามถอยหลัง
5. `log.md` — บันทึกเหตุการณ์ทุกอย่าง ต้องอ่านทุกครั้งเมื่อเริ่ม session และอ่าน entry ล่าสุดก่อนวางแผน/แก้ไฟล์
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
- **ทุกกิจกรรมใน session ต้องอัปเดต `log.md` ก่อนสรุปงาน** ไม่ว่าจะเป็นการอ่าน/วิเคราะห์, วางแผน, แก้โค้ด, แก้เอกสาร, รันทดสอบ, เปิด/ปิด server, sync ไฟล์, หรือการตัดสินใจสำคัญ
- `log.md` ต้องระบุอย่างน้อย: เวลา, สิ่งที่ทำ, เหตุผล, ไฟล์ที่แตะ, ผลทดสอบ/ผลตรวจ, known issues
- ถ้างานไม่มีการแก้โค้ดหรือไม่ได้รัน test ให้บันทึกเหตุผลไว้ใน `log.md` ด้วย

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

## 8. Static Asset Verification (ตรวจสอบ Static Files)

> ทุก sprint ที่แตะ `proto/server.py`, `proto/static/`, หรือ `proto/ui.html` ต้องผ่าน checklist นี้

### Required server.py pattern

```python
from pathlib import Path
from fastapi.staticfiles import StaticFiles

_BASE_DIR = Path(__file__).resolve().parent
_STATIC_DIR = _BASE_DIR / "static"
print(f"[static] serving from: {_STATIC_DIR}")
app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")
```

**ห้าม** guard ด้วย `if _STATIC_DIR.exists():` — การ guard นี้ซ่อน RuntimeError จาก missing `aiofiles` ทำให้ mount ล้มเหลวแบบ silent → 404 ทุก static request

### Required dependency

`aiofiles` ต้องอยู่ใน `proto/requirements.txt` และต้องติดตั้งแล้ว:

```bash
python -c "import aiofiles"   # ต้องไม่ error
```

### E2E assertions (ต้อง True ทุกครั้ง)

| Key | ตรวจอะไร |
|-----|----------|
| `cssLinkPresent` | `<link href="/static/css/app.css">` อยู่ใน DOM |
| `cssVarLoaded` | CSS custom property `--blue` ถูก load |
| `semanticMetaJsLoaded` | `AREA_SEMANTIC_TAGS` ถูก define ใน global scope |
| `openingParentJsLoaded` | `openingProbePoints` ถูก define ใน global scope |

### HTTP verification (ทำก่อน commit ทุกครั้งที่แตะ static)

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/static/css/app.css
# ต้อง: 200
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/static/js/semantic-meta.js
# ต้อง: 200
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/static/js/opening-parent.js
# ต้อง: 200
```

### ตรวจ BOM ใน CSS

ถ้าสร้างหรือเขียน `app.css` ใหม่ ต้องตรวจ BOM:

```bash
python -c "
with open('static/css/app.css','rb') as f: b=f.read(3)
print('BOM present:', b == b'\xef\xbb\xbf')  # ต้อง False
"
```

ถ้า True → strip BOM ก่อน commit ดู `docs/process/ANTI_PATTERNS.md` #4

### เมื่อ UI แสดงผลเป็น raw HTML

ดู `docs/process/TROUBLESHOOTING.md` — Static Assets Return 404

---

## 9. Stop Conditions (เงื่อนไขที่ต้องหยุด)

หยุดและรายงานทันทีถ้าเจอ:

- scale ไม่รู้ที่มาแต่ถูกใช้เป็นเมตร/ตารางเมตรจริง
- export result ไม่ตรงกับ UI summary
- real permit PDF โหลดแล้วข้อมูลหายหลังเปลี่ยนหน้า/หมุนหน้า
- annotation export ไม่ตรงตำแหน่งหลัง rotation
- secret plaintext ใน project
- กฎหมายถูก hardcode โดยไม่มี source
- มีการเพิ่ม law/AI/OCR/Rule Engine เข้ามาใน Phase 1
- PDF vector dependency ถูก assume โดยไม่มี raster fallback
