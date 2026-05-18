# BMA-Plan Review — รีวิวโปรแกรมเพื่อพัฒนาต่อ

---

## 1. Verdict (คำตัดสินตรง ๆ)

โปรแกรมนี้มีแกนที่ดีแล้ว แต่ยังอยู่คนละครึ่งระหว่าง “เครื่องมือวัดแบบจริง” กับ “ระบบตรวจแบบอัตโนมัติ”

ถ้าพัฒนาถูกทาง มันควรเป็น **Bluebeam-lite สำหรับงานอนุญาต กทม.** ไม่ใช่ AI checker (ระบบ AI ตรวจแบบ) ที่รีบตัดสิน pass/fail โดยข้อมูลยังไม่ครบ

ข้อดีใหญ่:

- แก้ปัญหาเดิมของ Google Apps Script (สคริปต์กูเกิลแอปส์) ได้ถูกทาง
- backend (ฝั่งประมวลผลหลังบ้าน) แข็งขึ้นมากจาก case_id, upload guard, PDFium, degraded mode
- measurement workflow (workflow การวัด) เริ่มใช้งานจริงได้
- export XLSX/PDF annotation ทำให้ผลลัพธ์ไม่ติดอยู่ในหน้าจอ
- มี E2E tests (ทดสอบ end-to-end) กับไฟล์จริง

ข้อเสียใหญ่:

- scale/dimension extraction ยังเป็นคอขวด
- UI ยังเสี่ยงถอยหลังถ้าปรับ compact (ย่อส่วน) เกินไป
- rule กฎหมายยังไม่ควรแตะลึกถ้ายังไม่มี source ต้นฉบับ + data model ที่รองรับ
- ยังไม่มี release discipline (วินัยการปล่อยเวอร์ชัน) แบบจริงจัง

---

## 2. Product Positioning (ตำแหน่งผลิตภัณฑ์)

### ไม่ควรขายตัวเองว่า

> ระบบตรวจแบบกฎหมายอัตโนมัติเต็มรูปแบบ

เพราะตอนนี้ยังไม่พร้อมเรื่อง:

- อ่าน scale/dimension ทั้งหมดเอง
- เข้าใจ semantic entity (หน่วยความหมายในแบบ) เช่น ห้อง, ทางเดิน, บันได, เขตที่ดิน
- map กับกฎหมายหลายฉบับ
- ให้เหตุผล pass/fail แบบรับผิดชอบได้

### ควรนิยามว่า

> เครื่องมือวัดและจัดโครงข้อมูลจาก PDF แบบก่อสร้าง เพื่อช่วยเจ้าหน้าที่/วิศวกรตรวจแบบเร็วขึ้น ตรวจซ้ำได้ และสร้างรายงานได้

นี่แม่นกว่าและขายต่อได้จริงกว่า

---

## 3. What We Learned (เราได้เรียนรู้อะไรจากการทำแบบนี้)

### Lesson 1 — อย่าเริ่มจาก AI ให้เริ่มจาก geometry (เรขาคณิต)

งานตรวจแบบไม่ได้เริ่มจากให้ AI ตอบว่า “ผ่าน/ไม่ผ่าน”  
มันเริ่มจากคำถามพื้นฐานกว่า:

- เส้นนี้ยาวเท่าไร
- พื้นที่นี้เท่าไร
- ช่องเปิดหักออกเท่าไร
- พื้นที่นี้เป็น GFA หรือ non-GFA
- ระยะนี้วัดจากเส้นอ้างอิงไหน
- หน้านี้มี scale ที่เชื่อได้หรือไม่

ถ้าวัดยังไม่นิ่ง AI จะมั่วด้วยความมั่นใจสูง

### Lesson 2 — PDF แบบก่อสร้างไม่ใช่รูปภาพธรรมดา

PDF มีหลายโลกซ้อนกัน:

- vector geometry (เส้นเวกเตอร์)
- raster image (ภาพสแกน)
- text layer (ชั้นข้อความ)
- page rotation (การหมุนหน้า)
- coordinate transform (การแปลงพิกัด)
- scale notation (ข้อความมาตราส่วน)

ดังนั้นเครื่องมือที่ดีต้องรู้ว่าแต่ละหน้ามีข้อมูลแบบไหน และต้องบอกผู้ใช้เมื่อ “manual only”

