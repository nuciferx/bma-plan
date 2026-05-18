# RUN_INV_002_SETTINGS_MODAL — INV-2026-05-15-002: Unified Settings/Preferences modal

Date: 2026-05-17
Branch: main
Status: PASS — completed 2026-05-17
Commit hash: `b6856df`

## Goal

Port the Settings/Preferences modal spike (`docs/invent/settings-panel.md` + `proto/sandbox/invent-
settings-panel.html`) to production `proto/ui.html`. Unified tabbed modal (`Ctrl+,`) with 4 tabs
(วาด / หน่วย / หน้าจอ / Widgets) absorbs legacy `bmaPlan.uiLayoutOptions.v1` and
`bmaPlan.widgetPlacement.v1` keys via one-way migration. New `bmaPlan.settings.v1` localStorage key.
Draft/Apply/Cancel + Reset pattern. Bad-JSON and wrong-version safety added on top of spike.

Source: PHASE_INDEX.md row `INV-2026-05-15-002` (status `queued — invent-done-go`). Spike PASS 7/7
sub-checks. Production sprint extends spike's 5 success criteria to 13 total (added bad-JSON +
wrong-version recovery). Production also resolves 3 carry-over risks from the spike checkpoint.

## Spike checkpoint carry-over risks — resolved in this sprint

1. **Legacy key shape verification** — handled in `migrateFromLegacy()` via flexible
   `preset || mode` lookup (supports both `uiLayoutOptions.v1` shape variants) + `visible` field
   extracted from `{visible: bool}` OR plain bool (both shapes in `widgetPlacement.v1` seen
   in real localStorage data). No rigid shape assertion that could break migration.

2. **Widget-registry coupling decision** — ONLY `widgets.visible` migrated from
   `bmaPlan.widgetPlacement.v1`. Region / order / size fields deliberately untouched — they remain
   in `WIDGET_MENU_REGISTRY` defaults. This avoids coupling the new settings schema to the widget
   placement internals.

3. **Apply-vs-immediate-apply per pref** — spike Apply-on-save pattern adopted for all prefs in v1.
   Immediate-apply (live preview while the modal is open) is deferred to a follow-up UX sprint.
   Rationale: Apply-on-save is predictable and simpler; immediate-apply requires transient undo
   and per-pref binding — not worth the complexity in v1.

## Scope — IN

- `bmaPlan.settings.v1` localStorage key: `{version:1, prefs:{snap:{enabled, threshold},
  tool:{default}, unit:{area, decimals}, layout:{preset}, widgets:{visible:{...}}}}`.
- `getPref(path, fallback)` reader at call-sites — reads from `bmaPlan.settings.v1`; safe fallback.
- `setPref(path, value)` writer — mutates in-memory draft; not committed until Apply.
- `openSettingsModal()` / `closeSettingsModal()` — loads current prefs into modal fields.
- `applySettings()` — writes draft to `bmaPlan.settings.v1`; triggers affected subsystems (snap
  enabled/threshold, layout preset, widget visibility); closes modal.
- `resetSettings()` — resets draft to defaults with confirm dialog; Apply required to commit.
- `migrateFromLegacy()` — one-way migration on first load: reads legacy `uiLayoutOptions.v1`
  (layout.preset via `preset || mode` lookup) + `widgetPlacement.v1` (widgets.visible extraction
  from `{visible:bool}` or plain bool). Legacy keys preserved post-migration → graceful degrade.
- 4-tab UI: วาด (snap settings), หน่วย (unit/decimals), หน้าจอ (layout preset), Widgets (visibility).
- `Ctrl+,` shortcut opens modal.
- Bad-JSON safety: `JSON.parse` wrapped in try/catch; corrupt `bmaPlan.settings.v1` → reset to defaults.
- Wrong-version safety: if `parsed.version !== 1`, treat as incompatible → reset to defaults + warn.
- New E2E marker `SETTINGS_OK` with 13 sub-checks (spike's 7 + bad-JSON + wrong-version recovery +
  3 additional production checks).

## Scope — OUT

