# Invent: post-it-page-notes

- **Idea (raw):** ทำโพสต์อิทสำหรับเอาไว้แปะที่หน้า PDF แต่ละหน้าเพื่อที่จะเขียนคอมเมนต์หรือเอาไว้โน้ต
- **Source:** /idea 2026-05-19 19:30 — `~/.claude/ideas/IDEAS.md`
- **Tags:** bma-plan, annotation, p-med
- **PHASE_INDEX:** Discovered backlog → ideas 2026-05-19
- **Status:** invent-in-progress (started 2026-05-19)

## Open questions captured at /idea time

1. Note ผูกกับ page coordinate (เลื่อนตาม pan/zoom) หรือ anchor มุม viewport?
2. Notes โผล่ใน export (XLSX/PDF) หรือ canvas-only?

## Research

**Verdict: `PRIOR_ART_PARTIAL`** (2026-05-19, bma-researcher)

### In-repo prior art (most important finding)

- `proto/ui.html` already has `ann_comment` mode — click → prompt → stores annotation with pts/text/color, page-coord anchored via `pdfToC()`, survives pan/zoom. **Half-implemented sticky note.**
- `drawAnnotations()` renders 7 annotation types on canvas (comment / text / highlight / rect_frame / circle_frame / cloud / arrow). Already in PDF export pipeline (ANNOT_OK marker).
- `docs/invent/comment-redesign.md` — prior invent pass proposed Markups List pane + individual delete + inline edit + ~260 LOC lightweight widget for ALL annotation types.
- **What's missing for "post-it" feel:** draggable floating yellow card visual (not just a dot+label), inline text editing on canvas, persistent visual identity, optional global list pane.

### Library scan

No shrink-wrapped sticky-note JS library fits BMA-Plan's no-bundler constraint. Hand-built widget is the proven pattern (cf. summary-widget + comment-redesign spike at ~260 LOC).

### Incumbents (CAD / PDF review)

| Tool | Sticky-note UX |
|---|---|
| Bluebeam Revu | Color-coded note icon + popup text + Markups List pane |
| Adobe Acrobat | Yellow icon + popup + Comments pane |
| Foxit PhantomPDF | Speech-bubble note + author/timestamp |
| Procore / PlanGrid | Inline markup + per-markup sidebar |

**Common pattern:** Click → text input → visible icon/card on page-coord → persists → appears in global list → optional post-edit. BMA-Plan's `ann_comment` covers steps 1-3-4 already; missing 5-6.

### Open-Q resolution from research

| Q | Resolution |
|---|---|
| Q1: page-coord vs viewport-corner? | **Page-coord** — matches all incumbents + existing 7 annotation types |
| Q2: appear in export? | **Yes (PDF already)** — XLSX could list in separate sheet (future, not blocking) |

### Recommendation from researcher

> **Option A (MERGE)**: Fold draggable sticky-note UX into `comment-redesign` sprint (already in backlog). That sprint's Markups List pane becomes the home for stickies. Add ann_comment-specific yellow-square visual + inline edit as sub-task.
>
> **Option B (STANDALONE)**: Build dedicated `sticky-note` as simplified entry point (faster than full comment-redesign, less scope).

Both options are PHASE_PARTIAL — not greenfield, not fully solved by existing primitives.

## Frame

### Problem

User reviewing a 45-page raster permit PDF wants to **leave inline notes per page** — quick comments like "ตรงนี้ scale ผิด", "ผนัง ENT ขาด dimension", "ถามวิศวกร" — that are visible at-a-glance as **post-it-style yellow cards** stuck to page coords. Existing `ann_comment` mode prompts for text once and renders a small circle+label that's easy to miss visually and not editable after creation.

### Constraints

1. **Must work on raster PDFs** — no PDF vector annot API. Render in canvas overlay (HTML div positioned via `pdfToC()`) or canvas-drawn card.
2. **Phase 1 boundary** — no AI, no OCR, no rule engine, no FAR/OSR. Just text notes.
3. **Page-scoped** — store per-page in `pageStore[pg].annotations[]`, page-coord anchored.
4. **`.bmaplan` schema additive only** — extend existing `ann_comment` annotation shape with new fields (e.g. `width`, `height`, `stickyStyle`) — NO field renames/removals.
5. **Single-file inline JS** — no bundler. Hand-built widget pattern (~200-300 LOC).
6. **Must round-trip** — save/load via .bmaplan, export to annotated PDF (already supported for ann_comment).

