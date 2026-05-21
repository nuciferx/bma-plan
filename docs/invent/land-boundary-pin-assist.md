# Invent: land-boundary-pin-assist

- **Idea source:** `~/.claude/ideas/IDEAS.md` @ 2026-05-21 23:47
- **PHASE_INDEX:** Discovered backlog → `### ideas 2026-05-21`
- **Status:** invent-done-nogo (closed 2026-05-22 at human checkpoint; spike PASS, parked)
- **Summary:** บนหน้าผังบริเวณ ให้โปรแกรมช่วยวางหมุดมุมขอบเขตที่ดินกึ่งอัตโนมัติ จากมุมนอกสุดของแปลง — ลดการคลิกวางมุดเองทีละจุด.

> Reshape constraint (จาก /idea scope flag): Phase-1 ห้าม "auto boundary detection" เต็มรูป → เป้าหมายคือ **semi-auto / snap-assist** เท่านั้น.

## Frame

**Problem.** บนหน้าผังบริเวณ ผู้ใช้ต้องคลิกวางมุมขอบเขตที่ดินเองทีละจุดด้วย Land tool (`activateAreaTool('land')`) ซึ่งบนแปลงหลายมุมหรือ PDF สเกลใหญ่เป็นงานช้าและพลาดง่าย. อยากให้โปรแกรม "ช่วยเดามุมนอกสุด" ให้แล้วผู้ใช้แค่ยืนยัน/แก้.

**Constraints.**
- ต้องทำงานบน **raster PDF** ได้ (ไม่มี vector geometry) — raster-fallback contract บังคับ
- **Phase-1 boundary:** ห้าม full "auto boundary detection" (CV/OpenCV) → ต้องเป็น **semi-auto / snap-assist** เท่านั้น
- page-scoped layer model — หมุด/polygon ผูกกับ `site_boundary` layer ของหน้านั้น
- `.bmaplan` schema **additive only** — ห้ามแก้ field เดิม
- ผลลัพธ์เป็น polygon ที่ดิน type `land` ตามโมเดลเดิม (ป้อนเข้า `polyEdgeTags.role` / setback workflow เดิมได้)

**Forbidden surfaces to avoid:** `polyAreaM2` / `polyMetrics` / `polySelfIntersects` / `pdfToC` / `cToPdf` / `RS` / `buildSnapIndex` + `snap` internals / `.bmaplan` schema fields. ต่อยอด = เพิ่มฟังก์ชันใหม่ข้างๆ + เรียก snap จากภายนอก ไม่แก้ภายใน.

**Success criteria (spike).** เปิด sandbox HTML แล้ว:
1. ผู้ใช้คลิกหยาบๆ รอบแปลง (เช่น 8-12 จุด เลอะๆ) → ระบบคืน "มุมนอกสุด" ที่สะอาด (convex hull + RDP) ≤ จำนวนจุดจริงของแปลง
2. แต่ละมุมที่เสนอ snap เข้าหา corner/endpoint ที่ใกล้สุด ภายใน radius ที่กำหนด (จำลอง snap index)
3. ผู้ใช้ยืนยัน/ลบมุมรายจุดได้ ก่อน commit เป็น polygon
4. ทำงานล้วนใน client, ไม่มี server, ไม่มี build step

**Out of scope (invention pass นี้).** CV corner detection จาก pixel จริง, การ trace เส้นจาก raster อัตโนมัติ (QGIS-style), arc/curved boundary edges, การผูกกับ setback auto-suggest (เป็น sprint แยก).

## Research

> verdict: **PRIOR_ART_PARTIAL** — math (convex hull + RDP) + snap engine + suggest-dialog pattern มีอยู่/พิสูจน์แล้ว; ความใหม่อยู่ที่ UX integration + การ reshape ให้อยู่ในกรอบ semi-auto. **อย่า** diverge เรื่อง math — diverge เรื่อง data-source (hand-drawn vs raster-analyzed) + workflow (suggest-all vs corner-by-corner).

### 1. In-repo prior art
- `proto/ui.html:869` — `freehandTolerance = 4` + RDP perpendicular-distance simplification (Phase H.1 freehand) → reuse ได้
- `proto/ui.html:1496` — `buildSnapIndex()` + `snap(cx,cy)` (endpoint/midpoint/center/nearest/intersection/perpendicular) → snap มุมที่เดาเข้าหา corner จริง
- `docs/design/SITE_PLAN_MEASUREMENT_PLAN.md §5.1` — `polyEdgeTags.role` taxonomy (front_road/side_left/side_right/back/canal/ignore) → ปลายทางของมุมที่เดา
- `docs/design/SITE_PLAN_UI_MOCKUP.md §4.8` — "setback auto-suggest dialog" = pattern เสนอ-แล้ว-ผู้ใช้ยืนยัน มีร่างแล้ว
- `sprints/completed/2026-05-17-inv-freeform-area/` — freeform Alt-drag capture + snap-bypass พิสูจน์แล้ว (drag-vs-snap interaction model)
- `PHASE_INDEX.md` — flag ชัด: "auto boundary detection" = Phase-1 forbidden → ต้อง semi-auto

