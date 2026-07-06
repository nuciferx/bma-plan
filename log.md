# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (BLOAT-1 + BLOAT-2 + 2026-05-19 bundle) · [docs/archive/log-2026-05-20.md](docs/archive/log-2026-05-20.md) (BLOAT-3 + BLOAT-4 + BLOAT-5 + BLOAT-FLAKE-1 + BUG-20260520-sel-midpan + INV-2026-05-20-001 + INV-2026-05-20-002/003/004) · [docs/archive/log-2026-05-21.md](docs/archive/log-2026-05-21.md) (BUG-20260521-lite-menu-clip + LITE-5 + LITE-SNAP/REVIEW/ANNOT/EXPORT/PAGESETUP + LITE-1..4 + LITE-0 + HT-ACC series) · [docs/archive/log-2026-05-22.md](docs/archive/log-2026-05-22.md) (LITE-REPORT INV-2026-05-21-002) · [docs/archive/log-2026-05-24.md](docs/archive/log-2026-05-24.md) (LITE-BUG-2-OPUS47-FINDINGS) · [docs/archive/log-2026-05-25.md](docs/archive/log-2026-05-25.md) (LOVS-1 + LPFL-1 + INV-2026-05-25-001 + Centerline Snap arc + SIM-2) · [docs/archive/log-2026-07-02.md](docs/archive/log-2026-07-02.md) (BUG-20260702-lite-cfss-summary / BUG-20260702-lite-arc-summary / SLICE report-edit-1 + invent lite-pdf-render-quality resumed+completed + paused / BUG-20260526-lite-stale-pf-folder-cleanup / LOVS-1 Lite Overview Setup wizard / AUDIT-20260702-infra-bundle / BUG-20260702-lite-pagerot-registration / PERF-20260702-lite-foxit-smoothness) · [docs/archive/log-2026-07-03.md](docs/archive/log-2026-07-03.md) (BLOCK-20260703-clear-queue + GO-20260703-invariants-streaming-worker-recycle + INV-20260703-layer-linkage plan-B-complete + UX-REVIEW-20260703/BUG-20260703-lite-save-wipes-data)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-07-06 — bug intake ×2 (lite, user field report): stale-drawing-on-page-change + multi-site-page-tag — วิเคราะห์+file เข้าคิว ยังไม่แก้ (branch: main)

**ทำอะไร:** `/bma-bug-report` โหมด file-for-next-round ตามคำสั่ง user (2 อาการจาก field use หลัง ship 2026-07-04). Triage คู่ขนาน 2 ตัว (bma-bug-triager, read-only):

(1) **BUG-20260706-lite-stale-drawing-on-page-change** (FRICTION) — วาดหน้า 1 เปลี่ยนหน้าแล้วเส้นค้าง. Data model ถูก (`PS` page-keyed) — สาเหตุน่าจะเป็น (a) `afterPage()` (`ui-lite.html:429`) ไม่ reset `state.vertMode` → handle โหมดแก้จุดของหน้าเดิมถูกวาดทับหน้าใหม่ หรือ (b) object ถูก promote เป็น CFSS ต้นแบบข้ามชั้น (by design) โดยไม่รู้ตัว. ต้องยืนยัน repro ก่อนเลือก fix.

(2) **BUG-20260706-lite-multi-site-page-tag** (FRICTION) — ผังบริเวณ >1 แผ่นเปิด/แท็กไม่ครบ. สาเหตุน่าจะเป็น (a) wizard lock ปลดทันทีที่แท็กหน้าแรก (`wiz-auto.js:92-101`) แผ่นที่ 2 เลยหลุด หรือ (b) ทุกแผ่น site แชร์ `PF_site` โฟลเดอร์เดียว + seed layer "ที่ดิน" ครั้งเดียว (`page-folder-layers.js:104-157, 244-300`). พบ blind spot: ไม่มีเทสเคส site >1 หน้าเลยทั้ง suite.

