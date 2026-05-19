# เริ่มต้นใช้งาน BMA-Plan

BMA-Plan = เครื่องมือวัดพื้นที่จากแบบก่อสร้าง PDF (raster หรือ vector) สำหรับสถาปนิก/วิศวกร/เจ้าหน้าที่ตรวจ

## Workflow หลัก 6 ขั้นตอน

1. **Open PDF** — เลือกไฟล์จากเมนู `📂 เปิด PDF` (รองรับสูงสุด 256 MB; ปรับได้ผ่าน env `BMA_MAX_UPLOAD_MB`)
2. **Set Scale** — คลิกปุ่ม `Scale` แล้วคลิก 2 จุดที่รู้ระยะจริง → ใส่ระยะเป็นเมตร
3. **Page Setup** — ตั้งชื่อหน้า / ชั้น / ประเภทแบบ (`site` / `plan` / `elev` / `section`)
4. **Measure** — เลือกเครื่องมือ (Polygon / Rectangle / Circle / Path) แล้ววาดพื้นที่
5. **Review** — เปิด Summary Widget ดู warnings (มุมแหลม, area=0, opening ไม่มี parent, scale ขาด)
6. **Export** — XLSX สำหรับสรุปยื่นเขต / Annotated PDF สำหรับ markup กลับให้ผู้ออกแบบ

## รุ่น Phase 1 — ขอบเขตที่ครอบคลุม

**ทำได้:** วัดพื้นที่/ระยะ/ระบบ marker, สรุปด้วย semanticTag, summary widget, annotated PDF, .bmaplan save/load, page-scoped layers, arc-polygon (3-click inline arc).

**ไม่ทำ (Phase 1 boundary):** legal checker / OCR / AI / Rule Engine, FAR/OSR/setback pass-fail verdict, K.1 generator, auto boundary detection, multi-user/SaaS.

> Phase 1 = facts only. ระบบไม่ตัดสินว่า "ผ่าน/ไม่ผ่าน BMA review" — แสดงตัวเลขจริงเทียบกับขีดที่ user ตั้งเอง แล้วผู้ใช้ตัดสินเอง

## เริ่มต้นเร็ว 3 นาที

1. คลิก `📂 เปิด PDF` หรือ `ตัวอย่าง` (เปิด test_plan_A1)
2. คลิก `📐 Scale` → คลิก 2 จุดบน dimension line → ใส่ระยะจริงเป็นเมตร
3. คลิก `⬡ Area` → คลิกหลายจุดวาด polygon → กด `Enter` ปิดวง → ใส่ชื่อ
4. ดู status bar: `อาคาร/ห้อง X.XX ตร.ม. · สุทธิ X.XX ตร.ม.`
5. คลิก `📊 Summary Widget` → ดูสรุปครบทุก tab

## หน้าถัดไป

- [ตั้ง Scale ให้แม่นยำ](#manual/set-scale) — รายละเอียดการสอบเทียบ
- [เครื่องมือวัด](#manual/measure-tools) — Polygon, Rectangle, Circle, Path, Arc-polygon
- [การ Export](#manual/export) — XLSX, Annotated PDF, .bmaplan project file
- [Zen Mode + Command Palette](#manual/zen-mode) — โหมด chrome-hide + ค้นหน้าด้วย Ctrl+K
- [Keyboard Shortcuts](#manual/keyboard-shortcuts) — คีย์ลัดทั้งหมด

## ขอความช่วยเหลือ

- พบบั๊ก / มีคำถาม: ดู `docs/process/TROUBLESHOOTING.md` หรือดู Dev Log สำหรับ session ล่าสุด
- ต้องการเพิ่มหน้าใหม่ในคู่มือ: เพิ่ม markdown ใน `proto/manual/` แล้วรัน `python scripts/build_docs.py`
