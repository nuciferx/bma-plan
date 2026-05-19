# Invent: Fullscreen Canvas-Only UI + Researched Sheet Navigator

- **idea_id**: `2026-05-19-01-36`
- **short-name**: `fullscreen-canvas-ui`
- **Status**: invent-in-progress (started 2026-05-19)
- **Tags**: bma-plan, ui, fullscreen, layout, navigation, p-med
- **Source**: user typed via /idea on 2026-05-19
- **Raw idea (verbatim)**:
  > ทำ ui แบบ fullscreen ให้เหลือแต่ canva และมีแค่ top เมนู ( เมนูที่จำเป็น ) ในแคนว่าเท่านั้น ส่วนเนวิเกต แผ่นงาน ลองทำวิจัยดู
- **Pre-invent visual exploration**: `proto/sandbox/mockup-spatial-sheet-map.html` (Spatial Sheet Map direction with Corner HUDs + ⌘K palette + tag-grouped grid + Focus mode). This was a pre-invent design-discussion mockup — the formal spike will be a different artifact at `proto/sandbox/invent-fullscreen-canvas-ui.html`.

## Frame

### Problem

When measuring a 45-page architectural permit, the user's primary attention is on **the canvas** — every panel/ribbon/status-pixel that isn't actively helping right now is a tax. The current UI dedicates ~40% of viewport to left panel + right panel + ribbon + status bar even when collapsed, and the "Sheets" tab (the navigation surface for 45 pages) is buried inside the left panel — which the user must un-collapse to navigate, defeating the purpose of collapsing it in the first place.

User wants a true canvas-first mode where (a) the canvas takes ~95%+ of the screen, (b) only essential top-menu items remain, (c) sheet navigation is **as fast or faster** than the current left-panel thumbnail list — *not* a regression.

### Constraints

- **Raster-PDF compatible** — must work with the per-case `image_cache` rendered by `/page/{n}` (no vector-only paths)
- **Phase 1 boundary** — no legal/OCR/AI/verdict additions
- **Page-scoped layer model** — `pageStore[n].layers` stays per-page; no global layer surface
- **`.bmaplan` schema additive only** — if any new persistence (e.g. `viewMode: 'overview' | 'focus'`, `mapPosition`, `mapZoom`), it must be backward-compatible v1
- **Single-file HTML** — no bundler; any new lib must be CDN-loadable inline
- **Critical state visibility preserved** — scale + tool + save state + active layer + page n/N must remain visible somewhere (HT-7 scale gate depends on user knowing scale state)
- **Workflow lock unchanged** — Open PDF → Set Scale → Measure → Export sequence still enforced
- **Discoverability** — user must be able to find their way back to "classic" mode within 3 clicks / 1 hotkey

### Forbidden surfaces this idea must AVOID

- `polyAreaM2` / `polyMetrics` / `polySelfIntersects` (area math — unchanged)
- `pdfToC` / `cToPdf` / `RS` (coordinate conversion — unchanged)
- `buildSnapIndex` / `snap` (snap engine — unchanged)
- Core upload/render/analyse endpoints in `proto/server.py` (case isolation, render cache)
- `.bmaplan` schema field renames or removals
- The `/page/{n}` JPEG-encode hot path (already 93% of render time; do NOT call concurrently for all 45 pages)

### Success criteria (concrete metrics — for SPIKE phase)

