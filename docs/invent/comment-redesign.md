# Invent — Comment/Annotation system redesign

**Idea source:** `docs/status/PHASE_INDEX.md#discovered-backlog` (2026-05-17), refined 2026-05-18
**Short-name:** `comment-redesign`
**Status:** invent-in-progress
**Context:** BMA-Plan Phase 1 has 7 annotation tools with incomplete workflow: no individual delete, no inline edit, no threads, no list pane.

## Frame

### Problem
ผู้ตรวจแบบเอกสารใน BMA-Plan ปัจจุบันมี 7 annotation tools (Comment / Text / Highlight / Rect Frame / Circle Frame / Cloud Frame / Arrow) สร้างได้ทีละชิ้นแต่ขาด workflow — ไม่มี global list view, ไม่มี individual delete (มีแต่ clear-all), ไม่มี inline edit หลังสร้าง, ไม่มี author attribution, ไม่มี filtering/sorting, ไม่มีการเชื่อมกับ Properties panel.

ผลกระทบจริง: ผู้ตรวจไม่เห็น overview ของ comments ทั้งโปรเจกต์, ผู้ขออนุญาตที่รับ annotated PDF กลับมาตรวจไม่รู้ว่ามีกี่จุด/อยู่หน้าไหน.

### Constraints
- **Phase 1 boundary** — single-user (collaborative = Phase 2)
- **Raster PDF** — annotation overlay บน raster image, ไม่พึ่ง vector geometry
- **Page-scoped** — annotations อยู่ใน `pageStore[curPage].annotations` (per-page array)
- **`.bmaplan` schema additive** — เพิ่ม fields ใหม่ใน annotation object ได้ แต่ห้าม rename/remove existing
- **Forbidden surfaces (must NOT touch):**
  - `polyAreaM2`, `polyMetrics` — annotation ไม่เกี่ยวกับ area math
  - `pdfToC`, `cToPdf`, `RS` — coordinate conversion stays
  - `buildSnapIndex`, `snap` — annotations don't snap
  - `proto/server.py` core endpoints — `/export-pdf` already supports annotations
  - `.bmaplan` v1 schema fields — backward-compat for existing user saves

### Success criteria (testable in spike)
1. Markups List pane shows all annotations on current page (and option for whole project)
2. Each row: icon + subject + page# + hover ✎/🗑 actions
3. Filter by type (7 types), sort by time/page/type, search by text
4. Click row → jump to canvas + select annotation (highlight)
5. ✎ → inline edit (subject/color) in modal (HT-11 modal already exists, reuse)
6. 🗑 → individual delete (with confirm)
7. Round-trip: create annotations → save .bmaplan → reload → list shows same content
8. Schema-additive — load legacy `.bmaplan` v1 files unchanged

### Out of scope (this invention pass)
- Multi-user collaborative comments (threading, @mention, real-time sync) — Phase 2
- Resolved/Open state UI (Adobe/Figma pattern) — keep schema-additive `isResolved` for future
- Author attribution — schema-additive `author` field but no auth/identity infra
- Batch ops — defer until single-row hover actions prove useful
- Annotation = layer pattern — keep annotations separate from measurement layer system



## Research

### 1. In-repo prior work

- `proto/ui.html:160-172` — Annotate menu with 7 mode entries + Clear Annotations
- `proto/ui.html:1250` — `addAnnotation(ann)` pushes to `pageStore[curPage].annotations[]`
- `proto/ui.html:1251` — `clearAnnotations()` deletes ALL on current page (no individual delete)
- **Annotation data** — id, type, pts, text?, color, opacity, createdAt per page in `.bmaplan`
- **Export** — Annotations serialized to PDF via `/export-pdf` (2026-05-13 RUN, `ANNOT_OK` marker)
- **No Properties panel** — Annotations show same Properties as measurement objects
- **No filtering** — No way to find comments by type, date, or topic

### 2. App survey: 8 competitors

**Bluebeam Revu** — Markups List (table, sortable, filterable by status/author/type); double-click to edit subject; nested replies; author stamped; batch delete/color/status change. Canonical for PDFs.

**Foxit PDF Editor** — Comments pane (filterable by type); tap to edit via Appearance dialog; flat replies on notes; batch multi-select on canvas; author in metadata.

**Adobe Acrobat Pro** — Comments pane (reverse-chrono, open/resolved filters); click to open thread inline; full nested replies with @tags; author auto-stamped; delete individual or thread.

**PlanGrid** — Canvas-only (no list pane); inline text edit overlay on tap; flat comments; author+date visible on markup; multi-select on canvas.

**Procore Drawings** — Sidebar per-markup (not global list); comment sidebar opens on select; threaded comments per markup; author+timestamp; delete markup or comment.

**Figma** — Comments pane (shows unresolved count); click to edit inline; full nested replies; author auto-tagged with @mention; delete own reply or thread.

**Google Docs** — Comment history pane (All/For you/Open/Resolved filter); click to open thread inline; full nested with @mention; author auto-tagged; delete individual.

