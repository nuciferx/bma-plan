# Spike — 45-page permit measurement walkthrough (lite)

- **Started**: 2026-05-23
- **Source PDF**: `20250616_RAMA4 APARTMENT PERMIT rev 1.pdf` (45 หน้า, A1 landscape, rotation=90°)
- **Sandbox**: `lite/sandbox/invent-45page-permit-spike.html` (1 ไฟล์, interactive — Pages tab + Report tab)
- **Survey raw**: `artifacts/permit-45p-survey.json` (text extract ต่อหน้า)
- **Trigger**: ผู้ใช้ถามว่า lite รับ case "PDF 10+ หน้า ผังบริเวณ + ชั้น 1-4 + section/detail" ได้อย่างไร → spike นี้ตอบด้วยไฟล์ permit จริง 45 หน้า

## TL;DR

**ใน 45 หน้าของ permit นี้ มีเพียง 9 หน้าที่ต้องวัดพื้นที่จริง** (20%) — ที่เหลือ 36 หน้าเป็น cover / legend / section / detail / schedule / notes / restroom-enlargement. lite รับ case นี้ได้โดยไม่ต้องแก้ schema/model — โครงสร้าง `PS[n]` per-page + `LAYERS` global + `pageTags`/`pageFloorKind`/`pageFloorNum` ครอบคลุมพอดี. gap เดียวที่ค้างคือ aggregator "GFA แยกชั้น" ในรายงาน (group-by `pageFloorNum`).

## 1. หน้าที่วัดพื้นที่ (9 หน้า, manual classification)

| Page | Tag      | Floor   | สิ่งที่วัด                                 | Layer ที่ผูก            |
|-----:|----------|---------|--------------------------------------------|-------------------------|
| 5    | site     | —       | ที่ดิน + setback (boundary view)            | `site_land`, `site_setback` |
| 7    | site ★   | —       | ที่ดิน + อาคารปกคลุม 839.10 m² + setback   | `site_land`, `site_cover` |
| 8    | site     | —       | ขอบเขตอาคาร + setback (alt view, cross-check) | `site_land` (verify)  |
| 11   | floor    | 1       | GFA ชั้น 1 (Ground — โถงพักคอย/ห้องรับรอง) | `gfa_l1`, `ded_lift`    |
| 12   | floor    | 2       | GFA ชั้น 2 (ห้องพัก 211-)                   | `gfa_l2`, `use_resid`   |
| 13   | floor    | 3       | GFA ชั้น 3 (ห้องพัก 311-)                   | `gfa_l3`, `use_resid`   |
| 14   | floor    | 4       | GFA ชั้น 4 (ห้องพัก 411-)                   | `gfa_l4`, `use_resid`   |
| 15   | floor    | 5       | GFA ชั้น 5 (door layout overlay)            | `gfa_l5`, `use_resid`   |
| 16   | floor    | roof    | GFA ดาดฟ้า / Roof deck                      | `gfa_rd`                 |

★ = primary site sheet — มีตัวเลขชี้ชัด "839.10 ตารางเมตร" บน drawing

## 2. หน้าที่ไม่วัด (36 หน้า)

| Range            | จำนวน | ประเภท              | ทำไมไม่วัด                                   |
|------------------|------:|---------------------|----------------------------------------------|
| p1               | 1     | cover / DRAWING SET | สารบัญแบบ ไม่มี geometry                     |
| p3, p4           | 2     | legend, fixtures    | สัญลักษณ์ / มาตรฐานสุขภัณฑ์                  |
| p6               | 1     | sanitary            | แบบระบบสุขาภิบาล (วัดไม่ใช่พื้นที่)          |
| p9, p18-21, p35-37 | 8   | section / elevation | รูปตัด / รูปด้าน — วัด height ได้แต่ไม่ใช่ area |
| p10, p38         | 2     | notes / title block | ไม่มี geometry                                |
| p17              | 1     | roof plan           | แปลนหลังคา (มัก exclude จาก GFA)             |
| p22-26           | 5     | restroom enlarge    | แปลนขยายห้องน้ำ (option ตรวจ fixture)        |
| p27-29           | 3     | stair               | แปลนบันได + รายละเอียด                       |
| p30-31           | 2     | lift / detail       | LS-01 lift shaft enlarge                     |
| p32-34           | 3     | door/window schedule| ตารางประตู/หน้าต่าง (ไม่ใช่ plan)            |
| p39-45           | 7     | detail              | RL01, RL02, DT01, DT04, A10_05, FC01, FC02   |