**Why:** user สั่ง "ใส่ไว้ให้แก้รอบหน้าให้สมดุลที่สุด" — จึง file แบบ NEEDS-REPRO-CONFIRM พร้อม fix candidate + acceptance + test plan ต่อบั๊ก แทนการเดา fix ทันที (ทั้งคู่มี 2 hypotheses ที่ชี้คนละ fix). อาจเกี่ยวกับ pending re-test ของ INV-2026-07-04-001 slice 4 (`e1c6a76`).

**Update ในวันเดียวกัน (บั๊ก 1):** user ส่ง screenshot (`lite/bug/Screenshot 2026-07-06 091956.png`) — เปลี่ยนการวินิจฉัยทั้งหมด: ไม่ใช่เส้นค้าง/vertMode/CFSS (ถอนทิ้ง) แต่คือ **active draw layer ไม่ตามหน้า**: หน้า 29 หลังคา แผง layer สลับถูก แต่ "วาดที่: ผังบริเวณ·ที่ดิน (ซ่อน)" ค้าง + วาดลงได้ → **BROKEN** (บันทึกพื้นที่ผิดชั้นเงียบ ๆ). Root cause: `_lsSyncActiveCatToFolder` (`layer-scope.js:449-471` จาก `e1c6a76`) ไม่มี fallback สำหรับ folder ที่ไม่เคยแวะใน session + `mkObj()`/`finishDraft()` (`ui-lite.html:558`) ไม่มี guard เช็ค layer↔หน้า. Fix plan 2 จุด (fallback else-branch + JIT-gate ตาม pattern SCALE-GATE) ลง PHASE_INDEX แล้ว — READY-TO-FIX ทั้ง 2 บั๊ก. เปลี่ยนชื่อ id เป็น BUG-20260706-lite-active-layer-not-following-page.

**Update ในวันเดียวกัน (บั๊ก 2):** user ยืนยัน repro บั๊ก 2 = "ติดป้ายครบแล้วแต่ข้อมูลโชว์แค่แผ่นเดียว" → deep trace ปักหมุด root cause ได้: folder membership + aggregation ถูกหมด ตัวพังคือ `_lsGoTo` (`layer-scope.js:153-158`) วาร์ป `pages[0]` เสมอ + floor-rail นับ PF_site เป็น 1 stop → แผ่น site ที่ 2 เข้าไม่ถึงผ่าน rail/search → ไม่ได้วาด → report โชว์แผ่นเดียว. เป็น regression-by-design-gap ของ INV-2026-07-04-001 (rail สร้างบนสมมติฐาน 1 หน้า/โฟลเดอร์). Fix plan + acceptance + test ลง PHASE_INDEX แล้ว สถานะ READY-TO-FIX. บั๊ก 1 ยังรอ user สังเกต (โหมดแก้จุด / CFSS).

