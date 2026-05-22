# LITE L2c — Custom Layer Panel · Sub-spec

ต่อจาก `LITE_LAYER_ROADMAP.md` (L2a/L2b ✅). L2c = เพิ่ม / ลบ / rename / recolor / drag-reorder layer.
**risk สูง** เพราะแตะ `.bmaplan` (forbidden surface) → spec นี้คือ "sub-spec แยก + ผ่าน /bma-check-forbidden" ที่ roadmap บังคับก่อนเริ่ม.

- **Started**: 2026-05-22
- **Decisions (จากผู้ใช้ 2026-05-22)**: (1) persist แบบ **additive** `liteLayers` + `liteCatId` · (2) ลบ layer ที่มี object → **ย้าย object ไป default layer ของ role เดียวกัน**
- **/bma-check-forbidden verdict**: ⚠️ WARN — `.bmaplan` เป็น forbidden surface; ทำได้เฉพาะเมื่อ (a) field ใหม่ **additive เท่านั้น** (b) **proto เปิดไฟล์ lite ได้เหมือนเดิม** (c) calc/export ยังอ่าน `semanticTag`/role ไม่ใช่ชื่อ layer

## หลักการที่ห้ามแตะ (มาจากการสแกน schema 2026-05-22)

ปัจจุบัน `.bmaplan` ที่ lite เขียน = **รูปแบบ proto**: `buildPageStore()` แปลง object → `pageStore[n].{polys,openings,lines,refs,counts}`; `loadProto()` สร้าง `catId` กลับจาก **`semanticTag`** (`SEM_REV[semanticTag]`).
→ identity ที่ round-trip ได้ = **semanticTag (role)** เท่านั้น. ทุก object ถูกยุบกลับเป็น 6 role ตอนโหลด.
→ custom layer **จะหาย** ถ้าไม่เพิ่ม field. นี่คือเหตุผลที่ต้องมี `liteLayers` + `liteCatId`.

## Schema เพิ่ม (ADDITIVE เท่านั้น — proto ignore ได้หมด)

```jsonc
{
  "version": 1, "app": "bma-plan-lite", "pdfName": "...",
  "pageStore": { /* เดิม — proto อ่านได้เหมือนเดิม ไม่แตะ */ },

  // === ใหม่ (additive) ===
  "liteLayers": [
    { "id": "gfa", "name": "พื้นที่อาคาร", "color": "#4c8dff", "role": "gfa", "order": 0 },
    { "id": "L7",  "name": "ชั้น 2 โซน A",  "color": "#80c0ff", "role": "gfa", "order": 1 }
    // ...เก็บ "ทุก" layer (default + custom) เพื่อ rename/recolor/reorder ของ default ก็ persist
  ]
}
```
- แต่ละ object ที่ persist (`polys[]`/`openings[]`/`lines[]`/`refs[]`/`counts[]`) เพิ่ม field **`liteCatId`** = id ของ layer นั้น (proto ignore field นี้)
- **role ต้องเป็น 1 ใน 6 role เดิม** (gfa/use/ded/site/open/count) → `semanticTag` = `roleSemanticTag(role)` เสมอ → calc/export/proto ไม่เปลี่ยน
- custom layer id ต้อง **unique + ไม่ชนกับ role id** (เช่น prefix `"L"+seq`)

### Load logic (additive, backward-compatible)
1. ถ้ามี `doc.liteLayers` → replace `LAYERS` ด้วยมัน (validate ทุก `role` ต้องเป็น 6 role ที่รู้จัก; ถ้าไม่รู้จัก drop layer นั้น + ย้าย object ไป default role)
2. ถ้า**ไม่มี** `liteLayers` (ไฟล์เก่า / ไฟล์ proto แท้) → seed 6 default เหมือนเดิม
3. ต่อ object: `catId = (liteCatId ที่ resolve ได้ใน LAYERS) ?? SEM_REV[semanticTag] ?? fallback เดิม` — ของเดิมไม่พังเพราะ liteCatId ไม่มีก็ fallback path เดิม

## Cross-open parity (บังคับ — เกณฑ์ผ่าน L2c-2)
- **lite → proto**: proto ignore `liteLayers`+`liteCatId`, อ่าน `polys/openings/semanticTag` → **area/grouping/export เท่าเดิมเป๊ะ**
- **lite → lite**: custom layer (ชื่อ/สี/ลำดับ) กลับมาครบ; object อยู่ layer เดิม
- **ไฟล์เก่า (ไม่มี liteLayers) → lite**: seed 6 default, object resolve ด้วย semanticTag เหมือนเดิม
- ต้องมี test: ขยาย `test_measure_parity.py` หรือเพิ่ม `test_custom_layer_roundtrip.py` (lite save → re-open ค่าเท่าเดิม + custom layer คงอยู่)

## UX (panel)
- เพิ่ม layer: ต้องเลือก **role (บังคับ)** + ตั้งชื่อ/สี → role ให้ semanticTag
- rename / recolor: แก้ได้อิสระ (display เท่านั้น — ไม่กระทบ calc)
- drag-reorder: เขียน `.order` → **z-order (L2a) บริโภค `.order` อยู่แล้ว** → render สลับทันที (ฟรี)
- ลบ layer: ถ้ามี object → **ย้าย object ไป default layer ของ role เดียวกัน** (reassign `catId`/`liteCatId` เป็น seed id ของ role นั้น) + เตือนก่อนยืนยัน; ถ้าเป็น default layer ของ role → ห้ามลบ (มันคือปลายทาง fallback)

## แตกเป็น 3 sub-slice (หนึ่ง slice = หนึ่ง commit รีวิวได้)

| slice | สิ่งที่ทำ | forbidden? | build อัตโนมัติได้? |
|---|---|---|---|
| **L2c-1 data model** | `LAYERS` mutable: `addLayer(role,name,color)` / `removeLayer(id)` (ย้าย object ไป default role) / `renameLayer` / `recolorLayer` / `reorderLayer`. อยู่ใน `layer-system.js`. **runtime-only, ไม่มี UI, ไม่แตะ schema**. + unit test | ❌ ไม่ | ✅ ได้ (ปลอดภัย) |
| **L2c-2 persistence** | `liteLayers` + `liteCatId` ใน save (`buildPageStore`/`doc`) + `loadProto`. **+ cross-open round-trip test (lite↔proto)** | ✅ **ใช่ (.bmaplan)** | ⛔ ต้อง checkpoint คน + /bma-check-forbidden รอบสอง ก่อนเริ่ม |
| **L2c-3 UI panel** | ปุ่ม +/ลบ/rename/recolor/drag-reorder ใน picker/panel | ❌ ไม่ (ถ้า model+persist พร้อม) | ✅ ได้ |

**ลำดับ**: L2c-1 → L2c-2 (checkpoint) → L2c-3. L2c-1 ทำก่อนได้เลย (ปลอดภัย, ตั้ง foundation, ไม่แตะ schema/UI).

## Acceptance รวม
- ทุก slice: `py_compile` + `MEASURE_PARITY_OK` + `LITE_ZORDER_OK`/`LITE_LOCK_OK` ไม่ถดถอย
- L2c-2: round-trip test ผ่าน + เปิดไฟล์ lite ใน proto แล้ว area/export เท่าเดิม (พิสูจน์จริง ห้ามเดา)
- ไม่แตะ `measure-engine.js`/`RS`/`pdfToC`/`cToPdf`/area math; ไม่ rename/remove field `.bmaplan` เดิม
