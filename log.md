# BMA-Plan — Log (บันทึกเหตุการณ์)

> ไฟล์นี้บันทึกเฉพาะ 2 session ล่าสุด
> ประวัติเต็ม: [docs/archive/log-2026-05-09.md](docs/archive/log-2026-05-09.md) · [docs/archive/log-2026-05-14.md](docs/archive/log-2026-05-14.md) · [docs/archive/log-2026-05-15.md](docs/archive/log-2026-05-15.md) · [docs/archive/log-2026-05-18.md](docs/archive/log-2026-05-18.md) · [docs/archive/log-2026-05-19.md](docs/archive/log-2026-05-19.md) (BLOAT-1 + BLOAT-2 + 2026-05-19 bundle) · [docs/archive/log-2026-05-20.md](docs/archive/log-2026-05-20.md) (BLOAT-3 + BLOAT-4 + BLOAT-5 + BLOAT-FLAKE-1 + BUG-20260520-sel-midpan + INV-2026-05-20-001 + INV-2026-05-20-002/003/004) · [docs/archive/log-2026-05-21.md](docs/archive/log-2026-05-21.md) (BUG-20260521-lite-menu-clip + LITE-5 + LITE-SNAP/REVIEW/ANNOT/EXPORT/PAGESETUP + LITE-1..4 + LITE-0 + HT-ACC series) · [docs/archive/log-2026-05-22.md](docs/archive/log-2026-05-22.md) (LITE-REPORT INV-2026-05-21-002) · [docs/archive/log-2026-05-24.md](docs/archive/log-2026-05-24.md) (LITE-BUG-2-OPUS47-FINDINGS) · [docs/archive/log-2026-05-25.md](docs/archive/log-2026-05-25.md) (LOVS-1 + LPFL-1 + INV-2026-05-25-001 + Centerline Snap arc + SIM-2) · [docs/archive/log-2026-07-02.md](docs/archive/log-2026-07-02.md) (BUG-20260702-lite-cfss-summary / BUG-20260702-lite-arc-summary / SLICE report-edit-1 + invent lite-pdf-render-quality resumed+completed + paused / BUG-20260526-lite-stale-pf-folder-cleanup / LOVS-1 Lite Overview Setup wizard / AUDIT-20260702-infra-bundle / BUG-20260702-lite-pagerot-registration / PERF-20260702-lite-foxit-smoothness) · [docs/archive/log-2026-07-03.md](docs/archive/log-2026-07-03.md) (BLOCK-20260703-clear-queue + GO-20260703-invariants-streaming-worker-recycle + INV-20260703-layer-linkage plan-B-complete + UX-REVIEW-20260703/BUG-20260703-lite-save-wipes-data) · [docs/archive/log-2026-07-04.md](docs/archive/log-2026-07-04.md) (2026-07-04 full-day 8-ship block + 2026-07-03 บ่าย layer redesign A+B/UX batch 2-3/V2 U-series/undo/staleness-audit) · [docs/archive/log-2026-08-10.md](docs/archive/log-2026-08-10.md) (PM-META + PM-ID + BUG-20260706 bug intake ×2)
> อัปเดตทุกครั้งที่: แก้โค้ด / เพิ่มฟีเจอร์ / แก้บั๊ก / รันทดสอบ / ตัดสินใจสำคัญ

---

## 2026-08-11 — BUG-20260811-escape-paths: ทางออกทุกทางผ่านประตูเดียว — FIXED same day (branch: main)