**Update (ship, commit `ba109f0`):** ทั้ง 2 บั๊กแก้เสร็จและ ship วันเดียวกัน หลัง root-cause ชัดแล้วทั้งคู่. Fix บั๊ก 1 (BUG-20260706-lite-active-layer-not-following-page): (a) `_lsSyncActiveCatToFolder` (`layer-scope.js`) เพิ่ม fallback — folder ที่ไม่เคยแวะ session นี้ → เลือก layer แรกตาม model order แทนการค้าง `activeCat` เดิม; (b) เพิ่ม guard ใหม่ `lsForeignDrawBlocked()` เรียกจาก `finishDraft()` และ count tool ใน `ui-lite.html` — ปฏิเสธ commit วัตถุที่ layer ปลายทางไม่ตรงกับ folder ของหน้าปัจจุบัน พร้อม hint เตือน 5 วิ (ใช้ pattern `state.hintFlash` เดียวกับ SCALE-GATE ไม่ใช่เขียน `#hint` ตรงๆ — รอบแรกที่รันเทสพบว่า `draw()`→`updateHUD()` เขียนทับ `#hint` ทิ้ง จึงเปลี่ยนมาใช้ hintFlash). Fix บั๊ก 2 (BUG-20260706-lite-multi-site-page-tag): `_lsGoTo` รู้จักหน้าใน folder เดียวกัน — เลือก folder เดิมซ้ำ → ก้าวไปหน้าถัดไปใน folder นั้น (wrap รอบ), มาจาก folder อื่น → ไปหน้าแรก (`pages[0]`); floor-rail ◀/▶ ก้าวข้าม "หน้า" ภายใน folder ก่อนข้าม folder; ตัวนับเปลี่ยนเป็น "ชั้น i/N · แผ่น i/N". เทส: `test_layer_scope.py` ขยาย 6→9 checks (+140 บรรทัด) มี marker ใหม่ `LITE_ACTIVE_LAYER_FOLLOW_OK` + `LITE_LAYER_SCOPE_MULTI_PAGE_FOLDER_OK` — รันสองรอบ, รอบแรก FAIL ที่ check `foreignDrawCommitBlocked` (เจอปัญหา hintFlash ข้างต้น) → แก้แล้วรอบสอง 9/9 เขียว. Regression 7 suites เขียวหมด: `test_page_folder_ui.py`, `test_pf_folder_order.py` 4/4, `test_pf_kind_folders.py` 11/11, `test_custom_layer_ui.py`, `test_wiz_auto.py` 8/8, `test_measure_parity.py` (`MEASURE_PARITY_OK`). ไม่ต้องรัน proto E2E — lite-only, proto ไม่ถูกแตะ, ไม่มี forbidden surface (measure-engine/pdfToC/RS/snap ไม่ถูกแตะ). **เหตุการณ์ระหว่างทาง:** เจอ `.git/index.lock` ค้างจาก git process ที่ crash เมื่อ 2026-07-04 23:32 — index ถูกล้าง (ทุกอย่างขึ้น staged-deleted + untracked) ซ่อมด้วย `rm index.lock` + `git read-tree HEAD` + รัน `git update-index --refresh` แบบ background (Google Drive FS ช้า — foreground commit ไทม์เอาต์ที่ 2 นาที; ใช้ background สำหรับ git commit ใน repo นี้ต่อไป). Commit `ba109f0` รวมทั้ง 2 fix + เทสในคอมมิตเดียว. Delegation: triage รอบนี้ผ่าน `bma-bug-triager` (sonnet) ×2 รอบ + deep-trace resume, main agent (Fable 5) แก้โค้ดเอง, รันเทสผ่าน haiku runner.

**Files touched (update):** `lite/static/js/layer-scope.js` (+96/-17 incl. comments), `lite/ui-lite.html` (+2 guard call lines, now 1189/1200 cap), `lite/tests/test_layer_scope.py` (6→9 checks, +140 lines), `docs/status/PHASE_INDEX.md`, `log.md`. **Tests:** 7 suites green (`test_layer_scope.py` 9/9 incl. new markers `LITE_ACTIVE_LAYER_FOLLOW_OK`/`LITE_LAYER_SCOPE_MULTI_PAGE_FOLDER_OK`, run twice — first run caught the hintFlash issue; `test_page_folder_ui.py`, `test_pf_folder_order.py` 4/4, `test_pf_kind_folders.py` 11/11, `test_custom_layer_ui.py`, `test_wiz_auto.py` 8/8, `test_measure_parity.py`). No proto E2E needed. **Known gaps:** ทั้ง 2 fix (`ba109f0`) รอ user field re-test จริง — โดยเฉพาะ permit PDF 29 หน้าเดิมและผังบริเวณ 2 แผ่น.

---

## 2026-07-04 — 8 ships เต็มวัน: layer-menu invent+build (INV-2026-07-04-001) + page-tagging invent+build (INV-2026-07-04-002) + report-truth 5 slices + BUG native-rotate + SNAP-2026-07-04 engine extraction + SCALE-GATE — PASS (branch: main)

**ทำอะไร (18 commits, ทั้งหมด lite/, proto untouched):**

