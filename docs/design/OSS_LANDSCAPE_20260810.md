# สำรวจโลก Open-Source สำหรับ BMA-Plan — 2026-08-10

ที่มา: user ถาม "มี open source บ้างไหม" · สำรวจโดย `bma-researcher` 6 หมวด · **หมายเหตุ: บล็อกนี้มีคำวินิจฉัยของ orchestrator (Opus/Fable) กำกับทุกข้อ — ไม่ใช่การรับรายงาน researcher มาทั้งดุ้น**

## 🔴 ข้อค้นพบเร่งด่วนที่สุด: PyMuPDF เป็น AGPL และเราเพิ่งสร้างช่องทางแจกจ่าย

- `PyMuPDF (fitz)` = **AGPL-3.0 หรือ commercial (dual license)** — เราใช้เป็นแกน server ทั้ง proto และ lite
- เมื่อวาน (2026-08-10) เรา ship **PKG-PORTABLE** ซึ่ง**บรรจุ PyMuPDF ลงในโฟลเดอร์ที่ตั้งใจแจกให้เจ้าหน้าที่** — การแจกจ่าย binary ที่มี AGPL ก่อให้เกิดภาระเปิดเผย source ตามสัญญาอนุญาต
- ความเสี่ยงจริงแค่ไหนขึ้นกับ "แจกในหน่วยงานเดียวกัน vs ข้ามหน่วยงาน/สาธารณะ" — **ต้องให้ user ตัดสิน ไม่ใช่เดา**
- ทางเลือกถ้าต้องเลี่ยง AGPL: `pypdfium2` (Apache-2.0/BSD — เราใช้อยู่แล้วใน proto สำหรับ vector snap) + `PDF.js` (Apache-2.0) ครอบคลุม render/ผ่าหน้าได้เกือบทั้งหมด · ส่วนที่ PyMuPDF ทำแล้วตัวอื่นทำแทนยาก = การ bake annotation ลง PDF
- **Action:** file เป็นการ์ด `LICENSE-AUDIT` (ดู PHASE_INDEX)

## ❌ ข้อเสนอที่ orchestrator ปฏิเสธ: "เอา flatten-js แทน polyAreaM2"

researcher จัดให้เป็น Tier-1 อันดับ 1 (MIT, 80KB, arc area แม่นแบบ closed-form) — **ปฏิเสธ** ด้วย 3 เหตุผล:

1. `polyAreaM2` เป็น **forbidden surface**: vendored byte-identical จาก proto, sha256-pinned ใน `check_executable_truth`, และล็อกด้วย `test_measure_parity.py` — การสลับไป lib ทำลาย**สัญญา vendoring ทั้งระบบ** และทำให้ `.bmaplan` เปิดข้าม proto↔lite แล้วได้ตัวเลขไม่ตรงกัน
2. คณิตที่จะแทนคือ **shoelace ระดับมัธยม ที่ไม่มีบั๊ก** และผ่าน property-based test ~500 เคส (I3) — เปลี่ยนของที่พิสูจน์แล้วเพื่อได้ dependency 80KB = trade ที่ขาดทุน
3. researcher เขียนเองว่า "full test re-baseline required" — นั่นแปลว่าเสนอให้ทิ้ง baseline ที่เป็นหลักประกันความถูกต้องของทั้งโปรเจกต์

> บทเรียน: รายงานวิจัยที่ไม่รู้ข้อจำกัดภายในจะเสนอสิ่งที่ดู "ถูกหลักวิศวกรรม" แต่ผิดกติกาโปรเจกต์ — orchestrator ต้องกรองเสมอ

## ✅ ของที่ควรรับมาใช้จริง

| ลำดับ | ตัว | license | ใช้กับการ์ดไหน | cost |
|---|---|---|---|---|
| 1 | **PaddleOCR** | Apache-2.0 ✅ | **Track AI** — เป็น OCR ตัวเดียวที่อ่านไทยได้ดีจริง (ราว 82% เทียบ Tesseract ~40% ตามรายงาน — ยังไม่ verify เอง) และ**รัน local ได้** | M |
| 2 | **Clipper2** | Boost ✅ | wall-trace / Compare revisions (boolean หักช่องเปิด, area delta) | L — ยังไม่ใช่ตอนนี้ |
| 3 | **odiff** | MIT ✅ | Compare revisions (diff ภาพ เร็วกว่า pixelmatch 5-8×) | S |
| 4 | **OpenCV / opencv.js** | BSD ✅ | wall-trace (Hough/LSD), Compare revisions (auto-registration) | M |

**PaddleOCR ตอบคำถามนโยบายที่ค้างอยู่:** local model ที่อ่านไทยได้ดีมีจริง → Track AI ไม่จำเป็นต้องส่งภาพออก cloud อย่างน้อยในชั้น OCR

## 🔎 ต้องตรวจสอบก่อนเชื่อ

**OpenTakeoff** (อ้างว่า Apache-2.0, browser, one-click room detection, ขับด้วย AI agent ได้, 2026) — ถ้าจริงคือ prior art ระดับแอปทั้งตัวตัวเดียวในโลก open source **แต่ผมยังไม่ได้เปิดดู repo จริง** อย่าเพิ่งวางแผนบนสมมติฐานนี้จนกว่าจะเห็นของ (ดูจำนวน commit/issue/ผู้ใช้จริง)

## ❌ ข้อค้นพบเชิงลบ (มีค่าพอๆ กับข้อบวก)

- **ไม่มี pipeline "แบบสแกน → polygon" แบบ open source ที่โตพอ** → `centerline-snap` ที่เราเขียนเองไม่ได้ล้าหลัง เป็นระดับเดียวกับที่โลกมี
- **ไม่มีโมเดล AI อ่านแบบแปลนที่ใช้กับแบบไทยได้ทันที** — CubiCasa5k เทรนบนแบบสถาปัตย์ฟินแลนด์ที่สะอาด, FloorPlanCAD เป็น CAD vector, VLM local ทุกตัวอ่อนภาษาไทย → Track AI ขั้นวาด polygon = greenfield จริง ต้องเดินแบบ eval-first ตามที่วางไว้
- **ไม่มีเครื่องมือ Compare-revisions พร้อม registration ใน open source** → ยืนยันว่าแนวทาง (a) ที่ค้าง checkpoint เป็นงานประดิษฐ์จริง

## สรุปที่ใช้ตัดสินใจได้

1. เรื่องที่ต้องทำ: **ตัดสินเรื่อง AGPL ของ PyMuPDF** ก่อนแจกโฟลเดอร์ portable ให้ใครนอกทีม
2. เรื่องที่ห้ามทำ: อย่าเปลี่ยน measure engine ไปใช้ lib
3. เรื่องที่ปลดล็อกได้: Track AI มีทางเดินแบบ local-only แล้ว (PaddleOCR)