### 2. Library scan (inline-JS, no bundler)
| lib | ใช้ได้ไหม | note |
|---|---|---|
| **convexhull-js** (Andrew monotone chain) | ✅ viable | MIT, ~8KB, CDN, หา outermost corners O(n log n) |
| **simplify.js** (RDP) | ✅ viable | BSD, ~4KB, CDN, ลด noise มุม |
| OpenCV.js | ❌ wrong-shape | 8MB+ WASM, bundler-heavy, ขัด Phase-1 (CV) |
| hull.js (concave) | ~ marginal | convex ง่าย+เร็วกว่าสำหรับ "มุมนอกสุด" |
| paper.js | ❌ | ~200KB, bundler-dependent |

### 3. CAD/GIS incumbents
- **AutoCAD** — polyline bulge per-vertex (arc); snap-to-vertex precision, ไม่ auto-detect
- **Rhino** — End osnap snap ปลาย/มุม polyline; manual + snap, ไม่ auto-suggest
- **QGIS Raster Tracer** — semi-auto line-following: คลิก seed → trace raster connectivity
- **ArcGIS Vectorization Trace** — คล้าย QGIS, follow centerline ของ raster cells
- **Bluebeam Dynamic Fill** — edge-constrained fill (ถ้ามี vector) / threshold raster — ไม่ใช่ corner detection
- **Photoshop Magnetic Lasso** — edge-snapping ขณะวาด, วาง anchor อัตโนมัติตาม contrast

### 4. Algorithms
- Convex Hull: Graham scan / Andrew monotone chain (O(n log n)) — หา outermost corners
- Douglas-Peucker (RDP) — ลด vertex รักษารูปทรง
- Harris corner / Canny contour — raster CV, หนักเกินสำหรับ inline-JS → ทาง server ถ้าจำเป็น (อยู่นอก scope)
- Green's theorem / shoelace — area (ถ้าต่อ arc edge ในอนาคต)

### 5. Competitor UX
- Bluebeam / Foxit — manual click-per-corner, ไม่มี snap-to-corner suggest
- QGIS Raster Tracer — semi-auto "guide tool to boundary then confirm" = archetype ที่ใกล้สุด
- Rhino — snap ซ่อนจนกว่า hover ใกล้มุม (BMA snap engine สะท้อนอยู่แล้ว)

**ไม่มีคู่แข่งตัวไหน** ship "semi-auto land-boundary corner-pin from rough outline" → ส่วนที่ใหม่ = UX integration เข้ากับ site-plan layer + snap + suggest-dialog ของ BMA.

## Diverge

5 approaches, แต่ละตัวต่างแกน:

- **A — Rough-outline → hull+RDP → confirm-all** (axis: workflow). Shift+L เข้า assist sub-mode → คลิกหยาบ 8-12 จุดรอบแปลง → Enter → `convexHull(mPts)` → `rdpSimplify` (reuse ui.html:1661) → snap แต่ละมุม → dialog ยืนยัน/ลบรายมุม → commit เป็น land polygon. ไม่มี field ใหม่. lib: convexhull-js ~8KB.
- **B — Draw-then-enhance** (axis: integration). วาด land polygon ปกติก่อน → ปุ่ม ribbon "ปรับให้นอกสุด" โผล่เมื่อเลือก closed land poly → `convexHull(pts)` → snap → diff overlay (เก่าเทา/ใหม่เขียว) → ยืนยัน replace in-place (pushUndo). ถูกสุด ~80 บรรทัด.
- **C — Magnetic-lasso trace** (axis: UX). Land tool โหมด magnetic: mousemove debounce 200ms อ่าน `userSnapLines()` → cursor ดูดเข้าเส้นใกล้สุด + ghost trail → คลิก commit. ใหม่สุดแต่ accuracy พึ่ง skill ผู้ใช้ + เสี่ยง creep ไป CV.
- **D — Bbox → corner-grid picker** (axis: data-source). ลาก bounding box → ระบบเสนอ candidate (4 มุม bbox + midpoints + snap ep ใน bbox ≤20) → ผู้ใช้คลิกเลือกมุม → sort CCW → commit. ปลอดภัยสุดแต่ accuracy จำกัดที่ snap points ใน bbox.
- **E — Vector-snap-hull (server-assist)** (axis: data-source). ปุ่มเดียว → กรอง `pageData.snaps[]` (จาก /analyse เดิม) → `convexHull` → rdp → dialog. ไม่ต้องวาดเลย แต่**พึ่ง vector PDF** → raster (เคสหลัก) ใช้ไม่ได้ → fallback abort graceful.

> ทุก approach `forbidden_surface_touch: NO` และไม่มีตัวไหนแตะ CV pixel จริง (Phase-1 safe).

## Score

