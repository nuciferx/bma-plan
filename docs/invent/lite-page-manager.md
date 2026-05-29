# Invent pass — lite page manager (GoodNotes/ABBYY-style page management)

- **Date:** 2026-05-29
- **Skill:** `/lite-invent`
- **Source idea:** user 2026-05-29 "เอาวิธีการจัดการหน้าต่างๆ ใน pdf แบบ GoodNotes / ABBYY"
  merged with queued idea `ideas 2026-05-29` → "Permanently add or remove pages from an uploaded PDF" (IDEAS.md @ 2026-05-29 11:47)
- **Status:** ✅ **GO (approach D)** — user decided 2026-05-29 → sprint card `INV-2026-05-29-LPM` (build via `/bma-lite-dev`)
  - **Decisions:** (1) approach **D**; (2) save = **mutate case-file at flush**; (3) v1 **includes multi-file merge**; insert/blank-page **parked**.
- **Spike:** `lite/sandbox/invent-page-manager/` — `node eval.js` → **6/6 ACCEPT**

## Problem
Lite manages PDF pages only by: navigate (thumbnail click), soft-exclude (⛔), tag, rotate.
User wants GoodNotes/ABBYY page panel: **drag-reorder, permanent delete, duplicate** (+insert deferred).
Core blocker = **page identity**: every per-page state is keyed by page NUMBER (`PS[n]`, `pageTags[n]`,
`pageRot[n]`, `excluded[n]`, `.bmaplan pageStore[n]`), so any reorder/delete/insert shifts numbers and
silently corrupts attached measurement data.

## Research (bma-researcher) — verdict PRIOR_ART_PARTIAL
- PyMuPDF page mutation = **mature** — proto already shipped `/rebuild-pdf` (`delete_page` + renumberMap, 2026-05-19).
- GoodNotes/ABBYY page-panel UX = **mature** (drag-reorder, context-menu delete, thumbnail jump).
- **GREENFIELD part = lite's data model.** Number-keyed state has no reorder safety; proto's renumber-map
  dialog has no client reindex logic. The hard part is the data model, NOT the UI or the lib.

## Diverge + Score (bma-inventor) — 5 approaches
| | approach | axis | fst* | total |
|---|---|---|---|---|
| A | renumber-map relay (no UUID, server-authoritative) | storage-authority | NO | 21 |
| B | UUID identity layer, lazy remap | data-model | NO | 23 |
| C | slot-array indirection | representation | NO | 22 |
| **D** | **optimistic client + stable page-id + deferred server sync** | storage-authority | **NO** | **24** |
| E | number-keyed minimal baseline (proto port) | UX safety | NO | 20 |

\*fst = forbidden_surface_touch. All NO (none touch measure-engine / RS / pdfToC / .bmaplan non-additive).

- **Recommended spike: D** — highest score; only approach with full undo + instant (no-spinner) drag.
- **Fallback: E** — ~100 LOC, working delete/reorder/duplicate via atomicRemap, accepts no-undo as a documented Phase-1 limit.
- Discarded A (dominated by E/D); B & C valid but dominated by D (same accuracy/boundary, lower UX).

## FRAME + Eval
Forbidden (lite): `measure-engine.js`, `RS`, `pdfToC`/`cToPdf`, `.bmaplan` non-additive renames, area-math reading a display name.
Out of scope: multi-PDF merge, insert-blank-page, handwriting/templates.

Runnable eval (data-model only, no PDF/server) — 5-page state markers A..E; sequence = move p5→pos2, delete "C", duplicate "B":
- **E1** survivors keep object/tag/rot/excluded by identity (no shift) — PASS
- **E2** "C" + all data gone, zero orphans — PASS
- **E3** duplicate is independent deep copy — PASS
- **E4** save→.bmaplan→reload deep-equal — PASS
- **E5** legacy number-keyed save loads + auto-migrates to id-keyed — PASS
- **E6** server renumber-map (journal replay) == live UI index 1:1 — PASS

**Result: 6/6 ACCEPT.** live order after sequence = `A,E,B,B′,D`; renumberMap = `{1:1,2:3,4:5,5:2}`.

