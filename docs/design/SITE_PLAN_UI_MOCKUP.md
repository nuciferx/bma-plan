# SITE_PLAN_UI_MOCKUP.md — Site Plan Measurement UI Mockup & Programme Guide

> Date: 2026-05-13 (reconciled 2026-05-14 — field names aligned to shipped Phase I-A schema; `.markers`→`.parking` fixed; §11 sprint split revised for Pack D + I-A/I-B1 done)
> Status: DESIGN MOCKUP — no source code; defines the UI surface and user journey
> Parent: `docs/design/SITE_PLAN_MEASUREMENT_PLAN.md` (what to measure)
> This doc: how the user interacts with it

---

## 1. Scope

This document is the **UI design + programme guideline** for site plan (ผังบริเวณ) measurement. It defines:

- The user journey from "open PDF" to "ready to export site plan summary"
- ASCII mockups of every screen/state involved
- Component specifications (what each control does, its state, its events)
- Data flow (which UI control writes which `.bmaplan` field; which field drives which display)
- Programme guideline (where each piece goes in `proto/ui.html`)

This doc does **not** add code; it defines the shape of code to be added in Phase I-A through I-D implementation sprints.

---

## 2. Phase 1 Hard Rule for UI

```
UI shows FACTS.
UI does NOT show "ผ่าน/ไม่ผ่าน" verdict, ✓/✗ badges, color-coded pass/fail.
```

When the user has filled in a reference threshold and the measured value exceeds or falls short, the UI shows the two numbers **side by side, neutrally**. The user reads them and makes the legal judgment themselves.

Allowed:
- `FAR: 5.91 : 1   |  เกณฑ์ผู้ใช้: ≤ 10.0`
- `OSR: 49.7%      |  เกณฑ์ผู้ใช้: ≥ 30%`

Forbidden:
- `FAR: 5.91 ✓ ผ่าน`
- ❌ red/green color-coded badges based on the comparison
- ❌ "ผ่าน 4 จาก 5 รายการ" verdict summary

This rule applies to **every** UI element described below.

---

## 3. User Journey

```
[A] Open PDF
     ↓
[B] Project Setup
     - tag pages (one or more pages = "site")
     - fill building classification / use type
     - fill user-defined limits (FAR/OSR/permeable/setback)
     - fill zone code, frontage road width
     ↓
[C] Switch to site page → Start Site Measurement
     ↓
[D] Step 1 — วาดเขตที่ดิน (site_land_area polygon)
     ↓
[E] Step 2 — Tag edge ที่ดิน (front_road / side_left / side_right / back / canal)
     ↓
[F] Step 3 — วาดปกคลุมอาคาร (building_coverage polygon) → fill height + wallType per edge
     ↓
[G] Step 4 — วาดที่ว่าง / ซึมน้ำ / hardscape (optional polygons)
     ↓
[H] Step 5 — Place markers (parking, parking_fire, parking_ambulance, entrance, aed)
     ↓
[I] Step 6 — Measure setbacks (auto-suggest 4 directions, user confirms)
     ↓
[J] Step 7 — Open Site Summary tab → review measured vs reference values
     ↓
[K] Step 8 — Export XLSX (includes "สรุปผังบริเวณ" sheet)
```

Steps D through I are tracked in a **workflow stepper** widget (see §4.5).

---

## 4. Screen Mockups

All mockups are at viewport 1440×900 unless noted. Existing UI elements that stay unchanged are not redrawn — only the additions / modifications are highlighted with `🆕` or `🔄`.

### 4.1 Project Setup screen — site plan additions

