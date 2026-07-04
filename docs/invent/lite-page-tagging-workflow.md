# Invent: lite-page-tagging-workflow

- **idea_id**: `2026-07-04-13-21`
- **Status**: invent-in-progress (PICK done 2026-07-04)
- **Raw idea** (verbatim): "ทำที่ fable คิด" — pointing at Fable's independent opinion on the upload→scroll→tag workflow (same conversation, 2026-07-04)
- **The referenced opinion (4 moves, keep human-tags-as-ground-truth, demote wizard from gate to tool):**
  1. **Just-in-time tagging** — ask for a page's tag at first measure instead of requiring all pages tagged upfront
  2. **Range-tagging** — "หน้า 11–16 = แปลนชั้น เริ่มชั้น 1" in one action (permit sets are ordered runs)
  3. **Visual verification view** — thumbnail grid grouped by tag; a mis-tagged page is caught by eye before it silently corrupts the report
  4. **Fearless retag** — retag mid-work remaps folder+objects cleanly and is undoable
- **Tags**: bma-plan, lite, ui, page-setup, workflow, p-med
- **Known tension to resolve in FRAME:** UX-20260703 batch 2 recently SHIPPED a "wizard Next gate at 0 tagged" (`036a49d`) — hard gating was deliberately added; user also has a standing preference for hard workflow gating over soft warnings (HT-7). JIT tagging must not regress "measure tools refuse when scale missing" discipline — the gate being challenged is "ALL pages tagged before proceeding", not "THIS page tagged before measuring it".
- **Related prior work**: `overview-setup.js` (~1059 lines, LOVS-1 wizard), `page-folder-layers.js` seeding from tags, LFLOOR-1b/1c numbering cards (queued), INV-2026-07-04-001 context-scoped panel (shipped — folder = tag-derived)

## Frame

**Problem:** ชุดแบบ 45 หน้าบังคับแท็กครบทุกหน้าใน wizard ก่อนเริ่มวัด — แรงงานล่วงหน้าสูงทั้งที่งานวัดจริงใช้ ~10 หน้า และแท็กผิด 1 หน้าไหลไปผิดชั้นในรายงานแบบเงียบ ๆ ต้องการ: แท็กเมื่อจะใช้ (JIT), แท็กเป็นช่วง (range), ตรวจด้วยตา (grid), แก้แท็กกลางงานได้ไม่กลัวพัง (retag)

**Gate semantics (resolves the HT-7 tension):** คง hard gate ระดับ*หน้า* — จะวัดหน้าไหน หน้านั้นต้องมีแท็กก่อนเสมอ (refuse, ไม่ใช่ warning) สิ่งที่ถอดคือ gate ระดับ*ชุด* ("ทุกหน้าต้องแท็กก่อนไปต่อ") ซึ่งเพิ่ง ship `036a49d` — ถ้า GO, gate นั้นถูกแทนด้วย per-page JIT gate

**Constraints:** raster PDF / no OCR-auto-classification (Togal-style = Phase-1 boundary, ห้าม) / `.bmaplan` additive / lite size caps (overview-setup.js 1059→ต้อง extract ถ้าโต) / reuse existing remap math (`liteSetTag` wrapper, `reseedActivePageFolders`, `pageFolderIdFor`, `_pflFolderHasUserDrawnObjects` guard) — diverge on UX integration, NOT on remap math

**Forbidden surfaces:** measure-engine.js, RS, pdfToC/cToPdf, area math, semanticTag derivation

**Out of scope:** OCR/auto-tag, proto wizard, floor-numbering conventions themselves (LFLOOR-1b/1c คิวแยกอยู่แล้ว), report layout

## Eval

Runnable in sandbox spike (standalone HTML, synthetic 45-page set, in-page harness prints per-case PASS/FAIL):

