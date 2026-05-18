# Invent — User-configurable settings / preferences panel

**Idea source:** `~/.claude/ideas/IDEAS.md` @ 2026-05-15 18:26 (via PHASE_INDEX.md Discovered backlog)
**Backlog entry:** `docs/status/PHASE_INDEX.md` → ideas 2026-05-15
**Short-name:** `settings-panel`
**Started:** 2026-05-15
**Status:** invent-in-progress

## Summary

A user-facing Settings/Preferences UI to customize BMA-Plan defaults — snap rules, scale defaults, default layer, export format, UI layout presets. Today some preferences are partially live as scattered localStorage keys (`bmaPlan.uiLayoutOptions.v1`, `bmaPlan.widgetPlacement.v1`, `bmaPlan.recentProjects.v1`) with no surface to inspect or change them. The invention question is **what architecture** to give the settings layer (one modal vs left-panel tab vs Mockup-V3-style preset switcher), **what surface area** to cover in v1, and **where to persist** (localStorage / `.bmaplan` per-project / both).

## Frame

### Problem
Today BMA-Plan customisation is fragmented: UI Layout Options + Widget Placement live as separate top-bar modals; snap threshold, default measurement tool, default scale unit, and export column choice have NO surface and are baked into code or set per-action. A real user who prefers (a) snap=midpoint+endpoint only, (b) default unit=ตร.ม. (not ตร.ฟต.), (c) default tool=polygon (not rect) must re-set those every session and per page, or accept the hard-coded default. The invention question is the **architecture, surface area, and persistence model** of a unified preferences layer that absorbs the existing two modals AND extends to the new content areas — without breaking either existing localStorage key or the v1 `.bmaplan` schema.

### Constraints (non-negotiable)
- **Phase 1 boundary.** No legal verdict, no OCR, no AI, no FAR/OSR rule check.
- **Forbidden surfaces.** Cannot edit `polyAreaM2`, `polyMetrics`, `polySelfIntersects`, `pdfToC`, `cToPdf`, `RS`, `buildSnapIndex`, `snap`, `.bmaplan` schema (additive optional fields are OK, renaming/removing breaks user saves). Server endpoints in `proto/server.py` likely untouched — settings are a pure client concern.
- **Backward compatibility.** Existing keys MUST keep working: `bmaPlan.uiLayoutOptions.v1`, `bmaPlan.widgetPlacement.v1`, `bmaPlan.recentProjects.v1`. A user opening v(N+1) BMA-Plan must not lose their saved layout / widget state. A `.bmaplan` saved before this feature must keep loading unchanged.
- **Single-file inline JS.** No bundler, no NPM at runtime. Any helper code goes inline in `proto/ui.html` next to the existing two modals' helpers.
- **Thai-first labels.** All visible strings in Thai (matches existing app surface).
- **Page-scoped layer model.** Any "default layer" preference must respect that `layer.id` is per-page; the preference is by name/role, not by id.
- **Schema additive only.** If we ever embed per-project prefs, they go in a NEW optional top-level field (e.g. `projectPrefs`) — never modify existing v1 fields.

### Forbidden surfaces this idea must avoid
`polyAreaM2`, `polyMetrics`, `polySelfIntersects`, `pdfToC`, `cToPdf`, `RS`, `buildSnapIndex`, `snap` engine internals, `.bmaplan` schema field renaming/removal, FastAPI endpoints, render cache. The settings UI MAY read from these surfaces (e.g. read current snap threshold) but MAY NOT modify them — instead it should configure a NEW wrapper layer (`getUserPref('snap.threshold')`) that callers consult.