**Miro** — Comments pane (resolved separate); click object → sidebar reply; full nested comments; author+timestamp; can assign to user; delete own or creator thread.

**Key finding:** Bluebeam List is canonical for PDFs (global table view). Most modern tools ship full threading + resolved state. Sidebar/canvas-only tools trade discovery for mobile simplicity.

### 3. Inline-JS library options

| Library | Fit | Notes |
|---|---|---|
| PDF.js Express | No | Bundler-dependent, commercial |
| pdfAnnotate.js | Partial | MIT, CDN, lightweight; no thread UI |
| Tiptap Comments | No | Heavy (~100KB), collage paradigm |
| Hand-built widget | Yes | ~400 lines, no dep, Phase 1 scope |

**Conclusion:** Hand-built lightweight comment-list pane is pragmatic for Phase 1. Threading is Phase 2.

### 4. Data model & algorithm

**Current BMA-Plan annotation:**
```
id, type, pts, text?, color, opacity, createdAt
Stored per-page in .bmaplan v1 JSON
```

**Incumbent patterns (for Phase 2 reference):**
- Author field + timestamp — Bluebeam, Adobe, Figma, Google Docs, Miro
- Resolved boolean — Adobe, Figma, Miro, Google Docs
- Reply array — Adobe, Figma, Procore, Miro (nested)

**Backward compat:** Adding optional `author?`, `isResolved?`, `replies?` is schema-compatible.

### 5. Competitor measurement UX patterns

| App | List pane | Edit after create | Threading | Attribution | Phase 1 fit |
|---|---|---|---|---|---|
| Bluebeam | Table (sortable) | Double-click in list | Nested replies | Auto-stamp | Excellent (canonical) |
| Foxit | Type-filtered pane | Appearance dialog | Flat | Metadata | Good |
| Adobe | Reverse-chrono | Inline thread edit | Full | Auto-stamp | Good |
| PlanGrid | Canvas-only | Inline overlay | Flat | Name+date | Fair (mobile trade-off) |
| Procore | Sidebar per-markup | Comment sidebar | Thread per-markup | Author+time | Fair (loses global view) |
| Figma | Thread-count pane | Inline reply edit | Full | Auto-tag | Good |
| Google Docs | Comment history | Inline reply edit | Full | Auto-tag | Good |
| Miro | Resolved-separate | Sidebar reply | Full | Auto-stamp+assign | Good |

**Phase 1 minimum viable:**
- List pane (Bluebeam style) showing all annotations on current page
- Individual delete (currently missing blocker)
- Inline edit after create (double-click in list or inline editor)
- No threading required (Phase 2)
- Optional minimal author field (Phase 2)
- No batch ops required (individual + clear-all sufficient)

### Verdict: PRIOR_ART_PARTIAL

Bluebeam's Markups List is proven industry template for construction PDFs. Adobe/Figma show threading + resolved state are best-practice. **BMA-Plan Phase 1 (single-user, raster-only) is simpler than any incumbent.**

**Design choice:** Adopt Bluebeam-style list pane (global table) NOT sidebar (per-object detail) or canvas-only (PlanGrid). Measurement workflow benefits from seeing all annotations at once.

Hand-built ~300-400 line widget is pragmatic. Threading and resolve-state are natural Phase 2 additions.

---

## Summary for invent loop

**Prior art maturity:** PRIOR_ART_PARTIAL

**Recommendation:**
1. SKIP library exploration — no widget fits single-HTML + Phase 1 well
2. ADOPT Bluebeam Markups List pattern (table, sortable, click-to-canvas)
3. DIVERGE on edit UX — Properties panel vs inline-in-list vs modal?
4. Scope Phase 1 lean — individual delete + list pane are must-haves; threading Phase 2
5. Schema-additive — add optional author, isResolved, replies fields to unblock Phase 2 multi-user


## Diverge

### Approach A: Markups Tab in Right Panel  (axis: UI)
- 5th tab "📝 Markups" in right panel tab strip
- Renderer `_renderMarkupsInPanel` separate from `_renderListInPanel`
- curPage only, filter/sort/search + ✎/🗑 hover actions
- Touches: `proto/ui.html` (tab HTML + JS renderer ~150 LOC)
- Schema additive: `ann.subject?`
- Forbidden surface: NO
- Spike cost: ~180 LOC

### Approach B: Cross-Page Markups Index + Floating Widget  (axis: storage)
- In-memory `pageStore.markupsIndex` rebuilt on annotation change
- Floating widget (like summary widget) cross-page, page# column, click-jump
- Touches: `proto/ui.html` (~260 LOC)
- Schema impact: zero — derived in-memory
- Forbidden surface: NO
- Spike cost: ~260 LOC

### Approach C: Annotation Context Drawer  (axis: interaction)
- Canvas-edge drawer slides in when annotation clicked
- Shows detail + siblings (mini-list), inline ✎/🗑, prev/next breadcrumb
- Touches: `proto/ui.html` (~200 LOC)
- Schema additive: `ann.subject?`
- Forbidden surface: NO (uses existing annotationHitTest read-only)
- Spike cost: ~200 LOC

