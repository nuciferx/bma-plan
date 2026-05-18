# RUN_PHASE_I_B4 — Phase I-B4: Site Plan 6-step stepper widget

Date: 2026-05-17
Branch: main
Status: PASS — completed 2026-05-17
Commit hash: `91fede9`

## Goal

Add a 6-step guided stepper widget (`#site-stepper`) visible only on site pages. Guides users
through the full site-plan measurement workflow: Set Scale → Tag page as site → Project Info →
วาด ปกคลุมอาคาร → วาด ที่ว่าง/ซึมน้ำ → Place Markers. Each step shows status and links to the
relevant tool or panel action.

Source: PHASE_INDEX.md row `I-B4` (depends on I-B1 ✅).

## Scope — IN

- `#site-stepper` DOM widget: 6 steps, collapsible, site-page-only visibility.
- Step 1: Set Scale — check `pageTags[curPage].scale !== 'unknown'`; link to scale tool.
- Step 2: Tag = site — check `pageTags[curPage] === 'site'`; link to Page Setup.
- Step 3: Project Info — check `projectInfo.buildingClassification` set; link to Project Info.
- Step 4: ปกคลุมอาคาร — check at least one `building_coverage` polygon exists on page.
- Step 5: ที่ว่าง/ซึมน้ำ — check at least one `open_space` or `permeable_area` polygon on page.
- Step 6: Markers — check at least one marker exists on page.
- `updateSiteStepperUI()` function called by `updateBottomBar()` and `loadPage()`.
- Widget hidden via `display:none` when `pageTags[curPage] !== 'site'`; shown on site pages.
- New E2E marker `PHASE_I_B4_OK` with 10 sub-checks.

## Scope — OUT

- Stepper does not block actions — it is advisory only.
- No auto-advance logic; user drives the workflow.
- No persistence of stepper step state in `.bmaplan`.

## Implementation summary

### Functions added (`proto/ui.html`)

- `updateSiteStepperUI()` — reads current page state; sets `data-done` attribute per step;
  updates step status indicators. Called from `updateBottomBar()` and `loadPage()`.
- 6-step DOM block `#site-stepper` (additive HTML section, collapsible).
- `#site-stepper` visibility toggle in `updateSiteRibbon()` (already site-page-gated).

### Key design decisions

- Advisory-only: no blocking. User can skip any step.
- Steps derive their "done" state from existing page/project data — no new state variables.
- Widget collapses to a one-line header to minimize canvas space usage.

## Files changed

| File | Change |
|---|---|
| `proto/ui.html` | `#site-stepper` DOM; `updateSiteStepperUI()` fn; hook in `updateBottomBar`/`loadPage`; visibility in `updateSiteRibbon` |
| `proto/e2e_ui_test.py` | NEW `_test_phase_i_b4(page)` 10 sub-checks + marker `PHASE_I_B4_OK` |

## Tests run

```
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PYCOMPILE_OK
python proto/e2e_ui_test.py smoke                          → PASS GREEN
python proto/e2e_ui_test.py full                           → PASS GREEN
```

PHASE_I_B4_OK: 10 sub-checks all PASS.

## Phase 1 + forbidden-surface check

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNTOUCHED
- `pdfToC`, `cToPdf`, `RS`, scale math — UNTOUCHED
- `buildSnapIndex`, `snap` engine — UNTOUCHED
- `proto/server.py` — UNTOUCHED
- `.bmaplan` schema — UNTOUCHED (stepper state not persisted; reads existing project/page data only)
- Phase 1 boundary — kept (advisory tool only; no verdict, no rule engine)

## References

- PHASE_INDEX.md row `I-B4`
- `docs/design/SITE_PLAN_UI_MOCKUP.md` — stepper concept