### Success criteria (spike must demonstrate ALL)
1. **Single entry point.** One modal accessible from a single ribbon/menu entry — not 3 different ones — surfaces ALL preferences in v1 scope. Existing Widget Placement + UI Layout Options modals are reachable from this entry as sub-sections (or migrated entirely — spike must show the migration is safe).
2. **Read-write round-trip.** A user changes (a) snap default, (b) default unit, (c) UI layout preset, hits Apply, reloads the browser, and sees all three persist. Existing widget placement + layout state migrates correctly into the new persistence key.
3. **Backward-compat.** A `localStorage` snapshot with only old keys (`bmaPlan.uiLayoutOptions.v1` + `bmaPlan.widgetPlacement.v1`, no new key) loads without error and seeds the new model from those old keys (a one-way migration). A `.bmaplan` v1 file (no `projectPrefs`) loads unchanged.
4. **Restore defaults.** A "คืนค่าเริ่มต้น" button resets EVERY pref to the documented factory default with a confirm step. Existing widget placement + layout state are reset alongside.
5. **Reachable in ≤2 clicks** from the main UI to the snap-default control. (Discovery is the #1 settings-UX failure mode per research.)
6. **Schema version field.** The persisted object carries `version: 1` — future migrations can branch on it without re-encoding all keys.

### Out of scope (this invention pass)
- Cross-machine sync (Chrome storage `sync`, server-side user accounts) — Phase 1 stays single-machine.
- Per-PDF preferences embedded in `.bmaplan` — defer to follow-up unless DIVERGE finds a compelling reason to include them in v1.
- Export schema builder (column picker, sheet grouping). v1 covers at most a simple "include setbacks Y/N" checklist; full schema editing is a separate sprint.
- Theme / dark mode — separate concern, not part of this invention.
- Snap-engine internal config (which snap targets to compute) — v1 only exposes the snap **threshold** and snap **enabled** toggle that already exist as variables. Adding/removing snap target types is a snap-engine sprint.
- Localization (Thai / English toggle). All labels Thai in v1.

### Decisions deferred to DIVERGE
1. **Persistence model:** localStorage-only vs localStorage + optional `.bmaplan.projectPrefs` overlay vs separate "Profile" file (`.bmaplan-profile`). The frame allows any of these; the inventor must rank.
2. **UI shell:** modal vs left-panel tab vs right-panel docked. The frame requires single entry point — the inventor decides the shape.
3. **Initial scope of v1 content:** the minimum set of preferences that justifies the new architecture. Inventor must pick a small set that gives real user wins WITHOUT overrunning the spike budget.

## Research

_Delegated to `bma-researcher` 2026-05-15. Verbatim output below._

### 1. In-repo prior work

Existing preferences systems (already shipped):
- `docs/status/WIDGET_MENU_PLACEMENT_SYSTEM.md` (2026-05-11) — registry-based widget placement (visibility, region, order, size per widget). Persisted in `bmaPlan.widgetPlacement.v1` localStorage. 10-entry registry with metadata. Backward-compatible defaults rebuild from registry if localStorage empty. No `.bmaplan` schema changes.
- `LATEST_STATUS.md` line 80 — "UI Layout Options" (`#btn-ui-layout`) presets (Current Stable / Mockup V3 / Inspection Focus / Layer Focus / Compact) + per-section switches. Persisted in `bmaPlan.uiLayoutOptions.v1`. v3 modes apply CSS-class overrides to `<body>`. Default = Current Stable.
- `docs/status/SAVE_SYSTEM_AUDIT.md` — recent files list in `bmaPlan.recentProjects.v1` only.

**Pattern identified:** BMA-Plan already has a 3-tier localStorage settings model (layout presets, widget registry, recent files), all accessed via modal panels in the topbar. Reusable frame: the widget registry's normalization logic and `loadX()/saveX()` pattern can extend to cover snap/scale/export preferences.

Related sprints: `sprints/completed/2026-05-09-widget-placement-polish/` (E2E structure for preference UI), `sprints/archive/RUN_UI_PACK_1_HEADER_TOOLBAR.md` (UI Layout Options genesis).

No prior work on snap-engine preferences, scale defaults, export-format preferences, or default-layer preferences. These are all new.

### 2. CAD / GIS / graphics incumbents — settings UX

- **AutoCAD 2025** — `OPTIONS` command → tabbed modal (User Preferences / Display / Colors / Fonts / Drafting / Selection). App-scoped global profile. Reset/restore defaults available.
- **Bluebeam Revu** — Revu > Preferences → modal with General / Advanced / Grid & Snap / Document subsections. Theme + snap threshold. Export to XML for team rollout. App-scoped.
- **QGIS** — Settings ► Options → tabbed dialog with vertical left-panel tabs. Restart hint at bottom.
- **Foxit Reader** — File > Preferences > Measuring (snap to intersections/paths/H/V/diagonal). Scale unit set per-measurement via right-panel Format. Document-local snap, not global.
- **PlanGrid** — No global measurement prefs; in-workflow pop-up unit choice.

**Pattern:** Large desktop apps use tabbed modals; web/mobile tools expose prefs in right-panel format menus. No incumbent merges app-scoped + per-document prefs in one UI.

### 3. Inline-JS library options

| lib | verdict | note |
|---|---|---|
| Form.io JSON Forms | viable | MIT, 30–80 KB, UMD; JSON-Schema-driven |
| react-jsonschema-form | wrong-shape | React dep |
| jsonform | partial | last release ~2014, Bootstrap 3 |
| SurveyJS | wrong-shape | 200+ KB, bundler-friendly only |

**Verdict:** No single-script library beats hand-coding for BMA-Plan. Schema versioning + validation overhead outweighs gain. BMA-Plan hand-codes its modals — consistency favours hand-coding settings too.

### 4. Literature / algorithm

- **VS Code settings.json** — three-tier scope (default < user < workspace), JSON-based, per-layer override. Settings Sync replicates user layer; not workspace.
- **.NET Application Settings** — app-scoped (read-only) vs user-scoped (writable); pluggable providers.
- **Chrome extension Storage API** — `local` / `sync` / `session`. BMA-Plan has no cross-browser sync; `localStorage` = appropriate.

**Pattern:** scope + persistence tier + schema versioning (migrations on load). No closed-form theorem; the design choice is just *which scopes*.

### 5. Competitor / web-app settings UX

- **Figma** — right-sidebar context panels, per-selection prefs; no app-global modal in docs.
- **Bluebeam Cloud** — inherits desktop Preferences modal; theme + snap + units. XML import/export.
- **ArcGIS Online** — scattered settings; weak discovery.

Mobile/responsive: PlanGrid + Foxit web use pop-ups, not full prefs panels. Desktop (BMA-Plan target) has room for a modal.

"Restore defaults": AutoCAD/Bluebeam = red Reset button with confirm. QGIS = none. Standard = explicit confirm.

### Verdict: PRIOR_ART_PARTIAL

BMA-Plan already has a working modal + registry + localStorage pattern (Widget Placement, UI Layout Options, Recent Projects). Architecture is proven; the question is scope expansion. Snap/scale/export/default-layer preferences are new *content*, not new architecture. Three genuine divergence points remain:

1. **Scope layering** — stick to app-scoped localStorage only (simpler, matches current pattern), or add per-document `.bmaplan` overrides? Incumbents split: AutoCAD/Bluebeam = app-only; VS Code = layered.
2. **Snap/scale "defaults" UX** — today snap is hard-coded in `buildSnapIndex()` and scale is set per-page. Making them configurable implies a new workflow ("set snap once → applies to all new polygons this session") and state-machine integration.
3. **Export format as a preference** — XLSX is fixed-schema today. Allowing column selection implies (a) a schema-builder modal (complex) or (b) a simple checklist (simpler, matches existing export panel).

## Diverge

_Delegated to `bma-inventor` 2026-05-15. All 5 approaches verified: `forbidden_surface_touch: NO`, `phase_1_boundary_violation: NO`, `additive_schema_compatible: YES`._

### Approach A: Unified Tabbed Modal — localStorage-only, absorb existing modals (axis: UI shell)
Single full-screen modal `#settings-overlay` replaces fragmented entry points. Four vertical tabs: **วาด** (snap + default tool), **หน่วย** (display unit + decimals), **หน้าจอ** (UI layout preset, migrates `bmaPlan.uiLayoutOptions.v1`), **Widgets** (migrates `bmaPlan.widgetPlacement.v1`). One new localStorage key `bmaPlan.settings.v1` with `version: 1`. Old keys preserved post-migration → graceful degrade. All reads via `getPref(key, default)`. v1 scope: snap enabled + threshold, default tool, unit, decimals, layout preset, widget placement.

### Approach B: Layered scope — app localStorage + optional `.bmaplan.projectPrefs` overlay (axis: data-model)
Two persistence tiers like VS Code (workspace > user > default). `.bmaplan` gets one new optional top-level field `projectPrefs` (additive). `getPref(key)` checks project → app → factory. Per-row "บันทึกในโปรเจกต์ / บันทึกในแอป" toggle in the modal. Same UI shell as A. v1 scope adds per-project snap threshold + display unit (real win for PDFs of different pixel densities).

### Approach C: Right-panel docked strip — always-visible quick-access, no modal (axis: UX flow) ⭐
Collapsible docked strip at the bottom of the right panel. 4-6 high-frequency prefs as inline controls: unit toggle, snap-threshold slider, default-tool radios, UI-density toggle. Always visible → snap threshold reachable in 0 clicks. Persists to `bmaPlan.settings.v1` (debounced 300ms). Widget Placement + UI Layout Options stay as separate modals (NOT migrated). Deliberately fails frame success criterion 1 ("single entry point for ALL prefs") in exchange for the lowest discovery friction.

### Approach D: Preference registry + JSON-exported profile (axis: representation)
A `PREF_REGISTRY` (declarative `{key, label, type, default, min, max, group}` like `WIDGET_REGISTRY`) drives both the modal UI and the localStorage shape. Adds "ส่งออก / นำเข้า การตั้งค่า" — JSON file download/upload for portability (Bluebeam-XML analogue). Round-trip: change 3 prefs → export → clear localStorage → import → restored. Registry-driven modal generation = adding a pref is one registry line, not new form HTML.

### Approach E: Minimal scope-first — snap + unit only via `View > Settings…` (axis: scope-cut)
Deliberate scope minimalism. Two preferences only: snap (enabled + threshold) and display unit (ตร.ม./ตร.ฟต.). Tiny ~360×280 modal opened via `View > Settings…` or `Ctrl+,`. No migration of widget placement or UI layout — they remain in their existing modals. Persists `{version:1, snap:{...}, unit:'sqm'}`. Explicitly FAILS frame success criterion 1 to de-risk the persistence layer cheaply before absorbing existing modals.

## Score

| Approach | Novelty | Accuracy | UX | Model fit | Boundary | Cost | Total |
|---|---|---|---|---|---|---|---|
| **A: Unified Tabbed Modal** | 3 | 4 | 4 | 5 | 5 | 3 | **24** |
| B: Layered localStorage + projectPrefs | 4 | 5 | 3 | 4 | 5 | 2 | **23** |
| C: Right-panel Docked Strip | 3 | 3 | 5 | 4 | 5 | 4 | **24** |
| D: Registry-driven + JSON export | 4 | 4 | 4 | 4 | 5 | 2 | **23** |
| E: Minimal scope-first | 2 | 3 | 3 | 5 | 5 | 5 | **23** |

A and C tie at 24. Tie-break favours A: it satisfies ALL six frame success criteria with a single implementation pass; C explicitly fails success criterion 1.

**SCORE-VERIFICATION (per skill phase 5):**
- No approach with `forbidden_surface_touch: YES` ranks first ✓ (none touch forbidden surfaces).
- No approach crossing Phase 1 boundary ranks first ✓.
- No re-rank or override needed.

## Recommendation

**Top approach for spike: A — Unified Tabbed Modal.** Only approach satisfying ALL six frame success criteria in one pass. Migration from two existing localStorage keys is a one-way seeding (~30 lines) with the old keys preserved → graceful degrade if migration is buggy. Spike validates round-trip + backward-compat without touching `proto/ui.html`.

**Fallback if A's migration proves regression-prone in spike: C — Right-panel Docked Strip.** If absorbing the two existing modals is more brittle than expected (e.g. widget registry tightly coupled to modal-open timing), C ships zero-click access to snap threshold + unit, leaves existing modals untouched, and the "single entry point" goal moves to a v2 consolidation sprint.

## Spike

**Approach attempted:** A — Unified Tabbed Modal.
**Outcome:** ✅ PASS on the persistence kernel (Node-headless 7/7 incl. 2 bonus robustness tests). UI reachability (criterion 5) verified structurally inside the spike HTML — first tab is `วาด` and is `class="active"` by default, snap threshold control lives on that tab → 1 click from main UI. Fallback (C) not needed.

**Sandbox file:** `proto/sandbox/invent-settings-panel.html` — standalone, opens directly in browser, no server. ~17 KB. Contains the full modal, 4-tab navigation, draft/apply/cancel/reset flow, legacy-key seed button, wipe button, and an in-page "Run all 6 tests" harness mirroring the headless test.

### Verification — Node-headless smoke run

```
=== Spike acceptance kernel test (Node-headless) ===
  ✅ PASS  1. Factory defaults load when localStorage empty  —  threshold=10 unit=sqm version=1
  ✅ PASS  2. Read-write round-trip  —  threshold=22 unit=sqft layout=compact
  ✅ PASS  3. Backward-compat migration from legacy keys  —  layout=inspection-focus widget.workflow=false legacy preserved=true
  ✅ PASS  4. Restore defaults  —  threshold=10 unit=sqm version=1
  ⏭️  5. Snap threshold reachable in ≤2 clicks  —  UI test (in-browser only; structural check inside spike: 1 click)
  ✅ PASS  6. Schema version field present  —  localStorage[bmaPlan.settings.v1].version === 1
  ✅ PASS  7. Bad JSON gracefully falls back to defaults
  ✅ PASS  8. Wrong-version payload → defaults
=== 7 passed, 0 failed ===
```

| # | Criterion | Result | Detail |
|---|---|---|---|
| 1 | Single entry point | ✅ | exactly one `#btn-open-settings` button in DOM; modal absorbs Widget tab + Layout tab |
| 2 | Read-write round-trip | ✅ | mutate snap+unit+layout → `JSON.stringify` to `bmaPlan.settings.v1` → re-`JSON.parse` returns identical values |
| 3 | Backward-compat migration | ✅ | seed `bmaPlan.uiLayoutOptions.v1` + `bmaPlan.widgetPlacement.v1` only → first `loadPrefs()` writes new key + **leaves old keys intact** (graceful degrade contract held) |
| 4 | Restore defaults | ✅ | `PREFS = clone(PREF_DEFAULTS); savePrefs()` returns to `threshold=10 unit=sqm`; spike additionally clears the two legacy keys so reset is total |
| 5 | Reachable in ≤2 clicks | ✅ (structural) | ribbon button → modal opens on Draw tab (default-active) where snap threshold lives → 1 click from main UI to control |
| 6 | Schema version field | ✅ | `version: 1` present in `PREF_DEFAULTS` and persisted to every save; out-of-version payload (`version: 0`) is rejected and defaults restored |

### Robustness bonus (above-criteria)
- **Bad-JSON safety** — corrupting `bmaPlan.settings.v1` with `"{not valid json"` does not crash; `loadPrefs()` falls through to factory defaults.
- **Forward-version safety** — if a future v2 ever ships and the user downgrades, the v1 loader sees `version !== 1` and falls back cleanly. Migration code can branch on `version` at any future point.

### Architecture demonstrated
- One new localStorage key `bmaPlan.settings.v1` with `version: 1`. Schema = `{ version, snap:{enabled,threshold}, tool:{default}, unit:{area,decimals}, layout:{preset}, widgets:{...} }`.
- `getPref(path, fallback)` thin reader — callers like `snapEnabled = getPref('snap.enabled', true)` replace direct localStorage reads.
- `migrateFromLegacy()` one-way seeder; old keys preserved so a downstream bug degrades gracefully (user sees factory defaults, not a crash).
- Draft/Apply pattern — modal mutates a `DRAFT` object; clicking "บันทึก" commits to `PREFS` and `savePrefs()`. Cancel discards the draft, leaves PREFS untouched.
- Reset button calls `confirm()` then `PREFS = clone(PREF_DEFAULTS); savePrefs()` and additionally clears legacy keys (frame success criterion 4).
- Shallow-merge-over-defaults on load handles forward compat: if v1 adds new sub-fields later, old saves auto-inherit the new defaults without manual migration code.

### Estimated production sprint cost
- New modal HTML (4 tabs, ~10 controls): ~200 lines in `proto/ui.html`.
- `getPref / loadPrefs / savePrefs / migrateFromLegacy / openSettings` helpers: ~80 lines.
- Wire-up: snap engine reads `getPref('snap.threshold')` at `buildSnapIndex` call sites (NOT inside buildSnapIndex — read at the boundary). Tool defaults read `getPref('tool.default')`. Unit formatters read `getPref('unit.area')`. ~30 lines of call-site reads.
- Tests: 1 new E2E marker `SETTINGS_OK` + 1 new test in `proto/e2e_ui_test.py` (seed legacy keys + load + assert migration + assert reset).
- **Total ≈ 310 lines + 1 marker.** No forbidden-surface edits. Schema fully additive (no `.bmaplan` change).

### Risks observed in the spike
- **Migration ambiguity for layout preset name.** Spike assumes `bmaPlan.uiLayoutOptions.v1.preset` is a string from the documented enum (`current-stable / mockup-v3 / inspection-focus / layer-focus / compact`). Production must verify the actual live key structure — if the real key uses a different field name, `migrateFromLegacy` needs to match. Mitigation: the production sprint should read the live key once before the migration commit and confirm shape.
- **Widget registry coupling.** Spike treats widget visibility as a flat `{key: bool}` map; the real `WIDGET_REGISTRY` carries more metadata (region, order, size). v1 production should migrate ONLY the `visible` field and leave region/order/size in their existing registry — do NOT consolidate into `bmaPlan.settings.v1` unless absolutely necessary. The frame allows either; the safest production cut is "settings.widgets stores visibility; existing registry stores layout details."
- **Apply-vs-Live binding.** The spike's "Apply" commits the whole draft at once. The live app may want immediate-apply for some prefs (e.g. snap threshold updates the active snap radius without a modal "OK"). Production decision deferred — both patterns are achievable from the same persistence layer; the choice is per-pref UX taste.

### Why approaches C–E were not attempted
A's spike passed first attempt with no architecture revisions needed, and the persistence kernel survived 2 robustness stress tests (corrupt JSON + wrong-version payload). The fallback (C) is documented for the production sprint in case widget-registry migration proves more brittle than the spike's simplified model suggests.

## Decision (GO)

**Decided:** 2026-05-15 by user at human checkpoint.
**Sprint id:** `INV-2026-05-15-002`
**Status flip:** `invent-in-progress` → `invent-done-go (→ INV-2026-05-15-002)`

### Why GO
- Persistence kernel passed 7/7 (incl. 2 robustness bonuses) on first attempt; structural reachability check confirms ≤2-click access to snap threshold.
- Architecture is a thin, well-isolated layer that callers consult — no forbidden-surface internals are touched; the existing snap-engine variable can be initialised from `getPref()` at the boundary.
- Single new localStorage key with `version` field + one-way legacy migration → graceful degrade if migration is buggy. `.bmaplan` schema completely unchanged.
- Absorbs the two existing settings modals (UI Layout Options + Widget Placement) into one entry point — solves the fragmentation problem the user named in the original /idea note.

### Sprint scope handed to `/bma-dev-loop`
Sprint card written to `docs/status/PHASE_INDEX.md` under id `INV-2026-05-15-002`. Production sprint follows Approach A with the 3 documented risks as scope sub-items (legacy-key shape verification, widget-registry coupling decision, Apply-vs-immediate-apply per-pref UX choice).

### Carry-over risks for the production sprint
1. **Legacy key shape verification** — before the migration commit lands, read the live `bmaPlan.uiLayoutOptions.v1` + `bmaPlan.widgetPlacement.v1` shapes and confirm `migrateFromLegacy` matches them exactly. Mismatch = silent data loss.
2. **Widget-registry coupling** — production should migrate ONLY the `visible` field into `bmaPlan.settings.v1.widgets`; leave region/order/size in the existing `WIDGET_REGISTRY` to avoid coupling the two storage tiers. Frame allows either; this is the safest cut.
3. **Apply vs. immediate-apply per pref** — spike commits the whole draft on "บันทึก"; production may want snap threshold to be live (no Apply needed). Decision deferred to UI specialist; both patterns sit on the same persistence layer.
4. **Snap engine boundary** — `getPref('snap.threshold')` must be read at the call-site **outside** `buildSnapIndex`/`snap` internals; the engine itself stays untouched (forbidden surface).


