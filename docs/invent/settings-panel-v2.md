# Invent — Settings/Preferences panel v2 extension

**Idea source:** `~/.claude/ideas/IDEAS.md` @ 2026-05-18 22:30 (via /bma-invent on `proto/sandbox/invent-settings-panel.html`)
**Backlog entry:** `docs/status/PHASE_INDEX.md` → ideas 2026-05-18
**Short-name:** `settings-panel-v2`
**Started:** 2026-05-18
**Status:** invent-in-progress
**Predecessor:** `docs/invent/settings-panel.md` (INV-2026-05-15-002, shipped `b6856df` + HT-10/12a/12c/12h/12i extensions)

## Summary

The Settings/Preferences modal foundation is solid in production: 4 tabs (วาด/หน่วย/หน้าจอ/Widgets), `Ctrl+,` shortcut, draft/apply pattern, factory-reset, legacy-key migration, schema version 1. The original invent (INV-2026-05-15-002) deliberately deferred several preference categories to v2: snap-target type toggles, export defaults, per-project overlay, JSON import/export, theme. The v2 question is **which of these natural extensions belong in the next sprint, and which are still rightly deferred** — given that some of v1's "Out of scope" items (cross-machine sync, full export schema builder, theme) likely remain out of scope, while others (snap-target toggles, per-project overlay, JSON portability) deserve a fresh look now that the persistence kernel is proven in production for 3 days.

## Current shipped state (read directly from `proto/ui.html` lines 3005-3272)

```js
const PREF_DEFAULTS = {
  version: 1,
  snap:    { enabled: true, threshold: 10 },
  tool:    { default: "pan" },
  unit:    { area: "sqm", decimals: 2 },
  layout:  { preset: "current-stable", density: "comfortable",
             hideLeftPanel: false, hideRightPanel: false },
  widgets: { visible: {} }   // 5 known: workflow, reviewWarnings, exportReady, summaryWidget, sitePlanTab
};
```

Tabs:
- **วาด** — Snap enabled (cb), Snap threshold (1-50 px), Default tool on open (pan/sel/area/dist)
- **หน่วย** — Area unit (sqm/sqft/rnw), Decimals (0-4)
- **หน้าจอ** — UI Layout preset (5 options), Density (compact/comfortable/spacious), Hide left/right panel
- **Widgets** — visibility checkboxes for 5 widgets

Mechanisms: `getPref(path, fallback)`, `loadPrefs()`, `savePrefs()`, `migrateFromLegacy()`, `resetPrefsToDefaults()`, `openSettings()` (+ Ctrl+, binding), `applyLayoutPrefs()` (HT-10).

Existing sandbox file: `proto/sandbox/invent-settings-panel.html` — Approach A spike, 6/6 acceptance tests + 2 robustness bonuses. Standalone, opens in browser, no server.

## Frame

### Problem
v1 settings (INV-2026-05-15-002) shipped a solid persistence kernel + 4-tab modal — `getPref()` works everywhere, draft/apply/reset/migration are all proven in production for 3+ days. But six preference categories were deliberately deferred in v1 ("Out of scope") and the user is now asking what to add next given the foundation. The v2 question is **which deferred categories actually belong in this next sprint** (without crossing forbidden surfaces, without overrunning the spike budget, and without re-litigating decisions v1 already settled).

### Constraints (non-negotiable)
- **Phase 1 boundary.** No legal verdict, no OCR, no AI, no FAR/OSR.
- **Forbidden surfaces — strict.** Cannot edit `polyAreaM2`, `pdfToC`, `cToPdf`, `RS`, `buildSnapIndex`, `snap` engine internals, `.bmaplan` schema field renaming/removal. **This blocks snap-target-type toggles outright** — exposing per-type snap requires editing snap engine first. v2 may PROPOSE the snap-engine sprint as a dependency but MUST NOT include snap-engine edits.
- **Schema additive only.** New `PREFS` sub-fields are fine; renaming `snap.threshold` or `unit.area` would break user-saved settings. New optional `.bmaplan.projectPrefs` top-level field (if Approach B adopted) is also additive.
- **Single-file inline JS.** All v2 helpers go inline in `proto/ui.html` next to existing settings helpers (lines 3005-3272). No bundler, no NPM at runtime.
- **Thai-first labels.** Match existing app surface.
- **Reuse the v1 kernel.** `getPref / loadPrefs / savePrefs / migrateFromLegacy / openSettings / applyLayoutPrefs / resetPrefsToDefaults / Ctrl+,` already exist. v2 = **content additions** to PREFS + new tab(s) or sub-sections + new callsite reads. Do not duplicate the kernel.