The existing Project Setup screen already has: file info, page list with tag dropdowns, project name, customer. The additions live in a new card group below the existing fields.

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Project Setup                                                  [เริ่มตรวจ] │
├──────────────────────────────────────────────────────────────────────────┤
│  ── ข้อมูลโปรเจกต์ ──────────────────────────────────────────────         │
│  ชื่อโปรเจกต์: [Sindhorn Midtown          ]                                │
│  เจ้าของ:    [บริษัท สยามสินธร จำกัด     ]                                  │
│  เลขรับ:    [ข.1 153 / 2568              ]                                 │
│                                                                            │
│  ── ประเภทอาคาร (ใช้ตัดสินใจกฎที่อ้างอิง) 🆕 ─────────────────────         │
│  การใช้งาน:   [▼ โรงแรม + พาณิชย์รวม                ]                       │
│              (อยู่อาศัย / พาณิชย์ / สำนักงาน / โรงงาน / คลังสินค้า /        │
│               โรงแรม / โรงพยาบาล / โรงมหรสพ / สถานบริการ / รวม)            │
│  ขนาด:        ( ) ทั่วไป     ( ) ใหญ่     ( ) สูง (≥23ม.)   (●) ใหญ่พิเศษ │
│              ↑ auto-detect จาก height + GFA แต่ override ได้                │
│  ความสูงสุดที่กรอก: [110.60] ม.   ความสูงดาดฟ้า: [104.30] ม.                │
│                                                                            │
│  ── ผังเมือง + ถนนหน้าที่ดิน 🆕 ─────────────────────────────             │
│  โซนผังเมือง:        [พ.5-2 (สีแดง)               ]                        │
│  ถนนหน้าที่ดิน:      [ถนนหลังสวน        ] กว้าง [16.90] ม.                 │
│                                                                            │
│  ── เกณฑ์อ้างอิง (ผู้ใช้กรอกตามผังเมือง + กฎกระทรวง) 🆕 ──────────         │
│  FAR ไม่เกิน:       [10.0]                                                 │
│  OSR ไม่น้อยกว่า:    [3.0  ] %  ← ตามผังเมือง (อาจไม่เท่ามร.33 ข้อ 6)     │
│  ซึมน้ำไม่น้อยกว่า:  [50.0 ] %                                              │
│  ระยะร่นหน้า:       [6.0  ] ม.                                              │
│  ระยะร่นข้าง:       [2.0  ] ม.                                              │
│  ระยะร่นหลัง:       [2.0  ] ม.                                              │
│  ระยะรอบอาคาร:      [6.0  ] ม. ← สำหรับอาคารสูง/ใหญ่พิเศษ (มร.33 ข้อ 3)   │
│                                                                            │
│  ⓘ เกณฑ์ทั้งหมดที่กรอก จะนำมาแสดงเทียบ "วัดได้ X / เกณฑ์ Y" ในหน้าสรุป      │
│  ⓘ ระบบไม่ตัดสินผ่าน/ไม่ผ่าน — ใช้สำหรับเปรียบเทียบเท่านั้น                  │
│                                                                            │
│  ── Pages (existing) ────────────────────────────────────                 │
│  📄 หน้า 1   tag: [▼ ผังบริเวณ (site)        ]                            │
│  📄 หน้า 2   tag: [▼ ผังชั้น 1 (plan)        ]                            │
│  ...                                                                       │
└──────────────────────────────────────────────────────────────────────────┘
```

**State stored** — reconciled with the shipped Phase I-A schema (2026-05-14). The ASCII labels above are illustrative; this list is the authoritative field spec.

Shipped in Phase I-A (`984eb7e`) — `projectInfo`:
- `projectInfo.buildingClassification` (`general | large | tall | extra_large`)
- `projectInfo.buildingUseType`
- `projectInfo.zoneCode`
- `projectInfo.siteAccessRoadWidth_m` — ⚠️ this mockup originally called it `frontageRoadWidth_m`; the shipped name is `siteAccessRoadWidth_m` (per `MEASUREMENT_PLAN §9`). Use the shipped name.
- `projectInfo.userDefinedLimits = { far_max, osr_min_pct, permeable_min_pct, setback_front_min_m, setback_side_min_m, setback_back_min_m }`

Shipped in Phase I-A — object-level (NOT `projectInfo`):
- `poly.buildingHeight_m` — per `building_coverage` polygon (the per-building height for มร.55 ข้อ 44/48). There is **no** project-level `buildingHeight_m`; the per-object field is the source of truth.

Deferred — add **additively** in the sprint that first needs it (do NOT rename anything shipped):
- `projectInfo.frontageRoadName` (text label) — when Project Setup UI is next touched
- `poly.buildingRoofHeight_m` (per-building roof-deck height) — in I-B3 (Properties panel)
- `projectInfo.userDefinedLimits.road_clearance_min_m` (ระยะรอบอาคาร, มร.33 ข้อ 3) — in I-B3 or I-C

### 4.2 Site Plan canvas — first entry

When user clicks "เริ่มตรวจ" and navigates to a site page, the workspace shows a guided overlay if no measurements yet:

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Title bar │ Menu bar (existing 13 items)                  │ topbar      │
├──────────────────────────────────────────────────────────────────────────┤
│ [📂Open][⚙Setup][📏Scale][🎯Active Layer▼][💾Save]            🟢Saved   │
├──────────────────────────────────────────────────────────────────────────┤
│ [Ribbon: ✏️Pan │ 🎯Select │ 📏Set Scale │ ⬛Area │ ◯Open │ ─Ref │ ...] │
├─────────┬─────────────────────────────────────────────────┬─────────────┤
│ Left    │                                                  │ Right       │
│ panel   │       Canvas / PDF Viewer                        │ panel       │
│         │                                                  │             │
│ Tabs:   │   ┌──────────────────────────────────┐          │ Layers:     │
│ Sheets  │   │ 🏙️ ผังบริเวณ — ยังไม่ได้วัด       │          │ ─────────── │
│ Objects │   │                                   │          │ ⬛ 01_ที่ดิน-│
│ Props   │   │ ลำดับขั้นตอน:                      │          │   แนวเขต   │
│         │   │ ① วาดเขตที่ดิน      [▶ เริ่ม]       │ 🆕       │   👁🔒 (0) │
│ ─────── │   │ ② Tag edge ที่ดิน                  │          │             │
│ Site    │   │ ③ วาดปกคลุมอาคาร                  │          │ ⬛ 02_ที่ว่าง│
│ stepper │   │ ④ วาดที่ว่าง / ซึมน้ำ              │          │   👁🔒 (0)  │
│ widget  │   │ ⑤ ใส่ markers จอดรถ              │          │             │
│ 🆕      │   │ ⑥ ตรวจ setback 4 ทิศ              │          │ ⬛ 03_ลานจอด│
│         │   │ ⑦ ดู Summary                       │          │   👁🔒 (0)  │
│         │   │                                    │          │             │
│         │   │ ⓘ ทำตามลำดับ หรือคลิกขั้นใดก็ได้    │          │ ─Ref geom   │
│         │   └──────────────────────────────────┘          │ ─Labels     │
│         │                                                  │             │
│         │   [PDF page background visible underneath]      │             │
├─────────┴─────────────────────────────────────────────────┴─────────────┤
│ Status: Tool=─ │ Scale=★1:200 │ Objects=0 │ Layer=ที่ดิน │ 🟢 saved │ 1/45│
└──────────────────────────────────────────────────────────────────────────┘
```

