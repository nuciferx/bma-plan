# SITE_PLAN_MEASUREMENT_PLAN.md — Measurement Requirements for Site Plan (ผังบริเวณ)

> Date: 2026-05-13
> Status: PLANNING DOCUMENT — no source code, no UI, no test change
> Scope: ระบุ "ต้องวัดอะไรบ้าง" บนผังบริเวณ — Phase 1 measurement requirements
> Law sources: `law/mr35-33-upd69.pdf`, `law/mr43-55-upd68.pdf`, `law/สยามสินทร ร้านอาหาร 2568.pdf`
> Aligns with: `MEASUREMENT_BY_SECTION_ANALYSIS.md §1`, `PAGE_SCOPED_LAYER_MODEL.md`

---

## 1. Purpose

กำหนด list ของพื้นที่ / ระยะ / มุม / การนับ ที่ระบบ BMA-Plan ต้อง **capture** บนหน้าผังบริเวณ (`pageType = site` / `site_plan`) เพื่อให้ผู้ใช้สามารถวัดและส่งออกข้อมูลครบสำหรับการตรวจแบบอนุญาตก่อสร้างตามกฎกระทรวง

เอกสารนี้คือ **measurement requirements specification** — ระบุว่าระบบต้องเก็บข้อมูล **อะไร** ไม่ได้กำหนดว่าระบบต้องตัดสิน **ผ่าน/ไม่ผ่าน**

---

## 2. Phase 1 Hard Rule

```
ระบบเก็บ measurement (fact)
ระบบไม่ตัดสิน pass / fail (law judgment)
```

| Allowed (Phase 1) | Forbidden (Phase 1) |
|---|---|
| ✅ บันทึก FAR ที่คำนวณได้ | ❌ ตรวจ FAR vs กฎหมาย pass/fail |
| ✅ บันทึก OSR % ที่ได้ | ❌ ตรวจ OSR ≥ 30% pass/fail |
| ✅ บันทึก ระยะร่น 4 ทิศ | ❌ บอก "ระยะร่นน้อยไป" |
| ✅ บันทึก เกณฑ์ที่ผู้ใช้กรอกเอง | ❌ Auto-load FAR ตามผังเมืองโซน |
| ✅ แสดง reference (กฎกระทรวงข้อ X.) | ❌ Generate ค.1 |
| ✅ Show side-by-side: "วัดได้ X ม. / ผู้ใช้กรอกเกณฑ์ Y ม." | ❌ "ผ่าน/ไม่ผ่าน" auto verdict |

อ้างอิง: `AGENTS.md §3.1` Phase 1 Scope Lock, `CLAUDE.md` "What this project is", `MEASUREMENT_BY_SECTION_ANALYSIS.md §2 D Q2`.

ผู้ใช้กรอกเกณฑ์เอง — ระบบเปรียบเทียบและ **display** ผล แต่ไม่ generate verdict, ไม่ block submission

---

## 3. Building Classification (ส่งผลต่อ measurement category)

```
ที่ดินที่ตั้งอาคาร
  ↓
ประเภทอาคาร (ผู้ใช้เลือกใน Project Setup)
  ↓
list ของ measurement ที่ต้องวัดเปลี่ยนตาม classification
```

### 3.1 ประเภทตามขนาด (กฎกระทรวง 33)

| Type | เกณฑ์ | Site plan implications |
|---|---|---|
| อาคารทั่วไป | ความสูง < 15 ม. และ พื้นที่ < 1,000 ตร.ม. | กฎ มร.55 |
| อาคารขนาดใหญ่ | พื้นที่รวมทุกชั้น ≥ 2,000 ตร.ม. หรือ สูง ≥ 15 ม. + 1,000-2,000 ตร.ม. | + เพิ่มข้อกำหนด |
| อาคารสูง | สูง ≥ 23.00 ม. | + กฎ มร.33 ทั้งหมด |
| อาคารขนาดใหญ่พิเศษ | พื้นที่รวมทุกชั้น ≥ 10,000 ตร.ม. | + กฎ มร.33 ทั้งหมด |

### 3.2 ประเภทตามการใช้งาน (กฎกระทรวง 55)

```
อาคารอยู่อาศัย / อยู่อาศัยรวม / ห้องแถว / ตึกแถว / บ้านแถว / บ้านแฝด / 
อาคารพาณิชย์ / อาคารสาธารณะ / อาคารพิเศษ / โรงงาน / คลังสินค้า / 
สำนักงาน / โรงมหรสพ / โรงพยาบาล / โรงแรม / สถานบริการ / ห้างสรรพสินค้า
```