1. **happy — JIT + range efficiency:** เริ่มจาก 0 หน้าแท็ก; (a) เข้าหน้า 11 กดวัด → JIT prompt โผล่, แท็ก 1 action แล้ววัดต่อได้ทันที; (b) range-tag "11–16 = แปลนชั้น เริ่มชั้น 1" 1 action; grader: จำนวน UI actions รวมจน 6 หน้า floor แท็ก+เลขครบ ≤ 8 (นับ event จริง), หน้าที่ไม่แท็กเปิดดูได้เสมอไม่ถูกบล็อก, กดวัดบนหน้าไม่แท็กต้องโดน refuse+prompt ทุกครั้ง (per-page gate)
2. **edge — mixed run + conflict:** range 11–17 มีชั้นลอยแทรกที่ 14 → override kind กลางช่วงได้ + เลขรันข้ามชั้นลอยตาม convention; range ทับหน้าที่แท็กแล้ว → ถามก่อน ไม่ทับเงียบ; grader: ผล tag/floorNum ต่อหน้าตรง expected map, ไม่มี silent overwrite
3. **adversarial — fearless retag + verify grid:** หน้า 12 (floor-2) มี 3 objects → retag เป็นชั้นลอย: objects อยู่ครบ, folder remap, grid จัดกลุ่มใหม่ถูก; หน้า elevation ที่จงใจแท็กผิดเป็น floor ต้องมองเห็นใน grid กลุ่ม floor (คลิก retag จาก grid ได้); undo คืนสถานะเดิมทั้ง tag+folder+object assignment (deep-equal); grader: object loss = 0, undo round-trip เท่าเดิมทุก field

**EVAL-GATE: ผ่าน** — ทั้ง 3 เคสรันได้จริงใน sandbox

## Research

**Verdict: PRIOR_ART_PARTIAL** (bma-researcher, 2026-07-04)

- **In-repo:** wizard gate ที่ต้องถอดอยู่ `overview-setup.js:284-289`; JIT hook point = `liteSetTag` (ui-lite.html:899, wrapper page-folder-layers.js:794-801 เรียก `reseedActivePageFolders()` อยู่แล้ว); guard กัน object หาย = `_pflFolderHasUserDrawnObjects` (page-folder-layers.js:291-330) → **remap math เสร็จแล้ว เหลือ UX**
- **Incumbents:** Bluebeam/STACK/PlanGrid ล้วน classify-upfront; Togal auto-classify ด้วย OCR (ต้องห้ามใน Phase 1); **ไม่มีใคร ship measure-first-classify-later หรือ reclassify-after-draw** — greenfield
- **Patterns:** JIT/progressive disclosure = mature; shift-click range = mature ตั้งแต่ spreadsheet ยุค 1985; verify-by-grouping = HCI concept (partial); transparent remap = novel
- **No library needed** — grid libs ใหญ่เกิน cap, DnD มีของเองแล้ว
- Moves สรุป: (1) JIT mature, (2) range mature, (3) grid partial, (4) retag greenfield-but-math-done

## Diverge

(bma-inventor, sonnet, 2026-07-04 — verbatim)

Ground truth correction before diverging: `overview-setup.js` L19-509 already ships a **shift-click multi-select + bulk-tag chip bar** (`_lovsSelected`, `#bulkbar`, line 323-440) — range-tagging by page-order already exists at the UI level, calling `liteSetTag(n,t)` per page. What's actually missing per the Frame: (1) floor-number auto-increment on bulk-apply, (2) overwrite-conflict confirm (today it silently overwrites), (3) single `pushUndo()` wrap for the whole bulk op (today N calls = N or 0 undo entries, untested), (4) a JIT per-page prompt, (5) a tag-grouped (not just page-order) view, (6) removing the Step-1 SET gate (`_lovsAnyTagged`, L284-289). `_docSnap`/`_applyDoc` (ui-lite.html L858) already snapshot `pageTags/pageFloorKind/pageFloorNum/folders` — undo is "free" if callers wrap mutations in `pushUndo()`.

### A — Inline canvas JIT banner (axis: WHERE JIT prompt lives)
Non-blocking banner pinned atop canvas, fires when an armed measure tool sees `curPage` untagged; tag chips call `liteSetTag` directly (wrapper already reseeds). Range/grid/retag stay in the existing bulk-select bar, untouched except gate removal.
Wizard/gate: SET gate deleted (~6 lines); Step 1 bulk-bar unchanged.
Size cost: new `canvas-tag-banner.js` ~70 lines; `overview-setup.js` shrinks.
Riskiest eval: Case 2 — banner solves JIT only; conflict-confirm + floor-auto-increment still must land inside the *existing* bulk-bar code this approach doesn't touch.