Tag system ที่ใช้ใน spike (13 tag): `cover, site, floor, roof, section, restroom, stair, detail, schedule, notes, legend, fixtures, sanitary`.

## 3. ทำใน lite ปัจจุบันได้กี่ %?

ตรวจฟิลด์ที่มีจริงใน `ui-lite.html`:

| Capability needed                          | lite มี?    | ที่เก็บ                              |
|--------------------------------------------|------------|--------------------------------------|
| Per-page object storage                    | ✅          | `PS[n].objects[]`                    |
| Per-page scale (1:500 site, 1:100 floor)   | ✅          | `PS[n].scale.pts_per_m`              |
| Page tag (cover/site/floor/section/…)      | ✅          | `pageTags[n]` (`PAGE_TAGS` enum)     |
| Floor kind (normal/basement/rooftop)       | ✅          | `pageFloorKind[n]`                   |
| Floor number (1, 2, …, roof)               | ✅          | `pageFloorNum[n]`                    |
| Page name (auto "ชั้น N")                  | ✅          | `pageNames[n]` + `autoNamePage()`    |
| Excluded pages from totals                 | ✅          | `excluded[n]`                        |
| Layer pool (gfa/use/ded/site/open/count)   | ✅          | `LAYERS[]` (global) + custom L2c     |
| Sublayer tree (folder + nest)              | ✅          | `FOLDERS[]` + `parentId` (L3)        |
| Roll-up Σ ต่อ folder                       | ✅          | `rollupArea()` (LST-3b)              |
| Named report variables (FAR/OSR/coverage)  | ✅          | `doc.reportVars` (LRV)               |
| **GFA แยกชั้นในรายงาน**                    | ❌ **gap**  | ปัจจุบัน LRV รวมต่อ layer ไม่แตก per-floor |

**ทำได้ทันที: 11/12 capability.** ที่ค้างเพียงอย่างเดียวคือ aggregator แตก floor — ไม่ใช่ schema change.

## 4. โครงสร้าง storage สำหรับ permit นี้ (เป้าเขียนลง `.bmaplan`)

```
projectInfo  = {name:"RAMA4 APARTMENT", address:"ถนนพระราม 4 ซอยจอมสมบูรณ์", ...}

pageTags     = {1:"cover", 2:"site", 3:"legend", 4:"fixtures", 5:"site", 6:"sanitary",
                7:"site",  8:"site",  9:"section", 10:"notes",
                11..16:"floor",  17:"roof", 18..21:"section", 22..26:"restroom",
                27..29:"stair", 30..31:"detail", 32..34:"schedule",
                35..37:"section", 38:"notes", 39..45:"detail"}
pageFloorKind= {11:"normal", 12:"normal", 13:"normal", 14:"normal", 15:"normal", 16:"rooftop"}
pageFloorNum = {11:1, 12:2, 13:3, 14:4, 15:5}                  // rooftop ไม่ต้องมีเลข
pageNames    = auto = {11:"ชั้น 1", 12:"ชั้น 2", ..., 16:"ดาดฟ้า"}
excluded     = {2:true}                                          // p2 = location-only, ไม่นับ

PS[5,7,8]    = {scale:{1:500}, objects:[poly site_land, poly site_cover, lines setback]}
PS[11..15]   = {scale:{1:100}, objects:[poly gfa_l*, openings ded_lift, ...]}
PS[16]       = {scale:{1:100}, objects:[poly gfa_rd]}
PS[ทุกหน้าอื่น] = {scale:null, objects:[]}                       // ว่าง

LAYERS       = [site_land, site_cover, site_setback, gfa(generic), ded_lift, ded_stair,
                use_resid, use_lobby, use_wc, cnt_rooms, cnt_park]   // global pool
FOLDERS      = [F_site, F_gfa, F_ded, F_use, F_count]                // 5 folder

doc.reportVars = [
  {id:"v_land",  name:"ที่ดิน",        unit:"m²",  ref:"layer:site_land"},
  {id:"v_cover", name:"อาคารปกคลุม",   unit:"m²",  ref:"layer:site_cover"},
  {id:"v_gfa",   name:"GFA รวม",       unit:"m²",  ref:"folder:F_gfa"},      // roll-up
  {id:"v_open",  name:"ที่ว่าง",       unit:"m²",  expr:"v_land - v_cover"},
  {id:"v_cov",   name:"Coverage",      unit:"%",   expr:"v_cover / v_land * 100"},
  {id:"v_far",   name:"FAR",           unit:"",    expr:"v_gfa / v_land"},
  {id:"v_osr",   name:"OSR",           unit:"%",   expr:"v_open / v_gfa * 100"},
]
```