→ ต้องเพิ่มใน `projectInfo.buildingUseType` หรือ `pageStore[pg].buildingClassification`

---

## 4. พื้นที่ที่ต้องวัด (Site Plan Areas)

### 4.1 พื้นที่หลัก (Required)

| # | พื้นที่ | semanticTag (เสนอใหม่) | areaType ปัจจุบัน | กฎอ้างอิง | Note |
|---|---|---|---|---|---|
| 1 | **พื้นที่ดินทั้งหมด** | `site_land_area` | `land` | มร.55 ข้อ 33, มร.33 ข้อ 5-6 | denominator ของทุก ratio |
| 2 | **พื้นที่ปกคลุมอาคาร** (footprint) | `building_coverage` 🆕 | ⚠️ `building` (semanticTag ผิด) | มร.55 ข้อ 36-39, มร.33 ข้อ 4-6 | ใช้คำนวณ BCR |
| 3 | **พื้นที่อาคารรวมทุกชั้น** (GFA total) | `gross_floor_area` (รวมจาก plan) | `gfa` (per floor) | มร.33 ข้อ 5 (FAR) | คำนวณจาก plan pages → site total |
| 4 | **พื้นที่ว่าง** (Open Space) | `open_space` 🆕 | ❌ ไม่มี | มร.55 ข้อ 33, มร.33 ข้อ 6 | = land − coverage หรือกรอกเอง |
| 5 | **พื้นที่ซึมน้ำ** (Pervious) | `permeable_area` 🆕 | ❌ ไม่มี | (กม. ผังเมือง / ไม่ใช่ มร.33/55) | OSR ของผังเมือง |
| 6 | **พื้นที่ Hardscape** (ลาน/ทางเดิน) | `hardscape` 🆕 | ❌ ไม่มี | derived | ที่ว่างที่ไม่ซึมน้ำ |
| 7 | **พื้นที่ Softscape / Green** | `softscape` 🆕 | ❌ ไม่มี | landscape credit | optional sub-category ของ permeable |
| 8 | **พื้นที่จอดรถนอกอาคาร** | `parking_area_outdoor` 🆕 | ⚠️ `parking_area` (เดิม) | กม.ที่จอดรถ | แยกจาก in-building parking |
| 9 | **พื้นที่ถนน/access road ภายใน** | `internal_road` 🆕 | ❌ ไม่มี | มร.33 ข้อ 3 (≥6ม.รอบ) | สำหรับอาคารสูง/ใหญ่พิเศษ |
| 10 | **พื้นที่ทางเดินสะพานเชื่อม** (ถ้ามี) | `connecting_walkway` | optional | มร.55 ข้อ 6 / 32/1 | ส่วนบุคคล ≥3.50ม. / สาธารณะ ≥6ม. |

### 4.2 พื้นที่ optional (ตามประเภทอาคาร)

| พื้นที่ | semanticTag | เมื่อไหร่ต้องการ |
|---|---|---|
| พื้นที่สระว่ายน้ำ | `pool_area` | ที่อยู่อาศัยรวม / โรงแรม |
| พื้นที่ที่พักมูลฝอย | `garbage_collection_area` | อาคารสูง/ใหญ่พิเศษ (มร.33 ข้อ 40) — ≥3 เท่าของมูลฝอย/วัน, ห่าง อาคาร≥4ม. (ถ้า≥3ลบ.ม.→≥10ม.) |
| พื้นที่บ่อบำบัดน้ำเสีย | `wastewater_treatment_area` | (มร.33 หมวด 3) |
| พื้นที่ลานจอดรถดับเพลิง/พยาบาล | `emergency_vehicle_area` 🆕 | อาคารสูง/ใหญ่พิเศษ (มร.33 ข้อ 29/1): รถดับเพลิงกว้าง≥3, ยาว≥10ม. / รถพยาบาลกว้าง≥2.40, ยาว≥7ม., สูง≥2.85ม. |
| พื้นที่ Helipad | `helipad_area` | optional |

---

## 5. ระยะที่ต้องวัด (Site Plan Distances)

### 5.1 ระยะร่นจากเขตที่ดิน (Setback from property line)

ทุก edge ของ polygon `site_land_area` (`semanticTag = site_boundary`) มี `edgeTag` ระบุประเภท:

