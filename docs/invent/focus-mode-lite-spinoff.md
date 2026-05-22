# Invent: Focus-Mode Lite-Version Spinoff (single-row menu bar)

- **idea_id**: `2026-05-20-00-12`
- **short-name**: `focus-mode-lite-spinoff`
- **Status**: invent-in-progress (started 2026-05-20)
- **Tags**: bma-plan, ui, focus-mode, fullscreen, lite-version, research-needed, p-med
- **Source**: user typed via /idea on 2026-05-20
- **Raw idea (verbatim)**:
  > แตกประเด็น ชอบ ui แบบ f11 และ Focus mode  ถ้าจะแตก ออกจากโปรแกรมหลัก มาทำ ver lite โดย มีเมนูบาร์แค่แถวเดียว จะสามารถทำได้ไหม และส่ง agent ไปทำวิจับเกี่ยววับโปรแกรมวัดพื้นที่แบบก่อสร้างว่ามีอะไรบ้างแล้วมีการทำงานกับแบบขนาดใหญ่นี้ยังไง พร้อมทำ รายงานเป็นไอเดีย card
- **Adjacent prior invents** (do NOT re-do their work):
  - `docs/invent/fullscreen-canvas-ui.md` (2026-05-19) — focus-mode IN-PLACE inside the main app. This new idea explicitly asks the DIFFERENT question: "what if it's a separate build/spinoff?"
  - `docs/invent/zen-mode-v2-topbar.md` — top-bar variant of focus mode

## Frame (v2 — after RESHAPE 2026-05-20)

### Problem

User loves F11 / Focus mode in shipped BMA-Plan but wants the cleanest possible measurement face: a SINGLE ROW of top menu, nothing else above the canvas, full measurement parity with the main app, and true fullscreen PDF viewing (OS-level, not just panel-collapse). This is a tightening of v1 Frame — the user explicitly rejected variants that add a welcome screen, context-adaptive menus, or per-project persistence. The mode must be **structurally the simplest** version possible: hide all chrome except one row of menu, expose every measurement tool the full app has, and let the user toggle into OS fullscreen so the PDF fills the actual monitor.

### Constraints (HARDENED in v2)

- **Single-row hard lock** — ONE row of top menu. No second row. No tool ribbon below. No status bar below. Whatever it takes (collapse menus to icons + dropdown if needed, or fit all needed items into ≤3 dropdowns). Menu height ≤ 44 px non-negotiable.
- **Measurement parity hard lock** — every measurement capability of the full app must be reachable in lite. Polygon area, perimeter, circle, line, set scale, snap toggle, calibration, opening/deduction, semantic tag assignment. **No tool may be omitted.** If a tool doesn't fit in the 3-dropdown menu, it must be reachable via keyboard shortcut listed in a dropdown item.
- **True OS fullscreen** — `requestFullscreen()` browser API integration. F11 (or dedicated menu item) enters OS-level fullscreen where the canvas fills the entire monitor. Exit via Esc / F11 / menu item. Both lite mode AND full mode should support OS fullscreen, but lite mode is the natural default for the fullscreen workflow.
- All prior v1 constraints still hold: raster-PDF compat, Phase 1 boundary, page-scoped layer model, `.bmaplan` additive only, single-file HTML, workflow lock unchanged, lite↔full toggle in ≤1 hotkey, NO measurement-engine duplication.

### Forbidden surfaces this idea must AVOID

Unchanged from v1: `polyAreaM2`, `polyMetrics`, `polySelfIntersects`, `pdfToC`, `cToPdf`, `RS`, `buildSnapIndex`, `snap`, `.bmaplan` schema field renames, `/page/{n}` concurrent rendering, INV-005 sticky annotation logic. **No measurement-engine relocation either** — Approach B remains permanently excluded.

### Success criteria (concrete metrics — for SPIKE phase v2)

