# Invent: centerline-snap-dashed-boundary

- **Idea source:** `~/.claude/ideas/IDEAS.md` @ 2026-05-24 22:14
- **PHASE_INDEX:** Discovered backlog → `### ideas 2026-05-24`
- **Status:** invent-in-progress (started 2026-05-24 via `/bma-invent 2026-05-24-22-14`)
- **Summary:** เมื่อผู้ใช้ลากตามเส้นปะของขอบเขตที่ดิน (โฉนด) ที่มีความหนามองเห็นได้ การลากตามขอบนอก / ขอบใน / กลางเส้น ได้พื้นที่ 3 ค่าต่างกัน — ตัวที่ถูกคือกลางเส้น. ต้องการกลไกให้ผลลัพธ์คงที่ ไม่ว่าผู้ใช้จะ "รู้สึก" ว่าลากตรงไหน.

> Related prior art (NOT a duplicate): `docs/invent/land-boundary-pin-assist.md` (closed 2026-05-22 NOGO) เป็นเรื่อง "เดามุมจากคลิกหยาบ"; เรื่องนี้คือ "snap เข้ากลางเส้นตอนวาด" — กลไกคนละชั้น แต่ research แชร์กันได้บางส่วน (raster/vector constraint, snap engine map).

## Frame

**Problem.** ผู้ใช้กำลังลาก polygon ตามขอบเขตที่ดินที่วาดเป็น **เส้นปะที่มีความหนามองเห็นได้** (cadastral deed boundary, 3–8 px ขึ้นกับการ scan). คลิกตามขอบนอกของแถบ vs ขอบใน vs กลาง → ได้พื้นที่ 3 ค่าต่างกัน (errror = stroke_width/2 ต่อ vertex, ทบกันรอบ perimeter). ค่าที่ถูกคือกลางเส้น. ผู้ใช้ไม่มีกลไกใดๆ ช่วยให้ผลลัพธ์คงที่ — pure eyeballing บน raster ระดับ pixel.

**Constraints.**
- **PDF type = mix** — ต้องครอบคลุมทั้ง raster scan (เคสหลัก) และ vector PDF ที่มี stroke จริง. Vector-only solution ตกชั้น `E` เหมือน `land-boundary-pin-assist` Approach E.
- **Raster-fallback contract** — ทำงานได้แม้ไม่มี vector geometry.
- **Phase-1 boundary** — "centerline ของ stroke" = geometry/snap, **ไม่ใช่** auto-boundary-detection ของรูปทรงเต็มๆ → in-scope. ห้าม AI / OCR / CV ระดับ scene-understanding.
- **inline JS, no bundler** — ≤ ~30KB CDN lib OK (skeletonization-js วัด ~20KB), multi-MB (OpenCV.js WASM) BLOCK.
- **`.bmaplan` schema additive only** — ฟิลด์ใหม่อย่าง `traceMode: "outer"|"inner"|"center"` หรือ `centerlineSource: "raster-skel"|"vector-stroke"|"manual"` ใส่ได้ ห้ามแก้ฟิลด์เดิม.
- **Page-scoped layer model** — ผลลัพธ์เป็น polygon บน layer ของหน้าตาม semanticTag เดิม.
- **Frame budget** — ถ้าทำ live-during-draw ต้อง ≤16ms ต่อ mousemove (60fps). research ระบุ skeletonization-js บน 100×100 ROI ≈ 8–12ms → OK; full-page thinning ≈ second-scale → ต้อง pre-compute หรือทำ on-demand.

**Forbidden surfaces to avoid:** `polyAreaM2` / `polyMetrics` / `polySelfIntersects` / `pdfToC` / `cToPdf` / `RS` / `buildSnapIndex` + `snap` internals (อาจ **เพิ่ม** snap target ใหม่ข้างๆ ได้ ห้ามรื้อ). server.py `extract_snaps_pdfium()` / `extract_snaps_typed()` ปัจจุบันทิ้ง stroke-width — ถ้าใช้ vector route ต้อง **เพิ่ม** field ใหม่ใน response, ห้ามแก้ schema เดิม.

