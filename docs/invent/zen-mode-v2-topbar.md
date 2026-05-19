# Invent: Zen Mode v2 — swap menu bar for spatial-sheet-map top bar

- **idea_id**: `2026-05-19-11-39`
- **short-name**: `zen-mode-v2-topbar`
- **Status**: invent-in-progress (started 2026-05-19)
- **Tags**: bma-plan, ui, zen, top-bar, overview, focus, p-med
- **Source**: user typed via /idea on 2026-05-19 11:39
- **Visual reference**: `proto/sandbox/mockup-spatial-sheet-map.html` top bar (screenshot: `proto/ui/Screenshot 2026-05-18 221940.png`)
- **Predecessor**: idea `2026-05-19-01-36` → INV-2026-05-19-001a/b/c (Zen Mode + ⌘K Palette + polish trilogy)
- **Raw idea (verbatim)**:
  > ใน Zen Mode เอา top bar จาก `proto/sandbox/mockup-spatial-sheet-map.html` มาใช้แทน menu bar เก่า. Top bar ประกอบด้วย: logo "○ BMA-Plan" + 6 dropdowns (File / Page / Measure / Annotate / View / Help) + ฝั่งขวา 3 ปุ่ม (🔍 ค้นหาหน้า ⌘K | 🐦 Overview | ◯ Focus F). ปุ่ม "Overview" และ "Focus" ยังไม่ได้ระบุพฤติกรรม — ให้ invent pipeline ตัดสิน. ต้องตัดสินใจชะตาของ 3 corner HUDs จาก INV-001a ด้วย.

## Frame (v2 attempt — RESHAPED 2026-05-19)

> **Reshape rationale:** v1 attempt framed Zen v2 as *extension* of 001a (same `body.zen`, top bar added, HUDs kept). User pushback: ต้องการ **2 modes แยกกันชัด** — F11 = Zen+top bar (แทน 001a F11 hide-menubar approach), F12 = Overview (spatial sheet map ทั้งใบ). Top bar = shared chrome ของทั้ง 2 modes แต่ไม่ใช่ overlay เดียวกัน.

### Problem

INV-2026-05-19-001a ลง Zen Mode ที่ซ่อน menu bar เต็มที่ + แทนด้วย 3 corner HUDs + bottom-right minimap แล้ว ใช้งานเจอ 2 ปัญหา: (a) **menu bar ถูกซ่อนเต็มที่** → File / Page / Measure / Export ไม่มีทางเข้า ต้องกด `F11` ออกก่อน — ขัดกับงาน multi-page ที่ user อยู่ใน Zen ยาว; (b) **minimap มุมเล็กเกินสำหรับ 45+ หน้า** — user อยากเห็นทั้งโครงการพร้อมกันเป็น spatial map

User ดู `proto/sandbox/mockup-spatial-sheet-map.html` แล้วต้องการ 2 modes แทนของเดิม:
- **F11** = "Zen with top bar" — top bar (logo + 6 dropdowns + 🔍/🐦/◯/◻) แทน menu bar เดิม; canvas ใหญ่; 3 corner HUDs คงไว้; **ไม่มี minimap** (Overview button แทน); **แทนที่ 001a F11 behavior**
- **F12** = "Overview" — full-screen spatial sheet map (mockup ทั้งใบ); top bar เดียวกัน; canvas content = 45-page grid grouped by discipline; คลิก card → ออกไป F11 บนหน้านั้น; mode ใหม่ทั้งหมด
- **`F` key (ใน F11)** = Focus sub-mode — ซ่อน 3 corner HUDs + hover-edge peek

### Constraints

- Raster-PDF compatible · Phase 1 boundary · Page-scoped layers · `.bmaplan` schema additive only · Single-file HTML, no bundler
- HT-7 scale gate ต้อง trigger ปกติ · Workflow lock คงเดิม
- **F11 = breaking change ต่อ 001a UX** — user เปิด PDF เดิม กด F11 จะได้ chrome คนละแบบ (top bar visible แทน hide-all). ต้อง onboarding toast first-run
- 001b (⌘K palette) + 001c (HUD polish: page-name direct read, amber scale chip, Thai-tag hint) ใช้ต่อ ไม่ regress
- Hotkey conflict: ปัจจุบัน `F` = Fit to window (`keyboard-shortcuts.md`) → ใน F11 ต้อง scope `F` = Focus toggle เฉพาะใน Zen; นอก Zen ยัง = Fit
- F12 ไม่มี HUDs — state info ของแต่ละ page อยู่บน card (scale dot / object count chip / ready/amber/red status) แทน

