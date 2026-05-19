# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md)

---

# Latest: INV-2026-05-19-001b — ⌘K Command Palette (fuzzy page jump)

Branch: main
Date: 2026-05-19

## Result: PASS — py_compile PASS, smoke EXIT 0, full EXIT 0, JOURNEY_OK

## Commands

```bash
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3.11 proto/e2e_ui_test.py smoke                          → EXIT 0
python3.11 proto/e2e_ui_test.py full                           → EXIT 0
bma-human-journey-tester (real 45-page permit PDF)             → JOURNEY_OK
```

## New Marker: PHASE_INV_PALETTE_OK (10/10)

| Sub-check | Result |
|---|---|
| helpersAndDomExist | PASS |
| paletteShownAndFocused | PASS |
| defaultPrefilterShows | PASS |
| numberFilterWorks | PASS |
| nameFilterWorks | PASS |
| tagFilterWorks | PASS |
| moveSelWorks | PASS |
| jumpClosesPalette | PASS |
| midDrawGuard | PASS |
| escClosesPalette | PASS |

## Pre-existing Markers

All pre-existing smoke markers GREEN — no regressions. `PHASE_INV_ZEN_OK` 10/10 still PASS (001a Zen Mode unaffected).

## Full Run

EXIT 0. `ANNOT_OK`, `PERSIST_OK`, `REAL_OK` GREEN. No regressions on export/rotation/real-PDF paths.

## Human Journey Test

`JOURNEY_OK` — 13/13 spec steps PASS. Zero JS errors throughout. One FRICTION finding filed:
- HT-Z-3: empty-state when filtering by Thai tag on an untagged PDF lacks hint that Page Setup tagging is needed first

Filed to `PHASE_INDEX.md` `### zen-mode 2026-05-19` backlog.

---

# Previous: INV-2026-05-19-001a — Zen Mode + Sheet Minimap

Branch: main
Date: 2026-05-19

## Result: PASS — py_compile PASS, smoke EXIT 0, full EXIT 0, JOURNEY_OK

## Commands

```bash
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3.11 proto/e2e_ui_test.py smoke                          → EXIT 0 (PHASE_INV_ZEN_OK 10/10; all pre-existing GREEN)
python3.11 proto/e2e_ui_test.py full                           → EXIT 0
bma-human-journey-tester (real 45-page permit PDF)             → JOURNEY_OK (0 CRASH/BROKEN; HT-Z-1 + HT-Z-2 filed)
```

## Marker: PHASE_INV_ZEN_OK (10/10)

| Sub-check | Result |
|---|---|
| helpersAndDomExist | PASS |
| bodyZenClassAdded | PASS |
| canvasGE92Pct (actual: 94.44% vh) | PASS |
| hudHasScaleToolPageSaveLayer | PASS |
| minimapCellCountMatch | PASS |
| lazyLoadActive | PASS |
| f11ExitsZen | PASS |
| escExitsZen | PASS |
| statusHiddenInZen | PASS |
| prefsRoundTrip | PASS |

<!-- older Previous (Ribbon Cleanup + Page Setup trilogy) archived to docs/archive/test-history-2026-05-09.md -->
