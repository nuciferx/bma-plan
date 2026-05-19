# Invent: F12 Overview — Mockup-spatial-sheet-map faithful port

- **idea_id**: `2026-05-19-16-00`
- **short-name**: `f12-overview-mockup-port`
- **Status**: invent-in-progress (started 2026-05-19)
- **Tags**: bma-plan, ui, zen, overview, mockup-port, p-high
- **Source**: user 2026-05-19 — "ทำแบบนี้ใหม่ทั้งหมด เอาตามนี้เลยไม่ต้องเปลี่ยน" (after NOGO of f12-excluded-group)
- **Mockup reference (the spec):** `proto/sandbox/mockup-spatial-sheet-map.html` — port verbatim
- **Predecessors:** INV-002a (top bar, kept) + INV-002b (F12 Overview, **to be REPLACED**) + Page Setup 001a (excluded pattern)
- **Supersedes:** `f12-excluded-group` (NOGO — incremental gap-by-gap approach scrapped in favor of full port)
- **Raw idea (verbatim):**
  > "ทำแบบนี้ใหม่ทั้งหมด เอาตามนี้เลยไม่ต้องเปลี่ยน" (mockup-spatial-sheet-map.html) — redo F12 Overview entirely per mockup, no deviations.

## Research

### Verdict: **PRIOR_ART_MATURE** (skip-path)

**Rationale:** This sprint is a **faithful port** of an *in-repo* prior-art artifact. The mockup `proto/sandbox/mockup-spatial-sheet-map.html` was authored 2026-05-19 as the visual spec for the entire spatial-sheet-map direction, then partially adopted via INV-002a (top bar) + INV-002b (basic grid). The user has now explicitly directed: do not deviate, port the mockup as-is.

When prior art is **in-repo and user-blessed**, the /bma-invent pipeline's purpose (diverge + score + spike) is redundant — there's nothing to invent. The design IS the mockup. Per /bma-invent skill spec:

> If verdict = `PRIOR_ART_MATURE` → SKIP phases 3-6. Go directly to phase 7 CHECKPOINT with a "use prior art" recommendation: write a normal sprint card that adopts the existing solution. This is a WIN exit, not a failure.

**Phases 3 FRAME / 4 DIVERGE / 5 SCORE / 6 SPIKE are intentionally skipped.** The implementation itself happens during the regular sprint (post-GO), not a sandbox spike.

### Mockup → Live-app delta map (what the port sprint must do)

| Mockup feature | Current live (002b) | Port action |
|---|---|---|
| `.spatial-map` container w/ padding 60px 80px 100px | `#overview-content` padding 24px 36px 40px | Bump padding to mockup's |
| `.group-band` margin-bottom 54px | `.ov-group` gap 28px in flex | Change `gap` → margin-bottom per group; widen |
| `.group-label` font-size 15px, gap 14px | 13.5px, gap 12px | Match mockup |
| `.group-grid` `grid-template-columns: repeat(auto-fit, 180px)` gap 16px | `auto-fill, 170px` gap 12px | Bump card width 170→180; gap 12→16; `auto-fit` not `auto-fill` |
| `.sheet` card 180px white bg + dark border | `.ov-card` 170px dark bg | **Repaint** — white card on dark scroll bg per mockup (more contrast); hover scale 1.04 instead of translateY only |
| `.sheet-thumb` 124px height white interior | 108px height dark | Bump 108→124; light interior with `d-site/d-plan/d-plan-2/d-elev/d-section/d-detail/d-sys` discipline-tinted backgrounds |
| 7 group bands: site/title/plan/elev/section/detail/sys (with mockup-specific icons + Thai labels) | 6 groups: site/plan/elev/section/detail/none | **Add `title` group** (covers "ปก / สารบัญ — ยกเว้นจากการวัด"); **add `sys` group** ("⚡ งานระบบ"); keep others; rename labels per mockup verbatim ("📐 ผังพื้น 14 หน้า · ชั้นใต้ดิน → ดาดฟ้า" etc.) |
| Status chips: "พร้อม" green / "ตรวจ scale" amber / "ยังไม่วัด" red / "auto scale" amber / "ยกเว้น" gray | Single dot color (green/amber/red) | Replace plain dot with text-chip + dot combo: `<div class="chip"><div class="dot dot-X"></div>LABEL</div>` |
| Object-count chip top-right `.obj-chip` | `.ov-obj` similar | Keep; restyle |
| Banner: "💡 Mockup ... · 45 หน้าทั้งโครงการบน infinite canvas เดียว · คลิก sheet ใดก็ได้เพื่อ zoom เข้า · กด ⌘K เพื่อค้นหา" | None | **Add banner** above `.spatial-map` (sticky or top-fixed) |
| Active sheet: green border + box-shadow | Same pattern, slightly different green | Match mockup exactly |
| Hover: `translateY(-4px) scale(1.04)` + box-shadow `0 10px 28px rgba(59,130,246,.35)` | `translateY(-2px)` only | Match mockup |
| Group label color coding | Present but only via `.gb-X .ov-group-label{color}` | Already done — verify all 7 groups have colors per mockup CSS (gb-site green / gb-title gray / gb-plan blue / gb-elev amber / gb-section purple / gb-detail cyan / gb-sys red) |
| Excluded pages: in "ปก / สารบัญ" group with `.dot.dot-red` + chip "ยกเว้น" | Filtered out entirely via `_ovBuildGrid` `continue` | Render them; replace the `continue` skip with assignment to title-or-derived-excluded group |
| Card click → `enterFocus(n)` | `_ovCardClick(n)` = closeOverview + loadPage | Equivalent — keep current behavior, rename to match if desired |
| Ghost zoom hint near cursor (bottom 62px) | None | Defer (Phase 1 boundary — not measurement-critical) |

