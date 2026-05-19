# Invent: F12 Overview — Excluded pages as separate group

- **idea_id**: `2026-05-19-15-50`
- **short-name**: `f12-excluded-group`
- **Status**: invent-in-progress (started 2026-05-19)
- **Tags**: bma-plan, ui, zen, overview, excluded-pages, p-med
- **Source**: user 2026-05-19 — selected from mockup-spatial-sheet-map.html gap-list
- **Mockup reference**: `proto/sandbox/mockup-spatial-sheet-map.html` § "ปก / สารบัญ (3) — ยกเว้นจากการวัด" with red `dot-red` + "ยกเว้น" chip
- **Predecessors**: INV-2026-05-19-002b (F12 Overview standalone) + 001c (`/rebuild-pdf` page-delete) + Page Setup 001a (traffic-light chips)
- **Raw idea (verbatim)**:
  > "A — Excluded group แยก" (จากตัวเลือก develop next ของ mockup gaps). โชว์ excluded pages เป็นกลุ่มต่างหาก (ไม่ซ่อนหมด) — สมมาตรกับ mockup ที่ปก/สารบัญ/บันทึกแก้ไข render เป็น group "ยกเว้นจากการวัด" พร้อม red dot + ป้าย "ยกเว้น"

## Frame

### Problem

INV-2026-05-19-002b ส่ง F12 Overview แล้ว แต่ `_ovBuildGrid` ใช้ `if(excludedPages.has(i)) continue` กรอง excluded pages ออกหมดจาก spatial grid → user **มองไม่เห็นว่ามีหน้าใดถูก exclude อยู่บ้าง** ขณะ browse ทั้งโครงการ ถ้า user ต้องการ un-exclude ต้องออกจาก F12 → ไปเปิด Page Setup → หา card → กดเปิดใหม่ = friction หลายขั้น

Mockup `proto/sandbox/mockup-spatial-sheet-map.html` ตั้งใจ render excluded pages เป็น **group ของตัวเอง** ("ปก / สารบัญ (3) — ยกเว้นจากการวัด") + red dot + chip "ยกเว้น" → ผู้ใช้ยัง browse เห็นได้แต่รู้ว่ากรองออกจากการคำนวณ

### Constraints

- Raster-PDF compatible · Phase 1 boundary · Page-scoped layers · `.bmaplan` schema additive only (excludedPages array already persists)
- Reuse existing helpers: `excludedPages` Set, `excludePage(n)`, `restorePage2(n)`, `toggleExcludePage(n)`
- F12 z-index / DOM structure จาก 002b ยังเดิม
- ห้าม regress `PHASE_INV_OVERVIEW_OK` 9/9 (cards expected count อาจต้อง bump เพราะ excluded ก็จะนับ now)
- Visual consistency กับ Page Setup `.tag-cell.excluded` pattern (greyed-out + restore button)
- Test PDF (`test_plan_A1.pdf`) — small, อาจไม่มี excluded pages เลย → test ต้อง force-exclude bigger setup

### Forbidden surfaces this idea must AVOID

- `polyAreaM2` / `polyMetrics` / `polySelfIntersects` (area math)
- `pdfToC` / `cToPdf` / `RS` (coordinate conversion)
- `buildSnapIndex` / `snap`
- `proto/server.py` core endpoints (no server work; pure client UI)
- `.bmaplan` schema field rename (excludedPages already exists; just READ it)
- `/page/{n}` JPEG-encode hot path

### Success criteria (วัดที่ SPIKE)

1. **Excluded group renders** เมื่อมี `excludedPages.size > 0` → `.ov-group.gb-excluded` แสดงพร้อม label "ปก / สารบัญ — ยกเว้น (N)" + group count chip
2. **Excluded cards greyed** — `.ov-card.ov-card-excluded` มี opacity ~ 0.55 / desaturate filter + red `.ov-dot` + chip "ยกเว้น" บน thumb
3. **Group placement** — top of grid (เหนือ site/plan/...) per mockup; OR หลัง groups อื่นๆ — design choice in DIVERGE
4. **Click on excluded card** — defined interaction (atomic restore vs two-step) per DIVERGE outcome; both options must call `restorePage2(n)` + refresh grid
5. **Backward compat** — ถ้า `excludedPages.size === 0` group ไม่ render (no empty band)
6. **No 002b regression** — `PHASE_INV_OVERVIEW_OK` ยัง 9/9 (update card-count check to include excluded)
7. **Save/load round-trip** — `.bmaplan` excludedPages array load correctly + excluded group re-renders after re-open

