# Bug Archive — the evolutionary loop's memory

`bug-archive.jsonl` is the feedback memory that makes the test+develop loop **self-improving** (see `docs/design/EVOLUTIONARY_TEST_LOOP.md`, pillar 4). One JSON object per line, one confirmed bug each.

## The contract
Every future test/hunt run **seeds from this file first** — "you have already missed these before; verify they are still guarded." This is the prompt-side analog of an evolutionary archive (Darwin-Gödel Machine): the loop never re-ships a bug class it has already learned. Because Claude weights are frozen, the "learning" lives here, not in the model.

## Fields
| field | meaning |
|---|---|
| `id` | stable bug id (e.g. `BUG-20260530-lpm-3`) |
| `date` | found date (absolute) |
| `severity` | CRASH / BROKEN / FRICTION / COSMETIC |
| `surface` | file + region where it lived |
| `summary` | one-line what-was-wrong |
| `repro` | how to reproduce |
| `guard_test` | the test that now PERMANENTLY guards it (green guard = the bug can't silently return) |
| `fixed_commit` | commit that fixed it (`null`/`pending` if not yet) |
| `status` | `fixed` or `open` |

## How to use
- **Before a release / hunt:** run every `guard_test` listed here. All must be green.
- **`status:open` items are the next fix targets.** Currently open: `lpm-7` (Apply order from `serverNum` not `simulateFlush` — two flush algos), `lpm-8` (95-thumb load no spinner). Both FRICTION, non-data-loss. (`lpm-9` pm-overlay hotkey-leak + Esc double-fire — fixed 2026-05-31 `3611e31`, guarded by `test_pm_modal_hotkeys.py`. `lpm-4` undo-desync was the last BROKEN — fixed 2026-05-30 `7d6f230`, guarded by `MR-undo-consistency`.)
- **When you confirm a NEW bug:** append a line with `status:"open"`; the moment you write its guard test, fill `guard_test`; on fix set `fixed_commit`+`status:"fixed"`. A bug is not "done" until it has a green guard_test — that is what stops regression.

## Seeded history (2026-05-30 full-program hunt)
10 bugs from the post-INV-2026-05-29-LPM hunt. **8 fixed** (lpm-1/2/3/4/5/6/9 + cfss-guard) with permanent guards — metamorphic MRs (`MR-save-roundtrip`/`MR-save-pending`/`MR-render-source`/`MR-dirty`/`MR-undo-consistency`), server `test_apply_page_mutations.py` T1–T7, EVOLT-3 cap-check, and `test_pm_modal_hotkeys.py` (lpm-9). **2 open** (lpm-7/8, both FRICTION non-data-loss). The 42-green unit suite missed all 10 — which is exactly why this archive + the metamorphic/PBT layer (`test_metamorphic_pages.py`, `test_pbt_measure.py`) now exist. Every BROKEN/data-loss bug from the hunt is now closed + guarded.