### Estimated scope

- `proto/ui.html`: replace `_OV_GROUPS` config (6 → 7 groups with mockup labels) + replace `_ovBuildGrid` chip logic (dot → chip+dot) + remove excluded `continue` + add banner element + minor card markup tweaks. ~90 LOC delta.
- `proto/static/css/app.css`: rewrite `.ov-*` classes to match mockup `.sheet`/`.group-*` styling (white card bg, scale-1.04 hover, larger padding, group-band margin, banner styling, status chip pill). ~120 LOC delta.
- `proto/e2e_ui_test.py`: update `_test_inv_overview_mode` — `groupsAndCardsRendered` sub-check now expects all pages rendered (no excluded filter); add `excludedRendersWithChip` sub-check; bump `PHASE_INV_OVERVIEW_OK` from 9 → 10-11 sub-checks. ~30 LOC delta.

Total: **~240 LOC**. Single sprint-sized.

### Constraints carried forward (from earlier framing work)

- Phase 1 boundary · raster-PDF compatible · page-scoped layers · `.bmaplan` schema additive only
- Forbidden surfaces: `polyAreaM2` / `polyMetrics` / `polySelfIntersects` / `pdfToC` / `cToPdf` / `RS` / `snap` / `proto/server.py` / `.bmaplan` schema rename — none touched
- No new lib dep (Fuse.js already in)
- Test PDF (`test_plan_A1.pdf`) small — must force-tag and force-exclude in test setup to verify the 7 groups all render conditionally
- HT-7 scale gate preserved (Overview doesn't enter measure mode, gate not triggered)
- F11 Zen + ⌘K palette + F12 toggle all preserved from 002a/b

## Diverge

**SKIPPED** per PRIOR_ART_MATURE — no divergent approaches needed. The mockup is the spec.

## Score

**SKIPPED** per PRIOR_ART_MATURE.

## Recommendation

**Adopt prior art:** port mockup-spatial-sheet-map.html verbatim into live app, replacing INV-002b implementation. Single sprint card.

## Spike

### Outcome

**Artifact:** `proto/sandbox/invent-f12-overview-mockup-port.html` — created 2026-05-19 on user request ("มีทำ invent ให้ดู ก่อนไหม" — "is there a preview to see first?"). Originally planned to skip per PRIOR_ART_MATURE rule, but user wanted a concrete preview before committing to ~240 LOC of production work.

**What it demonstrates:**
- All 7 group bands in mockup order (site / title / plan / elev / section / detail / sys)
- 45 mock pages distributed per RAMA4 permit structure (1 site / 3 title / 14 plan / 4 elev / 3 section / 8 detail / 12 sys)
- Excluded pages (2/3/4) integrated into title group with chip "ยกเว้น" — NOT a separate band
- 5 status states with chip+dot combo (พร้อม / ตรวจ scale / ยังไม่วัด / auto scale / ยกเว้น)
- 180px white sheet cards on dark dotted-grid bg; 124px discipline-tinted thumb
- Hover transform `translateY(-4px) scale(1.04)` + accent shadow per mockup CSS
- Banner with mockup-verbatim text above grid
- Group label colors per discipline (7 colors)
- Object-count chips top-right where objCount > 0

**Self-verifying:** auto-runs 10 acceptance criteria 400 ms after load; result badge top-right.

**Expected: 10/10 PASS** — the spike matches the production sprint's `PHASE_INV_OVERVIEW_PORT_OK` planned sub-checks 1-for-1 (so passing the spike = de-risking the sprint).

**How to use:** open `proto/sandbox/invent-f12-overview-mockup-port.html` in browser → see the full ported layout → verify visual matches expectation → confirm GO is still correct → proceed to 002c sprint.

## Decision

**GO** (user, 2026-05-19) — promote to single sprint card INV-2026-05-19-002c.

**Sprint:** INV-2026-05-19-002c — F12 Overview faithful port from mockup-spatial-sheet-map.html
**Depends-on:** INV-002b ✅ (002c replaces 002b's implementation in-place)
**Scope skill:** `/bma-ui-scope` (UI region: canvas-ui standalone mode — same surface as 002b)
**Estimated LOC:** ~240 (proto/ui.html ~90, app.css ~120, e2e_ui_test.py ~30)
**Success marker:** `PHASE_INV_OVERVIEW_PORT_OK` (10-11 sub-checks; supersedes 002b's `PHASE_INV_OVERVIEW_OK` 9/9 with port-specific assertions)

**Implementation guide for the sprint:** see § Research → "Mockup → Live-app delta map" table above for the row-by-row port plan.

**Hard rules for the sprint:**
- Do NOT redesign — port mockup verbatim. Any deviation requires user check-in.
- Banner text exactly: "💡 45 หน้าทั้งโครงการบน infinite canvas เดียว · คลิก sheet ใดก็ได้เพื่อ zoom เข้า · กด ⌘K เพื่อค้นหา"
- 7 groups in order: site / title / plan / elev / section / detail / sys (per mockup section order)
- Excluded pages go in `title` group (where mockup puts them) with chip "ยกเว้น" — do NOT make a separate excluded group (that was f12-excluded-group's approach; mockup integrates them into title)
- Card click → existing `_ovCardClick(n)` behavior preserved (exit overview + loadPage)
- Forbidden surfaces untouched

**Re-frame attempt count:** 1 (no reshape needed; mockup is the spec).
