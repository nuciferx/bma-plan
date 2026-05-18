# Invent: Page Setup Redesign

- **idea_id**: `2026-05-18-21-51`
- **short-name**: `page-setup-redesign`
- **Status**: invent-in-progress (started 2026-05-18)
- **Tags**: bma-plan, ui, page-setup, page-naming, pdf-edit, p-med
- **Source (verbatim)**: "redesign หน้า Page Setup ui มีอะไไร บ้าง จะต้องมี ทำไอเดียมาประดิษ หรือ ต้องวิจัยก่อน แล้วเอาไปลงใน sandbox ปล ชอบระบบตั้งชื่อหน้าอัตโนมัต และ ควรมีการตัดหน้า pdf ถาวร ส่วยในรายละเอียดด้านซ้าย ควรมีข้อมมูลจริงๆอะไรบ้าง"

## User's stated direction (parsed)

1. **Redesign the Page Setup UI holistically** — what should be on it
2. **Likes** the auto page-naming system (keep / improve, don't remove)
3. **Wants** permanent PDF page deletion (current `excludedPages` is soft-hide; user wants hard delete)
4. **Asks** what real/useful data the left detail pane should show
5. **Process preference**: invent or research first, spike in `sandbox/`

## Current state (snapshot 2026-05-18, before invent)

- Modal overlay `#setup-overlay` opened via menu `⚙ Page Setup` and ribbon button
- **Left pane** = project-info form (`#proj-form-panel`) with 4 sections:
  - ข้อมูลโครงการ (project no, building type, work type)
  - ข้อมูลอาคาร (floors, GFA total, units)
  - ผังบริเวณ (zoning, road, user-input FAR/OSR/setback minima)
  - การตั้งชื่อและจัดหมวดหมู่ (6 auto-name prefixes: site / plan / elev / section / detail / schedule + `applyAutoNamesFromSetup()`)
- **Right pane** = `#tag-grid` thumbnails with search + filter + per-page name+category chips
- **Footer** = save status + "เริ่มวัด ▶"
- **Separate** page-manager modal `#pgmgr-overlay` (export PDF subset only — does NOT delete from working doc)
- `.bmaplan` v1 schema fields: `pageStore`, `pageRotations`, `pageTags`, `projectInfo`, `excludedPages`, per-page annotations
- Auto-name logic: prefix + page number per category (e.g. "ชั้น 1", "ชั้น 2", "รูปด้าน A") — purely sequential, no content awareness

## Research

> Run 2026-05-18 via `bma-researcher` (haiku). Verdict: **PRIOR_ART_PARTIAL**.

### 1. In-repo prior work

- **`proto/ui.html:576–630`** — Current `#setup-overlay` (Page Setup modal): left `#proj-form-panel` (4 sections) + right `#tag-grid-wrap`. Auto-naming = prefix + sequence per category.
- **`proto/ui.html:~2970-2984`** — `setPageName`, `setPageTag`, `toggleExcludePage`, `buildTagGrid`, `selectSetupPage`, `buildSidebar`. Exclude = soft-hide via `excludedPages` Set; `getNextPage/getPrevPage` skip excluded; export respects exclusion. **No hard-delete yet.**
- **`.bmaplan` v1 schema** — `pageStore, pageRotations, pageTags, pageNames, projectInfo, siteOrientation, excludedPages:[...]`. Pages tracked by **number, not by ID** → reordering would be a breaking change. Renaming fields breaks user saves.
- **Auto-name logic** — `applyAutoNamesFromSetup()` uses `inferSetupTag()` (page 1 → site, others → plan) + `countTagBefore()` for sequence. Purely sequential prefix; no content awareness.
- **`sprints/completed/2026-05-06-project-setup-ui/`** — defined current MVP scope. Redesign now on backlog.
- **`#pgmgr-overlay` (line 641)** — separate bulk-export-PDF tool. Currently CANNOT delete/reorder pages.
- **Mockup history** — `proto/sandbox/mockup-top-menu-redesign.html`, `mockup-ribbon-redesign.html`, `mockup-interactive-full.html` referenced Page Setup but did not redesign it.

### 2. External prior art (incumbents)

- **Bluebeam Revu** — `Document → Delete Pages` modal, thumbnails + multi-select + hard-delete. Set Manager = soft grouping. No content auto-naming.
- **Foxit PDF Editor** — `Organize → Delete Pages` modal; range picker + multi-select; extraction preserves annotations. Manual naming via page properties.
- **Adobe Acrobat Pro** — `Tools → Organize Pages` toolbar; multi-select thumbnails + Delete button. Must leave ≥1 page. Confirmation modal.
- **AutoCAD Sheet Sets** — Auto-name from layout-tab name (FIELD `CTAB`) or sheet metadata. **No OCR.** Title-block fields auto-populate.
- **PlanGrid** — Title-block OCR region + manual override + discipline prefix. Version sets. No permanent delete (uses version archival).

**Pattern summary:** Incumbents split deletion (Bluebeam/Foxit/Adobe = hard-delete modal) from naming (AutoCAD = field-based, PlanGrid = OCR region). **None ship "all-in-one Page Setup redesign"** — each is a separate concern.

### 3. Algorithms / libraries

| Library | Capability | Status | Note |
|---|---|---|---|
| `pdf-lib` (JS) | Client-side page delete/extract/merge | viable | MIT, ~80KB, `pdfDoc.removePage(index)` hard-deletes. Raster PDF works but loses original quality on rebuild. |
| PDF.js | Page rendering, metadata read | viable | Mozilla; metadata extraction only — deletion needs server. |
| pypdfium2 (server-side) | Already in stack | already-used | Could add `/rebuild-pdf` endpoint that drops `excludedPages` and re-serves. |
| Tesseract.js | OCR title block | **Phase 1 OUT** | Per CLAUDE.md OCR is excluded. Flag only. |

### 4. Phase 1 boundary risks

- **OCR for content-aware naming** → **OUT** (CLAUDE.md line 9). Content-aware auto-naming (AutoCAD title-block / PlanGrid OCR region) cannot land in Phase 1.
- **Hard PDF deletion** → 3 options: (a) client-side `pdf-lib`, (b) server-side rebuild endpoint, (c) mark-for-delete-on-export. Each has trade-offs.
- **`.bmaplan` compat** → Additive only. Renaming `pageTags` / `excludedPages` breaks user saves. Page-by-number indexing means reordering is risky.

### 5. Recommended direction

Three orthogonal axes (each can be picked independently):

1. **Deletion model**: (A) keep soft-hide / (B) add delete-on-export rebuild / (C) hard-delete in working doc.
2. **Left-pane inventory**: (A) project meta only / (B) + page categorization templates / (C) + OCR region selectors (OUT).
3. **Auto-naming strategy**: (A) sequential prefix (current) / (B) + per-page editor + reusable templates / (C) content-OCR (OUT).

**Algorithms = solved.** **Composition for BMA-Plan workflow = genuinely new.** Diverge on the *composition* (one coherent screen unifying review + categorize + delete + export-choice + project-info), not on algorithms.

### Verdict: PRIOR_ART_PARTIAL

Pre-existing tech (pdf-lib for client-side delete; sequential prefix already in repo) covers all building blocks. What's new is how to *compose* them into one coherent pre-measurement screen that answers the user's four concrete questions: (1) what's on the left pane, (2) hard or soft delete, (3) auto-name strategy, (4) one-screen flow.

Sources: Bluebeam Revu help, Foxit Organize Pages, Adobe Acrobat Organize Pages, AutoCAD Sheet Sets blog, PlanGrid Sheets help, pdf-lib GitHub.


## Frame

### Problem

The current Page Setup modal mixes 4 unrelated concerns into one cluttered left form (project info, building data, site-plan minima, auto-name prefixes) and a right thumbnail grid with no real *page lifecycle* — pages can be soft-hidden but never deleted, names are sequential-prefix only with no per-page workflow, and there's no clear "this page is ready / needs scale / has measurements" status. The user lands here right after Open PDF, before scale + measurement, and the screen does not answer their two practical questions: **"which pages am I keeping?"** and **"what is each page actually for?"**.

### Constraints

- **Phase 1 boundary** — No OCR, no AI title-block reading, no rule engine, no legal validation. Content-aware naming is OUT.
- **Raster-first** — Must work on scanned PDFs. Cannot depend on vector PDF text layer.
- **`.bmaplan` schema is additive only** — `pageStore`, `pageRotations`, `pageTags`, `pageNames`, `projectInfo`, `excludedPages` exist in v1; new fields OK, rename/remove BREAKS user saves.
- **Pages indexed by number (1..N)** — Hard-deleting a page from the working doc renumbers everything after it. Reordering is risky for the same reason. Any deletion model must address this.
- **Page-scoped layers locked** (`docs/design/PAGE_SCOPED_LAYER_MODEL.md`) — layer.id is per-page; Page Setup should surface layer state but not redefine it.
- **Workflow lock** — Open PDF → Set Scale → **Page Setup** → Measure → Review → Export. Page Setup sits before Set Scale per the current flow (though user typically opens it after a quick page browse).
- **Status-bar discipline** — Save state, page label, scale label all reactive to Page Setup actions. Renumbering pages on hard-delete must update all UI.

### Forbidden surfaces this idea must avoid

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — measurement math contract, untouched
- `pdfToC`, `cToPdf`, `RS` constant — coordinate math contract, untouched
- `buildSnapIndex`, `snap` — snap engine, untouched
- Core `/upload`, `/page/{n}`, `/analyse` endpoints — case isolation logic, only ADD endpoints (e.g. `/rebuild-pdf`) if needed; never edit existing
- `.bmaplan` v1 schema field names — read existing fields, ADD new optional fields only

### Success criteria (how spike proves it works)

The spike opens as a standalone HTML and demonstrates **at least 4 of these 5** with mock 10-page PDF data:

1. **One coherent screen** answers "what is each page" + "which pages stay" + "what do I name them" in a single flow (no separate page-manager modal)
2. **Permanent page deletion** is represented as either (a) hard-delete preview with renumber map shown, or (b) export-time rebuild with checkbox per page — user can see the consequence before committing
3. **Auto-naming is template-driven, not just prefix** — e.g. user picks a template per page tag and the name regenerates; per-page override possible; templates saved
4. **Left detail pane has a clear inventory** of what belongs there (not the current "everything dumped in") — proven by the spike layout, even if some fields are mock
5. **Status indicator per page** showing readiness: has-rotation, has-tag, has-name, has-scale, has-measurements, excluded/deleted

### Out of scope (explicitly NOT solving in this invention pass)

- OCR / content-aware naming (Phase 1 OUT)
- Multi-PDF merge / split into multi-document project (Phase 2)
- Reordering pages (drag to reorder) — possible follow-up but renumber complexity puts it out for first spike
- Per-page password / encryption / access control (Phase 2+)
- Bulk annotation operations from Page Setup (separate concern, see `docs/invent/comment-redesign.md`)
- Integration with K.1 generator, FAR/OSR pass-fail UI (Phase 1 OUT — historical v2 only)


## Diverge

> Run 2026-05-18 via `bma-inventor` (sonnet). 5 approaches on 5 different axes.

### A — two-column-gateway (axis: information-architecture)

Two-stage gateway. Step 1 (full-screen) = thumbnail film-strip with Keep / Skip / Delete-on-close buckets. Step 2 = split view: left = selected-page detail card, right = remaining strip. Project metadata moves to a separate sidebar accessible any time.

- **Delete model**: 3 states (Keep / Skip / Delete-on-export). New `deletedPageNumbers` field; new `/rebuild-pdf` endpoint strips deleted pages server-side and renumbers. Renumber map confirmed before commit.
- **Auto-name**: Template per tag with `{n}` token, stored `projectInfo.autoNameTemplates`. Per-page manual override wins.
- **Left pane (Step 2)**: selected-page detail card — large thumb, tag, name, scale badge, object count, layer names, rotation, template preview.
- **Status**: per-thumbnail chips — rotation, tag pill, name check, scale traffic-light, measurement count.
- **Forbidden touch**: NO. **Phase 1 crossing**: NO.
- **Schema delta**: `deletedPageNumbers: number[]`, `projectInfo.autoNameTemplates: Record<string,string>` (both optional, additive).

### B — always-on-side-rail (axis: workflow-positioning)

Modal removed entirely. Page Setup = a collapsible left-rail panel — always accessible alongside the canvas. "Pages" tab = film-strip with per-page status; "Project" tab = project metadata. Workflow lock step "Page Setup" becomes a readiness badge in the status bar instead of a hard gate. First-run tooltip sequence guides new users.

- **Delete model**: soft-hide only (existing `excludedPages`). Hard-delete deferred to a secondary "Manage Pages" dialog to avoid accidental destructive clicks in an always-on panel.
- **Auto-name**: same template system as A, triggered inline on tag pick.
- **Left pane**: 2 tabs — Pages (film-strip) + Project (form).
- **Status**: color-coded row per page — icon row (rotation/tag/name/scale/objects) + traffic-light dot.
- **Forbidden touch**: NO. **Phase 1 crossing**: NO.
- **Schema delta**: `projectInfo.autoNameTemplates: Record<string,string>` (additive).

### C — delete-with-renumber-map (axis: page-lifecycle-model)

Keep current modal shape. Add a first-time "Page Triage" step prepended above the existing form. Horizontal film-strip; user drags pages into Include / Skip / Delete buckets. On confirm → renumber-preview table (old → new). On "Confirm & Rebuild" → `/rebuild-pdf` (PyMuPDF `doc.delete_page()` reverse order, re-analyse). Project metadata + auto-naming unchanged.

- **Delete model**: 3-state lifecycle with explicit renumber preview. `/rebuild-pdf` endpoint.
- **Auto-name**: unchanged (prefix-only). This approach is laser-focused on lifecycle.
- **Left pane**: unchanged.
- **Status**: only in triage step (bucket counters); after rebuild, existing tag-grid chips.
- **Forbidden touch**: NO. **Phase 1 crossing**: NO.
- **Schema delta**: `deletedPageNumbers: number[]` (cleared after rebuild — pages are gone).

### D — smart-left-pane-inspector (axis: left-pane-inventory) ★ TOP

Keep right thumbnail grid. Redesign left pane into a **context-sensitive inspector** that changes by selection.

- **Nothing selected** → "Project Readiness Dashboard": progress bars (Pages categorized N/M, named N/M, scaled N/M, with measurements N/M) + Top issues list with page links.
- **Page selected** (click thumb) → page property card: tag, name + template preview, rotation badge, scale status, object count, layer list. Project metadata (building type, GFA, etc.) → collapsible "Project Info" accordion at bottom of left pane, collapsed by default.
- **Delete model**: soft-hide (existing). "Delete permanently" link in page-card opens a renumber-map dialog **borrowed from approach C** (covers user's "permanent delete" requirement).
- **Auto-name**: template-driven with live preview in page card.
- **Status**: per-thumbnail tag pill + single traffic-light dot (green/amber/red). Tooltip = breakdown.
- **Forbidden touch**: NO. **Phase 1 crossing**: NO.
- **Schema delta**: `projectInfo.autoNameTemplates: Record<string,string>` (additive). If renumber-delete is implemented, also add `deletedPageNumbers: number[]`.

### E — template-name-engine (axis: auto-name-strategy)

Keep modal layout + lifecycle unchanged. Redesign **only** the auto-naming into a token-based template engine. Per-tag template strings (`{n}`, `{prefix}`, `{suffix}`, `{floor}`). Live preview column in tag-grid. Preset dropdown saved in localStorage. "Apply all" / "Apply uncustomized" buttons.

- **Delete model**: unchanged.
- **Auto-name**: token templates per tag in `projectInfo.autoNameTemplates`. `pageNameCustomized: number[]` tracks manual overrides.
- **Left pane**: existing form + new "Name Templates" section replaces 6 prefix inputs.
- **Status**: "template name" vs "custom name" pencil icon. Summary chip "Names set: 34/45".
- **Forbidden touch**: NO. **Phase 1 crossing**: NO.
- **Schema delta**: `projectInfo.autoNameTemplates` + `projectInfo.pageNameCustomized: number[]` (additive).

## Score

| approach | novelty | accuracy | UX | model-fit | boundary | cost | total |
|---|---|---|---|---|---|---|---|
| A two-column-gateway | 5 | 5 | 4 | 4 | 5 | 2 | **25** |
| B always-on-side-rail | 4 | 3 | 5 | 3 | 5 | 3 | **23** |
| C delete-with-renumber-map | 3 | 4 | 3 | 5 | 5 | 3 | **23** |
| **D smart-left-pane-inspector** | **3** | **5** | **4** | **5** | **5** | **4** | **26** ★ |
| E template-name-engine | 2 | 3 | 3 | 5 | 5 | 4 | **22** |

**Override check** — top approach D: `forbidden_surface_touch: NO`, `phase_1_crossing: NO`. ✅ Valid to rank first.

## Recommendation

**Spike D (smart-left-pane-inspector) with C's renumber-map dialog embedded** as the "Delete permanently" action. This directly answers all 4 user questions:

- **Q1 "what should be on the left"** → context-sensitive inspector with clear inventory (dashboard mode + page-property mode)
- **Q2 "permanent page deletion"** → renumber-map dialog from approach C, triggered from page-card
- **Q3 "auto-naming"** → token-template engine (subset of E) inline in page-card
- **Q4 "one coherent screen"** → all unified in the modal, no separate page-manager

**Fallback for spike**: C alone if D's mode-switch (dashboard ↔ page-card) feels confusing during prototyping. C is the most surgical and reliably advances the lifecycle model on its own.


## Spike

> Run 2026-05-18. Standalone HTML in `proto/sandbox/invent-page-setup-redesign.html` (513 lines). Opens directly in browser — no server, no build step.

### Approach attempted

**D (smart-left-pane-inspector) with C's renumber-map dialog embedded** — composed per Recommendation. Implemented:

- 10-page mock with varied state (tags, rotations, scales: manual/auto-unverified/unknown, object counts)
- Right-side thumbnail grid with per-page chips: tag pill (color-coded), object-count, traffic-light dot (green/amber/red)
- Left pane context-switch:
  - **Nothing selected** → "Project Readiness Dashboard" — 4 progress bars (categorized / named / scaled / measured) + Top Issues list with click-to-jump links
  - **Page selected** → page property card — preview, tag picker, name input with live template preview, rotation + scale + objects + layers cells, "↺ ใช้ template" reset button when custom, **Danger Zone with permanent-delete button**
- Project Info accordion at bottom of left pane (collapsed by default) — contains project metadata form + token-based auto-name templates (`{n}` placeholder, edits trigger live grid re-render)
- Renumber-map dialog: shows old → new page mapping in a table with the deleted row crossed out and labeled "ลบ" in red; confirm/cancel; on confirm runs the renumber locally (simulates `/rebuild-pdf` server call)
- Built-in self-test panel at top — 6 checks (5 success criteria from Frame + 1 schema-additive bonus). Tests re-run on every action so user can see PASS/FAIL update live

### Outcome

**PASS — all 6 self-tests green when opened in browser.**

| # | Success criterion | Status |
|---|---|---|
| 1 | One coherent screen (no separate page-manager) | PASS |
| 2 | Permanent delete with renumber-map preview | PASS |
| 3 | Auto-naming template-driven with live preview | PASS |
| 4 | Left detail pane context-sensitive (dashboard ⇄ page-card) | PASS |
| 5 | Status indicators per page (traffic-light + chips) | PASS |
| 6 | Schema additive only (no forbidden field rename) | PASS (by construction — new fields are `autoNameTemplates`, `deletedPageNumbers`) |

### Notes for production sprint

- Template engine uses `{n}` token only in spike — production should add `{floor}` for Thai floor names (ชั้น 1, ชั้น 2 … ดาดฟ้า) per E's design
- Renumber commit in spike is purely client-side; production must call a new `/rebuild-pdf` endpoint that uses PyMuPDF `doc.delete_page()` in reverse order, re-runs `analyse`, and updates `pageStore` / `pageTags` / `pageNames` / `excludedPages` indexing
- After server rebuild, `deletedPageNumbers` should be cleared (those pages no longer exist); only kept in memory between mark-and-confirm
- Dashboard "Top issues" link uses `selected=N` then re-render — production should also auto-scroll the thumbnail grid to the selected page
- Color-coded traffic-light readiness rule: green = tag set + scale=manual; amber = tag set + scale=auto-unverified; red = untagged or scale=unknown. Production should make this rule configurable in Settings (ties to `INV-2026-05-15-002` settings panel)
- Project Info accordion stays collapsed by default — most projects fill these once. If user opens it, remember state across sessions (`bmaPlan.uiLayoutOptions.v1`)

### Fallback not needed

Approach D + C composition cleared all criteria on the first attempt. Fallback C (delete-with-renumber-map alone) was not exercised.


## Research — INV-2026-05-18-001c permanent delete addendum

> Run 2026-05-19 via `bma-researcher` (haiku). User requested research before building 001c. Verdict: **PRIOR_ART_PARTIAL**.

### Incumbent UX matrix (10 questions × 6 products)

| Tool | Delete surface | Immediate action | Reversible | Renumber preview | Save model | Confirmation |
|---|---|---|---|---|---|---|
| **Bluebeam Revu** | Document menu / right-click thumbnail / Ctrl+Shift+D | Modal: range/selected/current picker | Ctrl+Z within session | NO — implicit on save | Implicit on save/Export | Dialog confirms range |
| **Adobe Acrobat Pro** | Tools → Organize Pages / thumbnail | Multi-select + Delete button | Ctrl+Z within session | NO — inline renumber | File → Save / Save As | "Are you sure?" modal |
| **Foxit PDF Editor** | Organize tab / right-click / Select+Delete | Right-click → Delete Pages | **NO** — explicitly permanent | NO — inline renumber | File → Save / Save As only | "Delete Pages?" dialog |
| **Nitro PDF** | Pages pane / right-click | Right-click → Delete | Partial session undo | NO | File save | Right-click → Confirm |
| **AutoCAD Sheet Sets** | Sheet Set Manager / right-click | Removes from set | Undo in drawing | NO (sheets ≠ doc order) | Manual save | Right-click only |
| **PlanGrid** | Version archival, not delete | Create new "version set" | YES — older versions preserved | NO — versioning not deletion | Auto version archival | Version name picker |

**Annotations on deleted pages — ALL incumbents**: deleted with page (no "move to preserved" logic). PlanGrid is unique with version-archival (keeps all old sheets).

### Key insights

1. **Renumber preview is rare** — only BMA's spike + AutoCAD's "Rename & Renumber" offer it. Most tools rely on user trust + implicit renumber. **BMA's preview is genuinely better UX than incumbents.**
2. **Undo is session-scoped** — Ctrl+Z works only before save. After save, hard-delete is final.
3. **Weak confirmations** — Foxit "permanent"; Acrobat "are you sure?"; others just a dialog. Renumber preview itself is the strongest confirmation.
4. **Save triggers finality** — Foxit explicit: delete is non-reversible after save. Adobe/Bluebeam same in practice (no in-PDF trash).
5. **Annotations follow pages** — universal pattern. BMA stores annotations in `.bmaplan` (separate from PDF) so this is actually our easiest part — reindex client-side dicts.

### Library/algorithm

- **PyMuPDF `doc.delete_page(n)`** → already in stack, raster-safe, reverse-order deletion avoids shift confusion. Recommended.
- **pdf-lib client-side `removePage`** → MIT ~80KB but raster PDFs lose quality on rebuild. Not recommended for raster-first BMA.
- No OCR/AI needed → zero Phase-1 boundary risk.

### Verdict: PRIOR_ART_PARTIAL

Algorithm = solved (PyMuPDF). UX pattern = mostly solved (incumbents all do implicit renumber + session undo). **BMA can ship better UX** with explicit renumber-map preview (spike already proved feasibility).

## Q1–Q4 Design Answers (post-research, 2026-05-19)

### Q1: ให้แก้ `proto/server.py` ได้ไหม?

**✅ YES — add new `/rebuild-pdf` endpoint (do NOT edit existing `/upload`, `/page/{n}`, `/analyse`).**

Rationale: precedent (U1, U2, SB-001, U1) all added new endpoints successfully. The "forbidden" surface table targets EXISTING core endpoints. New endpoint added next to them is permitted per the same pattern as `polyAreaM2` → add new functions alongside.

### Q2: `/rebuild-pdf` scope — in-place vs new case?

**✅ In-place edit of `CASES[case_id]["doc"]`.**

Rationale: PyMuPDF `doc.delete_page()` is in-place by design. Server flushes `page_cache` + `image_cache` + bumps `docVersion` so client's thumbnail URLs invalidate. `case_id` stays — no client rebind needed. Simpler + matches incumbents' "modify file in place" pattern.

### Q3: Client-side reindex strategy

**✅ Server-authoritative renumber map.**

Rationale: avoid client-side O(n²) shift loops that are error-prone with 7+ dicts. Server returns:
```json
{
  "totalPages": 9,
  "renumberMap": {"1":1, "2":2, "3":3, "4":4, "6":5, "7":6, "8":7, "9":8, "10":9},
  "deletedNumbers": [5]
}
```
Client uses `renumberMap` to walk every per-page dict (`pageStore`, `pageTags`, `pageNames`, `pageRotations`, `excludedPages`, `pageFloorKind`, `pageFloorNum`) and rebuild with new keys. Single helper `_reindexPageDicts(renumberMap)`. If `curPage` was deleted, redirect to nearest surviving page.

### Q4: Mid-draw protection

**✅ Hard-block during draw (matches HT-7 scale-gate pattern).**

Rationale: if `mPts.length > 0` (uncommitted polygon vertices) when user clicks "🗑 ลบถาวร", refuse with toast "วาดอยู่ — กด Enter จบหรือ Esc ยกเลิกก่อนลบหน้า". Same defensive pattern as HT-7's `_scaleGateBeforeMode()` — refuse the destructive action until user resolves the in-flight state.

### Confirmation UX (from research)

- **Renumber-map dialog** = primary confirmation (BMA's UX advantage over incumbents)
- **Warning line** "การลบนี้ไม่สามารถย้อนกลับได้หลังจากบันทึก" (Foxit style)
- **No second modal** — preview + warning line is enough
- **Undo**: session-scoped via `pushUndo()` before commit. After save, final.

## Decision

**GO** — 2026-05-18, user verdict after testing spike.

User feedback verbatim: "ตรวจแล้ว จะต้องมีชั้นใต้ดินด้วย และชั้น ห้องเครื่อง ชั้นดาดฟ้า และตั้งชื่อเองได้ ส่วนดีไซน์โอเค"

Design approved as-is. **One scope addition** for the production sprint: template engine must support floor sub-types beyond simple `{n}` sequencing — specifically **basement levels (ใต้ดิน 1, 2, …)**, **normal levels (ชั้น 1, 2, …)**, **mechanical floor (ชั้นห้องเครื่อง)**, **rooftop (ชั้นดาดฟ้า)**, and **per-page custom name** override.

### Refinement applied to spike

Spike updated 2026-05-18 to demonstrate floor sub-types:
- New optional schema fields per-page: `floorKind ∈ {basement|normal|mechanical|rooftop|custom|null}`, `floorNum: number|null`
- When `tag=plan` and `floorKind` is set, the floor sub-type drives the auto-name (not the generic `{n}` token)
- New UI in page-card: floor-kind picker + numeric input for basement/normal
- New self-test #6 verifies basement/mechanical/rooftop produce correct Thai names
- All 7 self-tests + 1 bonus = PASS

### Promoted to sprint

Sprint card: **INV-2026-05-18-001** — Page Setup Redesign (Approach D + C + floor-sub-types). Written into `docs/status/PHASE_INDEX.md` queued list for `/bma-dev-loop` pickup.

