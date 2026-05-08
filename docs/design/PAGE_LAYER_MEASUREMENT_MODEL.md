# PAGE_LAYER_MEASUREMENT_MODEL.md

## Purpose

This document records the accepted Phase 1 architecture model for factual measurement objects in BMA-Plan.

The model is:

```text
Page / Sheet
-> Layer
-> Object Type
-> Object Category
-> Semantic Tag
-> Measurement Profile
-> Report Target
```

This is documentation only. It does not implement new fields, UI, export behavior, tests, legal rules, OCR, AI, or pass/fail checking.

## Core Rule

Do not calculate from layer name.

Layer is for workflow, visibility, locking, and user organization. Semantic meaning must come from object metadata.

Wrong:

```text
Object is on layer "พื้นที่อาคาร" -> count as building area
```

Correct:

```text
object.semanticTag == "legal_building_area"
object.measurementProfile == "legal_building_area"
object.reportTarget == "Building Area Summary"
```

## Level Definitions

| Level | Meaning | Example |
|---|---|---|
| Page / Sheet | Drawing page and drawing role | site plan, floor plan, elevation |
| Layer | Workflow and visibility group | land, open space, dimension lines |
| Object Type | Geometry/tool shape | polygon, line, polyline, label |
| Object Category | Functional object family | area, site_fact, dimension |
| Semantic Tag | Meaning used for calculation/reporting | legal_building_area |
| Measurement Profile | Why and how the object is measured | building area profile |
| Report Target | Export/report destination | Building Area Summary |

## Page Types

Allowed `pageType` values:

| Value | Meaning |
|---|---|
| `site_plan` | Site plan / ผังบริเวณ |
| `floor_plan` | Floor plan / แปลนพื้น |
| `elevation` | Elevation / รูปด้าน |
| `section` | Section / รูปตัด |
| `detail` | Detail drawing / รายละเอียด |
| `schedule_table` | Schedule/table page / ตาราง |
| `other` | Other page type |

Each page type may later select suitable layer presets and measurement profiles. This document does not change current page setup behavior.

## Layer Presets

Layer presets are proposed workflow defaults only. They are not calculation rules.

### Site Plan

For `pageType = site_plan`:

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

Use for land parcel facts, site boundary, parcel sides, north arrow, road/access facts, building footprint, open space, setback/distance facts, outdoor parking, references, and notes.

### Floor Plan

For `pageType = floor_plan`:

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

Use for floor building area, use category area, parking area, service/common/circulation area, rooms/zones, void/shaft/court deductions, reference dimensions, labels, and notes.

### Elevation / Section

For `pageType = elevation` or `section`:

```text
01_ความสูงอาคาร
02_ระดับอ้างอิง
03_ระยะดิ่ง
04_ช่องเปิด/ผนังทึบ
05_เส้นอ้างอิง
06_ป้าย/หมายเหตุ
```

Use for height facts, reference levels, vertical dimensions, opening/wall facts, references, and notes.

## Object Types

Allowed base `objectType` values:

```text
polygon
line
polyline
arrow
label
note
marker
```

Object type is geometry only. It must not determine report membership by itself.

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

| Object Type | Object Category | Typical Meaning |
|---|---|---|
| `polygon` | `area` | floor/building/use area |
| `polygon` | `site_fact` | land area, building footprint |
| `polygon` | `deduction` | void, shaft, court |
| `line` | `dimension` | setback, height, distance |
| `arrow` | `orientation` | north arrow |
| `label` | `annotation` | label/note text |
| `line` | `reference` | reference geometry |

## Semantic Tags

Semantic tags are the primary machine-readable meaning for reporting.

### Site / Land

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

### Area

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

### Dimension / Reference

```text
scale_line
dimension_line
reference_line
setback_measure_line
height_measure_line
distance_check
```

### Annotation

```text
label
review_note
issue_marker
highlight
```

## Measurement Profiles

A Measurement Profile tells the app why an object is measured and how it should be reported. It is not a legal decision engine.

Profile schema:

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

`lawBasis` is a descriptive label for factual review context only. It must not trigger pass/fail logic in Phase 1.

## Core Profiles

