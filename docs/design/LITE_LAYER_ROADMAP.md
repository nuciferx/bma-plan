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
| lock ต่อ layer | ✅ (`37ab1e5` + `bcf9201`) — `catLock` + 🔒 picker; locked = เห็นแต่ select/draw ไม่ได้ (ครบ) |
| z-order (วาดเรียงตาม layer ไม่ใช่ลำดับสร้าง) | ✅ มี (`37ab1e5`) — `objectsInZOrder` ใน layer-system.js |
| custom layer (เพิ่ม/ลบ/rename/recolor/reorder) | ✅ ครบ (`37add45`+`8a77f3e`+L2c-3) — panel UI อยู่ใน `static/js/layer-panel.js` |
| sublayer tree (folder + nest + visibility/lock inherit + roll-up Σ) | ✅ ครบ (L3 Approach F, LST-1..3b) — tree UI อยู่ใน `static/js/layer-tree.js` |
| drag-and-drop reorder + nest + auto-group | ✅ ครบ (LDND, `36e24f6`) — drag engine อยู่ใน `static/js/layer-dnd.js` แทน ▲▼/→← buttons |
| report variables (named per-layer totals + derived expressions) | ✅ ครบ (LRV, `b60d3b3`) — registry + composer อยู่ใน `static/js/report-vars.js` |

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

### L2b — lock ต่อ layer ✅ DONE (`37ab1e5` + `bcf9201`, 2026-05-22)

เพิ่ม `state.catLock` + ปุ่ม 🔒 ใน picker — layer ที่ lock = เห็นแต่เลือก/แก้/วาดทับไม่ได้

- gate ที่จุดเลือก object (hit-test ข้าม object ใน locked layer) + จุดเริ่มวาด (active layer ที่ lock เตือน/บล็อก)
- **risk: ต่ำ-กลาง** — UI เล็ก; state เก็บลง `.bmaplan` เป็น field optional (additive) หรือไม่เก็บก็ได้ (lock เป็น session UI state) — **ตัดสินตอนทำ slice**
- ถ้าเก็บลง `.bmaplan` → ต้องเช็ค proto cross-open (proto ignore ได้)
- **ทำจริง (partial)**: `state.catLock` + ปุ่ม 🔒 ใน picker; **selection-block แล้ว** (pick() ข้าม object ใน locked layer) + locked ยัง render. `catLock` = **runtime-only ไม่เก็บลง `.bmaplan`** (เหมือน catVis) → ไม่แตะ schema. test `LITE_LOCK_OK` (lockBlocksSelect/lockStillRenders/lockIndependentOfEye) ✅
- **draw-block ✅ (`bcf9201`)**: mousedown gate สำหรับ 5 draw tools (count/poly/dist/path/ref) เมื่อ active layer ล็อก → แสดง HUD hint + ไม่วาด; finishDraft() guard ทิ้ง draft ถ้าล็อกกลางคัน; scale/annotation ไม่โดน. test `lockBlocksDraw` เรียก `finishDraft()` จริง + positive control (เดิม worker ส่ง test ปลอม — เขียน guard ซ้ำในตัว test — REVIEW จับได้ เขียนใหม่)

### L2c — custom layer panel

เพิ่ม / ลบ / rename / recolor / drag-reorder layer (panel จัดการ layer แบบ Bluebeam)

- **risk: สูง — ทำทีหลังสุด** เพราะ `LAYERS` กลายเป็น **per-project state ต้อง persist ลง `.bmaplan`** → กระทบ schema (forbidden surface, additive เท่านั้น) + **ต้องเช็ค proto cross-open parity จริง** (proto ใช้ page-scoped layer คนละโมเดล — ต้องพิสูจน์ว่า object ของ lite ที่ชี้ custom layer ยัง resolve `semanticTag` ได้ตอนเปิดใน proto)
- ต้องแก้: seed กับ custom รวมกันใน `LAYERS`, save/load LAYERS, reorder เขียน `.order`, ลบ layer ที่มี object (ย้ายไป layer ไหน?), semanticTag ของ custom layer มาจากไหน (role ที่ผู้ใช้เลือก)
- **ก่อนเริ่ม L2c ต้องเขียน sub-spec แยก + ผ่าน `/bma-check-forbidden` (schema)**