| edgeTag.role | คำอธิบาย | ระยะร่นต้องวัด | กฎอ้างอิง |
|---|---|---|---|
| `front_road` | ด้านหน้า ติดถนน | ระยะแนวอาคารถึงเขตถนน | มร.55 ข้อ 36-39, ข้อ 41 |
| `side_left` / `side_right` | ด้านข้าง ติดเพื่อนบ้าน | ระยะผนังถึงแนวเขตที่ดิน | มร.55 ข้อ 50 |
| `back` | ด้านหลัง | ระยะผนังถึงแนวเขตที่ดิน | มร.55 ข้อ 36 |
| `neighbor` | เพื่อนบ้าน (ทั่วไป) | เหมือนข้อ 50 | มร.55 ข้อ 50 |
| `canal` / `waterway` | ติดแหล่งน้ำสาธารณะ | ระยะถึงเขตแหล่งน้ำ | มร.55 ข้อ 42 |
| `public_road` | ติดถนนสาธารณะ (รอบอาคาร) | กว้างของถนน + แนวอาคารถึงกึ่งกลาง | มร.55 ข้อ 41 |
| `ignore` | ไม่ใช้รายงาน | — | — |

✅ ของเดิม `polyEdgeTags` มี role list ที่ใช้งานได้ตรงนี้ — `front_road / side_left / side_right / back / neighbor / canal / ignore`

### 5.2 ระยะที่ต้องวัดเฉพาะ

| ระยะ | จากอะไร → ถึงอะไร | กฎอ้างอิง | Phase H.0 hint |
|---|---|---|---|
| **ระยะร่น 4 ทิศ** | ผนังอาคาร → แนวเขตที่ดิน 4 ด้าน | มร.55 ข้อ 50 + ข้อ 36 + ข้อ 41 | distance + perp |
| **ระยะ 2h** | ผนังอาคาร (เอียง 45°) → แนวเขตถนนด้านตรงข้าม | มร.55 ข้อ 44 — สูง ≤ 2× ระยะราบ | ⚠️ ต้องการ 45° lock (Phase H.0) |
| **ระยะอาคาร-อาคาร** (ในที่ดินเดียวกัน) | ผนัง A → ผนัง B | มร.55 ข้อ 48 | 4 ระดับ height-based |
| **ระยะหน้าต่าง-เขตที่ดิน** | ผนังที่มีหน้าต่าง → แนวเขตที่ดิน | มร.55 ข้อ 50 | สูง≤9ม.→≥2ม. / 9-23ม.→≥3ม. |
| **ระยะรอบอาคาร** (อาคารสูง/ใหญ่พิเศษ) | ขอบอาคารทุกด้าน → ถนนภายในรอบอาคาร | มร.33 ข้อ 3-4 | ≥6ม. รอบ |
| **ความกว้างถนนสาธารณะ** | เขตถนนทั้ง 2 ฝั่ง | สังเกตจากผังบริเวณ | กำหนดในแบบ |
| **ระยะถึงแหล่งน้ำ** | ผนังอาคาร → เขตแหล่งน้ำ | มร.55 ข้อ 42 | <10ม.→≥3ม. / ≥10ม.→≥6ม. / ใหญ่→≥12ม. |
| **ระยะมุมถนน-ปาดมุม** | จุดปาดมุมรัศมี | มร.55 ข้อ 5 | ≥4ม. ถ้ามุม<135° + ถนน≥3ม. |
| **ระยะระหว่างทางเข้าออก-ทางแยก** | จุดปากทางเข้า → ทางร่วม/แยก | (เคสสยามสินทร ใช้ 20ม.) | optional, จากเคสจริง |

### 5.3 ข้อกำหนดเฉพาะอาคารสูง/ใหญ่พิเศษ (มร.33)

| ระยะ | เกณฑ์ |
|---|---|
| ด้านยาวติดถนน | ≥ 12 ม. |
| ความกว้างถนนติด (พื้นที่ ≤30,000 ตร.ม.) | ≥ 10 ม. |
| ความกว้างถนนติด (พื้นที่ >30,000 ตร.ม.) | ≥ 18 ม. |
| ถนนรอบอาคาร | ≥ 6 ม. ปราศจากสิ่งปกคลุม |
| ขอบนอกอาคาร → เขตที่ดินผู้อื่น/ถนน | ≥ 6 ม. |
| ติดน้ำสาธารณะ | ≥ 12 ม. + ที่ว่างริมน้ำ |

### 5.4 ข้อ 48 (อาคารหลายหลังบนที่ดินเดียวกัน) — ต้องการการวัดเป็นคู่

ผนังที่มีหน้าต่าง vs ผนังของอาคารอื่น — เกณฑ์ขึ้นกับความสูงทั้งสองหลัง:

| H1 (ของผนัง A) | H2 (ของผนัง B) | ผนัง A: หน้าต่าง | ผนัง A: ทึบ |
|---|---|---|---|
| ≤ 9 ม. | ≤ 9 ม. | ≥ 4 ม. | ≥ 2 ม. |
| ≤ 9 ม. | 9-23 ม. | ≥ 5 ม. | ≥ 2.50 ม. |
| 9-23 ม. | 9-23 ม. | ≥ 6 ม. | ≥ 3.50 ม. |
| 15-23 ม. (ทึบทั้งสอง) | 15-23 ม. (ทึบทั้งสอง) | — | ≥ 1 ม. |

→ ต้องเพิ่ม **building object** บน site plan ที่ระบุ:
- `wallType: "window" | "opaque"` (per edge)
- `heightRange: "≤9" | "9-23" | "15-23"` (สำหรับ logic เปรียบเทียบ)

---

## 6. การนับ (Counts on Site Plan)

| รายการ | ปัจจุบัน | กฎอ้างอิง |
|---|---|---|
| ที่จอดรถ (จำนวนคัน) | ✅ parking marker (point) + count | กม.ที่จอดรถ |
| ที่จอดรถผู้พิการ | ⚠️ derive ได้จาก marker tag | กม.ที่จอดรถ |
| ที่จอดรถดับเพลิง | ❌ ต้องเพิ่ม | มร.33 ข้อ 29/1 (1) — ≥1 คัน |
| ที่จอดรถพยาบาล | ❌ ต้องเพิ่ม | มร.33 ข้อ 29/1 (2) — ≥1 คัน |
| ทางเข้า-ออกอาคาร | ❌ ต้องเพิ่ม | มร.33 ข้อ 3 |
| เครื่อง AED | ❌ ต้องเพิ่ม | มร.33 ข้อ 29/2 |
| ป้ายโฆษณา | ❌ ต้องเพิ่ม | มร.55 ข้อ 7-13 |

→ เพิ่ม `markerType` enum: `parking | parking_disabled | parking_fire | parking_ambulance | entrance | aed | sign | tree`

---

## 7. มุม / ทิศ (Angles & Orientation)

| รายการ | ปัจจุบัน | กฎอ้างอิง |
|---|---|---|
| ทิศเหนือ (N arrow) | ✅ มี (`north` per page) | ทั่วไป |
| มุมที่ดิน | ⚠️ derive จาก polyEdgeTags | มร.55 ข้อ 5 |
| มุมหักของรั้ว/กำแพง | ❌ ต้องคำนวณ | มร.55 ข้อ 5 — ถ้า <135° + ถนน ≥3ม. ต้องปาดมุม ≥4ม. |
| มุม 45° สำหรับ 2h | ❌ ❗ Phase H.0 | มร.55 ข้อ 44 |

---

## 8. % Calculations (Reference Display)

ระบบ **คำนวณและแสดง** แต่ **ไม่ตัดสินผ่าน/ไม่ผ่าน**

```
BCR (Building Coverage Ratio) = building_coverage / site_land_area × 100
OSR (Open Space Ratio)        = open_space / site_land_area × 100
                              = (site_land_area − building_coverage) / site_land_area × 100
FAR (Floor Area Ratio)        = total_GFA_all_floors / site_land_area
                              (อาจแสดงเป็น "5.91 : 1")
% permeable                   = permeable_area / site_land_area × 100
% permeable in open           = permeable_area / open_space × 100
% hardscape in open           = hardscape / open_space × 100
```

### 8.1 Reference thresholds (display only — ผู้ใช้กรอกเอง ไม่ hardcode)

UI แสดงในรูป "วัดได้ X / เกณฑ์ที่ผู้ใช้กรอก Y" — เปรียบเทียบให้เห็นภาพ ไม่ block submission

| Metric | กฎอ้างอิง (reference) | ตัวอย่างเคสสยามสินทร |
|---|---|---|
| FAR max | มร.33 ข้อ 5: ≤ 10:1 (อาคารสูง/ใหญ่พิเศษ) | วัดได้ 5.91:1 |
| OSR min | มร.33 ข้อ 6 (1): ≥ 30% (อยู่อาศัย) / ≥ 10% (พาณิชย์) | วัดได้ 49.70% |
| % permeable | (ผังเมือง — ผู้ใช้กรอก) | วัดได้ 50% |

→ Field schema: `projectInfo.userDefinedLimits = { far_max, osr_min, permeable_min, ... }`

---

## 9. Required Field Schema Additions (.bmaplan — additive only)