### Approach D: Annotations Sub-tab inside List Tab  (axis: data-model)
- Toggle "Objects | Annotations" inside existing List tab
- Show only annotations in annotation mode with new `ann.subject` field
- Touches: `proto/ui.html` (`_renderListInPanel` extension ~80 LOC)
- Schema additive: `ann.subject?`
- Forbidden surface: NO
- Spike cost: ~120 LOC

### Approach E: Dedicated Markups Modal (Bluebeam-clone)  (axis: algorithm)
- Full-screen modal opened via Annotate menu
- Table columns: icon/subject/type/page/time/color/actions, sortable headers
- Cross-page rebuild on open
- Touches: `proto/ui.html` (~280 LOC)
- Schema additive: `ann.subject?`, `ann.isResolved?`
- Forbidden surface: NO
- Spike cost: ~300 LOC

## Score

| Approach | Novelty | Accuracy | UX | Model Fit | Boundary | Spike Cost | Total |
|---|---|---|---|---|---|---|---|
| A Markups Tab | 2 | 3 | 4 | 5 | 5 | 4 | **23** |
| **B Cross-Page Index** | **3** | **5** | **4** | **4** | **5** | **3** | **24 ★** |
| C Context Drawer | 4 | 2 | 3 | 4 | 5 | 4 | 22 |
| D Sub-tab in List | 2 | 3 | 2 | 5 | 5 | 5 | 22 |
| E Bluebeam Modal | 3 | 5 | 3 | 4 | 5 | 2 | 22 |

## Recommendation

**Spike B (Cross-Page Markups Index + Floating Widget).** Wins on accuracy (cross-page overview = success criterion #1) + zero schema impact.

**Fallback:** Approach A (Markups Tab in right panel) — if floating widget clashes with canvas area, falls back to right-panel tab pattern that's proven safe (matches HT-8d-1/2 work).

**Phase 5 SCORE verification:** ✅ Top approach (B) has Boundary=5 — zero forbidden surface touches, schema-additive only, Phase 1 boundary respected.

## Spike

**File:** `proto/sandbox/invent-comment-redesign.html` (single standalone HTML, no server, no deps)

**Approach attempted:** B — Cross-Page Markups Index + Floating Widget

**Architecture in spike:**
- Mock `pageStore` with 5 pages, pre-seeded 8 annotations across 4 pages (page 5 intentionally empty to test edge case)
- `rebuildIndex()` iterates pageStore → flat `markupsIndex` array of {pageNum, annIdx, annId, type, subject, text, color, createdAt}
- Floating widget (draggable via header) renders index with filter (type) + sort (time/page/type) + search + scope toggle (current page / all pages)
- Click row → if pageNum ≠ curPage, calls `loadPage(pageNum)` then highlights marker on canvas (visual flash)
- ✎ → modal with subject + color edit (HT-11 modal pattern)
- 🗑 → individual delete with confirm + index rebuild

**Outcome: PASS** — 10 automated acceptance checks run 1.5s after page load:

| # | Check | Result |
|---|---|---|
| 1 | List shows annotations across pages (≥5 entries) | ✅ |
| 2 | Row layout: icon + subject + page# + ✎/🗑 | ✅ |
| 3 | Filter by type=comment returns subset | ✅ |
| 4 | Sort by page returns ascending order | ✅ |
| 5 | Search "ห้องนอน" finds 1 match | ✅ |
| 6 | Cross-page click row jumps to other page + selects | ✅ |
| 7 | ✎ opens modal + saves edited subject | ✅ |
| 8 | 🗑 individual delete reduces index count | ✅ |
| 9 | Round-trip: JSON.stringify(pageStore) → parse → rebuildIndex → identical | ✅ |
| 10 | Schema-additive: legacy ann without `subject` field falls back to `text` | ✅ |

**Verification method:** automated checks injected into spike HTML — open the file in any browser → wait 1.5s → see the report panel turn all checks green (or red if regression).

**Cross-page jump:** the central UX value-add — clicking a row whose pageNum ≠ curPage automatically calls loadPage() + selects + visual flash. Verified in check #6.

**Schema additive proof:** check #10 pushes a "legacy" annotation without `subject` field into pageStore; widget displays it correctly by falling back to `text` field. No schema migration needed for existing `.bmaplan v1` files.

## Recommendation

Promote to production sprint **INV-2026-05-18-001 — Comment/Annotation system redesign (Markups List widget + cross-page index)**. Approach B has Boundary safety = 5 (zero forbidden surfaces, schema additive only). ~260 LOC estimate. Floating widget pattern proven by existing `#summary-widget` infrastructure (HT-8d-2). Modal pattern proven by HT-11 (`ann-edit-overlay`).

## Decision

**PENDING-CHECKPOINT** — awaiting user GO / NOGO / RESHAPE.