**Success criteria (spike).** เปิด sandbox HTML แล้ว:
1. โหลด raster image จำลองที่มีเส้นปะหนา ~6px วาดเป็น polygon ปิด (สี่เหลี่ยม L-shape หรือคล้าย).
2. ผู้ใช้ลากตาม "ขอบนอก" 1 รอบ + "ขอบใน" 1 รอบ + "กลาง" 1 รอบ → ระบบรายงาน 3 พื้นที่.
3. ระบบเสนอ **centerline-corrected** polygon จากแต่ละการลาก → 3 ผลลัพธ์ที่ corrected ตรงกันภายใน **±0.5%** (เทียบกับ ground-truth area ของกลางเส้นจริง).
4. ทำงานล้วนใน browser, ไม่มี server, ไม่มี build step.
5. Per-mousemove cost (ถ้า approach เลือก live-snap) ≤ 16ms บน ROI ที่ใช้.

**Out of scope (invention pass นี้).**
- Live-wire / Intelligent-Scissors edge-following ที่ trace ตลอดเส้น (ไกลกว่า centerline-snap; sprint แยก).
- Full-page raster-to-vector vectorization (Phase-1 forbidden).
- Concave hull / corner detection (อยู่ใน `land-boundary-pin-assist` แล้ว).
- การ wire เข้า `polyEdgeTags.role` / setback workflow (ใส่หลังจาก go).
- Vector stroke-width recovery ใน server.py (ใส่หลังจาก go ถ้า approach ที่ชนะต้องการ).
- Concave boundary ที่ stroke ตัดตัวเอง (เคสยาก, ใส่หลัง).

## Research

> verdict: **PRIOR_ART_PARTIAL** — math (distance-transform, Zhang-Suen thinning, live-wire) มีอยู่ 30 ปี + JS lib พร้อม (skeletonization-js ~20KB CDN); ความใหม่อยู่ที่ **integration เข้า BMA snap + UX choice ของ outer/inner/center**. ไม่มี incumbent (Bluebeam/Foxit/QGIS/AutoCAD/ArcGIS) ตัวไหน expose stroke-centerline เป็น user choice. **อย่า** diverge เรื่อง math — diverge เรื่อง when (live-during-draw vs post-draw vs on-demand) + how (raster ROI vs vector stroke-width vs hybrid) + UX (auto-correct vs offer choices).

### 1. In-repo prior art
- `proto/ui.html:1496` — `buildSnapIndex()` + `snap()` ครอบคลุม endpoint/midpoint/center/nearest/intersection/perpendicular. **ไม่มี stroke-width awareness** เลย — มอง path หนาบางเหมือนเส้นเดียว.
- `proto/ui.html:2164` — Loupe magnifier (80–160px, 2–8×) มีอยู่แล้วสำหรับ raster precision — leverage ได้.
- `proto/server.py:275–350` — `extract_snaps_pdfium()` / `extract_snaps_typed()` คืน `[x0,y0,x1,y1]` ล้วน, **ทิ้ง stroke-width** ตอน parse. operator-list ของ PDFium/PyMuPDF มีค่า stroke-width อยู่ — ต้องเพิ่ม field ใหม่ในการตอบ ไม่ใช่แก้ schema เดิม.
- `docs/invent/land-boundary-pin-assist.md` (NOGO 2026-05-22) — ปัญหาคนละชั้น (corner-from-rough-click) แต่ pattern "convex-hull + RDP + dialog ยืนยัน" reuse ได้ถ้าจะ post-process centerline.
- **ไม่มี raster-pixel analysis ใน codebase** — ไม่มี distance transform / skeletonization / morphological ops. งานใหม่ทั้งหมด.

### 2. Library scan (inline-JS, CDN-loadable, ≤200KB)
| lib | ใช้ได้ไหม | note |
|---|---|---|
| **skeletonization-js** (LingDong-) | ✅ viable | MIT, ~20KB, CDN, Canvas-based Zhang-Suen, ~8–12ms บน 100×100 ROI binary |
| **skeleton-tracing** (LingDong-) | ✅ complement | MIT, ~30KB, มี WASM, แปลง skeleton → polyline พร้อม snap |
| morph.js (PorkShoulderHolder) | ❌ | erode/dilate ช้าเกิน 16ms |
| paper.js | ❌ | ~200KB + bundler |
| flatten-js | ~ marginal | offset/boolean ใช่ แต่ไม่ตรงโจทย์ raster centerline |
| OpenCV.js | ❌ | 8MB+ WASM, ขัด Phase-1 + size |

**สรุป:** `skeletonization-js` เป็น lib ตัวเดียวที่เหมาะ. ถ้า raster route เลือกแล้ว ใช้คู่กับ `skeleton-tracing` ออก polyline.

