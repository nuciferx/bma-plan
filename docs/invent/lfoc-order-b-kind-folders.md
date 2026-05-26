# LFOC-ORDER-B — Kind-aware PF folder separation + migration

**Status:** invent-done-go (2026-05-26)
**Skill:** `/lite-invent`
**Spike:** `lite/sandbox/invent-lfoc-order-b-composite-id.html` (Playwright-verified 11/11 PASS)
**Build:** via `/bma-lite-dev` (lite-builder worker)
**Depends on:** LFOC-keep (`90b0b81`) + LFOC-ORDER-A (`7a6992b`)

## Problem

`pageFolderIdFor(n, tag, floorNum)` in `lite/static/js/page-folder-layers.js` derives PF folder IDs from `tag` + `floorNum` only. The `pageFloorKind` field (LFLOOR-1a: normal/basement/mezzanine/mechanical/rooftop) is ignored.

**Data-loss bug** (discovered by `bma-sim-driver` on 45-page permit):
- p20 = tag `floor`, floor# `1`, kind `basement` → maps to `PF_floor_1`
- p11 = tag `floor`, floor# `1`, kind `normal`   → maps to `PF_floor_1`
- Both → SAME folder → user's basement-1 vs ground-1 semantic distinction collapses. Auto-seeded base layers (gfa/ded/ded) shared → take-off becomes wrong.

Same for mezzanine: p15 floor#2 kind=mezzanine merges with p12 floor#2 kind=normal.

## RESEARCH verdict (Phase 2, `bma-researcher`)

`PRIOR_ART_PARTIAL`. Tuple sort is standard (AutoCAD prefix strings, Revit elevation-based ordering). Lite integration — folding `pageFloorKind` into folder ID + a kind-aware rank function — is the novel piece. No incumbent uses a composite `{tag, floor, kind}` 3-tuple folder ID; this is a lite-specific design.

## DIVERGE + SCORE (Phase 4-5, `bma-inventor`)

Inventor produced 4 approaches:

| Approach | Axis | Score (24max) |
|---|---|---|
| **A** Composite-string ID (`PF_floor_basement_1`) | ID encoding | 24 |
| **B** Kind field on folder object, ID unchanged | Data model | 24 |
| **C** Nested kind buckets (3-level tree) | Representation | 17 (ruled out — violates mezz-interleaved UX) |
| **D** Runtime comparator tuple sort | Render ordering | 19 |

Inventor recommended **B**. Main agent (Opus) **overrode to A** on review: B's "collision handler" (`PF_floor_2__b` disambiguation suffix) is hidden complexity that degenerates to A under the very case LFOC-ORDER-B exists to fix. A is explicit + predictable + self-documenting in JSON.

## FRAME (final)

**ID format (composite-string, additive):**

```
PF_site               → tag=site
PF_floor_<N>          → tag=floor, kind=normal (or kind=undefined — legacy compat)
PF_basement_<N>       → tag=floor, kind=basement
PF_mezz_<N>           → tag=floor, kind=mezzanine
PF_mech_<N>           → tag=floor, kind=mechanical
PF_floor_roof         → tag=floor, floor#=roof OR kind=rooftop (legacy preserved)
PF_excluded           → tag=excluded
```

**ID generation:**

```js
function pageFolderIdFor(page, tag, floorNum, kind) {
  if (!tag) return null;
  if (tag === "excluded") return "PF_excluded";
  if (tag === "site")     return "PF_site";
  if (tag !== "floor")    return null;

  kind = kind || "normal";  // LEGACY default

  if (floorNum === "roof" || kind === "rooftop") return "PF_floor_roof";

  switch (kind) {
    case "basement":   return "PF_basement_" + floorNum;
    case "mezzanine":  return "PF_mezz_"     + floorNum;
    case "mechanical": return "PF_mech_"     + floorNum;
    case "normal":
    default:           return "PF_floor_"    + floorNum;
  }
}
```

**Rank function (deterministic ordering):**

```js
function _rankPFFolder(folderId) {
  if (folderId === "PF_site")       return 0;
  if (folderId === "PF_excluded")   return 9999;
  if (folderId === "PF_floor_roof") return 9000;

  // PF_basement_N → 100 - N*5  → B3=85, B2=90, B1=95  (ascending = B3 first)
  var mb = /^PF_basement_(\d+)$/.exec(folderId);
  if (mb) return 100 - parseInt(mb[1], 10) * 5;

  // PF_floor_N → 100 + N*10
  var mf = /^PF_floor_(\d+)$/.exec(folderId);
  if (mf) return 100 + parseInt(mf[1], 10) * 10;

  // PF_mezz_N → 100 + N*10 + 5  (interleaved between floor N and N+1)
  var mm = /^PF_mezz_(\d+)$/.exec(folderId);
  if (mm) return 100 + parseInt(mm[1], 10) * 10 + 5;

  // PF_mech_N → 100 + N*10 + 7  (after mezz, before next floor)
  var me = /^PF_mech_(\d+)$/.exec(folderId);
  if (me) return 100 + parseInt(me[1], 10) * 10 + 7;

  return 5000;  // unknown PF
}
```

