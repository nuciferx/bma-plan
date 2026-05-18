# RUN_PACK_G_SANDBOX_TEST — Sprint Card

**Sprint name:** Pack G — Sandbox Test Pre-Release Gate
**Branch:** main
**Date:** 2026-05-15
**Outcome:** PASS (DOCS-ONLY)

---

## Summary

สร้าง pre-release gate 3 ชิ้นใน `.claude/`:
1. Skill `/bma-sandbox-test` — pre-release gate runner
2. Subagent `bma-sandbox-journey-tester` (sonnet) — Tier1+Tier2 per-file journey driver
3. Subagent `bma-issue-triager` (sonnet) — root-cause cluster + propose-first specialist drafting

First run (same session) against `sandbox/251121_CHH_Submission_REV2 - Copy.pdf` (90.8 MB):
- Tier1: FAIL — HTTP 413 (`MAX_UPLOAD_BYTES = 80 MB` in `proto/server.py:51`)
- Tier2: SKIPPED
- Verdict: `SANDBOX_TEST_ISSUES` (no CRASH)
- Filed: SB-2026-05-15-001 BROKEN (upload cap) + SB-2026-05-15-002 FRICTION (UX message)

No app code touched. No marker test rerun. Test baseline unchanged (smoke 20/20, full 22/22 GREEN from Phase I-B2b).

---

## Files Changed

| File | Change |
|---|---|
| `.claude/skills/bma-sandbox-test/SKILL.md` | NEW — skill `/bma-sandbox-test` |
| `.claude/agents/bma-sandbox-journey-tester.md` | NEW — sonnet subagent, Tier1+Tier2 journey |
| `.claude/agents/bma-issue-triager.md` | NEW — sonnet subagent, cluster+propose |
| `CLAUDE.md` | EDITED — Pack G sections in skills + subagent tables + invariant |
| `AGENTS.md` | EDITED — step 8 Pre-Release Gate |
| `docs/status/PHASE_INDEX.md` | EDITED — SB-001/SB-002 queue rows + sandbox 2026-05-15 sub-block |

---

## Phase 1 Scope Check

- polyAreaM2 / polyMetrics / polySelfIntersects — unchanged
- pdfToC / cToPdf / RS / scale math — unchanged
- proto/server.py core endpoints — unchanged (MAX_UPLOAD_BYTES discovery filed as SB-001, fix next sprint)
- .bmaplan schema — additive only, not touched
- No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

---

## Tests

No tests run. Docs/.claude-only sprint. No `proto/` source modified.

Baseline (Phase I-B2b, commit `92c4f81`):
```
py -3.12 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
py -3.12 proto/e2e_ui_test.py smoke                          → PASS 20/20
py -3.12 proto/e2e_ui_test.py full                           → PASS 22/22
```

---

## Known Gaps / Follow-ups

- SB-2026-05-15-001 BROKEN: raise `MAX_UPLOAD_BYTES` to ≥128 MB. Top of queue. Requires `/bma-check-forbidden` + `full` E2E.
- SB-2026-05-15-002 FRICTION: upload-cap UX message. After SB-001. Requires `/bma-ui-scope`.
- Subagents `bma-sandbox-journey-tester` + `bma-issue-triager` need session restart before `subagent_type` enum resolves to them. Fallback: general-purpose agent with inlined prompts (proven this session).