(1) **Invent: lite-layer-menu-ui-fix → GO `c35c1a7`** — reframe "แก้ ui เมนู layer" เป็นปัญหา scalability 100 ชั้น; research: incumbent ทุกตัวแยกแกนชั้น⊥ประเภท; diverge 5 แนว; spike B พิสูจน์ 9/9 (3 เคส × 3 preset สัดส่วน); opus first-stage review CONFIRM-WITH-CONCERNS; user เลือก P2 260px.

(2) **INV-2026-07-04-001 layer panel build** — `7600fde` (3 slices: NEW layer-scope.js — panel โชว์เฉพาะ PF folder ของหน้าที่เปิด + floor-rail ◀/select/▶ + grouped search cap-30, P2 260px geometry, พิสูจน์กับ permit จริง) + `e1c6a76` (slice 4 field bug: per-floor activeCat memory — root cause คือ global activeCat ไม่มี per-floor memory ไม่ใช่ rendering) + docs `dafb932`. กลืน LFOC-1e.

(3) **Invent: lite-page-tagging-workflow → GO `0a6677a`** — จาก Fable วิจารณ์ workflow อิสระ (user: "ทำที่ fable คิด"); spike C+minimal-A 3/3 (7/8 actions happy path); opus CONFIRM-WITH-CONCERNS.

(4) **INV-2026-07-04-002 page tagging rework** — `2df5d40` (4 slices: extract overview-grid.js 1059→845; bulk apply พร้อม basement-descending + overwrite-confirm + single undo; group-by-tag verify view; tag-jit.js per-page JIT gate ผ่าน setTool wrap + ลบ SET gate แบบ atomic). กลืน REVIEW S-10.

(5) **report-truth (5 slices, จาก Fable วิจารณ์ export pipeline, user: "ใช้ความคิดเห็น fable")** — A `bb5090f` XLSX+computeSummary→object-agg tuple stream, ตัด excluded semantic ออก (A-4/B-6; ui-lite 1198→1192) · B `6ba7ea3` grid ALL pages + deduction sign (B-2/B-3) · C `fc63e72` grid single-mode พิมพ์ได้จริง, classic ลบทิ้ง, reportVars ย้ายบ้าน (S-1 ทาง ก; lite-report 332→204) · D `8362c3f` 3 export doors ที่ตรงความจริง + Thai PDF-overlay labels (S-6/S-12) · E `52725a1` plan-image appendix พร้อม SVG overlays (user checkpoint decision).

(6) **BUG-20260704-lite-native-rotate `fbe28fb`** — user field report "pdf เปิดกลับข้าง ต้องหมุน 90": PDF.js getViewport explicit rotation REPLACES intrinsic /Rotate (regression จาก GO-20260703 streaming). fix 2 บรรทัด (natVp + thetaTotal รวม cp.rotate); repro-first fixture 6 pre-fix fail → 24/24; registration ≤0.5px.

(7) **SNAP-2026-07-04 (จาก Fable snap review; user เลือกเอง — เก็บ 3 blocks, ตัด centerline-unification รอ INV-2026-05-25-001 retest, wall-trace → /idea)** — `cd6a960` extract snap-engine.js + static-intersection cache (ฆ่า O(n²)/mousemove; ui-lite 1192→1158) · `23f3914` angle-lock ผสาน snap ได้ (ray∩segment apparent intersection, click==preview, orthoOn indicator side-fix) · `42a0767` nearest-on-edge toggle (5-type symmetry).

(8) **SCALE-GATE `a5044aa`** — JIT gate ที่สอง: measure บนหน้าที่ยังไม่ตั้ง scale ถูกปฏิเสธ + banner ตั้ง scale ใน 1 tap + re-arm pending tool แค่ครั้งเดียว; count ยกเว้น; report โชว์ "—" (ไม่ใช่ 0.00) สำหรับ area null, subtotal/net ไม่รวมมัน. ปิด same-day finding. (Help-system layers 2/3 ตัดทิ้งตามคำสั่ง user "จำเป็นไหม" → ทำแค่ layer นี้.)