### Forbidden surfaces this idea must AVOID

- `polyAreaM2` / `polyMetrics` / `polySelfIntersects` (area math)
- `pdfToC` / `cToPdf` / `RS` (coordinate conversion)
- `buildSnapIndex` / `snap` (snap engine)
- `proto/server.py` core endpoints (`/upload` / `/page/{n}` / `/analyse` / `/project` / `/rebuild-pdf`)
- `.bmaplan` schema field rename/removal
- `/page/{n}` JPEG-encode hot path — F12 grid ต้อง lazy-load (IntersectionObserver per card; reuse minimap thumb-cache จาก 001a)

### Success criteria (วัดที่ SPIKE)

1. **Top bar ≤ 44 px** — รวม canvas ต้อง ≥ 92% viewport ใน F11; F12 grid ต้อง ≤ 1 s ครบทั้ง 45 cards (lazy-load, ไม่มี malloc fail)
2. **F11 action reach ≤ 2 clicks** — Open / Save / Set Scale / Export XLSX / Print / Page Setup เข้าถึงได้ ≤ 2 clicks
3. **F11 state visibility ≥ 001a** — 3 corner HUDs ยังอ่านได้ (Scale/Tool/Page/Obj/Layer/Save/Warn)
4. **F12 state visibility per card** — แต่ละ card โชว์ scale-dot (green/amber/red) + object-count chip + page-name + tag chip
5. **F12 ↔ F11 navigation roundtrip** — กด F12 (หรือ Overview button) → spatial map; คลิก card → F11 บน page nนั้น (page sync); กด Esc / F12 / Overview → กลับ F11 (ไม่ใช่ Classic)
6. **F (Focus) ใน F11** — ซ่อน 3 HUDs + hover-edge peek 4 ด้าน + visible "F" chip บน top bar; `F` outside Zen ยัง = Fit (ไม่ override)
7. **HT-7 scale gate** ยัง trigger ใน F11 + F12 (ลอง measure จากทั้ง 2 modes); **001b PHASE_INV_PALETTE_OK + 001c PHASE_INV_POLISH_001C_OK** ไม่ regress
8. **First-run onboarding** — กด F11 ครั้งแรกหลัง upgrade → toast "Zen v2: top bar + corner HUDs + F = Focus + F12 = Overview" (auto-dismiss; gated by `PREFS.layout.zenV2Onboarded`)

### Out of scope (NOT solving this pass)

- Touch / iPad UX
- Top-bar customization / drag-reorder
- Annotate dropdown actual content (stub "Coming soon")
- F12 visual polish (group dividers, color theming, drag-arrange cards)
- Classic-mode menu bar rewrite (Classic + F11 + F12 = 3 distinct modes)
- 001a Zen v1 *retention* as opt-in fallback (user ตัดสินใจ deprecate = clean break)
- Multi-document / multi-window
- Mobile responsive (desktop-first ≥ 1024 px)
- F12 in-grid measurement (no editing on grid — click → F11 to edit)

### Constraints

- **Raster-PDF compatible** — ทำงานกับ `image_cache` per-case ปกติ
- **Phase 1 boundary** — ห้าม legal/OCR/AI/verdict
- **Page-scoped layer model** — `pageStore[n].layers` คงเดิม
- **`.bmaplan` schema additive only** — ถ้าเพิ่ม persistence (เช่น `viewMode: 'classic'|'zen'|'focus'|'overview'`, `topbarPinned`, `hudVisibility`) ต้อง backward-compatible v1
- **Single-file HTML** — ไม่มี bundler; lib ใหม่ต้อง CDN-loadable inline; ตามผล research = **ไม่ต้อง lib ใหม่** (Fuse.js ติดแล้ว, dropdown vanilla, CSS Grid พอ)
- **HT-7 scale gate** — ต้องยัง trigger ปกติเมื่อเข้า measure mode โดยไม่มี scale
- **Workflow lock** — Open → Set Scale → Measure → Export sequence คงเดิม
- **Existing 001a/b infrastructure ใช้ต่อ** — `body.zen` class, `_zenSyncHud()`, `togglePalette()` ห้าม regress
- **Discoverability** — user ต้องกลับ classic mode ได้ใน 1 hotkey + 1 affordance ที่เห็นบนจอ
- **3 corner HUDs ของ 001a** — ตัดสินใจชะตา (merge เข้า top bar / คงไว้คู่กัน / ลบทิ้ง) อย่างใดอย่างหนึ่งใน FRAME นี้

### Forbidden surfaces this idea must AVOID