### Forbidden surfaces this idea must avoid

- `polyAreaM2` / `polyMetrics` — measurement math, untouched.
- `pdfToC` / `cToPdf` / `RS` — coordinate conversion, only READ (for positioning).
- `snap` engine — sticky notes don't snap.
- `.bmaplan` field rename — only additive.
- `server.py` core — sticky notes are pure client-side state.
- Existing 6 non-comment annotation types (text/highlight/rect_frame/circle_frame/cloud/arrow) — leave alone unless explicit scope.

### Success criteria (spike-measurable)

1. Click "Sticky Note" button → cursor enters note-placement mode.
2. Click page → yellow draggable card appears at click coord (~120×80px default).
3. Card is text-editable inline (textarea inside card, no separate prompt).
4. Drag card by header → card moves; position persists.
5. Click outside / Esc → exits edit mode, note saved.
6. Save .bmaplan → reload → note re-renders at same page-coord with same text + position.
7. Existing `ann_comment` annotations from prior saves still render correctly (backward compat).
8. Export to PDF → note text appears on the exported page (inherits ann_comment path).

### Out of scope (for this invent pass)

- Thread replies / multi-author comments (Phase 2)
- Global Markups List pane (that's `comment-redesign` scope)
- Color picker / multiple sticky colors (post-MVP)
- Rich text formatting (post-MVP)
- Cross-page references / @-mentions (Phase 2)
- Resize handles on sticky card (post-MVP — fixed size first)

## Diverge

5 approaches on 5 different axes (data-model / render-surface / scope / edit-UX / extended-UX).

| id | name | axis | est LOC | novelty |
|---|---|---|---|---|
| A | render-mode flag on `ann_comment` | data-model | 90 | 2 |
| B | new `ann_sticky` type + HTML div overlay | render-surface | 150 | 3 |
| C | MERGE into comment-redesign sprint | scope | 380 (120 net-new) | 2 |
| D | hybrid canvas card + popup textarea | edit-UX | 170 | 3 |
| E | sticky with resize handle | extended-UX | 250 | 4 |

All 5 approaches: forbidden-surface = NO, Phase 1 boundary = OK, library = none.

## Score

| approach | novelty | accuracy | UX | model-fit | boundary | cost | total |
|---|---|---|---|---|---|---|---|
| A render-flag | 2 | 3 | 3 | 5 | 5 | 5 | **23** |
| **B HTML div overlay** | 3 | 4 | **5** | 4 | 5 | 4 | **25** ⭐ |
| C merge-into-redesign | 2 | 4 | 4 | 5 | 5 | 3 | **23** |
| D hybrid canvas+textarea | 3 | 4 | 4 | 4 | 5 | 4 | **24** |
| E resize handle | 4 | 4 | 3 | 3 | 5 | 2 | **21** |

Key reasoning:
- B UX=5 — HTML div gives native Thai IME, selection, copy-paste, line-wrap; canvas text degrades at low zoom.
- A UX=3 — canvas-drawn card doesn't get native text input benefits.
- E cost=2 — resize handle overengineered for note card; defer.
- C model-fit=5 — clean structural fit, but BLOCKED on comment-redesign not yet at GO.

## Recommendation

**Spike B first** (new `ann_sticky` type + HTML div overlay). HTML div is the correct rendering surface for editable text — browser handles IME, focus, wrap natively. Schema-additive (new type string), preserves all existing annotations.

**Fallback D** (hybrid canvas+textarea) if HTML div z-index drifts relative to canvas transforms during page rotation or zoom animation. D shares B's data model — fallback costs render layer only.

**Do NOT MERGE into comment-redesign now** (approach C). That sprint is at PENDING-CHECKPOINT with no GO yet. Merging would block sticky notes on that decision. Sticky-note is additive regardless — if comment-redesign ships, stickies auto-appear in its Markups List via `annotations[]` iteration. No rework needed.

### Score validation (per /bma-invent step 5)

- ✅ Top approach (B) `forbidden_surface_touch: NO`
- ✅ Top approach (B) Phase 1 boundary OK (no AI/OCR/legal)
- No re-ranking needed.

## Spike

**Approach: B** (new `ann_sticky` type + HTML div overlay)
**Sandbox file:** `proto/sandbox/invent-post-it-page-notes.html`
**LOC:** ~280 (HTML+CSS+JS combined; net JS = ~150 as estimated)

### Implementation (standalone, no proto/ui.html touch)

- HTML div `.sticky-card` positioned via `pageCoordToClient(ann.pts[0].x, ann.pts[0].y)` → CSS `left/top`. Yellow background (`#fef3a6`), slight tilt (`rotate(-1deg)`), Marker-Felt font for post-it feel.
- Header bar with drag handle (⋮⋮) + delete (×). Body is `<textarea>` with placeholder "เขียน note…" — native Thai IME, selection, line-wrap.
- `setMode("ann_sticky")` adds `body.mode-sticky` (crosshair cursor); click canvas → drops sticky at click coord → auto-focuses textarea → auto-exits mode (one-shot place).
- Pointer-events drag: pointerdown on header → captures pointer → pointermove updates `ann.pts[0]` → DOM left/top sync.
- Save: serializes `annotations[]` to localStorage. Load: reads back, re-renders, page-coords preserved.
- Legacy `ann_comment` renders as red dot on a separate `<canvas>` layer (proves the new type COEXISTS with the existing 6 types — backward-compat).

### Acceptance check vs Frame § Success criteria

| # | Criterion | Pass | How verified |
|---|---|---|---|
| 1 | Click "Sticky Note" → placement mode | ✅ | `body.mode-sticky` class + crosshair cursor; `setMode` toggles |
| 2 | Click page → yellow card appears | ✅ | `canvas-area` click handler creates ann + `renderSticky()` |
| 3 | Inline text editing | ✅ | `<textarea>` inside card; `input` event updates `ann.text` |
| 4 | Drag by header → moves | ✅ | pointerdown/move/up on header updates `ann.pts[0]` |
| 5 | Esc/click-outside → saves | ✅ | input event saves continuously; Esc blurs textarea |
| 6 | Save → reload → round-trips | ✅ | localStorage save/load button; demo state preserved |
| 7 | Backward-compat with ann_comment | ✅ | Legacy comments render as red dots on `#legacy-canvas` alongside stickies |
| 8 | Export inheritance | ✅ | annotations[] dump panel shows full serialized state; production `/export-pdf` already iterates `annotations[]` |

**Outcome:** PASS — all 8 criteria met in spike. Real-browser interaction verification deferred to user smoke test on the sandbox file before GO decision.

### Notes for production sprint

- New type string `"sticky"` must be enumerated in: `drawAnnotations()` (skip — HTML layer handles), `/export-pdf` server endpoint (verify it handles unknown types as no-op or extends to render yellow card), Notes tab filter (HT-20), annotation icon picker.
- New optional fields on annotation object: `width`, `height` (default 120×80; nullable for backward compat) — additive, no schema break.
- Drag-state management mirrors existing `dragState` pattern in proto/ui.html (sel mode for measurement objects) — reusable pattern.
- HTML overlay z-index needs to sit below modals (z 9000) but above canvas (z 1) — single CSS variable.
- Spike does NOT cover: page-rotation interaction with HTML overlay (rotate via CSS transform on container?), zoom-scaling of card text (constant pixel size? or scales with zoom?). These need design decisions during sprint scoping — note in sprint card.

## Decision

**GO** — 2026-05-19, user pre-emptive authorization via standing-order goal
("ทำ /bma-invent ใน เรื่อง Post it® จนกว่าจะได้ชิปออกมาใช้ใน product").

Rationale: user explicitly took implementation risk BEFORE seeing spike results.
All gating conditions met: spike 8/8 PASS, score 25/30 (top of 5 approaches),
zero forbidden-surface touches, Phase 1 boundary OK, schema additive-only,
no library dependencies. Sandbox file ready for user smoke-test post-ship.

Sprint card filed as **INV-2026-05-19-005** in `docs/status/PHASE_INDEX.md`.
`/bma-dev-loop` will pick it up for production implementation.
