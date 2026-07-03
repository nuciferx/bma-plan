# RELEASE_RITUAL.md — BMA-Plan lite (V2 U6)

The steps to cut a distributable build. Tooling automates the mechanical parts;
the **gated** steps need a human decision and are never run by the autonomous loop.

## Pre-flight (automated — must all be green before tagging)

```bash
# 1. executable truth + roadmap reconcile + full suite
python lite/tests/run_all_tests.py            # preflight runs check_executable_truth + reconcile, then all tiers

# 2. ledger + derived docs in sync
python scripts/gen_status_docs.py --check     # exit 0 = PATCH_SUMMARY/TEST_RESULT/FINAL_REPORT/LATEST_STATUS match SHIPS.jsonl
python scripts/gen_changelog.py --check       # exit 0 = docs/CHANGELOG.md matches SHIPS.jsonl
python scripts/reconcile_roadmap.py           # exit 0 = no lying roadmap rows
```

## Gated steps (human decides — NOT autonomous)

1. **`/lite-sandbox-test`** on every real customer PDF in `sandbox/` — must return
   `SANDBOX_TEST_PASS` (or ISSUES with all CRASH resolved). This is the pre-release
   gate; a build is never handed off on an unresolved CRASH.
2. **Golden real-project acceptance** (U6): open the 1–2 pinned customer `.bmaplan`
   files, verify the m² totals still match the recorded golden values (catches
   regressions synthetic tests never see). *(Golden fixtures not yet pinned — first
   release that adds them closes this.)*
3. **Regenerate CHANGELOG + tag:**
   ```bash
   python scripts/gen_changelog.py --write
   git add docs/CHANGELOG.md && git commit -m "docs: changelog for lite-vX.Y"
   git tag lite-vX.Y
   ```
4. **Build** via the PyInstaller path (LITE-7, still deferred) or the current run path.
5. **Dogfood** (U6 weekly ritual): use the app on a real job ~30 min → file findings
   through `/bma-bug-report`. Substitutes for the telemetry Phase 1 has no way to collect.

## Discipline

- The ledger (`docs/status/SHIPS.jsonl`) is the single source: append one line at
  each ship's finalize, then `gen_status_docs --write` + (at release) `gen_changelog --write`.
  Do **not** hand-curate the CHANGELOG or the 4 derived docs — regenerate them.
- `CURRENT_STATUS.md` (one-liner) and `log.md` (context/lessons) stay hand-written.
- Tagging and the sandbox/golden gates are human calls — the `/bma-dev-loop` and
  `/loop` never tag a release or hand off a build on their own.
