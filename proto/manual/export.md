# การ Export

BMA-Plan มี export 5 รูปแบบ — เลือกตามผู้รับและจุดประสงค์

## 1. XLSX Report (เต็มรายละเอียด)

**ปุ่ม:** Export panel → `📊 Export XLSX`
**ไฟล์:** `<projectname>_report.xlsx` (4-6 sheets)

โครงสร้าง sheet:
- `Page Scales` — รายชื่อ scale ทุกหน้า + สถานะ (manual / auto-unverified / unknown)
- `Objects` — ทุก polygon + opening + parking + reference (พร้อม 5 metadata columns: measurementProfile, objectCategory, reportTarget, lawBasis, countingRule)
- `Areas by Page` — สรุปพื้นที่ตามหน้า
- `Report Target Summary` — สรุปตาม `reportTarget` (e.g. GFA, Building Footprint, Open Space)

**ใช้กับ:** ส่งให้วิศวกรโครงสร้าง / ผู้ตรวจสอบกฎหมาย / รวมเข้าระบบบัญชี-ปริมาณ

## 2. 1-Page Excel Summary (สรุปสั้น)

**ปุ่ม:** Export panel → `⬇ Export Summary (1 หน้า)`
**ไฟล์:** `<projectname>_summary.xlsx` (1 sheet, A4 landscape, fit-to-page)

แสดง:
- พื้นที่รวม 7 site `semanticTag` (ปกคลุมอาคาร, ที่ว่าง, ซึมน้ำ, hardscape, softscape, จอดรถนอกอาคาร, ถนนภายใน)
- ratios: BCR, OSR, FAR, Permeable% (ตัวเลขดิบ + limit ที่ user ตั้ง — ไม่มี verdict)
- setback 4 ทิศทาง (front, back, side1, side2) — คำนวณจาก land-edge roles
- count markers ทุกประเภท

**ใช้กับ:** เอกสารส่ง BMA แบบ 1 หน้า / ภาพรวมสำหรับ stakeholder

> ⚠ Phase 1 boundary: ไม่มี pass/fail verdict — ตัวเลขดิบเท่านั้น

## 3. Annotated PDF — current page

**ปุ่ม:** Export panel → `📄 Export หน้าปัจจุบัน + Annotations`
**ไฟล์:** `<projectname>_p<pagenum>.pdf`

PDF หน้าปัจจุบัน 1 หน้า + วาด annotation (polygons, labels, dimensions, comments) ทับลงไป

**ใช้กับ:** markup ส่งกลับให้ designer / เก็บเป็นหลักฐานการตรวจ

## 4. Annotated PDF — all pages

**ปุ่ม:** Export panel → `📚 Export ทุกหน้า + Annotations`
**ไฟล์:** `<projectname>_all_annotated.pdf`

ทุกหน้าใน PDF ต้นฉบับ + annotation ทุกหน้า รวมในไฟล์เดียว

**ใช้กับ:** ส่ง consultant / archive โครงการเต็มชุด

## 5. Save Annotated PDF in-place (เขียนทับไฟล์ต้นฉบับ)

**เมนู:** Project → `📄 Save PDF (ทับไฟล์เดิม)` (`Ctrl+Shift+S`)
**ไฟล์:** ทับ `<source>.pdf` ที่เปิดอยู่ (หรือ fallback download `<source>_annotated.pdf`)

ใช้ File System Access API — ต้องเปิด PDF ผ่าน `📂 เปิด PDF` (FSAPI handle) ก่อน

**ใช้กับ:** workflow ที่ user รักษาไฟล์เดียวกันแล้วเพิ่ม annotation ต่อเนื่อง

## 6. Project File `.bmaplan`

**ปุ่ม:** Project → `💾 Save` (`Ctrl+S`) หรือ `Save As`
**ไฟล์:** `<projectname>.bmaplan` (JSON v1)

เก็บทุกอย่าง: polygons, openings, references, parking, page tags, project info, site orientation, page scales, excluded pages.

**ใช้กับ:** เปิดต่อ / share กับเพื่อนร่วมงาน / backup

> Schema additive — ไฟล์เก่าโหลดได้, ไฟล์ใหม่มี field เพิ่ม (เช่น `obj.edges[]` สำหรับ arc-polygon)

## รายการ Export อื่น (CSV/JSON)

- **CSV:** Export panel → `📋 Export CSV` (ตาราง flat รวมทุก object)
- **JSON:** Export panel → `📄 Export JSON` (เหมือน CSV แต่ structured)

ทั้งสองใช้กับ pipeline / scripts ภายนอก

## ขั้นตอนก่อน Export

1. ตั้ง Scale ทุกหน้าที่ต้องวัด
2. รัน `Validate All Polygons` (เมนู Object หรือคีย์) — เช็คมุมแหลม, ตัดกันเอง, area=0
3. ตรวจ Warnings widget — เคลียร์ทุก ⚠ ก่อน export
4. ดู Summary Widget แต่ละ tab — ตรวจตัวเลขก่อนส่ง