**ทำอะไร:** user เริ่มทดสอบมือ 8 ข้อแล้วรายงานทันที: "หน้า setup ดับเบิลคลิกที่หน้าใดหน้าหนึ่ง จะเข้าไปหน้านั้นโดยไม่ setup" → ตรวจโค้ดพบ 2 จุด: (ก) **regression ของผมเอง** — ยามกัน dblclick ใน `overview-grid.js:317` เช็ค `__lwizAutoLockActive` ซึ่ง WIZ-UNLOCK (`fb9b2af`) ทำให้ false ถาวร = ยามตาย; (ข) PM tile-click เรียก `_pmCloseOverlay()` ตรง ข้ามเกราะ `_pmTryClose()` ที่ PM-GUARD เพิ่งสร้าง. User ถาม "ถ้าออกไป layer หรือระบบอื่นจะพังไหม" → วิเคราะห์: ไม่พัง/ข้อมูลไม่หาย (เปลี่ยนหน้าเป็นงานปกติ, pending คงอยู่ใน pageMgr) แต่เสีย selection + active layer เปลี่ยนตามหน้า + ผู้ใช้ไม่รู้ว่ามีของค้าง. User สั่ง "ทำเลย" → file bug ก่อน (`53226d2`) → builder แก้ตามหลัก "ทุกทางออกผ่านประตูเดียวที่ตรวจงานค้าง": PM tile-click เช็ค pending ก่อน (ค้าง=เตือน+ไม่ไป, สะอาด=ไปตามปกติ), wizard dblclick เปลี่ยนเงื่อนไขเป็น `_lovsSelected.size>0` (เลือกค้าง=hint+block, ว่าง=ไปได้) + ลบ flag ตายทิ้ง + อัปเดต `test_wiz_followup.py` ตาม contract ใหม่ (assertion เดิม 4 ตัวคงอยู่ เปลี่ยนแค่ trigger).

**Tests:** guard ใหม่ `test_escape_paths.py` (`LITE_ESCAPE_PATHS_OK`) พิสูจน์ RED ก่อนแก้ (case A+C fail ตรงตามรายงาน, B+D ผ่านตั้งแต่ก่อนแก้ = พฤติกรรมสะอาดไม่ถูกกระทบ) → GREEN 4/4. Baseline 7 ไฟล์เขียวก่อนเริ่ม. Suite เต็ม **106/107** (fail เดียว `test_closing_dup_strip.py` pre-existing). `TRUTH_CHECK_OK` 6/6. wc: page-manager-ui 704, overview-grid 555.

**Commits:** `53226d2` (file bug), `d06a4db` (fix). **บทเรียนที่ file ไว้ในการ์ด:** ตอนถอดฟีเจอร์ ไล่แค่ "ใครเรียกฟังก์ชันที่ลบ" ไม่พอ — ต้องไล่ "ใครเช็คตัวแปรสถานะของมัน" ด้วย.

---

## 2026-08-11 (ต่อจากคืน 08-10) — OSS landscape survey + พบความเสี่ยง license AGPL — ANALYSIS (branch: main)

**ทำอะไร:** user ถาม "มี open source บ้างไหม / หาแล้วยัง" — ตอบตรงว่ายังไม่เคยสำรวจเป็นระบบ แล้วส่ง `bma-researcher` สำรวจ 6 หมวด (แอปทั้งตัว / PDF engine / raster→geometry / floor-plan AI / CAD-GIS lib / infra) โดยบังคับให้ระบุ **license เป็นตัวตัดสิน** เพราะเป็นเครื่องมือแจกให้ราชการ. บันทึกผล + คำวินิจฉัยของ orchestrator ไว้ที่ `docs/design/OSS_LANDSCAPE_20260810.md`.

**ผลสำคัญ 3 ข้อ:**
1. 🔴 **PyMuPDF เป็น AGPL** และเราเพิ่ง ship `PKG-PORTABLE` ที่บรรจุมันลงโฟลเดอร์แจกจ่ายเมื่อวาน → file การ์ด `LICENSE-AUDIT` (p-high) + ระบุห้ามแจกออกนอกทีมจนกว่าจะตัดสิน
2. ❌ **orchestrator ปฏิเสธข้อเสนอ Tier-1 ของ researcher** ที่ให้เอา `flatten-js` แทน `polyAreaM2` — ละเมิดสัญญา vendoring/parity ที่ sha-lock ไว้, ทำ `.bmaplan` ข้าม proto↔lite ไม่ตรง, และแทนที่คณิตที่ผ่าน PBT ~500 เคสด้วย dependency 80KB โดยไม่ได้อะไรเพิ่ม (บทเรียน: รายงานวิจัยไม่รู้ข้อจำกัดภายใน ต้องกรองเสมอ)
3. ✅ **PaddleOCR (Apache-2.0, รัน local, อ่านไทยได้จริง)** ปลดล็อกคำถามนโยบายที่ค้างของ Track AI — ชั้น OCR ไม่ต้องส่งภาพออก cloud