| approach | novelty | accuracy | UX | model-fit | boundary | cost | total |
|---|---|---|---|---|---|---|---|
| **A rough-outline hull** | 4 | 4 | 5 | 5 | 5 | 4 | **27** |
| B draw-then-enhance | 3 | 4 | 4 | 5 | 5 | 5 | **26** |
| C magnetic-lasso | 5 | 3 | 4 | 4 | 4 | 3 | 23 |
| D bbox-corner-grid | 3 | 3 | 3 | 5 | 5 | 5 | 24 |
| E vector-snap-hull | 2 | 5 | 4 | 5 | 5 | 3 | 24 |

ประเด็นสำคัญ: A กับ B ห่างกัน 1 แต้ม — A สำหรับคนคลิกมุมเป๊ะไม่ไหว (หยาบก่อน-เก็บทีหลัง), B สำหรับคนวาดได้แต่อยากให้ clean ทีหลัง. E พึ่ง vector เต็มตัว → ตกเพราะเคสหลักเป็น raster. C เสี่ยง creep เข้า CV (ต้องบังคับใช้ `userSnapLines()` เท่านั้น).

**Phase-5 verify:** อันดับ 1 (A) ไม่แตะ forbidden surface, ไม่ข้าม Phase-1 boundary → ผ่าน ไม่ต้อง re-rank.

## Recommendation

**Spike A ก่อน** — UX score สูงสุด, ตรงกับ pain ที่ผู้ใช้พูด ("คลิกหยาบรอบแปลง") เป๊ะ, และ `rdpSimplify` compile อยู่ใน ui.html:1661 แล้ว → math cost เกือบศูนย์.
**Fallback B** ถ้า human-test บอกว่า "Shift+L เข้าโหมดใหม่" งงสำหรับผู้ใช้ Land tool เดิม — B layer ทับ flow เดิมเป็นปุ่ม post-process, drop-in ปลอดภัยสุด.

## Spike

**Approach attempted:** A (rough-outline → convex hull → RDP → snap → confirm).
**File:** `proto/sandbox/invent-land-boundary-pin-assist.html` — standalone, no server, no build. เปิดในเบราว์เซอร์ได้เลย.
**Implementation:** `convexHull()` (Andrew monotone chain) + `rdpSimplify()` (copy ของ ui.html:1661, isolated) + `snapToCorner()` (จำลอง snap index ด้วย hardcoded 6-corner L-shape parcel, radius 34px). UI: คลิกหยาบ → ▶ วิเคราะห์ → dialog รายมุม (snapped badge) + ลบ/คืนรายมุด → Commit เป็น land polygon.

**Outcome: PASS 5/5** (headless Playwright, `window.__SPIKE_PASS=true`):
```
rough=13 → hull=7 → rdp=5 → suggested=5 (snapped 5/5)
✓ hull ≤ rough              ✓ rdp ≤ hull
✓ suggested ≤ true-corner count (6)
✓ ≥3 corners snapped to real corners
✓ all snapped pins lie exactly on a true corner
```
Screenshot: `artifacts/invent/land-boundary-pin-assist/spike-A.png`

**Finding (สำคัญสำหรับ sprint จริง):** RDP tolerance สำคัญ — ที่ tol=12 จุดคลิกกลางขอบ 2 จุดเหลือรอดเป็น hull vertex ปลอม (suggested=7, snapped 5/7). bump → tol=25 สะอาด (suggested=5, snapped 5/5). สรุป: (1) convex hull ตัดมุมเว้า (concave) ของ L-shape ทิ้ง — ผู้ใช้ต้องเพิ่มมุมเว้าเองใน dialog (ข้อจำกัดของ convex; ถ้าแปลงเว้าเยอะ approach นี้อ่อน → อาจต้อง concave hull ใน sprint จริง). (2) tolerance ควรเป็น snap-radius-relative ไม่ใช่ค่าคงที่. (3) human-delete dialog เป็น safety net จำเป็น ไม่ใช่ optional.

**Scope confirmation:** ไม่มีการแตะ pixel จริง / CV — snap จาก geometry ล้วน → อยู่ในกรอบ Phase-1 semi-auto.

## Decision

**NOGO** — human checkpoint 2026-05-22. Spike PASS แต่ผู้ใช้ตัดสินไม่โปรโมตเป็น sprint ตอนนี้.

**สถานะที่ทิ้งไว้:** artifact + sandbox spike เก็บไว้พร้อม revive. การพิสูจน์เชิงเทคนิคผ่านแล้ว (semi-auto, Phase-1 safe, ไม่แตะ forbidden surface) — สิ่งที่ยังไม่คุ้มลงมือคือ value/priority (idea เป็น p-low) เทียบกับข้อจำกัด convex-hull กับแปลงเว้า.

**ถ้าจะ revive ในอนาคต** — research (PRIOR_ART_PARTIAL) ยัง valid. จุดที่ต้อง RESHAPE ก่อนทำจริง:
- convex hull → **concave hull / alpha shape** สำหรับแปลงเว้า (L-shape, แปลงไม่ปกติ) — ข้อจำกัดหลักที่ spike เผย
- RDP tolerance ผูกกับ snap-radius (relative ไม่ใช่ค่าคงที่)
- พิจารณา approach B (draw-then-enhance, ~80 บรรทัด, drop-in) เป็นทางเริ่มที่ถูกและปลอดภัยกว่า A