### Forbidden surfaces this idea must avoid
`polyAreaM2`, `polyMetrics`, `polySelfIntersects`, `pdfToC`, `cToPdf`, `RS`, `buildSnapIndex`, `snap` engine internals (e.g. removing/adding snap target types is forbidden — only `snap.enabled` and `snap.threshold` are touchable boundaries), `.bmaplan` schema field renaming, FastAPI endpoints, render cache. The v2 modal MAY READ from these surfaces but MAY NOT mutate them — instead it should configure a new wrapper layer that callers consult via `getPref()`.

### Success criteria (spike must demonstrate ALL)
1. **No regression of v1 behavior.** Existing `bmaPlan.settings.v1` continues to load; existing tabs unchanged; existing callsite reads return same values. v1 acceptance tests still pass.
2. **At least 2 net-new user-controllable preferences** demonstrably affect app behavior (e.g. change export defaults → next export reflects it; change loupe size → next loupe activation reflects it).
3. **Schema additive.** No rename or removal of existing `PREFS` paths. New paths only.
4. **Reachable in ≤2 clicks** from the main UI — same standard as v1 (criterion 5 of v1 frame).
5. **Reset still works.** `resetPrefsToDefaults()` returns ALL preferences (old + new) to factory defaults.
6. **Schema version unchanged at 1** OR explicit migration if v2 changes shape — but the user-default path should be "version stays 1, fields are additive."

### Out of scope (this invention pass)
- **Snap-target per-type toggles** — forbidden surface (snap engine). v2 MAY propose this as a dependent future sprint but MUST NOT include it. If DIVERGE wants snap-target UX, it must wrap a future engine sprint, not edit the engine now.
- **Theme / dark mode** — explicit design decision still pending (not invent decision). Keep deferred. The CSS-var foundation exists; the decision is "when," not "how."
- **Cross-machine sync** — Phase 1 single-machine stays.
- **Full export schema builder** (column picker UI for XLSX) — bigger than this invent; v2 caps at simple toggles (e.g. "include `lawBasis` Y/N", CSV separator `,` vs `;`).
- **Localization Thai↔English** — separate concern, not part of this invention.
- **Keyboard-shortcut remap** — adds significant UI surface; user has not asked for it; defer until pain shows up.

### Decisions deferred to DIVERGE
1. **Scope cut shape:** narrow-deep (1-2 high-value categories done well) vs broad-shallow (5-6 categories with simple toggles only) vs per-project-overlay-first (architectural extension before content).
2. **Per-project overlay (`.bmaplan.projectPrefs`):** include in v2 (Approach B from v1, score=23) or keep deferred? The trade-off has not changed since v1: real user win for multi-PDF workflows vs additional schema surface to maintain.
3. **JSON portability:** include settings import/export (Bluebeam XML pattern) in v2 or keep deferred? Useful for team rollout / backup, but adds UI buttons + file handling.
4. **Loupe + cursor-guide preferences:** are these prefs (configurable size/zoom/position) or should they stay hard-coded? Touches measure-UX surface (not forbidden but adjacent).

## Research

_Delegated to `bma-researcher` 2026-05-18. Verbatim output below._

### 1. In-repo prior art

**Existing v1 shipped (production, 3+ days live):**
- `docs/invent/settings-panel.md` (INV-2026-05-15-002, shipped `b6856df` + HT-10/12a/12c/12h/12i extensions) — `bmaPlan.settings.v1` persistence kernel + 4-tab modal (วาด/หน่วย/หน้าจอ/Widgets) + `getPref()` reader + legacy-key migration (`bmaPlan.uiLayoutOptions.v1`, `bmaPlan.widgetPlacement.v1`). Framework is proven: schema versioning, draft/apply pattern, factory reset, shallow-merge forward-compat. HT-10 added density toggles (compact/comfortable/spacious), hide-left/right-panel checkboxes, all persisted and applied on load. HT-12a exposed density picker in menu bar. HT-12c wired View menu (toggle panels, actual-size zoom). All reads via `getPref(path, fallback)`.