```jsonc
// projectInfo (top level, optional)
{
  "buildingClassification": "general" | "large" | "tall" | "extra_large",
  "buildingUseType": "residential" | "residential_mixed" | "commercial" 
                    | "industrial" | "office" | "public" | "warehouse" 
                    | "hotel" | "hospital" | "shop_house" | "townhouse" | "...",
  "userDefinedLimits": {
    "far_max": 10.0,           // ผู้ใช้กรอกตามผังเมือง
    "osr_min_pct": 30.0,
    "permeable_min_pct": 50.0,
    "setback_front_min_m": 6.0,
    "setback_side_min_m": 2.0,
    "setback_back_min_m": 2.0
  },
  "zoneCode": "พ.5-2",          // ผังเมือง — ผู้ใช้กรอก (display only)
  "siteAccessRoadWidth_m": 16.9 // ความกว้างถนนหน้าที่ดิน
}

// pageStore[siteIndex] additions
{
  "pageType": "site",            // เดิม
  "buildingObjects": [...]       // อาคารบนผังบริเวณ — ใช้ในข้อ 48 logic
}

// Each polygon on site page (additive)
{
  "semanticTag": "building_coverage" | "open_space" | "permeable_area" | 
                 "hardscape" | "softscape" | "parking_area_outdoor" | 
                 "internal_road" | "site_land_area" | "...",
  "buildingHeight_m": 110.6,     // เฉพาะ building_coverage objects (สำหรับข้อ 44/48)
  "wallEdges": [                 // เฉพาะ building objects (สำหรับข้อ 48/50)
    {
      "edgeIndex": 0,
      "wallType": "window" | "opaque",
      "openings": ["door", "window", "ventilation", "balcony"]
    }
  ]
}

// Markers (extend markerType enum)
{
  "markerType": "parking" | "parking_disabled" | "parking_fire" | 
                "parking_ambulance" | "entrance" | "aed" | "sign" | "tree"
}
```

**ห้าม** เปลี่ยน `.bmaplan` version (เก็บที่ 1) — เพิ่ม optional fields เท่านั้น

---

## 10. Mapping ไปยัง Existing Model

### 10.1 Layer (Page-Scoped Layer Model)

แต่ละ semanticTag ใหม่ ต้องเลือก **default layer** เมื่อสร้าง:

| semanticTag | default layer.slug |
|---|---|
| `site_land_area` | `base_area` (preset `site_default`) |
| `building_coverage` | `base_area` |
| `open_space` | `sub_area` |
| `permeable_area` | `sub_area` |
| `hardscape` / `softscape` | `sub_area` |
| `parking_area_outdoor` | `sub_area` |
| `internal_road` | `sub_area` |
| markers (parking/etc.) | `sub_area` |

### 10.2 Measurement Profile / Report Target

| semanticTag | measurementProfile | reportTarget |
|---|---|---|
| `site_land_area` | `site_land` | "ผังบริเวณ: พื้นที่ดิน" |
| `building_coverage` | `building_footprint` | "ผังบริเวณ: ปกคลุม BCR" |
| `open_space` | `open_space` | "ผังบริเวณ: ที่ว่าง OSR" |
| `permeable_area` | `permeable` | "ผังบริเวณ: ซึมน้ำ" |
| `hardscape` | `hardscape` | "ผังบริเวณ: hardscape" |
| `parking_area_outdoor` | `parking` | "ผังบริเวณ: จอดรถ" |

→ ใน `proto/ui.html` ปัจจุบัน `AREA_LABELS` มี:
`room, building, land, residential_unit, bedroom, corridor, stair, fire_stair, parking_area, service, gfa, non_gfa`

**ต้องเพิ่ม** (ตาม semanticTag ใหม่ — ทำเป็น additive options ใน Project Setup):
`building_coverage, open_space, permeable, hardscape, softscape, parking_outdoor, internal_road`

### 10.3 Existing `polyEdgeTags` (Land Edge)

✅ ระบบเดิมมี edge tag enum ที่ตรงกับความต้องการ:
```
front_road / side_left / side_right / back / neighbor / canal / ignore
```

ระบบเดิมรองรับการวัด **perpendicular distance** จากผนังอาคารถึง edge เหล่านี้แล้ว (Setback feature) — ต้องเพิ่มเฉพาะ:
- การ classify edge ของ **อาคาร** ว่าเป็น `wallType: window | opaque` (สำหรับข้อ 48/50)
- ส่ง building height per object สำหรับ comparison

---

## 11. UI Required Features (เสนอ — แยก sprint)

### 11.1 Project Setup (เพิ่ม fields)