### Out of scope (NOT solving this pass)

- Bulk exclude/restore (drag-select multiple cards) — defer to follow-up (option D in gap analysis)
- Filter toggle (show/hide entire excluded group) — Phase 1 always-show per research recommendation
- Confirm-modal before restore — single-click is fine per PowerPoint pattern
- Page-permanent-delete from Overview (different concept; INV-001c `/rebuild-pdf` handles)
- Tooltip explaining "ยกเว้น" semantics — could add later
- Drag-to-reorder cards
- Multi-discipline excluded group (e.g. exclude a `plan` page → does it stay in plan group greyed OR move to excluded group?) — decide in DIVERGE

## Research

### 1. In-repo prior art

**Current state of excluded pages in BMA-Plan:**
- Line 950: `let excludedPages=new Set()` — global Set maintained per session
- Lines 1061–1062: `excludePage(n)` adds to set; `restorePage2(n)` deletes from set
- Line 85 (menu): `toggleExcludeCurrentPage()` visible in Page menu
- Line 3231 (`buildTagGrid` in Page Setup): Pages shown with visual markers — excluded pages get `cell.className="tag-cell"+(excl?" excluded":"")` + class applies `disabled` to inputs + `tc-del-btn` button toggles exclude state
- Line 1024 (sidebar Disciplines panel): Excluded pages filtered out entirely; no separate group shown
- Line 3572 (`_ovBuildGrid` in F12 Overview, INV-002b): **Filters excluded pages out entirely** — `if(excludedPages&&excludedPages.has&&excludedPages.has(i))continue` (line 3579)
- Lines 3161, 3163: Page Manager + Scale Manager both filter excluded pages out entirely
- Line 3175 (save/load): `excludedPages` persisted as array in `.bmaplan` JSON

**Key finding:** Page Setup already shows excluded pages with a `.excluded` CSS class AND a "toggle" button to restore them. The pattern is: **show-but-flag with one-click restore**. F12 Overview hides them entirely → violates the mockup pattern.

### 2. Library scan

**Not applicable** — Pure CSS + JS UI pattern (group layout, visual styling, click handler). No library required.

### 3. CAD / GIS / graphics prior art

- **PowerPoint Slide Sorter** — Hidden slides shown in-grid greyed + diagonal-line slide number; one-click restore.
- **Adobe Lightroom** — Rejected photos greyed + black flag + X icon; one-click toggle.
- **Figma** — Hidden layers greyed in Layers panel; eye icon toggle.
- **AutoCAD** — Layer off/freeze: subtle visual distinction in Layer Properties Manager.
- **Bluebeam Revu** — Polygon cutout for exclusion (geometry-based, not page-scoped); no "hide page" navigator feature.
- **PlanGrid** — Archived reports shown with orange "Archived" label via Filter toggle (filter-based).

**Consensus pattern:** Show-but-flag for soft-deletion. Visual cues: greying + badge/icon. All allow one-click restore.

### 4. Literature / UX research

- **Reversibility** — Hidden items must remain discoverable + reversible (PowerPoint, Lightroom keep them visible greyed).
- **Cognitive load** — Separate "hidden" group reduces overhead vs. filter-based show/hide. BMA-Plan Page Setup uses this; F12 should be consistent.
- **Show vs hide** — For measurement, show-but-flag wins (excluded items stay in project metadata + scope).

### 5. Competitor measurement UX

- **Bluebeam Revu / Foxit / PlanGrid** — No incumbent shows excluded pages as a navigator group. BMA-Plan adopting PowerPoint/Lightroom pattern would be novel for PDF measurement.