**ข้อค้นพบเชิงลบที่มีค่า:** ไม่มี pipeline "สแกน→polygon" open source ที่โตพอ (centerline-snap ของเราไม่ล้าหลัง) · ไม่มีโมเดลอ่านแบบแปลนที่ใช้กับแบบไทยได้ทันที (CubiCasa5k = แบบฟินแลนด์สะอาด, VLM local อ่อนไทย) → Track AI ขั้นวาด polygon เป็น greenfield จริง ต้อง eval-first · ไม่มีเครื่องมือ Compare-revisions พร้อม registration → ยืนยันว่าแนวทาง (a) เป็นงานประดิษฐ์

**ต้องตรวจก่อนเชื่อ:** `OpenTakeoff` (อ้าง Apache-2.0 browser takeoff 2026) — ยังไม่ได้เปิด repo จริง อย่าวางแผนบนสมมติฐานนี้

**Tests:** ไม่มีการแก้โค้ด — no-test rationale (งานวิจัย+เอกสาร). `TRUTH_CHECK_OK` 6/6 หลังบันทึก.

---

## 2026-08-10 (ดึก-2) — INFRA-CI: GitHub Actions ทำให้ด่านทั้งหมดรันเอง — SHIPPED (branch: main)

**ทำอะไร:** `9e72502` เพิ่ม `.github/workflows/ci.yml` (repo นี้ไม่เคยมี CI มาก่อน). แรงจูงใจ: จากบทสนทนาเทียบแนวปฏิบัติ Anthropic/OpenAI — ด่าน 6 ตัว + test pyramid ที่โปรเจกต์ลงทุนสร้างมาทั้งหมด "มีอยู่จริงเฉพาะตอนมีคนสั่งรัน" = ช่องว่างอันดับ 1 เทียบมาตรฐานอุตสาหกรรม. โครง 3 job: `truth-gate` (ubuntu, `check_executable_truth --verbose`, `fetch-depth: 0` เพราะ ships-commits ต้อง resolve hash จริง) + `fast-tests` (ubuntu, tier t0 parity/PBT ผ่าน Node + tier t1 server endpoints) ทั้งคู่ยิงทุก push; `full-suite` (windows-latest ให้ตรงกับเครื่อง dev, Playwright เต็มชุด) เฉพาะ manual dispatch + nightly cron 01:00 น. ตั้ง `concurrency.cancel-in-progress` กัน queue ซ้อน.

**Why:** ที่ผ่านมาถ้า session ไหนลืมรัน suite หรือ subagent ข้ามด่าน ก็ไม่มีอะไรจับได้เลย — CI ทำให้วินัยที่เขียนไว้ในเอกสารกลายเป็นสิ่งที่บังคับได้จริงโดยไม่ขึ้นกับความจำของใคร.

**Files touched:** `.github/workflows/ci.yml` (NEW, 75 บรรทัด), `docs/status/PHASE_INDEX.md` (การ์ด INFRA-CI + ข้อจำกัด).

**Tests:** ยืนยัน `python lite/tests/run_all_tests.py --tier t0` ในเครื่อง → 2/2 PASS (`MEASURE_PARITY_OK`, `LITE_PBT_MEASURE_OK`); YAML parse ผ่าน (3 jobs, triggers ครบ 4); `check_executable_truth` → `TRUTH_CHECK_OK` 6/6. **ยังไม่ได้พิสูจน์ผลรันจริงบน GitHub** — `gh` ในเครื่องไม่ได้ auth.

**Known gaps (บันทึกในการ์ดแล้ว):** (1) job ubuntu ยังไม่เคยพิสูจน์ว่าเทสต์ที่เขียนบน Windows รันผ่านบน Linux — รอผลรันรอบแรก ถ้าแดงเพราะสภาพแวดล้อมให้ย้ายไป windows; (2) nightly cron ยิงจาก **default branch เท่านั้น** ซึ่งตอนนี้คือ `main` สายเก่า ส่วนงานอยู่ `main-v2-2026-05-19` → nightly ยังไม่ทำงานจนกว่าจะตัดสินเรื่อง default branch; (3) `full-suite` ตั้ง `continue-on-error` ชั่วคราวเพราะ `test_closing_dup_strip.py` แดง pre-existing (ไม่งั้น badge แดงถาวรจนคนเลิกมอง = อาการเดียวกับ `--no-truth-check` ที่เคยตำหนิ) — ต้องปลดเมื่อบั๊กถูกแก้.