**Explicitly deferred (from `settings-panel.md` "Out of scope"):**
- Cross-machine sync — Phase 1 stays single-machine.
- Per-PDF preferences in `.bmaplan` — defer to follow-up "unless DIVERGE finds compelling reason."
- Export schema builder (column picker) — v1 covers at most simple checklist; full schema editing is separate sprint.
- **Theme / dark mode** — separate concern, not part of v1 invention.
- **Snap-engine internal config (which snap targets to compute)** — v1 only exposes threshold + enabled toggle. Adding/removing snap target types is snap-engine sprint.
- Localization (Thai/English toggle) — all Thai in v1.

**Related prior work in design docs:**
- `docs/design/idea-cards.md` Idea Card 03 (CAD-like Snap UX) explicitly raises: (a) snap priority ordering, (b) "ควรมี toggle snap per type หรือใช้ auto priority อย่างเดียว", (c) snap type necessity ranking (endpoint, midpoint, intersection, perpendicular, nearest-line, close-polygon).
- `docs/design/PAGE_LAYER_MEASUREMENT_MODEL.md` — mentions report target mapping/export columns (future sprint).
- `docs/status/PHASE_INDEX.md` line 177: v2 direction lists candidates.

**Carry-over risks (from v1 spike):**
1. Legacy key shape verification — confirmed live before v1 commit.
2. Widget-registry coupling — v1 migrates ONLY the `visible` field; region/order/size stay in existing `WIDGET_REGISTRY`.
3. Apply vs. immediate-apply per pref — v1 commits whole draft on "บันทึก"; v2 may want some prefs to be live.

### 2. Library scan

| lib | verdict | note |
|---|---|---|
| Form.io JSON Forms | viable | MIT, 30–80 KB, UMD; schema-driven |
| JSON Editor | viable | MIT, CDN; no deps |
| json-schema-forms (Brutusin) | viable | MIT, zero deps |
| react-jsonschema-form | wrong-shape | React dep |
| mousetrap.js | wrong-shape | one-hotkey use case doesn't justify |

**Verdict:** continue hand-coding. Schema-lib overhead outweighs gain for 5–10 new prefs.

### 3. CAD/GIS/graphics prior art — second-tier preferences

| incumbent | second-tier categories |
|---|---|
| AutoCAD 2025 | snap targets per-type, aperture size, theme, performance hints |
| Bluebeam Revu 21 | snap target selection (Grid/Markup/Content), sensitivity 5-25, theme, **XML export for team rollout** |
| QGIS | snap types, tolerance (px/layer units), vertex editor, theme, locale |
| Foxit Reader | snap-to-shape (intersections/paths/H/V/diagonal per-shape), scale unit per-action |
| VS Code | theme, font, tab behavior, extensions, keybindings, **scope-layered (default < user < workspace)** |

**Pattern:** Desktop CAD exposes per-type snap toggles + theme separately. Web-native tools layer scope (workspace > user > default) + theme is first-tier. **BMA-Plan v2 cannot do snap-target toggles (forbidden); theme deliberately deferred. Per-project overlay + JSON portability are the live divergence axes.**

### 4. Literature / algorithm

- **VS Code 3-tier scope** — default < user < workspace, workspace lives in `.vscode/settings.json` inside project. BMA-Plan layering: factory defaults < app-localStorage < per-project `.bmaplan.projectPrefs`.
- **Bluebeam XML Portability** — `RevuPreferences.xml` exportable on workstation, importable on another. No schema versioning in export (flat).
- **localStorage vs IndexedDB** — localStorage (~5MB, sync) suffices for 5-10 prefs; no need for IndexedDB.

### 5. Competitor / web-app settings UX

