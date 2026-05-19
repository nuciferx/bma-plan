# HT-18 — Phase A Audit (read-only drift map)

**Date:** 2026-05-19
**Sprint card:** docs/status/PHASE_INDEX.md → HT-18
**Source idea:** ~/.claude/ideas/IDEAS.md @ 2026-05-19 16:08 — "ระบบ save ไม่ตรงกับ ที่เขียนใน canvas"
**Audit method:** 3 parallel `bma-explorer` (haiku) deep enumerations + spot-checks.

---

## A1. Save (`_makeProjBlob`) — proto/ui.html L3176

12 top-level fields persisted:

| # | Field | Source | Notes |
|---|---|---|---|
| 1 | `version` | `1` (hardcoded) | Checked at load (throws on mismatch) |
| 2 | `pdfName` | `currentFileName` | Round-trip warning, not blocking |
| 3 | `totalPages` | `totalPages` | Snapshot at save |
| 4 | `pageStore` | dict (per-page objects) | See per-object section |
| 5 | `pageRotations` | dict (page → degrees) | |
| 6 | `pageTags` | dict (page → tag) | site/plan/elev/section/detail/schedule/other |
| 7 | `pageNames` | dict (page → label) | |
| 8 | `projectInfo` | dict | reqNo, buildingType, workType, floors, gfa, units, buildingClassification, buildingUseType, zoneCode, siteAccessRoadWidth_m, userDefinedLimits.{far_max, osr_min_pct, permeable_min_pct, setback_front_min_m, setback_side_min_m, setback_back_min_m} |
| 9 | `siteOrientation` | dict (per-page north config) | |
| 10 | `excludedPages` | `[...excludedPages]` (Set→Array) | |
| 11 | `pageFloorKind` | dict (page → basement/normal/custom) | INV-001b |
| 12 | `pageFloorNum` | dict (page → floor#) | INV-001b |

Pre-save hooks:
- `syncProjectInfoFromForm()` — reads form fields into `projectInfo`
- `normalizeAllObjects()` — assigns IDs + normalizes semantic fields for every object (in every page) before serialization

---

## A2. Load (`applyLoadedProject`) — proto/ui.html L3215

9 top-level dicts restored (3 validation-only fields handled separately at L3219):

| # | Restored | Pattern |
|---|---|---|
| 1 | `pageStore` | `proj.pageStore \|\| {}` |
| 2 | `pageRotations` | `proj.pageRotations \|\| {}` |
| 3 | `pageTags` | `proj.pageTags \|\| {}` |
| 4 | `pageNames` | `proj.pageNames \|\| {}` |
| 5 | `projectInfo` | `proj.projectInfo \|\| {}` |
| 6 | `siteOrientation` | `proj.siteOrientation \|\| {}` |
| 7 | `excludedPages` | `new Set(proj.excludedPages \|\| [])` |
| 8 | `pageFloorKind` | `proj.pageFloorKind \|\| {}` |
| 9 | `pageFloorNum` | `proj.pageFloorNum \|\| {}` |

Post-load hooks per page-store:
- `ensureStoreObjectIds(store)` — assigns missing IDs + normalizes semantic fields for `lines`/`polys`/`openings`/`refs`/`parking`
- `linkOpeningsInStore(store)` — re-resolves opening parent links
- Path geometry migration: `obj.geometryType === 'path'` + `obj.segments[]` → `obj.pts = flattenPathToPoints(obj, 1.0)` + `obj.closed = true`
- Parking defaulting: `if (!p.markerType) p.markerType = "parking"`

---

## A3. Save/Load drift verdict

✅ **NO top-level drift.** 12 fields saved ↔ 9 dicts restored + 3 validation-only (version/pdfName/totalPages). All symmetric.

✅ **Per-object drift** — pageStore is JSON.stringify-ed AS-IS. Per-object fields (`semanticTag`, `measurementProfile`, `objectCategory`, `reportTarget`, `lawBasis`, `countingRule`, `wallEdgeType`, `landEdgeRole`, `buildingHeight_m`, `markerType`, color/opacity/locked/areaType/useCategory/etc.) round-trip through JSON serialization without field-stripping.

✅ **Annotations** — `pageStore[pg].annotations[]` lives inside the per-page store. Persists via the `pageStore` dict serialization. Verified: `ensureStoreObjectIds` does NOT touch annotations (no risk of normalization stripping fields).

✅ **Defaults** — Only `markerType="parking"` and path→points migration. No risky implicit defaults that might silently override saved data.

**→ Field-level save/load drift is NOT the root cause** of "save ไม่ตรงกับที่เขียนใน canvas". State that IS in memory at save time DOES round-trip through JSON.

---

## A4. CRITICAL — pushUndo / isDirty leak (20 sites)

`pushUndo()` calls `_setDirty()` internally (L3180/L2841). Mutation sites that DON'T call `pushUndo()` → `isDirty` never flips → unsaved-changes warning never fires → user can close tab and lose state.

### Layer mutations (11 sites, 0 covered)

| Line | Function | Mutation |
|---|---|---|
| 2738-2746 | `moveLayerUp()` | Reorder |
| 2748-2756 | `moveLayerDown()` | Reorder |
| 2758-2769 | `renameLayer()` | `layer.name` |
| 2779-2787 | `setLayerColor()` | `layer.color` |
| 2802 | `toggleLayerLock()` | Lock toggle |
| 2830 | `setAllLayersVisible()` | Bulk vis |
| 2831 | `hideOtherLayers()` | Bulk vis |
| 2832 | `lockOtherLayers()` | Bulk lock |
| 2833 | `setAllLayersLocked()` | Bulk lock |

> Note: layer show/hide/lock/unlock for SELECTED row (L2825-2828) + solo (L2829) DO have pushUndo. Only bulk + move + rename + color leak.

### Page metadata (8 sites, 0 covered)

| Line | Function | Mutation |
|---|---|---|
| 1037 | `setQuickTag(pg, tag)` | `pageTags[pg]` + `pageNames[pg]` |
| 1038 | `hideSelectedPages()` | `excludedPages.add(...)` |
| 1041-1049 | `autoNamePage(pg)` | `pageNames[pg]` |
| 1052-1053 | `setPageFloorKind(pg, kind)` | `pageFloorKind[pg]` + `pageFloorNum[pg]` |
| 1056 | `setPageFloorNum(pg, n)` | `pageFloorNum[pg]` |
| 1059 | `applyAutoNames()` | bulk `pageTags` + `pageNames` |
| 1061 | `excludePage(pg)` | `excludedPages.add(pg)` |
| 1062 | `restorePage2(pg)` | `excludedPages.delete(pg)` |
| 1451 | `rotatePage()` | `pageRotations[curPage]` |

### Scale (1 site, 0 covered)

| Line | Function | Mutation |
|---|---|---|
| 2813 | `resetPageScale()` | Delete `calibScale` |

### Total: 20 mutation sites leak isDirty

---

## A5. Other pushUndo coverage (verified PRESENT)

✅ Object property changes (right panel L2061-2114): rename, areaType, useCategory, buildingHeight_m, refType, parkingType, color, opacity, label mode, link/unlink opening
✅ Object deletion (L2181, L2391/L2844, L3128)
✅ Draw completion (L2158, L3114)
✅ Marker placement (L2531)
✅ Annotation create/edit/delete (L1720, L1764)
✅ Scale line visibility toggle (L2814)
✅ Single-row layer show/hide/lock/unlock/solo (L2825-2829)
✅ F2 rename (L2818)
✅ Color/opacity picker mousedown anticipatory (L3332-3333)

---

## A6. Phase B scope (proposed)

**Fix strategy:** prepend `pushUndo();` to each of the 20 mutation handlers BEFORE the mutation. Each insertion is ~1-2 lines. Total Phase B LOC: **~30-40 lines** (well under 200-LOC SPLIT_REQUIRED threshold).

**Phase B sub-batches** (for surgical edits):
1. Layer reorder + rename + color (4 sites) — L2738-2787
2. Layer bulk visibility + lock (5 sites) — L2802, L2830-2833
3. Page tag + name (3 sites) — L1037, L1041-1049, L1059
4. Page floor (2 sites) — L1052-1053, L1056
5. Page exclude/restore (3 sites) — L1038, L1061, L1062
6. Page rotation + scale reset (2 sites) — L1451, L2813

**Per-batch:** prepend `pushUndo();` → done. No restructuring needed.

**Risks:**
- Bulk ops will create N undo entries per click (e.g. `applyAutoNames` mutates all pages). Acceptable: undo will progressively reverse. If user pain → wrap in a single `pushUndo` (current approach).
- One mutation site might be inside a callback that already does pushUndo at a higher level — verify each.

---

## A7. Phase C scope (proposed)

**E2E test:** `_test_ht18_save_load_round_trip` in `proto/e2e_ui_test.py`.

**Method:** open test PDF → mutate every category → save → reload → assert each mutation persisted.

**Mutation matrix** (≥12 sub-checks per sprint card):
1. Poly created → save/load → fields match (semanticTag, color, areaType, locked, lineWidth, opacity)
2. Opening linked to parent → save/load → parent link preserved
3. Line drawn → save/load → fields match
4. Ref point placed → save/load → fields match
5. Parking marker → save/load → markerType + count preserved
6. Annotation cloud → save/load → text + position preserved
7. pageTags set → save/load → tag preserved
8. pageRotations set → save/load → rotation preserved
9. pageNames set → save/load → name preserved
10. pageFloorKind/Num → save/load → preserved
11. excludedPages → save/load → preserved
12. projectInfo (all 12 form fields) → save/load → preserved
13. siteOrientation north → save/load → angle preserved
14. buildingHeight_m on a wall poly → save/load → preserved
15. semanticTag on every object type → save/load → preserved

Emit `PHASE_HT18_OK` marker if all sub-checks pass.

**Estimated LOC:** ~100-140 (helper + matrix + asserts).

**Total Phase B+C:** ~130-180 LOC. Single sprint OK.