---

## 2026-08-10 (ดึก) — GOV-MAXLEN ratchet + extraction project-io.js (ui-lite 1191→1086) — PASS (branch: main)

**ทำอะไร:** user ตัดสินเรื่องลิมิตไฟล์ ("จัดไป"): (1) `033ad5c` เพิ่มด่าน `maxlen-ratchet` ใน `check_executable_truth.py` (คู่ ESLint max-lines+max-len: บรรทัด >300 ตัวอักษรห้ามเพิ่มจาก baseline ที่ freeze ไว้ — ui-lite 10, measure-engine 11 (vendored), อื่นๆ 0; ยอดรวมลดได้อย่างเดียว; RED-proven ด้วยการแอบเติมบรรทัดยาวแล้วด่านจับได้จริง) — ด่านรวมเป็น 6 ตัว; (2) `df5a1f2` extraction sprint: ย้าย region save/load `.bmaplan` (เดิม ui-lite.html:934-1038) แบบ byte-verbatim (พิสูจน์ programmatic) ไป `static/js/project-io.js` (154 บรรทัด + header สัญญา globals ครบ) — `ui-lite.html` 1191→1086 คืน headroom ~114 บรรทัดโดยเพดาน 1200 ไม่ขยับ; MAXLEN_BASELINE ย้ายตาม (10→8 + project-io 2, ยอดรวมเท่าเดิม). cfssWrapSave/Load ยังเกาะถูกตัว (`wrappersInstalled=True`), persist battery 7/7, suite เต็ม 105/106 (fail เดียว pre-existing), `TRUTH_CHECK_OK` 6/6.

**หมายเหตุ:** builder เผลอลบ `lite/out.txt` (ไฟล์ scratch untracked ที่รีวิว 2026-08-10 แนะนำให้ลบอยู่แล้ว) — ยอมรับได้ ไม่ต้องกู้. **Idea filed:** Track AI อ่านแบบแปลน (`invent-queued`, ffc763f) + คุยยุทธศาสตร์ engine ระดับ Bluebeam (vector-snap port / Compare revisions / Viewports เป็น candidate ไอเดียถัดไป — ยังไม่ file).

---

## 2026-08-10 (ค่ำ) — PKG-PORTABLE (zero-install build) + PM-REDESIGN approach D (PM-GUARD/TAG-JIT/WIZ-UNLOCK) + SHELL (status-bar+float-panel) — PASS (branch: main)

**ทำอะไร:** ต่อจาก /lite-invent 2 pipeline ที่ HALT ไว้ที่ human checkpoint ตอนบ่าย (`lite-zero-install-packaging` + `page-manager-redesign`) — user ตัดสิน "go ทั้งสองตัว" แล้วสั่ง build วันเดียวกัน รวม 3 ก้อนงาน + ledger close, ship ขึ้น `main` + push ตลอด, suite เขียวทุกจุด, `TRUTH_CHECK_OK` 5/5, ทุก code slice มี RED-first guard test:

1. **PKG-PORTABLE** (`fc4a407`, invent `lite-zero-install-packaging` GO approach B) — `lite/build_portable.bat` ผลิต `dist-portable/BMA-Plan-Lite/` (Python 3.11.9 embed + deps + lite runtime + `run.bat` CRLF, 115MB/3193 ไฟล์); verify แล้วด้วย sanitized-PATH launch, cold start 6.22s, `/health` 200. เพิ่ม flag ใหม่ `BMA_LITE_NO_BROWSER` ใน `launch_lite.py` (additive, default ไม่เปลี่ยน) + README section. Output dir gitignored. **ค้าง:** user ต้องเทสบนเครื่อง Windows สดจริงเครื่องหนึ่ง (เช็คลิสต์ 7 ข้อให้ไว้ในแชทแล้ว) ก่อนแจกจริง.

