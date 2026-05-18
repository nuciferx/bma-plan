ได้ ใช้ไฟล์นี้เป็นตัวต่อได้เลย

ชื่อไฟล์:

```text
RUN_PAGE_LAYER_MEASUREMENT_MODEL.md
```

เนื้อหา:

````md
# RUN_PAGE_LAYER_MEASUREMENT_MODEL.md — Page → Layer → Object → Category → Tag → Profile → Report Model

## Goal

ออกแบบและวางฐานระบบการทำงานของ BMA-Plan ให้รองรับการวัดพื้นที่และข้อเท็จจริงตามงานตรวจแบบจริง โดยใช้โครงสร้าง:

```text
Page / Sheet
→ Layer
→ Object Type
→ Object Category
→ Semantic Tag
→ Measurement Profile
→ Report Target
````

แนวคิดหลัก:

```text
Layer = ชั้นงาน / การมองเห็น / workflow
Object Type = รูปทรงหรือเครื่องมือที่ใช้วาด
Object Category = หมวดของสิ่งที่วาด
Semantic Tag = ความหมายที่ระบบใช้คำนวณหรือรายงาน
Measurement Profile = วิธีวัด / ฐานนิยาม / วัตถุประสงค์การวัด
Report Target = ตารางหรือรายงานปลายทาง
```

This sprint is still Phase 1 factual measurement support only.

Do not add automatic legal pass/fail checking.

---

## Background

จากการวิเคราะห์ตารางพื้นที่ที่ใช้จริงตามงานอนุญาต และกฎหมายที่เกี่ยวข้อง พบว่าโปรแกรมไม่ควรมีแค่เครื่องมือ “วัดพื้นที่” แบบเดียว

การวัดจริงต้องแยกตามวัตถุประสงค์ เช่น:

* พื้นที่อาคารตามกฎหมาย
* พื้นที่ดินที่ใช้เป็นที่ตั้งอาคาร
* กรอบอาคารบนผังบริเวณ
* ที่ว่างตามกฎหมาย
* พื้นที่ตามประเภทการใช้
* พื้นที่จอดรถ
* พื้นที่บริการ / งานระบบ
* พื้นที่หักออก เช่น void / shaft / court
* เส้นวัดระยะ / ระยะร่น / ระยะตรวจสอบ
* ทิศ / ถนน / ด้านที่ดิน

ดังนั้นระบบต้องแยก “ชั้นงาน” ออกจาก “ความหมายของ object”

---

## Core Principle

Do not calculate from layer name.

Wrong:

```text
ถ้าอยู่ layer ชื่อ "พื้นที่อาคาร" → นับเป็นพื้นที่อาคาร
```

Correct:

```text
object.semanticTag == "legal_building_area"
→ นับใน Building Area Summary
```

Layer ใช้เพื่อจัด workflow และการมองเห็น
Semantic Tag ใช้เพื่อคำนวณและส่งออก report

---

## Data Hierarchy

Use this hierarchy:

```text
Page
→ Layer
→ Object Type
→ Object Category
→ Semantic Tag
→ Measurement Profile
→ Report Target
```

### Meaning of Each Level

| Level               | Meaning                  | Example                                |
| ------------------- | ------------------------ | -------------------------------------- |
| Page                | หน้าแบบ / แผ่นแบบ        | ผังบริเวณ, แปลนชั้น 1, รูปด้าน         |
| Layer               | ชั้นงานตรวจ / การมองเห็น | ที่ดิน, ที่ว่าง, ระยะวัด               |
| Object Type         | รูปทรง                   | polygon, line, label                   |
| Object Category     | หมวด object              | area, site_fact, dimension, annotation |
| Semantic Tag        | ความหมาย                 | legal_building_area, legal_open_space  |
| Measurement Profile | วิธีวัด                  | พื้นที่อาคารตามกฎหมาย                  |
| Report Target       | ตารางปลายทาง             | Building Area Summary                  |

---

## Page Types

Each page should have a `pageType`.

Allowed page types:

```text
site_plan          = ผังบริเวณ
floor_plan         = แปลนพื้น
elevation          = รูปด้าน
section            = รูปตัด
detail             = รายละเอียด
schedule_table     = ตาราง
other              = อื่น ๆ
```

Each `pageType` should load a suitable layer preset and measurement profile set.

---

## Layer Presets

### 1. Site Plan Layer Preset

For `pageType = site_plan`

```text
01_ที่ดิน/แนวเขต
02_ด้านที่ดิน
03_ทิศ/ถนน/ทางเข้าออก
04_กรอบอาคาร/แนวอาคาร
05_ที่ว่าง
06_ระยะวัด/ระยะร่น
07_จอดรถภายนอก
08_เส้นอ้างอิง
09_ป้าย/หมายเหตุ
```

Use for:

* แปลงที่ดิน
* แนวเขต
* ด้านติดถนน
* ทิศเหนือ
* ถนน
* อาคารบนผังบริเวณ
* ที่ว่าง
* ระยะจากอาคารถึงแนวเขต
* ทางรถดับเพลิง
* ทางเข้าออก

---

### 2. Floor Plan Layer Preset

For `pageType = floor_plan`

```text
01_พื้นที่อาคารตามกฎหมาย
02_พื้นที่ตามประเภทการใช้
03_พื้นที่หัก/ช่องเปิด
04_ห้อง/โซน
05_ทางเดิน/บันได/โถง
06_ที่จอดรถภายใน
07_เส้นวัด/ระยะอ้างอิง
08_ป้าย/หมายเหตุ
```

Use for:

* พื้นที่อาคารแต่ละชั้น
* gross floor area
* use area
* พื้นที่พักอาศัย
* สำนักงาน
* พาณิชย์
* บริการ
* ที่จอดรถ
* void / shaft / court
* พื้นที่หักออก
* gross / deduction / net

---

### 3. Elevation / Section Layer Preset

For `pageType = elevation` or `section`

```text
01_ความสูงอาคาร
02_ระดับอ้างอิง
03_ระยะดิ่ง
04_ช่องเปิด/ผนังทึบ
05_เส้นอ้างอิง
06_ป้าย/หมายเหตุ
```

Use for:

* ความสูงอาคาร
* ระดับพื้นดิน / ถนน / ดาดฟ้า
* รูปตัด
* ระยะดิ่ง
* ช่องเปิด
* ผนังทึบ

---

## Object Types

Allowed base object types:

```text
polygon
line
polyline
arrow
label
note
marker
```

Object type is geometry only.

Do not use object type alone for report calculation.

---

## Object Categories

Allowed `objectCategory` values:

```text
area
site_fact
dimension
orientation
annotation
deduction
reference
```

Examples:

```text
polygon + area
line + dimension
arrow + orientation
label + annotation
polygon + site_fact
polygon + deduction
```

---

## Semantic Tags

### Site / Land Tags

```text
site_land_area
site_boundary
parcel_side
road_line
frontage_line
access_line
north_arrow
building_footprint
```

### Legal / Area Tags

```text
legal_building_area
use_area
parking_area
service_area
common_area
legal_open_space
deduction_area
excluded_area
```

### Dimension / Reference Tags

```text
scale_line
dimension_line
reference_line
setback_measure_line
height_measure_line
distance_check
```

### Annotation Tags

```text
label
review_note
issue_marker
highlight
```

---

## Measurement Profiles

Measurement Profile tells the app why the object is being measured.

Each profile should define:

```json
{
  "profileId": "...",
  "label": "...",
  "objectType": "...",
  "objectCategory": "...",
  "semanticTag": "...",
  "defaultLayerPresetKey": "...",
  "requiresFloor": true,
  "requiresUseCategory": false,
  "reportTarget": "...",
  "lawBasis": "...",
  "countingRule": "included"
}
```

---

## Core Measurement Profiles

### 1. Site Land Area

```json
{
  "profileId": "site_land_area",
  "label": "พื้นที่ดินที่ใช้เป็นที่ตั้งอาคาร",
  "objectType": "polygon",
  "objectCategory": "site_fact",
  "semanticTag": "site_land_area",
  "defaultLayer": "01_ที่ดิน/แนวเขต",
  "requiresFloor": false,
  "requiresUseCategory": false,
  "reportTarget": "Site Facts",
  "lawBasis": "พื้นที่ดินที่ใช้เป็นที่ตั้งอาคาร",
  "countingRule": "included"
}
```

Use for:

* พื้นที่แปลงที่ดิน
* ฐานคำนวณ FAR
* ฐานคำนวณที่ว่าง

---

### 2. Site Boundary

```json
{
  "profileId": "site_boundary",
  "label": "กรอบที่ดิน / แนวเขต",
  "objectType": "polygon",
  "objectCategory": "site_fact",
  "semanticTag": "site_boundary",
  "defaultLayer": "01_ที่ดิน/แนวเขต",
  "requiresFloor": false,
  "requiresUseCategory": false,
  "reportTarget": "Site Facts",
  "lawBasis": "แผนผังบริเวณ / แนวเขตที่ดิน",
  "countingRule": "reference"
}
```

Use for:

* ด้านที่ดิน
* แนวเขต
* ระยะจากอาคารถึงเขตที่ดิน
* site-side metadata

---

### 3. Building Footprint

```json
{
  "profileId": "building_footprint",
  "label": "กรอบอาคารบนผังบริเวณ",
  "objectType": "polygon",
  "objectCategory": "site_fact",
  "semanticTag": "building_footprint",
  "defaultLayer": "04_กรอบอาคาร/แนวอาคาร",
  "requiresFloor": false,
  "requiresUseCategory": false,
  "reportTarget": "Site Facts",
  "lawBasis": "แนวอาคาร / ขอบเขตนอกสุดของอาคาร",
  "countingRule": "reference"
}
```

Use for:

* ตรวจตำแหน่งอาคารในแปลง
* ระยะร่น
* ระยะจากแนวเขต
* ถนนรอบอาคาร

Important:

* Building footprint is not the same as total building floor area.

---

### 4. Legal Building Area

```json
{
  "profileId": "legal_building_area",
  "label": "พื้นที่อาคารตามกฎหมาย",
  "objectType": "polygon",
  "objectCategory": "area",
  "semanticTag": "legal_building_area",
  "defaultLayer": "01_พื้นที่อาคารตามกฎหมาย",
  "requiresFloor": true,
  "requiresUseCategory": false,
  "reportTarget": "Building Area Summary",
  "lawBasis": "พื้นที่อาคาร",
  "countingRule": "included"
}
```

Use for:

* พื้นที่อาคารแต่ละชั้น
* พื้นที่รวมทุกชั้น
* อาคารขนาดใหญ่ / อาคารขนาดใหญ่พิเศษ
* FAR facts
* ตารางสรุปพื้นที่

---

### 5. Use Area

```json
{
  "profileId": "use_area",
  "label": "พื้นที่ตามประเภทการใช้",
  "objectType": "polygon",
  "objectCategory": "area",
  "semanticTag": "use_area",
  "defaultLayer": "02_พื้นที่ตามประเภทการใช้",
  "requiresFloor": true,
  "requiresUseCategory": true,
  "reportTarget": "Use Category Summary",
  "lawBasis": "ประเภทการใช้อาคาร",
  "countingRule": "classified"
}
```

Use for:

* พื้นที่พักอาศัย
* สำนักงาน
* พาณิชย์
* บริการ
* ที่จอดรถ
* ส่วนกลาง
* งานระบบ
* อาคารผสม

---

### 6. Parking Area

```json
{
  "profileId": "parking_area",
  "label": "พื้นที่จอดรถ",
  "objectType": "polygon",
  "objectCategory": "area",
  "semanticTag": "parking_area",
  "defaultLayer": "06_ที่จอดรถภายใน",
  "requiresFloor": true,
  "requiresUseCategory": false,
  "reportTarget": "Parking Summary",
  "lawBasis": "พื้นที่จอดรถ / อาคารจอดรถ",
  "countingRule": "classified"
}
```

Additional fields:

```json
{
  "parkingLocation": "indoor | outdoor | basement | mechanical",
  "parkingCount": null
}
```

---

### 7. Deduction Area

```json
{
  "profileId": "deduction_area",
  "label": "พื้นที่หัก / ช่องเปิด",
  "objectType": "polygon",
  "objectCategory": "deduction",
  "semanticTag": "deduction_area",
  "defaultLayer": "03_พื้นที่หัก/ช่องเปิด",
  "requiresFloor": true,
  "requiresUseCategory": false,
  "reportTarget": "Deduction Summary",
  "lawBasis": "พื้นที่ที่ไม่นับรวมตามการจัดทำรายงาน",
  "countingRule": "deducted"
}
```

Additional fields:

```json
{
  "deductionType": "void | shaft | court | roof_deck | external_roof_stair | other",
  "parentAreaId": null
}
```

---

### 8. Legal Open Space

```json
{
  "profileId": "legal_open_space",
  "label": "ที่ว่างตามกฎหมาย",
  "objectType": "polygon",
  "objectCategory": "site_fact",
  "semanticTag": "legal_open_space",
  "defaultLayer": "05_ที่ว่าง",
  "requiresFloor": false,
  "requiresUseCategory": false,
  "reportTarget": "Open Space Summary",
  "lawBasis": "ที่ว่าง",
  "countingRule": "included"
}
```

Use for:

* ที่ว่างภายนอก
* พื้นที่ไม่มีหลังคาปกคลุม
* พื้นที่ใช้คำนวณอัตราส่วนที่ว่าง

---

### 9. Setback Measure Line

```json
{
  "profileId": "setback_measure_line",
  "label": "เส้นวัดระยะจากอาคารถึงแนวเขต",
  "objectType": "line",
  "objectCategory": "dimension",
  "semanticTag": "setback_measure_line",
  "defaultLayer": "06_ระยะวัด/ระยะร่น",
  "requiresFloor": false,
  "requiresUseCategory": false,
  "reportTarget": "Distance Facts",
  "lawBasis": "ระยะจากอาคารถึงแนวเขต / ถนน",
  "countingRule": "reference"
}
```

Important:

* This stores facts only.
* Do not decide pass/fail.

---

### 10. Height Measure Line

```json
{
  "profileId": "height_measure_line",
  "label": "เส้นวัดความสูงอาคาร",
  "objectType": "line",
  "objectCategory": "dimension",
  "semanticTag": "height_measure_line",
  "defaultLayer": "01_ความสูงอาคาร",
  "requiresFloor": false,
  "requiresUseCategory": false,
  "reportTarget": "Height Facts",
  "lawBasis": "ความสูงอาคาร",
  "countingRule": "reference"
}
```

---

## Use Categories

For `use_area`, use:

```text
residential
office
commercial
service
parking
mechanical
storage
circulation
common
other
```

Thai labels:

```text
residential = อยู่อาศัย
office = สำนักงาน
commercial = พาณิชย์
service = บริการ
parking = ที่จอดรถ
mechanical = งานระบบ
storage = เก็บของ
circulation = ทางเดิน/โถง/บันได
common = ส่วนกลาง
other = อื่น ๆ
```

---

## Object Data Model

Each measured object should have:

```json
{
  "id": "OBJ-001",
  "pageId": "PAGE-001",
  "pageType": "floor_plan",
  "layerId": "LAYER-001",
  "objectType": "polygon",
  "objectCategory": "area",
  "semanticTag": "legal_building_area",
  "measurementProfile": "legal_building_area",
  "reportTarget": "Building Area Summary",
  "floor": "ชั้น 1",
  "useCategory": null,
  "area_m2": 1457.77,
  "length_m": null,
  "countingRule": "included",
  "lawBasis": "พื้นที่อาคาร",
  "properties": {}
}
```

---

## UI Requirements

### Page Setup

Each page must have:

```text
pageType
floorName
pageLabel
discipline
```

Examples:

```text
pageType = site_plan
pageType = floor_plan
pageType = elevation
pageType = section
```

---

### Layer Panel

Layer panel should show layers based on pageType preset.

Do not use layer name for calculation.

Layer row should show:

```text
Layer name
visible
locked
object count
```

Future:

* rename layer
* reorder layer
* group layer

But this sprint may only define the model.

---

### Area Tool

When user clicks “พื้นที่”, ask/select Measurement Profile:

```text
พื้นที่อาคารตามกฎหมาย
พื้นที่ตามประเภทการใช้
พื้นที่จอดรถ
พื้นที่หัก/ช่องเปิด
ที่ว่างตามกฎหมาย
พื้นที่ดินที่ใช้เป็นที่ตั้งอาคาร
กรอบอาคารบนผังบริเวณ
```

After profile selection, object defaults are assigned:

```text
layer
objectCategory
semanticTag
measurementProfile
reportTarget
lawBasis
countingRule
```

---

### Properties Panel

When selecting object, show:

```text
Name
Page
Layer
Object Type
Object Category
Semantic Tag
Measurement Profile
Floor
Use Category
Report Target
Law Basis
Counting Rule
Area / Length
Notes
```

Do not show pass/fail legal judgment.

---

## Report Targets

Supported report targets:

```text
Site Facts
Building Area Summary
Use Category Summary
Deduction Summary
Open Space Summary
Parking Summary
Distance Facts
Height Facts
Audit Log
```

---

## Export Requirements

XLSX should eventually support sheets or sections:

```text
Site Facts
Building Area Summary
Use Category Summary
Deduction Summary
Open Space Summary
Parking Summary
Distance Facts
Height Facts
Audit Log
```

For this sprint, if full report generation is too large, at minimum add fields to object export:

```text
pageType
layerName
objectType
objectCategory
semanticTag
measurementProfile
useCategory
reportTarget
lawBasis
countingRule
```

---

## Legal Boundary

This model is for factual measurement only.

Allowed:

* store legal basis label
* store measurement purpose
* store area/length facts
* organize objects for future legal review

Forbidden:

* automatic pass/fail
* FAR compliance result
* OSR compliance result
* setback compliance result
* parking requirement judgment
* rule engine
* OCR
* AI checker

---

## Acceptance Criteria

Pass only if:

1. Page → Layer → Object → Category → Tag → Profile → Report model is documented.
2. Page types are defined.
3. Layer presets for site plan, floor plan, elevation/section are defined.
4. Measurement profiles are defined.
5. Object data model supports pageType, layerId, objectType, objectCategory, semanticTag, measurementProfile, reportTarget.
6. No automatic legal pass/fail is added.
7. Existing semanticTag/useCategory foundation remains compatible.
8. Existing Area/Land toolbar behavior remains unchanged.
9. Existing save/load remains unchanged unless explicitly required.
10. Existing tests pass if code is touched.

---

## Implementation Strategy

Do not implement everything at once.

Recommended split:

```text
Sprint 1 = Document model only
Sprint 2 = Add measurementProfile field to object model
Sprint 3 = Add profile selector in Area tool
Sprint 4 = Add pageType-based layer presets
Sprint 5 = Add report target mapping/export
Sprint 6 = Add report preview table
```

---

## Stop Conditions

Stop if:

* implementation requires layer rewrite
* save/load risk is high
* object geometry would change
* legal pass/fail logic appears
* UI redesign begins
* scope expands beyond model foundation

---

## Final Instruction

This model is the new foundation.

Do not treat Layer as calculation logic.

Use:

```text
Layer = workflow / visibility
Semantic Tag = meaning
Measurement Profile = how to measure
Report Target = where it goes
```

````

เอาไฟล์นี้ไปวางใน root ก่อน หรือถ้าจัดระเบียบแล้วให้วางใน:

```text
docs/design/PAGE_LAYER_MEASUREMENT_MODEL.md
````

และถ้าจะให้ Codex ใช้งานต่อ ให้สร้างไฟล์ sprint แยกอีกตัวชื่อ:

```text
RUN_DOCUMENT_PAGE_LAYER_MEASUREMENT_MODEL.md
```

ให้มัน copy แนวคิดนี้ไปลง docs แล้ว update index/current status โดย **ยังไม่แก้ code**.