```
[Project Info card]
- ประเภทอาคาร: [dropdown] อยู่อาศัย / พาณิชย์ / สำนักงาน / โรงแรม / ...
- ขนาดอาคาร: [auto-detect from height + total GFA] หรือ user override
- โซนผังเมือง: [text]    เกณฑ์ FAR: [number]   เกณฑ์ OSR: [number %]
- ความสูงอาคาร (สูงสุด): [number] ม. (มาจาก elev page หรือกรอกเอง)
- ถนนหน้าที่ดิน: ความกว้าง [number] ม.
```

### 11.2 Site Plan Toolbar (เพิ่ม shortcuts)

```
[ผังบริเวณ] เลือก area type:
  ⬛ พื้นที่ดิน          (semanticTag = site_land_area)
  ⬛ ปกคลุมอาคาร        (semanticTag = building_coverage)  ← NEW
  ⬛ ที่ว่าง            (semanticTag = open_space)         ← NEW
  ⬛ ซึมน้ำ            (semanticTag = permeable_area)      ← NEW
  ⬛ Hardscape         (semanticTag = hardscape)           ← NEW
  ⬛ จอดรถ (poly)      (semanticTag = parking_area_outdoor)← NEW
  📌 จอดรถ (marker)    (markerType = parking)
  🚒 จอดดับเพลิง       (markerType = parking_fire)        ← NEW
  🚑 จอดพยาบาล         (markerType = parking_ambulance)   ← NEW
```

### 11.3 Site Plan Summary Widget (เพิ่ม tab "ผังบริเวณ")

```
┌─ ผังบริเวณ ─────────────────────────────────┐
│ พื้นที่ดิน:        6,576.60 ตร.ม.            │
│ ปกคลุมอาคาร:     3,303.00 ตร.ม. (BCR 50.2%) │
│ ที่ว่าง:          3,264.60 ตร.ม. (OSR 49.7%) │
│ ─ ซึมน้ำ:         3,288.49 ตร.ม. (50.0%)    │
│ ─ Hardscape:    (derived)                  │
│ ─ จอดรถ outdoor: 458.00 ตร.ม.               │
│                                              │
│ FAR (ทุกชั้น):    38,887.50 / 6,576.60       │
│                = 5.91 : 1                    │
│                                              │
│ ระยะร่นรอบอาคาร (วัดได้):                     │
│   ทิศเหนือ:    7.84 ม.                       │
│   ทิศใต้:     12.00 ม.                       │
│   ทิศตะวันออก: 8.19 ม.                       │
│   ทิศตะวันตก: 7.22 ม.                        │
│                                              │
│ ที่จอดรถ:        258 คัน                     │
│ ─ พิการ:        (count)                     │
│ ─ ดับเพลิง:     1 คัน                       │
│ ─ พยาบาล:       1 คัน                       │
│                                              │
│ [แสดง reference จากผู้ใช้กรอก ที่ Project    │
│  Setup — ไม่ pass/fail]                      │
└──────────────────────────────────────────────┘
```

→ Widget นี้เป็น **display only**. ผู้ใช้ดูเอง ตัดสินใจเอง

---

## 12. Out of Scope (Phase 1)

❌ Auto-load FAR/OSR ตามผังเมืองโซน (Rule Engine)
❌ Auto-judge pass/fail (FAR ≤ 10, OSR ≥ 30%, etc.)
❌ Auto-extract scale/north/orientation จาก raster PDF (OCR)
❌ Auto-detect ขอบที่ดิน / footprint (AI/auto boundary)
❌ Generate ค.1 / สรุปรายการไม่ผ่าน
❌ Cross-reference กับ database กฎหมาย / ผังเมือง real-time
❌ ตรวจ 2h vs ความสูงจริง (เป็น user comparison เท่านั้น)
❌ Multi-jurisdiction (กทม. / ตจว. / ผังเมืองพิเศษ)

✅ เก็บ measurement, ให้ผู้ใช้กรอกเกณฑ์เอง, แสดงเปรียบเทียบ, export

---

## 13. Implementation Phases (Suggested — แยก sprint คนละหัวข้อ)

ห้าม implement ทุก feature ใน sprint เดียว — แยกตาม risk:

### Phase I-A: Schema additions (low risk, additive)
1. เพิ่ม `semanticTag` enum: `building_coverage, open_space, permeable_area, hardscape, parking_area_outdoor, internal_road`
2. เพิ่ม `AREA_LABELS` ใน proto/ui.html
3. เพิ่ม Project Setup fields: `buildingClassification, buildingUseType, userDefinedLimits, zoneCode`
4. Backward-compat ใน `applyLoadedProject`