## Key design decisions proven by the spike
1. **Stable id per page** (`pageOrder` = ordered ids); page number = index+1, derived on read. All state id-keyed.
2. **`.bmaplan` stays additive + proto-compatible**: `pageStore`/`pageTags`/`pageRot`/`excluded` saved number-keyed by
   *display index*; NEW optional `pageIdentities` array carries the ids. Legacy saves (no `pageIdentities`) load and
   auto-migrate (mint fresh ids) — old files never break.
3. **Deferred server sync**: mutations journalled in `pending`, flushed at save/export via one `/apply-page-mutations`
   (server replays reorder/delete/duplicate, returns renumberMap). Close-without-save = original PDF untouched.
4. **Undo** = snapshot stack (Ctrl+Z restores `pageOrder` + all id-dicts + journal).

## Sprint card `INV-2026-05-29-LPM` (build via `/bma-lite-dev`)
- New module `lite/static/js/page-manager.js` (≤1000 lines) owning `pageOrder` + id-keyed dicts + accessors
  (`idAt`/`numOf`/`PSn`...) + reorder/del/duplicate/undo + save/load migration.
- Refactor ui-lite.html per-page reads (`PS[n]`, `pageTags[n]`, ...) to route through accessors (~30 call-sites — main risk; **stage accessors first behind a flag** to de-risk the 1200-line cap).
- Port proto `/rebuild-pdf` → add `/apply-page-mutations` to `lite/server_lite.py` (reorder=`move_page`, duplicate=`copy_page`, delete=`delete_page`, **merge=`insert_pdf`**); returns renumberMap.
- Extend `#overview` panel → drag-reorder grid + del/dup context actions + **merge-file picker**.
- Markers: `LITE_PAGE_MANAGER_OK` (E1–E6 ported to `lite/tests/`) + `LITE_PAGE_MERGE_OK` (insert_pdf round-trip + id assignment for merged pages).

## Decisions locked (was open questions)
- **Save model = mutate case-file at flush** (chosen over export-new). Mutations journalled in `pending`, applied to the server PDF copy at save/export; close-without-save leaves the original untouched.
- **Multi-file merge IS in v1** (PyMuPDF `insert_pdf`); merged pages get freshly minted ids, `originNum=null`.
- **Insert/blank-page PARKED** — out of scope for v1 (permits are scanned, low value).

