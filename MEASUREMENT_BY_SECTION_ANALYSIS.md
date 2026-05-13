# Measurement by Section — Spec Analysis (Phase I pre-planning)

> Status: **Analysis only — no implementation yet.** ผู้ใช้สั่ง "อย่าพึ่งทำอะไร นายดูลอจิกให้หน่อย"
> Date: 2026-05-12
> Source: in-conversation analysis of `proto/ui.html` + `proto/server.py`
> Branch: `feature/menu-power-up` (current — Phase H.1+H.2 committed)

---

## Context

ผู้ใช้ระบุว่าการวัดตามกฎหมายต้องแบ่ง **3 ส่วนตามกายภาพ**:

1. **ผังบริเวณ** (Site Plan)
2. **พื้นที่ในแต่ละชั้น** (Floor Plans)
3. **ดาดฟ้า** (Roof)

แต่ละ section มีการวัดต่างกัน — บางอันวัดพื้นที่, บางอันวัดความสูง/ระยะร่น

ก่อนจะออกแบบ feature ผู้ใช้ขอให้พิจารณา spec ของแต่ละ section ก่อน

---

## Section Mapping: กายภาพ ↔ Page Tag ปัจจุบัน

| Physical Section | Page Tag ปัจจุบัน | สถานะ |
|---|---|---|
| 1. ผังบริเวณ | `site` | ✅ มี |
| 2. พื้นที่ในแต่ละชั้น | `plan` (multi-page: ชั้น 1, 2, 3...) | ✅ มี |
| 3. **ดาดฟ้า** | `plan` (ใช้รวมกับชั้นอื่น) | ⚠️ **ไม่มี tag แยก** — ต้องเพิ่ม `roof` |
| รูปด้าน (สำหรับความสูง) | `elev` | ✅ มี |
| รูปตัด | `section` | ✅ มี |

---

## 1️⃣ ผังบริเวณ (Site Plan) — Page Tag: `site`

### 1.1 พื้นที่ที่ต้องวัด

| พื้นที่ | Use case ตามกฎหมาย | สถานะปัจจุบัน |
|---|---|---|
| **พื้นที่ที่ดินทั้งหมด** | denominator ของทุกสัดส่วน | ✅ areaType `land` |
| **พื้นที่ปกคลุมอาคาร (Building Coverage)** | BCR — มี max ตามกฎหมาย (พื้นที่ส่วน A/B/C/D) | ⚠️ areaType `building` มีแต่ semanticTag ผิด (default = `gross_floor_area` แต่ควรเป็น `building_coverage`) |
| **พื้นที่ว่าง (Open Space)** | กฎหมาย: ≥ 30% ของที่ดิน (residential), แตกต่างตามประเภท | ❌ **ไม่มี** — ต้อง derive = land − coverage |
| **พื้นที่ซึมน้ำ (Pervious / Permeable)** | กฎหมาย: ≥ 50% ของที่ว่าง ห้ามเป็น hardscape ทั้งหมด | ❌ **ไม่มี category** เลย |
| **พื้นที่ Hardscape** (ทางเดิน/ลาน/จอดรถนอกอาคาร) | อยู่ในที่ว่างแต่ไม่นับ permeable | ❌ **ไม่มี** |
| **พื้นที่ Softscape / Green** (สวน/ต้นไม้) | นับเป็น permeable + ใช้เป็น landscape credit | ❌ **ไม่มี** |
| **พื้นที่จอดรถ (area polygon)** | คนละอันกับ parking marker (point) | ⚠️ areaType `parking_area` ใช้กับ marker เป็นหลัก |
| **พื้นที่ถนน/access road ภายใน** | ต้องมีตามจำนวนหน่วย | ❌ **ไม่มี** |

### 1.2 ระยะที่ต้องวัด (Setback / Distance)