### Lesson 3 — scale คือแกนกลาง ไม่ใช่ feature เสริม

ถ้า scale ผิด ทุกอย่างผิด:

- ระยะผิด
- พื้นที่ผิด
- FAR/OSR ผิด
- ระยะร่นผิด
- รายงานผิด
- ค.1 ผิด

ดังนั้น scale ต้องมี source/confidence และ manual override

### Lesson 4 — UI งานวิศวกรรมต้องเหมือนเครื่องมือ ไม่ใช่ landing page (หน้าเว็บโฆษณา)

งานวัดแบบต้องการ:

- wheel zoom
- pan ลื่น
- snap predictability
- label อ่านง่าย
- toolbar ที่เข้าใจทันที
- undo/redo ในอนาคต
- keyboard shortcut

UI สวยแต่ใช้วัดช้าคือพัง

### Lesson 5 — Tests สำคัญกว่าคำบอกว่า “แก้แล้ว”

โปรเจกต์นี้เริ่มมี smoke/full test ซึ่งถูกทางมาก เพราะงานแบบนี้พังง่ายจาก:

- rotation
- scale recalibration
- multi-page persistence
- export annotation
- stale response
- snap engine

ถ้าไม่มี regression test จะวนแก้บั๊กเดิมไม่จบ

### Lesson 6 — อย่าเอากฎหมายเข้าก่อน data model พร้อม

กฎหมายควบคุมอาคารไม่ใช่แค่ if/else  
ต้องมีข้อมูลขั้นต่ำ:

- ประเภทอาคาร
- การใช้ประโยชน์
- ความกว้างถนน
- ความสูง
- พื้นที่อาคาร
- ระยะร่น
- จำนวนที่จอดรถ
- เงื่อนไขพื้นที่/ผังเมือง/ข้อยกเว้น

ดังนั้น rule engine ต้องมาหลัง measurement + semantic tagging

---

## 4. Strengths (จุดแข็ง)

| จุดแข็ง | ทำไมสำคัญ |
|---|---|
| case_id isolation (แยกเคสด้วยรหัสเคส) | ป้องกัน PDF หลายไฟล์ชนกัน |
| raw geometry recalculation (คำนวณใหม่จากเรขาคณิตดิบ) | recalibrate แล้วค่าไม่ค้าง |
| PDFium snap engine (ระบบดูดจุดจาก PDFium) | ทำให้ใกล้เครื่องมือ CAD มากขึ้น |
| manual calibration (สอบเทียบมือ) | รับมือ PDF ที่อ่าน scale ไม่ได้ |
| export XLSX/PDF annotations | ส่งต่อใช้งานราชการได้ |
| real permit PDF test | ไม่ใช่ทดสอบกับไฟล์ของเล่นอย่างเดียว |
| degraded raster mode | บอกผู้ใช้เมื่อ PDF ไม่มี vector geometry |

---

## 5. Weaknesses (จุดอ่อน)

| จุดอ่อน | ความเสี่ยง | วิธีแก้ |
|---|---|---|
| auto scale ยังไม่ verified | วัดผิดทั้งระบบ | confidence + source + manual override |
| dimension text ยังไม่อ่านครบ | ตรวจระยะยาก | OCR/text extraction เฉพาะ dimension line |
| raster PDF manual assist | ไฟล์สแกนใช้งานจำกัด | เพิ่ม raster calibration + visual guides |
| annotation test ยังไม่ exact | export อาจพลาดแต่ test ผ่าน | ตรวจ label/object/position ละเอียดขึ้น |
| UI compact เกินไป | ใช้งานจริงช้า | tool-first UI, label ชัด, shortcut |
| legal rule ยังเสี่ยงมั่ว | ความรับผิดชอบสูง | primary-source only + explainable rule |

---

## 6. Development Strategy (ยุทธศาสตร์พัฒนาต่อ)

### Strategy A — Measurement Kernel First (ทำแกนวัดให้แน่นก่อน)

ต้องมี kernel (แกนกลาง) ที่ตอบได้:

- input geometry คืออะไร
- scale มาจากไหน
- confidence เท่าไร
- object นี้อยู่หน้าไหน
- export row นี้มาจาก object ไหน
- recalibrate แล้วค่าทั้งหมดเปลี่ยนถูกไหม

