# BMA-Plan Idea Cards — สมมติฐานและคำถามทดสอบเชิงลึก

> หมายเหตุ: คำว่า research question (คำถามวิจัย) ในไฟล์นี้หมายถึงคำถามค้นคว้า/คำถามทดสอบผลิตภัณฑ์เพื่อพัฒนาโปรแกรม ไม่ใช่จำเป็นต้องทำเป็นงานวิจัยมหาวิทยาลัย

---

## Idea Card 01 — Scale Confidence Engine

### ชื่อไอเดีย
ระบบประเมินความน่าเชื่อถือของ scale (มาตราส่วน)

### ปัญหา
โปรแกรมวัดระยะ/พื้นที่ได้ แต่ถ้า scale ผิด ทุกค่าจะผิดหมด ปัจจุบัน auto scale ยังเป็น `auto-unverified`

### สมมติฐาน
ถ้าระบบรวม scale text, dimension text, scale bar, และ manual calibration เป็น confidence model (แบบจำลองความมั่นใจ) เดียวกัน ผู้ใช้จะเชื่อถือค่าที่วัดได้มากขึ้นและลดการ recalibrate ซ้ำ

### คำถามวิจัย/คำถามทดสอบ
1. PDF แบบก่อสร้างจริงมี scale text อยู่ตำแหน่งใดบ่อยที่สุด
2. scale text จาก title block น่าเชื่อกว่า scale bar หรือไม่
3. dimension text ใดเหมาะสำหรับ cross-check scale
4. confidence threshold เท่าไรจึงควรแสดงค่าเมตร/ตร.ม. โดยไม่เตือน
5. manual calibration ควร override auto scale ทุกกรณีหรือเฉพาะเมื่อ conflict
6. หนึ่งหน้า PDF อาจมีหลาย scale หรือไม่ และควรจัดการอย่างไร
7. ถ้า scale text กับ scale bar ขัดกัน UI ควรถามผู้ใช้แบบไหน

### Data ที่ต้องเก็บ
- page_id
- detected_scale_candidates
- source_type
- confidence
- manual_override
- final_scale
- conflict_reason

### Acceptance
- ทุกค่าที่เป็นเมตร/ตร.ม. ต้องมี scale source
- export ต้องบันทึก scale source และ confidence
- UI ต้องแสดงสถานะ scale ชัดเจน

### Skill ที่ต่อยอดได้
`pdf-scale-verification-skill`

---

## Idea Card 02 — Dimension Text Extraction

### ชื่อไอเดีย
อ่าน dimension text (ข้อความบอกระยะ) จากแบบเพื่อช่วยตรวจสอบ scale และวัดอัตโนมัติ

### ปัญหา
แบบก่อสร้างมีตัวเลขระยะจำนวนมาก แต่ระบบยังไม่ได้อ่าน/จับคู่กับเส้น dimension อย่างสมบูรณ์

### สมมติฐาน
ถ้าระบบจับคู่ dimension text กับเส้น dimension ได้ จะช่วย validate scale และสร้าง measurement suggestion (คำแนะนำการวัด) ได้เร็วขึ้น

### คำถามวิจัย/คำถามทดสอบ
1. dimension text ใน PDF จริงเป็น text layer หรือกลายเป็น vector/raster บ่อยแค่ไหน
2. ตัวเลขระยะมี pattern (รูปแบบ) ใด เช่น 5.00, 5000, 5.00 ม.
3. จะรู้ได้อย่างไรว่าตัวเลขไหนเป็น dimension ไม่ใช่เลขห้อง/เลขแบบ
4. เส้น dimension มี marker/tick/arrow รูปแบบใดบ่อยที่สุด
5. การจับคู่ text กับ line ควรใช้ proximity (ระยะใกล้), orientation (ทิศทาง), หรือ layer cue (สัญญาณจากชั้นข้อมูล)
6. ความคลาดเคลื่อนกี่เปอร์เซ็นต์จึงถือว่า scale mismatch
7. ถ้า dimension text หลายตัวขัดกัน ควรให้ผู้ใช้เลือกหรือใช้ majority vote