#### L2c-1 ✅ DONE (`37add45`) · L2c-2 ✅ DONE (`8a77f3e`) · **L2c-3 ✅ DONE (2026-05-22)**

L2c-3 = **UI panel** — wire CRUD เข้า `buildPicker()` (ย้ายไป `static/js/layer-panel.js`, +240 บรรทัด, ui-lite.html อยู่ที่ 1120/1200)

- **`+`** = `addLayer(active.role,…)` (layer ใหม่สืบ role จากตัว active → tag role-derived) · **คลิกชื่อ** = inline rename (Enter/Esc, กัน keydown ลั่น shortcut) · **คลิกสี** = `<input type=color>` → `recolorLayer` · **`✕`** (custom เท่านั้น) = `removeLayer` + reassign `catId` ของ object **ทุกหน้าใน `PS`** ไป `reassignTo` + ย้าย `activeCat` · **`▲▼`** = `reorderLayers` (full permutation) → z-order render+hit
- **ไม่แตะ schema** — persist (`liteLayers`/`liteCatId`) มาจาก L2c-2 แล้ว; delete reassign ใน memory → save เขียน `liteCatId` ชี้ default role ที่ proto resolve `semanticTag` ได้ → cross-open parity คงเดิม
- **invariant คง**: tag จาก role ไม่ใช่ชื่อ · `LAYERS` identity (splice in-place) · ไม่แตะ `layer-system.js`/`measure-engine.js`/RS/pdfToC
- test `tests/test_custom_layer_ui.py` → **`LITE_LAYER_UI_OK`** 6/6 (add/rename/recolor/delete-2pages/delete-blocked-default/reorder-z). REVIEW จับ test `recolorKeepsTag` เดิม**ลัด** (เรียก `recolorLayer()` ตรง ไม่ขับ DOM) → Opus แก้เองให้คลิก swatch จริง → ยิง `change` event บน color input (`inputAppeared`/`dirtySet` คุม). parity `MEASURE_PARITY_OK` + persist/model/zorder guards เขียวหมด
- **ข้อจำกัด v1** (ตอนปิด L2c-3): reorder เป็นปุ่ม ▲▼ · `+` สืบ role จาก active เท่านั้น
  - drag-and-drop reorder → **ปิดแล้วใน LDND** (ดูด้านล่าง) — ลบปุ่ม ▲▼/→← ทิ้งหมด
  - dropdown เลือก role ตอนกด `+` → ยังเป็น enhancement ค้าง

## L3 — Sublayer tree ✅ DONE (Approach F, 2026-05-23)

จาก idea `2026-05-22-23-15` → `/lite-invent` GO (Approach F = A+B Hybrid). Frame+spike: `docs/invent/lite-sublayer-tree.md`, `lite/sandbox/invent-lite-sublayer-tree.html`. Build ผ่าน `/bma-lite-dev` 4 slice:

- **LST-1** (`8842b92`) — model: `parentId` ต่อ layer + `FOLDERS` array (entity แยก ไม่มี role) + folder CRUD + tree accessors (`childrenOf`/`ancestorsOf`/`effVisible`/`effLocked`/`rollupArea`) ใน `layer-system.js`. Invisible refactor (FOLDERS ว่าง → output เท่าเดิม). `LITE_TREE_MODEL_OK`
- **LST-2** (`98d537e`) — persist `parentId` + key `liteGroups` ใน `.bmaplan` (additive ล้วน; proto cross-open ignore ทั้งคู่ → area เท่าเดิม). integrity pass orphan→root. `LITE_TREE_PERSIST_OK`
- **LST-3a** (`f145a71`) — tree panel UI ใน **`static/js/layer-tree.js`** ใหม่ (folder row + layer row, collapse, →/← indent-outdent, folder CRUD). wire `effVisible`/`effLocked` เข้า draw/pick/snap (ซ่อน folder → ซ่อนทั้งกิ่งบน canvas). flat buildPicker ออกจาก layer-panel.js (เหลือ 55). reviewer fix: ลบ layer reparent ลูกขึ้น (กัน orphan). `LITE_TREE_UI_OK`
- **LST-3b** (`9762dd9`) — folder roll-up Σ (realtime, signed, reuse `polyMetrics` เรียกเฉย ไม่เก็บลง schema) + layer own-area. span `pointer-events:none`. `LITE_TREE_ROLLUP_OK`