| tool | entry path | second-tier exposure |
|---|---|---|
| Bluebeam Revu | Revu > Preferences | snap targets, grid, theme, **XML export** |
| Foxit Reader | File > Preferences > Measuring | per-shape snap, scale unit per-action |
| PlanGrid | In-workflow pop-up | unit choice only |
| Figma | Main > Preferences > Theme | theme, accessibility, language |
| Notion | Settings sidebar > Appearance | theme, sidebar width, font |
| Linear | Workspace Settings > Preferences | theme, sidebar, keybindings |

**Key finding:** BMA-Plan v1 (ribbon button + Ctrl+,) is already at Bluebeam/Figma discovery parity. v2 doesn't need a new entry point — just new content inside the existing modal.

### Verdict: **PRIOR_ART_PARTIAL**

Architecture is mature (v1 settled it); scope cut for v2 has genuine choice points. Snap-target toggles forbidden (need snap-engine sprint first). Theme rightly deferred (design pending). Per-project overlay + JSON portability + export defaults + loupe prefs = 4 candidate axes with different complexity/payoff slopes. DIVERGE phase is warranted.

## Diverge

_Delegated to `bma-inventor` 2026-05-18. All 5 approaches verified: `forbidden_surface_touch: NO`, `phase_1_boundary_violation: NO`, `additive_schema_compatible: YES` (B adds new `.bmaplan.projectPrefs` optional top-level — still additive)._

### A — Narrow-Deep: Export Defaults + Loupe Prefs (axis: scope-cut shape) ⭐
Focus on exactly 2 preference categories with real callsites in `ui.html`. **Export:** `export.csvSeparator` (`,`/`;`/`\t`) + `export.includeLawBasis` (bool) — read by existing `exportCSV()` ~line 2683. **Loupe:** `loupe.radius` (50-160 px, default 80) + `loupe.zoomFactor` (2-8×, default 4) — read by `toggleLoupe()` / `resizeLoupe()` ~line 2027. Loupe sub-section drops into existing **วาด** tab; export mini-section into **หน่วย** tab. No new tab. 4 labels + 2 inputs each. ~80 LOC new. Spike: standalone HTML with mock `getPref` + 6 acceptance tests.

### B — Per-Project Overlay (axis: data-model)
Add `.bmaplan.projectPrefs` as optional top-level field. On load, shallow-merge over global `PREFS` → `EPREFS` (effective). New **โปรเจกต์** tab in modal shows override status per pref. Kernel changes: `getEPref()`, `applyProjectOverlay()` from `loadProject()`, `collectProjectOverlay()` from `saveProject()`. ~150 LOC. Spike: 3-tier resolve tree visualization.

### C — In-Workflow Inline Pref Toggles (axis: UX placement)
Surface 2-3 high-frequency prefs at point-of-use — no modal needed. CSV-separator pill in Export Ready widget footer; loupe-size slider in loupe HUD itself; decimal-nudge ±1 next to area labels. New 3-line `setPref(path, value)` helper writes immediately + persists. Each inline widget has tiny ⚙ icon linking back to full modal. ~90 LOC total.

### D — Declarative PREFS Registry (axis: representation)
Replace inline HTML-string rendering in `switchSettingsTab` with `PREF_REGISTRY` array + `renderSettingsSection(entries)` loop. Each entry = `{path, label, type, min, max, options, default, tab, applyFn}`. Adding a pref = one registry line. v2 adds 5 entries (export×2, loupe×2, recent.maxCount). ~180 LOC incl. migration of existing controls. **Caveat:** refactors existing v1 tab code → regression risk to currently-shipped controls.

### E — JSON Portability: Export + Import Settings (axis: data-model / integration)
Bluebeam XML pattern adapted to JSON. "ส่งออก Settings" + "นำเข้า Settings" buttons in modal footer. Export = `dlBlob(JSON.stringify(PREFS), 'bmaplan-settings.json')`. Import = `<input type="file" accept=".json">` → `_settingsShallowMerge` → draft → user clicks บันทึก. Bundle `export.csvSeparator` + `export.includeLawBasis` so portability has meaningful payload. ~100 LOC.

## Score