The site stepper widget on the left replaces the generic workflow card **only on site pages**. On floor / elevation / section pages, it shows the regular workflow.

### 4.3 Ribbon toolbar — site plan section

The existing ribbon has groups for File, Workflow, Tools. Add a Site Plan group (visible only when `pageType === "site"`):

```
┌─ Ribbon ───────────────────────────────────────────────────────────────┐
│  ✏️Pan │ 🎯Select │ 📏Set Scale │                                       │
│  ⬛Area │ ◯Open │ ─Ref │ T̲Label │ ↶Undo │ 🗑Del │ 💾Save │ 📤Export  │
│                                                                          │
│  ── ผังบริเวณ (visible only on site pages) 🆕 ───────────────────────  │
│  ⬛land │ ⬛cov │ 🟩open │ 💧perm │ 🟫hard │ 🅿️outdoor │ 🛣️road        │
│  🅿️ │ ♿ │ 🚒 │ 🚑 │ 🚪 │ ➕AED │ 📍sign │ 🌳tree                       │
└──────────────────────────────────────────────────────────────────────────┘
```

Hotkeys (added to existing keydown handler):
- `Shift+1` = land (existing)
- `Shift+2` = building_coverage 🆕
- `Shift+3` = open_space 🆕
- `Shift+4` = permeable 🆕
- `Shift+5` = parking_outdoor 🆕
- `M` then `1`-`5` cycle markers: parking → disabled → fire → ambulance → entrance 🆕

Each button calls existing `setMode("area")` + `setAreaType(<type>)` after Phase I-A schema additions.

### 4.4 Measure dropdown menu — site plan additions

The existing Measure dropdown (Phase G) has 14 items. Add a sub-section:

```
[Measure ▼]
─────────────────────────────
📐 Set Scale                      S
🚫 Reset Page Scale
🔁 Verify Scale (mark verified)
─────────────────────────────
⬛ Area Polygon                    A
◯ Opening (cutout)                O
─ Reference Line                   R
T̲ Label                            L
─────────────────────────────
🏙️ ผังบริเวณ (Site) ► 🆕
   ├─ ⬛ พื้นที่ดิน
   ├─ ⬛ ปกคลุมอาคาร
   ├─ 🟩 ที่ว่าง
   ├─ 💧 ซึมน้ำ
   ├─ 🟫 Hardscape
   ├─ 🅿️ จอดรถ outdoor (poly)
   ├─ 🛣️ ถนนภายใน
   ├─ ─────────────────
   ├─ 🅿️ Marker: จอดรถ
   ├─ ♿ Marker: จอดผู้พิการ
   ├─ 🚒 Marker: จอดดับเพลิง
   ├─ 🚑 Marker: จอดพยาบาล
   ├─ 🚪 Marker: ทางเข้า-ออก
   ├─ ➕ Marker: AED
   └─ 📍 Marker: ป้ายโฆษณา
─────────────────────────────
🧭 Set North Arrow                 N
📐 Tag Land Edges                  E
```

This adds **1 entry** to the existing dropdown (the cascading "ผังบริเวณ" submenu). Implementation reuses the existing nested-submenu pattern from "Snap Modes" and "Set Active Layer".

### 4.5 Site stepper widget (left panel, replaces workflow card on site pages)

```
┌─ ลำดับขั้นตอน — ผังบริเวณ ─────────┐
│                                       │
│ ✅ ① เขตที่ดิน          1 poly        │
│ ✅ ② Tag edge ที่ดิน    4/4 edge       │
│ ⏳ ③ ปกคลุมอาคาร       1 poly         │
│ ⏳   └ ใส่ height + wall            │
│ ⬜ ④ ที่ว่าง / ซึมน้ำ    0 poly        │
│ ⬜ ⑤ Markers จอดรถ    0/3 type       │
│ ⬜ ⑥ Setback 4 ทิศ    0/4 measured   │
│ ⬜ ⑦ Summary           ▶ ดูสรุป       │
│                                       │
│ [แสดงทุกขั้น] [ซ่อนที่ทำแล้ว]          │
└───────────────────────────────────────┘
```