| ระยะ | กฎหมายอ้างอิง | สถานะปัจจุบัน |
|---|---|---|
| **ระยะร่นด้านหน้า** | ตามความกว้างถนน (≥ 3m, 6m, ...) | ⚠️ มี edge tag `front_road` + setback distance helper |
| **ระยะร่นด้านข้าง** (ซ้าย/ขวา) | residential ≥ 2m, commercial ≥ 3m | ⚠️ มี edge tag `side_left/side_right` |
| **ระยะร่นด้านหลัง** | ≥ 2m | ⚠️ มี edge tag `back` |
| **ระยะ 2h** (อาคารสูง / ขนาดใหญ่พิเศษ) — **ผู้ใช้เน้น** | กฎกระทรวง 33: ระยะร่น ≥ 2× ความสูงอาคาร (มุม 45°) | ❌ **ไม่มี logic เฉพาะ** — Phase H.0 (45° lock) จะ enable |
| **ระยะ 6m** (ทางเข้า-ออกอาคาร) | ตามประเภทอาคาร | ⚠️ วัดได้แบบ generic distance |
| **ระยะถึงลำคลอง** | ≥ 3m, 6m, 12m ตามขนาดคลอง | ⚠️ edge tag `canal` |
| **ความกว้างถนน** | ตามประเภท → กำหนด setback ขั้นต่ำ | ⚠️ บันทึกใน `polyEdgeTags.note` (string) |
| **ระยะระหว่างอาคาร** | ตามความสูงอาคาร | ❌ ไม่มี helper เฉพาะ |

### 1.3 มุม / ทิศ

| รายการ | สถานะ |
|---|---|
| ทิศเหนือ (N angle) | ✅ มี (north arrow) |
| มุมที่ดิน | ⚠️ derive จาก polyEdgeTags ได้ — ไม่มี explicit storage |

### 1.4 % คำนวณ (ที่ต้องเพิ่ม)

```
BCR (Building Coverage Ratio) = building_coverage / land × 100
OSR (Open Space Ratio)        = (land − building_coverage) / land × 100
% ซึมน้ำ                       = permeable / land × 100
% hardscape                    = hardscape / (land − building_coverage) × 100
```

❌ **ไม่มีสูตรเลย**

---

## 2️⃣ พื้นที่ในแต่ละชั้น (Floor Plans) — Page Tag: `plan`

### 2.1 พื้นที่ที่ต้องวัด

| พื้นที่ | Use case | สถานะปัจจุบัน |
|---|---|---|
| **GFA ต่อชั้น (Gross Floor Area)** | รวม → FAR | ⚠️ areaType `gfa` มี แต่ summary นับ "ทุกอย่างไม่ใช่ land" รวมกัน |
| **GFA รวมทุกชั้น** | numerator ของ FAR | ⚠️ "รายชั้น" tab รวมหยาบเกินไป (ไม่ filter เฉพาะ gfa) |
| **พื้นที่ใช้สอย/Net Floor** | rent area, NFA | ⚠️ areaType `room` (semanticTag `use_area`) |
| **พื้นที่ทางเดิน (Corridor)** | ต้องนับใน GFA, มี max ratio | ✅ areaType `corridor` |
| **พื้นที่บันได + บันไดหนีไฟ** | บางส่วนหักออกจาก GFA | ✅ areaType `stair`, `fire_stair` |
| **พื้นที่ลิฟต์ / ปล่อง** | บางส่วนหักจาก GFA | ❌ ไม่มี — ใช้ areaType `non_gfa`? |
| **พื้นที่ห้องน้ำ / pantry** | นับ GFA | ⚠️ areaType `service` |
| **พื้นที่จอดรถในอาคาร** | กฎหมาย: ≥ 1 คัน/60 ตร.ม. office (BMA) | ⚠️ areaType `parking_area` (poly) + parking marker (point) |
| **ช่องโล่ง / Atrium / Void** | หักจาก GFA | ✅ openings (deduction layer) |
| **พื้นที่ไม่นับ GFA** | balcony, ระเบียง, terrace (บางส่วน) | ✅ areaType `non_gfa` |
| **ยูนิตพักอาศัย** | ขั้นต่ำ 20 ตร.ม. / unit (อพาร์ตเมนต์) | ✅ areaType `residential_unit` |
| **ห้องนอน** | ขั้นต่ำ ตามประเภท | ✅ areaType `bedroom` |

### 2.2 ระยะ / ความกว้างที่ต้องวัด

| ระยะ | กฎหมาย | สถานะปัจจุบัน |
|---|---|---|
| **ความกว้างทางเดิน** | residential ≥ 1.50m / corridor ≥ 1.50m | ⚠️ วัดด้วย distance tool ทั่วไป — ไม่มี categorize |
| **ความกว้างประตูทางเข้า** | ≥ 0.80m / unit, ≥ 0.90m main | ❌ ไม่มี logic แยก |
| **ความกว้างประตูหนีไฟ** | ≥ 0.90m | ❌ |
| **ความกว้างบันไดหนีไฟ** | ≥ 0.90m residential, ≥ 1.50m commercial | ❌ |
| **ระยะหนีไฟ (Travel Distance)** | ≤ 30m / 45m / 60m ตามประเภท | ❌ **ไม่มี logic เฉพาะ** — ต้องวัด path จากจุดใดๆ ถึงทางออก |
| **ระยะระหว่างบันไดหนีไฟ** | ตามขนาดอาคาร | ❌ |