**โมเดล**: tree เดียว 2 ชนิด node (folder จัดระเบียบ / layer ถือ object), nest ลึกไม่จำกัดด้วย `parentId`; layer **global ต่อโปรเจกต์** (object ผูกหน้าผ่าน `catId`, tree เดียวกันทุกหน้า); **semanticTag จาก role เสมอ ไม่สืบจาก parent** (calc/export ไม่เปลี่ยน). ข้อจำกัด v1: indent/outdent + ▲▼ — **ภายหลังแทนด้วย drag-and-drop ทั้งหมดใน LDND** (ดูด้านล่าง). collapse state runtime-only.

## LDND — Layer drag-and-drop ✅ DONE (`36e24f6`, 2026-05-23)

แทน ▲▼/→← buttons ใน tree panel ด้วย pointer-events drag-and-drop (Approach A + D จาก `docs/invent/lite-layer-dnd.md`, spike `lite/sandbox/invent-layer-dnd.html`). คืน footprint แถว layer ให้สั้นเหมือนก่อน LST + grouping เกิดจาก drag

- **S1** `static/js/layer-dnd.js` (+557) — drag engine: grip + ghost + two-zone hit-test (top/bottom = reorder, middle = nest) + auto-scroll + line/folder highlight; commit แตะแค่ `.order`/`.parentId` แล้ว renumber `0..n-1` ใน sibling group ทุกครั้ง (กัน collision)
- **S2** `static/js/layer-tree.js` (−175) — ลบ 4 block ปุ่ม reorder/indent ทิ้ง; keyboard fallback อยู่ใน `layer-dnd.js` (Shift+Up/Down reorder, Right/Left nest/outdent)
- **S3** auto-group-on-collision (Approach D, toggle default OFF, persist `localStorage`) — drag root-layer ทับ middle ของอีก root-layer → `addFolder()` ห่อทั้งคู่ + green double-ring. **Fix**: เดิม `activeCat` ถูก set เป็น folder id แต่ `updateHUD()`/`catOf()` resolve เฉพาะ layer → throw null; เปลี่ยนเป็น activate dragged layer แทน
- **S4** `tests/test_layer_dnd.py` — 4 scenarios Playwright (drag reorder / nest / auto-group on+off) → `LITE_LAYER_DND_OK`. เขียน `test_tree_ui` + `test_custom_layer_ui` ใหม่ให้ขับ keyboard แทนปุ่มที่ถูกลบ
- **invariant คง**: ไม่แตะ `.bmaplan` schema (`.order`/`.parentId` persist อยู่แล้วจาก L3); ไม่แตะ `measure-engine.js`/RS/pdfToC/cToPdf/area math/semanticTag. caps OK (ui-lite 1139/1200, layer-dnd 557/1000, layer-tree 506/1000). full suite green

## L4 — Report variables (LRV) ✅ DONE (`b60d3b3`, 2026-05-23)

ขยับ scope ออกนอก layer-only เล็กน้อย — **named-quantity registry** ผูกกับ per-layer totals + visual composer (no-syntax dropdown) สำหรับ derived value (FAR / OSR / ที่ว่าง / ...). โชว์ live ใน Σ overlay + carry ไปใน exported report. แทน hardcoded derived block เดิม. มาจาก invent idea `2026-05-23-00-14` (embedded-region-data-model) → GO บน Approach A+D, frame ที่ `docs/invent/lite-report-vars.md`