**Why:** วันเดียวรวบ 8 ชิ้นจาก field report + Fable review 3 รอบ (export pipeline, snap, workflow) — pattern คือ user delegate ให้ Fable คิดวิเคราะห์ก่อน แล้ว build ตาม findings ที่ Fable เลือก ไม่ build ทุกอย่างที่พบ (เช่น snap ตัด centerline-unification ทิ้ง, help-system ตัด layer 2/3). Model ladder ใหม่ที่ยึดทุก invent วันนี้: haiku/sonnet ทำงาน → opus ตัดสินขั้น 1 → Fable ตัดสินสุดท้าย.

**Files touched:**
- `lite/static/js/layer-scope.js`: NEW — page-scoped layer panel + floor-rail + grouped search
- `lite/static/js/overview-grid.js`: extracted from ui-lite.html (1059→845)
- `lite/static/js/tag-jit.js`: NEW — per-page JIT scale/tag gate via setTool wrap
- `lite/static/js/snap-engine.js`: NEW — extracted snap logic + static-intersection cache
- `lite/static/js/export-annotate.js`, `lite/static/js/report-vars.js`: object-agg tuple stream wiring, Thai PDF-overlay labels
- `lite/lite-report.html`: grid single-mode only, classic table removed (332→204)
- `lite/ui-lite.html`: net DOWN across the day (1197→1188) despite 6 feature ships — 2 extractions offset new code
- `lite/server_lite.py`: native-rotate fix (natVp + thetaTotal incl. cp.rotate)
- 15+ new/updated `lite/tests/test_*.py` files (one per marker below)
- `docs/status/PHASE_INDEX.md`: 8 cards filed/closed across the day

**เทส:** full lite suite 97/98 files เขียว (fail เดียวคือ `test_closing_dup_strip.py` — pre-existing, พิสูจน์แล้วว่าเป็นบั๊กของตัวเทสเอง ไม่ใช่แอป ตรวจกับ HEAD แล้ว, คิว housekeeping). Markers ใหม่วันนี้: `LITE_LAYER_SCOPE_OK` 6, `LITE_LAYER_SEARCH_OK` 5, `LITE_BULK_APPLY_OK` 5, `LITE_GRID_GROUP_VIEW_OK` 5, `LITE_TAG_JIT_OK` 6, `LITE_EXPORT_TRUTH_OK` 5, `LITE_GRID_ALL_PAGES_OK` 5, `LITE_REPORT_SINGLE_MODE_OK` 5, `LITE_EXPORT_DOORS_OK` 4, `LITE_REPORT_APPENDIX_OK` 5, `LITE_NATIVE_ROTATE_OK` 24, `LITE_SNAP_ENGINE_OK` 5, `LITE_SNAP_RAY_OK` 6, `LITE_SNAP_TYPES_OK` 9, `LITE_SCALE_GATE_OK` 5. พิสูจน์ visual: 10 screenshots ใน `artifacts/report-truth-proof/` (8 feature + 2 native-rotate), zero console errors.

**เหตุการณ์/บทเรียน:** `.git/index` เสียซ้ำอีกครั้ง (ครั้งที่ 2 ของสัปดาห์) จาก subagent `git stash` บน Drive-synced repo → ซ่อมสำเร็จด้วยสูตรเดิม (mv index + git reset) → ตั้ง hard rule ใหม่: ห้าม subagent เขียน git ops ใดๆ ในทุก spec (บันทึกใน memory แล้ว). Size-cap บังคับใช้จริง 2 ครั้ง (overview-grid.js, snap-engine.js extraction) — `ui-lite.html` สุทธิลดลง (1197→1188) ทั้งที่ ship ฟีเจอร์ไป 6 รอบในวันเดียว. ค้าง: user field re-test ทุกอย่างที่ ship วันนี้; `test_closing_dup_strip` + `test_undo_layers` cp1252 print crash (housekeeping); LFOC-1b dead render path; mi-xlsx visible duplicate (micro); B-10 remainder (cross-project hash namespacing); ไอเดียคิว: wall-trace assist `2026-07-04-21-45` (รอ INV-2026-05-25-001), page-jump/floor ideas ตาม PHASE_INDEX; INV-2026-05-25-001 centerline ยัง WAITING USER FIELD DATA.