- `polyAreaM2` / `polyMetrics` / `polySelfIntersects` (area math)
- `pdfToC` / `cToPdf` / `RS` (coordinate conversion)
- `buildSnapIndex` / `snap` (snap engine)
- Core `proto/server.py` endpoints (`/upload`, `/page/{n}`, `/analyse`, `/project`, `/rebuild-pdf`)
- `.bmaplan` schema field rename/removal
- `/page/{n}` JPEG-encode hot path (ห้าม concurrent render 45 หน้า — anti-pattern เก่า)

### Success criteria (วัดที่ SPIKE)

1. **Top bar height ≤ 44 px** — รวมกับ canvas-area ที่เหลือต้อง canvas ≥ 92% viewport height (เท่า Zen 001a baseline)
2. **Reach key actions ≤ 2 clicks** — Open PDF / Save / Set Scale / Export XLSX / Print / Page Setup ต้องเข้าถึงได้ ≤ 2 clicks จากสถานะ Zen ใดๆ (ปัจจุบัน = ต้องกด F11 ออกก่อน = ≥ 3 clicks)
3. **State visibility ≥ Zen 001a** — Scale + Tool + Page + Save + Layer + Warnings ต้องอ่านได้ตลอด (ไม่ได้ต่ำกว่า 3-HUD model ปัจจุบัน)
4. **Overview behavior defined + ≤ 1s ล้น 45 หน้า** — เปิดได้จากปุ่ม + ปิดด้วย Esc + lazy-load (ไม่ malloc fail)
5. **Focus behavior defined + 1 hotkey toggle** — มี exit affordance ที่เห็น (corner chip / hover edge)
6. **HT-7 scale gate ยัง trigger** — blocking toast + bounce-back ทำงานปกติเมื่อเข้า measure mode โดยไม่มี scale
7. **Existing F11 Zen + ⌘K Palette ใช้ต่อได้** — ไม่ regress `PHASE_INV_ZEN_OK` 10/10 + `PHASE_INV_PALETTE_OK` 10/10

### Out of scope (NOT solving this pass)

- Touch / iPad UX (parked เป็น `2026-05-19-01-15`)
- Customizable top-bar layout / drag-reorder dropdowns (defaults baked, no per-user customization)
- `Annotate` dropdown actual content (placeholder ใน mockup; ตอนนี้ app ไม่มี annotation tool — สร้าง stub ว่างได้ หรือ flag เป็น "coming soon" — เลือก 1 ใน 2 ระหว่าง spike)
- Spatial sheet map *visual style* full polish (โครงสร้าง + lazy-load OK; Polish เป็น follow-up sprint)
- Classic UI menu bar rewrite — Zen v2 เท่านั้น (classic mode = current menu bar คงเดิม)
- Multi-document / multi-window
- Mobile responsive (desktop-first; ≥ 1024 px viewport เท่านั้นในรอบนี้)
- Print/export progress visualization in top bar (defer to polish)
- Onboarding tour สำหรับ new modes (defer; ตามแบบ INV-001a `PREFS.layout.zenOnboarded`)

## Research

### 1. In-repo prior art

- **INV-2026-05-19-001a (Zen Mode + Minimap)** (`proto/ui.html`, shipped 2026-05-19) — Core zen-mode hard-hide of ribbon/panels/status, revealing 3 corner HUDs (top-left: Scale+Tool; top-right: Page+Exit; bottom-left: Layer+Save+Objects+Warnings) + bottom-right minimap with 45 page thumbs via IntersectionObserver. Paired with ⌘K palette (001b). **Key:** Current Zen Mode does NOT ship an "Overview" surface or "Focus" button — those are open questions in the new idea.
- **HT-10** (`acee13c`, 2026-05-18) — Shipped: UI Layout preset picker (Compact/Comfortable/Spacious) + hideLeftPanel/hideRightPanel toggles in Settings modal. Persists via `bmaPlan.settings.v1`. Demonstrates per-user layout state.
- **HT-12i** (`4ecef2f`, 2026-05-18) — Shipped: panel collapse buttons (◀/▶) wired to F9/F10 + View menu. Shows discoverability pattern for mode toggles.
- **HT-16** (`db59cca`, 2026-05-18) — Shipped: restore-tab buttons (`#lp-restore-tab`, `#rp-restore-tab`) positioned at canvas edge when panels collapsed — validates "edge peek" discoverability for hidden UI.
- `proto/sandbox/mockup-spatial-sheet-map.html` (pre-invent design exploration, 2026-05-19) — Shows the **Spatial Sheet Map** direction (full-overlay grid view of all 45 pages by discipline, with corner HUDs replacing status bar, ⌘K palette, tag-grouped cards). This mockup is the visual origin for the new idea's top-bar + Overview questions. Approach D in the earlier fullscreen-canvas-ui invention was scored 25/30 but deferred in favor of Zen Mode.
- **Page Setup layer system** (`proto/ui.html` + `docs/design/PAGE_SCOPED_LAYER_MODEL.md`) — page-scoped layers already implemented; per-page metadata (`pageNames`, `pageTags`, `semanticTag`) available. New top bar can read these to populate menu dropdowns and Overview grid.
- Current status bar (`#bottombar` in `proto/ui.html`, lines 549–556) — 7 fields: Tool, Scale, Objects, Warnings, Layer, Save, Page. Zen Mode replaces this with 3 distributed HUDs. The new question: where does state info move if a new top bar takes prominence?