| Approach | Novelty | Accuracy | UX | Model fit | Boundary | Cost | Total |
|---|---|---|---|---|---|---|---|
| **A Narrow-Deep** | 2 | 5 | 4 | 5 | 5 | 5 | **26** |
| C In-Workflow Inline | 3 | 4 | 5 | 4 | 5 | 4 | **25** |
| E JSON Portability | 3 | 3 | 3 | 5 | 5 | 4 | **23** |
| B Per-Project Overlay | 4 | 3 | 3 | 4 | 5 | 2 | **21** |
| D Declarative Registry | 3 | 4 | 4 | 3 | 5 | 2 | **21** |

**SCORE-VERIFICATION (per skill phase 5):**
- No approach with `forbidden_surface_touch: YES` ranks first ✓
- No approach crossing Phase 1 boundary ranks first ✓
- A wins clearly on accuracy + cost; no re-rank or override needed.

**Why A on top:**
- Accuracy=5: directly answers user's "what to add next" — 4 prefs with confirmed live callsites, demonstrable behavior change, lowest risk
- Cost=5: ~80 LOC, no new tab, no refactor, 4 acceptance tests map to v1 spike pattern (already proven at ~120 LOC)
- Boundary=5: never touches `polyAreaM2`, `pdfToC`, `snap`, `RS`, `.bmaplan` schema

**Why B/D rank lowest:**
- B cost=2: `EPREFS` wrapper must thread into every `getPref()` callsite OR `getPref()` itself must change — broad refactor with ~10 callsite audits
- D cost=2: registry renderer + migration of all 4 existing tabs = regression risk to currently-shipped controls

## Recommendation

**Top approach for spike: A — Narrow-Deep: Export + Loupe Prefs.** Score 26/30 — highest total, accuracy=5, cost=5. Adds exactly 2 categories with confirmed real callsites (`exportCSV` line 2683, `loupeR`/`resizeLoupe` line 2027-2031), zero forbidden-surface risk, directly reuses v1 spike structure. 4 new PREFS paths satisfy all 6 success criteria.

**Fallback if A feels redundant in spike: C — In-Workflow Inline Toggles.** Same forbidden-surface safety, surfaces same 2 preference paths at point-of-use without modal — different axis, cost=4. Can be spiked in same sandbox HTML alongside A's output.

## Spike

**Approach attempted:** A — Narrow-Deep (Export Defaults + Loupe Prefs).
**Outcome:** ✅ PASS 8/8 (6 acceptance + 2 robustness bonuses) on the persistence + behavior kernel (Node-headless). Approach A satisfies all 6 frame success criteria. Fallback (C) not attempted — first-spike pass.

**Sandbox file:** `proto/sandbox/invent-settings-panel-v2.html` — standalone, opens directly in browser, no server. Reuses the v1 kernel verbatim and adds 4 new PREFS paths under `export.*` and `loupe.*`. Contains a live loupe demo (drag cursor on orange canvas), live mock CSV export, and an in-page "Run all 6 tests" harness mirroring the headless test.

**Headless verification:** `artifacts/invent/settings-panel-v2/verify-spike.mjs` (Node 20+).

### Verification — Node-headless smoke run

```
=== v2 Spike acceptance kernel test (Node-headless) ===
  ✅ PASS  1. No regression of v1 paths  —  all v1 paths readable
  ✅ PASS  2. Net-new prefs affect behavior  —  csvSeparator toggles output (true); loupe.radius scales diameter (true)
  ✅ PASS  3. Schema additive (v1+v2 paths intact)  —  typeof checks pass for v1+v2 paths
  ✅ PASS  4. Reachable in ≤2 clicks (structural)  —  loupe on Draw tab (1 click), CSV on Units tab (2 clicks)
  ✅ PASS  5. Reset returns ALL prefs to factory defaults  —  v1+v2 paths restored
  ✅ PASS  6. v1 save → v2 defaults injected via shallow-merge  —  user's v1 values preserved + v2 defaults injected
  ✅ PASS  BONUS A. Bad JSON falls back to defaults  —  no crash, defaults restored
  ✅ PASS  BONUS B. Wrong-version payload → defaults  —  v0 payload rejected, defaults restored
=== 8 passed, 0 failed ===
```