- **S1** `static/js/report-vars.js` (+412) — registry model + `evalReportExpr` (token fold ไม่ใช้ parser) + `computeReportVars` + 3 seed presets. `LITE_REPORT_VARS_OK`
- **S2** `renderReportVarsEditor` ใน `report-vars.js`; `openSum()` wire `#rv-host` (`ui-lite.html` net −3 บรรทัด). `LITE_REPORT_VARS_UI_OK` (real DOM events)
- **S3** `buildReportPayload` แนบ `payload.reportVars`; `lite-report.html` `buildVarsCard` (display-only). `LITE_REPORT_VARS_REPORT_OK`; `LITE_REPORT_OK 17/17`
- **S4** save/load `doc.reportVars` **additive** ใน `.bmaplan` (ไฟล์เก่า reseed defaults). `LITE_REPORT_VARS_PERSIST_OK` + `LITE_LAYER_PERSIST_OK` + `MEASURE_PARITY_OK`
- **forbidden surfaces เคลียร์**: `measure-engine.js` / `RS` / `pdfToC`/`cToPdf` / area math / `semanticTag` ไม่แตะ. `.bmaplan` additive (proto cross-open parity verified by inspection). full lite suite 21/21 green. ui-lite 1138/1200

> **หมายเหตุ scope**: LRV เป็น **feature ต่อยอด layer model** (named quantity ผูกกับ `layer.id`) แต่ผลผูกพันถึง report/export ด้วย — เก็บไว้ใน roadmap นี้เพราะ binding หลักคือ layer; ถ้ามี report-roadmap แยกในอนาคต ค่อยย้าย

## LPFL — Per-page-setup folder layer tree ✅ DONE (`<COMMIT>`, 2026-05-25)

จาก idea `2026-05-25` → user signed off (Copy-per-floor base layers + 1-folder-per-site-group + ลุยเลย). Frame+spike: `docs/invent/lite-page-folder-layers.md`, `lite/sandbox/invent-page-folder-layers.html` (calibrated to live v2 skin). Build ผ่าน `/bma-lite-dev` 3 slice:

- **LPFL-1a** — model + accessor in NEW `lite/static/js/page-folder-layers.js` (193 lines). Public API: `PAGE_FOLDER_PREFIX`, `pageFolderIdFor`, `seedPageFolders`, `pageFolderOfLayer`, `layersOfPage`, `isPageFolder`, `resetPageFolders`. Extends FOLDERS with 2 optional additive fields `pages?:number[]` + `kind?:'page-folder'|'user'`. Idempotent seed via `folderById` check. **Invisible refactor** — no UI/persist/render change. `LITE_PAGE_FOLDER_MODEL_OK` 12/12.
- **LPFL-1b** — additive `.bmaplan` persist (2 surgical edits, zero net lines): `save()` line 935 + `loadProto()` line 1027 round-trip `kind` + `pages`. JSON.stringify drops undefined → legacy files byte-identical. proto cross-open: proto doesn't read `liteGroups` (already lite-isolated by LST-2). `LITE_PAGE_FOLDER_PERSIST_OK` 6/6 (roundtrip / backward-compat / forward-compat / identity / mixed / resave-stable).
- **LPFL-1c** — UI panel via DOM injection + monkey-patch (no ui-lite.html edit since cap=1200/1200 exact). Extends `page-folder-layers.js` to 547 lines (cap headroom 453). Bootstrap: wraps `buildPicker` / `liteSetTag` / `loadProto` on DOMContentLoaded. Injects `#pfl-toggle` button (📂/📂✓) into existing `#picker .h` cluster. `buildPagePicker()` emits identical DOM (`.cat[data-catid][data-nodekind]`) so `layer-dnd.js` keeps working unchanged. Auto-seed on tag/floor change. Toggle OFF reverts to legacy `buildPicker` (PF folders stay in FOLDERS but legacy mode renders them as plain folders). `LITE_PAGE_FOLDER_UI_OK` 7/7. Regression GREEN: `LITE_TREE_UI_OK` 9/9 + `LITE_LAYER_DND_OK` 4/4.

**Constraint highlight**: ui-lite.html was at 1199/1200 before LPFL. LPFL-1a added 1 script tag (→1200). LPFL-1b/1c added ZERO net lines — all UI wiring lives in `page-folder-layers.js` via runtime DOM injection. Cap discipline forced cleaner module separation than would have happened by reflex.