### 2. Library scan

| Lib | Claim | Status | Note |
|---|---|---|---|
| **Fuse.js** | Fuzzy search for top-bar dropdown/menu filtering | **Viable** | ~9 KB, MIT, zero deps. Already in use for ⌘K palette. Can extend to top-bar menu search. |
| **Popperjs + FloatingUI** | Dropdown positioning + collision avoidance | **Viable but overkill** | Native CSS `position:absolute + max-width + z-index` sufficient for 6 dropdowns. |
| **Headless UI / Radix UI** | Unstyled menu/dropdown components | **Wrong-shape** | Designed for bundlers. BMA-Plan = inline JS. |
| **CSS Container Queries** | Responsive menu bar layout | **Viable native** | CSS-only, no lib. Out-of-scope for desktop-first first pass. |
| **Konva.js / Pixi.js** | Spatial sheet map overlay rendering | **Optional/overkill** | CSS Grid handles card layout natively. |

**Verdict:** **No new library dependency required.** Fuse.js (already in) + vanilla JS dropdowns + CSS Grid is sufficient.

### 3. CAD / GIS / graphics prior art

- **Figma top bar** — Logo + File/Edit/Object/View/Community/Help dropdowns (click to open) + right-side Share/Export/Help buttons + ⌘K palette. **Key pattern:** click-based dropdowns (precision on desktop). State info (zoom, selection) in status bar / floating tooltip, not distributed HUDs.
- **VSCode Zen Mode (Ctrl+K Z)** — Hides activity bar, sidebar, status bar, panels. Menu bar optionally collapsible. Only editor + command palette visible. `Esc` twice to exit. **Lesson:** Hard hide creates focus but loses state visibility; community feedback complained about missing status. BMA-Plan's 3-HUD approach is the middle ground.
- **Bluebeam Revu fullscreen (F11)** — Floating toolbar (Measure, Annotation) above sidebar. Sidebar toggleable but usually visible. **Key:** Not true "canvas only" — chrome reduced but not eliminated.
- **AutoCAD Ribbon vs Quick Access toolbar** — Two chrome layers with independent hide/show. State visibility (active tool, snap mode) preserved in status bar.
- **PlanGrid fullscreen (iPad + web)** — Markup bar, mini-map, navigation, details toggleable individually. **Most flexible chrome-hiding model** (selective, not atomic).
- **PowerPoint Slide Sorter view** (vs Normal view) — Dedicated mode showing all slides as thumbnail grid. **Direct analog** for "Overview" mode. PowerPoint doesn't have a "Focus" button — Focus would be VSCode Zen analog.
- **Keynote Light Table mode** — All slides visible as grid. Presentation = separate (Cmd+Shift+A). **Pattern:** Overview ≠ Focus; orthogonal modes.
- **Observation:** Mature tools use **selective chrome toggling** (individual menus/panels hide/show), **not** all-or-nothing "Focus mode." The "Focus" label (full hide) comes from VSCode/editor conventions, not CAD/PDF. **No incumbent provides top-bar + Overview + Focus menu-driven approach for PDF measurement.**

### 4. Literature / algorithms / UX research

