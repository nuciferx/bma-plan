# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-05-19 — INV-2026-05-19-001b ⌘K Command Palette — PASS (branch: main)

**What changed:** Additive ⌘K Command Palette feature across three files. `proto/static/css/app.css`: `.cmd-palette` fixed-center modal (z-index 9500, above zen overlays at 1500), input field, results list, hint bar, color-coded tag chips (site/plan/elev/section/detail) — ~35 LOC appended. `proto/ui.html`: 5 new helpers (`togglePalette`, `closePalette`, `filterPalette`, `_palJumpToIdx`, `_palMoveSel`, `_palEsc`); `Ctrl+K`/`Cmd+K` keybind with mid-draw guard (`mPts.length===0`); ArrowDown/Up/Enter/Esc keydown branch placed BEFORE inInput guard so palette input does not swallow nav keys; View menu "🔍 ค้นหาหน้า (Command Palette) Ctrl+K" item; `#cmd-palette` modal HTML block — ~120 LOC additive. `proto/e2e_ui_test.py`: new `_test_inv_palette(page)` with 10 sub-checks + `PHASE_INV_PALETTE_OK` marker registered in main() — ~95 LOC.

**Why:** Companion sprint to INV-2026-05-19-001a (Zen Mode). The original idea `2026-05-19-01-36` was SPLIT_REQUIRED at the invent checkpoint into 001a (canvas chrome-hide + HUDs + minimap) and 001b (quick page search/jump). In Zen Mode the left-panel Sheets tab is hidden, so a keyboard-first page-jump mechanism becomes essential for high-density multi-page workflows. The palette is purely transient UI state — no schema changes, no server changes, composes cleanly above the zen z-index layer.

**Files touched:**
- `proto/static/css/app.css`: ~35 LOC — `.cmd-palette` modal, input, results list, hint bar, tag-chip colors
- `proto/ui.html`: ~120 LOC — `togglePalette`, `closePalette`, `filterPalette`, `_palJumpToIdx`, `_palMoveSel`, `_palEsc`, Ctrl+K keybind, ArrowDown/Up/Enter/Esc palette input handlers, View menu item, `#cmd-palette` DOM
- `proto/e2e_ui_test.py`: ~95 LOC — `_test_inv_palette` (10 sub-checks), `PHASE_INV_PALETTE_OK` marker

**Tests:**
```
python3.11 -m py_compile proto/server.py proto/e2e_ui_test.py  → PASS
python3.11 proto/e2e_ui_test.py smoke                          → EXIT 0
  PHASE_INV_PALETTE_OK 10/10 PASS (helpersAndDomExist, paletteShownAndFocused,
  defaultPrefilterShows, numberFilterWorks, nameFilterWorks, tagFilterWorks,
  moveSelWorks, jumpClosesPalette, midDrawGuard, escClosesPalette)
  PHASE_INV_ZEN_OK still 10/10 — no regression
python3.11 proto/e2e_ui_test.py full                           → EXIT 0
bma-human-journey-tester (real 45-page permit PDF)             → JOURNEY_OK
  13/13 spec steps PASS; 0 JS errors
  HT-Z-3 filed: empty-state when filtering by Thai tag on untagged PDF
    lacks hint that Page Setup tagging is needed first (FRICTION)
```

**Phase 1 scope check:**
- ✅ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` — UNCHANGED
- ✅ `pdfToC` / `cToPdf` / `RS` / scale math — UNCHANGED
- ✅ `buildSnapIndex` / `snap` engine — UNCHANGED
- ✅ `proto/server.py` core endpoints — UNCHANGED (no server edit)
- ✅ `.bmaplan` schema — UNCHANGED (palette is purely transient UI state; version stays 1)
- ✅ No legal / OCR / AI / Rule Engine / FAR-OSR pass-fail

**Known gaps / follow-ups:**
- HT-Z-3: empty-state hint missing when filtering by Thai tag on an untagged PDF; filed to `PHASE_INDEX.md`
- HT-Z-1 + HT-Z-2 (from 001a) still open — can batch into a Zen polish sprint

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

<!-- sessions before 2026-05-19 INV-001a are archived to docs/archive/log-2026-05-19.md (Ribbon Cleanup) and docs/archive/log-2026-05-18.md (earlier) -->