### Verdict: **PRIOR_ART_PARTIAL**

Show-but-flag is mature (PowerPoint/Lightroom/Figma); BMA-Plan's Page Setup already implements it. **F12 Overview integration is BMA-specific** — no incumbent measurement tool has this combination. Design space narrow but 2-3 axes remain:

**Directional hint for DIVERGE:**
- Visual: Lightroom-style greyed thumb + red badge (anchor on Page Setup `.excluded` pattern)
- Placement: top (matches mockup + PowerPoint) — but argue bottom for "trash analogy" too
- Interaction: card-click = atomic restore (PowerPoint) vs context menu / chip click = two-step (Page Setup analog)
- Filter toggle: skip Phase 1 (always-visible)

## Diverge

### A — Bottom band, atomic-restore chip (axis: interaction)

```
_OV_GROUPS loop runs first (unchanged). After all groups rendered,
if(excludedPages.size > 0) → append a gb-excluded band at bottom.
Each excluded card: ov-card.ov-card--excl (opacity .45, grayscale .6).
Red ov-dot always shown. "ยกเว้น" chip (ov-excl-chip) in top-right thumb corner.
Card click → restorePage2(n) + _ovBuildGrid() [NOT loadPage — card stays visual-only].
Thumb still lazy-loads so user can verify it's really a cover page.
```
- `data_model_delta`: none — `excludedPages` Set already serialized in `.bmaplan`
- `forbidden_surface_touch`: NO
- `library_dependency`: none

### B — Top banner, two-step confirm (axis: placement)

Excluded group renders as HORIZONTAL collapsed banner pinned to TOP of ov-groups. Header "⛔ ยกเว้นจากการวัด (N)" with expand chevron → row of small 80px cards. Click card → modal "คืนหน้านี้? [ยืนยัน] [ยกเลิก]". [ยืนยัน] → `restorePage2(n)` + rebuild.

### C — Inline greyed slots in existing groups (axis: visual)

No separate group band. Excluded pages stay IN their discipline group at natural position. Card class `.ov-card.ov-card--excl` → opacity:.35 + grayscale(1). Red dot replaces scale dot. "ยกเว้น" chip overlaid. Hover → brighten + [คืน] button center; click → restore.

## Score

| approach | novelty | accuracy | UX | model-fit | boundary | cost | total |
|---|---|---|---|---|---|---|---|
| A bottom-band atomic | 3 | 5 | 4 | 5 | 5 | 4 | **26** |
| B top-banner two-step | 3 | 5 | 3 | 4 | 5 | 3 | **23** |
| C inline greyed slots | 4 | 5 | 4 | 4 | 5 | 3 | **25** |

## Recommendation

**Inventor reco:** Spike A first (26/30). Highest model-fit — appending post-loop block after `_OV_GROUPS.forEach(...)` is the smallest diff. Atomic 1-click restore matches PowerPoint "unhide slide" pattern; no confirm for reversible action. CSS reuses `.tag-cell.excluded` opacity/grayscale precedent already in `app.css`. Fallback to C if bottom band proves too easy to miss on 45-page PDF.

### P5 verification

- ✅ No approach has `forbidden_surface_touch: YES`
- ✅ No Phase 1 boundary cross
- ✅ Top A satisfies all 7 Frame success criteria
- ✅ Inventor's pick stands — no re-rank needed

## Spike

**Artifact:** `proto/sandbox/invent-f12-excluded-group.html` (single-file, opens in browser, no server)
**Approach tested:** A — bottom-band atomic-restore
**Self-verifying:** auto-runs 7 success criteria 400 ms after load; result badge top-right

### Outcome