**ทุก field ข้างบนมีอยู่แล้วใน lite schema** ไม่ต้องเพิ่ม. ส่วน `pageTags` enum (`PAGE_TAGS`) ปัจจุบันรองรับ floor/site/excluded — ถ้าอยากมี cover/legend/section/detail/schedule/restroom/stair เป็น tag ของตัวเอง = แค่เพิ่มสมาชิกใน enum (ไม่กระทบ schema, additive).

## 5. โครงสร้างรายงาน (mockup)

ดู Report tab ใน sandbox. 6 section:

1. **ข้อมูลโครงการ** — ที่ตั้ง, ประเภท, ที่ดิน, หน้าที่ใช้คำนวณ (9/45)
2. **ผังบริเวณ — Site Coverage** — ที่ดิน / อาคารปกคลุม / ที่ว่าง / coverage % + ตาราง setback 5 ด้าน
3. **GFA Breakdown ต่อชั้น** — ตาราง 6 row (ชั้น 1-5 + ดาดฟ้า) × คอลัมน์ {การใช้งาน, หน้า, gross, หัก, net} + แถวรวม
4. **ตัวเลขควบคุม (Derived)** — FAR / Coverage / OSR (มาจาก `reportVars` expr)
5. **จำนวนนับ (Counts)** — ห้องพัก/โถงลิฟต์/ห้องน้ำส่วนกลาง
6. **Traceability** — list หน้าที่นับ (9 pill) + list หน้าที่ไม่นับ (36 pill สีแดง) — ตรวจสอบได้ว่าหน้าไหนถูก exclude เพราะอะไร

ส่วน Traceability สำคัญ — เป็นเหตุผลที่เก็บ `pageTags` แม้กับหน้าที่ไม่วัด (audit trail).

## 6. Finding & Gap

### A. โครงสร้าง lite ปัจจุบันรับได้

หลักการ 3 มิติของ lite (object×page × layer × pageMetadata) จับ case 45 หน้าได้ลงตัวพอดี. **ไม่มี case ที่ต้อง page-scoped layer** สำหรับ permit ที่ทดสอบ — สี gfa เหมือนกันทุกชั้นตามมาตรฐาน drawing.

### B. Gap ที่เจอ (เรียงตาม impact)

| # | Gap                                                | Severity | แก้ที่ไหน                          | ไม่กระทบ schema? |
|---|----------------------------------------------------|----------|------------------------------------|------------------|
| 1 | LRV ไม่แตก GFA แยกชั้น (รวม layer เดียวทั้ง 6 ชั้น) | medium   | `report-vars.js` `computeReportVars` — เพิ่ม group-by `pageFloorNum` | ✅ aggregator-only |
| 2 | `PAGE_TAGS` enum ปัจจุบันไม่ครบ — ขาด cover/legend/section/detail/schedule/restroom/stair | low      | `ui-lite.html` `PAGE_TAGS` ค่าคงที่ — append additive | ✅ enum string, additive |
| 3 | ไม่มี bulk-tag UI (45 หน้า ตั้ง tag ทีละหน้าน่าเบื่อ) | low-med  | Sheets tab — เพิ่ม batch select + apply | ✅ UI-only |
| 4 | ไม่มี auto-classifier (จาก text content) — heuristic ใน spike ของ python script | low      | optional — `lite/static/js/auto-tag.js` ใหม่ | ✅ optional helper |
| 5 | report ไม่มี per-page traceability section          | medium   | `lite-report.html` `buildReportPayload` + `lite-report.html` — เพิ่ม section "หน้าที่ใช้/ไม่ใช้" | ✅ template-only |
| 6 | ไม่มี cross-check ระหว่าง 3 site sheet (p5/p7/p8) — ถ้าผู้ใช้วัดที่ดินทั้ง 3 ได้ตัวเลขต่างกันจะรู้ตอนไหน? | low      | warnings panel — เพิ่ม cross-page-consistency check | ✅ warning-only |