### 3. CAD/GIS incumbents
- **AutoCAD Raster Design** — vectorization ทำได้ แต่ไม่ expose centerline-vs-edge choice ใน UI.
- **QGIS Raster Tracer plugin** — semi-auto line-follow (least-cost path บน inverted intensity). ไม่แยก outer/inner/center ให้ผู้ใช้เลือก.
- **QGIS AI Vectorizer (2024)** — click + ปล่อย AI → single path; ไม่มี centerline option.
- **Bluebeam Revu (2025)** — polyline + area ปกติ. ไม่มี stroke-aware mode.
- **Foxit (2025)** — same as Bluebeam.
- **Photoshop Magnetic Lasso** — real-time edge-snapping จาก gradient. คล้าย live-wire — UX archetype สำหรับ "ดูดเข้าเส้นตอนวาด".

> **ไม่มีคู่แข่งตัวไหน** ship "user เลือก outer/inner/center ของ stroke" → ส่วนใหม่ทั้งหมดอยู่ที่ BMA-Plan.

### 4. Algorithms / literature
- **Distance Transform** (Chamfer / Felzenszwalb) — O(n) per pass, per-pixel ระยะถึง boundary. Chamfer ~2× เร็วกว่า Euclidean. 100×100 ROI < 5ms.
- **Zhang-Suen Skeletonization** — O(n·k) k≈3–10 passes, ลดเป็น 1-pixel skeleton. Stable, no tuning.
- **Skeleton Tracing** (LingDong) — O(n) ใน skeleton pixels → polyline พร้อม snap.
- **Intelligent Scissors / Live-Wire** (Mortensen-Barrett 1995) — DP shortest-path บน gradient. 8–15ms ต่อ move. Interactive. ต้องการ contrast แรง.
- **Polygon offset / Minkowski sum / straight skeleton** — สำหรับ "trace ขอบเดียว → offset w/2 เข้ากลาง". flatten-js / paper.js รองรับ vector offset.
- **Per-mousemove cost บน 100×100 ROI**: distance-transform + Zhang-Suen + trace ≈ 12–20ms (ภายใน 16ms ถ้า debounce + ROI ลด).

### 5. Competitor measurement UX
- **Bluebeam / Foxit** — click-per-vertex manual ล้วน, ผู้ใช้รับผิดชอบเลือกเอง.
- **QGIS Raster Tracer** — click-start → live snap preview → click-end. Best-in-class "ตอนลากเห็นเส้นดูดอยู่".
- **PlanGrid / ArcGIS** — same as Bluebeam family.

> UX pattern ใกล้ที่สุด = QGIS Raster Tracer's live-snap-preview-during-draw. ถ้า BMA เพิ่ม "toggle: outer / inner / center" ลง preview นี้ = unique.