2. **PM-REDESIGN approach D** (invent `page-manager-redesign`, spike 14/14 PASS ก่อนตัดสิน, GO เช่นกัน) — 3 slices:
   - **PM-GUARD** (`c88a379`) — backdrop/Esc/X ทุกทางเข้าปิดวิ่งผ่าน `_pmTryClose()` เดียว: มีงานแก้ไขค้าง (`pending>0`) → โชว์คำเตือนในจอ (บันทึก/ทิ้งการแก้ไข ผ่าน undo-loop) แล้วปฏิเสธการปิด; ลบหน้า → confirm ในจอบอกจำนวนงานวัดที่ผูกอยู่ (แทน browser `confirm()`); ไม่มี PDF เปิดอยู่ → hint มองเห็นได้แทน silent return. Guard `LITE_PM_GUARD_OK` RED 5/5 → GREEN 7/7 (รวมเคส `BUG-20260810`, ⇧F12 หลัง upload). **แก้ field report ตรงตัว** "เปิด page manager แล้วคลิกนอก = งานหาย".
   - **TAG-JIT** (`b0a13bf`) — banner chip อ่าน `curPage` สดตอนคลิก (เดิม: closure จำหน้าเก่าค้าง ติดป้ายผิดหน้า); banner ซ่อน + pending tool เคลียร์ตอน `afterPage`; `__jitWrapped` ตั้งเป็น true หลัง wrap สำเร็จเท่านั้น + retry ladder 5×200ms. Guard `LITE_TAG_JIT_BANNER_OK` RED 2/2 → GREEN.
   - **WIZ-UNLOCK** (`fb9b2af`, breaking-ish UX policy change — user approve ที่ invent checkpoint) — `wiz-auto.js` 256→135 บรรทัด: ถอด auto-open trigger + global keydown/mousedown hard-lock ทิ้งทั้งหมด — F12 wizard เหลือแบบเปิดเองอย่างเดียว, วินัยการติดแท็กใช้ per-page tag-jit gate แทน. **ปิด `BUG-20260810` เชิงโครงสร้าง** (⇧F12 ไม่มีอะไรกลืนแล้ว). เทสเขียนใหม่ตาม contract ใหม่ทั้งคู่: `test_wiz_auto.py` 8/8, `test_bug_force_setup.py` 8/8 (coverage ส่วนที่ไม่เกี่ยว lock คงเดิมทุกจุด). Suite หลังก้อนนี้: **103/104**.

3. **SHELL** (`2b1887f`, sprint card `SHELL-STATUS` + `SHELL-FLOAT`, ผ่าน needs-GO ritual แล้ว — `PRIOR_ART_MATURE` เลย **skip invent เต็มตามกฎ**, grounded บน invent `fullscreen-canvas-ui` GO 2026-05-19):
   - `lite/static/js/status-bar.js` (NEW, 210 บรรทัด) — status bar ล่าง 7 ช่อง: page/floor (คลิก = เปิด Page Manager), scale state, tool (ไทย), draw-target layer, snap indicator (กู้คืนช่องที่หายไปตอน menu-flyout rebuild), dirty dot, current-floor net ผ่าน `ObjectAgg.byFloorRole`. **I2 RITUAL ทำครบ:** ลงทะเบียน `_sbFloorNet` เป็น I2 consumer ใน `lite/tests/INVARIANTS.md` + เพิ่ม arc-inclusive parity fixture ใน `test_summary_arc_parity.py` (`sbOk: True`). ซ่อนตอน focus mode.
   - `lite/static/js/float-panel.js` (NEW, 232 บรรทัด) — ห่อ `#picker` แบบ Photoshop: ลากได้ (clamp ในขอบ stage), พับได้, ซ่อนได้พร้อม edge restore-tab, dblclick reset, ตำแหน่ง persist ที่ `bmaLite.floatPanel.v1`. ระหว่าง build เจอ+แก้ collision จริงกับ `empty-state.js` overlay. `ui-lite.html` +2 script tag เท่านั้น (1189→1191/1200). Guards: `LITE_STATUS_BAR_OK` 6/6, `LITE_FLOAT_PANEL_OK` 7/7. Suite หลังก้อนนี้: **105/106** — fail เดียวคือ `test_closing_dup_strip.py` (pre-existing, คงเดิมไม่เปลี่ยน).