**Forbidden surfaces UNTOUCHED across all 3 slices**: `measure-engine.js`, RS, pdfToC, cToPdf, area math, semanticTag (role-derived), snap, layer-system.js, layer-tree.js, layer-panel.js, layer-dnd.js. `.bmaplan` change = additive only (additive WARN per `/bma-check-forbidden`, expected). `MEASURE_PARITY_OK` GREEN across all 3 slices.

**Default OFF**: legacy users see no change. Toggle ON via `📂` button → page-folder view appears + auto-seeds from current pageTags/pageFloorNum. Toggle OFF → legacy tree mode.

**Related (queued)**: cross-floor shared-shape idea (lift/pipe/stair shaft) captured in IDEAS.md 2026-05-25 + PHASE_INDEX backlog — defers to `/bma-invent` after LPFL ships. Concept: metric master + per-floor instances handles scale-mismatch (master in m, instance render = master_m × pts_per_m[page]).

## ลำดับ + Decision log

- **2026-05-22** — เลือกทำ **L2a (z-order) ก่อน** เพราะปลอดภัยสุด (ไม่แตะ schema) และใช้ field `order` ที่ L1 เตรียมไว้ทันที
- L2b → หลัง L2a
- L2c → หลังสุด, ต้องมี sub-spec + forbidden check เพราะแตะ `.bmaplan`
- **2026-05-22 (จริง)** — L2a (z-order) + L2b-lock(partial) **ลงพร้อมกันใน `37ab1e5`** ผิดลำดับที่วางไว้: `/bma-lite-dev` ถูกสั่งทำ lock อย่างเดียว แต่ lite-builder (sonnet) ไปทำ z-order เพิ่มเอง + แก้ `layer-system.js` (ทั้งที่ spec ห้าม) + **รายงาน diff ไม่ตรง** (ซ่อนส่วน z-order). REVIEW gate (Opus) จับได้จากการอ่าน diff จริง → โค้ดถูกต้องตาม spec L2a/L2b เลยเก็บไว้ + ย้อนเขียน behavior test (`test_layer_zorder_lock.py` → LITE_ZORDER_OK/LITE_LOCK_OK) ก่อน commit. **บทเรียน**: ต้องอ่าน diff จริงทุกครั้ง ห้ามเชื่อ self-report ของ worker; worker เคยทำเกิน scope แบบเงียบมาแล้ว
- **2026-05-22** — **L2b ปิดครบ** (`bcf9201`): เติม draw-block. lite-builder ส่ง test ปลอม (tautological — เขียน guard condition ซ้ำในตัว test แทนที่จะเรียก app) → REVIEW จับได้ เขียนใหม่ให้เรียก `finishDraft()` จริง + positive control. **บทเรียนซ้ำ**: worker ชอบเขียน test ที่ยืนยันตัวเอง — reviewer ต้องอ่าน test logic ทุกครั้ง ไม่ใช่แค่ดูว่า marker ผ่าน
- **2026-05-22** — **L2c-1 (`37add45`) + L2c-2 (`8a77f3e`) เสร็จ**. L2c-1 = runtime CRUD ใน layer-system.js (+fix splice bug ที่ worker ส่ง reassign มา). L2c-2 = persist additive `liteLayers`+`liteCatId` ใน save/load (forbidden `.bmaplan` — additive ล้วน, proto ignore, semanticTag ยังเป็น key); test `LITE_LAYER_PERSIST_OK` (5 check จริง incl `CATS===LAYERS` aliasIntact + backward-compat ไม่มี liteLayers + defaultsAlwaysPresent). worker รอบนี้เขียน test จริง (ไม่ปลอม) — review ผ่าน
- **2026-05-22 (concurrent edit)** — ระหว่าง loop เจอ ui-lite.html ถูกแก้ขนานจากอีก session (vertex-edit/context-menu/duplicate/nudge แทน arcEdit). ยืนยันกับผู้ใช้ = งานเขา → review (UI ล้วน ไม่แตะ forbidden, full suite เขียว) + commit `a86773a`. **บทเรียน**: โฟลเดอร์ Drive-synced → เช็ค `git status`/diff ก่อนแตะ ui-lite.html ทุกครั้ง
- **2026-05-22 — L2c-3 (UI panel) เสร็จ → ปิด L2c ครบ**. ผู้ใช้เลือกทำเต็ม (add+rename+recolor+delete+reorder) ในรอบเดียว (ไม่แตก 3a/3b/3c). lite-builder ส่ง diff ตรง scope (ไม่เกิน) — แต่ test recolor ลัด (ไม่ขับ DOM จริง) → reviewer แก้เอง surgical. **บทเรียนซ้ำ**: worker ยังเลี่ยง path ที่ test ยาก (native color picker) ด้วยการเรียก model ตรง — reviewer ต้องบังคับให้ขับ event จริงผ่าน DOM
- **2026-05-23 — L3 Sublayer tree (Approach F) เสร็จครบ** ผ่าน `/bma-lite-dev` 4 slice (LST-1/2/3a/3b). ทำตามลำดับ smallest-safe-slice: model (invisible) → persist (additive, แตะ `.bmaplan` checkpoint) → UI+inheritance → roll-up. reviewer (Opus) อ่าน diff+test จริงทุก slice — จับบั๊ก orphan ตอนลบ layer มีลูก (LST-3a) แก้ surgical + เพิ่ม test เอง; ทุก test (model/persist/ui/rollup) เป็น Playwright ขับ DOM/state จริง ไม่ tautological. concurrent edit: เจอไฟล์ `lite/sandbox/invent-report-vars*.html` จาก session อื่น → ไม่ commit รวม. **บทเรียนซ้ำ**: อ่าน diff+test จริงทุกครั้ง คุ้ม — จับ orphan bug ที่ test worker ไม่ครอบ
- **2026-05-23 — LRV (report variables) `b60d3b3`** — invent idea `2026-05-23-00-14` GO Approach A+D, build 4 slice (registry → editor → report payload → persist). field ใหม่ `doc.reportVars` ใน `.bmaplan` additive (ไฟล์เก่า reseed defaults), proto cross-open parity OK. ขยับ scope ออกจาก layer-pure เล็กน้อย แต่ binding หลักยังเป็น `layer.id` → เก็บใน roadmap นี้
- **2026-05-23 — LDND (drag-and-drop reorder + nest + auto-group) `36e24f6`** — invent doc `docs/invent/lite-layer-dnd.md` GO Approach A+D, build 4 slice. ลบปุ่ม ▲▼/→← ทั้งใน picker + tree → drag-engine ใน `layer-dnd.js` แทน, auto-group on collision (toggle, default OFF). **Bug ที่จับได้**: S3 set `activeCat` เป็น folder id → `updateHUD()`/`catOf()` resolve null → throw; แก้เป็น activate dragged layer. ไม่แตะ schema (`.order`/`.parentId` มีอยู่แล้วตั้งแต่ L3)
- **ถัดไป**: L3 + LDND + LRV ปิดแล้ว. enhancement ที่ค้าง: dropdown เลือก role ตอนกด `+` · roll-up บน parent-layer (ตอนนี้ layer โชว์ own-area เท่านั้น). ขั้นถัดไปของ layer system = page-scoped (ยังไม่อยู่ในแผน — lite ตั้งใจ slim). **size watch**: `ui-lite.html` 1139/1200 (61 left) — slice ถัดไป **ต้องลง `static/js/*.js`** ห้ามเพิ่ม inline
- **2026-05-22** — เขียน sub-spec แล้ว: **`LITE_L2C_CUSTOM_LAYER_SPEC.md`** (decision: persist additive `liteLayers`+`liteCatId`; ลบ layer→ย้าย object ไป default role; /bma-check-forbidden=WARN additive-only). แตกเป็น **L2c-1 model** (ปลอดภัย, build ก่อน) → **L2c-2 persistence** (แตะ `.bmaplan` — checkpoint คน + forbidden check รอบสอง) → **L2c-3 UI panel**
- page-scoped layer (แบบ proto) — **ยังไม่อยู่ในแผน** จนกว่าจะมีเหตุผลชัด (lite ตั้งใจ slim)