### Data ที่ต้องเก็บ
- text candidate
- bbox
- nearby line candidates
- orientation
- parsed value
- unit assumption
- validation result

### Acceptance
- แยก dimension text ออกจาก text ทั่วไปได้ในระดับใช้งานได้
- ใช้ cross-check scale ได้
- ไม่เอาค่าที่ไม่มั่นใจไปตัดสินผลอัตโนมัติ

### Skill ที่ต่อยอดได้
`pdf-dimension-extraction-skill`

---

## Idea Card 03 — CAD-like Snap UX

### ชื่อไอเดีย
ทำ snap experience (ประสบการณ์ดูดจุด) ให้ใกล้ CAD/Bluebeam

### ปัญหา
งานวัดแบบต้อง snap แม่นและคาดเดาได้ ถ้า snap เพี้ยนหรือจับยาก ผู้ใช้จะไม่เชื่อระบบ

### สมมติฐาน
ถ้า snap radius ปรับตาม zoom, มี visual guide, มี priority tier (ลำดับความสำคัญ), และใช้ spatial index (ดัชนีเชิงพื้นที่) ผู้ใช้จะวัดได้เร็วและผิดน้อยลง

### คำถามวิจัย/คำถามทดสอบ
1. snap type ใดจำเป็นที่สุดสำหรับงานตรวจแบบ กทม.: endpoint, midpoint, intersection, perpendicular, nearest-line, close polygon
2. snap priority ควรเรียงอย่างไรเมื่อหลายชนิดอยู่ใกล้กัน
3. radius บนหน้าจอควรกี่ px จึงจับง่ายแต่ไม่ดูดผิด
4. ตอนซูมออกควรลดจำนวน snap candidate อย่างไรไม่ให้ช้า
5. visual guide แบบใดช่วยให้ผู้ใช้เชื่อว่าระบบ snap ถูก
6. user-drawn geometry ควรเป็น snap source ทันทีหรือหลัง save
7. ควรมี toggle snap per type หรือใช้ auto priority อย่างเดียว

### Data ที่ต้องเก็บ
- snap_type
- source_geometry
- distance_to_cursor
- zoom_level
- selected_candidate
- user_cancel/undo events

### Acceptance
- snap behavior คงที่ทุก zoom
- IX/perpendicular มี logic จริง
- close polygon ใช้ง่ายทั้ง zoom เข้า/ออก
- E2E test ครอบคลุม snap หลัก

### Skill ที่ต่อยอดได้
`cad-snap-engine-skill`

---

## Idea Card 04 — Measurement Audit Trail

### ชื่อไอเดีย
เลขทุกตัวต้องย้อนกลับได้ว่าเกิดจาก object ไหน หน้าไหน scale ไหน

### ปัญหา
งานราชการต้องตรวจซ้ำได้ ถ้า export แค่ตัวเลขรวมแต่ไม่รู้ที่มา จะใช้จริงยาก

### สมมติฐาน
ถ้าทุก measurement มี audit trail (ประวัติตรวจย้อนกลับ) ผู้ใช้จะกล้าใช้ผล export ใน workflow งานจริงมากขึ้น

### คำถามวิจัย/คำถามทดสอบ
1. ผู้ใช้ต้องการ trace กลับจาก XLSX ไปยังหน้า PDF อย่างไร
2. object_id ควรแสดงใน PDF annotation หรือซ่อนใน metadata
3. audit trail ต้องเก็บ raw geometry หรือ derived value ก็พอ
4. ถ้า recalibrate หลังวัดแล้ว export เก่า/ใหม่ควรบอก version อย่างไร
5. XLSX ควรมี sheet audit แยกหรือรวมในทุก sheet
6. PDF annotation ควรใส่ label แบบใดไม่รกแบบ
7. ต้องเก็บผู้แก้ไข/เวลาแก้ไขหรือไม่

