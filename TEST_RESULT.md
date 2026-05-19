# TEST_RESULT.md — Latest Test Result

> Full test history: [docs/archive/test-history-2026-05-09.md](docs/archive/test-history-2026-05-09.md)

---

# Latest: INV-2026-05-19-001c — Zen+Palette FRICTION polish (HT-Z-1 + HT-Z-2 + HT-Z-3 bundle)

Branch: main
Date: 2026-05-19

## Result: PASS — py_compile PASS, smoke EXIT 0, full EXIT 0; TEST-H SKIPPED (no-test rationale below)

## Commands

```bash
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3.11 proto/e2e_ui_test.py smoke                          → EXIT 0
python3.11 proto/e2e_ui_test.py full                           → EXIT 0
```

## No-Test-H Rationale

Per AGENTS.md: sub-200-LOC polish sprint with full marker coverage of all changed branches. `PHASE_INV_POLISH_001C_OK` 5/5 directly exercises all 3 changed code paths (page-name direct read, amber scale chip, Thai-tag hint). All changes are UI label / CSS class tweaks — no new interactive flow requiring end-to-end journey validation. Prior JOURNEY_OK baseline (001b, 13/13 steps) remains valid.

## New Marker: PHASE_INV_POLISH_001C_OK (5/5)

| Sub-check | Result |
|---|---|
| hudReadsPageNamesDirectly | PASS |
| unverifiedScaleAmber | PASS |
| manualScaleNotAmber | PASS |
| thaiTagHintShown | PASS |
| hintAbsentWhenTaggedOrNoThai | PASS |

## Pre-existing Markers

`PHASE_INV_ZEN_OK` 10/10 — no regression. `PHASE_INV_PALETTE_OK` 10/10 — no regression. All other pre-existing smoke markers GREEN.

## Full Run

EXIT 0. `ANNOT_OK`, `PERSIST_OK`, `REAL_OK` GREEN.

---

# Previous: INV-2026-05-19-001b — ⌘K Command Palette (fuzzy page jump)

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

## Marker: PHASE_INV_PALETTE_OK (10/10)

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

`PHASE_INV_ZEN_OK` 10/10 still PASS (001a unaffected). All pre-existing markers GREEN.

Human journey: JOURNEY_OK — 13/13 spec steps PASS; 0 JS errors; HT-Z-3 filed.

<!-- 001a Zen Mode + older entries archived to docs/archive/test-history-2026-05-09.md -->
