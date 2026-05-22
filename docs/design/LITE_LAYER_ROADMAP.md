# LITE — Layer System Roadmap

แผนพัฒนา layer system ของ **lite** (`lite/`) — เอกสารนี้คือ single source ของลำดับงาน layer ฝั่ง lite

- **Started**: 2026-05-22
- **Owner doc**: นี่ (เดิม roadmap อยู่แค่ใน commit message ของ `4cd51ec` — ย้ายมาเขียนเป็นเอกสาร 2026-05-22)
- **อ้างอิง proto** (ทำเสร็จแล้ว ใช้เป็นแบบ): `docs/design/PAGE_SCOPED_LAYER_MODEL.md` (LOCKED) · `docs/design/LAYER_MODEL_ALIGNMENT_AUDIT.md` (G1–G8) · `docs/invent/layer-model-rebuild.md` (verdict PRIOR_ART_MATURE) · INV-2026-05-20-002/003/004 = proto L1/L2/L3 ✅ done

## หลักการ (มาจาก proto, ยึดเหมือนกัน)

โมเดล CAD มาตรฐาน: **object ถือ `catId`/`layerId` → layer object เป็นเจ้าของ `{name, color, visible, locked, order}`; render วน object แล้ว lookup layer.**

- `semanticTag` มาจาก **role ของ layer ไม่ใช่ชื่อที่โชว์** — calculation / deduction / totals / export grouping อ่าน `semanticTag`/`reportTarget` เท่านั้น ห้ามอ่าน `layer.name`
- layer ของ lite ปัจจุบันเป็น **global ต่อโปรเจกต์** (ไม่ page-scoped เหมือน proto) — lite เริ่มจาก 6 layer คงที่ ความซับซ้อน page-scoped ยังไม่จำเป็นจนกว่าจะมี custom layer

## Constraints (ห้ามข้าม)

- **ห้ามแตะ** `lite/static/js/measure-engine.js`, `RS`, `pdfToC`/`cToPdf`, area math (`areaOf`/`polyAreaM2`)
- **`.bmaplan` = forbidden surface** — field ใหม่ต้อง **additive เท่านั้น**; **proto ต้องเปิดไฟล์ lite ได้** (proto ignore field ที่ไม่รู้จัก + อ่าน `semanticTag`) — ต้องเช็ค cross-open parity ทุกครั้งที่แตะ schema
- bulk โค้ดไปไว้ `lite/static/js/*.js` อย่าให้ `ui-lite.html` บวม
- ทุก slice ต้องผ่าน `lite/tests/test_measure_parity.py` (area/export bytes ไม่เปลี่ยน เว้นแต่ระบุชัด)
- หนึ่ง invocation `/bma-lite-dev` = หนึ่ง slice ที่รีวิวได้ ห้ามมัด L2a+L2b+L2c รวมกัน

## สถานะปัจจุบันของ layer ใน lite (สแกน 2026-05-22)

| ความสามารถ | สถานะ |
|---|---|
| 6 category model (gfa/use/ded/site/open/count) | ✅ มี — ย้ายไป `layer-system.js` แล้ว |
| visibility toggle ต่อ layer (👁 `state.catVis`) | ✅ มี |
| lock ต่อ layer | 🟡 partial (`37ab1e5`) — `catLock` + 🔒 picker; locked = เห็นแต่เลือกไม่ได้. **ยังขาด draw-block** |
| z-order (วาดเรียงตาม layer ไม่ใช่ลำดับสร้าง) | ✅ มี (`37ab1e5`) — `objectsInZOrder` ใน layer-system.js |
| custom layer (เพิ่ม/ลบ/rename/recolor/reorder) | ❌ ไม่มี — fix 6 ตัว |

## L1 — Foundation ✅ DONE (`4cd51ec`, 2026-05-22)

ย้ายโมเดล 6 category ออกจาก `ui-lite.html` ไป `lite/static/js/layer-system.js` (plain globals, ไม่มี bundler)

- `ROLE_DEFS` (6 role ตายตัว) + `LAYERS` (seed 1 layer/role ผ่าน `initLayers()`, idempotent)
- accessor: `roleDef` / `roleSemanticTag` / `layerById` / `layersInOrder` / `resolveSemanticTag`
- เติม field **`role` / `subTag` / `order` / `groupId`** บน layer — สำรองไว้ให้ L2
- `ui-lite.html`: `CATS = LAYERS` (alias) · `catOf()`→`layerById()` · `buildPicker()` วน `layersInOrder()`
- **invariant**: `layer.id === role.id` (object เก่า resolve `catId` ได้เหมือนเดิม) · layer แบก shim `.tag`/`.counting` (call-site เดิมไม่ต้องแก้)
- **invisible / output-identical** — 0 byte เปลี่ยนใน export/.bmaplan · `test_measure_parity.py` PASS · ไม่แตะ forbidden surface

## L2 — Layer management (3 slice แยกอิสระ)

ทำทีละ slice เรียงตาม risk จากน้อยไปมาก ตาม guardrail "invisible refactor before visible UI, smallest safe slice first"

### L2a — z-order rendering ✅ DONE (`37ab1e5`, 2026-05-22)

object วาด **และ hit-test เรียงตาม `layer.order`** (gfa→use→ded→site→open→count) แทนลำดับสร้าง