### B — Command-palette range syntax (axis: WHERE range-tag lives)
New parsed-text alternative to drag-select: `"11-16=ชั้น เริ่ม1"` → regex → loop `liteSetTag/liteSetFloorKind/liteSetFloorNum` in one `pushUndo()`. Sits beside the existing bulk-bar as a second entry point for the same mutation loop.
Wizard/gate: gate removed; Step 1 gains a command input.
Size cost: new `tag-command.js` ~90 lines (extracted — `overview-setup.js` already over its 1000-line cap).
Riskiest eval: Case 1 — Thai grammar ambiguity/typos risk retries that blow the ≤8-action budget; duplicates drag-select.

### C — Extend the existing bulk-bar into a dual-mode grid (axis: verification grid design)
Reuse `_lovsSelected`/bulk-bar as-is; add (a) "Apply: tag+kind+start#" to the bar so a drag-selected range gets floor-numbers in one click, (b) overwrite-confirm before silently retagging already-tagged pages, (c) a view toggle "page-order ↔ grouped-by-tag" that re-sorts the same tiles (client-side only) — this toggle *is* the verification grid, not a new screen.
Wizard/gate: gate removed; Step 1 becomes materially more capable, still one surface.
Size cost: extend existing render fns +~120 lines net → must extract into `overview-grid.js` (satisfies cap); lowest-risk extraction since scaffolding (selection, chip bar, tile DOM) already exists.
Riskiest eval: Case 3 — grouped view must instantly re-bucket a retagged page and keep it visually obvious without breaking `ltDndDecorate` reorder wiring attached to the same tiles.

### D — Four independent micro-features, no shared surface (axis: bundling strategy)
JIT = inline check at tool-arm site; range = separate small modal off the right-panel page list; grid = brand-new standalone view; retag = click-anywhere + `pushUndo()` at `liteSetTag` call sites.
Wizard/gate: gate removed; wizard becomes legacy/optional, flagged for later removal sprint.
Size cost: 3 small new files (~50-70 lines each) but duplicates range-select logic.
Riskiest eval: Case 1 — passes action count but forces user across 3-4 UI locations for one workflow.

### E — Staged `tagSession` draft model (axis: data-model)
Multi-page ops write into `tagSession.pending`; diff panel ("หน้า 11-16 → แปลนชั้น 1-6") previews before one "ยืนยัน" commits via the existing mutation loop inside exactly one `pushUndo()`. Single-page JIT bypasses staging (auto-commits) so the per-page gate stays instant.
Wizard/gate: gate removed; Step 1 internals read/write `tagSession` until commit.
Size cost: new `tag-session.js` ~110 lines; `_pflFolderHasUserDrawnObjects` guard must be re-pointed at *pending* state — genuine integration work.
Riskiest eval: Case 3 — guard must warn correctly pre-commit AND commit-time undo must deep-equal the live-apply path.

All 5: forbidden-surface touch = NO.

## Score

| approach | novelty | accuracy* | UX | model-fit | boundary | cost | total |
|---|---|---|---|---|---|---|---|
| A canvas banner | 3 | 4 | 3 | 5 | 5 | 4 | 24 |
| B command syntax | 4 | 3 | 3 | 4 | 5 | 3 | 22 |
| C extend bulk-bar/dual grid | 4 | 5 | 5 | 4 | 5 | 3 | **26** |
| D decoupled micro-features | 2 | 4 | 2 | 3 | 5 | 4 | 20 |
| E tagSession draft | 5 | 5 | 4 | 3 | 5 | 2 | 24 |

*accuracy = fidelity of resulting tag/floor data + no silent mis-tag (workflow feature, not area math).

Key rationales: C accuracy=5 (click-based + confirm-before-overwrite = deterministic, directly targets "แท็กผิดไหลแบบเงียบ"); D UX=2 (4 discovery points for one workflow, against HT-7 discipline); E novelty=5/cost=2 (matches the greenfield "reclassify-after-draw" but most net-new state risk).

