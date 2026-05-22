# Invent — lite report variables (named-quantity registry + derived formulas)

- **idea id**: `2026-05-23-00-14` (embedded-region-data-model)
- **pipeline**: `/lite-invent` (lite-framed)
- **date**: 2026-05-23
- **status**: ✅ **BUILT & SHIPPED 2026-05-23** via `/bma-lite-dev` (LRV-S1..S4). GO on **A+D** (after side-by-side compare vs B/C/E against the real taxonomy; A+D was the only one able to split ที่ดิน/ปกคลุม/ที่ซึมน้ำ as separate variables). Full lite suite 21/21 GREEN. See PHASE_INDEX `#### LRV`.

## User reframing

> เราควรทำ option ในการเลเยอร์ ที่เป็น พท / ระยะ / นับจำนวน เพื่อนำไปใช้ต่อ — option ทั้งการ **รับข้อมูล** และการ **นำตัวแปรไปคำนวณใน report** ที่อยากให้แสดงใน report

มาจาก taxonomy 3 คอลัมน์ (พื้นที่ / ระยะ / นับ) 2 ระดับ (ผังบริเวณ + อาคาร/ชั้น): ที่ดิน, ปกคลุม, ที่ว่าง=ที่ดิน−ปกคลุม, ที่ซึมน้ำ, FAR, OSR, สีเขียว, ร่น, ที่จอดรถ ฯลฯ (full table ใน `~/.claude/ideas/IDEAS.md`).

## Phase 2 RESEARCH — verdict `PRIOR_ART_PARTIAL` (bma-researcher)

- **อย่าเพิ่ม enum "measurement-kind" ลง layer.** lite แยก kind ออกจาก layer อยู่แล้ว: object `kind` มาจาก tool (poly→area m² / dist→length m / count→count); `semanticTag` มาจาก `role` ไม่ใช่ชื่อ layer; calc/export อ่าน `semanticTag`+`kind` ไม่อ่าน `layer.name`. ยัด field ลง layer = ทำลายการแยก + เสี่ยง `.bmaplan` เปล่าๆ.
- **ส่วนที่มีค่า = report variable binding.** prior art ชัด: Bluebeam Revu "Markup List custom columns + Formula column" (measurement = ค่าตัวเลข uniform, สูตรอ้าง column อื่น, ไม่ต้อง AST parser). มาตรฐานหนุน: IFC quantity sets (area/length/count quantity types ระดับ object).
- lite ปัจจุบัน aggregate by `semanticTag` (`server_lite.py areaByTag()`); ยัง**ไม่มี** derived-variable / formula layer.
- library: hand-rolled ชนะ (lite no-bundler) — evaluator เล็ก ~60–100 LOC.

## Phase 3 FRAME

- **Problem**: ผูกผลวัดจริง (พท/ระยะ/นับ) → ตั้งเป็นตัวแปรชื่อ → คำนวณค่า derived (FAR/OSR/ที่ว่าง/สัดส่วน) แสดงใน report โดยไม่คำนวณมือนอกระบบ.
- **Forbidden (lite)**: ห้ามแตะ `measure-engine.js` / area math / RS / pdfToC-cToPdf / semanticTag derivation; `.bmaplan` additive + proto เปิดได้; `ui-lite.html` ≤1200 (ตอนนี้ ~1120 → bulk ไป `static/js/`); ผ่าน `test_measure_parity.py`.
- **Success**: นิยามตัวแปรจากยอดวัด, เขียน derived formula, report แสดงค่าสด recalc เมื่อวัดเปลี่ยน, parity คงเดิม.
- **Out-of-scope**: กฎหมาย pass/fail FAR-OSR (= v2 ต้องห้าม). ทำแค่ **compute + display**, ไม่ใช่ rule engine.

## Phase 4-5 DIVERGE + SCORE (bma-inventor) — 5 approaches

| # | approach | axis | forbidden touch | score |
|---|---|---|---|---|
| A | project-level named-variable registry | representation | NO | 25 |
| B | report-template formula rows (ephemeral) | algorithm | NO | 25 |
| C | formula per role in layer-system.js | data-model | NO | 25 |
| D | visual block-composer (dropdown chain) | UX | NO | 24 |
| E | typed quantity-slot override per role | data-entry | NO* (`computeSummary` patch, ไม่ใช่ forbidden) | 21 |

inventor แนะ **C** (tie-break: co-located, ไม่ต้อง parser).

## Orchestrator override (Opus)

**เลือก A (data-model) + D (UX) hybrid แทน C** — เหตุผล domain-fit:
- C ผูกสูตร "ต่อ role" แต่ lite มีแค่ 6 role; taxonomy ผู้ใช้มี ~15+ ตัวแปรที่ใช้ role เดียวกัน (ที่ดิน/ปกคลุม/ที่ซึมน้ำ/สีเขียว ล้วน area) → C แยกไม่ได้.
- A = registry ระดับโปรเจกต์ จำนวนตัวแปรไม่จำกัด; operand ผูก **layerId** (custom layer ทำได้แล้วจาก L2c) หรือชื่อตัวแปรอื่น — calc ไม่อ่าน layer.name (อ้าง id) → ปลอดภัยตาม contract.
- D = visual dropdown composer วางทับ A → zero-syntax UX (UX score 5), เก็บสูตรเป็น token array `{ref|lit, op}[]` eval ด้วย left-to-right fold (ไม่ต้อง parser).

## Phase 6 SPIKE

`lite/sandbox/invent-report-vars.html` (standalone, ไม่แตะ app). พิสูจน์:
1. registry รับตัวแปรไม่จำกัด (ไม่ติด 6-role).
2. operand ผูก `layerId`/ชื่อตัวแปร — ไม่อ่าน layer.name.
3. สูตร = token array, eval left-to-right fold (~60 LOC, no parser), รองรับ chain `(A op B) op C`.
4. recalc สดเมื่อยอดวัดเปลี่ยน (แก้ "ปกคลุม" → ที่ว่าง/OSR/FAR อัปเดต).
5. compute+display only — ไม่มี pass/fail.
6. persist เป็น `doc.reportVars` additive (proto ignore ได้).

## Phase 7 CHECKPOINT — รอมนุษย์

ถ้า **GO** → เขียน sprint card `invent-done-go` ใน PHASE_INDEX, build ผ่าน `/bma-lite-dev` slice:
- **S1** `lite/static/js/report-vars.js` — model + `evalExpr` fold + `computeReportVars(measuredAgg)`.
- **S2** ปุ่ม composer ใน Σ summary overlay (`ui-lite.html`, ~40 LOC; ระวัง cap 1200).
- **S3** derived panel ใน `lite-report.html`.
- **S4** save/load `doc.reportVars` additive + proto cross-open parity test + `test_measure_parity.py`.

**Open questions — default ที่ตั้งไว้ (ยืนยันตอน S1)**:
- operand ผูก "ยอดของ layer 1 ตัว = ตัวแปร 1 ตัว" → **default: ใช่** (พอ; semanticTag/page-level เก็บเป็น enhancement ถ้าต้องการ).
- ระยะ (ร่น) + count เข้าสูตรร่วม area → **default: ได้** (treat เป็นตัวเลขล้วน; หน้าที่ผู้ใช้คุมความหมายเอง).
- preset → **default: ให้ FAR / OSR / ที่ว่าง มาเป็น seed** (ผู้ใช้แก้/ลบ/เพิ่มได้).