State markers:
- ✅ = complete (criteria satisfied per Phase I-A schema)
- ⏳ = in progress (some criteria met, some missing)
- ⬜ = not started

Click on a step → navigates to the relevant tool / opens the relevant property panel.

The stepper is read-only — it never blocks the user from doing things out of order.

### 4.6 Properties panel — site-specific fields per object type

When user selects a `building_coverage` polygon:

```
┌─ Properties — Object B-01 ──────────────────────┐
│ ID:        B-01                                   │
│ Name:      [อาคาร A (โรงแรม)        ]              │
│ Layer:     [01_ที่ดิน-แนวเขต         ▼]            │
│ Type:      [ปกคลุมอาคาร              ▼]            │
│                                                    │
│ ── Measurement ──────────────────────────────    │
│ Area:      1,944.40 ตร.ม.                          │
│ Perimeter: 173.45 ม.                                │
│ Color:     [🟦] Opacity: [▬▬▬○──] 18%             │
│ Label:     [● auto  ○ custom  ○ hidden]            │
│                                                    │
│ ── ผังบริเวณ-specific 🆕 ──────────────────────  │
│ ความสูงสูงสุด:    [110.60] ม.                       │
│ ความสูงดาดฟ้า:   [104.30] ม.                       │
│                                                    │
│ Edge wallType:                                     │
│   E0 (ทิศเหนือ ~7.84ม.):  ( ) ทึบ  (●) มีหน้าต่าง │
│   E1 (ทิศตะวันออก 8.19ม.):( ) ทึบ  (●) มีหน้าต่าง │
│   E2 (ทิศใต้ 12.00ม.):   (●) ทึบ  ( ) มีหน้าต่าง   │
│   E3 (ทิศตะวันตก 7.22ม.):( ) ทึบ  (●) มีหน้าต่าง │
│                                                    │
│ ⓘ wallType ใช้ในการวัดอ้างอิงตาม มร.55 ข้อ 48/50 │
│                                                    │
│ ── Metadata (existing 5 fields) ─────────────    │
│ semanticTag:      [building_coverage      ▼]      │
│ measurementProfile:[building_footprint   ▼]      │
│ objectCategory:   [building              ▼]      │
│ reportTarget:     [ผังบริเวณ: ปกคลุม      ▼]      │
│ lawBasis:         [มร.55 ข้อ 36-39        ]      │
│ countingRule:     [—                     ▼]      │
└────────────────────────────────────────────────────┘
```

When user selects a `site_land_area` polygon — properties show the existing land edge panel (no change). When selecting `open_space`, `permeable`, `hardscape` — properties show the basic measurement panel (no extra building-specific fields).

When user selects a marker (any `markerType`):

```
┌─ Properties — Marker PK-01 ─────────┐
│ ID:        PK-01                      │
│ Type:      [🚒 จอดรถดับเพลิง   ▼] 🆕   │
│ Note:      [ใต้อาคาร A ทางเข้าด้านใต้]   │
│ Position:  x=1452, y=987 pt           │
│ Layer:     [03_ลานจอดรถ      ▼]      │
└───────────────────────────────────────┘
```

### 4.7 Site Summary Widget — new tab "🏙️ ผังบริเวณ"

The existing summary widget has 4 tabs (Area / Floor / Site / Warnings per mockup-v3 Phase D). The **Site tab is currently a placeholder** — this mockup specifies its content:

```
┌─ Summary Widget — Site (🏙️ ผังบริเวณ) ─────────────────────────┐
│ [Area] [Floor] [🏙️ Site (active)] [Warnings]                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│ ── Areas ──                                                       │
│ พื้นที่ดิน:           6,576.60 ตร.ม.                                │
│ ปกคลุมอาคาร:        3,303.00 ตร.ม.   (A:1,944 + B:1,207 + C:152) │
│ ที่ว่าง:              3,264.60 ตร.ม.                                │
│ ─ ซึมน้ำ:           3,288.49 ตร.ม.                                │
│ ─ Hardscape:        (derived) ตร.ม.                              │
│ ─ จอดรถ outdoor:    (sum)    ตร.ม.                                │
│ ─ ถนนภายใน:        (sum)    ตร.ม.                                 │
│                                                                   │
│ ── Ratios (display only, ผู้ใช้พิจารณาเอง) ──                       │
│ ┌─────────────┬──────────────┬─────────────────────┐             │
│ │ Metric      │ วัดได้        │ เกณฑ์ผู้ใช้กรอก       │             │
│ ├─────────────┼──────────────┼─────────────────────┤             │
│ │ FAR         │ 5.91 : 1     │ ≤ 10.0              │             │
│ │ BCR         │ 50.2 %       │ —                   │             │
│ │ OSR         │ 49.7 %       │ ≥ 3.0 % (ผังเมือง)   │             │
│ │ % permeable │ 50.0 %       │ ≥ 50 %              │             │
│ └─────────────┴──────────────┴─────────────────────┘             │
│ ⓘ ระบบไม่ตัดสินผ่าน/ไม่ผ่าน — ผู้ใช้พิจารณาด้วยตนเอง                │
│                                                                   │
│ ── Setback (วัดจากแต่ละ edge ที่ tag) ──                            │
│ ┌────────────────┬──────────┬──────────────────────┐             │
│ │ ทิศ            │ วัดได้    │ เกณฑ์ผู้ใช้กรอก          │             │
│ ├────────────────┼──────────┼──────────────────────┤             │
│ │ ⬆️ เหนือ        │ 7.84 ม.  │ ≥ 6.0 ม. (รอบ มร.33) │             │
│ │ ⬇️ ใต้          │ 12.00 ม. │                       │             │
│ │ ➡️ ตะวันออก     │ 8.19 ม.  │                       │             │
│ │ ⬅️ ตะวันตก     │ 7.22 ม.  │                       │             │
│ └────────────────┴──────────┴──────────────────────┘             │
│                                                                   │
│ ── ที่จอดรถ (count) ──                                              │
│ 🅿️ ปกติ:            256 คัน                                        │
│ ♿ ผู้พิการ:         0 คัน                                          │
│ 🚒 ดับเพลิง:        1 คัน                                          │
│ 🚑 พยาบาล:          1 คัน                                          │
│ รวม:                258 คัน                                        │
│                                                                   │
│ ── อื่นๆ ──                                                          │
│ ทางเข้า-ออก:        🚪 1 จุด                                       │
│ AED:                ➕ 0 จุด                                       │
│ ป้ายโฆษณา:          📍 0 ป้าย                                      │
│ N arrow:            ✅ ตั้งแล้ว ทิศเหนือ = 12.3°                    │
│                                                                   │
│ ── Actions ──                                                      │
│ [📤 Export XLSX สรุปผังบริเวณ]  [📋 Copy summary text]            │
└────────────────────────────────────────────────────────────────────┘
```

**Computation rules (display only — defined in `proto/ui.html` as pure functions):**

```js
// ที่จะเพิ่ม proto/ui.html — ใกล้ existing summary code
function siteAreaSummary(pg) {
  const polys = pageStore[pg]?.polys || [];
  const groupByTag = (tag) => polys
    .filter(p => p.semanticTag === tag)
    .reduce((sum, p) => sum + (objectAreaM2(p, pg) || 0), 0);
  return {
    land:             groupByTag("site_land_area"),
    coverage:         groupByTag("building_coverage"),
    open_space:       groupByTag("open_space"),
    permeable:        groupByTag("permeable_area"),
    hardscape:        groupByTag("hardscape"),
    parking_outdoor:  groupByTag("parking_area_outdoor"),
    internal_road:    groupByTag("internal_road"),
  };
}

function siteRatios(s, gfaTotalAcrossPlanPages) {
  if (!s.land) return null;
  return {
    BCR_pct:  (s.coverage / s.land) * 100,
    OSR_pct:  ((s.land - s.coverage) / s.land) * 100,
    FAR:      gfaTotalAcrossPlanPages / s.land,         // ratio number, display as "X : 1"
    perm_pct: (s.permeable / s.land) * 100,
  };
}

function siteMarkerCounts(pg) {
  const m = pageStore[pg]?.parking || [];   // ⚠️ markers live in pageStore[pg].parking (mParking), NOT .markers
  return {
    parking:           m.filter(x => x.markerType === "parking").length,
    parking_disabled:  m.filter(x => x.markerType === "parking_disabled").length,
    parking_fire:      m.filter(x => x.markerType === "parking_fire").length,
    parking_ambulance: m.filter(x => x.markerType === "parking_ambulance").length,
    entrance:          m.filter(x => x.markerType === "entrance").length,
    aed:               m.filter(x => x.markerType === "aed").length,
    sign:              m.filter(x => x.markerType === "sign").length,
  };
}
```

`gfaTotalAcrossPlanPages` comes from summing `objectAreaM2` of every poly with `semanticTag === "gross_floor_area"` across pages where `pageType === "plan"`. This already exists conceptually for the Floor tab — Site tab reuses it.

### 4.8 Setback auto-suggest — direction binding

When the user finishes drawing a `site_land_area` polygon and the page has a north arrow set, a one-shot suggest dialog appears:

```
┌─ ผูกทิศของแต่ละ edge ────────────────────────┐
│ พบ 4 edge ของเขตที่ดิน — เสนอทิศตามที่ตั้ง:     │
│                                               │
│ Edge 0 (75.4 ม.):   ⬆️ ทิศเหนือ    [ยอมรับ]    │
│ Edge 1 (110.2 ม.):  ➡️ ทิศตะวันออก [ยอมรับ]    │
│ Edge 2 (75.4 ม.):   ⬇️ ทิศใต้       [ยอมรับ]    │
│ Edge 3 (110.2 ม.):  ⬅️ ทิศตะวันตก   [ยอมรับ]    │
│                                               │
│ [✓ ยอมรับทั้งหมด]  [ปรับเอง]  [ปิด]            │
└───────────────────────────────────────────────┘
```

The dialog is a **suggestion** — accepting just fills `polyEdgeTags[i].compassDirection`. Existing `polyEdgeTags[i].role` (`front_road / side_left / ...`) stays the source of truth for legal categorization. Both fields coexist.

Auto-suggest algorithm:
```
For each edge i:
  midpoint_angle = atan2 from polygon centroid toward edge midpoint
  rotate by -(north.angleDeg)  // north arrow rotation
  bucket into N / NE / E / SE / S / SW / W / NW (8 bins of 45°)
  display the 4 most-extreme directions as N/E/S/W only
```

### 4.9 Mode and active layer interaction

The active layer dropdown on the topbar shows site layers when on a site page:

```
[Active Layer ▼]
  01_ที่ดิน-แนวเขต  (active)
  02_ที่ว่าง
  03_ลานจอดรถ
  04_ทางเข้า-แยก
  05_เส้นอ้างอิง
  06_ป้ายชื่อ
```

When the user clicks "ปกคลุมอาคาร" in the ribbon, the system **does not auto-switch** the active layer (that violates the existing Tool-Layer Awareness model). Instead, the new polygon is created with `layerSlug = "base_area"` by `assignDefaultObjectLayer` (existing function) based on its `semanticTag`. The default layer per semanticTag is defined in §10 of `SITE_PLAN_MEASUREMENT_PLAN.md`.

---

## 5. Component Specifications

### 5.1 Tier 1 — Minimum Viable (Phase I-A + I-B)

| # | Component | DOM id (proposed) | State source | Events |
|---|---|---|---|---|
| 1 | Project Setup classification fieldset | `#ps-building-class` | `projectInfo.buildingClassification` + `buildingUseType` | change → `saveProject(silent=true)` |
| 2 | Project Setup limits fieldset | `#ps-user-limits` | `projectInfo.userDefinedLimits.*` | change (debounced 300ms) → save |
| 3 | Ribbon Site Plan group | `#tool-row-site` (visible when `pageType==="site"`) | reads `setAreaType` / `addMarker` | click → mode change |
| 4 | Site stepper widget | `#site-stepper` (replaces `#workflow-card` on site pages) | derived from `pageStore[site]` poly/marker counts | click step → setMode / openPanel |
| 5 | Building object property fields | `#bp-building-height` + `#bp-wall-edges` | poly.buildingHeight_m + poly.wallEdges[] | input → save + redraw (re-render label) |
| 6 | Marker submenu items in Measure dropdown | `.menu-item[data-marker-type]` | reads `setMarkerType` | click → mode = `marker_<type>` |

### 5.2 Tier 2 — Summary (Phase I-C)

| # | Component | DOM id | State source | Events |
|---|---|---|---|---|
| 7 | Site summary tab in Summary Widget | `#sw-tab-site` | derived from `siteAreaSummary` / `siteRatios` / `siteMarkerCounts` | click tab → render summary |
| 8 | Setback table widget | `#site-setback-table` | per-edge `polyEdgeTags` + `polyMetrics` | live update on poly edit |
| 9 | XLSX export "สรุปผังบริเวณ" sheet | (backend) | reuses derived values | export button click |

### 5.3 Tier 3 — Compare + advanced (Phase I-D + I-E)

| # | Component | DOM id | State source |
|---|---|---|---|
| 10 | "วัดได้ X / เกณฑ์ Y" rows | inline in summary tab | `projectInfo.userDefinedLimits` + measured |
| 11 | Building-to-building distance widget | `#site-bb-distances` | pairwise on `building_coverage` polys |
| 12 | Setback auto-suggest dialog | `#dlg-suggest-edge-dir` | one-shot after edge tagging |
| 13 | Compass direction overlay on canvas | drawn in `redraw()` | `polyEdgeTags[i].compassDirection` |

---

## 6. Data Flow