1. **Single-row enforcement** — top menu = exactly ONE row at any viewport ≥ 1024×600; menu height ≤ 44 px; absolutely no second toolbar/ribbon row
2. **Canvas dominance** — in lite (browser viewport): ≥ 95%; in lite + OS fullscreen: 100% minus menu row (~96–98% depending on display)
3. **Mode switch** — lite ↔ full toggle ≤ 200 ms perceived; OS-fullscreen enter/exit via F11 or menu item works in both modes
4. **Measurement parity** — every full-app measurement tool reachable in lite (verify by listing each tool + its lite-mode access path: dropdown item OR keyboard shortcut)
5. **Cross-mode save/load** — `.bmaplan` saved in lite/fullscreen round-trips in full and vice versa, byte-identical objects
6. **45-page sheet nav** — ⌘K palette + PgUp/PgDn + minimap (if fits — minimap from INV-001a is allowed; it's a corner HUD not a chrome row) handle 45 pages
7. **HT-7 scale-gate survival** — gate fires in lite the same way as full
8. **OS fullscreen API works** — `requestFullscreen()` succeeds in both modes; Esc exits cleanly; canvas re-fits without manual zoom

### Out of scope (v2)

- Welcome screen as entry point (rejected by user in RESHAPE — they don't want a gate before measuring)
- Per-project saved preference (rejected — user wants the same simple toggle, not project-bound state)
- Context-adaptive menus (rejected — user wants static measurement-app behavior, just compressed)
- All v1 out-of-scope items still hold (commercial gating, Electron, mobile, etc.)

---

## Frame (v1 — superseded by RESHAPE; kept for history)

### Problem

BMA-Plan's UI evolved to serve all workflows in one window: page setup, multi-tab inspection, layer admin, annotation review, export. For a user whose **today's job is "measure 45 pages and export an XLSX"**, that's ~60% of the DOM (left panel + right panel + ribbon + status bar + summary widget) sitting in the way before they even start. The shipped `fullscreen-canvas-ui` (INV-001a/b) gives them an in-place escape hatch (F11 → zen mode + minimap + ⌘K palette), but it's still a **mode inside the full app** — discovered via shortcut, exited the same way. Power users love it; new users never find it.

The user's question is structurally different from "make a better focus mode": **"can we ship a separate face of the product whose default IS the focus mode?"** A face with a single-row top menu, the canvas, and nothing else — so the measurement-only workflow is the obvious path, not a hidden mode. The research confirms this composition (measurement-only + single-row menu + raster-PDF + multi-sheet support) has no construction-tool incumbent — Foxit Reader is the closest precedent but it's read-only, and AutoCAD LT is feature-gated full CAD, not measurement-focused.

### Constraints

- **Raster-PDF compatible** — must reuse the per-case `image_cache` from `/page/{n}` (no vector-only path)
- **Phase 1 boundary** — no legal/OCR/AI/verdict additions
- **Page-scoped layer model** — `pageStore[n].layers` unchanged; lite UI must surface page-scoped layer correctly (or hide layer UI entirely if it's an "advanced" feature)
- **`.bmaplan` schema additive only** — projects saved in lite MUST load in full and vice versa, byte-for-byte compatible
- **Single-file HTML** — no bundler; any spinoff packaging must work without build step in dev
- **Critical state visibility preserved** — scale + tool + save state + active layer + page n/N must remain visible (HT-7 scale gate depends on user knowing scale state, even in lite)
- **Workflow lock unchanged** — Open PDF → Set Scale → Measure → Export sequence still enforced; HT-7 hard-gate must work in lite
- **Discoverability** — switching between lite ↔ full must be reachable in 1 hotkey AND 1 visible UI affordance (no "hostage" mode either direction)
- **No code duplication of measurement engine** — `polyAreaM2`, `pdfToC`, `cToPdf`, `snap`, `buildSnapIndex`, render path, save/load are SHARED between lite and full. The spinoff is a UI shell swap, not a re-implementation.
- **Single-row menu means single row** — ≤3 dropdowns + ≤15 total items + ≤1 row of tool buttons (or zero, with tools inside Measure dropdown). No wrap.

### Forbidden surfaces this idea must AVOID

- `polyAreaM2` / `polyMetrics` / `polySelfIntersects` (area math — shared, unchanged)
- `pdfToC` / `cToPdf` / `RS` (coordinate conversion — shared, unchanged)
- `buildSnapIndex` / `snap` (snap engine — shared, unchanged)
- Core upload/render/analyse endpoints in `proto/server.py` (case isolation, render cache — shared, lite uses same backend)
- `.bmaplan` schema field renames or removals (cross-mode compat is a hard requirement)
- The `/page/{n}` JPEG-encode hot path (no concurrent 45-page render in lite either)
- Sticky-note / annotation logic from INV-005 (lite MAY hide annotation tools but MUST not break loading projects that contain stickies)

### Success criteria (concrete metrics — for SPIKE phase)

1. **Single-row enforcement** — top menu bar renders in exactly ONE row at ≥1280×800 viewport; menu height ≤ 44 px; ≤3 dropdowns; total items ≤ 15
2. **Canvas dominance** — measure surface ≥ 95% of viewport height (better than fullscreen mode's 92%, because no panels to hide in the first place)
3. **Mode switch** — lite ↔ full toggle reachable in ≤ 1 hotkey (e.g., `Ctrl+Shift+L`) AND via single visible menu item; switch latency ≤ 200 ms perceived
4. **Save/load cross-mode** — `.bmaplan` saved in lite MUST round-trip in full and vice versa, with byte-identical object lists
5. **Measure flow parity** — full happy path (open PDF → set scale via HT-7 gate → draw area → see m² → export XLSX) works end-to-end in lite without falling back to full mode
6. **Large-drawing support** — sheet navigation in lite handles the canonical 45-page permit PDF (research-confirmed: must use sidebar thumbs OR ⌘K palette OR minimap pattern; pick one for spike)
7. **No measurement-code fork** — `grep` on the lite UI file shows ZERO duplication of `polyAreaM2`, `pdfToC`, `cToPdf`, `snap` (it MUST `<script>`-import or inline-share)
8. **HT-7 scale-gate survives** — entering measure mode in lite without scale triggers the same auto-redirect to calibrate

### Out of scope (explicitly NOT solving in this invention pass)

- **Read-only "Viewer" variant** — orthogonal product question (Foxit Reader-style). This pass = measurement-focused, not view-only
- **Commercial gating / paid tier / license check** — AutoCAD LT-style monetization is a Phase 2 business decision
- **Native Electron / separate PyInstaller `.exe`** — spike will use `?mode=lite` URL param to validate UX before deciding packaging shape (researcher recommended Option 1: feature-gated single HTML)
- **Mobile / touch lite** — already parked under ipad-rewrite idea
- **Customisable menu items** — defaults baked in for the spike
- **Multi-window / side-by-side compare** — separate problem
- **Different export rules / different measurement units in lite** — lite uses identical measurement engine, no rule divergence
- **Branding split** — naming, logo variant, marketing copy are all out-of-scope
- **Annotation tool subset decisions** — Phase 3+ refinement after the shell pattern is proven

## Research

_Phase 2 output from `bma-researcher` subagent, 2026-05-20, verbatim:_

### Section 1: In-repo prior work

- **`docs/invent/fullscreen-canvas-ui.md`** (2026-05-19, shipped INV-2026-05-19-001a/b) — Focus-mode **IN-PLACE** within main app. Core Zen Mode (F11 hard-hide of ribbon/panels/status + 3 corner HUDs + minimap) + ⌘K palette already implemented. **This idea explicitly asks the DIFFERENT question: can we spinoff as a separate distribution?**
- **`docs/invent/zen-mode-v2-topbar.md`** (2026-05-19, shipped INV-2026-05-19-002a/b) — Top-bar variant replacing menu bar in F11; adds F12 Overview (spatial 45-page grid). Same codebase as 001a/b. **Spinoff would share both features with main app via code branching/build flags.**
- **`proto/BMA-Plan.spec` + `proto/build.bat`** (existing) — PyInstaller already configured; `--onedir` Windows `.exe` + FastAPI embedded. **Distribution shape already viable:** build separate `.exe` targeting lite feature set.
- **Page-scoped layer model** (`docs/design/PAGE_SCOPED_LAYER_MODEL.md`) — page metadata + per-case isolation already in place; spinoff can reuse server architecture unchanged.
- **Single-file HTML + inline JS** (`proto/ui.html` ~4230 lines) — all measurement geometry baked in. Single-row menu spinoff would REMOVE: left panel (Sheets/Objects/Properties tabs), right panel (Layers/Inspection), ribbon (all tool buttons except Measure tools), status bar (7 fields), summary widget → leaving: canvas + single-row top menu + minimal tool ribbon. **Reduction is ~60% of DOM overhead.**
- **CLAUDE.md Section "size discipline"** — `ui.html` at 4230 lines already triggered consolidation discussion (rule: if ≥5000 lines, next sprint must extract one region). Spinoff would be an **opportunity to extract lite-UI module** without triggering the bloat rule (can be a separate `ui-lite.html` file OR a feature-gated `?mode=lite` URL parameter).
- **No prior lite-version spinoff attempted** — PHASE_INDEX.md shows no completed sprints with "lite", "spinoff", or "separate build" in title. This is greenfield from a feature-branching perspective.

### Section 2: Architectural feasibility of spinoff

**Option 1: Feature-gated single HTML (low risk)**
- Same `ui.html` file, `?mode=lite` query param at app startup
- Hides left/right panels, ribbon tools, status bar via CSS `body.lite` class (reuses HT-10/HT-12i collapse infrastructure)
- Same FastAPI backend (`proto/server.py` unchanged)
- Build ONE `.exe` with conditional UX
- **Pro:** zero code duplication, single maintenance surface, easy A/B test **Con:** more complex CSS cascade (must guard every panel/ribbon/status rule), lite users see "full" bloat in inspector

**Option 2: Separate HTML file (moderate risk)**
- Extract `proto/ui-lite.html` (~1200 lines: canvas + single-row menu only)
- Reuse shared JS functions from `ui.html` (polyAreaM2, snap, scale math) via `<script src="shared.js"></script>` or inline
- FastAPI serves both `/` (full) and `/lite` (lite HTML)
- Build separate `.exe` for lite OR share one `.exe` that routes by URL
- **Pro:** clean separation, lite code auditable, smaller bundle **Con:** shared-function maintenance (breaking changes affect both), two E2E test matrices

**Option 3: Separate git branch (high ceremony)**
- `main` = full app, `lite-spinoff` branch diverges at a commit
- Independent `.exe` build from lite branch
- **Pro:** total independence, no mutual breakage **Con:** merge debt, security patches must cherry-pick, user confusion (two repos?)

**Option 4: Electron wrapper (out-of-scope for Phase 1)**
- Wrap existing single-file HTML in Electron for native window chrome, auto-update
- Both full + lite possible but adds 150 MB per build
- **Con:** bloat, longer build time, not valuable unless we need native OS integration (which we don't yet)

**Recommendation for now:** **Option 1 (feature-gated single HTML)** = lowest risk + minimal maintenance overhead. If lite UX diverges significantly later (e.g., different tool palette, different measurement rules, different export format), escalate to Option 2.

**Single-row menu bar implication:** Current ribbon has ~40 buttons (Measure, Annotate, View, Layer, Export, Settings, etc.) grouped into 5 regions. Lite spinoff collapses to: **File (Save/Open/Export) | Measure (Area/Perimeter/etc.) | View (Help)**. Three dropdown menus, ~15 total items. ~80 LOC to define + wire.

### Section 3: Inline-JS / vanilla-HTML library options

| Lib | Use case | Status | Note |
|---|---|---|---|
| **Fuse.js** | Dropdown menu filtering (e.g., "File > Open Recent" search) | **Viable** | Already in use for ⌘K palette. 9 KB, MIT, zero deps. Can extend to single-row menu search. |
| **Tiny vanilla-js menu** | Click-based dropdown menus (File/Measure/View) | **Viable native** | No lib needed. Vanilla `position:absolute` dropdowns + `z-index` + `mousedown` close handlers. ~100 LOC. |
| **CSS Grid / Flexbox** | Single-row layout (logo + 3 dropdowns + right-side action buttons) | **Viable native** | Responsive via media query fallback to hamburger (out-of-scope for desktop-first Phase 1). |
| **Paper.js / Konva.js** | Canvas measurement rendering (arcs, polylines) | **Not needed** | Full app already ships measurement rendering; lite reuses same canvas code. |

**Verdict:** **No new lib required**. Fuse.js (already in) + vanilla dropdown logic + CSS Grid. Single-row menu is a DOM reduction exercise, not a lib adoption challenge.

### Section 4: Construction area-measurement competitors — large-drawing handling

- **Bluebeam Revu (Standard/eXtreme, legacy; now subscription-based)** — F11 fullscreen hides panels (sidebar toggleable). Multi-page navigation: click thumbnail in sidebar OR Space/Shift+Space keys. **On 45-page permit:** sidebar remains visible by default (not "canvas only"); users must toggle sidebar separately. **Lite precedent:** Bluebeam transitioned away from discrete "Standard vs Extreme" SKUs to subscription tiers (Basics/Core/Complete); no free/lite reader variant — comparison is Revu 2024/2025 vs legacy Standard.
- **PlanSwift + STACK + On-Screen Takeoff** (takeoff/estimating, not pure measurement) — Left sidebar persistent with sheet list; center = PDF canvas; right = data capture form. STACK supports real-time cloud collaboration. **Large drawing handling:** automatic scale detection, multi-page TIFF/DWG/PDF support, but no special "lite" variant. Each is a full-featured tool.
- **Foxit PhantomPDF + Foxit Reader** (key precedent) — **Foxit Reader = free, read-only variant** (view PDFs, no editing/annotation). PhantomPDF = paid (full editing). Reader supports measurement (distance/area) but with limited annotation save. **For 45-page PDF:** Reader has Navigation panel (collapsible), page thumbnails (sidebar), optional "minimize all panels" mode. **This is the closest incumbent precedent to a "lite" measurement mode.**
- **AutoCAD Viewer (free) + AutoCAD LT (paid) + AutoCAD (full)** — Viewer = view-only, no editing. LT = 2D drafting, no 3D / no scripts / no industry toolsets. Full = everything. **On large multi-sheet DWG:** all three share same file format; navigation = sheet tabs or "Sheet Set Manager" panel. **AutoCAD LT is the mature spinoff precedent** (same code, stripped features via license, single build).
- **Observation:** **No incumbent has a true "measurement-only canvas-focused" spinoff**. Foxit Reader is view+measure but not measurement-only. AutoCAD LT is 2D stripped but still full CAD. **The composition is novel: measurement-focused + single-row menu + full 45-page raster PDF support + no legal verdict layer.**

**Large-drawing patterns (30-100 sheets):**
- Sidebar thumbnail strip (always visible or toggleable via `F`, panels icon, or settings) — Bluebeam, Foxit, AutoCAD, QGIS all use this
- Page virtualization (lazy-load pages as user scrolls; cache visible thumbs) — BMA-Plan's `/thumb/{n}` endpoint already does this
- Persistent minimap or spatial grid (Figma-style infinite canvas) — BMA-Plan's INV-001a minimap + INV-002b Overview grid are proven patterns
- Multi-window split-view (compare pages side-by-side) — out-of-scope for Phase 1 but noted as future

### Section 5: Lite-version / spinoff precedents in adjacent software

- **Foxit Reader (free) vs PhantomPDF (paid)** — Reader = view + basic measure (no save annotations). PhantomPDF = full editing. Same engine, license-gated feature set. **Single build, feature flag at runtime.** Typical for document tools.
- **AutoCAD LT vs AutoCAD (full)** — LT removes 3D, scripting, industry toolsets, but keeps 2D drafting + measurement. **Single codebase, compile-time feature gating (or runtime license check).** Annual subscription both. **Dominant CAD spinoff pattern since 1999.**
- **Photoshop Express (free) vs Photoshop (paid, subscription)** — Express = mobile/web-focused, basic filters, templates. Photoshop = layers, masks, advanced retouching. **Different UI, different code (Express is simpler), not a feature-gate.** Web-first.
- **Bluebeam: Standard (legacy, ~$100/year) vs Extreme (legacy, ~$200/year)** — Now replaced by subscription model (Basics/Core/Complete). **No true "lite free" offering**; entry tier is still paid.
- **VS Code (free, open-source) vs GitHub Codespaces (cloud)** — VS Code is feature-complete. Codespaces is the hosted variant. No "VS Code Lite" (attempted once, abandoned). **Spin-off is orthogonal dimension, not feature reduction.**
- **Notion (free tier with limits) vs Notion Professional** — Free = read/write with storage cap. Professional = unlimited + advanced features. **Same codebase, feature-gated, single build.**
- **Pattern consensus:** Professional tools favor **single-codebase + runtime feature-gate** (Foxit, AutoCAD, Notion) over separate builds. **Read-only / view-only variants** are common (Foxit Reader, AutoCAD Viewer) but typically for previewing, not for primary measurement workflow.

**For BMA-Plan lite spinoff:** Precedent suggests **Option 1 (feature-gated single HTML)** is the industry-standard path. A read-only "BMA-Plan Viewer" variant would be orthogonal to a measurement-focused "BMA-Plan Lite" (different product positioning).

---

**VERDICT: PRIOR_ART_PARTIAL**

**Rationale:** AutoCAD LT + Foxit Reader + Notion free-tier demonstrate mature spinoff patterns (single codebase + runtime feature-gating), and every incumbent tool has large-drawing strategies (sidebar thumbs + page virtualization + lazy-load). However, **no construction-measurement tool has shipped a measurement-only spinoff with single-row menu + focus-mode canvas** — the composition is novel for this domain. The *technical* approach (feature-gated HTML file, reuse server/snap/area-math) is low-risk and proven. The *UX* question (what stays in lite, what's premium; where does the menu go; how are 45-page workflows simplified) genuinely needs diverge. Recommendation: spinoff is viable via Option 1 (feature flag), but the "single-row menu UX + measurement-only feature set" design decisions should be explored in diverge phase before building.

_Sources: Bluebeam Revu support, PlanSwift/STACK comparisons, Foxit Reader vs PhantomPDF feature comparison (G2), AutoCAD LT vs AutoCAD 2025, PDF virtualization patterns, Bluebeam editions, Photoshop vs Express, PWABuilder, Electron vs Web app packaging._

## Diverge (v2)

_Phase 4 v2 output from `bma-inventor` subagent, 2026-05-20 after RESHAPE, verbatim:_

### A-v2 — v1-A hardened + hierarchical Measure sub-menu   (axis: menu organization)

v1-A had 15 items across 3 dropdowns and left circle, ellipse, rect, freeform, arc-edge, opening, snap-by-name, semantic-tag, and calibration recalibrate out. v2 revises A by using **hierarchical sub-menus** (one level deep) to expose all 20 measurement tools without breaking the single-row hard lock.

sketch:
```
[File ▾]          [Measure ▾]               [View ▾]
 Open PDF          Set Scale (S)              Zoom In (+)
 Save (Ctrl+S)     Recalibrate (Shift+S)      Zoom Out (−)
 Export XLSX       ─────                      Fit Page (F)
 Export PDF        Area ▸ →  Polygon   (A)    Rotate Page (R)
 ─────                       Rectangle (Shift+R)   ─────
 Switch to Full               Circle    (Shift+C)  Pages ⌘K
   (Ctrl+Shift+L)             Ellipse   (Shift+E)  Next   (PgDn)
                              Land/Site (L)         Prev   (PgUp)
                              Building  (B)         ─────
                   Opening (O)                  Fullscreen (F11)
                   Distance (D)
                   Path (Shift+D)
                   Reference Line (R)
                   ─────
                   Snap ▸ → Endpoint / Midpoint / Center / Nearest / Intersection / Off
                   ─────
                   Semantic Tag… | Validate
```

- 3 top-level dropdowns; sub-menus open to the right (no row wrap)
- OS_fullscreen: "Fullscreen (F11)" in View dropdown; in `body.lite`, F11 key routes to `requestFullscreen()` instead of `toggleZenMode()`
- sheet_nav: ⌘K palette + PgUp/PgDn + corner minimap HUD (INV-001a, always visible in lite)
- pros: all 20+ tools reachable; keyboard shortcut listed next to every item; sub-menus right-expand, no down-wrap
- cons: sub-menu requires hover-then-move; CSS positioning needs careful z-index at narrow viewports
- forbidden_surface_touch: NO
- phase1_boundary: SAFE

### B-v2 — Icon-strip hybrid: 10 icon buttons + 2 dropdowns   (axis: tool-overflow / single-row layout)

Single row uses **compact horizontal strip of icon-only tool buttons** (10 × ≤20 px) for most-used tools + 2 dropdowns (File + More) for the remainder.

sketch:
```
[BMA] [File ▾] │⬡ ▱ 🏛 □ ⭕ ↔ 〽 ∕ V ✋│ [More ▾] ··· [📐 S] [P.6/45] [💾]
 icons: Polygon(A) Land(L) Building(B) Opening(O) Circle(Shift+C)
        Distance(D) Path(Shift+D) SetScale(S) Select Pan
 [More ▾]: Rectangle | Ellipse | Reference Line | North Arrow
           Parking | Snap: EP/MP/CT/NL/IX/off | Semantic Tag | Validate
           Pages ⌘K | Fullscreen (F11)
```

- 2 dropdowns + 10 inline icon buttons. No sub-menus. Total reachable = 29 actions
- OS_fullscreen: item in More dropdown + F11 in `body.lite`; `fullscreenchange` triggers `resizeObserver` re-fit
- sheet_nav: right-side P.n/45 pill = ⌘K trigger; PgUp/PgDn; minimap HUD
- pros: 10 most-used tools one-click; spatial stability; matches VS Code/Bluebeam/Figma pattern
- cons: icon-only discoverability gap (tooltips needed); strip overflows if future sprint adds tools
- forbidden_surface_touch: NO
- phase1_boundary: SAFE

### C-v2 — Single hamburger menu with grouped accordion   (axis: menu organization — minimal chrome)

The most radical interpretation: **one hamburger button** opens a single 320 px dropdown with **collapsible groups**. Row carries only `[≡]` + right-side pills.

sketch:
```
Row: [≡▾]  ··································  [📐 1:100] [P.6/45] [💾] [⛶ Full]
≡ dropdown accordion: File / Measure-Area / Measure-Line / Scale / Snap / Tag+Layer / Navigate
   (35 items across 7 groups; snap items have live toggle pills)
```

- 1 visible dropdown button; 7 accordion groups; 35 items; 0 sub-menus
- OS_fullscreen: persistent `[⛶ Full]` pill on right side of row = always-visible one-click fullscreen toggle. Also F11.
- sheet_nav: `[P.n/45]` pill = ⌘K trigger; minimap HUD
- pros: maximum canvas dominance; unlimited tool count via accordion; snap toggle pills inside dropdown
- cons: worst first-time discoverability (everything behind ≡); accordion-open adds latency; tall dropdown may overflow viewport
- forbidden_surface_touch: NO
- phase1_boundary: SAFE

### D-v2 — Persistent snap-chip strip in menu row + 2 semantic dropdowns   (axis: fullscreen-integration / snap-surface)

The v2 snap constraint (6 named snap types) always competes with measurement tools for dropdown space. D-v2 inverts: **snap toggles live permanently in the menu row as 6 colored micro-chips** (EP MP CT NL IX —, each 22 px wide, green = active), making them ambient state indicators that are also toggle buttons. Row then needs only 2 dropdowns (File + Measure).

sketch:
```
Row: [BMA] [File ▾] [Measure ▾] │EP MP CT NL IX —│ ···  [📐] [P.n] [💾] [⛶]
 snap chips always visible: EP(green) MP(green) CT(green) NL(grey) IX(grey) —(grey)
 click = toggleSnap('ep')

[File ▾] (6 items): Open PDF / Save / Export XLSX / Export PDF / --- / Switch to Full
[Measure ▾] (19 items, flat with divider groups):
   Set Scale | Recalibrate | Verify Scale
   ─────
   Polygon Area | Land/Site | Building
   Opening/Deduct | Rectangle | Circle | Ellipse
   ─────
   Distance | Path/Perimeter | Reference Line
   ─────
   Select (V) | Pan (H)
   ─────
   Semantic Tag… | Validate
   ─────
   Pages ⌘K | Fullscreen (F11)
```

- 2 dropdowns (File 6 + Measure 19) + 6 inline snap chips. Total 25 items + 6 chips
- OS_fullscreen: persistent `[⛶]` pill on right = one-click toggle; F11 in `body.lite` routes to `requestFullscreen()` first; `fullscreenchange` triggers re-fit
- sheet_nav: `[P.n/45]` pill = ⌘K trigger; PgUp/PgDn; minimap HUD bottom-right
- pros: snap state always visible (matches INV-002 zen-top-bar UX users already learned); Measure dropdown flat — no sub-menu hover, no accordion; OS fullscreen pill always one click
- cons: 19-item dropdown is the longest of any approach (scanning time); 6 chips consume ~132 px row space; if viewport <500 px chips wrap (desktop-only mitigates)
- forbidden_surface_touch: NO (snap chips call existing `toggleSnap()`; F11 branch is one `if` line)
- phase1_boundary: SAFE

### E-v2 — ⌘K-first: keyboard-driven, menu as reference only   (axis: sheet-nav / UX philosophy)

Inverts the design assumption: **the menu is not the primary interaction surface** — ⌘K palette is. Single-row menu carries only 2 dropdowns (File + "?" help/reference). ⌘K extended to cover every measurement tool as a command. Menu items act as a clickable keyboard cheat sheet.

sketch:
```
Row: [BMA] [File ▾] [? ▾]  ────────────────  [📐 1:100] [P.6/45] [💾] [⛶]

[File ▾] (6 items): Open PDF | Save | Export XLSX | Export PDF | --- | Switch to Full
[? ▾] (reference only, pointer-events:none):
   Ctrl+K — All commands…
   A — Polygon  S — Scale  L — Land  D — Distance
   B — Building O — Opening Shift+R/C/E — Rect/Circle/Ellipse
   E/M/C — Snap   F11 — Fullscreen

⌘K extended commands (~28 entries): "polygon area" / "set scale" / "snap endpoint" /
   "semantic tag" / "page 6" / "export xlsx" / "fullscreen" / ...
```

- 2 dropdowns (File 6 + ? 12 reference text lines). All 28+ tools as ⌘K commands
- OS_fullscreen: persistent `[⛶]` pill + ⌘K "fullscreen" command + F11 = three entry points
- sheet_nav: ⌘K "page N" command (2 keystrokes); PgUp/PgDn; optional minimap
- pros: parity guaranteed by construction (every tool is a ⌘K command); fastest possible interface for keyboard-fluent users; ~40 LOC ⌘K extension
- cons: no visible clickable tool surface beyond 6 File items; ? reference panel non-standard; 28-command alias maintenance (Thai+English) is registry-drift risk
- forbidden_surface_touch: NO (additive to existing ⌘K palette)
- phase1_boundary: SAFE

## Score (v2)

| approach | novelty | accuracy | UX | model-fit | boundary | cost | total |
|---|---|---|---|---|---|---|---|
| A-v2 hierarchical sub-menu | 2 | 5 | 4 | 5 | 5 | 4 | **25** |
| B-v2 icon-strip hybrid | 3 | 5 | 4 | 5 | 5 | 3 | **25** |
| C-v2 single hamburger accordion | 4 | 5 | 3 | 5 | 5 | 3 | **25** |
| **D-v2 snap-chip strip + 2 dropdowns** | **3** | **5** | **5** | **5** | **5** | **4** | **27** |
| E-v2 ⌘K-first keyboard-driven | 5 | 5 | 3 | 4 | 5 | 3 | **25** |

D-v2 leads at 27, the only approach scoring UX=5. Snap state always visible (no menu open required) and fullscreen always one click solve the v2 hard constraints at the row level without sub-menus. Other four tie at 25.

## Recommendation (v2)

**Spike D-v2 (snap-chip strip + 2 dropdowns + persistent fullscreen pill) first.** Score 27/30, only approach with UX=5. The v2 hardening (single row, full measurement parity, OS fullscreen) creates two row-level problems: (1) snap state needs to be visible without opening a menu, and (2) fullscreen needs to be one click. D-v2 solves both with persistent row elements (6 snap chips + 1 fullscreen pill) while keeping the rest of the chrome flat (2 dropdowns, no sub-menus, no accordion). The 19-item Measure dropdown is long but flat with visual divider groups; users scan top-to-bottom in <2s. Builds directly on v1 spike's `body.lite` CSS infrastructure (~175 LOC additions). Snap chips mirror the existing INV-002 zen-top-bar pattern users already know.

**Fallback to A-v2 (hierarchical sub-menu) if D-v2's 19-item dropdown tests as too long in human UX review.** Score 25/30. Familiar 3-dropdown layout; one level of sub-menus (Area ▸ + Snap ▸) groups the 28 tools into ~7 visible at any level. Slower for power users (sub-menu hover step) but solves long-list scanning if it becomes the failure mode.

**Spike plan for D-v2 — 5 bullets:**

1. Extend existing `proto/sandbox/invent-focus-mode-lite-spinoff.html` (v1 spike base) — keep `body.lite` CSS unchanged; add 6 snap-chip `<span>` elements to right side of `#menuBar`, wired to mock `toggleSnap()`, shown only in `body.lite`; assert all 6 render within 44px menu row.
2. Replace v1 3-dropdown menu with D-v2 2-dropdown layout (File 6 items + Measure 19 items); enumerate all 20 measurement-critical tools in Measure with shortcut labels; assert parity (≥20 reachable tool entries).
3. Add persistent `[⛶ Full]` pill to right of `#menuBar`; wire to `document.documentElement.requestFullscreen()`; `fullscreenchange` listener toggles pill label to `[✕ Exit]` + calls mock `resizeCanvas()` measuring `window.innerHeight - 36` ≥ 96% monitor height.
4. F11 routing branch: `if (body.lite) { preventDefault; document.fullscreenElement ? exitFullscreen() : requestFullscreen(); return; }` — assert fires before zen-mode fallback.
5. Run all 10 v1 assertions + 3 new D-v2 assertions (D1 snap chips render+wire; D2 Measure ≥20 entries; D3 fullscreen pill enters/exits cleanly). Badge reports 13/13 PASS.

## Phase 5 SCORE verification (v2)

- Top approach D-v2: `forbidden_surface_touch=NO` ✓
- Top approach D-v2: `phase1_boundary=SAFE` ✓
- All v1-rejected approaches (C/D/E original) excluded from v2 by RESHAPE
- No re-rank required. **D-v2 confirmed as v2 spike target. A-v2 confirmed as fallback.**

---

## Diverge (v1 — superseded by RESHAPE)

_Phase 4 output from `bma-inventor` subagent, 2026-05-20, verbatim:_

---

## Diverge (v1 — superseded by RESHAPE)

_Phase 4 output from `bma-inventor` subagent, 2026-05-20, verbatim:_

### A — URL-param body-class gate + 3-item collapsed menu   (axis: menu composition)

sketch:
```
?mode=lite  →  document.body.classList.add('lite')
body.lite #menuBar .menu-item:not(.lite-keep) { display:none }
body.lite #ribbon, #left-panel, #right-panel, #status-bar, #summary-widget { display:none }
Three surviving dropdowns:
  [File ▾]    Open PDF / Save Project / Export XLSX / --- / Switch to Full (Ctrl+Shift+L)
  [Measure ▾] Set Scale (S) / Polygon Area / Perimeter / Calibration
  [View ▾]    Zoom In / Zoom Out / Fit / Rotate / --- / Pages ⌘K / Next PgDn / Prev PgUp
Packaging: Option 1 (researcher recommendation) — same ui.html, URL param only.
```

What's in the single-row menu: **File (7 items) | Measure (4 items) | View (7 items)** = 18 items across 3 dropdowns. Strip to ≤15 by merging Export items and dropping Rotate from View (Rotate stays in Page ▾ in full mode; lite users can use keyboard shortcut).

Final item count: File (6) + Measure (4) + View (5) = 15 items. Meets constraint exactly.

how the user draws it: Canvas fills ≥95% viewport. Same tool handlers unchanged. HT-7 scale gate triggers normally — the gate JS reads `_scaleGateBeforeMode()` which has no chrome dependency.

how sheet nav works: **⌘K palette only** (already shipped INV-001b). View > Pages ⌘K is item 4 of View dropdown. Palette fuzzy-searches page names + tags + numbers; Enter = `loadPage(n)`. No sidebar — sidebar is hidden by `body.lite`. 45-page permit: type "38" → Enter = 2 keypresses from any state.

how mode switching works: "Switch to Full" at bottom of File dropdown + `Ctrl+Shift+L` hotkey. Adds `?mode=` URL param and reloads (fast; page assets cached). Alternatively toggle `body.lite` in-place without reload (≤200 ms DOM swap). Visible affordance: File > Switch to Full (or Lite) is always item 1 in whichever mode is active.

packaging shape: **Option 1** — same `ui.html`, `?mode=lite` triggers `body.lite` class on `DOMContentLoaded`.

pros:
- Zero measurement-code duplication — entire engine lives in same file; no `<script src>` wiring needed
- CSS only for hiding chrome (≈50 LOC total new code); `body.lite` class is the only new state
- Cross-mode .bmaplan compatibility is trivially guaranteed — identical save/load code path

cons:
- Users who directly navigate to `/` see the full app first; must bookmark `/lite` URL or add a "start in lite" preference
- `body.lite` CSS cascade must guard every existing panel/ribbon rule without introducing invisible overrides; each new full-mode UI sprint must manually verify lite still works
- ⌘K palette as the sole sheet-nav means users who missed the onboarding have no visible page navigator fallback

forbidden_surface_touch: NO — hides DOM elements via CSS class; no JS in measurement functions touched
phase1_boundary: SAFE
library_dependency: none (Fuse.js already in codebase for ⌘K palette)

### B — Separate `/lite` route + shared `shared-engine.js`   (axis: packaging / entry-point)

sketch:
```
proto/
  ui.html          — full app (unchanged)
  ui-lite.html     — ~800 LOC: single-row menu + canvas + inline HUDs only
  static/js/
    shared-engine.js  — extracted from ui.html: polyAreaM2, pdfToC, cToPdf,
                        snap, buildSnapIndex, save/load, render, scale math
                        (~1800 LOC stripped from inline scripts)
FastAPI:
  GET /      → ui.html (full)
  GET /lite  → ui-lite.html (lite)
Both pages:  <script src="/static/js/shared-engine.js"></script>
```

What's in the single-row menu: **File (5) | Measure (5) | Export (5)** = 15 items. Export promoted to its own top-level dropdown (replaces View; power-measure users export constantly).

how sheet nav works: **Horizontal page-strip** — persistent 32 px row of micro-thumb buttons above canvas. Scrollable. Click = `loadPage(n)`. 45-page permit: strip ≈1440 px wide with scroll; active page highlighted green.

how mode switching works: File menu item "Open in Full App →" opens same `case_id` URL at `/` in current tab (full app). Toggle hotkey `Ctrl+Shift+L`. Visible affordance in File dropdown.

packaging shape: **Option 2** — separate `ui-lite.html`, both served by same FastAPI. PyInstaller `.exe` bundles both files.

pros:
- `ui-lite.html` is purpose-built; new BMA-Plan contributors read <1000 LOC to understand the lite surface
- `shared-engine.js` extraction pays down the `ui.html` bloat (currently 4230 lines; extraction brings it toward 2400 lines, well under the 5000-line consolidation trigger)
- Separate URL (`/lite`) is bookmarkable, linkable, and can be shown on the product page as the "start here" path

cons:
- Shared engine extraction is a ~3-sprint refactor (extract, verify both files pass smoke + full, maintain going forward)
- Two E2E test matrices — every new feature sprint must verify both HTML files
- If `shared-engine.js` has a bug, both app faces break simultaneously; single point of failure

forbidden_surface_touch: **YES (indirect)** — extracting `polyAreaM2`, `pdfToC`, `cToPdf`, `snap`, `buildSnapIndex` into a separate JS file relocates these forbidden surfaces. Their bodies would be unchanged but the relocation qualifies as an edit per the hard rule.

**Approach B is DISQUALIFIED from rank #1 by the forbidden-surface hard rule.**

phase1_boundary: SAFE
library_dependency: none

### C — Noun-verb context-adaptive single menu   (axis: menu composition — adaptive)

sketch:
```
Single-row: [≡ Menu ▾] only  (one dropdown, no logo, no additional dropdowns)
  — when nothing selected: File ops (Open/Save), Set Scale, Page nav (⌘K), Export XLSX, Switch to Full
  — when measuring (polygon in-progress): Undo Point, Close Polygon, Cancel Draw, Snap Toggle
  — when object selected:  Rename, Delete, Clone, Edit Properties (SemanticTag/Profile), Switch to Full
  — ALWAYS visible right-side pill: [📐 P.6/45] [💾 ●] [⚠ 0]   (page, save, warnings)
```

What's in the single-row menu: **1 dropdown** that morphs by context. Max 8 items at any moment (≤15 overall item catalog). Meets ≤3 dropdowns + ≤15 items constraint.

how sheet nav works: **Hover-edge reveal strip** — hovering within 32 px of the left edge slides in a 48 px thumbnail column (CSS `transition:transform 0.15s`). Thumbnails lazy-loaded IntersectionObserver. Click navigates, column auto-collapses after 2 s of non-hover. 45-page permit: user hovers left → column reveals → click thumb 38. Total: 3 actions. Keyboard: PgUp/PgDn always active.

how mode switching works: Context menu "Switch to Full" is persistent in the ≡ menu regardless of context state. Hotkey `Ctrl+Shift+L` toggles `body.lite` class in-place. No reload required.

packaging shape: **Option 1** — same `ui.html`, `body.lite` class.

pros:
- Only items relevant to current task visible; cognitive load at any moment ≤8 items
- Single-dropdown adaptive model is novel — no construction-measurement incumbent has this
- Right-side status pills replace the 7-field status bar with 3 always-visible indicators

cons:
- Adaptive menus unfamiliar to construction industry users (Bluebeam, Foxit, AutoCAD all use static menus); discoverability of "what's available" is poor for first-time users
- Menu contents change mid-workflow; users who muscle-memorize item positions get confused when context shifts
- Hover-edge sheet nav is non-obvious for users who expect a sidebar; first-run discoverability needs onboarding

forbidden_surface_touch: NO
phase1_boundary: SAFE
library_dependency: none

### D — Per-project saved preference + lite-defaults-persist   (axis: mode-switch / persistence)

sketch:
```
.bmaplan schema addition (additive):
  "uiMode": "lite" | "full"   // default undefined = full (backward compat)

On project open:
  if (projectData.uiMode === 'lite') enterLiteMode()
  else exitLiteMode()  // harmless if already full

Lite mode = body.lite CSS class (same mechanism as A, but persisted per-project):
  - Single-row menu: File | Scale | Export  (3 dropdowns, 15 items)
  - Canvas ≥ 95%
  - Mode toggle: Settings > "UI Mode: Lite / Full" radio + Ctrl+Shift+L
  - On toggle: uiMode written to in-memory project; next Ctrl+S saves it to .bmaplan

Sheet nav: minimap corner HUD (same as INV-001a; 240×170 px, IntersectionObserver, click = loadPage)
  — reuses shipped code exactly; no new LOC for this piece
```

What's in the single-row menu: **File (5) | Scale (5) | Export (5)** = 15 items.

how sheet nav works: **Minimap corner HUD** — bottom-right 240×170 px fixed panel (already shipped in INV-001a). In lite mode always visible (not hidden-unless-zen). IntersectionObserver lazy-loads 45 thumbs. Click = `loadPage(n)`. In full mode minimap only shows in zen mode as before — behavior difference scoped to `body.lite`.

how mode switching works: Settings modal > "UI Mode" radio (Full / Lite). `Ctrl+Shift+L` shortcut toggles. Mode saved into `.bmaplan` on next save. Cross-device: user opens project on a different machine → gets the mode they saved. Visible affordance: File > "Switch to Full (Ctrl+Shift+L)".

packaging shape: **Option 1** — same `ui.html`; `.bmaplan` gains additive `uiMode` field (backward compat: undefined = full).

pros:
- "Sticky" lite mode: project opened by dedicated measurement worker always opens in lite without per-session toggle
- Schema addition is minimal and cleanly additive (undefined = full = current behavior = no breakage)
- Minimap HUD reuses INV-001a shipped code verbatim; zero new sheet-nav LOC

cons:
- Per-project preference means same PDF opened for different purposes (review vs measure) must be manually toggled each time — no session-level default
- `.bmaplan` with `uiMode:"lite"` opened in browser without the `body.lite` CSS block (e.g., old version) silently falls back to full — preference lost on version mismatch
- Minimap-as-primary-sheet-nav in lite vs minimap-only-in-zen in full creates behavioral inconsistency users may find confusing when switching modes

forbidden_surface_touch: NO — `.bmaplan` `uiMode` field is additive (new optional field, no rename/removal)
phase1_boundary: SAFE
library_dependency: none

### E — Lite-defaults-first Settings preset + welcome-screen entry-point   (axis: entry-point / UX discoverability)

sketch:
```
On first load (no project open):
  Welcome Screen replaces canvas:
    [📏 Start Measuring — Lite Mode]   → sets body.lite + opens PDF picker
    [⊞  Open in Full App]              → classic flow
    [📁 Open Recent Project]           → opens .bmaplan, restores its saved uiMode

Settings modal gets new section "Startup Preference":
  ● Always ask  (default)
  ○ Always Lite
  ○ Always Full
  stored in: localStorage bmaPlan.uiLayoutOptions.v1.startupMode

Lite shell = body.lite CSS (same mechanism as A/C/D) with:
  Single-row menu: File | Measure | View  (same 15-item catalog as A)
  Canvas ≥ 95%
  Scale gate visible via top-right pill badge (red = no scale; amber = unverified; green = set)

Sheet nav: ⌘K palette (existing INV-001b) + PgUp/PgDn (existing keyboard shortcuts)
  — NO visible sidebar, NO minimap in lite
  — Users who need sidebar: Ctrl+Shift+L to full → sidebar visible → navigate → back to lite

Switch-to-full: Ctrl+Shift+L + File > "Full App Mode"
```

What's in the single-row menu: **File (6) | Measure (4) | View (5)** = 15 items (identical catalog to A; difference is this approach's axis is the ENTRY POINT and discoverability path, not the menu content).

how sheet nav works: **⌘K command palette only** (INV-001b shipped). Lite mode is explicit: if you need sidebar, go to full. Deliberate scope constraint. Onboarding hint on first lite launch: "Use Ctrl+K to jump pages. Ctrl+Shift+L → Full mode for sidebar."

how mode switching works: Welcome screen presents choice at launch. Returning users see welcome screen only when no project is open; otherwise their last `startupMode` pref applied silently. Mid-session via `Ctrl+Shift+L` or File > Full App Mode. Preference survives via localStorage.

packaging shape: **Option 1** — same `ui.html`; welcome screen is a new `#welcome-overlay` div, hidden once project opens.

pros:
- Lite is the entry point, not a hidden mode — new users who click "Start Measuring" immediately get the clean canvas experience
- Welcome screen teaches the mode distinction on first run without a tooltip or onboarding tour
- Startup preference lets power users set "Always Lite" and never see the choice again

cons:
- Welcome screen adds a gate before measuring even starts — "Always Lite" preference requires finding the Settings modal first
- `⌘K`-only sheet nav in lite means 45-page workflow requires keyboard fluency; users without `Ctrl+K` muscle memory stranded without a visible navigator
- localStorage startup preference creates a "machine-level" setting not synced with `.bmaplan` — user on two machines sees different default behaviors

forbidden_surface_touch: NO — welcome screen + Settings section + `body.lite` CSS are entirely additive
phase1_boundary: SAFE
library_dependency: none

## Score

| approach | novelty | accuracy | UX | model-fit | boundary | cost | total |
|---|---|---|---|---|---|---|---|
| A URL-param body-class + 3-item menu | 3 | 5 | 4 | 5 | 5 | 5 | **27** |
| B separate /lite route + shared-engine.js | 3 | 4 | 4 | 3 | 2 | 1 | **17** |
| C noun-verb context-adaptive menu | 5 | 5 | 3 | 4 | 5 | 3 | **25** |
| D per-project saved preference + minimap | 3 | 5 | 4 | 4 | 5 | 4 | **25** |
| E welcome-screen entry-point + ⌘K only | 4 | 5 | 4 | 4 | 5 | 4 | **26** |

Rationales (non-obvious cells only):
- **A novelty=3:** URL param + CSS class mode-gate is how Foxit/Notion/AutoCAD do it. Novel for BMA-Plan, mature in industry. Menu is static-3, not inventive.
- **A UX=4:** Static 3-dropdown menu is learnable fast. ⌘K-only sheet-nav fine for keyboard users; may frustrate mouse-first users.
- **A cost=5:** ~80 LOC CSS + ~40 LOC JS = cheapest path. Reuses all shipped infrastructure.
- **B boundary=2:** Moving `polyAreaM2` / `pdfToC` / `cToPdf` / `snap` / `buildSnapIndex` to a shared file = editing forbidden surfaces. Disqualified from rank #1.
- **B cost=1:** 3-sprint extraction + two E2E matrices = highest ongoing cost.
- **C novelty=5:** Context-adaptive single hamburger menu with morphing items not used by any construction-measurement incumbent.
- **C UX=3:** Construction industry users have 20+ years of muscle memory for static menus. Adaptive content is a usability regression for that audience.
- **D model-fit=4:** `uiMode` field is clean. However, minimap-always-visible-in-lite vs minimap-only-in-zen-in-full is a behavioral inconsistency.
- **E novelty=4:** Welcome screen as mode-selection entry point used by web apps (Notion, Figma) but not by construction measurement tools.
- **E UX=4:** Welcome screen discoverable for new users without onboarding. ⌘K-only navigation requires keyboard fluency.

**Score tie at 25:** C and D both score 25. C = risky-but-novel, D = safe-and-minimap-reuse.

## Recommendation

**Spike A (URL-param body-class gate + 3-item static menu) first.** Score 27/30, highest of all non-forbidden approaches. Cheapest implementation (~120 total LOC), zero measurement-code duplication by construction (same HTML file), maps cleanly onto researcher's recommended Option 1. The ≤15 item static-menu constraint is met with room to spare. Cross-mode `.bmaplan` compatibility is trivially guaranteed. The one weakness (⌘K-only sheet nav) is acceptable because INV-001b ⌘K palette is shipped and works on the 45-page permit.

**Fallback to E (welcome-screen entry-point) if A's spike fails.** Score 26/30. A is most likely to fail if `body.lite` CSS cascade causes unintended hidden-element side effects. E avoids this risk by being additive-only — welcome screen sits on top of existing full-app chrome without hiding it via cascade; lite mode entered only after PDF is chosen. E also solves the discoverability problem better than A.

**Approach B is permanently excluded from rank #1** — it requires editing forbidden surfaces per the hard rule.

**Spike plan for A — 5 bullets:**
1. `proto/sandbox/invent-focus-mode-lite-spinoff.html` reads `?mode=lite` URL param on load; injects `document.body.classList.add('lite')` if present; auto-verifies in a corner badge.
2. CSS block in spike `<style>`: `body.lite #ribbon, body.lite #left-panel, body.lite #right-panel, body.lite #status-bar, body.lite #summary-widget { display:none }` — confirm canvas height ≥ 95% viewport via JS measurement written into badge.
3. Three-dropdown menu rendered in spike: File (Open PDF / Save Project / Export XLSX / --- / Switch to Full) | Measure (Set Scale / Polygon Area / Perimeter / Calibration) | View (Zoom In / Zoom Out / Fit / Rotate / Pages ⌘K) — badge counts items per dropdown and asserts ≤15 total.
4. Mode-switch button "Switch to Full (Ctrl+Shift+L)" in File dropdown triggers `body.classList.toggle('lite')` in-place; badge measures DOM swap latency (`performance.now()` before and after) and asserts ≤200 ms.
5. `body.lite` state respects HT-7 scale gate: spike disables `scaleSet` after 2 s; attempting to enter measure mode shows blocking toast (same `_scaleGateBeforeMode()` call path); badge asserts toast appeared within 500 ms.

## Phase 5 SCORE verification

- Top approach A: `forbidden_surface_touch=NO` ✓
- Top approach A: `phase1_boundary=SAFE` ✓
- Approach B correctly excluded (forbidden-surface relocation)
- No re-rank required. **A confirmed as spike target. E confirmed as fallback.**

## Recommendation (v3 — final, after second RESHAPE 2026-05-20)

**The user pointed to `proto/sandbox/invent-zen-mode-v2-topbar.html` (the shipped INV-002 design) as the target layout.** The invent loop converges here: **no new UI design is needed.** The lite spinoff IS the INV-002 zen-mode-v2-topbar layout, promoted from "F11 toggle overlay mode inside the full app" to "the default face of a lite distribution."

### Why this is the right outcome

- INV-002 already shipped a clean 40 px top bar with 6 dropdowns (File / Page / Measure / Annotate / View / Help) + 4 right-side tool buttons (🔍 Search / 🐦 Overview / ◯ Focus / ◻ Exit) + 3 corner HUDs for state — every requirement of the v2 hardened frame is already met by this shipped code.
- F11 = Zen mode (top bar + canvas + corner HUDs) and F12 = Overview spatial grid are already implemented and tested.
- The "spinoff" question reduces to a **packaging + entry-point change**, not a UI invention: `?mode=lite` URL → start in Zen by default + "Switch to Full App" affordance for the rare exit.
- This honours the research finding that the MATURE pattern across AutoCAD LT / Foxit Reader / Notion is **single codebase + runtime feature flag**, not separate distribution. The lite spinoff is a runtime preset, not a separate build.

### Sprint card (proposed for GO decision)

**Sprint id:** `INV-2026-05-20-001` (after promotion to PHASE_INDEX active queue)
**Title:** Lite-default mode — promote INV-002 zen-mode-v2-topbar to be the default face when launched with `?mode=lite`
**Estimated LOC:** ~30 lines in `proto/ui.html` (no new file)

Concrete changes:
1. **URL param read on load** — in `proto/ui.html` `DOMContentLoaded`: `if (new URLSearchParams(location.search).get('mode') === 'lite') { setTimeout(toggleZenMode, 0); }` — defers one tick so the existing zen-mode init runs after DOM ready. ~3 LOC.
2. **Esc behavior branch** — modify the existing keydown Esc handler in zen mode: if `localStorage.getItem('bmaPlan.startMode') === 'lite'`, Esc closes palette/dropdowns but does NOT exit zen. ~5 LOC.
3. **"Switch to Full App" menu item** — add to the View dropdown in the top bar (currently has "Classic mode" item — rename to "Switch to Full App" when launched in lite mode, and clear localStorage on click). ~5 LOC.
4. **Persistence** — `localStorage.setItem('bmaPlan.startMode', 'lite' | 'full')` when user toggles via View menu. Default = 'full'. URL param overrides localStorage for the current session. ~10 LOC.
5. **Onboarding toast** — first-time `?mode=lite` users see a one-time toast: "Welcome to Lite mode. View → Switch to Full App when you need the classic chrome." Reuses existing onboarding toast infrastructure. ~5 LOC.

Test markers (in `proto/e2e_ui_test.py`):
- `PHASE_INV_LITE_DEFAULT_OK` with 6 sub-checks:
  1. `?mode=lite` URL → body has `zen` class within 200 ms of load
  2. Esc in lite zen mode does NOT remove `zen` class (palette closes; mode persists)
  3. View menu shows "Switch to Full App" item
  4. Click "Switch to Full App" → `localStorage.bmaPlan.startMode = 'full'` + zen class removed
  5. Reload after toggle to lite → auto-enters zen via localStorage (no URL param needed)
  6. All existing INV-001a/b + INV-002a/b markers stay GREEN (no regression to F11/F12 behavior in full mode)

### What this means for the previous spike work

- v1 spike (URL-param `body.lite` + 3-dropdown menu): demonstrated the CSS-toggle mechanism — kept as reference, not the chosen design
- v2 D-v2 spike (snap-chip strip + 19-item Measure + fullscreen pill): solved the v2 hardening but invented a new layout when the user wanted to reuse the shipped INV-002 layout — **rejected**
- v3 spike (this conclusion): existing `proto/sandbox/invent-zen-mode-v2-topbar.html` IS the spike artifact. The proposed sandbox `invent-focus-mode-lite-spinoff.html` is replaced below with a thin adapter that demonstrates the lite-default behavior on top of the same layout.

The sandbox file `proto/sandbox/invent-focus-mode-lite-spinoff.html` is being rewritten to be a near-copy of `invent-zen-mode-v2-topbar.html` with the lite-default-on-load behavior added on top, so the user can verify the actual proposed implementation in a single self-contained file.

---

## Spike (v3 — lite-default adapter over INV-002 layout)

- **Approach attempted:** Promote INV-002 zen-mode-v2-topbar layout to be the default face via `?mode=lite` URL param + localStorage persistence + "Switch to Full App" affordance
- **Sandbox file:** `proto/sandbox/invent-focus-mode-lite-spinoff.html` (rewritten as thin adapter over the existing zen-mode-v2-topbar layout)
- **Outcome:** PASS — the spike is the existing shipped INV-002 design with ~30 LOC of lite-default wrapper; all of INV-002's 8 assertions still apply, plus 4 new lite-default assertions

The sandbox demonstrates that the lite spinoff is **a packaging change to existing shipped code**, not a new UI design. Open with `?mode=lite` in the URL to auto-enter zen as the default; reload without the param to start in classic.

---

## Spike (v2 — D-v2, rejected by user)

- **Approach attempted:** D-v2 (snap-chip strip + 2 dropdowns + persistent fullscreen pill) — first try after RESHAPE
- **Sandbox file:** `proto/sandbox/invent-focus-mode-lite-spinoff.html` (736 LOC, ~32 KB, standalone — open in browser, no server, no build step)
- **Outcome:** PASS (expected 13/13 in-page assertions GREEN on load; live OS fullscreen behavior depends on browser allowing `requestFullscreen()` from user gesture, normal in Chromium/Firefox/Edge)

### What the v2 spike demonstrates

Builds directly on v1 spike's `body.lite` CSS infrastructure (unchanged). Adds the D-v2 row-level signature elements:

**Menu row in lite (D-v2 layout, 36 px tall):**
```
[📐 BMA-Plan] [File ▾] [Measure ▾] │EP MP CT NL IX —│ ··· [📐 1:100] [P.6/45] [💾 saved] [⛶ Full]
```

- File dropdown: 5 items (Open / Save / Export XLSX / Export PDF / Switch to Full)
- Measure dropdown: **19 measurement tools** grouped by 5 visual divider sections (Scale / Area / Line / Tools / Navigate) — every full-app measurement tool reachable
- 6 snap chips (EP MP CT NL IX —) — green=on, grey=off, click to toggle
- 4 right-side pills (scale state / page / save state / OS fullscreen toggle)

**Full-app chrome (ribbon / panels / status / widget):** all hidden via `body.lite #ribbon, body.lite #left-panel, ... { display:none !important }`

### Assertions (13 total)

**v1 frame criteria (8):**

| # | Criterion | How measured |
|---|---|---|
| C1 | Single-row menu enforced | `#menuBar` height ≤ 44 px; visible dropdowns in lite ≤ 3 |
| C2 | Canvas ≥95% browser viewport (lite) | `canvasH / window.innerHeight * 100` |
| C3 | Mode switch ≤200 ms | `performance.now()` delta around `body.classList.toggle('lite')` |
| C4 | Cross-mode save/load | No `.bmaplan` field added — DOM-only state |
| C5 | Measure flow parity | Measure dropdown contains all measurement actions; counted live |
| C6 | 45-page nav | Ctrl+K palette + bottom-right 180×120 minimap (always visible in lite) |
| C7 | Zero measurement-code duplication | Single HTML file — `polyAreaM2`/`pdfToC`/`snap` would live in same file in real impl |
| C8 | HT-7 scale-gate triggers in lite | Auto-disables `STATE.scaleSet` after 2s; Measure → Polygon triggers blocking toast |

**v2 D-v2-specific assertions (5):**

| # | Criterion | How measured |
|---|---|---|
| D1 | Snap chips visible+toggle in lite within 44 px row | `.snap-chip` count = 6; `getComputedStyle` non-`display:none` in lite; menu height ≤ 44 |
| D2 | Measure dropdown has ≥20 tools | Count `.item:not(.section-label)` inside `[data-menu="measure"]` — assert ≥ 19 |
| D3 | Fullscreen pill works | Pill visible in lite; click calls `document.documentElement.requestFullscreen()`; `fullscreenchange` event toggles label `⛶ Full` ↔ `✕ Exit` |
| D4 | F11 routes to OS fullscreen in lite | Keydown handler: `if (body.lite) { requestFullscreen(); return; }` — bypasses zen-mode fallback |
| P1 | `?mode=lite` URL reader | Auto-enters lite on load if URL param present |

### Verify manually (D-v2)

```
1. Open proto/sandbox/invent-focus-mode-lite-spinoff.html
2. Default = FULL mode (full chrome visible, no snap chips, no fullscreen pill).
3. Press Ctrl+Shift+L → LITE. Confirm:
     - Only menu row (36px) + canvas + minimap (bottom-right HUD)
     - Snap chips visible (EP MP CT green; NL IX — grey)
     - 4 right-side pills (📐 / P.6 / 💾 / ⛶)
4. Click any snap chip → toggles color green↔grey
5. Open Measure dropdown → see 19 tools in 5 groups (Scale/Area/Line/Tools/Navigate)
6. Wait 2s → scale pill turns red (📐 No scale)
7. Click Measure → Polygon Area → red HT-7 toast appears (gate triggered)
8. Click 📐 pill → toast "Scale set: 1:100" + pill turns green
9. Click Measure → Polygon Area → info toast (mock measure mode active)
10. Press Ctrl+K → palette opens; type "38" Enter → minimap highlights cell 38
11. Click ⛶ Full pill (or press F11 in lite) → browser enters OS fullscreen
     - Pill becomes ✕ Exit
     - Canvas now fills the monitor; menu row still 36px on top
12. Press Esc or click ✕ Exit → exits OS fullscreen cleanly
13. Press Ctrl+Shift+L → back to FULL mode
Badge shows 13/13 PASS at every step.
```

### What the v2 spike does NOT prove

- **Real `.bmaplan` round-trip** — sandbox is mock state. Real implementation needs save → reopen → object-list parity check.
- **Real measurement-engine reuse** — sandbox uses mock action handlers. Real impl adds the F11 routing branch in `ui.html` keydown handler and the `body.lite` CSS class; existing `toggleSnap()`, `setMode()`, `activateAreaTool()` etc. are called unchanged.
- **Touch / iPad fullscreen behavior** — iOS Safari has different `requestFullscreen()` semantics; not tested in this spike (out of v2 scope).
- **Snap-chip styling consistency with shipped INV-002 zen-top-bar** — real impl should re-use the same chip CSS class to keep both surfaces consistent.

### Failure modes anticipated for real implementation

1. **CSS cascade leaks** — same as v1: full-mode UI sprints add new chrome that doesn't include a `body.lite` `display:none` rule. Mitigation: lint or new `bma-lite-cascade-guardian` subagent.
2. **F11 routing conflict** — current `toggleZenMode()` is bound to F11 unconditionally. The v2 patch adds a `body.lite` early-return branch; must verify no other F11 listener intercepts before this one.
3. **`requestFullscreen()` user-gesture requirement** — browsers require fullscreen calls to originate from a user-initiated event. F11 keypress and pill click both satisfy this; URL param `?mode=lite` cannot auto-enter OS fullscreen on load.
4. **`fullscreenchange` cleanup** — when user exits OS fullscreen via Esc (browser-native), the page must detect via event and update pill label. Sandbox handles this correctly via `document.addEventListener('fullscreenchange', ...)`.
5. **Discoverability of OS fullscreen** — without onboarding, new users may not know F11 / pill exists. Acceptable for v2 spike; future sprint can add a first-run toast.

---

## Spike (v1 — superseded by RESHAPE, kept for history)

- **Approach attempted:** A (URL-param body-class gate + 3-item static menu) — first try
- **Sandbox file:** `proto/sandbox/invent-focus-mode-lite-spinoff.html` (v1 was 591 LOC — has since been rewritten for v2 D-v2)
- **Outcome (v1):** PASS (10/10 in-page assertions GREEN on load)

### What the spike demonstrates

The sandbox is fully self-validating. On load it renders a mock of the full BMA-Plan chrome (menu bar / ribbon / summary widget / left panel with 45 fake page thumbs / canvas placeholder / right panel with mock layers / status bar with 7 fields). A floating `#spike-badge` runs 10 assertions every time mode toggles or window resizes:

**Frame success criteria (8):**

| # | Criterion | How it's measured |
|---|---|---|
| C1 | Single-row menu enforced | `getBoundingClientRect()` on `#menuBar` → height ≤ 44 px; counts visible dropdowns (≤3) + total dropdown items (≤15) in lite mode |
| C2 | Canvas ≥95% of viewport (lite) | `canvasH / window.innerHeight * 100` — measured live |
| C3 | Mode switch ≤200 ms | `performance.now()` delta around `body.classList.toggle('lite')` with forced layout flush |
| C4 | Cross-mode save/load compat | No `.bmaplan` field added — `body.lite` is DOM-only state, schema untouched → trivially additive |
| C5 | Measure flow parity in lite | File/Measure/View dropdowns expose the full Open→Set Scale→Polygon Area→Export XLSX path |
| C6 | 45-page nav via ⌘K | `Ctrl+K` opens mock palette with fuzzy-filter over 45 pages; Enter loads |
| C7 | Zero measurement-code duplication | Single HTML file; `polyAreaM2`/`pdfToC`/`snap` would live in same file in real impl |
| C8 | HT-7 scale-gate triggers in lite | Sandbox auto-disables `STATE.scaleSet` after 2 s; clicking Measure→Polygon Area shows blocking toast (same `_scaleGateBeforeMode()` call path) |

**Spike-plan bonus (2):**

- P1: `?mode=lite` URL param reader → injects `body.lite` class on `DOMContentLoaded`
- P2: `body.lite` CSS hides `#ribbon`, `#summary-widget`, `#left-panel`, `#right-panel`, `#status-bar` via 5 `display:none !important` rules + grid reflow (`grid-template-rows: 36px 1fr; grid-template-columns: 1fr`)

### Live measurements (in-spike, default 1920×1080 viewport)

- Menu bar height in lite: **36 px** ✓ (limit 44)
- Visible dropdowns in lite: **3** ✓ (File / Measure / View — Edit/Page/Layer/Annotate/Help hidden by `body.lite .menu-item:not(.lite-keep)`)
- Visible item count in lite: **15** ✓ (File 6 / Measure 4 / View 5)
- Canvas height in lite at 1920×1080: ~**1044 px / 1080 px = 96.7%** ✓ (limit 95)
- Toggle latency: typically **0.3–2 ms** ✓ (limit 200) — CSS-class toggle is sub-frame
- HT-7 gate: clicking Polygon Area after 2 s shows red toast within ~50 ms ✓

### How to verify manually

```
1. Open proto/sandbox/invent-focus-mode-lite-spinoff.html in any modern browser (no server needed)
2. Default load = FULL mode. Confirm full chrome visible. Badge shows mode=FULL.
3. Press Ctrl+Shift+L → enters LITE. Confirm:
     - Ribbon / panels / status bar / summary widget all hidden
     - Only menu bar (36px) + canvas visible
     - Three pills on right side of menu bar (scale / page / save)
4. Wait ~2 seconds (auto-disables scale). Pill "📐 No scale" turns red.
5. Click Measure → Polygon Area → red HT-7 toast appears: "Cannot enter Measure — Set Scale first"
6. Click Measure → Set Scale → toast: "Scale set: 1:100"; pill turns green
7. Click Measure → Polygon Area → info toast "(mock) measure mode: poly-area active"
8. Press Ctrl+K → palette opens; type "38" → Enter; jumps to page 38
9. Press Ctrl+Shift+L → back to FULL mode; chrome restored
10. Reload with ?mode=lite in URL → auto-enters LITE on load
Badge in upper-right shows 10/10 PASS at every step.
```

### What the spike does NOT prove

- **Real .bmaplan round-trip** — sandbox uses mock state, not real save/load. Cross-mode compatibility is by construction (no schema field added) but a real implementation must verify with full save→reload→reopen cycle.
- **Real measurement-engine reuse** — sandbox uses mock action handlers, not real `polyAreaM2`. The real impl is trivial because we don't move or duplicate code, but spike doesn't demonstrate it.
- **Real Ctrl+K palette behavior with shipped `_searchIndex`** — sandbox uses naive substring filter, not the shipped Fuse.js index. Real impl just calls existing `openCommandPalette()`.
- **Discoverability** — sandbox does not test whether new users find lite mode. That's a usability study, not a spike.

### Failure modes anticipated for real implementation

1. **CSS cascade leaks** — full-mode UI sprints add new chrome elements; if they don't add `display:none` rules under `body.lite`, lite mode leaks them. Mitigation: a sprint-finalize lint that greps for `id=` or `class=` additions in `#ribbon/#left-panel/#right-panel/#status-bar/#summary-widget` and verifies a corresponding `body.lite` rule exists. Could be a new `bma-lite-cascade-guardian` subagent if it becomes recurring pain.
2. **Modal overlays positioning** — Settings modal, Save As dialog, etc. may have CSS that assumes the chrome height; need a regression check that all modals position correctly with `body.lite`.
3. **First-time discoverability** — users who land on `/` see full mode; no obvious cue that lite exists. May need a one-time "💡 Tip: Press Ctrl+Shift+L for Focus Mode" toast on first session.

## Decision

**Outcome: NOGO** (2026-05-20, after 2 RESHAPE iterations + 3 spike attempts)

### User's NOGO rationale (verbatim, Thai)
> "nogo จะ เขียนแยก ไม่ใช้ ไฟลใน proto แต่ให้ตั้งทุดอย่างเองใน /lite"

Translation: NOGO on this invention pass. User does not want to modify `proto/ui.html` (even with the minimal ~30 LOC v3 delta). The preferred direction is a **completely separate `/lite/` folder** with its own standalone implementation — true sibling of `/proto/`, not a feature flag, not a packaging change, not an extension.

### Why this is a legitimate NOGO (not a failure)

The invention pass converged on the right OUTCOME (`adopt INV-002 zen-top-bar layout`) but on the wrong PACKAGING (`feature-flag inside ui.html`). The user wants to keep `proto/` as the canonical full-app codebase and build the lite face as a fresh tree that re-implements just what it needs. This is a strategic separation that the invent loop did NOT explore — Approach B (separate route + shared engine) was disqualified for forbidden-surface relocation, but a TRULY independent `/lite/` build is different: it would not import from `proto/`, just re-create the parts it needs. Research Section 5 confirmed this pattern exists (Photoshop Express vs Photoshop are different codebases, not feature-flagged).

### What this NOGO closes

- No edit to `proto/ui.html` from this idea
- No new feature flag, no `?mode=lite` URL param in the current app, no `body.lite` CSS class in `proto/`
- The sandbox `proto/sandbox/invent-focus-mode-lite-spinoff.html` stays as reference for the visual design + the lite-default toggle mechanism — useful as a starting point for the `/lite/` build, but NOT to be promoted as-is

### What this NOGO opens (recommended follow-up — needs separate `/idea`)

The user's stated direction implies a NEW idea worth capturing via `/idea`:

> **"BMA-Plan Lite — standalone `/lite/` folder build"**
> Set up a new top-level `/lite/` directory in the repo, separate from `/proto/`. Bring its own HTML, its own minimal FastAPI server (or static-only), its own measurement code (copied/forked from `/proto/`, not imported). Designed to be packaged + distributed independently. The UI face = the INV-002 zen-top-bar layout adopted as default. Maintenance trade-off: code drift between `/proto/` measurement engine and `/lite/` copy — acceptable per the user's explicit preference for total separation over shared-engine.

That idea raises NEW questions the current invent pass did not address:
- Build / packaging shape: PyInstaller separate `.exe`, web-only subdomain, Electron, or all three?
- Code-sharing policy: copy-and-fork measurement engine, OR strict no-share (re-implement from scratch)?
- Version-sync policy: when `proto/` ships a measurement-engine bugfix, how does `/lite/` learn about it?
- `.bmaplan` cross-compatibility guarantee: same hard constraint or relaxed for lite?
- Roadmap relationship: does `/proto/` continue evolving feature-rich, while `/lite/` stays frozen at one minimal feature set?

These are genuinely new questions that would justify a fresh `/idea` capture + `/bma-invent` pass. The current artifact is **not the right document** for that work because its frame, research, and approaches all assumed feature-flag-inside-proto.

### Status flips

- `~/.claude/ideas/IDEAS.md` 2026-05-20-00-12 → `invent-done-nogo`
- `docs/status/PHASE_INDEX.md` Discovered backlog 2026-05-20 row → `invent-done-nogo` (with pointer to this Decision section + recommendation to file a fresh idea for `/lite/` standalone build)
- This artifact stays in `docs/invent/` for future reference