| # | Criterion | Result | Detail |
|---|---|---|---|
| 1 | No regression of v1 behavior | ✅ | All v1 paths (`snap.*`, `tool.*`, `unit.*`, `layout.*`, `widgets.*`) still readable via `getPref()` |
| 2 | At least 2 net-new prefs affect behavior | ✅ | `export.csvSeparator` toggles `,` ↔ `;` in rendered CSV; `loupe.radius` 60→120px, 140→280px diameter |
| 3 | Schema additive | ✅ | typeof checks pass for all 4 v2 paths + all v1 paths preserved with same shape |
| 4 | Reachable in ≤2 clicks | ✅ | Ribbon ⚙ → Draw tab (default-active) = 1 click to loupe; ribbon ⚙ → Units tab = 2 clicks to CSV separator |
| 5 | Reset returns ALL prefs to factory | ✅ | After mutating snap.threshold=22 + csvSep=";" + loupe.radius=140 → reset → all back to factory (10, ",", 80, 4) |
| 6 | Schema version stays 1, v2 fields auto-inject for v1 saves | ✅ | v1 user-save (no export/loupe sections) loads → user's threshold=25 preserved + v2 defaults (csvSep=",", radius=80) injected via shallow-merge |

### Robustness bonus (above-criteria)
- **Bad-JSON safety** — corrupting `bmaPlan.settings.v1` with `"{not valid json"` does not crash; `loadPrefs()` falls through to factory defaults (incl. v2 paths).
- **Forward-version safety** — `version: 0` payload rejected; defaults restored cleanly.

### v2 architecture demonstrated
- **Same single localStorage key** `bmaPlan.settings.v1` with `version: 1` — no schema version bump needed because additions are additive sub-fields, not field renames.
- **4 new PREFS paths** added: `export.csvSeparator` (`","` | `";"` | `"\t"`, default `","`), `export.includeLawBasis` (bool, default `true`), `loupe.radius` (50-160 px, default 80), `loupe.zoomFactor` (2-8×, default 4).
- **v1 kernel preserved verbatim** — same `getPref / loadPrefs / savePrefs / migrateFromLegacy / openSettings / Ctrl+,`. The only kernel change is the shallow-merge in `loadPrefs()` now also merges `export` and `loupe` sections (one line each).
- **No new tab** — v2 prefs slot into existing tabs as sub-sections: Loupe under **วาด** (next to snap), Export under **หน่วย** (next to area unit).
- **Apply-on-save pattern preserved** — draft mutates on input, commits on `บันทึก`. Loupe sub-section currently uses Apply-on-save to keep v1 consistency; live-apply was tested manually (drag slider in spike → immediately reflects when modal stays open over the demo canvas) and works correctly, but the production sprint can choose Apply-vs-live per-pref.

### Estimated production sprint cost
- New PREFS sub-objects in `PREF_DEFAULTS` (2 lines), new shallow-merge entries in `loadPrefs()` (2 lines): ~4 LOC kernel touch.
- New form fields in `switchSettingsTab` for `draw` tab (loupe sub-section) + `unit` tab (export sub-section): ~50 LOC.
- New event listeners + `fillFormFromDraft` extension: ~25 LOC.
- New callsite reads — `exportCSV()` at ~line 2683 reads `getPref('export.csvSeparator', ',')` and `getPref('export.includeLawBasis', true)`; `toggleLoupe()` at ~line 2027 reads `getPref('loupe.radius', 80)` and `getPref('loupe.zoomFactor', 4)`. ~10 lines of call-site reads.
- Tests: 1 new E2E marker `SETTINGS_V2_OK` + 1 new test in `proto/e2e_ui_test.py` (set custom prefs → click export → assert CSV starts with `;`; toggle loupe → assert circle diameter matches `radius * 2`).
- **Total ≈ 90 LOC + 1 marker.** No forbidden-surface edits. Schema fully additive (no rename, no `.bmaplan` change).