### Strategy B — Workflow Layer Second (ค่อยทำ workflow)

หลังวัดนิ่ง ให้สร้าง workflow:

1. tag หน้า
2. tag object
3. group ตามชั้น/ประเภทงาน
4. map object กับรายการตรวจ
5. generate report

### Strategy C — Rule Engine Last (ตรวจเกณฑ์ทีหลัง)

rule engine ต้องใช้หลัก:

```text
measured value + source page + legal source + condition + conclusion
```

ไม่ใช่:

```text
AI says pass/fail
```

---

## 7. Recommended Next Sprint (สปรินต์ถัดไป)

### Sprint 1 — ทำให้ scale น่าเชื่อ

Tasks:

1. รวม scale_bar_detect.py เข้า `/analyse`
2. เพิ่ม scale source model:
   - manual
   - title_block_text
   - scale_bar_graphic
   - dimension_cross_check
   - unknown
3. เพิ่ม confidence score
4. UI แสดง badge:
   - manual verified
   - auto high confidence
   - auto-unverified
   - unknown/manual only
5. เพิ่ม E2E test:
   - recalibrate แล้วค่า export เปลี่ยน
   - rotation แล้ว annotation ไม่เพี้ยน
   - real permit PDF หน้าที่มี/ไม่มี scale

Acceptance:

- ไม่มีค่าเมตร/ตร.ม. ที่ไม่มี scale source
- manual override ชนะ auto scale
- full test ผ่าน

### Sprint 2 — ทำ report traceability

Tasks:

1. ทุก export row ต้องมี object_id, page, source_scale, confidence
2. XLSX เพิ่ม sheet `Audit Trail`
3. PDF annotation ใส่ label object_id แบบย่อ
4. JSON export เก็บ raw geometry + derived metrics

Acceptance:

- เปิด XLSX แล้วตรวจย้อนกลับได้ว่าเลขนี้มาจากหน้าไหน/object ไหน
- UI summary = XLSX summary = JSON derived value

### Sprint 3 — ทำ workflow site plan

Tasks:

1. object type: land, building_footprint, road_reference, canal_reference
2. edge tag: front/left/right/rear/canal/ignore
3. setback calculation เฉพาะ measured distance ยังไม่ตัดสินกฎหมาย
4. report ระยะร่นแบบ “ค่าที่วัดได้” ก่อน

Acceptance:

- ยังไม่บอกผ่าน/ไม่ผ่านถ้าไม่มี legal rule source
- แสดงค่าที่วัดได้ + หน้า + object source

---

## 8. Review Score (คะแนนรีวิว)

| ด้าน | คะแนน | เหตุผล |
|---|---:|---|
| แนวคิดผลิตภัณฑ์ | 8/10 | ปัญหาจริง ใช้งานราชการจริงได้ |
| สถาปัตยกรรมล่าสุด | 7.5/10 | backend ดีขึ้นมาก แต่ยังต้องแยก frontend/backend ให้สะอาดขึ้น |
| ความแม่นการวัด | 6.5/10 | manual ใช้ได้ แต่ auto scale ยังไม่สุด |
| UX งานวัดแบบ | 6.5/10 | feature เริ่มครบ แต่ต้องระวัง UI ถอยหลัง |
| Test discipline | 7/10 | มี smoke/full แล้ว ควรทำ CI/release gate |
| ความพร้อม deploy | 4.5/10 | ต้อง cleanup secret, packaging, logging, TTL |
| ความพร้อมใส่กฎหมาย | 3.5/10 | ยังไม่ควรรีบจนกว่าข้อมูลวัด/semantic พร้อม |

สรุป: **ควรพัฒนาต่อ แต่ต้องคุม scope ให้โหด**

---

## 9. Final Recommendation (ข้อเสนอสุดท้าย)

ทำ BMA-Plan เป็น 3 ชั้น:

```text
Layer 1: Measure Engine
- scale
- snap
- geometry
- measurement
- export traceability

Layer 2: Permit Workflow
- page tagging
- object tagging
- site/floor/elevation/detail tabs
- reports

Layer 3: Legal Reasoning
- primary source law
- rule condition
- pass/fail with citation
- draft K.1
```

อย่าข้าม Layer 1 ไป Layer 3  
ถ้าข้าม จะได้ระบบที่ดูฉลาดแต่เชื่อไม่ได้