### Data ที่ต้องเก็บ
- object_id
- page
- object_type
- raw_geometry
- scale_source
- confidence
- derived_metrics
- created_at/updated_at

### Acceptance
- UI summary = JSON = CSV/XLSX = PDF annotation
- ทุกเลขใน report มี source
- recalibration ไม่ทำให้ค่าเก่าค้าง

### Skill ที่ต่อยอดได้
`measurement-audit-export-skill`

---

## Idea Card 05 — Site Plan Workflow

### ชื่อไอเดีย
workflow ตรวจผังบริเวณแบบวัดก่อน ตัดสินทีหลัง

### ปัญหา
ผังบริเวณมีข้อมูลสำคัญต่อ FAR, OSR, setback, road width แต่ถ้ารีบตัดสินกฎหมายก่อนข้อมูลครบจะเสี่ยงผิด

### สมมติฐาน
ถ้าแยก workflow เป็น measured facts (ข้อเท็จจริงที่วัดได้) ก่อน legal conclusion (ข้อสรุปทางกฎหมาย) ระบบจะใช้จริงได้ปลอดภัยกว่า

### คำถามวิจัย/คำถามทดสอบ
1. object ขั้นต่ำของ site plan คืออะไร: land, building footprint, road edge, canal, adjacent land, north arrow
2. edge tag แบบใดพอสำหรับระยะร่น: front/left/right/rear/canal/ignore
3. ผู้ใช้ควรกรอก road width เองหรือให้ระบบอ่านจากแบบ
4. setback ควรวัดจากจุดใดของ building footprint ถึงเส้นใดของ land/road
5. กรณีที่ดินไม่เป็นสี่เหลี่ยมควรเลือกเส้นอ้างอิงอย่างไร
6. ควรแสดงระยะร่นเป็นหลายจุดต่อด้านหรือระยะน้อยสุดต่อด้าน
7. จะป้องกันผู้ใช้ tag ผิดด้านได้อย่างไร

### Data ที่ต้องเก็บ
- land polygon
- building footprint polygon
- edgeTags
- reference lines
- measured setbacks
- road width source
- page/object source

### Acceptance
- ได้รายงาน “ค่าที่วัดได้” โดยไม่ตัดสินกฎหมาย
- export trace กลับหน้า PDF ได้
- พร้อมต่อ legal rule ภายหลัง

### Skill ที่ต่อยอดได้
`site-plan-measurement-workflow-skill`

---

## Idea Card 06 — Parking Marker + Report

### ชื่อไอเดีย
นับและจัดหมวดที่จอดรถจากแบบแปลน

### ปัญหา
ที่จอดรถต้องนับตามประเภทและพื้นที่/ชั้น ปัจจุบันมี marker แล้ว แต่ยังต่อยอดเป็น rule ได้อีก

### สมมติฐาน
ถ้าผู้ใช้วาง marker แล้วระบบจัดหมวด/สรุปต่อหน้า/ชั้นได้ จะลดเวลานับช่องจอดและลดความผิดพลาด

### คำถามวิจัย/คำถามทดสอบ
1. marker 1 คลิก = 1 คันพอหรือควรมี rectangle parking bay
2. ประเภทที่จอดที่ต้องใช้จริงมีอะไรบ้าง: car, EV, disabled, motorcycle, service
3. marker ควร snap กับช่องจอดหรือวางอิสระ
4. จะป้องกันการนับซ้ำอย่างไร
5. ถ้าช่องจอดอยู่หลายหน้า/หลายชั้น ควรรวมอย่างไร
6. report ควรแยกตามหน้า ชั้น ประเภท หรือทั้งหมด
7. จะต่อ rule กฎหมายอย่างไรโดยไม่ hardcode มั่ว

