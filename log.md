# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-05-19 — INV-2026-05-19-001a Zen Mode + Sheet Minimap — PASS (branch: main)

**What changed:** Additive fullscreen-canvas "Zen Mode" feature across three files. `proto/static/css/app.css`: `body.zen` chrome-hide rules, `.zen-hud-tl/tr/bl` corner HUD styles, `.zen-minimap` 5-col lazy-loaded grid, `.zen-onboarding-toast` auto-dismiss, `.zen-exit-chip` style (~50 LOC). `proto/ui.html`: `PREFS.layout.zenMode` + `PREFS.layout.zenOnboarded` state; `applyLayoutPrefs()` extended with `body.zen` toggle + lazy minimap build + HUD sync hook; new helpers `toggleZenMode()`, `_zenBuildMinimapIfNeeded()` (IntersectionObserver-based), `_zenUpdateMinimapActive()`, `_zenToggleMinimap()`, `_zenSyncHud()`; View menu "⛶ Zen Mode" item; F11 toggle + Esc-exit-zen keydown branches; 3 `.zen-hud` corner DOM elements + `#zen-minimap` + `#zen-onboarding-toast`; MutationObserver bridges status-bar → HUD (~180 LOC). `proto/e2e_ui_test.py`: new `_test_inv_zen_mode(page)` 10 sub-checks + `PHASE_INV_ZEN_OK` marker; fixed 2 pre-existing baseline drifts from polish commit `0e4e851` (`#active-layer-select` removed from MAIN_UI_OK required-visible list; `#scale-badge` downgraded visible→exists) (~110 LOC).

**Why:** User idea 2026-05-19-01-36 ("ทำ ui แบบ fullscreen ให้เหลือแต่ canva และมีแค่ top เมนู") ran through the `/bma-invent` pipeline (PICK → RESEARCH → FRAME → DIVERGE → SCORE → SPIKE → CHECKPOINT) and was promoted `invent-done-go`. Zen Mode maximises canvas to ~94% viewport height for high-density measurement work by hiding ribbon, left panel, right panel, status bar, and summary widget, replacing them with three small corner HUDs (TL = scale + tool, TR = objects + layer, BL = save state) and a lazy-loaded sheet minimap. The IntersectionObserver lazy-load strategy was chosen specifically to avoid the malloc anti-pattern documented in `AGENTS.md` — only visible thumb cells trigger fetch, preventing concurrent render overload. Sprint was split into 001a (Zen Mode, this sprint) + 001b (⌘K command palette, next iteration) per the SPLIT_REQUIRED boundary.

**Files touched:**
- `proto/static/css/app.css`: ~50 LOC — `body.zen` chrome rules, HUD corner styles, minimap grid, onboarding toast, exit chip
- `proto/ui.html`: ~180 LOC — PREFS state, helpers, View menu item, F11/Esc handlers, HUD + minimap DOM, MutationObserver
- `proto/e2e_ui_test.py`: ~110 LOC + 2-line baseline fix — `_test_inv_zen_mode` (10 sub-checks), `PHASE_INV_ZEN_OK` marker, baseline drift fixes

**Tests:**
```
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3.11 proto/e2e_ui_test.py smoke                          → EXIT 0
  PHASE_INV_ZEN_OK 10/10 PASS (canvas 94.44% vh; F11 + Esc exit; minimap lazy-load; PREFS round-trip; status hidden)
  all pre-existing markers GREEN (no regressions)
python3.11 proto/e2e_ui_test.py full                           → EXIT 0
bma-human-journey-tester: JOURNEY_OK (real 45-page permit, zero CRASH/BROKEN)
  HT-Z-1 filed: transient stale HUD page name during fast minimap nav (MutationObserver timing)
  HT-Z-2 filed: auto-unverified scale not visually distinguished in HUD chip
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` core endpoints — UNCHANGED (no server edit)
- ✅ `.bmaplan` schema — ADDITIVE only (`PREFS.layout.zenMode` + `PREFS.layout.zenOnboarded`; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- HT-Z-1: transient stale HUD page name during fast minimap nav — MutationObserver timing; filed to `PHASE_INDEX.md` `### zen-mode 2026-05-19`
- HT-Z-2: auto-unverified scale not visually distinguished in HUD chip — amber styling deferred to 001b or polish sprint
- INV-2026-05-19-001b (⌘K command palette) queued as next sprint for the loop

---

## 2026-05-19 — Ribbon Cleanup Polish — PASS (branch: main)

**What changed:** Pure cosmetic ribbon cleanup in two files. `proto/static/css/app.css`: `body { font-size: 16px }` reverted to `14px` (16px caused inherited-element layout shifts). `proto/ui.html`: (1) `#scale-badge` hidden via `style="display:none"` — stays in DOM for `updateAnalyseUI()` and status bar already shows scale state; (2) `#active-layer-select` ribbon-group hidden via `style="display:none"` on wrapping `.ribbon-group`, flanking `<div class="rdiv">` dividers removed — the `<select>` element preserved for `activeLayerLabel()` / `getActiveLayer()` / `setActiveLayerMenu()` / `updateActiveLayerControl()` / draw functions; (3) `#btn-report` Review button rewrapped from bare `.ribbon-group` into `.ribbon-group.rsection` with `.rlbl` + `.rrow` to match all other ribbon groups and prevent flex-stretch to full 78px height.

**Why:** Real-Chrome browser testing exposed three visual defects: the "ยังไม่ตั้ง Scale" red pill in the ribbon duplicated info already in the status bar Scale field (post-HT-19 reorder); the "Layer: พื้นที่ย่อย ⌄" dropdown in the ribbon broke the uniform 60px button row and is redundant with the Right panel Layers tab; the Review button icon appeared disproportionately large because it sat in a bare `.ribbon-group` without `.rsection`/`.rrow` wrapper. Body 16px (set earlier the same session to match mockup default) caused text in inherited-font-size elements to push past their container bounds — 14px is the safe baseline.

**Files touched:**
- `proto/static/css/app.css`: `body { font-size: 16px }` → `14px` (1-line revert)
- `proto/ui.html`: `#scale-badge` `display:none`; `.ribbon-group` wrapping `#active-layer-select` `display:none` + 2 `rdiv` dividers removed; `#btn-report` rewrapped in `.rsection` + `.rlbl "📊 REVIEW"` + `.rrow` + leading `rdiv`

**Tests:**
```
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS (no syntax errors)
python3.11 proto/e2e_ui_test.py smoke  → PASS (earlier in session; env port-8011 bind conflict
  developed later from leftover python processes; resolved via taskkill but env remains flaky).
  All 18 markers GREEN incl. MAIN_UI_OK / MENU_OK / PROJECT_OK / SELECT_OK / PATH_GEOMETRY_OK.
full not required: no export/save-load/rotation/real-PDF/snap/layer-model changes.
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` core endpoints — UNCHANGED (no server.py edit)
- ✅ `.bmaplan` schema — UNCHANGED (no schema edit)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- Smoke env flakiness (port 8011 hangs from leftover processes) — file as separate `dev-env-cleanup` follow-up; not blocking.
- Active-layer-select hidden — verify Right panel Layers tab `setActiveLayer` flow on real 45-page PDF still works (HT-25 should cover).
- Manual test: open in real Chrome, confirm ribbon row reads `TOOL | SCALE | พื้นที่ | LINES | MARKER | HELPERS | EDIT | REVIEW` with no gap where Layer select used to be.

<!-- sessions before 2026-05-19 Ribbon Cleanup are archived to docs/archive/log-2026-05-18.md -->
