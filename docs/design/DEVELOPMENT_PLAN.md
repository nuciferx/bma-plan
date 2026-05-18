# BMA-Plan Development Plan

อัปเดตจากเอกสารและ source ที่อ่านในโปรเจกต์ ณ 2026-04-25

## Current Baseline

โปรเจกต์หลักตอนนี้คือ prototype ใน `proto/`:

- Backend: `proto/server.py` ใช้ FastAPI, PyMuPDF, pypdfium2
- Frontend: `proto/ui.html` เป็น vanilla HTML/JS canvas app
- สถานะล่าสุดรองรับ upload PDF per case, render page/thumbnail, analyse snap/scale, manual calibration, measurement per page, save/load `.bmaplan`, export CSV/JSON/PDF/PDF annotations/XLSX
- มี E2E smoke/full ใน `proto/e2e_ui_test.py`
- real test PDF หลักคือ `20250616_RAMA4 APARTMENT PERMIT rev 1.pdf` จำนวน 45 หน้า

ข้อจำกัดสำคัญ:

- scale auto detection ยังเป็น `auto-unverified`
- ยังไม่ได้อ่าน dimension text และ scale bar อย่างสมบูรณ์
- raster/scanned PDF ยังเป็น manual assist เป็นหลัก
- test harness ยังมี cleanup noise ตอน shutdown
- `opencode.json` มี API key เป็น plaintext ต้องแก้ก่อนแชร์หรือ deploy

## Development Direction

### Phase 0: Engineering Governance and Security

เป้าหมาย: ทำให้โครงการพัฒนาต่อได้อย่างปลอดภัยและ reproducible

- ย้าย secret ทั้งหมดออกจาก repo และ rotate key ที่เคยอยู่ใน config
- เพิ่ม dependency ที่ runtime ใช้จริง เช่น `xlsxwriter` ถ้า export XLSX เป็น feature หลัก
- จัดการ build artifacts ให้ไม่ปนกับ source และไม่ถูก commit โดยไม่ตั้งใจ
- ใช้ `AGENTS.md` เป็น checklist บังคับก่อนเริ่มงานทุกครั้ง

Acceptance:

- ไม่มี secret plaintext ในไฟล์ project
- install dependencies แล้ว feature ปัจจุบันรันได้
- smoke test ผ่าน

### Phase 1: Scale and Measurement Reliability

เป้าหมาย: วัดระยะ/พื้นที่ได้แม่นและตรวจสอบย้อนกลับได้

- รวม `scale_bar_detect.py` และ dimension text extraction เข้า `/analyse`
- แสดง confidence/source ของ scale ใน UI ชัดเจน
- ทำ calibration workflow ต่อหน้าให้เร็วขึ้นและไม่ทำให้ค่าที่วัดไว้ค้าง
- เพิ่ม test สำหรับ rotation + scale + export annotations แบบตรวจละเอียดกว่าเดิม

Acceptance:

- หน้า vector PDF ที่มี scale text/dimension/scale bar ได้ confidence ที่อธิบายได้
- manual calibration override auto scale ได้
- recalibrate แล้ว summary/export เปลี่ยนตาม raw geometry เสมอ
- full test ผ่านกับ real permit PDF

### Phase 2: BMA Review Workflow

เป้าหมาย: เปลี่ยนจาก measurement tool เป็น workflow ตรวจแบบจริง

- Setup page: tag หน้า, ตั้งชื่อชั้น/หน้า, ซ่อนหน้า, project info
- Site plan tab: ที่ดิน, footprint, OSR/open area, setback, road width, FAR
- Floor plan tab: GFA, room tags, corridor width, stair distance/count
- Elevation/section tab: building height, floor height, vertical clearance
- Detail tab: stair/egress/fire escape/door/ventilation checks

Acceptance:

- ผู้ใช้เปิด PDF, tag หน้า, วัด/กรอกข้อมูล แล้วเห็น pass/fail พร้อม reference ได้
- ข้อมูลทุก tab ถูกเก็บใน `.bmaplan`
- export สรุปใช้ข้อมูลเดียวกับ UI ไม่คำนวณซ้ำคนละทาง

### Phase 3: Reports and K.1 Draft

เป้าหมาย: สรุปผลตรวจเป็นเอกสารใช้ทำงานต่อได้

- Summary page รวม pass/fail และ missing information
- Export PDF report พร้อมหน้า/ตำแหน่งอ้างอิง
- Export XLSX ที่แบ่ง sheet ตาม workflow
- Generate draft ค.1 จากรายการไม่ผ่านและข้อมูล project

Acceptance:

- รายงานอ่านได้โดยไม่ต้องเปิด app
- รายการไม่ผ่านมีค่า, เกณฑ์, reference, และหน้าอ้างอิง
- draft ค.1 สร้างจากข้อมูลที่ตรวจจริง ไม่ใช่ข้อความ generic

### Phase 4: Packaging and Deployment

เป้าหมาย: ให้ใช้งานซ้ำได้ทั้ง local และ hosted

- สรุป mode การรัน: local app, packaged executable, Render deployment
- กำหนด upload size, TTL, cleanup, logging, error reporting
- เพิ่ม release checklist และ smoke test ก่อนส่งมอบ

Acceptance:

- ผู้ใช้รัน local ได้จากคำสั่งเดียว
- hosted deployment ไม่เก็บ PDF ค้างเกิน TTL
- release ใหม่มีผล test แนบทุกครั้ง

## Next Recommended Sprint

Sprint ถัดไปควรทำ Phase 0 + เริ่ม Phase 1:

1. Security cleanup: ย้าย API key ออกจาก `opencode.json`, rotate key, ใช้ env var
2. Dependency cleanup: เพิ่ม/ล็อก dependency ที่ใช้จริง โดยเฉพาะ `xlsxwriter`
3. Scale confidence: ต่อ `scale_bar_detect.py` เข้า `/analyse` แบบไม่ทำลาย response เดิม
4. Test hardening: เพิ่ม assertion export annotation/label และลด shutdown noise
5. Documentation: อัปเดต `PROGRESS.md` และ `proto/STATUS.md` หลังแต่ละงาน

## Mandatory Reading Checklist

ก่อนเริ่มงานทุกครั้งต้องอ่าน:

- `AGENTS.md`
- `proto/STATUS.md`
- `PROGRESS.md`
- `BMA_PLAN_V2_SCOPE.md`
- `HANDOFF.md`
- source/test files ที่เกี่ยวกับงานโดยตรง

ก่อนแก้ logic กฎหมาย ต้องอ่านกฎหมาย/ประกาศต้นฉบับล่าสุดของรายการนั้นก่อน แล้วใส่อ้างอิงไว้ใน code comment, docs, หรือ report output ตามความเหมาะสม