4. **Ledger/roadmap close** (`d231be5`/`3534d35`/`f89659d`) — เพิ่ม 3 แถวใน `SHIPS.jsonl` (`PKG-PORTABLE-20260810`, `PM-REDESIGN-D-20260810`, `SHELL-20260810`); `BUG-20260810` mark CLOSED STRUCTURALLY; ทั้ง 2 invent + ทั้ง 2 SHELL card mark SHIPPED ใน `PHASE_INDEX.md`. Invent docs (`docs/invent/page-manager-redesign.md` + `docs/invent/lite-zero-install-packaging.md`) เพิ่ม Decision section แต่ละไฟล์. `check_executable_truth.py` → `TRUTH_CHECK_OK` 5/5.

**Why:** ทั้ง 2 invent pipeline (research→diverge→spike ALL PASS→checkpoint) ผ่านครบตั้งแต่ตอนบ่าย รอแค่ human GO — user สั่ง "go ทั้งสองตัว" ช่วงเย็น. PM-GUARD แก้ตรงจุดของ field report จริง (คลิกนอก page manager = งานหาย); WIZ-UNLOCK เป็นการตัดสินใจนโยบาย UX ที่ user เห็นชอบแล้วว่าการบังคับเปิด wizard ไม่จำเป็นอีกต่อไปเมื่อมี tag-jit gate คุมวินัยแทน; SHELL ทำตาม mockup ที่ user เลือกไว้ตอนบ่าย (Shell v2 rev.3 — เมนูเดิมคงไว้ทั้งหมด, canvas full-bleed, floating layer palette แบบ Photoshop, status bar บางไว้).

**Files touched:** `.gitignore`, `lite/README.md`, `lite/build_portable.bat` (NEW), `lite/launch_lite.py`, `lite/static/js/page-manager-ui.js`, `lite/tests/test_pm_guarded_close.py` (NEW), `lite/static/js/tag-jit.js`, `lite/tests/test_tag_jit_banner_fix.py` (NEW), `lite/static/js/wiz-auto.js`, `lite/tests/test_wiz_auto.py`, `lite/tests/test_bug_force_setup.py`, `lite/static/js/status-bar.js` (NEW), `lite/static/js/float-panel.js` (NEW), `lite/tests/test_status_bar.py` (NEW), `lite/tests/test_float_panel.py` (NEW), `lite/tests/INVARIANTS.md`, `lite/tests/test_summary_arc_parity.py`, `lite/ui-lite.html` (+2 script tags, 1189→1191/1200), `docs/status/PHASE_INDEX.md`, `docs/status/SHIPS.jsonl`, `docs/invent/page-manager-redesign.md`, `docs/invent/lite-zero-install-packaging.md`.

**Tests:** ทุก slice มี RED-first guard test ก่อน build จริง — `LITE_PM_GUARD_OK` RED 5/5→GREEN 7/7, `LITE_TAG_JIT_BANNER_OK` RED 2/2→GREEN, `test_wiz_auto.py` 8/8 + `test_bug_force_setup.py` 8/8 (rewritten to new no-lock contract), `LITE_STATUS_BAR_OK` 6/6, `LITE_FLOAT_PANEL_OK` 7/7. Full suite progression: 103/104 (หลัง WIZ-UNLOCK) → 105/106 (หลัง SHELL) — fail เดียวตลอดคือ `test_closing_dup_strip.py` (pre-existing, ยืนยันแล้วจาก sprint ก่อนหน้าว่าไม่เกี่ยวกับงานที่แก้). `check_executable_truth.py` → `TRUTH_CHECK_OK` 5/5.

**Commits:** `fc4a407` (feat: PKG-PORTABLE), `c88a379` (feat: PM-GUARD), `b0a13bf` (fix: TAG-JIT), `fb9b2af` (feat!: WIZ-UNLOCK), `2b1887f` (feat: SHELL status-bar+float-panel), `d231be5`+`3534d35`+`f89659d` (docs: GO + ledger/roadmap close).

**Process note:** ทั้ง 2 invent pipeline รันเต็มตอนบ่าย (research→diverge→frame→spike ALL PASS→checkpoint→user GO "go ทั้งสองตัว"); build ทั้งหมด delegate ให้ `lite-builder` (sonnet) ตาม no-git rule; orchestrator รีวิว diff ทีละ slice + commit เอง. proto ไม่ถูกแตะทั้งก้อน.