| Profile | Object Type | Category | Semantic Tag | Report Target | Counting Rule |
|---|---|---|---|---|---|
| `site_land_area` | `polygon` | `site_fact` | `site_land_area` | Site Facts | included |
| `site_boundary` | `polygon` | `site_fact` | `site_boundary` | Site Facts | reference |
| `building_footprint` | `polygon` | `site_fact` | `building_footprint` | Site Facts | reference |
| `legal_building_area` | `polygon` | `area` | `legal_building_area` | Building Area Summary | included |
| `use_area` | `polygon` | `area` | `use_area` | Use Category Summary | classified |
| `parking_area` | `polygon` | `area` | `parking_area` | Parking Summary | classified |
| `deduction_area` | `polygon` | `deduction` | `deduction_area` | Deduction Summary | deducted |
| `legal_open_space` | `polygon` | `site_fact` | `legal_open_space` | Open Space Summary | included |
| `setback_measure_line` | `line` | `dimension` | `setback_measure_line` | Distance Facts | reference |
| `height_measure_line` | `line` | `dimension` | `height_measure_line` | Height Facts | reference |

Important distinctions:

- `building_footprint` is a site-plan fact, not total building floor area.
- `setback_measure_line` stores distance facts only and must not decide compliance.
- `height_measure_line` stores height facts only and must not decide compliance.
- `deduction_area` should retain parent-link intent such as `parentAreaId`, but this document does not implement linking.

## Use Categories

For `semanticTag = use_area`, allowed `useCategory` values are:

| Value | Thai Label |
|---|---|
| `residential` | อยู่อาศัย |
| `office` | สำนักงาน |
| `commercial` | พาณิชย์ |
| `service` | บริการ |
| `parking` | ที่จอดรถ |
| `mechanical` | งานระบบ |
| `storage` | เก็บของ |
| `circulation` | ทางเดิน/โถง/บันได |
| `common` | ส่วนกลาง |
| `other` | อื่น ๆ |

This remains compatible with the existing `semanticTag` and nullable `useCategory` foundation.

## Object Data Contract

Future measured objects should be able to carry these fields:

```json
{
  "id": "OBJ-001",
  "pageId": "PAGE-001",
  "pageType": "floor_plan",
  "layerId": "LAYER-001",
  "layerName": "01_พื้นที่อาคารตามกฎหมาย",
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

The existing implementation is not changed by this document. Future implementation must preserve raw geometry recalculation from scale and must not derive measured meaning from layer names.

## UI Contract For Future Sprints

Future UI work should follow these constraints:

- Page setup should expose `pageType`, `floorName`, `pageLabel`, and `discipline` when implemented.
- Layer panel should show preset layers by page type, with visible/locked/object count.
- Area tool may later select a Measurement Profile before drawing.
- Properties panel may later show Object Category, Semantic Tag, Measurement Profile, Report Target, Law Basis, Counting Rule, and notes.
- UI must not show legal pass/fail judgment.
- Existing Area/Land/Opening toolbar behavior must remain stable unless a dedicated implementation sprint changes it with regression coverage.

## Report Targets

Supported target names for future report/export mapping:

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

Future export fields should include:

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

## Legal Boundary

Allowed in Phase 1:

- Store factual area, length, orientation, and count values.
- Store descriptive measurement purpose labels.
- Store descriptive legal basis labels for human review context.
- Organize objects for future manual review.

Forbidden in Phase 1:

- automatic legal pass/fail
- FAR compliance result
- OSR compliance result
- setback compliance result
- parking requirement judgment
- Rule Engine
- OCR
- AI checker

## Implementation Split

Recommended next implementation sprints:

1. Add `measurementProfile`, `objectCategory`, `reportTarget`, `lawBasis`, and `countingRule` fields to object metadata with backward-compatible normalization.
2. Add a Measurement Profile selector for Area/Land/Opening flows without changing geometry.
3. Add pageType-based layer presets behind a compatibility guard.
4. Add report target mapping/export columns.
5. Add report preview tables using factual rows only.

Stop if implementation requires a layer rewrite, geometry rewrite, risky save/load migration, UI redesign, or legal pass/fail logic.