### Phase I-B: Site Plan tools (medium risk)
1. เพิ่ม area buttons ใน toolbar (Site plan tools)
2. เพิ่ม marker types (parking_disabled / parking_fire / parking_ambulance / entrance / aed)
3. Default layer assignment per new semanticTag

### Phase I-C: Site Plan summary (medium-high risk)
1. เพิ่ม Summary Widget tab "ผังบริเวณ"
2. คำนวณ BCR / OSR / FAR / %permeable (display only)
3. แสดง 4-direction setback summary (ใช้ของเดิม + grouping)
4. XLSX: เพิ่ม sheet "สรุปผังบริเวณ" (additive)

### Phase I-D: Reference compare (high risk — ต้องระวัง scope creep)
1. แสดง user-defined limit vs measured value แบบ "X / Y"
2. ❌ **ห้าม** เพิ่ม pass/fail badge, color-coded "ผ่าน/ไม่ผ่าน"
3. UI text style: neutral facts only

### Phase I-E: Building-to-building distance (มร.55 ข้อ 48) — สูงสุดของ complexity
1. รองรับ multiple buildings บน site plan
2. `wallType` per edge (window / opaque)
3. Distance pair measurement (wall A → wall B)
4. แสดง "ระหว่าง A-B = X ม. / ผู้ใช้กรอกเกณฑ์ Y ม."

---

## 14. Example Trace — เคสสยามสินทร (จาก `law/สยามสินทร ร้านอาหาร 2568.pdf`)

ข้อมูลที่ระบบควรเก็บได้:

```yaml
projectInfo:
  buildingClassification: extra_large
  buildingUseType: hotel_commercial_mixed
  buildingHeight_m: 110.60          # ระดับสูงสุด (104.30 ที่ดาดฟ้า)
  zoneCode: "พ.5-2 (สีแดง)"
  userDefinedLimits:
    far_max: 10.0
    osr_min_pct: 3.0                # ตามผังเมือง (ไม่ใช่ 30 ของ มร.55!)
    permeable_min_pct: 50.0

site (pageType="site"):
  polygons:
    - semanticTag: site_land_area
      area_m2: 6576.60
      edgeTags:
        - role: public_road
          note: "ถนนหลังสวน 16.90 ม."
        - role: neighbor
        - role: neighbor
        - role: neighbor
    - semanticTag: building_coverage
      area_m2: 3303.00
      label: "อาคาร A+B+C รวม"
      buildingHeight_m: 110.60
    - semanticTag: open_space
      area_m2: 3264.60
    - semanticTag: permeable_area
      area_m2: 3288.49
    - semanticTag: parking_area_outdoor
      area_m2: <computed>
  markers:
    - markerType: parking
      count: 258                    # รวม 258 คัน
    - markerType: parking_fire
      count: 1
    - markerType: parking_ambulance
      count: 1

# คำนวณ (display only)
computed:
  BCR: 50.2  # = 3303 / 6576.60
  OSR: 49.7  # = 3264.60 / 6576.60
  FAR: 5.91  # = 38887.50 / 6576.60
  permeable_pct: 50.0  # = 3288.49 / 6576.60

# Setback (วัดจาก building → land edge)
setbacks:
  north: 7.84
  south: 12.00
  east:  8.19
  west:  7.22
```

ระบบ **ไม่ตัดสิน** "ผ่าน/ไม่ผ่าน" — แสดงให้ผู้ใช้ดู
ผู้ใช้เห็น:
- FAR 5.91 < 10 (ตามที่กรอก) ✓ ผู้ใช้ตัดสินเอง
- OSR 49.7% ≥ 3% (ตามที่กรอก) ✓ ผู้ใช้ตัดสินเอง
- ระยะร่นทิศใต้ 12 ม. ≥ 6 ม. (เกณฑ์ มร.33 ข้อ 4) ✓ ผู้ใช้ตัดสินเอง

---

## 15. Hard Forbidden (Implementation Phase)

ตาม `AGENTS.md §3.1`, `CLAUDE.md` "Forbidden surfaces", `MEASUREMENT_BY_SECTION_ANALYSIS.md`:

- ❌ Hardcode FAR/OSR ratios ตามผังเมือง
- ❌ Auto-judge "ผ่าน / ไม่ผ่าน"
- ❌ Rule Engine / pass-fail badge / verdict
- ❌ OCR ดึงข้อมูลจาก PDF อัตโนมัติ
- ❌ AI / boundary detection
- ❌ Generate ค.1 หรือเอกสารทางการ
- ❌ Cross-reference กฎหมาย database real-time
- ❌ แก้ `polyAreaM2`, `polyMetrics`, `pdfToC`, `cToPdf`, `RS`, scale math, snap engine
- ❌ แก้ `proto/server.py`
- ❌ เปลี่ยน `.bmaplan` version (additive fields เท่านั้น)
- ❌ Calculate จาก `layer.name` / `layer.slug` (ใช้ `semanticTag` เสมอ)