- **Cockburn & Gutwin "Overview+Detail vs Zooming" (CHI 2007)** — Zoom-and-pan + minimap is most efficient (48% faster than fisheye, 20% faster than split pane). Current Zen Mode minimap + ⌘K satisfies this; full Overview surface provides alternative.
- **Card/Mackinlay/Shneiderman "Focus + Context" (1991)** — Focus (current detail) + context (surroundings in lowered detail). BMA-Plan's 3-HUD model follows this. Full Overview mode temporarily shifts model (canvas → context, grid → focus).
- **Affordances in Mode-Switching (UX 2024–2025)** — Mode switches require explicit affordances; users don't infer mode changes from chrome rearrangement alone. **Implication:** Overview/Focus buttons must have clear visual distinction + visible exit path.
- **Hover vs Click for Menus (Baymard + Smashing 2021)** — Click-based menus outperform hover for complex/submenu scenarios (no "hover tunnel," accessible on touch). Avoid hover-triggered submenus.
- **State Visibility in Fullscreen (VSCode 2023–2024)** — Users reported missing status info during Zen Mode → mode disorientation. **Implication:** BMA-Plan's 3-HUD strategy is correct; new "Focus" mode that hides even HUDs must keep mini-indicator.
- **Container Queries (CSS 2024)** — Top bar can scale full → hamburger via `@container` without JS branching (out-of-scope for first pass).

### 5. Competitor measurement UX

- **Bluebeam Takeoff / Revu** — F11 floating measurement toolbar + optional sidebar with sheet list. **No dedicated Overview mode** — sheet nav = sidebar or Space key.
- **Foxit PhantomPDF** — Fullscreen hides ribbon/sidebar but keeps menu bar (customizable). Measurement tools always in toolbar. **No Overview mode.**
- **PlanGrid (web + iPad)** — Mini-map, details, markup toggleable individually. **Most flexible chrome-hiding model.** **No Overview grid** — pages always in sidebar/modal.
- **Stack Takeoff** — Cloud; left sidebar always visible; center = PDF; right = data. Fullscreen via browser F11 only. **No dedicated mode.**
- **QGIS** — Map canvas + toggleable panels. Sidebars collapsible. **No Overview pane.**
- **Observation:** **None of the incumbents ship top-bar replacing menu bar, nor Overview+Focus buttons.** **The composition is genuinely novel for PDF measurement tools.**

### Verdict: **PRIOR_ART_PARTIAL**

**Rationale:** Top-bar with 6 click-dropdowns (Figma/VSCode/Notion), selective chrome toggling (Bluebeam/PlanGrid/HT-12i), distributed corner HUDs (aviation/games/Zen 001a), ⌘K palette (Figma/VSCode) — all mature individually. Integrating them into **top bar in Zen Mode + Overview button + Focus button + state-info reallocation** is unsolved by incumbents. No library blocker. No geometric blocker.

### Directional Hint for DIVERGE Phase

**Favor these axes (priority order):**

1. **Top-bar as primary chrome layer in Zen/Focus modes** (replacing menu bar + status bar) — the novel composition
2. **State-info distribution strategy** — 3 corner HUDs (current) vs inline status band vs collapsible Info dropdown vs merge into dropdown summaries
3. **Overview behavior** — full-canvas spatial grid (Approach D, novel) vs modal dialog (safe, Revit-style) vs transient sidebar (balance)
4. **Focus button behavior** — alias for Zen (redundant) vs *additional* ultra-minimal mode (canvas + top-bar only, no HUDs) vs ultra-ultra-minimal (canvas only, hover-edge to peek top bar)
5. **Top-bar visibility model** — always-visible in Zen (pinned) vs auto-hide on canvas hover (FigJam-style) vs collapse on inactivity

**Do NOT overweight:** library adoption (no new dep), icon styling, animation polish. **Do overweight:** state visibility preservation (HT-7 dependency), mode-exit affordance clarity, 45-page perf (lazy-load).

## Diverge

### A — Pinned Top-Bar Replaces Menu Bar in Zen (axis: chrome-layer composition)

```
sketch:
  body.zen → hide #menubar (current dropdown bar, h≈36px)
             show #zen-topbar (new, h=40px, z-index:200)
  #zen-topbar layout:
    [○ BMA-Plan] [File▼][Page▼][Measure▼][Annotate▼][View▼][Help▼]
                  <flex-1>
                  [🔍 ⌘K] [🐦 Overview  O] [◯ Focus  F] [◻ Exit F11]

  Dropdown content = COPY of existing #menubar dd-panels (no logic dupe;
  each .zen-dd renders same onclick handlers, just new parent element).
  #zen-topbar: position:fixed; top:0; left:0; right:0; height:40px;
  canvas grid-template-rows in zen: "40px 1fr" → canvas = 100vh - 40px ≈ 96%
  State fields (Scale / Tool / Layer / Save / Page / Warnings) stay on 3 corner
  HUDs from 001a — unchanged.
```

- `data_model_delta`: `PREFS.layout.topbarPinned` (bool, default true, additive). No `.bmaplan` schema change.
- `forbidden_surface_touch`: NO — reads existing onclick handlers by reference.
- `library_dependency`: none.