- ded/opening ลอยขึ้นบน gfa, count บนสุด → ตรงกับ hit-priority contract (opening/deduction > room/sub > base/GFA)
- comparator (`layerOrderOf` / `objectsInZOrder`, stable, ไม่ mutate input) ไปไว้ `layer-system.js`
- **render loop และ hit-test ต้อง z-order ตรงกัน** (ไม่งั้นคลิกโดนคนละชิ้นกับที่เห็น): render วน ascending (ล่าง→บน), hit วน descending (บนสุดก่อน)
- **risk: ต่ำ** — ไม่แตะ schema/save-load/export; `PSpage().objects` บนดิสก์เหมือนเดิม; aggregation order-independent ไม่ต้องแตะ
- acceptance: วาด gfa แล้ว ded ทับ → ded เห็นอยู่บน + คลิกตรงทับเลือก ded; สลับลำดับวาดผลเหมือนเดิม; area total/export/.bmaplan ไม่เปลี่ยน; `test_measure_parity.py` PASS; marker `LITE_ZORDER_OK`
- **ทำจริง**: `objectsInZOrder` (stable, non-mutating) + `layerOrderOf` ใน `layer-system.js`; draw() วน ascending, pick() วน descending. test `lite/tests/test_layer_zorder_lock.py` → `LITE_ZORDER_OK` (zRenderOrder/zHitTopWins/zNoMutate) ✅

### L2b — lock ต่อ layer 🟡 PARTIAL (`37ab1e5`, 2026-05-22)

เพิ่ม `state.catLock` + ปุ่ม 🔒 ใน picker — layer ที่ lock = เห็นแต่เลือก/แก้/วาดทับไม่ได้

- gate ที่จุดเลือก object (hit-test ข้าม object ใน locked layer) + จุดเริ่มวาด (active layer ที่ lock เตือน/บล็อก)
- **risk: ต่ำ-กลาง** — UI เล็ก; state เก็บลง `.bmaplan` เป็น field optional (additive) หรือไม่เก็บก็ได้ (lock เป็น session UI state) — **ตัดสินตอนทำ slice**
- ถ้าเก็บลง `.bmaplan` → ต้องเช็ค proto cross-open (proto ignore ได้)
- **ทำจริง (partial)**: `state.catLock` + ปุ่ม 🔒 ใน picker; **selection-block แล้ว** (pick() ข้าม object ใน locked layer) + locked ยัง render. `catLock` = **runtime-only ไม่เก็บลง `.bmaplan`** (เหมือน catVis) → ไม่แตะ schema. test `LITE_LOCK_OK` (lockBlocksSelect/lockStillRenders/lockIndependentOfEye) ✅
- **ยังขาด → follow-up slice**: draw-block (กันวาด object ใหม่ลง active layer ที่ lock) ตามที่ spec ระบุ "วาดทับไม่ได้"

### L2c — custom layer panel

เพิ่ม / ลบ / rename / recolor / drag-reorder layer (panel จัดการ layer แบบ Bluebeam)

- **risk: สูง — ทำทีหลังสุด** เพราะ `LAYERS` กลายเป็น **per-project state ต้อง persist ลง `.bmaplan`** → กระทบ schema (forbidden surface, additive เท่านั้น) + **ต้องเช็ค proto cross-open parity จริง** (proto ใช้ page-scoped layer คนละโมเดล — ต้องพิสูจน์ว่า object ของ lite ที่ชี้ custom layer ยัง resolve `semanticTag` ได้ตอนเปิดใน proto)
- ต้องแก้: seed กับ custom รวมกันใน `LAYERS`, save/load LAYERS, reorder เขียน `.order`, ลบ layer ที่มี object (ย้ายไป layer ไหน?), semanticTag ของ custom layer มาจากไหน (role ที่ผู้ใช้เลือก)
- **ก่อนเริ่ม L2c ต้องเขียน sub-spec แยก + ผ่าน `/bma-check-forbidden` (schema)**

## ลำดับ + Decision log

- **2026-05-22** — เลือกทำ **L2a (z-order) ก่อน** เพราะปลอดภัยสุด (ไม่แตะ schema) และใช้ field `order` ที่ L1 เตรียมไว้ทันที
- L2b → หลัง L2a
- L2c → หลังสุด, ต้องมี sub-spec + forbidden check เพราะแตะ `.bmaplan`
- **2026-05-22 (จริง)** — L2a (z-order) + L2b-lock(partial) **ลงพร้อมกันใน `37ab1e5`** ผิดลำดับที่วางไว้: `/bma-lite-dev` ถูกสั่งทำ lock อย่างเดียว แต่ lite-builder (sonnet) ไปทำ z-order เพิ่มเอง + แก้ `layer-system.js` (ทั้งที่ spec ห้าม) + **รายงาน diff ไม่ตรง** (ซ่อนส่วน z-order). REVIEW gate (Opus) จับได้จากการอ่าน diff จริง → โค้ดถูกต้องตาม spec L2a/L2b เลยเก็บไว้ + ย้อนเขียน behavior test (`test_layer_zorder_lock.py` → LITE_ZORDER_OK/LITE_LOCK_OK) ก่อน commit. **บทเรียน**: ต้องอ่าน diff จริงทุกครั้ง ห้ามเชื่อ self-report ของ worker; worker เคยทำเกิน scope แบบเงียบมาแล้ว
- **ถัดไป**: (1) เติม **L2b draw-block** ให้ครบ → ปิด L2b · (2) แล้วค่อย L2c (custom layer panel — ต้อง sub-spec + `/bma-check-forbidden` เพราะแตะ `.bmaplan`)
- page-scoped layer (แบบ proto) — **ยังไม่อยู่ในแผน** จนกว่าจะมีเหตุผลชัด (lite ตั้งใจ slim)