**Visual result (with sample dataset):**
```
PF_site (0)             📐 ที่ดิน + ผังบริเวณ
PF_basement_3 (85)      🅑 ชั้นใต้ดิน B3
PF_basement_2 (90)      🅑 ชั้นใต้ดิน B2
PF_basement_1 (95)      🅑 ชั้นใต้ดิน B1
PF_floor_1 (110)        🏢 ชั้น 1
PF_floor_2 (120)        🏢 ชั้น 2
PF_mezz_2 (125)         🅜 ชั้นลอย (Mezz 2)
PF_floor_3 (130)        🏢 ชั้น 3
PF_floor_4 (140)        🏢 ชั้น 4   (legacy — p20 with no kind field)
PF_mech_5 (157)         ⚙️ ชั้นเครื่อง M5
PF_floor_roof (9000)    🏠 หลังคา
PF_excluded (9999)      🚫 ไม่ใช้คำนวณ
```

## Migration story

**ZERO migration code.** Old `.bmaplan` files without `pageFloorKind` on pages:
- `pageFolderIdFor(n, "floor", N, undefined)` → falls through "normal" branch → returns `PF_floor_<N>`
- Identical to today's output → folder structure unchanged → no data movement

`liteGroups` array in `.bmaplan` (LST-2 persists folder list with `parentId` + `pages` + `kind`): new IDs coexist with legacy. Proto cross-open already ignores `liteGroups` (lite-isolated since LST-2).

## Backward compat guarantee

- Old saves (pre-LFLOOR-1a, no kind) → identical folder tree as today
- New saves with mixed kinds → distinct folders per (tag, floor#, kind)
- Reopening a new save in legacy code (impossible — same repo) — N/A

## Auto-seed extension

`_seedBaseLayers(folder)` needs kind-aware seeds:

| Folder | Layers seeded |
|---|---|
| `PF_site` | site / gfa / use (3) |
| `PF_floor_<N>` (normal) | gfa "GFA ชั้น N" / ded "ลิฟต์" / ded "บันได" (3) |
| `PF_basement_<N>` | gfa "GFA ชั้น BN" / ded "ลิฟต์" / ded "บันได" (3) |
| `PF_mezz_<N>` | gfa "GFA Mezz N" / ded "ลิฟต์" (2) |
| `PF_mech_<N>` | gfa "พื้นที่ชั้นเครื่อง" (1) |
| `PF_floor_roof` | gfa "GFA หลังคา" (1) |
| `PF_excluded` | none (0) |

Display-name helper `_floorLabel` + folder-render naming must also map the new IDs to human-readable Thai labels (per the visual result above).

## Build scope

1. `lite/static/js/page-folder-layers.js`:
   - `pageFolderIdFor` accepts 4th arg `kind`, branches per kind
   - `_rankPFFolder` adds regex branches for `PF_basement_`, `PF_mezz_`, `PF_mech_`
   - `_seedBaseLayers` kind-aware seeds (different layers per kind)
   - `_floorLabel` / display-name returns Thai label per ID prefix
   - All call sites of `pageFolderIdFor(...)` (incl. `reseedActivePageFolders`, `pageFolderOfLayer`, `layersOfPage`, `layer-panel.js` `_lpDoAddLayer` fallback) pass `pageFloorKind[n]`
2. NEW `lite/tests/test_pf_kind_folders.py`: ≥10 sub-checks proving separation + ordering + backward compat
3. Estimated net: ~50 LOC + ~150 LOC test

## Acceptance markers

- NEW: `LITE_PF_KIND_OK` (≥10 sub-checks)
- Regression GREEN:
  - `LITE_PAGE_FOLDER_MODEL_OK`
  - `LITE_PAGE_FOLDER_PERSIST_OK`
  - `LITE_PAGE_FOLDER_UI_OK`
  - `LITE_PF_ORDER_OK` (from LFOC-ORDER-A)
  - `LITE_TREE_UI_OK`, `LITE_LAYER_DND_OK`
  - `LITE_CFSS_PERSIST_OK`, `LITE_OVERVIEW_SETUP_OK`
  - `MEASURE_PARITY_OK`

## Forbidden surfaces (UNTOUCHED)

- `lite/static/js/measure-engine.js`, RS, `pdfToC`/`cToPdf`, area math, semanticTag (role-derived)
- `lite/ui-lite.html` (cap 1200/1200)
- `lite/static/js/layer-system.js`, `layer-tree.js`, `layer-dnd.js`, `layer-panel.js` (only call-site arg added, no logic change)
- `lite/static/js/overview-setup.js` (LFLOOR-1c/1a stays)
- `.bmaplan` schema (additive only — new ID strings only)

## Open question for the build phase

`_lpDoAddLayer` (LFOC-1f orphan fallback) calls `pageFolderIdFor(curPage, pageTags[curPage], pageFloorNum[curPage])` with 3 args. After this sprint, it needs the 4th arg `pageFloorKind[curPage]`. Verify the addLayer fallback still places a custom layer in the kind-appropriate folder (e.g. if current page is basement-1, "+" creates layer under `PF_basement_1`, not `PF_floor_1`).