## Recommendation

**Spike C (extend existing bulk-bar into dual-mode grid) first** — highest total and cheapest correct answer (scaffolding already ships; spike adds floor-auto-number, overwrite-confirm, one pushUndo wrap, view-toggle). **Fallback: A (canvas banner) for JIT alone** if C's grouped-view re-sort conflicts with `ltDndDecorate` reorder wiring. E revisit later as phase-2 if staged-preview demand appears.

**Phase-5 gate check (orchestrator, Fable):** no approach touches forbidden surfaces; none cross Phase-1 boundary → C stands. **Spike composition note:** Eval case 1 requires the JIT per-page prompt, which C alone doesn't provide → spike = **C + minimal-A** (JIT banner in its smallest form). This matches the inventor's own observation that A is decoupled and cheap.

## Spike

- **Approach:** C + minimal-A (bulk-bar dual-mode grid + JIT banner) — first attempt, no iteration needed
- **Artifacts:** `lite/sandbox/invent-lite-page-tagging-workflow.html` (649L standalone) + `-eval.py` + `artifacts/invent/lite-page-tagging-workflow/` (eval-results.json, 3 screenshots)
- **Builder:** sonnet · **First-stage review:** opus (rerun byte-identical 3/3) · **Final:** Fable

| Case | Result | Evidence |
|---|---|---|
| 1 happy | PASS | 7/≤8 real actions (JIT tap + range apply); per-page gate refused on p20/p11/p30 ทุกครั้ง; floor map 11-16→1-6 exact |
| 2 edge | PASS | mezzanine 14 = M/no-num, skip ถูก convention; overwrite-confirm overlap=3; cancel = zero-op deep-equal |
| 3 adversarial | PASS | retag เก็บ objects 3→3 + folder rebucket + grid ย้ายกลุ่มสด; mis-tag มองเห็นในกลุ่ม; undo คืน deep-equal |

### Opus first-stage review — CONFIRM-WITH-CONCERNS

Graders honest (real dispatched events, deep-equal snapshots, ไม่มี hardcoded pass) แต่:
1. **Spike ใช้โค้ดจริง 0 บรรทัด** — premise "remap math เสร็จแล้ว" ยัง *asserted, not demonstrated*: guard `_pflFolderHasUserDrawnObjects`, `reseedActivePageFolders`, `_docSnap`/`_applyDoc` undo ยังไม่ถูก exercise กับ objects จริง
2. **Basement convention ผิดทาง** — C2 expected map นับ B ขึ้น (B1..B4) แต่ของจริง `_lovsSequentialFloor` (overview-setup.js:597-615) นับ**ถอยหลัง** (ลึกสุด=เลขมากสุด) — build ต้องยึดของจริง
3. **folderKey แบบหยาบ** — พิสูจน์ "rebucket เกิด" แต่ไม่พิสูจน์ per-page composite ids จริง
4. **Extraction `overview-grid.js` = งานบังคับ** (overview-setup.js 1059 > cap 1000, closure-coupled) — ต้องเป็น step แรกของ build ไม่ใช่ของแถม
5. Gate-swap (per-set → per-page) สอดคล้อง HT-7; ไม่มี forbidden surface

**Fable final verdict:** spike พิสูจน์ "รูปทรง workflow + UX ถูกต้องและวัดได้" — ความเสี่ยงที่เหลือทั้งหมดคือ integration ซึ่งกลายเป็น acceptance criteria ของ build sprint → recommend **GO**

## Decision

**GO** — user, 2026-07-04 at checkpoint (asked "fable ว่าไง" first; Fable recommended GO on 4 grounds: highest user value in queue + risks boxed into acceptance criteria + moderate cost on existing scaffolding + principled gate-swap; user confirmed).

- Sprint card: **INV-2026-07-04-002** (queued, `/bma-lite-dev`, depends-on INV-2026-07-04-001 ✅) — slice 1 = mandatory `overview-grid.js` extraction; opus's 3 concerns + basement-descending fidelity + simultaneous gate-swap encoded as acceptance criteria.
- Model ladder: haiku research → sonnet diverge/spike → opus first-stage review → Fable final → human GO.