**Known gaps / follow-ups:** (1) ค้างตัดสินใจ user — E pywebview ruling (นับเป็น Electron ต้องห้ามไหม), Page Hub merge เต็ม (approach C, long-term vision), จานสี (layer palette) mockup ยังต้อง needs-GO (S-2..S-9); (2) `test_closing_dup_strip.py` pre-existing failure ยังไม่ investigate แยก; (3) module-review top-10 leftover (role=gfa hardcode `page-folder-layers.js:712`, mixed-category m² loss `object-agg.js:238`, CFSS freeze ทิ้ง catId, arc sweep sign, B-8 counting move, wizard modal ไม่อยู่ใน `modalOpen()`, listener leak `overview-grid`, export-pdf ไม่ข้าม excluded pages); (4) page-pipeline "slice 3-4" (pageRot/`_scanned` remap ตาม identity ตอน reorder, PM-overlay canvas/pageCount sync, wizard thumbnails ผ่าน `serverNum()`); (5) **user manual-test list (8 ข้อ, เครื่องเช็คไม่ได้)** — ดูรายละเอียดใน `docs/status/NEXT_ACTIONS.md` "Immediate Next" อันดับ 1.

---

## 2026-08-10 (บ่าย) — analysis/design bundle: module review 35 ไฟล์ + invent zero-install (HALTED@checkpoint) + BUG pagemgr-blocked + mockup 2 ใบ + system map (branch: main)

**ทำอะไร (กิจกรรมวิเคราะห์/ออกแบบ ไม่มีการแก้โค้ด runtime — ทั้งหมดต่อจาก sprint PM-META เช้านี้):**

1. **Governance audit ของ lite** — ตรวจกฎทั้ง 4 ชั้น (README caps / INVARIANTS I1-I10 / check_executable_truth 5 ด่าน / needs-GO process) → ข้อเสนอ 7 ข้อ เด่นสุด: เพดานวัดเป็น "บรรทัด" ถูกเกมด้วยบรรทัดยาว + hidden module loader, roadmap-recon เป็น run-blocking gate ที่เรียงลำดับผิด (ควรเป็น finalize-gate), กฎ semantic-grouping มีแต่ใน prose ไม่มี guard. ยังไม่ file เป็น sprint — รอ user เลือกข้อ.
2. **Module-by-module review 35 ไฟล์ / 12,758 บรรทัด** (5 agent ขนาน: pages/layers/measure-CFSS/report/chrome) → คะแนน เขียว 11 · เหลือง 18 · แดง 6 (`page-rotate`, `layer-dnd`, `layer-move`, `page-folder-layers`, `wiz-auto`) + **top-10 บั๊กเรียงความเสียหาย** (อันดับ 1-2 กลายเป็น sprint PM-META เช้านี้; ที่เหลือคิว: role=gfa hardcode `page-folder-layers.js:712`, mixed-category m² loss `object-agg.js:238`, CFSS freeze ทิ้ง catId, arc sweep sign จาก partial centroid, B-8 counting move, wizard modal ไม่อยู่ใน modalOpen(), listener leak overview-grid, export-pdf ไม่ข้าม excluded) + pattern เชิงระบบ 5 ข้อ (monkey-patch ซ้อน, guard-flag-ก่อน-wrap, listener รั่ว, number-keyed dicts ไม่ remap, สัญญาณตรวจสอบที่ตรวจไม่ได้แล้ว เช่น assertEnginesAgree เทียบตัวเอง).
3. **สถาปัตยกรรม "server ดีสุดแล้วหรือไม่" + /lite-invent เต็ม pipeline** — idea `lite-serverless` → research (haiku) verdict `PRIOR_ART_PARTIAL` (mupdf.js ติด AGPL, pdf-lib unproven >100MB, PDF.js worker heap เพดานเดิมจาก lite-range-streaming NOGO) → **reshape เป็น `lite-zero-install-packaging`** → diverge 5 ทาง score เสมอ 3 ที่ 25 (A onefile exe / B portable embed / E pywebview) → **spike A+B จริง ผ่าน eval ครบ 3 เคสทั้งคู่** (zero-Python launch / permit 45 หน้าชื่อไทย / double-launch): A=77.7MB cold 8-21s, B=112MB cold 6.5s, E side-check WebView2 เปิดได้จริง → **HALTED ที่ human checkpoint** (`docs/invent/lite-zero-install-packaging.md`) รอ GO/NOGO/RESHAPE + คำตัดสิน E ว่านับเป็น Electron ต้องห้ามไหม. Spike evidence: `lite/sandbox/invent-lite-packaging/` (commit เฉพาะ spec/script/results — binary ไม่เข้า git).
4. **BUG-20260810-lite-pagemgr-blocked** — user field report "เปิด pagemanager ไม่ได้" → Playwright repro ยืนยัน root cause: wiz-auto capture lock กลืน ⇧F12 + เมนูอยู่ใต้ #ov จนกว่าจะ tag ≥1 หน้า; `pmOpenManager()` เองปกติ (direct call เปิดได้) — **ไม่ใช่ regression จาก 878effd**. Workaround แจ้ง user แล้ว (tag 1 หน้าก่อน). Filed ใน PHASE_INDEX `### findings 2026-08-10` สถานะ bug-queued, fix direction: allowlist ⇧F12 ใน lock + hint แทน silent return — รอ user สั่งแก้.
5. **UI review + mockup 2 ใบ (mockup-first, ยังไม่ตัดสิน):** (a) Page Manager → ข้อเสนอ "🗂 ศูนย์หน้า" รวม F12+⇧F12 เป็นจอเดียว 2 โหมด, tile บอก tag/scale/จำนวนงานวัด, in-overlay delete confirm, pending มองเห็น — `lite/sandbox/mockup-page-hub.html`; (b) Layer panel → คำตัดสิน "วิธีคิดชั้นข้อมูลถูก ชั้น UI ควรเปลี่ยน" → mockup "🎨 จานสีประเภทพื้นที่" แทน layer tree: role เด่นก่อนชื่อ (+/−), โครงชั้น read-only, ตัด jargon — เป็นการ execute S-2/S-3/S-4/S-5/S-9 ที่ค้าง needs-GO ใน ledger `/lite-simplify` พร้อมกัน — `lite/sandbox/mockup-layer-palette.html`.
6. **แผนผังระบบ** — `docs/design/LITE_SYSTEM_MAP.html`: ภาพใหญ่ browser/server, เส้นทางข้อมูล 6 เส้น, แผนที่ 35 โมดูลพร้อมสีสุขภาพ, กฎแก้ 3 สี, ตาราง "แก้เรื่อง X → ไฟล์ไหน + ระวังอะไร".