```
User action                Field written                     Display updated
───────────────────────────────────────────────────────────────────────────
Fill FAR limit             projectInfo.userDefinedLimits.    Site Summary
in Project Setup            far_max                          comparison row
                                                              "วัดได้ / Y"

Draw building_coverage     poly = {                          Stepper ③ checks
polygon                      semanticTag:"building_coverage",  if any building
                             pts:[...]                        coverage exists.
                           }                                  Layer count +1.

Enter buildingHeight_m     poly.buildingHeight_m             Used by ข้อ 48
in properties               = 110.60                          + ข้อ 44 helpers
                                                              (Tier 3).
                                                              Display in
                                                              property panel.

Tag edge as front_road     polyEdgeTags[i] = {               Setback table
                             label, role: "front_road",       row appears
                             compassDirection: "south"        with measured
                           }                                  perp distance.

Accept N suggest dialog    polyEdgeTags[*].                  Compass overlay
                            compassDirection = "N/E/S/W"      on canvas;
                                                              setback table
                                                              groups by N/E/S/W.

Place 🚒 marker            pageStore[pg].parking.push({       Summary count:
                             id, markerType:"parking_fire",   🚒 ดับเพลิง 1
                             parkingType, x, y                 คัน
                           })  ← array is .parking, not .markers

GFA poly drawn on          (no change to projectInfo —       FAR ratio
plan page                  derived live by Site Summary)      recomputes
                                                              and re-renders.
```

All state lives in `pageStore[pg]` / `projectInfo` — no new top-level state. `pushUndo()` handles every change. Save flow is unchanged (Ctrl+S / Save As / FSAPI handle).

---

## 7. Programme Guideline (where things live in `proto/ui.html`)

Map each new feature to a region of `proto/ui.html`:

```
proto/ui.html (~1700 lines currently)
─────────────────────────────────────────────────────────────────
Constants block       (~line 100-200)
  + AREA_LABELS additions (Phase I-A)        🆕
    "building_coverage", "open_space", "permeable",
    "hardscape", "parking_outdoor", "internal_road"
  + MARKER_TYPES enum                          🆕
  + SITE_PLAN_LAYER_PRESET                    🆕

DOM scaffold (top of <body>)                  (~line 200-700)
  + #site-stepper widget (initially hidden)   🆕
  + Site Plan section in #ui-layout-panel     🆕
  + Project Setup card additions              🆕
  + Building-edge wall-type radio group       🆕

Geometry / math (existing)                    (~line 900-1000)
  ✅ Already has path geometry (PATH_GEOMETRY_OK)
  + siteAreaSummary(pg)                        🆕 (pure function)
  + siteRatios(s, gfaTotal)                   🆕
  + siteMarkerCounts(pg)                      🆕

Render block (existing)                       (~line 1000-1200)
  + drawCompassDirectionOverlay() inside redraw  🆕

Mode handlers (existing setMode)              (~line 1200-1400)
  + cases for "site_land", "site_coverage",     🆕
    "site_open", "site_perm", "site_hard",
    "site_parking_outdoor", "site_road"
  + cases for marker modes (parking_disabled,    🆕
    parking_fire, parking_ambulance, entrance, aed)

Menu dropdowns (Phase G existing)             (~line 1400-1500)
  + site_plan submenu items (under Measure)   🆕

Save/load (existing applyLoadedProject)       (~line 1500-1600)
  + backward compat for missing site fields    🆕
    (default empty arrays / sensible defaults)

Summary widget (Phase D existing)             (~line 1600-1700)
  + Site tab content render                    🆕
```

Total addition: **~200-300 lines** in `proto/ui.html` for Tier 1 + ~150 lines for Tier 2 (summary tab). No file split needed.

`proto/static/css/app.css` — add roughly:
- `.site-stepper` + `.ss-step-*` (`.done`, `.in-progress`, `.todo`)
- `.tool-row-site` (visibility selector based on `body[data-page-type="site"]`)
- `.compare-row` (neutral side-by-side rows in summary)
- `.compass-overlay-text` (canvas-overlay style)

`proto/e2e_ui_test.py` — new assertions per phase:
- **Phase I-A:** `SITE_AREA_TYPES_OK` — new semanticTag enum accepted; Project Setup new fields persist
- **Phase I-B:** `SITE_TOOL_BUTTONS_OK` — ribbon group visible only on site pages; marker types create
- **Phase I-C:** `SITE_SUMMARY_OK` — computed ratios match hand-calculation within 0.01 of example case
- **Phase I-D:** `SITE_COMPARE_OK` — comparison rows render; **no verdict text or pass/fail badge present** (negative assertion)
- **Phase I-E:** `SITE_BUILDING_PAIR_OK` — building-to-building distance widget renders for 2+ buildings

---

## 8. Acceptance — Example case (สยามสินทร)

When this UI is fully implemented (Phase I-A → I-C), loading a project that matches the สยามสินทร case data should:

| Display | Expected value |
|---|---|
| Project Setup → buildingClassification | extra_large |
| Project Setup → buildingHeight_m | 110.60 |
| Project Setup → frontageRoadName / Width | "ถนนหลังสวน" / 16.90 |
| Project Setup → userDefinedLimits.far_max | 10.0 |
| Project Setup → userDefinedLimits.osr_min_pct | 3.0 |
| Site Summary → land | 6,576.60 |
| Site Summary → coverage | 3,303.00 |
| Site Summary → open_space | 3,264.60 |
| Site Summary → permeable | 3,288.49 |
| Site Summary → BCR | 50.22% |
| Site Summary → OSR | 49.65% |
| Site Summary → FAR | 5.91 |
| Site Summary → permeable_pct | 50.00% |
| Setback table → north / south / east / west | 7.84 / 12.00 / 8.19 / 7.22 |
| Marker counts → parking / fire / ambulance | 256 / 1 / 1 |