### C. ไม่ใช่ gap — ตั้งใจไม่ทำ

- **page-scoped layer** (สีต่างต่อหน้า, lock เฉพาะหน้า) — ไม่จำเป็นใน permit case
- **OCR / auto-detect boundary** — Phase 2, ออกจาก lite scope

## 7. ลำดับ slice ที่เสนอ (ถ้าจะ build ต่อ)

1. **LSP-1 Sheets/Pages bulk-tag UI** (gap #3) — รับ 45 หน้าให้ tag ได้เร็ว, foundation ของทุกอย่าง — risk: ต่ำ, ไม่แตะ schema
2. **LSP-2 PAGE_TAGS extend** (gap #2) — เพิ่ม 7 tag (additive enum)
3. **LRR-1 GFA-by-floor aggregator** (gap #1) — เพิ่มใน LRV: เมื่อ `ref: "layer:gfa AND floor:N"` ให้ filter ผ่าน `pageFloorNum` — risk: medium
4. **LRP-1 Traceability section in report** (gap #5) — append section "หน้าที่ใช้คำนวณ" + "หน้าที่ไม่ใช้" ใน `lite-report.html`
5. **LSP-3 (optional) auto-classify** (gap #4) — Thai-keyword heuristic เลียน python script ที่ใช้ใน spike

ขั้นที่ 1-4 รวมกัน = lite รับ case 45-page permit ได้ครบ end-to-end. ขั้นที่ 5 เป็น UX nice-to-have.

## 8. Open questions (ก่อนเริ่ม build slice ใด ๆ)

1. **ตัวเลขใน mock report** — ผมประมาณจากระยะที่อ่านได้ใน drawing (45.00 × 16.50 m ≈ 740 m² × 5 ชั้น). ถูกไหม? หรือต้องการให้ผมเปิด lite จริง + วัด p11 ให้ดูเป็น proof?
2. **`PAGE_TAGS` enum ที่จะ extend** — ตอนนี้ใช้ 13 tag ใน spike (cover/site/floor/roof/section/restroom/stair/detail/schedule/notes/legend/fixtures/sanitary) — ผู้ใช้ approve set นี้ไหม หรือควรรวบ (เช่น detail+schedule+notes รวมเป็น `aux`)?
3. **GFA-by-floor**: report ต้องการแยกชั้นแค่ "ตาราง breakdown" หรือต้อง expose เป็น `reportVar` แต่ละชั้นด้วย (`v_gfa_l1`, `v_gfa_l2`, ...) เพื่อใช้ใน expr อื่น?
4. **site cross-check (p5/p7/p8)** — รับว่ามี 3 sheet site แล้วผู้ใช้วัดที่ดินซ้ำ 3 ครั้ง → ระบบควรเลือก primary ตัวเดียว (เช่น p7) หรือ flag warning ถ้าไม่ตรง?
5. **roof (p17) vs ดาดฟ้า (p16)** — ดาดฟ้า (p16) มี GFA จริง (มี object ตั้งอยู่), roof slab (p17) ไม่ค่อยนับ — confirm? หรือบาง project นับ roof slab ด้วย?

## 9. Files

- `lite/sandbox/invent-45page-permit-spike.html` — interactive (open ในเบราว์เซอร์ เดี่ยว ๆ ได้, ไม่ต้องรันเซิร์ฟเวอร์)
- `artifacts/permit-45p-survey.json` — raw text extract ต่อหน้า (gitignored — ใช้สำหรับยืนยัน classification)
- `artifacts/permit-45p-classified.json` — auto-classifier output (heuristic — มีหลุด เลยใช้ manual override ใน sandbox HTML)