- Snap engine internals untouched — `getPref('snap.enabled')` is read at the boundary only; the
  `buildSnapIndex` / `snap` function bodies are forbidden surfaces and remain unchanged.
- Per-pref immediate-apply (live preview) — deferred to follow-up UX sprint.
- Embedding settings in `.bmaplan` per-project — deferred (Phase 1: localStorage only).
- New pref categories beyond v1 set — additive in future sprints.

## Implementation summary

### Functions added (`proto/ui.html`)

- `getPref(dotPath, fallback)`, `setPref(dotPath, value)` — path-based get/set on in-memory draft.
- `loadSettingsDraft()`, `commitSettingsDraft()` — draft lifecycle.
- `migrateFromLegacy()` — called once on app init; idempotent (checks `bmaPlan.settings.v1`
  existence first).
- `openSettingsModal()`, `closeSettingsModal()`, `applySettings()`, `resetSettings()` — modal lifecycle.
- `#settings-modal` DOM: 4 tabs + tab content + Draft/Apply/Cancel/Reset buttons.
- `Ctrl+,` keydown handler.

### E2E (`proto/e2e_ui_test.py`)

NEW `_test_settings(page)` 13 sub-checks:
- A. `keyExists` — `bmaPlan.settings.v1` initialized on load
- B. `versionField` — `version === 1`
- C. `getPrefExists` — `getPref` function present
- D. `setPrefExists` — `setPref` function present
- E. `modalExists` — `#settings-modal` in DOM
- F. `tabCount` — 4 tabs present
- G. `shortcutWired` — `Ctrl+,` dispatches openSettingsModal
- H. `applyFn` — `applySettings` function present
- I. `resetFn` — `resetSettings` function present
- J. `migrateExists` — `migrateFromLegacy` function present
- K. `badJsonSafe` — setting corrupt JSON → load returns defaults (no throw)
- L. `wrongVersionSafe` — setting `version:99` → treated as incompatible → defaults
- M. `legacyPreserved` — legacy keys still in localStorage post-migration

Marker `SETTINGS_OK` wired at end of `main()`. Count: smoke +1 (total 13 sub-checks vs spike's 7).

## Files changed

| File | Change |
|---|---|
| `proto/ui.html` | `getPref`/`setPref`; `loadSettingsDraft`/`commitSettingsDraft`; `migrateFromLegacy`; `openSettingsModal`/`closeSettingsModal`/`applySettings`/`resetSettings`; `#settings-modal` DOM; `Ctrl+,` handler |
| `proto/e2e_ui_test.py` | NEW `_test_settings(page)` 13 sub-checks + marker `SETTINGS_OK` |

## Tests run

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PYCOMPILE_OK
python proto/e2e_ui_test.py smoke                          → PASS GREEN (SETTINGS_OK 13/13)
python proto/e2e_ui_test.py full                           → PASS GREEN
```

SETTINGS_OK: `{keyExists:T, versionField:T, getPrefExists:T, setPrefExists:T, modalExists:T,
tabCount:T, shortcutWired:T, applyFn:T, resetFn:T, migrateExists:T, badJsonSafe:T,
wrongVersionSafe:T, legacyPreserved:T, all:T}`.

## Phase 1 + forbidden-surface check

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNTOUCHED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNTOUCHED
- `buildSnapIndex`, `snap` engine — UNTOUCHED; `getPref('snap.enabled')` read at call-site boundary only
- `proto/server.py` — UNTOUCHED (pure client feature)
- `.bmaplan` schema — UNTOUCHED (settings live in `localStorage` only; not embedded in project file)
- Phase 1 boundary — kept (no legal verdict, no OCR, no AI)

## References

- PHASE_INDEX.md row `INV-2026-05-15-002`
- `docs/invent/settings-panel.md` — invention doc (research + approaches + scoring + spike rationale)
- `proto/sandbox/invent-settings-panel.html` — spike implementation (SPIKE_PASS 7/7 sub-checks);
  production adds bad-JSON + wrong-version checks (sub-checks K + L) + legacyPreserved (M) = 13 total