---

## 16. Open Questions (ต้อง decide ก่อน implement)

### Q1: User-defined limits vs Reference table
- **A.** ผู้ใช้กรอกเองทั้งหมด (Phase 1 strict) ← แนะนำ
- **B.** มี dropdown โซนผังเมือง (ใส่ FAR/OSR auto) — เริ่มกลายเป็น Rule Engine
- **C.** Mix: เริ่ม A, ภายหลังเพิ่ม B เป็น Phase 2

### Q2: Building object บน site plan
- **A.** เพิ่ม polygon `building_coverage` ปกติ + `buildingHeight_m` field
- **B.** เพิ่ม object type ใหม่ `building` ที่มี own schema
- **C.** Link จาก plan pages → site (1 building polygon = พื้นที่จาก plan ที่เป็น GFA สูงสุด)

### Q3: Multiple buildings (มร.55 ข้อ 48)
- **A.** เก็บแยกเป็น polygon แต่ละหลัง (recommended)
- **B.** Group หลายหลังเป็น 1 polygon รวม

### Q4: 2h rule (มร.55 ข้อ 44)
- ต้องการ Phase H.0 (45° angle lock) ก่อน
- ระบบวัดได้ — ผู้ใช้เปรียบเทียบเอง

### Q5: ที่จอดรถ — area polygon vs marker
- **A.** Marker (point) สำหรับนับจำนวนคัน
- **B.** Polygon `parking_area_outdoor` สำหรับขนาดพื้นที่
- **C.** ทั้ง 2 — marker linked to polygon (auto count per polygon)

---

## 17. Verification

**Docs-only sprint** — no source code, no UI, no test change

| Item | Result |
|---|---|
| `proto/server.py` | Not touched |
| `proto/ui.html` | Not touched |
| `proto/e2e_ui_test.py` | Not touched |
| `.bmaplan` schema | Unchanged (additive plan only) |
| `py_compile` | Not required |
| `smoke` / `full` | Not required |
| Phase 1 scope check | ✅ No legal judgment, no Rule Engine introduced |
| Hard forbidden | ✅ Documented §15 |
| Pass/fail logic | ✅ Explicitly forbidden §2, §12, §15 |

---

## 18. References

### Law sources
- `law/mr35-33-upd69.pdf` — กฎกระทรวง ฉบับที่ 33 (พ.ศ. 2535), update 69 (พ.ศ. 2564) — อาคารสูง/ใหญ่พิเศษ
- `law/mr43-55-upd68.pdf` — กฎกระทรวง ฉบับที่ 55 (พ.ศ. 2543), update 68 (พ.ศ. 2563) — อาคารทั่วไป
- `law/สยามสินทร ร้านอาหาร 2568.pdf` — เคสจริง ข.1 เลขรับ 153 (พ.ศ. 2568) — บริษัท สยามสินธร

### Internal docs
- `AGENTS.md` — operating manual + Phase 1 scope lock
- `CLAUDE.md` — Claude Code project context
- `MEASUREMENT_BY_SECTION_ANALYSIS.md` — pre-planning analysis
- `docs/design/PAGE_LAYER_MEASUREMENT_MODEL.md` — semantic tag pyramid
- `docs/design/PAGE_SCOPED_LAYER_MODEL.md` — layer model

### Key law articles referenced
- มร.33 ข้อ 2 (ที่ดิน + ถนนติด), ข้อ 3 (ถนนรอบอาคาร 6 ม.), ข้อ 4 (ขอบนอก 6 ม.), ข้อ 5 (FAR ≤ 10), ข้อ 6 (OSR), ข้อ 29/1 (รถดับเพลิง/พยาบาล), ข้อ 40 (มูลฝอย)
- มร.55 ข้อ 5 (มุมรั้ว), ข้อ 33 (ที่ว่าง), ข้อ 34-39 (ที่ว่างต่าง types), ข้อ 41 (แนวอาคาร-ถนน), ข้อ 42 (แหล่งน้ำ), ข้อ 44 (2h rule), ข้อ 48 (อาคาร-อาคาร), ข้อ 50 (หน้าต่าง-เขตที่ดิน), ข้อ 51 (1/8 height)