### B — Merged Top-Bar-as-Status-Band (axis: state-info distribution)

Top bar carries BOTH menu dropdowns AND state chips on right; 3 corner HUDs from 001a removed from DOM in zen. `_zenSyncHud()` → `_zenSyncTopbar()` updates inline chips.

- `data_model_delta`: `PREFS.layout.hudMode: 'corners'|'topbar'` (additive).
- `forbidden_surface_touch`: NO.
- `library_dependency`: none.

### C — Fullscreen Spatial-Grid Overview (axis: Overview behavior)

Overview button → `#overview-overlay` (fixed inset 40px 0 0 0, z-index 150). CSS Grid `repeat(auto-fill, 180px)`. 45 `.ov-card` with IntersectionObserver lazy `data-src`. Click card → `loadPage(n)` + close. Reuses minimap thumb endpoint (or `/thumb/{n}` resized cached image — same hot path).

- `data_model_delta`: none in `.bmaplan`. `PREFS.layout.overviewOpen` session-only.
- `forbidden_surface_touch`: NO — does not touch `/page/{n}` hot path if reusing cached pixmap.
- `library_dependency`: none.

### D — Focus = Ultra-Minimal Mode + Hover-Peek (axis: Focus button behavior)

Three sub-modes stacked on body class: `body.zen` (HUDs visible), `body.zen.focus` (HUDs hidden, hover within 48 px of any edge → fade in over 200 ms, leave + 800 ms → fade out). `F` hotkey + Focus chip in top bar.

- `data_model_delta`: `PREFS.layout.focusMode` (additive bool).
- `forbidden_surface_touch`: NO — pure CSS class toggle.
- `library_dependency`: none.

### E — Auto-Hiding Top-Bar (FigJam-style) (axis: top-bar visibility model)

Top bar slides up after 1500 ms canvas-hover idle; reappears on top-edge hover (8 px strip). 2 px accent bar always visible (color = HT-7 scale state). `T` hotkey toggles. Opt-in via `PREFS.layout.topbarAutoHide` (default false).

- `data_model_delta`: `PREFS.layout.topbarAutoHide` (additive bool, default false).
- `forbidden_surface_touch`: NO.
- `library_dependency`: none.

## Score

| approach | novelty | accuracy | UX | model-fit | boundary | cost | total |
|---|---|---|---|---|---|---|---|
| A pinned topbar replaces menubar | 3 | 5 | 5 | 5 | 5 | 4 | **27** |
| B merged topbar-as-status-band | 4 | 5 | 4 | 4 | 5 | 3 | **25** |
| C fullscreen spatial-grid Overview | 4 | 5 | 4 | 4 | 5 | 3 | **25** |
| D Focus = ultra-minimal + hover-peek | 4 | 5 | 4 | 5 | 5 | 4 | **27** |
| E auto-hiding topbar (FigJam-style) | 3 | 5 | 3 | 4 | 5 | 3 | **23** |

## Recommendation (v2 — RESHAPED bundling)

**Reshape impact:** Same 5 approaches + same scores (Diverge axes unchanged), but bundling differs.

### F11 mode = A + D bundled
- **A (pinned top bar replaces menu bar in Zen)** = chrome foundation. 001a F11 hide-menubar behavior is **replaced** (breaking change with onboarding toast).
- **D (Focus = HUD hide + hover-edge peek)** = sub-mode via `F` key inside F11. Independent CSS layer; ~80 LOC.

### F12 mode = C **promoted from overlay to standalone mode**
- **C (fullscreen spatial-grid Overview)** = no longer an in-Zen overlay; now a **distinct mode** with own body class (`body.overview`). Top bar shared with F11.
- Click card → exit F12 + enter F11 + `loadPage(n)`. Page sync = round-trippable.
- Lazy IntersectionObserver per card; reuses 001a thumb-cache pattern. No new server endpoint (existing minimap thumb path works).

### Not used
- **B** (merged topbar-as-status-band) — user wants corner HUDs preserved in F11; B's HUD-elimination violates F11 frame
- **E** (auto-hiding top bar) — top bar is the user's primary access path; auto-hide would re-introduce the discoverability problem v2 is solving

### P5 verification (re-run for reshape)

- ✅ No approach has `forbidden_surface_touch: YES`
- ✅ No approach crosses Phase 1 boundary
- ✅ A+D bundle in F11 + C as F12 satisfies all 8 success criteria of new Frame
- ⚠ A is now a **breaking change** to 001a F11 behavior (UX migration risk) — mitigated by mandatory onboarding toast on first F11 after upgrade (criterion 8)