## Residual risk to watch during build
- Call-site refactor (~30 reads in ui-lite.html) is the real cost — stage accessors first behind a flag.
- Merge adds pages with no `originNum`; ensure the renumber-map / server replay handles new-page tokens (the spike's `simulateFlush` already models duplicate tokens the same way → extend for merge).

---

## Re-pass 2026-05-29 ("ต้องเพิ่มไรอีกไหม") — gaps found + closed in spike v2

Re-ran `/lite-invent` on the GO'd card to check completeness **before** `/bma-lite-dev` builds it. Recon of the *real* lite codebase (not the v1 assumptions) found 5 gaps that would corrupt a real save. v1 (`page-model.js`, E1–E6) was **happy-path only** — it violated the skill's own "eval taxonomy ≥3 (happy + edge + adversarial)" rule. Spike v2 (`page-model-v2.js` + `eval-v2.js`, **E7–E12 all PASS**) closes them. **Verdict: card stays GO, but build MUST follow v2, not v1.**

| # | Gap (verified in lite/) | Why it corrupts | Fix in v2 |
|---|---|---|---|
| **G-STATE** | lite has **7** number-keyed per-page dicts, not 4. v1 modelled `PS/tag/rot/excl` only and **missed `pageFloorKind`, `pageFloorNum`, `pageNames`** (`ui-lite.html:241`; save schema L910-912). | reorder/delete shifts floor-kind/floor#/name onto the wrong page → wrong floor designations + export rows. | fold **all** scalars into one id-keyed record (`meta_by_id`); "forgot a dict" becomes structurally impossible. **E7.** |
| **G-FOLDER** | page-folders carry a `.pages: number[]` (`page-folder-layers.js:23`). v1 never modelled groups. **⚠️ See v3 correction below — v2's "remap membership by id" fix was the WRONG mechanism.** | reorder/delete/dup desyncs `.pages` from reality → page-folder layer system breaks (`LITE_PAGE_FOLDER_*`). | ~~store membership by id, remap on mutation~~ **SUPERSEDED by v3:** `.pages` is DERIVED — let per-page meta move by identity, then call `reseedActivePageFolders()` to re-derive. **E8 (v2) / E13 (v3).** |
| **G-RENDER** | approach D shows the new order **instantly** but the page image still comes from the server, whose PDF is unchanged until flush. v1 had `originNum` but never used it for render. | display page *n* renders the **wrong page's** cached JPEG/thumb until the user saves. | `serverNum(n)` accessor → original server page; dup renders from source's server page; merged page = placeholder until flush. **E10.** |
| **G-REFLUSH** | users save **many times per session**; after a flush the server PDF *is* the new order. v1 set `_initialIds` once, never reset. | the 2nd save's renumber-map is computed against the **original** PDF → server mutates the wrong pages on the second flush. | `applyFlush()` re-baselines (`originNum := new index`, `pending := []`, `_initialIds := current`). **E9.** |
| **G-GUARD** | v1 allowed deleting down to **zero pages**. | empty document / `curPage` points at nothing. | `del()` refuses when `count()===1`. **E12.** Also bounded undo stack (45-page docs blew up v1's unbounded snapshots). |

Also corrected from the recon: real per-page read call-sites are **~70–90 across `ui-lite.html` + `static/js/*.js`** (not ~30); `ui-lite.html` is **1100/1200** (only 100 headroom) and `overview-setup.js` is **995/1000** — so the new `page-manager.js` module is mandatory and the call-site refactor must be **net-neutral** on `ui-lite.html` lines; lite `server_lite.py` is **fully read-only today (0 page-mutation endpoints)** — `/apply-page-mutations` is built from scratch, not "ported" from an existing lite endpoint.

**Spike v2 eval (phase-6 acceptance, taxonomy):** `node lite/sandbox/invent-page-manager/eval-v2.js` → **6/6 ACCEPT**
- E7 [edge] all 7 per-page fields survive reorder/delete/dup by identity
- E8 [adversarial] page-folder membership follows identity + saves as correct numbers + round-trips
- E9 [adversarial] second save re-baselines (renumberMap relative to post-flush PDF)
- E10 [adversarial] pre-flush render-source maps to original server page; dup renders from source
- E11 [edge] merge appends foreign pages; flush renumbers originals + assigns merged; placeholder→real
- E12 [edge] delete-last refused + legacy (no ids, `excludedPages` array, folders) migrates

(v1 `eval.js` E1–E6 still 6/6 — kept as the original record.)

## Sprint card additions (build MUST include these — fold into `LITE_PAGE_MANAGER_OK`)
1. **Page-data record, not 4 dicts** — `page-manager.js` owns ONE id-keyed record per page covering all 7 fields (`PS`, `tag`, `rot`, `excl`, `floorKind`, `floorNum`, `name`). Adding a future per-page field = edit the record + save/load fan-out, never a new parallel dict.
2. **`liteGroups`/page-folder remap is in scope** — membership held by id, serialised to numbers on save; delete removes dead refs; dup inherits. Regression `LITE_PAGE_FOLDER_*` must stay GREEN through a reorder+delete+dup sequence (new assertion).
3. **`serverNum(displayN)` for render/thumb** — `page-renderer.js` must request the *server* page, not the display page, until flush; merged pages show a placeholder. (This is the subtle heart of approach D — call it out so the builder doesn't wire render to display-number.)
4. **`applyFlush()` re-baseline after `/apply-page-mutations`** — reset `originNum`, clear `pending`, reset baseline. Add a **multi-save** acceptance test (mutate→save→mutate→save).
5. **Atomicity** (design note, not in spike): `/apply-page-mutations` must write to a temp PDF and swap on success; if the PDF mutation or the `.bmaplan` write fails, neither is half-applied. Add a flush-failure rollback test in the build sprint.
6. **Guards**: refuse delete-last-page; bound the undo stack.
7. Markers grow: `LITE_PAGE_MANAGER_OK` ports **E1–E12** (was E1–E6); `LITE_PAGE_MERGE_OK` unchanged.

Still **untouched** (forbidden): `measure-engine.js`, `RS`, `pdfToC`/`cToPdf`, `.bmaplan` non-additive. All v2 additions are additive (`pageIdentities`) or internal.

---

## Re-pass #2 2026-05-29 ("ตรวจหาจุดบกพร่องอีกครั้ง", Opus 4.8) — model correction + 2 new real bugs

A third, deeper read of `lite/static/js/page-folder-layers.js` proved **two of v2's own assumptions were wrong**, and found two bugs v1/v2 never tested. A green eval on a wrong model is *worse* than no eval — it manufactures false confidence — so this pass corrects the model in `page-model-v2.js`'s doc and adds `eval-v3.js` (**E13–E16, 5/5 PASS**). Net effect: the build gets **simpler** for folders and gains a **silent-data-loss guard**.

| # | Finding | Evidence | Build action |
|---|---|---|---|
| **C-FOLDER** (corrects v2 G-FOLDER) | A page-folder's id **encodes the floor** (`PF_floor_3`, `PF_basement_1`, `PF_site`, `PF_excluded`) and its `.pages` is **DERIVED** — `reseedActivePageFolders()` recomputes it from `pageTags`/`pageFloorNum`/`pageFloorKind`. `.pages` is set **nowhere else**. v2's "store membership by id + remap on every mutation" would *fight* reseed and double-maintain. | `page-folder-layers.js:85` `pageFolderIdFor`, `:123` `_collectFolderPages`, `:700-705` reseed iterates `1..pageCount` | **Do NOT remap folder membership.** Move per-page meta by identity (already done), then call `reseedActivePageFolders()` after a mutation → `.pages` re-derives for free. Drop v2's `groups`/`groupsOf` remap code from the build. **E13.** |
| **C-USER-FOLDER** | `kind:'user'`/legacy folders hold **layers via `parentId`**, not pages — they have no page membership to corrupt. | `page-folder-layers.js:24` | No special handling; just don't invent `.pages` for them. **E13b.** |
| **B-DIRTY** (NEW bug, adversarial) | `_docSnap()` — the unsaved-changes fingerprint — is `JSON{PS,excluded,pageTags,pageFloorKind,pageFloorNum,pageNames,projectInfo,_id}`. It has **no page order, no rotation, no liteGroups**. So a pure **reorder / duplicate / merge** would NOT flip `state.dirty` → user closes with no "unsaved changes" warning → **silently loses the entire page reorganization.** Dangerous twin of the "close-without-save = original untouched" decision. | `ui-lite.html:816` | **Extend `_docSnap()`** to include `pageOrder` (+ per-page identity & rotation). Add to `LITE_PAGE_MANAGER_OK`: pure reorder/dup/del each flips dirty. **E14.** |
| **B-DUP-REF** (NEW, edge) | duplicate-then-delete-original must leave the copy with fully independent data (no shared object reference back to the deleted page). v1/v2 tested dup OR delete, never the sequence. | — | covered by `deepCopy` in `duplicate()`; lock it with a regression. **E15.** |
| **B-NOOP** (NEW, edge) | a no-op reorder (drag a page and drop it in the same slot) must not journal garbage or desync `simulateFlush`. | — | guard `from===to` (skip snapshot+journal); identity renumber-map. **E16.** |

Also re-confirmed from this pass: **lite has NO manual "drag a page into a folder"** — page→folder assignment is 100% via tag/floor metadata, which the identity model already preserves. That removes a feature-interaction risk the v2 write-up implied.

**Spike v3 eval (phase-6, taxonomy):** `node lite/sandbox/invent-page-manager/eval-v3.js` → **5/5 ACCEPT** (E13 adversarial folder re-derive · E13b user-folder · E14 adversarial dirty-tracking · E15 dup-then-delete · E16 no-op reorder). v1 (E1–E6) + v2 (E7–E12) still green → **17 eval cases total**.

### Net change to the build (supersedes the v2 "sprint card additions" list)
- ❌ **Drop** v2 item #2 (folder membership remap) — replace with: *after every page mutation, call `reseedActivePageFolders()`*; assert `LITE_PAGE_FOLDER_*` stays GREEN through reorder+delete+dup (the re-derive, not a remap).
- ➕ **Add** B-DIRTY: extend `_docSnap()` with page order/identity/rotation; a page-only change must mark the doc dirty. **This is the highest-severity finding of the whole re-pass** (silent data loss > visual glitch).
- ➕ **Add** guards: no-op reorder short-circuit (`from===to`); dup-then-delete independence regression.
- Markers: `LITE_PAGE_MANAGER_OK` now ports **E1–E16**.