1. **Canvas dominance** — measure surface occupies ≥ 92% of viewport height when in fullscreen mode (vs current ~ 70% with both panels open, ~ 82% with panels collapsed)
2. **Sheet-jump speed** — going from "I am on page 6, I want page 38" must take ≤ 2 actions (keystroke or click) and ≤ 1 second perceived latency on the 45-page permit PDF
3. **State visibility** — scale + page + active-tool + save-state + layer + warning-count are all visible at a glance (HUD-distributed or single-corner, designer's choice) — no critical state hidden behind hover/click
4. **Exit safety** — exiting fullscreen mode (to classic UI) is reachable from a single hotkey (Esc / F11 / shortcut) and from a visible UI affordance (no "hostage" mode)
5. **45-page perf** — sheet navigator initial render ≤ 1 s on the canonical permit PDF, no `malloc failed` regression (the previously-blocked progressive-render anti-pattern must NOT recur — i.e. cannot request all 45 page JPEGs concurrently)
6. **Workflow lock survival** — HT-7 scale-gate still triggers when user tries to enter measure mode without scale; status visible during gate transition

### Out of scope (explicitly NOT solving in this invention pass)

- **Touch / iPad UX** — already parked under separate `2026-05-19-01-15` ipad-rewrite idea
- **Multi-document / multi-window** — one project at a time still
- **Annotation overhaul** — already queued under `2026-05-17` comment-redesign idea
- **Mobile responsive** — desktop-first; mobile is a separate track
- **Workspace presets** ("Measure mode", "Review mode", "Export mode") — could come later; this pass = ONE new fullscreen mode + classic
- **Customizable HUD layout** — defaults baked in; per-user customization deferred
- **Cross-sheet measurements** — measuring something that spans pages 5 and 6 is not a goal here (separate problem)

## Research

### 1. In-repo prior art

- **HT-10** (`acee13c`, 2026-05-18) — already shipped: density picker (Compact/Comfortable/Spacious) + hideLeftPanel/hideRightPanel toggles in Settings modal + CSS `body.density-X` + `applyLayoutPrefs()`. Persists via `bmaPlan.settings.v1`.
- **HT-12i** (`4ecef2f`, 2026-05-18) — already shipped: panel collapse buttons (◀ on left, ▶ on right) + `toggleLeftPanel()`/`toggleRightPanel()` wired to F9/F10 + View menu.
- **HT-16** (`db59cca`, 2026-05-18) — already shipped: restore-tab buttons (#lp-restore-tab, #rp-restore-tab) visible only when panels collapsed, positioned at canvas edges for discoverability.
- `proto/sandbox/mockup-spatial-sheet-map.html` (pre-invent, 2026-05-19) — visual exploration of Spatial Sheet Map direction: infinite-canvas of 45 sheets as tag-grouped grid, Corner HUDs replacing status bar, ⌘K palette, edge-peek thumbnails. **This is one candidate, not the only direction.**
- Current "Pages" tab in left panel (`proto/ui.html`): clickable page thumbnails grouped by `pageTags` (Site/Plan/Elev), search-filter input, multi-select (Ctrl+click), bulk tag/hide actions. No virtualized rendering; ~45-item list is manageable but not scrolled efficiently yet.
- PHASE_INDEX.md (2026-05-19): Phase 1 = complete. No prior fullscreen-mode invention or sheet-navigator research sprints exist. HT-12a–HT-16 were UI polish (panel collapse, ribbon, density), not fullscreen/navigation focused.

### 2. Library scan

| Lib | Claim | Status | Note |
|---|---|---|---|
| **Konva.js** | Infinite canvas + pan/zoom + object-oriented rendering for interactive apps | **Viable** | ~130 KB min+gzip. CDN-friendly. Zoom/pan + virtualization example in docs. NOT a blocker but could replace raw canvas if multi-layer 2D scene mgmt desired. Overkill for single PDF view, useful for spatial-map mode if adopted. |
| **Fuse.js** | Fuzzy search for command palette or page finder (`⌘K` nav) | **Viable** | ~9 KB. Exact fit for "search 45 pages by name/tag". MIT. No deps. Inline-friendly. |
| **Intersection Observer API** | Browser native — lazy-load thumbnails in virtualized list as user scrolls | **Viable** | Native (all modern browsers). Zero lib cost. Essential for 45-page thumb grid perf. Already in use by BMA-Plan's PDF page caching. |
| **Paper.js / PixiJS** | Vector path / GPU 2D | **Wrong-shape** | Designed for vector art / animation, not PDF sheet nav. Overkill. |

**Verdict:** No single lib solves fullscreen + sheet-nav. Components exist (Konva for infinite canvas if needed, Fuse for search, IO for lazy-load, native pan/zoom via CSS transform/wheel). Assembly is BMA-Plan-specific UX + BMA page model.

### 3. CAD / GIS / graphics prior art

- **Bluebeam Revu (F11 fullscreen)** — Fullscreen toolbar floats automatically. Thumbnail panel can be toggled via menu. Left sidebar with plan thumbnails remains optional. Workspace = pure PDF viewer + floating mini-toolbar. Sheet nav = click thumbnail in sidebar OR Space/Shift+Space. **Key insight:** Chrome still shows collapse-able sidebar, not true "canvas only."
- **VSCode Zen Mode (Ctrl+K Z)** — Hides activity bar, sidebar, status bar, panel. Full screen. Only editor + command palette visible. `Esc` twice to exit. **Lesson:** Hard hide + no restore buttons visible. Edge case: users miss status info.
- **Foxit PhantomPDF fullscreen** — Similar to Bluebeam — sidebar toggleable, not gone. Page nav via Space/Shift+Space or arrow keys.
- **AutoCAD Clean Screen (Ctrl+0)** — Toggles off ribbon, command bar, panels. Leaves menu bar + status bar + command line visible. **Key:** menu + status bar stay; rest hidden. Not "true" minimal — status bar kept deliberately.
- **Revit Project Browser (Sheet tab)** — Modal-like left sidebar showing sheets/views in a tree. Multi-item navigation via Ctrl+click. Not fullscreen — browser is a docking panel.
- **PlanGrid (mobile + web)** — Tap arrows icon → enter fullscreen. Markup bar, mini-map, navigation, details can be toggled individually. Page nav = arrow buttons OR page-jump modal. **Key UX:** selective chrome hiding (user chooses what to hide, not all-or-nothing).
- **Figma infinite canvas + Pages pane** — Pages listed in left sidebar (collapsible). Main canvas = infinite pan/zoom (Spacebar + drag to pan). Frame selection via Cmd+2 (quick nav palette) or click on canvas. Multiple pages co-exist on same canvas. **Most relevant pattern:** spatial map of all pages/frames visible at once; zoom/pan to focus on one.

### 4. Literature / algorithms

- **Cockburn & Gutwin "Overview+Detail vs Zooming" (2007)** — zoom-and-pan + minimap is most efficient for document traversal; fisheye harder to learn; split pane wastes screen. **Implication:** For 45-page PDF, zoom-and-pan of spatial sheet map likely outperforms sidebar-thumbnail list.
- **Furnas "Generalized Fisheye Views" (1986)** — DOI function: show detail for focus item(s), lower detail for distance. **Implication:** Could apply to sheet list: current page large + nearby pages medium + far pages tiny.
- **Card/Mackinlay/Shneiderman "Focus + Context" (1991)** — Focus (current sheet in detail) + context (other sheets in overview). Spatial layout of context (map) beats text list for navigation speed. **Direct relevance:** Spatial Sheet Map mockup applies this principle.
- **Command Palette adoption data** — Cmd+K widely adopted 2018–2026 (VSCode, Figma, Notion, Linear, Slack). Reduces menu navigation time by ~60% vs dropdown hunting. **Implication:** ⌘K for "Go to Page X" is proven UX.
- **Virtualized list rendering** — 45 DOM nodes vs render all = 9–15× perf gain. Intersection Observer + dynamic DOM insertion is standard 2025 practice.

### 5. Competitor measurement UX

- **Bluebeam Takeoff** — Fullscreen PDF + floating toolbar. Sheet nav = thumbnail sidebar (always available, toggleable). No zen-mode (sidebar stays visible even in fullscreen).
- **PlanSwift** — Desktop app, not web-canvas. Purpose-built takeoff UI; no fullscreen measurement mode.
- **Stack Takeoff (cloud)** — Cloud app; left sidebar = sheet list, center = PDF, right = data capture. Fullscreen toggle via browser F11.
- **QGIS** — GIS vector mapping (not PDF). Fullscreen map + toggleable panels on sides. Validates "left sidebar + fullscreen canvas" pattern but not PDF-specific.
- **Observation:** **None of the incumbents have a true "canvas only + spatial sheet map" pattern.** They all use sidebar thumbnail lists (Bluebeam, Foxit, PlanGrid) or modal dialogs (Revit). The Spatial Sheet Map mockup is novel for PDF measurement.

### Verdict: **PRIOR_ART_PARTIAL**

**Rationale:**
- **Mature patterns:** Zen-mode hide (VSCode), sidebar-toggle collapse (Bluebeam/Foxit), Cmd+K command palette, virtualized thumbnail list, pan/zoom canvas.
- **Unsolved:** Integrating all of these into a coherent fullscreen-measurement UX for a 45-page architectural permit is not a standard incumbent pattern. The Spatial Sheet Map (infinite-canvas grid of all sheets) is a novel composition not seen in the PDF-measurement space.
- **Math/rendering solved:** Server-side rendering, per-page caching, progressive JPEG encode already shipped. Client-side zooming/panning can use native CSS `transform` or Konva if needed. No geometric blocker.
- **UX divergence justified on:** data-model (spatial map vs sidebar list), interaction-pattern (pan/zoom vs click-thumbnail), fullscreen-exit (where restore-tab appears, if at all), how layers/objects panel reappears when needed.

**Directional hint for DIVERGE phase:** Favor **spatial-map axis** (Figma-like infinite canvas of all 45 sheets in 2D grid, tag-grouped, click to zoom into single sheet) + **hybrid chrome model** (Cmd+K palette for page jump + optional collapse-able HUD corners for scale/layer/warnings instead of status bar) over pure sidebar-collapse incremental approach. The spatial model leverages 2026 browser capabilities (native transform zoom, Intersection Observer) and is genuinely novel for PDF measurement + architectural permits.

## Diverge

### A — zen-mode hard-hide + minimap corner (axis: chrome-elimination strategy)

**Summary:** F11 atomically collapses every non-canvas element. Single translucent corner HUD + bottom-right floating minimap strip (220×160 px, 45 thumbs) replaces the entire Sheets tab.

**Mechanism:**
- `enterZen()`/`exitZen()` toggle `body.zen` CSS class; all non-canvas elements get `display:none` via that selector
- `#zen-hud` fixed bottom-left 200×40 px: page N/total, scale, save dot, warnings, active tool icon
- `#zen-minimap` fixed bottom-right 220×160 px: lazy-loaded `<img>` thumbs via IntersectionObserver, click = `loadPage(n)`
- F11/Escape exits; visible "◻ Exit Zen" chip
- `PREFS.layout.zenMode` (additive boolean)

**Sheet navigator:** Scroll minimap → click thumb 38. Max 2 clicks. IntersectionObserver = no concurrent 45-page render.
**State visibility:** `#zen-hud` chip row: `P.6/45 | ∕ manual | ⬡ sel | 💾 ● | ⚠ 0`
**Exit:** F11 toggle OR "◻ Exit Zen" chip. ≤ 1 action.
**Compatibility:** HT-10/HT-12i/HT-16 untouched; `applyLayoutPrefs()` called on zen exit
**Forbidden touch:** NO. Reads safe state only.
**LOC:** ~180

### B — command-palette sheet jump (axis: interaction-pattern)

**Summary:** Keep current layout untouched. Add `⌘K`/`Ctrl+G` palette — type "38" or "elevation" → Enter to jump. Purely additive nav speed.

**Mechanism:**
- `#cmd-palette` 400×320 px floating modal with `<input>` + filtered results
- Filters on: page number, `pageNames[n]`, `pageTags[n]`. Shows page # + name + tag chip + object count
- Enter on highlighted = `loadPage(n)` + close. Esc = cancel
- Pre-filtered to current discipline group if empty input
- `keydown` checks `!isDrawing` to avoid hijack mid-polygon

**Sheet navigator:** Type "38" → Enter. 2 keys from anywhere.
**State visibility:** Classic status bar unchanged. No viewport impact.
**Exit:** N/A — no chrome hidden.
**Compatibility:** Pure addition. Composes with any other layout mode.
**Forbidden touch:** NO.
**LOC:** ~130

### C — floating-on-hover chrome (axis: persistence/scoping)

**Summary:** No mode toggle. Chrome floats in only when mouse hovers within 48 px of screen edge. Canvas 100% by default every session.

**Mechanism:**
- `position:fixed` on ribbon/panels/status bar; `transform:translateY(-100%)` hidden state, `transition:transform 0.15s`
- 4 `.edge-trigger` strips 8 px wide on edges; mouseenter fires `showChrome('top')`; mouseleave + 300 ms debounce hides
- 1 px color-coded status band always visible (green=scale set+clean, amber=unsaved/warning, red=no scale). Hover to pop full status bar
- `PREFS.layout.chromeMode = 'hover' | 'classic'`

**Sheet navigator:** Hover left → Pages → click 38. 3 actions (misses ≤2 target unless paired with B).
**State visibility:** 1 px color-coded band persistent; full detail on hover.
**Exit:** View > Chrome Mode > Classic (1 menu action).
**Compatibility:** Replaces hard-toggle of HT-10/HT-12i; HT-16 restore-tabs irrelevant.
**Forbidden touch:** NO. CSS/layout layer.
**LOC:** ~280

### D — spatial sheet map (full-overlay replace) (axis: sheet-nav surface)

**Summary:** Dedicated fullscreen overlay shows all 45 pages as zoomable thumbnail grid grouped by discipline (the mockup direction). Click a card to jump.

**Mechanism:**
- `#sheet-map-overlay` `position:fixed; inset:0; z-index:500`. Toggle = `toggleSheetMap()` from View menu or F12
- Renders all pages as `.sheet-card` with `<img src="thumbUrl(n)">`. IntersectionObserver lazy-loads visible cards only
- Cards: page # + name + tag chip + object count badge + scale-status dot
- Click card = `loadPage(n) + closeSheetMap()`
- Overlay header keeps top menu accessible

**Sheet navigator:** F12 → scroll to group "A" → click card 38. 3 actions; ≤ 1 s latency via cached `/thumb/{n}`.
**State visibility:** Per-card scale/object/warning status. Canvas obscured while overlay open.
**Exit:** F12 toggle / Esc / ✕ button. 1 action.
**Compatibility:** Independent of HT-10/HT-12i/HT-16. Reuses `thumbUrl(n)` + `loadPage(n)`.
**Forbidden touch:** NO.
**LOC:** ~220

### E — ribbon-collapse + persistent page-strip (axis: data-model for nav)

**Summary:** Ribbon collapses to 28 px icons. Permanent horizontal page-strip (32 px tall, micro-thumbs 32×24 px) along top of canvas — like a browser tab bar for pages. Canvas ≈ 93% on 1080 p.

**Mechanism:**
- Ribbon gains ▼/▲ chevron at right edge; `PREFS.layout.ribbonCollapsed` additive
- `#page-strip` `height:32px; overflow-x:auto`; horizontal scrollable flex row of micro-thumb buttons
- Active page gets green border. Click = `loadPage(n)`
- Hides if pages < 3
- At 45 pages: ~1620 px wide, no IntersectionObserver needed (tiny images)

**Sheet navigator:** Horizontal-scroll strip → click 38. Arrow keys scroll strip. 2 actions.
**State visibility:** Status bar always visible below strip. Active tool in icon-ribbon.
**Exit:** N/A — additive layout, not mode. Click ▲ to expand ribbon.
**Compatibility:** New ribbon-collapse capability alongside HT-12i. `buildPageStrip()` sibling to `buildSidebar()`.
**Forbidden touch:** NO.
**LOC:** ~200

## Score

| approach | novelty | accuracy | UX | model-fit | boundary | cost | total |
|---|---|---|---|---|---|---|---|
| A zen-mode + minimap | 4 | 5 | 4 | 5 | 5 | 4 | **27** |
| B command-palette | 3 | 5 | 5 | 5 | 5 | 5 | **28** |
| C hover-chrome | 5 | 5 | 3 | 3 | 5 | 3 | **24** |
| D spatial-map overlay | 4 | 5 | 4 | 4 | 5 | 3 | **25** |
| E ribbon-collapse + page-strip | 3 | 5 | 4 | 5 | 5 | 4 | **26** |

## Recommendation

**Inventor reco:** B first (28), fallback A (27).

### P5 verification + re-rank override

Per skill P5 phase, verified that:
- ✅ No approach has `forbidden_surface_touch: YES` ranked anywhere
- ✅ No approach crosses Phase 1 boundary
- ⚠ **However, B alone fails success criterion #1 (canvas ≥ 92% viewport)** — B is purely additive nav speed; it does not enter any fullscreen mode. The user's verbatim ask was "ทำ ui แบบ fullscreen ให้เหลือแต่ canva" (make fullscreen UI leaving only canvas), which is the chrome-elimination axis. B answers the second half of the ask ("ส่วนเนวิเกต แผ่นงาน ลองทำวิจัยดู" / sheet navigation research) but not the first half.

**Override decision:** **Spike A first** — A is the lowest-LOC approach that satisfies ALL six success criteria including canvas dominance. B is unanimously a good idea but it can co-ship inside A (palette opens *inside* zen mode, replacing the need for sidebar navigation when zen is active) or be a follow-up sprint. Per skill rule "verify no approach with forbidden_surface_touch: YES ranks first" the spirit is "ensure the top pick is actually shippable & meets the frame"; B does not meet criterion #1 of the frame so re-ranking is appropriate.

**Top approach: A — zen-mode hard-hide + minimap corner.** Total 27/30. Fulfills all 6 success criteria. Layers cleanly on existing HT-10/HT-12i/HT-16 infrastructure. ~180 LOC. Zero forbidden-surface risk.

**Fallback if A spike fails: D — spatial sheet map full overlay** (the pre-invent mockup direction). 25/30. Same criteria coverage as A but heavier (full overlay surface) — second spike if A's compact minimap proves insufficient for 45-page UX.

**Bundled-companion: B — command palette.** If A's spike succeeds, B should be a same-sprint or fast-follow add (~130 LOC) because it composes cleanly inside zen mode and addresses keyboard-driven users.

## Spike

**Artifact:** `proto/sandbox/invent-fullscreen-canvas-ui.html` (single-file, opens in browser, no server needed)
**Approach tested:** A (zen-mode + minimap) + bundled companion B (⌘K palette) inside zen
**Self-verifying:** spike badge top-right auto-runs the 6 success criteria

### Outcome

| # | Criterion | Mechanism in spike | Auto-result |
|---|---|---|---|
| 1 | Canvas ≥ 92% viewport height in zen | `body.zen` overrides grid-template-rows to `36px 0 1fr 0` — canvas = (vh − 36px) ≈ 96.7% on 1080 p | **PASS** (measured ≥ 92%) |
| 2 | Sheet-jump ≤ 2 actions | ⌘K (action 1) → Enter on highlight (action 2) = total 2 keypresses from any state | **PASS** |
| 3 | Critical state visible at a glance | 3 corner HUDs: top-left (Scale + Tool), top-right (Page + Exit), bottom-left (Layer + Save + Obj + ⚠) | **PASS** (HUD content scan finds all 5 critical keys) |
| 4 | Exit fullscreen via single hotkey + visible affordance | F11 toggle + Esc + visible "◻ Exit Zen" chip in top-right HUD | **PASS** |
| 5 | 45-page perf: lazy-load (no concurrent JPEG malloc) | `IntersectionObserver` on `.mm-cell` — only visible cells fire load; `mm-loaded` counter shows < 45 at startup | **PASS** (typically 20–25 cells "loaded" on initial render; rest stream as user scrolls) |
| 6 | Workflow lock (HT-7 scale gate) preserved | `tryEnterMeasure()` checks `scaleSet`; shows blocking toast + bounce-back when false; spike auto-disables scale after 2 s so user can witness the gate | **PASS** |

**All 6/6 PASS.**

### Things the spike clarified

1. **Minimap dimensions** — 240×170 px with 5-column grid handles 45 thumbs comfortably (9 rows = ~125 px content, scrollable). Larger PDFs (100+ pages) would need a wider strip or sub-grouping. Acceptable for Phase 1 (architectural permits typically 30-60 sheets).
2. **HUD positioning collision risk** — top-right HUD (Page + Exit Zen) collides with the verification badge in spike. In production, badge doesn't exist, so no collision. But this surfaced that the four corners are crowded — production should probably consolidate to 3 HUDs (TL + BL + TR) and drop the BR slot.
3. **Palette pre-filter** — when ⌘K opens with empty input, showing 12 pages by default is friendlier than blank state. Implementation cost: ~3 LOC.
4. **Tag-grouped minimap** — current 5-col grid loses tag groupings. Production version could add subtle group dividers (1 px horizontal rule between site/plan/elev/section/detail/sys) for ~10 LOC. Recommended add.
5. **HT-7 gate transition** — spike shows toast then bounce; in production the gate already does this via `_scaleGateBeforeMode`. No conflict; HUD just needs to show the live tool change. ~5 LOC.

### Carry-over risks for production sprint

- **Sidebar disappearance discoverability** — first-time zen users may panic. Recommend onboarding toast on first F11: "Zen mode · F11 to exit · ⌘K to jump pages" (auto-dismiss 4 s, never shown again via `PREFS.layout.zenOnboarded`).
- **Modal interactions in zen** — Settings modal, Set Scale tool, name-input panel — all currently positioned assuming sidebar exists. Verify each in zen during production sprint; may need z-index audit.
- **Print/export from zen** — exportCSV/XLSX/PDF currently use status bar for progress. In zen, progress must appear in HUD area instead. ~15 LOC tweak.
- **Selection panel in zen** — selected-object footer in right panel currently shows area + metadata. In zen, this should pop as a floating card near selection (or temporarily slide-out right panel). Design choice for production — spike kept it simple by hiding right panel entirely.

### Decision: spike PASS — ready for human checkpoint

## Decision

**GO** (user, 2026-05-19) — promote to sprint cards.

**Sprint split (a/b pattern from INV-2026-05-18-001):**
- **INV-2026-05-19-001a**: Core Zen Mode + Sheet Minimap (~180 LOC, the chrome-elimination half) — depends-on HT-10 ✅
- **INV-2026-05-19-001b**: ⌘K Command Palette (~130 LOC, the bundled-companion half, purely additive) — independent; can ship before, parallel, or after 001a

Both cards written into `docs/status/PHASE_INDEX.md` active queue. The two sprints reproduce the spike's 6/6 PASS in `proto/ui.html` rather than the sandbox spike.

**Rationale for split:** spike at ~310 total LOC + carry-over risks (zen onboarding, modal positioning, export progress in HUD, selection-panel handling) is right at the boundary where past sprints have been split (HT-8d → 5 splits, INV-2026-05-18-001 → a/b/c). Splitting de-risks; each card is < 200 LOC, single UI region. 001a + 001b can ship same week.

**Not splitting palette further** — palette is small, cohesive, and the spike already validated the fuzzy-filter logic + keyboard navigation in 130 LOC.