### Data ที่ต้องเก็บ
- parking_marker_id
- page
- floor_name
- type
- position
- linked_area
- count_group

### Acceptance
- XLSX มี sheet ที่จอดรถ
- JSON/CSV มี row parking
- PDF annotation แสดง marker ได้
- ยังไม่ตัดสิน legal requirement ถ้าไม่มี source

### Skill ที่ต่อยอดได้
`parking-count-report-skill`

---

## Idea Card 07 — Report + Draft K.1 from Real Data

### ชื่อไอเดีย
สร้างรายงานและร่าง ค.1 จากข้อมูลที่วัดจริง

### ปัญหา
ถ้าร่าง ค.1 จากข้อความ generic จะดูดีแต่ไม่ปลอดภัย ต้องมาจาก issue list ที่ตรวจได้จริง

### สมมติฐาน
ถ้าระบบสร้าง issue list จาก measured object + legal source + missing data ก่อน แล้วค่อย generate draft ค.1 เอกสารจะน่าเชื่อและตรวจย้อนกลับได้

### คำถามวิจัย/คำถามทดสอบ
1. ค.1 ต้องการ field ขั้นต่ำอะไรบ้าง
2. ข้อทักท้วงควรผูกกับ object/page/reference อย่างไร
3. ควรแยก missing information กับ non-compliance อย่างไร
4. ถ้าไม่มีข้อมูลพอ ระบบควรเขียนว่า “ข้อมูลไม่พอ” หรือไม่สร้างข้อทักท้วง
5. output ควรเป็น DOCX, PDF, หรือ Google Docs
6. เจ้าหน้าที่ต้องแก้ข้อความตรงไหนบ่อยที่สุด
7. จะเก็บ template version อย่างไร

### Data ที่ต้องเก็บ
- issue_id
- measured_value
- legal_threshold
- legal_source
- page/object reference
- severity
- draft_text
- reviewer_note

### Acceptance
- draft ค.1 ไม่ใช้ข้อความ generic ลอย ๆ
- ทุก issue มี source
- missing data ไม่ถูกสรุปเป็นไม่ผ่าน

### Skill ที่ต่อยอดได้
`permit-report-k1-draft-skill`

---

## Idea Card 08 — Agentic Development Workflow

### ชื่อไอเดีย
ทำให้ AI coding agent พัฒนาโปรเจกต์นี้โดยไม่ทำของเดิมพัง

### ปัญหา
โปรเจกต์มีทั้ง PDF geometry, UI interaction, export, law workflow ถ้าให้ agent แก้แบบไม่มีกรอบจะพังง่าย

### สมมติฐาน
ถ้าใช้ agent.md + required plan + tests + stop conditions จะทำให้การพัฒนาด้วย LLM ปลอดภัยขึ้นและลดการวนแก้บั๊กเดิม

### คำถามวิจัย/คำถามทดสอบ
1. เอกสารขั้นต่ำที่ agent ต้องอ่านก่อนแก้คืออะไร
2. acceptance criteria ควรละเอียดแค่ไหนถึงพอ
3. test ใดควรเป็น release gate
4. agent ควรห้ามแตะไฟล์ใดโดยไม่ขออนุญาต
5. เมื่อเจอ secret หรือ legal hardcode ควรหยุดอย่างไร
6. จะป้องกัน agent แก้ UI แล้ว interaction ถอยหลังได้อย่างไร
7. ควรแยก task ระดับ prompt อย่างไร: bugfix, feature, refactor, test, docs

### Data ที่ต้องเก็บ
- task type
- files changed
- tests run
- failed assertions
- behavior changed
- documentation updated

### Acceptance
- ทุกงานมี plan ก่อน patch
- ทุกงานมี test result หลัง patch
- ทุกงานอัปเดต docs เมื่อ behavior เปลี่ยน

### Skill ที่ต่อยอดได้
`bma-plan-agent-dev-skill`