---

## 2026-07-03 (บ่าย) — Layer redesign A+B + UX batch 2-3 + V2 U-series complete + undo coverage + staleness audit — PASS (branch: main)

**What changed (17 commits, ทั้งหมด lite/process — proto untouched):** (1) **UX batch 2 `036a49d` + batch 3 `fcf5b23`** — F-4 HUD "✓✓ ยืนยันแล้ว" / F-5 mousedown hint / F-6 gateNoCaseMsg / F-9 verify in-app modal / seeded-vars "รอข้อมูล" / wizard Next gate / F-8 error+next-step ×11 / annotate hotkeys ⇧T⇧M⇧A⇧H⇧R⇧C⇧U / Thai PM+wizard / empty-state.js / page-scan-badge.js — UX review เหลือแค่ export-entry consolidation. (2) **CFSS+LAYERS undo** `81c4325`+`085ab60` — _docSnap ครอบ MASTERS แล้วต่อด้วย LAYERS/FOLDERS (in-place splice restore เพราะ `var CATS = LAYERS` alias; pushUndo ที่ UI entry points, seeding undo-silent) — ทุก layer op กด Ctrl+Z ได้. (3) **report grid default** `16698bb` — jss grid เป็นหน้ารายงานหลัก, classic = print escape hatch (@media print force-classic). (4) **V2 U-series ครบ 6 upgrade**: U2 impact-map `--changed` `2df65d4`, U3 SHIPS.jsonl+generator `77a610f`+`ea03f53` (แทน sprint-writer ~200-260K tok/finalize — dogfooded ตลอดบ่าย), U4 roadmap split+reconcile, U5 executable-truth gate `770ee14` เข้า preflight, U6 gen_changelog+RELEASE_RITUAL `a42bde6`. (5) **Layer redesign A+B (invent เต็มวง)** — research (PRIOR_ART_PARTIAL) → diverge 5 แนวทาง → spike 4/4 `f54bac3` → user GO ที่ checkpoint → A-model `92174b6` (`layer.floorKey` one-seam swap ใน objectTuples, RED-proven, save เก่า byte-identical) + B-ui `20129af` (layer-target-ui.js: chip "วาดที่:", canvas tint, ◉ make-current, reconcile banner — user approved ก่อน commit) — ปิด P1/P2/P3. (6) **Worker-recycle CHH re-probe PASS** `39de379` — คืน ~1,444 MB (tree RSS −80.4%), reinit 1.1s. (7) **Staleness audit** `3afacdb`+`721f67f` — พบ stale card 5 ใบ (wizard-followup, LFOC-ORDER-B, force-setup, probe-rewrite, PERF-streaming) ปิดหมด + reconcile ได้ check (d) จับ pattern นี้อัตโนมัติ (fix commit อ้าง card-id แต่ docs ไม่ flip) + `.git/refs/desktop.ini` ลบ (git log --all หาย) + `*.gsheet` ignored.

**Why:** ผู้ใช้ arm /loop go ต่อเนื่อง — เคลียร์คิว autonomous จนแห้ง เหลือเฉพาะ human-gated. บทเรียนสำคัญ: (ก) stale card เกิดจาก fix commit ลงแต่ docs follow-up ไม่ลง → แก้ที่ราก (reconcile (d)) ไม่ใช่แค่กวาดครั้งเดียว; (ข) ledger-first ทำงานจริง — finalize เหลือ "append 1 บรรทัด + gen --write"; (ค) invent checkpoint + per-commit review ตอบโจทย์ "ไม่ให้ user เลือกแล้วหรอ" — จุดตัดสินอยู่ที่ user เสมอ (GO A+B, approve B-ui ก่อน commit).

