# Invent: Verify Scale tool

- **idea_id:** in-convo 2026-05-20 (scale-accuracy discussion)
- **short-name:** verify-scale
- **Status:** invent-done-go (→ INV-2026-05-20-001)
- **Source:** user Q on scale calibration accuracy (med-reform .bmaplan review) — proposed a post-calibration cross-check tool.

## Frame

**Problem.** หลังผู้ใช้สอบเทียบสเกล (`finishCalib`) ค่า `verified:true` แปลว่า "ผู้ใช้กดยืนยัน" เท่านั้น — ไม่มีการตรวจอิสระว่าสเกลถูกจริง mis-click ปลายเส้น, พิมพ์ระยะผิด, หรือสแกนยืดไม่สม่ำเสมอ ทำให้พื้นที่เพี้ยน (area error ≈ 2× linear) โดยผู้ใช้ไม่รู้ตัวจนกว่าจะ export.

**Constraints.** ทำงานบน raster PDF · page-scoped · `.bmaplan` schema เพิ่ม field แบบ additive เท่านั้น · single-HTML inline JS (no bundler) · reuse 2-point draw UI เดิม.

**Forbidden surfaces ห้ามแตะ.** `polyAreaM2` / `polyMetrics` / `pdfToC` / `cToPdf` / `RS` / `snap` / `buildSnapIndex` / การ rename `calibScale` schema เดิม / core endpoints. ใช้ `getScaleForPage` + `ptsToM` (read) ได้, เพิ่มฟังก์ชันใหม่ข้าง ๆ.

**Success criteria (spike).** วัดเส้นที่รู้ค่าจริงอันที่ 2 → คำนวณ `%dev = 100·|measured − entered|/entered` ได้ถูกต้อง (verify กับเลขมือ), แสดง deviation + เขียว/เหลือง/แดงตาม threshold (เช่น <0.5% เขียว, <2% เหลือง, ≥2% แดง), และเสนอ action (รับ / re-calibrate / เฉลี่ย) — ทั้งหมดในหน้า sandbox เดียวเปิดด้วย browser ไม่ต้องมี server.

**Out of scope.** ไม่ทำ auto boundary detection, ไม่แตะ math พื้นที่, ไม่ georeference เต็มรูป (multi-GCP affine), ไม่ตัดสิน legal/FAR. MVP = 2nd-reference cross-check; least-squares หลาย references เป็น optional stretch.

## Research

### Verdict: PRIOR_ART_PARTIAL

**1. In-repo prior art**
- `PHASE_INDEX.md` HT-7 — per-page scale *enforcement* (gate ก่อนวัด) แต่ไม่ตรวจว่าสเกลถูก; `verified` = แค่กดยืนยัน
- `proto/ui.html:2103` `finishCalib()` set `calibrated/verified:true` ทันทีหลัง 2-point เดียว ไม่มี cross-check; `ptsToM()`/`getScaleForPage()` เป็นจุด read
- `proto/ui.html:2853` `phase1Warnings()` มีระบบ warning ต่อหน้าอยู่แล้ว — พับ scale-accuracy warning เข้าไปได้
- `DEVELOPMENT_PLAN.md` — ระบุว่า verification เป็น step ที่ขาด แต่ถูก defer

**2. Library scan**
- `least-squares` (npm, MIT, ~200 LOC, 0-dep) — inline ได้ ใช้ fit N references → best-fit scale + residual (stretch only)
- jStat / numericjs — overkill, ไม่เหมาะ single-HTML
- Apryse/Foxit SDK — ต้อง bundler/server, ใช้ไม่ได้กับ pattern ปัจจุบัน

**3. CAD/GIS prior art**
- Bluebeam Revu — แนะ "double-calibrate" (H+V เช็ค stretch) แต่ไม่มี residual report
- PlanSwift / On-Screen Takeoff — docs แนะตรวจ ≥2 references แต่ผู้ใช้ทำเอง
- QGIS Georeferencer — RMS error ต่อ GCP เป็นมาตรฐาน (math พร้อม) แต่เป็น multi-point affine
- AutoCAD/Rhino — ไม่มี verify UX, เป็นความรับผิดชอบผู้ใช้