### 2.3 ความสูงพื้น-เพดาน

วัดจาก `section`/`elev` page → ไม่ใช่ใน plan โดยตรง

---

## 3️⃣ ดาดฟ้า (Roof) — **ต้องเพิ่ม page tag ใหม่: `roof`**

### 3.1 พื้นที่ที่ต้องวัด

| พื้นที่ | Use case | สถานะปัจจุบัน |
|---|---|---|
| **พื้นที่ดาดฟ้ารวม** | base | ❌ ไม่มี category แยก |
| **พื้นที่ใช้ประโยชน์ดาดฟ้า** (Roof terrace, Garden) | บางอาคารนับ GFA, บางอาคารไม่นับ | ❌ |
| **พื้นที่ห้องเครื่อง (Machine room)** | ปกติไม่นับ GFA / ไม่นับเป็นชั้น | ❌ |
| **พื้นที่ MEP / equipment** | AC, solar, water tank | ❌ |
| **พื้นที่ Helipad** | ถ้ามี (อาคาร ≥ 23m) | ❌ |
| **Penthouse** | บางส่วนนับเป็นชั้นเพิ่ม | ❌ |
| **Green roof** | เครดิตในการคำนวณ permeable | ❌ |

### 3.2 ระยะ / ความสูงที่ต้องวัด

| ระยะ | กฎหมาย | สถานะปัจจุบัน |
|---|---|---|
| **ความสูงราวกันตก (parapet)** | ≥ 1.10m | ❌ |
| **ความสูง penthouse / ห้องเครื่อง** | นับ/ไม่นับ ในความสูงอาคาร | ❌ |
| **ระยะถึงขอบดาดฟ้า** (safety zone) | ตามประเภท | ❌ |
| **ระยะ helipad** (clear zone) | กฎ ICAO + DCA | ❌ |

### 3.3 ปัญหาเฉพาะ

- ดาดฟ้า มักรวมในหน้า "plan" สุดท้ายของ PDF → ระบบไม่แยกได้ → คำนวณ GFA ผิดเพราะ roof terrace จะถูกนับเป็น floor ปกติ
- ดาดฟ้ามีพื้นที่เปิดโล่ง vs ส่วนใช้ประโยชน์ → ปัจจุบันไม่มี logic แยก

---

## 🎯 สรุป Spec ที่ต้อง decide

### A. Page Tag ที่ต้องเพิ่ม
- `roof` — สำหรับดาดฟ้า (ใหม่)
- หรือเก็บ `plan` แต่เพิ่ม subtype `is_roof: true` ใน pageStore

### B. AreaType ใหม่ที่ต้องเพิ่ม (per section)

**Site (ผังบริเวณ):**
- `building_coverage` (ปกคลุมอาคาร) — replace/clarify ของ `building`
- `permeable` (พื้นที่ซึมน้ำ — สวน, ดิน)
- `hardscape` (ลาน, ทางเดิน — ไม่ซึมน้ำ)
- `softscape` (สวน) — อาจรวมกับ `permeable`
- `parking_outdoor` (จอดรถนอกอาคาร) — แยกจาก in-building parking

**Plan (แต่ละชั้น):**
- ใช้ของเดิมได้: `room`, `gfa`, `non_gfa`, `corridor`, `stair`, `fire_stair`, `service`, `parking_area`
- เพิ่ม: `lift_shaft`, `mep_shaft`, `bathroom` (ถ้าต้องการละเอียด)
- เพิ่ม: `balcony` (terrace ระเบียง — บางส่วน non_gfa)

**Roof (ดาดฟ้า):**
- `roof_terrace` (ใช้ประโยชน์)
- `roof_machine_room` (ห้องเครื่อง)
- `roof_equipment` (อุปกรณ์ MEP / Solar)
- `roof_green` (green roof — credit permeable)
- `roof_void` (พื้นโล่ง — ไม่นับ GFA)

### C. Linear Measurement Type ใหม่
ตอนนี้มีแค่ `dist` / `path` / `ref` / `setback` — **เพียง 4 ประเภท**

ต้องการเพิ่ม **measurement category** เพื่อแยกตามกฎหมาย:

**Site:**
- `setback_front`, `setback_side_l`, `setback_side_r`, `setback_back`, `setback_2h`
- `road_width`, `canal_distance`, `building_to_building`