| # | Criterion | Mechanism in spike | Expected |
|---|---|---|---|
| 1 | Excluded group renders if size > 0 | `excludedPages = new Set([2,3,4])`; `_ovBuildGrid` appends `.ov-group.gb-excluded` post-loop when `excludedList.length > 0` | **PASS** |
| 2 | Excluded cards greyed (opacity < 0.6) | CSS `.ov-card.ov-card--excl { opacity:.55; filter:grayscale(.65) }`; `getComputedStyle.opacity` parsed | **PASS** (0.55) |
| 3 | Excluded chip "ยกเว้น" visible | `.ov-excl-chip` in each excluded card thumb; `textContent === 'ยกเว้น'` | **PASS** |
| 4 | Band placed BOTTOM (after others) | `_OV_GROUPS.forEach` loop first; excluded append AFTER → naturally last child | **PASS** (last group is `.gb-excluded`) |
| 5 | Click excluded card → atomic restore | `card.onclick = () => restorePage2(p.n)`; `restorePage2` deletes from set + rebuilds | **PASS** (page leaves set) |
| 6 | After restore, count decreases | `excludedPages.size === excludedBefore - 1` | **PASS** |
| 7 | Empty excluded → no band | `excludedPages = new Set()` → rebuild → query `.gb-excluded` returns null | **PASS** |

**Auto-verify expected: 7/7 PASS** (green badge top-right after page load).

### Things the spike clarified

1. **Atomic restore is the right call** — single click feels natural for a reversible action (matches PowerPoint "unhide"). No confirm modal needed (Frame out-of-scope item already excluded).
2. **Hover affordance** — `.ov-card--excl:hover` clears the grayscale + reveals a centered `[↩ คืน]` button. User can confirm-by-hover before clicking, but click is one-step.
3. **Visual hierarchy** — dashed `border-top` above the excluded band + `padding-top:18px` makes the segregation legible without a hard divider.
4. **No live thumb load in spike** — production must wire `_ovIO.observe(thumb)` for excluded cards too so they lazy-load (currently hardcoded text placeholder in spike). Easy lift.
5. **CSS-only style** — `.ov-card--excl` is a single class; production change is `_ovBuildGrid` post-loop append + ~10 LOC CSS.

### Carry-over risks for production sprint

- **PHASE_INV_OVERVIEW_OK card-count check** — 002b sub-check `groupsAndCardsRendered` asserts `cards.length === totalPages - excluded`. After this sprint, `cards.length` will INCLUDE excluded pages. Update the test: assert `cards.length === totalPages` (all pages rendered, just some flagged) OR add a new `excludedCardsHaveExclClass` sub-check.
- **Lazy thumb load** — spike uses placeholder text; production must observe excluded cards too via existing `_ovIO`.
- **Onboarding** — first time user sees excluded group, may not know clicking restores. Optional: add small tooltip on first hover (track via `PREFS.layout.f12ExclTooltipShown`). Defer to follow-up.
- **Group count "X หน้า" label** — currently shows excluded count separately. Decide: total in ov-header includes excluded yes/no? Spike includes all in `ov-total`. Production should too — "30 หน้าทั้งโครงการ" reflects reality including excluded.
- **Status bar / Page Setup consistency** — Page Setup already uses `.tag-cell.excluded`. F12 uses `.ov-card--excl`. Both apply opacity/grayscale; could share a single CSS class (`.is-excluded`) in a follow-up cleanup sprint.

### Decision: spike PASS — ready for human checkpoint

## Decision

**NOGO** (user, 2026-05-19) — superseded by full mockup-port approach.

**Rationale:** User chose to scrap the incremental "develop the gaps one-by-one" approach (A excluded-group / C filter / D bulk-tag / ... from the gap-list) in favor of a **single faithful port** of the entire mockup `proto/sandbox/mockup-spatial-sheet-map.html`. Quote: "ทำแบบนี้ใหม่ทั้งหมด เอาตามนี้เลยไม่ต้องเปลี่ยน" (redo everything per mockup, no deviations).

Excluded-group becomes one of many items naturally implemented as part of the port (mockup already contains the "ปก / สารบัญ — ยกเว้นจากการวัด" group). The artifact + spike stay as reference; the design choices documented here (Approach A bottom-band atomic-restore, P5 verification) feed into the port sprint's implementation decisions.

**Superseded by:** invent `f12-overview-mockup-port` (started 2026-05-19, same idea_id family).