**Sources:**
- [LingDong-/skeletonization-js](https://github.com/LingDong-/skeletonization-js), [LingDong-/skeleton-tracing](https://github.com/LingDong-/skeleton-tracing)
- [QGIS Raster Tracer Plugin](https://plugins.qgis.org/plugins/raster_tracer/), [Bunting Labs AI Vectorizer](https://buntinglabs.com/blog/introducing-ai-qgis-plugin-for-vectorization)
- [Mortensen-Barrett Intelligent Scissors](https://www.semanticscholar.org/paper/Interactive-Segmentation-with-Intelligent-Scissors-Mortensen-Barrett/492a9a96dc0e1b1493748118e8b9aea85e6a5e10)
- [Distance Transform and Computation (arxiv)](https://arxiv.org/pdf/2106.03503)
- [AutoCAD Raster Design Vectorization](https://help.autodesk.com/cloudhelp/2026/ENU/AutoCAD-RasterDesign/files/GUID-C324644D-CB2B-4F31-8817-A3EFE8763FEC.htm)
- [Bluebeam Revu Measure Tool](https://support.bluebeam.com/user-manual/menus/tools/measure-tool.html), [PDF.js stroke properties #7767](https://github.com/mozilla/pdf.js/issues/7767)

## Diverge

5 approaches, แต่ละตัวต่างแกน (when × data-source × UX × integration × snap-reliance):

### A — Click-time local-ROI skeletonize  (axis: When=on-each-click · Source=raster local ROI)

ทุกครั้งที่คลิกใน area tool, grab canvas ROI 100×100 px รอบ cursor → Otsu binarise → Zhang-Suen thinning (skeletonization-js ~20KB) → หา skeleton pixel ที่ใกล้จุดคลิกที่สุด → คืนค่า corrected coord ฉีดเข้า `mPts` หลัง `cToPdf` ก่อน `snap()` จะทำงาน.

```
click(cx,cy) → roiImageData=ctx.getImageData(cx-50,cy-50,100,100)
  → binarise → ZhangSuen → skeletonPixels
  → nearest skeletonPixel to (50,50) → offsetBack → corrected (cx',cy')
  → cToPdf(cx',cy') → push to mPts
```

- **area_math**: unchanged (`polyAreaM2` untouched)
- **user_gesture**: เหมือนเดิม 100% — silent auto-correct ทุกคลิก
- **data_delta**: `poly.traceMode="centerline-roi"` (optional, additive)
- **forbidden_touch**: NO — bypass `snap()` ระดับ pre-snap, ไม่แก้ snap internals
- **lib**: skeletonization-js ~20KB (MIT)
- **server_change**: NO

### B — Pre-thinned full-page snap layer  (axis: When=once-after-page-load · Source=raster full-page pre-thinned)

หลัง page image โหลด, down-sample 1/4 → binarise → Zhang-Suen ครั้งเดียว → skeleton-tracing-js แปลงเป็น polyline → spatial index ใหม่ `pageData.clSnaps`. snap call-site อ่าน `clSnaps` ผ่าน `userSnapPoints()`-style append (pattern เดียวกับ user-snap points ที่มีอยู่). SNAP_COLORS เพิ่ม type "cl".

- **area_math**: unchanged
- **user_gesture**: เหมือนเดิม + snap indicator แสดง "CL" badge
- **data_delta**: `pageData.clSnaps` (runtime only, ไม่ save .bmaplan, recompute on load)
- **forbidden_touch**: NO — เพิ่ม field + เพิ่ม candidate array, ไม่แก้ `buildSnapIndex` / `snap` internals
- **lib**: skeletonization-js ~20KB + skeleton-tracing ~30KB = ~50KB (≥30KB cap; แต่ละตัวยังต่ำกว่า)
- **one_time_cost**: 200–500ms ตอนโหลด (Web Worker → postMessage)
- **server_change**: NO

### C — Post-draw correction dialog  (axis: When=after-drawing · UX=diff overlay before commit)

วาดปกติ → กด Enter/close → modal: "เส้นมี stroke ~N px, ปรับเป็นกลางไหม?" → [ดูก่อน] overlay สีต่าง (เก่าแดง/ใหม่เขียว) → [ยืนยัน]/[ยกเลิก]. Correction: ทุก edge sample 20×20 ROI ที่ midpoint → Zhang-Suen → estimate stroke direction → offset vertex ตาม edge normal เข้ากลาง. ~50ms ต่อ polygon 10-vertex (sync).

- **area_math**: unchanged
- **user_gesture**: วาดปกติ + 1 dialog opt-in
- **data_delta**: `poly.centerlineSource="roi-post"` + `poly.originalPts` (audit backup, optional)
- **forbidden_touch**: NO — fire ใน `finishCurrentArea()` ก่อน `pushUndo()`+`mPolys.push()`
- **lib**: skeletonization-js ~20KB
- **server_change**: NO

### D — Per-vertex Tab toggle outer/center/inner  (axis: UX=explicit toggle · Integration=per-vertex modifier)

status bar แสดง `[⬜ outer][▪ center][⬛ inner]`. Tab cycle ก่อนแต่ละคลิก. แต่ละ vertex บันทึก raw position + chosen mode. หลัง polygon ปิด: outer→shift inward w/2, center→none, inner→shift outward w/2 (w estimate จาก brightness gradient 1D scanline ไม่ใช้ lib).

- **area_math**: unchanged
- **user_gesture**: Tab ก่อนคลิก — power-user, mental load สูงกับ polygon หลายมุม
- **data_delta**: `poly.vertexModes=["outer","center",...]` (additive); `poly.strokeWidthPx` (estimate)
- **forbidden_touch**: NO
- **lib**: ไม่มี (estimator ทำเอง)
- **server_change**: NO

### E — Vector stroke-width server field + client offset  (axis: Source=vector stroke-width · Integration=new server field)

server.py `extract_snaps_typed()` อ่าน stroke-width จาก PyMuPDF `page.get_drawings()['width']` → response เพิ่ม field ใหม่ `strokeWidths:[{lineIdx,w_pt}]`. client: เมื่อ "nl" snap match ได้ stroke-width → snap indicator แสดง "CL" badge → กด C accept centerline shift = w_pt/2 perpendicular.

- **area_math**: unchanged
- **user_gesture**: snap ปกติ + กด C ถ้าอยากเข้ากลาง
- **data_delta**: `pageData.strokeWidths` (runtime, additive)
- **forbidden_touch**: PARTIAL — server.py extraction response **additive field ใหม่** (frame อนุญาตชัด); snap internals ไม่แก้
- **lib**: ไม่มี (PyMuPDF มี width อยู่แล้ว)
- **server_change**: YES (additive only)

> ทุก approach ไม่แตะ `polyAreaM2` / `polyMetrics` / `polySelfIntersects` / `pdfToC` / `cToPdf` / `RS` / snap internals. ทุก approach อยู่ในกรอบ Phase-1.

## Score

| approach | novelty | accuracy | UX | model-fit | boundary | cost | total |
|---|---|---|---|---|---|---|---|
| **A click-ROI skeletonize** | 4 | 4 | 5 | 5 | 5 | 4 | **27** |
| B pre-thinned page | 3 | 4 | 4 | 4 | 5 | 2 | 22 |
| C post-draw dialog | 4 | 4 | 4 | 5 | 5 | 4 | **26** |
| D per-vertex Tab | 5 | 3 | 3 | 4 | 5 | 3 | 23 |
| E vector stroke field | 2 | 2 | 3 | 4 | 5 | 3 | 19 |

**ประเด็นสำคัญ:**
- A vs C ห่างกัน 1 แต้ม — A ชนะที่ UX silent (zero new gesture), C ชนะที่ transparency (ผู้ใช้เห็น before/after).
- A accuracy=4: 100×100 ROI ครอบ stroke 6px ได้สบาย; risk เดียวคือ ROI ตกใน gap ของ dash → fix ขยายเป็น 140×140.
- B cost=2: ต้อง Web Worker + 2 lib + spatial index — งานหนัก แต่ snap UX ดีที่สุด (live highlight).
- D accuracy=3: brightness-gradient estimator ผิดได้ ±1-2px = ±17% บน stroke 6px → ไม่การันตี ±0.5%.
- E accuracy=2 ตามกฎ: raster เป็นเคสหลัก, vector-only โดน penalty.

**Phase-5 verify:** อันดับ 1 (A) `forbidden_surface_touch: NO`, ไม่ข้าม Phase-1 boundary → ผ่าน ไม่ต้อง re-rank.

## Recommendation

**Spike A ก่อน** (click-time local-ROI skeletonize). คะแนนรวมสูงสุด (27/30). Zero new gesture — ผู้ใช้วาดเหมือนเดิม, correction ทำเงียบๆ. Model-fit สะอาด (ฉีด corrected coord หลัง `cToPdf` ก่อน `mPts.push`; ไม่แตะ forbidden surfaces). Frame budget 16ms ผ่าน (100×100 ROI, Zhang-Suen ~8–12ms ตาม research). lib เดียว ~20KB. ±0.5% spike criterion ทำได้ถ้า tune ROI = 140×140 กัน dash-gap crop.

**Fallback: C (post-draw correction dialog)** — accuracy floor เท่ากับ A, lib เดียวกัน, cost band เดียวกัน, ไม่มี live-frame pressure. ชนะที่ transparency — ผู้ใช้เห็น overlay before/after แล้วตัดสินใจ. ใช้ C ถ้า A เจอเคส faded scan / low contrast ที่ Otsu misfire ทำให้ correction ผิดทาง.

## Spike

**Approach attempted:** A (click-time local-ROI Zhang-Suen).
**File:** `proto/sandbox/invent-centerline-snap-dashed-boundary.html` — standalone, no server/build/CDN. เปิดในเบราว์เซอร์ได้เลย; `?auto=1` รัน test ทันที.
**Verifier:** `artifacts/invent/centerline-snap-dashed-boundary/verify_spike.py` (Playwright headless).
**Test:** dashed pentagon, stroke=6px, dash=[12,8], 5 vertices. โปรแกรม trace polygon "outer / center / inner" (offset ±half-stroke ตาม bisector) แล้ว run correction.

**Outcome: PASS 4/4** (3 passes ในการ tune):

| pass | algorithm | max |Δ\| corrected | cost/vertex | result |
|---|---|---:|---:|---|
| 1 | per-click ROI → nearest-skeleton-pixel | 1.284% | 4.0ms | **FAIL #2** — inner trace ตกขอบ |
| 2 | + dilate ×4 ก่อน thin (close 8-px gaps) | **1.799%** | 6.8ms | **FAIL #2** — dilation ทำให้แย่ลง: รวบมุม |
| 3 | step1 + post-draw per-edge PCA + corner intersect | **0.185%** | 9.9ms | **PASS 4/4** ✓ |

**Pass-3 final report:**
```
outer raw = 149234 px² (Δ +3.10%)   → corrected 145017 (Δ +0.185%)
center raw = 144750 px² (Δ +0.00%)  → corrected 144741 (Δ -0.007%)
inner raw = 140333 px² (Δ -3.05%)   → corrected 144529 (Δ -0.153%)
max |Δ| corrected = 0.185% (target ≤0.5%) ✓
max avg per-click cost = 9.90 ms (target ≤16ms) ✓
all 15 vertices snapped (5+5+5) ✓
```

Screenshot: `artifacts/invent/centerline-snap-dashed-boundary/spike-A.png`
Report: `artifacts/invent/centerline-snap-dashed-boundary/spike-A-report.json`

**Findings (สำคัญสำหรับ sprint จริง):**

1. **per-vertex ROI snap อย่างเดียวไม่พอ** — มี systematic "corner-chamfering" bias เพราะ inner-corner-vertex อยู่ในมุม → nearest-skeleton-pixel = edge ที่ใกล้สุด (ไม่ใช่ corner) → polygon เล็กกว่าจริง. error ~1.3% บน pentagon stroke 6px dash [12,8].

2. **dilation-before-thinning คือทางผิด** — pass 2 พิสูจน์ว่า dilation รวบมุม → corner inset → ผลแย่กว่าเดิม (1.80%). อย่าใช้.

3. **ทางที่ใช่ = 2-step hybrid:**
   - **Step 1 (cheap, ~4ms/vertex):** per-click ROI snap. ใช้ระหว่างวาด (live preview, ไม่หน่วง mousemove).
   - **Step 2 (post-draw, ~6ms/vertex extra):** per-edge sample 5 จุด → snap แต่ละจุด → PCA หา principal direction ของ edge → intersect adjacent edges' lines = true corner. รันครั้งเดียวก่อน commit. แก้ corner bias สนิท.

4. **Threshold + binarisation** ใช้แบบ fixed (sum RGB < 384) — ทำงานบน synthetic test ขาวล้วน + เส้นดำล้วน. **บน real raster ที่มี gray / noise** ต้องสลับเป็น Otsu (ทำเองได้ ~20 บรรทัด) หรือ adaptive threshold. **ยังไม่ทดสอบ** บน real cadastral scan.

5. **ROI 140×140 เพียงพอ** — capture dash pattern ได้ครบแม้ stroke + gap + corner. ไม่มี case "no foreground found" บน test pattern.

6. **Closed-form scaling:** ที่ pass-3 ตัวเลขโน้มไปทาง +0.18% สำหรับ outer และ -0.15% สำหรับ inner — bias ยังมีนิดหน่อย, น่าจะ inherent ใน PCA fit เมื่อ samples ไม่กระจายสม่ำเสมอตาม edge. แก้ได้ด้วย weighted PCA หรือ RANSAC ในการ sprint จริง ถ้าจะลดจาก ±0.2% → ±0.05%.

**Scope confirmation:** ไม่แตะ `polyAreaM2` / `pdfToC` / `cToPdf` / `RS` / `snap()` internals. ใช้ `getImageData` (อยู่ใน canvas API ปกติ) + เพิ่ม Zhang-Suen + PCA inline (~150 บรรทัด net). lib เดียวที่ต้องใช้คือ skeletonization-js (~20KB) ใน sprint จริง (spike inline เพื่อ verifiability) — หรือ inline implementation ถ้าอยากปลอด CDN.

**ความเสี่ยงเหลือ (สำหรับ sprint discussion):**
- **เคส real raster** ที่ contrast ต่ำ / scan ไม่สะอาด / dash หลายสี: ยังไม่ทดสอบ (synthetic เท่านั้น)
- **Sharp corner < 60°:** PCA fit จาก 5 samples อาจ unstable ถ้า edge สั้นมาก → ต้องลด NSAMPLE หรือ fall-back to step-1-only
- **Self-intersecting / very concave polygon:** ROI อาจครอบหลาย edge cluster — algorithm จะหา nearest, อาจกระโดดข้าม → ต้องเพิ่ม connected-component filter หรือ "previous-vertex direction hint"
- **Vector PDF route ยังไม่มีเลย** — ถ้า GO ต้องเพิ่มแยก (Approach E hook กับ extract_snaps response)

## Decision

**GO — split into 2 sprints (proto + lite), human checkpoint 2026-05-24.**

Spike PASS 4/4 (pass 3 of 3 tuning iterations). max |Δ| corrected = 0.185% (เป้า ≤0.5%), max cost = 9.9ms/vertex (เป้า ≤16ms), 15/15 vertices snapped. Algorithm = **2-step hybrid** (per-click ROI snap step 1 + post-draw per-edge PCA + corner intersection step 2). User signed off: "ดูละ ทำลง lite ด้วย" — implement in both proto and lite.

**Sprint split rationale.** proto และ lite มี measure-engine แยกกัน (lite vendored from proto + drift-locked). Centerline-snap algorithm เป็น helper ใหม่ (~150 LOC, ไม่ใช่ measure-math edit) → ship เป็น JS helper file ที่ทั้งสองฝั่ง include ได้:
- **`INV-2026-05-24-002a`** (proto): ship helper + hook ใน area-tool click. Forbidden-surface check ครบ (ไม่แตะ polyAreaM2 / pdfToC / cToPdf / RS / snap internals).
- **`INV-2026-05-24-002b`** (lite): depend-on 002a. Vendor helper เข้า `lite/static/js/` + hook ใน lite area-tool click. Same algorithm, same toggle, same marker pattern. ตรงกับ lite-vendoring contract (math source-of-truth = proto; lite วันที่เปลี่ยน = proto's commit).

**Acceptance criteria carried forward to sprint:**
1. NEW `proto/static/js/centerline-snap.js` (~150 LOC) — exports `snapCenterlineROI(ctx, cx, cy, opts)` (step 1) + `refineCornersOnSkeleton(ctx, pts, opts)` (step 2). Inline Zhang-Suen (~50 LOC) — no CDN dependency.
2. Hook in area-tool click handler in `proto/ui.html` — guarded by user toggle (Helpers ribbon, sibling ของ Loupe/Ortho/Perp/Snap-off จาก HT-13a).
3. Schema additive: optional `obj.traceMode` field (`"centerline-roi"`); save/load round-trip; absence = legacy raw click.
4. Live mode = step 1 only (per mousemove if toggle ON). Commit = step 1 + step 2 (post-Enter, before `pushUndo()`).
5. Marker `PHASE_CENTERLINE_SNAP_OK` ≥ 8 sub-checks: lib loaded, fn exists, ROI snap correct, refine correct, schema additive, toggle persists, no PATH_GEOMETRY_OK / ARC_POLYGON_OK regression, threshold = adaptive (Otsu) ผ่าน synthetic + 1 real raster sample.
6. Lite mirror: `lite/static/js/centerline-snap.js` + hook in `lite/ui-lite.html`. Same algorithm, marker `LITE_CENTERLINE_SNAP_OK`.

**Open follow-ups (NOT this sprint):**
- **Vector PDF route (Approach E)** — extract stroke-width จาก `extract_snaps_typed()` + client offset shift. แยก sprint หลัง 002a/b ship; ไม่ block แต่ enhance vector PDF case.
- **Real-raster threshold robustness** — sprint นี้ใช้ Otsu; ถ้าเจอ scan ที่ contrast เพี้ยน อาจต้องเสริม adaptive threshold (Sauvola/Niblack) ในรุ่นถัดไป.
- **Sharp corner < 60°** — สำรองด้วย step-1-only fallback ถ้า PCA fit unstable.

**ส่วนที่ทิ้งไว้พร้อม revive:** artifact + sandbox + verifier + JSON report เก็บไว้ครบ. Approach C (post-draw correction dialog) เป็น fallback ถ้า user ไม่ชอบ live-silent behavior — รหัส step 2 ใน sprint นี้ใช้ได้ทันที (เปิด modal แทน auto-commit).