**Plan:**
- `corridor_width`, `door_width`, `exit_width`, `stair_width`
- `travel_distance` (path measurement สำหรับ fire egress)

**Vertical (section/elev):**
- `floor_to_ceiling_height`
- `building_height_total`
- `parapet_height`
- `floor_height` (ระยะระหว่างชั้น)

### D. % Calculations ที่ต้องเพิ่ม

| สูตร | ใช้ใน section |
|---|---|
| `BCR = building_coverage / land × 100` | site |
| `OSR = (land − building_coverage) / land × 100` | site |
| `FAR = total_GFA / land × 100` | site (อ้างถึง plan) |
| `% permeable = permeable / land × 100` | site |
| `% hardscape in open = hardscape / open_space × 100` | site |
| `% corridor = corridor / floor_area × 100` (per floor) | plan |
| `GFA per floor / total GFA` (per floor share) | plan |

---

## 📋 Open Questions (ยังต้อง decide)

### Q1: วิธีจัด section
- **A.** Tag-based per section (เพิ่ม pageTag `roof` + `measurementCategory` field) — ปลอดภัย backward compat
- **B.** Separate section panels ใน Summary Widget (3 แผง Site/Floor/Roof) — UX ชัดเจน
- **C.** ผสมทั้ง 2

### Q2: แสดง legal limits หรือไม่
- **A.** ไม่แสดง limit เลย — Phase 1 strict (ตาม AGENTS.md)
- **B.** แสดง reference limit (เช่น "BCR ของคุณ = 45% / กฎหมาย max 50%") — ไม่ตัดสินผ่าน/ไม่ผ่าน
- **C.** แยก limit ออกเป็น Phase 2

### Q3: Linear Measurement Categorize
- **A.** เพิ่ม `measurementCategory` field ต่อ line/poly — backward compat
- **B.** ใช้ mode ของ tool เดิม + tag ทีหลัง (right-click → tag)
- **C.** เพิ่ม menu Measure > Categorized Distance ที่บังคับ category ตั้งแต่ต้น

---

## Constraints (ห้ามแตะ ตาม AGENTS.md)

- `proto/server.py` (core endpoints)
- `polyMetrics`, `polyAreaM2`, `polySelfIntersects`, `pdfToC`, `cToPdf`
- Snap algorithm
- Existing `.bmaplan` schema (เพิ่ม optional field ได้)
- ห้ามเพิ่ม OCR / AI / Rule Engine / FAR-OSR-setback pass-fail / legal checker
  - **กฎสำคัญ:** ระบบบันทึก measurement, ห้าม auto-judge ผ่าน/ไม่ผ่าน
  - Phase 2 เป็น manual legal review only

---

## Current Logic Gaps Summary (ที่ระบุในการสนทนา)

| สิ่งที่ต้องการคำนวณ | ปัจจุบัน | Gap |
|---|---|---|
| พื้นที่ที่ดิน | ✅ `landArea` | — |
| พื้นที่อาคาร (รวม) | ⚠️ `measuredArea` (ทุกอย่างไม่ใช่ land) | ไม่แยก building vs room |
| พื้นที่ปกคลุมอาคาร (footprint) | ❌ | areaType หรือ semanticTag ใหม่ |
| ที่ว่าง (open space) | ❌ | คำนวณ: land − footprint |
| % ที่ว่าง | ❌ | สูตรไม่ได้ implement |
| พื้นที่ซึมน้ำ | ❌ | category ใหม่ทั้งหมด |
| % พื้นที่ซึมน้ำ | ❌ | สูตรไม่ได้ implement |
| GFA ต่อชั้น | ⚠️ มี areaType "gfa" / "non_gfa" แต่ summary ไม่แยก | logic แยก gfa จาก use_area |
| รวม GFA ทุกชั้น | ⚠️ totalArea ใน _swBuildFloor นับทุก areaType ที่ไม่ใช่ land | filter gfa-only |

---

## Next Steps (รอ decision)

1. ผู้ใช้พิจารณา 3 sections + อ่าน spec
2. ตอบ Q1/Q2/Q3 ในไฟล์นี้ (หรือใน chat)
3. ผู้ใช้สั่งเริ่ม design — ผมจะเขียน `PHASE_I_PLAN.md` ตาม direction ที่เลือก
4. Implement หลังแผนได้รับอนุมัติ

ไฟล์นี้เก็บไว้เป็น reference จนกว่า Phase I plan จะออกมา