**Tests:** ไม่มีการแก้โค้ด runtime — no-test rationale ยกเว้น repro script (ข้อ 4, scratchpad) และ spike eval (ข้อ 3, ผลใน `SPIKE_RESULTS.md`). `check_executable_truth` ยืนยัน TRUTH_CHECK_OK หลังแก้ PHASE_INDEX.

**Commits:** `812d7df` (invent doc + PHASE_INDEX findings 2026-08-10 + spike evidence), `38f483a` (mockup Page Hub), `ea97ac3` (mockup Layer Palette), `fb31206` (LITE_SYSTEM_MAP).

**รอ user ตัดสิน (4 เรื่องค้าง):** (1) GO/NOGO/RESHAPE zero-install packaging + คำตัดสิน E; (2) GO mockup ศูนย์หน้า; (3) GO mockup จานสี (=ตัดสิน S-2..S-9 batch); (4) สั่งแก้ BUG-20260810-lite-pagemgr-blocked. บวกงานเทสต์มือ: field re-test PM-META fix + ทดสอบ artifact A/B บนเครื่อง Windows สดจริง (เช็คลิสต์ 7 ข้อแจ้งไว้ในแชทแล้ว).

---

<!-- PM-META + PM-ID (2026-08-10) + BUG-20260706 bug intake ×2 archived to docs/archive/log-2026-08-10.md on 2026-08-10 (ค่ำ finalize: PKG-PORTABLE + PM-REDESIGN-D + SHELL, to keep root at last-2-sessions) -->
<!-- 2026-07-04 full-day 8-ship block + 2026-07-03 (บ่าย) Layer redesign A+B/UX batch 2-3/V2 U-series/undo/staleness-audit archived to docs/archive/log-2026-07-04.md on 2026-08-10 (PM-META + PM-ID sprint finalize, to keep root at last-2-sessions) -->
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