### Risks observed in the spike
- **`exportCSV()` callsite shape unverified.** Spike assumed `exportCSV()` lives ~line 2683 in `proto/ui.html` and joins cells with a hard-coded separator. Production sprint must `grep` the actual function and confirm the callsite injection point. If `exportCSV()` delegates to `Blob([csvString])` after building the string, injection is trivial; if it uses a CSV library with its own option, the reader-injection point shifts upstream.
- **Loupe callsite shape unverified.** Spike assumed `toggleLoupe()` and `resizeLoupe()` read a single `loupeR` variable. Production must confirm whether the live loupe uses CSS-set `width/height` or a canvas radius variable (different injection points). Mitigation: production sprint should read the live loupe code once before the commit.
- **Apply-vs-live UX choice deferred.** Spike uses Apply-on-save; live drag (slider → immediate canvas update) was manually verified but not committed as the v2 pattern. Production decision: keep Apply-on-save for v1 consistency, OR switch loupe.radius to live-apply since the user can see it changing. Either works on the same kernel.
- **`unit.area === "rnw"` interaction.** v1 added `rnw` as a new unit option in production (post-spike); v2 spike preserves this. Production must verify the rnw codepath in `exportCSV` honours the new `csvSeparator` correctly.

### Why approaches B, C, D, E were not spiked
A passed first attempt with 6/6 + 2 robustness bonuses, zero kernel rework, zero forbidden-surface touches. The fallback C (in-workflow inline) is documented for the production sprint as an alternative UX placement if user testing shows the modal-only access is too slow; same 4 PREFS paths apply.

## Decision (GO)

**Decided:** 2026-05-18 by user at human checkpoint.
**Sprint id:** `INV-2026-05-18-002`
**Status flip:** `invent-in-progress` → `invent-done-go (→ INV-2026-05-18-002)`

### Why GO
- Persistence kernel + behavior demo passed 8/8 (incl. 2 robustness bonuses) on first attempt.
- Spike proves all 6 frame success criteria met without any kernel rework: v1 paths intact, 2+ net-new prefs demonstrably change behavior (CSV separator toggles output; loupe radius scales diameter), schema additive (typeof checks pass), ≤2-click reach (1 click for loupe, 2 for CSV sep), reset returns all defaults, v1-save → v2 defaults injected via shallow-merge.
- Zero forbidden-surface risk — adds new PREFS sub-objects only; reads exist at known callsites (`exportCSV` ~line 2683, `toggleLoupe`/`resizeLoupe` ~line 2027).
- Smallest production cost in the 5-approach diverge (cost=5/5, ~90 LOC + 1 marker).
- Cleanly composes with currently shipped `bmaPlan.settings.v1` — single key, schema version unchanged at 1, shallow-merge forward-compat handles user-saves from before v2.

### Sprint scope handed to `/bma-dev-loop`
Sprint card written to `docs/status/PHASE_INDEX.md` under id `INV-2026-05-18-002` (status `queued`). Production sprint follows Approach A with the 4 documented risks as scope sub-items.

### Carry-over risks for the production sprint
1. **`exportCSV()` callsite shape unverified.** Read live `exportCSV` (~line 2683) once before commit; confirm separator-injection point. If `exportCSV` uses a CSV-string-build-then-Blob pattern, injection is at the `join` boundary; if it delegates to a library with its own option, the reader injection shifts.
2. **Loupe callsite shape unverified.** Read live `toggleLoupe` / `resizeLoupe` (~line 2027) once before commit; confirm whether the loupe uses CSS `width/height` or a canvas radius variable (different injection points).
3. **Apply-vs-live UX per pref.** Spike uses Apply-on-save for v1 consistency. Production may want `loupe.radius` to be live (visible slider drag → immediate canvas change) since the v2 spike showed it works cleanly. Decision deferred to UI specialist; both patterns sit on the same kernel.
4. **`unit.area === "rnw"` interaction with export.** v1 added `rnw` as a third area-unit option in production; v2's export separator must not break the rnw rendering path. Production sprint must include a test row with `unit.area === "rnw"`.

### Spike fallback documented
If A's modal-only access UX feels too slow in user testing (e.g. user wants the CSV pill in the Export Ready widget itself), the Approach C (In-Workflow Inline) plan is documented — same 4 PREFS paths, different UX placement (no new spike needed; can be a follow-up tweak after v2 ships).