**Tests:** ทุก ship มี guard ใหม่ (LITE_UX_BATCH2/3, LITE_UNDO_MASTERS/LAYERS, LITE_REPORT_DEFAULT_GRID, LITE_LAYER_FLOORKEY 5 proofs, LITE_LAYER_TARGET_UI, BUG_20260526_LITE_WIZ_FOLLOWUP, TRUTH_CHECK) + regression sweep ต่อ ship + t0 ทุกรอบ; truth-check + reconcile เขียวเป็น gate ก่อนทุก docs commit. Journey test เต็มวงบน RAMA4 45 หน้ากำลังรัน (ผลจะบันทึก session หน้า).

**Known gaps:** grid ไม่รู้เครื่องหมายลบ (deduction → classic เป็น source of truth); banner ทีละใบ; งานเปิดที่เหลือรอ user: export-entry design, LOVS Step 3, centerline field data, workflow-redesign 5 ข้อ, proto freeze, release cut.

---

<!-- INV-20260703-layer-linkage (plan B complete) + UX-batch-1 + save-fix follow-up / UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data archived to docs/archive/log-2026-07-03.md on 2026-07-04 (2026-07-04 full-day 8-ship sprint block, to keep root at last-2-sessions) -->
<!-- GO-20260703-invariants-streaming-worker-recycle archived to docs/archive/log-2026-07-03.md on 2026-07-03 (INV-20260703-layer-linkage plan-B-complete sprint block) -->
<!-- BLOCK-20260703-clear-queue archived to docs/archive/log-2026-07-03.md on 2026-07-03 (UX-REVIEW-20260703 + BUG-20260703-lite-save-wipes-data sprint block) -->
<!-- PERF-20260702-lite-foxit-smoothness archived to docs/archive/log-2026-07-02.md on 2026-07-03 (GO-20260703-invariants-streaming-worker-recycle session) -->
<!-- BUG-20260702-lite-pagerot-registration archived to docs/archive/log-2026-07-02.md on 2026-07-03 (BLOCK-20260703-clear-queue session) -->
<!-- AUDIT-20260702-infra-bundle archived to docs/archive/log-2026-07-02.md on 2026-07-02 (PERF-20260702-lite-foxit-smoothness sprint block) -->
<!-- BUG-20260702-lite-cfss-summary + BUG-20260702-lite-arc-summary + SLICE report-edit-1 + invent lite-pdf-render-quality (resumed+completed) + invent lite-pdf-render-quality (paused) + BUG-20260526-lite-stale-pf-folder-cleanup + LOVS-1 archived to docs/archive/log-2026-07-02.md on 2026-07-02 (BUG-20260702-lite-pagerot-registration sprint) -->
<!-- LPFL-1 + INV-2026-05-25-001 + Centerline Snap arc + SIM-2 archived to docs/archive/log-2026-05-25.md on 2026-05-26 -->
<!-- LITE-BUG-2-OPUS47-FINDINGS (2026-05-24) archived to docs/archive/log-2026-05-24.md on 2026-05-25 (Centerline Snap sprint) -->
<!-- LITE-REPORT (INV-2026-05-21-002, 2026-05-22) archived to docs/archive/log-2026-05-22.md on 2026-05-24 (SIM-2 sprint) -->
<!-- BUG-20260521-lite-pan-controls archived to docs/archive/log-2026-05-21.md on 2026-05-24 (LITE-BUG-2 sprint) -->
<!-- BUG-20260521-lite-menu-clip + LITE-5 + LITE-SNAP/REVIEW/ANNOT/EXPORT/PAGESETUP + LITE-1..4 + LITE-0 + HT-ACC series archived to docs/archive/log-2026-05-21.md -->
<!-- Earlier 2026-05-20 entries archived to docs/archive/log-2026-05-20.md -->
<!-- BLOAT-2 and BLOAT-1 entries archived to docs/archive/log-2026-05-19.md -->
