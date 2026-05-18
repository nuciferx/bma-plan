# RUN_DEV_WEBSITE — dev-website: Static docs site for BMA-Plan

Date: 2026-05-17
Branch: main
Status: PASS — completed 2026-05-17
Commit hash: `1bf61ca`

## Goal

Promote the dev-website invention from spike to production. User said GO 2026-05-17 after reviewing
`docs/invent/dev-website.md` (PRIOR_ART_PARTIAL, Approach A, spike PASS 8/8 sub-checks).

Single static HTML micro-site bundled inside `proto/static/docs/` — accessible at `/static/docs/`
when BMA-Plan server is running. Exposes Thai manual pages, recent dev log entries, sprint cards,
and anti-pattern / troubleshooting docs. Inline micro-markdown renderer; fetches sibling
`content.json`; offline file:// fallback works. Exposes `window.__bmaDocs` for automated testing.

Source: PHASE_INDEX.md `ideas 2026-05-17` row (status `invent-pending-checkpoint → invent-done-go
→ done`). User GO 2026-05-17. Invent spike: `docs/invent/dev-website.md` +
`proto/sandbox/invent-dev-website.html`.

## Carry-over decisions from spike checkpoint

1. **Help menu wiring** — DEFERRED to a follow-up `/bma-ui-menu` sprint. This sprint
   preserves the "zero `ui.html` edits" boundary — the site is reachable at `/static/docs/`
   directly; the Help menu dropdown link comes later.

2. **Stale-bundle drift** — MITIGATED: `proto/static/docs/content.json` is committed as a
   first build (28 pages). Adding `python scripts/build_docs.py` to `/bma-sprint-finalize` is
   a separate small skill-update sprint (queued in NEXT_ACTIONS).

3. **Bundle size** — 28 pages ≈ 50 KB (well below 200 KB threshold). Sibling `content.json`
   model already chosen at spike time — no inline-JSON needed for production.

## Scope — IN

- NEW `proto/static/docs/index.html` (~190 LOC): single static HTML; inline ~80-line
  micro-markdown renderer (handles `##`, `**bold**`, `` `code` ``, `- list`); fetches
  `content.json` as JSON; exposes `window.__bmaDocs = {nav, pages}` for tests; offline
  `file://` fallback; `<title>BMA-Plan Docs</title>`.
- NEW `scripts/build_docs.py` (~120 LOC, stdlib-only): walks `proto/manual/*.md`,
  `log.md` (split by `## YYYY-MM-DD`, 12 most recent), `sprints/completed/**/RUN_*.md`
  (12 most recent), `docs/process/{ANTI_PATTERNS,TROUBLESHOOTING}.md`. Emits
  `proto/static/docs/content.json`.
- NEW `proto/manual/getting-started.md` — Thai: เริ่มต้นใช้งาน (~60 lines)
- NEW `proto/manual/set-scale.md` — Thai: ตั้งสเกล (~50 lines)
- NEW `proto/manual/measure-tools.md` — Thai: เครื่องมือวัด (~70 lines)
- NEW `proto/manual/export.md` — Thai: Export ข้อมูล (~50 lines)
- NEW `proto/manual/keyboard-shortcuts.md` — Thai: คีย์ลัด (~40 lines)
- NEW `proto/static/docs/content.json` — first build; 28 pages; 4 groups
  (Manual / Dev Log / Sprint Cards / Process Docs)

## Scope — OUT (forbidden)

- `proto/ui.html` — UNTOUCHED (Help menu link deferred)
- `proto/server.py` — UNTOUCHED (static serving already registered via `StaticFiles`)
- `proto/e2e_ui_test.py` (except adding `_test_docs_site` + marker)
- Any forbidden surfaces: `polyAreaM2`, `pdfToC`, `cToPdf`, `RS`, `snap`, `.bmaplan` schema

## Files changed

| File | Change |
|---|---|
| `proto/static/docs/index.html` | NEW — ~190 LOC static HTML docs site |
| `scripts/build_docs.py` | NEW — ~120 LOC stdlib build script |
| `proto/manual/getting-started.md` | NEW — Thai getting-started manual |
| `proto/manual/set-scale.md` | NEW — Thai set-scale manual |
| `proto/manual/measure-tools.md` | NEW — Thai measure-tools manual |
| `proto/manual/export.md` | NEW — Thai export manual |
| `proto/manual/keyboard-shortcuts.md` | NEW — Thai keyboard-shortcuts manual |
| `proto/static/docs/content.json` | NEW — first build (28 pages, 4 groups) |
| `proto/e2e_ui_test.py` | NEW `_test_docs_site` (~65 lines) + marker `DOCS_SITE_OK` |

## E2E marker: DOCS_SITE_OK (7 sub-checks)

| Sub-check | What is verified |
|-----------|-----------------|
| `titleOK` | Page `<title>` contains "BMA-Plan" |
| `contentJsonFetches` | `content.json` loads as JSON without network error |
| `groupCount` | `window.__bmaDocs.nav.length >= 4` (4 groups) |
| `manualSlugsPresent` | all 5 manual slugs present in nav: getting-started, set-scale, measure-tools, export, keyboard-shortcuts |
| `articleRenders` | clicking a nav link renders article text in `#article-body` |
| `navLinksCount` | `window.__bmaDocs.pages.length >= 10` nav links |
| `markdownProbe` | rendered article contains no raw `##` or `**` (markdown primitives parsed) |

Result: DOCS_SITE_OK 7/7 PASS

## Forbidden-surface check

- `polyAreaM2`, `polyMetrics`, `polySelfIntersects` — UNTOUCHED
- `pdfToC`, `cToPdf`, scale math — UNTOUCHED
- `buildSnapIndex`, `snap` engine — UNTOUCHED
- `proto/server.py` core endpoints — UNTOUCHED
- `.bmaplan` schema version stays 1 — UNTOUCHED
- `RS` constant — UNTOUCHED
- `proto/ui.html` — UNTOUCHED

## Tests run

```bash
python -m py_compile proto/server.py proto/e2e_ui_test.py  → PYCOMPILE_OK
python proto/e2e_ui_test.py smoke                          → PASS GREEN
python proto/e2e_ui_test.py full                           → PASS 41/41 GREEN
```

Zero regressions across all 39 pre-existing markers.

## Phase 1 scope check

- All forbidden surfaces — UNTOUCHED
- `.bmaplan` schema — UNTOUCHED (no schema change)
- `proto/server.py` — UNTOUCHED
- `proto/ui.html` — UNTOUCHED
- Phase 1 boundary — kept (no legal checker / OCR / AI)

## Known gaps / follow-ups

- Help menu wiring — deferred to follow-up `/bma-ui-menu` sprint
- `python scripts/build_docs.py` integration into `/bma-sprint-finalize` skill — separate small sprint
- Run `/bma-human-test` against new docs site to surface UX issues
