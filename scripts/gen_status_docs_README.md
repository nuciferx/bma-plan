# gen_status_docs.py — ledger-first status-doc generator (V2 §U3)

Regenerates the **mechanical body** of 4 derived docs from `docs/status/SHIPS.jsonl`
(the single source of truth), replacing the ~200-260K-token `bma-sprint-writer` agent.

**Generates (per ship, newest-first — last ledger line = "Latest"):**
- `PATCH_SUMMARY.md` — id · date · area · summary · commit hashes+subjects · files-touched (unioned from `git show --name-only`).
- `TEST_RESULT.md` — `guards[]` markers as a PASS table + `closes[]`; adds "lite-only, proto untouched" when the area is lite.
- `FINAL_REPORT_FOR_CHATGPT.md` — one-paragraph outcome from `summary` + `closes`.
- `docs/status/LATEST_STATUS.md` — the machine table only (id / date / area / guards / commits).

**GEN-marker contract:** only the region between `<!-- GEN:START gen_status_docs -->` and
`<!-- GEN:END -->` is ever rewritten. Everything outside (PATCH/TEST/REPORT header archive-pointers
+ footer archive comments; LATEST_STATUS title, intro, and all prose) is preserved verbatim.
Markers are inserted on first run if absent. **Never touches** `log.md` or `CURRENT_STATUS.md` (hand-written).

**Modes:** `--check` regenerates in memory and diffs vs disk (exit 1 on drift — for runner preflight);
`--write` writes. Idempotent: output is derived from the ledger (+git), never `now()`, so re-running is a byte-identical no-op.

**New finalize discipline:** append exactly ONE line to `SHIPS.jsonl`, then run
`python scripts/gen_status_docs.py --write` — instead of spawning `bma-sprint-writer`.
