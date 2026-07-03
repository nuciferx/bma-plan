# SHIPS.jsonl — shipped-commit ledger (U3)

Machine-greppable, one JSON line per shipped commit-block. It is the single source of truth for
"what shipped when" so you never re-read multi-KB prose status docs to answer that.

**Schema (flat):**
`{"id", "date":"YYYY-MM-DD", "commits":[short-hashes], "area", "summary" (<=200 chars), "guards":[marker names], "closes":[finding/card ids], "docs": optional pointer}`

**Append discipline:** every ship appends exactly ONE line at finalize time — same facts as the commit
message. Append-only; never rewrite past lines. Query with `grep`/`jq` (e.g. `grep pagerot SHIPS.jsonl`).
Verify integrity anytime with `python scripts/reconcile_roadmap.py` (checks every referenced hash exists).