**4. Literature/algorithms**
- area error ≈ 2× linear error (Green's theorem / shoelace)
- least-squares + RMSD `sqrt(mean(resid²))` — math มาตรฐาน
- NIST metrology — แนะ repeated independent measurement + residual เพื่อจับ systematic error

**5. Competitor UX**
- ทุกเจ้า (Bluebeam/Foxit/Adobe/PlanSwift/OST) มี calibrate 2-point + แนะตรวจซ้ำ — **ไม่มีเจ้าไหนทำ "วัดอันที่ 2 → เทียบ % → เตือนอัตโนมัติ" เป็นเครื่องมือ integrated**

**Takeaway:** math แก้แล้ว, library มีถ้าจะ fancy, แต่ value = **UX pattern + integration เข้ากับ calibration + warning pipeline ของ BMA-Plan บน raster web-canvas** ซึ่งยังไม่มีใครทำ MVP = `%dev` บน 2nd reference; schema เพิ่ม optional `verifyReferences[]` บน calibScale.

## Diverge

- **A — Single-shot %dev modal (axis: UX).** หลัง/หรือสั่งจาก Scale menu → reuse 2-point draw เดิม วัดเส้นที่ 2 + พิมพ์ระยะจริง → modal คำนวณ `%dev=100·|d_meas−d_enter|/d_enter` โชว์ band เขียว/เหลือง/แดง + 3 ปุ่ม Accept / Re-calibrate / Average. ฟังก์ชันใหม่ `openVerifyModal()`/`verifyFinish()`. schema: `calibScale.verifyResult{pct,action,verifyPts_per_m,ts}` (optional). forbidden:NO. lib:none.
- **B — stored verifyReferences[] + confidence (axis: data-model).** ทุกครั้ง append entry แทน overwrite; `scaleConfidence()` คำนวณ mean + `rmsDevPct` + `confidenceLevel(high/med/low/unverified)` โชว์ที่ badge/Scale Manager; `pts_per_m` ไม่เปลี่ยนจนกดเลือก. schema: `verifyReferences[]`+`confidenceLevel`. forbidden:NO.
- **C — dual-axis H/V stretch detector (axis: algorithm).** วาด ref แนวนอน + แนวตั้ง → `computeAxisStretch()` คืน `stretchRatio=hPpm/vPpm`; ถ้า |ratio−1|>0.5% เตือน "ภาพยืดไม่สม่ำเสมอ". จับ non-uniform scan distortion ที่ single-axis จับไม่ได้. schema: `axisVerify{}`. forbidden:NO.
- **D — live canvas confidence badge (axis: representation).** เก็บผล verify แล้ว `drawScaleBadge()` ใน `redraw()` วาด tick สีข้างเส้น scale (เขียว/เหลือง/แดง) ผ่าน `pdfToC` (read-only). schema: `verifyResult{midPt,pct,ts}`. forbidden:NO.
- **E — phase1Warnings + export note (axis: integration).** พับ deviation เข้า `phase1Warnings()` (append block ใหม่ท้าย) → โชว์ใน Check panel/Summary Warnings tab อัตโนมัติ + เพิ่มคอลัมน์ `scaleVerifyNote` ใน export. schema: `verifyResult{pct,ts}`. forbidden:NO. ถูกที่สุด ~60 LOC.

## Score

| approach | novelty | accuracy | UX | model-fit | boundary | cost | total |
|---|---|---|---|---|---|---|---|
| **A modal %dev** | 4 | 4 | 5 | 4 | 5 | 5 | **27** ⭐ |
| B stored array | 3 | 4 | 3 | 5 | 5 | 4 | 24 |
| C dual-axis H/V | 5 | 5 | 3 | 3 | 5 | 3 | 24 |
| D canvas badge | 4 | 4 | 4 | 4 | 5 | 4 | 25 |
| E warnings fold | 3 | 3 | 4 | 5 | 5 | 5 | 25 |

Score-check (phase 5): อันดับ 1 (A) `forbidden_surface_touch:NO` + อยู่ใน Phase 1 boundary → ไม่ต้อง override.

## Recommendation

**Spike A ก่อน** — คะแนนสูงสุด, UX ดีสุด, ถูกสุด (~80 LOC), map ตรงกับ success criteria. **Fallback: D (canvas badge)** — ถ้า 3 ปุ่มของ A รู้สึก decision-fatigue, D แค่ปั๊ม badge บน canvas ไม่บังคับเลือก และ build บน schema ของ A ได้ (เพิ่มแค่ `midPt`) → A→A+D เป็น progression ธรรมชาติ. (C น่าสนใจสุดเชิงเทคนิค — จับ scan ยืด — แต่ UX/cost แพง เก็บเป็น stretch ภายหลัง)

## Spike

- **Approach attempted:** A (single-shot %dev modal). File: `proto/sandbox/invent-verify-scale.html` (เปิดด้วย browser ตรง ๆ ไม่ต้องมี server).
- **Outcome: PASS.** known-scale grid (1 ม. = 60 px → true pts_per_m = 40.0). มีเครื่องมือ Set Scale + Verify Scale (snap จุด grid), distance panel, และ verify modal (%dev + band เขียว/เหลือง/แดง + ปุ่ม Accept / Re-calibrate / Average) + เก็บ `calibScale.verifyResult{pct,action,ts}` (additive).
- **Self-test (headless Playwright, `artifacts/run_verify_scale_spike.py`): 10/10 PASS, 0 JS error.** ครอบคลุม: kernel `verifyDev` ทุก band, pipeline calibrate 5 ม. → ppm=40.0000 ตรง true, verify เส้น 3 ม. perfect → 0.00% เขียว, verify 3.12 vs 3 → 4.00% แดง.
- **Finding for real sprint:** การจัด band ที่ขอบ % พอดี (เช่น 2.000%) เปราะกับ float (`10.2−10`=0.19999…) — ในแอปจริงไม่สำคัญ (ค่าตรงขอบจะเป็นเหลืองหรือแดงไม่มีผลเชิงความหมาย) แต่ควรนิยาม threshold ด้วย epsilon เล็กน้อยหรือ doc ว่าเป็นค่าประมาณ.
- **Mirror correctness:** spike จำลอง `RS=1.5` + สูตร `N=round(1000·(72/25.4)/ppm)` ตรงกับ `finishCalib` จริง — ไม่ import ไฟล์ live, ไม่แตะ forbidden surface.

## Decision

**GO** (human checkpoint, 2026-05-20). Promote approach A to sprint `INV-2026-05-20-001` (status `queued` in PHASE_INDEX active queue). Rationale: spike PASS 10/10 with zero forbidden-surface touches; closes the long-standing gap that `calibScale.verified` only meant "user clicked confirm" with no independent check. Follow-ons D (canvas badge) / E (phase1Warnings + export note) optional; C (dual-axis stretch) deferred. Scope skill `/bma-measure-scope` (sub-area ux), close with `/bma-measure-regression`; marker `INV_VERIFY_SCALE_OK`.