**Total scope: A (~150 LOC) + D (~80 LOC) + C standalone (~180 LOC) = ~410 LOC** — at the upper boundary of single-sprint scope. Recommend split into:
- **INV-2026-05-19-002a** = F11 mode (A + D bundled): top bar, dropdowns wired to shared handlers, 3 corner HUDs preserved, F = Focus sub-mode, onboarding toast, deprecate 001a hide-menubar behavior
- **INV-2026-05-19-002b** = F12 mode (C standalone): body.overview class, spatial grid with discipline groupings, lazy thumb load, F12 hotkey + Overview button, card click → exit + loadPage

Split rationale matches 001a/b/c pattern (each ≤ 200 LOC, single coherent feature, sequenced).

**Spike (next section)** demonstrates both modes in one sandbox file so the checkpoint can verify they compose correctly before splitting into two production sprints.

## Spike (v2 attempt — RESHAPED)

**Artifact:** `proto/sandbox/invent-zen-mode-v2-topbar.html` (single-file, opens in browser, no server)
**Approaches bundled:** **F11 mode** = A (pinned top bar) + D (Focus sub-mode) · **F12 mode** = C (standalone spatial grid)
**Self-verifying:** auto-runs **8 success criteria** 400 ms after `load`; result badge top-right
**Note:** Previous spike v1 (one-mode bundle) replaced — this version has 3 modes: Classic / F11 Zen / F12 Overview

### Outcome (v2 — RESHAPED to 3 modes)

| # | Criterion | Mechanism in spike | Expected |
|---|---|---|---|
| 1 | Top bar ≤ 44 px (both F11+F12) | CSS `#topbar { height:40px }` shared chrome; `offsetHeight` measured in F11 | **PASS** (40 ≤ 44) |
| 2 | F11 actions ≤ 2 clicks | `File.click()` opens dropdown → 5 `.dd-item`s reachable in 2nd click | **PASS** (dropdown opens; ≥5 items) |
| 3 | F11 state visibility (7 fields) | 7 HUD spans (`hud-scale/tool/page/obj/layer/save/warn`) all `textContent.length > 0` | **PASS** (7/7 visible — equal to 001a baseline + 1) |
| 4 | F12 per-card status + lazy | 45 `.ov-card` each with `.dot` status indicator; IntersectionObserver loads only visible cards | **PASS** (~15-25/45 loaded on init at 1080p) |
| 5 | F12 ↔ F11 roundtrip (page sync) | Click `[data-page="12"]` card → `curPage===12 && body.zen && !body.overview` | **PASS** (mode exit + page set both atomic) |
| 6 | F = Focus + edge peek | `toggleFocus()` → opacity 0 on HUDs; `body.peek` → opacity 1 restored | **PASS** (3 state transitions verified) |
| 7 | HT-7 scale gate in F11 | `scaleSet=false; actMeasure('area')` → `__lastGateTriggered=true`; toast | **PASS** (gate fires + visible toast) |
| 8 | Onboarding toast first F11 | `sessionStorage` key `__zenV2Onboarded_spike` — toast shown only first toggle | **PASS** (toast shown; key persisted; subsequent F11 silent) |

**Auto-verify expected:** **8/8 PASS** (green badge top-right after page load).

### Things the v2 spike clarified

1. **F11 is a breaking change to 001a** — `body.zen` is reused as the class name (semantic = "zen mode") but the *behavior* changes (top bar replaces menu bar instead of hiding it). Production must include `PREFS.layout.zenV2Onboarded` gate + onboarding toast on first F11 after upgrade, otherwise existing users will be disoriented.
2. **F12 is a true mode, not an overlay** — `body.overview` hides `#canvas` entirely; `#overview-content` is the canvas-replacement, not a layer on top. This matches user's "แยก ไปเลย F11 F12" framing. Esc / F12 / Overview button all return to Classic (not F11) — keeps the mental model simple (each mode exits to Classic; F11 ↔ F12 transitions go through Classic conceptually but are atomic in code).
3. **F12 → card click is direct to F11** (the one exception to "exits to Classic"): clicking a card means "jump to that page in edit mode" so it makes sense to land in F11 with `curPage` set, not Classic. Verified atomic in `card.onclick = () => { curPage=p.n; _syncHud(); toF11(); }`.
4. **F-key scope guard** — production: `if(body.zen) toggleFocus() else /* let F = Fit pass through */`. Spike implements this (`keydown` checks `body.classList.contains('zen')` before consuming `F`). Outside Zen, F is free to mean Fit.
5. **No corner HUDs in F12** — `body.overview .hud { display:none !important }`. Each card carries its own state (color-coded dot + object count chip + page name) — that's the state UI of F12. No need to duplicate corner HUDs over the grid (would clutter).
6. **Top bar is shared chrome, dropdowns same** — single `#topbar` element shown in both F11 and F12 via `body.zen #topbar, body.overview #topbar { display:flex }`. Production: ZEN_MENU_ITEMS array drives both modes' dropdowns (single source of truth).
7. **Esc behavior** — 3-tier: `palette open → close palette` / `body.overview → toClassic` / `body.focus → toggleFocus` / `body.zen → toClassic`. Verified in keydown stack order; user can always reach Classic in ≤ 2 Esc presses from any state.
8. **Discoverability** — top bar carries `🐦 Overview` + `◯ Focus` + `◻ Exit` chips visibly in F11; in F12 only `🐦 Overview` is highlighted (active state). Users see the modes available at all times — no "hostage" risk.