**No "✓ ผ่าน" or "✗ ไม่ผ่าน" anywhere.** Comparison rows display "วัดได้ X | เกณฑ์ Y" only.

---

## 9. Out of Scope (for this UI mockup sprint)

This mockup deliberately excludes the following. They are tracked as later sprints or "do not implement":

- Pen / Bezier vertex-handle UI for paths (separate sprint after Phase H.1 implementation)
- 2h diagonal measurement tool (waits on Phase H.0 — 45° lock)
- Auto-load FAR/OSR from a zone database (forbidden — Rule Engine territory)
- Pass/fail verdict UI of any kind (forbidden — Phase 1 rule)
- ค.1 form generation (forbidden — Phase 2+)
- Multi-jurisdiction (กทม. vs ตจว. vs ผังเมืองพิเศษ) — out of scope
- OCR / AI auto boundary detection (forbidden)
- Real-time cross-reference with law database (forbidden in Phase 1)

---

## 10. Hard Forbidden (when implementing this UI)

Same list as `SITE_PLAN_MEASUREMENT_PLAN.md §15`. Specifically for UI:

- ❌ Color-coded pass/fail badges (red/green checkmarks)
- ❌ "ผ่าน N จาก M รายการ" verdict summary
- ❌ Auto-block submission / export based on comparison
- ❌ Hardcoded thresholds — every limit comes from `projectInfo.userDefinedLimits`
- ❌ Editing `polyAreaM2`, `polyMetrics`, `pdfToC`, `cToPdf`, `RS`, snap engine
- ❌ Editing `proto/server.py`
- ❌ Bumping `.bmaplan` version (additive fields only)
- ❌ Using `layer.name` / `layer.slug` for any calculation
- ❌ Touching forbidden surfaces listed in `CLAUDE.md`

---

## 11. Implementation Order (recommended sprint split)

> **Revised 2026-05-14** — this section originally pre-dated the Pack D UI discipline
> ("one UI region per sprint"). The coarse "I-B = one sprint" was split by `/bma-measure-scope`
> into I-B1…I-B4. Status column reflects what has actually shipped.

| Sprint | Scope from this doc | Status | Risk | E2E marker |
|---|---|---|---|---|
| **I-A** | §4.1 Project Setup additions, semanticTag/`SEMANTIC_TAG_LABELS`, schema backward-compat | ✅ DONE (`984eb7e`) | LOW | `PHASE_I_A_OK` |
| **I-B1** | `markerType` additive field + `MARKER_TYPE_LABELS` registry + backfill from `parkingType` | ✅ DONE (`c38c3e6`) | LOW | `PHASE_I_B1_OK` |
| **I-B2** | §4.3 ribbon Site Plan group + §4.4 Measure menu submenu (shared `setMode` handlers) | queued | LOW-MED | `PHASE_I_B2_OK` |
| **I-B3** | §4.6 Properties panel site fields — `buildingHeight_m` / `buildingRoofHeight_m` input + draw-then-classify `semanticTag` selector | queued | MED | `PHASE_I_B3_OK` |
| **I-B4** | §4.5 Site stepper widget (left panel, replaces workflow card on site pages) | queued | MED | `PHASE_I_B4_OK` |
| **I-C** | §4.7 Summary Widget "ผังบริเวณ" tab + `siteAreaSummary` / `siteRatios` / `siteMarkerCounts` + XLSX sheet | queued | MED | `PHASE_I_C_OK` |
| **I-D** | §4.7 comparison rows + §4.8 setback auto-suggest dialog + §4.9 compass overlay | queued | MED (scope creep) | `PHASE_I_D_OK` |
| **I-E** | Building-to-building distance widget + `wallEdges` / `wallType` schema | queued | HIGH | `PHASE_I_E_OK` |

Each `I-B*` sprint = one UI region → starts with `/bma-ui-scope`, ends with `/bma-ui-regression` (Pack D discipline). Every sprint follows the AGENTS.md GTM loop + the mandatory sprint outputs documented in `CLAUDE.md`.

---

## 12. References

- `docs/design/SITE_PLAN_MEASUREMENT_PLAN.md` — what to measure (parent of this doc)
- `docs/design/bma-plan-mockup-v3.html` — overall UI mockup the rest of the app aligns to
- `docs/design/PAGE_SCOPED_LAYER_MODEL.md` — layer model
- `docs/design/PAGE_LAYER_MEASUREMENT_MODEL.md` — semantic tag pyramid
- `CLAUDE.md` — Claude Code project context, forbidden surfaces
- `AGENTS.md` — operating manual
- `law/mr35-33-upd69.pdf`, `law/mr43-55-upd68.pdf`, `law/สยามสินทร ร้านอาหาร 2568.pdf` — legal references for the measurements this UI captures