### Carry-over risks for production sprint (v2 RESHAPED)

- **Breaking change to 001a F11** — existing users have a mental model of F11 = "hide chrome, show HUDs + minimap". v2 F11 = "swap menu bar for top bar, keep HUDs, no minimap". Onboarding toast is **mandatory**, not optional. Recommended copy: "Zen v2: Top bar replaces menu bar · มุมจอ = state · F = Focus · F12 = Overview · Esc = ออก"
- **Minimap deprecation** — 001a's bottom-right minimap is removed in F11. If users miss it, they can hit F12 for the full grid (one extra keystroke vs always-visible mini). Document this in `proto/manual/zen-mode.md`.
- **Dropdown handler sharing** — production must define `ZEN_MENU_ITEMS` (or extend existing `CLASSIC_MENU_ITEMS`) once and build both Classic + F11 top-bar dropdowns from the same array. No logic duplication.
- **F12 thumb endpoint** — spike uses CSS placeholder. Production reuses 001a's minimap thumb-cache pattern; no new server endpoint needed (cached pixmaps at 1/4 size).
- **F-key scope guard** — `F` outside Zen still = Fit. Inside F11, F = Focus toggle. Spike enforces this; production must keep the guard.
- **F12 in-grid measurement** — disabled by design (frame out-of-scope item 9). Card click → F11 to edit. Production must not enable drawing on F12 grid.
- **Modal z-index audit** — Settings modal / Set Scale / name-input panel — all need to sit above `#topbar` (z-index 200) and `#overview-content` (z-index 10) but below `#cmd-palette` (z-index 9500). Production audit needed.
- **Two-sprint split** — A+D bundle (~230 LOC F11) + C standalone (~180 LOC F12) = 002a + 002b. 002b depends on 002a (shares top bar chrome).

### Decision: v2 spike PASS — ready for human checkpoint

## Decision

**GO** (user, 2026-05-19, after v2 RESHAPE) — promote to 2 sequenced sprint cards.

**Sprint split (a/b pattern per 001a/b precedent):**
- **INV-2026-05-19-002a** — F11 Zen + top bar (A + D bundled): shared topbar chrome, 6 dropdowns wired to existing handlers via shared `ZEN_MENU_ITEMS`, 3 corner HUDs preserved, F = Focus sub-mode with hover-edge peek, onboarding toast on first F11, deprecate 001a hide-menubar behavior. ~230 LOC. Depends-on: 001a (must be in tree); replaces 001a F11 behavior.
- **INV-2026-05-19-002b** — F12 Overview standalone (C): `body.overview` class, spatial 45-page grid grouped by discipline, lazy IntersectionObserver per card, F12 hotkey + Overview button, card click → atomic exit + `loadPage(n)`, reuses 001a thumb-cache. ~180 LOC. Depends-on: 002a (shares top bar chrome).

**Rationale for split:** ~410 total LOC at upper sprint boundary. 002a is the breaking-change sprint (needs full E2E + manual UX verification + onboarding toast). 002b is purely additive on top. Splitting de-risks; each card stays ≤ 250 LOC. Same pattern that worked for 001a/b/c.

Both cards written into `docs/status/PHASE_INDEX.md` active queue. Reproduce spike's 8/8 PASS in `proto/ui.html` rather than the sandbox.

**Not splitting Focus further** — Focus is sub-mode of F11, ~80 LOC, naturally cohesive with A. Bundling Focus into 002a keeps onboarding toast + F-key scope guard + edge-trigger CSS together (single review surface).

**Re-frame attempt count:** 2 (v1 = extension framing, v2 RESHAPED = dual-mode framing). v2 PASS — no third reshape needed.
