# Invent: lite-pdf-render-quality

- **idea_id**: `2026-05-27-23-05`
- **Status**: invent-in-progress
- **Started**: 2026-05-27
- **Raw idea (verbatim)**: "`engin`ใน lite  เปิด  pdf เเปิดได้ไม่ชัดเท่า   foxie pdf ทำไงให้ มีคุณภาพเท่ากัน"
- **Tags**: bma-plan, lite, render, pdf, perf, p-med

## Frame

**Problem.** When the user opens a PDF in lite, rendered pages look noticeably less sharp than the same PDF in Foxit Reader — visible especially on architectural line art (thin walls, dim/text labels). When the user zooms in past ~150% the image gets blurry; Foxit stays crisp at the same zoom level.

**Root causes (from research).** Three compounding factors:
1. Backend pre-renders **once at `RS=1.5`** then frontend upscales via `ctx.scale(V.k)` → bilinear blur for any `V.k > 1.5/1.0` device-pixel ratio.
2. JPEG at `q=88` introduces minor ringing on hard line-art edges (worse than visually-lossless q=95+ or PNG).
3. Frontend never multiplies render scale by `devicePixelRatio` → on retina (DPR=2) we display 1.5× source onto 2× device pixels = effectively 0.75× per device pixel.

Foxit avoids this by **re-rendering from the PDF on every zoom** (native engine, GPU-accelerated); Bluebeam uses **Iterative Draw** (low-res preview during interaction → full-res on idle).

**Constraints (must NOT violate).**
- `RS = 1.5` constant in `lite/ui-lite.html` is **immutable** — proven to break setback math (sprint 2026-05-11, reverted). Used by `pdfToC` / `cToPdf` / `ptToScreen` / `screenToPt` / hit-test / snap.
- `polyAreaM2`, `polyMetrics`, `pdfToC`, `cToPdf` cannot be edited.
- `.bmaplan` schema must stay additive-only.
- Memory: prior `RUN_PROGRESSIVE_PREVIEW_AND_BACKGROUND_FULL_RENDER` proto sprint hit `malloc failed 27MB` from rendering 2× concurrently with thumbnails → **never render two scales of the same page in parallel**.
- Phase 1 boundary: no AI, no OCR, no legal verdict.
- `[BMA_PAGE_RENDER_PERF]` log shows JPEG encode = 93% of render time → encode-time is the perf bottleneck, not pixmap generation.

**Forbidden surfaces this idea must avoid (explicit list).**
- `RS` constant in `ui-lite.html`
- `ptToScreen` / `screenToPt` (the `*RS` / `/RS` factors)
- `tracePoly` and hit-test geometry
- `pdfToC` / `cToPdf` / `polyAreaM2` (proto, by reference — lite inherits the contract)
- Concurrent render of the same page at multiple scales (memory anti-pattern)
- `.bmaplan` schema fields

**Success criteria (how the spike proves it).**
The spike must show, on a real architectural permit PDF (the 45-page RAMA4 file at repo root):
- At `V.k = 1.0` (fit-to-screen) and `V.k = 2.0` (zoom-in 2×), the rendered raster looks visually as sharp as Foxit on the same page at the same zoom.
- Total memory per case stays bounded (no `malloc failed` from concurrent high-res renders).
- Coord math unchanged: a 4 m² rectangle drawn in the spike measures 4.00 m² (±0.01) at any render scale.
- JPEG encode time at `?scale=3.0` ≤ 4× JPEG encode time at `?scale=1.5` (acceptable proportionality; not exponential).

**Out of scope (this invention pass).**
- Vector-side re-rendering via PDF.js / mupdf-wasm — rules out the entire current architecture; tracked separately if user wants it later.
- Print / export PDF quality (`/export-pdf-overlay`) — already covered by `docs/invent/print-canvas-per-page.md`.
- Tile-based rendering (PlanGrid pattern) — over-engineered for a single-file inline-JS app.
- User-facing "render quality" preferences UI — invent the engine first; settings UI is a follow-up sprint.
- Proto parity — this invent is scoped to **lite** only. If GO, proto can copy it later.

## Research

### 1. In-repo prior art

- **`docs/status/RENDER_SCALE_REDUCE_AND_CACHE.md`** (2026-05-11) — Attempted to reduce default render scale from 1.5 → 1.2 to speed load times, but **reverted immediately** due to coordinate-math regression in setback distance calculations. Key finding: `RS=1.5` is baked into `pdfToC`/`cToPdf` and cannot be changed without refactoring all measurement geometry. Lesson: "To reduce render time without touching RS: reduce `jpg_quality` (88 → 70), increase cache hits, or investigate progressive JPEG."
- **`docs/status/PROGRESSIVE_PREVIEW_AND_BACKGROUND_FULL_RENDER.md`** (2026-05-11) — Spiked progressive rendering (preview JPEG q=50, then full q=75 in background). **BLOCKED**: Render 2× concurrently + thumbnails exhausted server memory (`malloc failed 27MB`). Real bottleneck was concurrent render contention, not encode quality. Verdict: "Server queue / concurrency architecture required before attempting progressive render."
- **`docs/invent/print-canvas-per-page.md`** (2026-05-19) — Print-output focused; notes the fuzzy issue but solves a different problem.
- **`lite/server_lite.py:130–158`** — Current: `RS=1.5` immutable. `/page/{n}` accepts `?scale=` 0.2–4.0 (defaults RS). `pix.tobytes("jpeg", jpg_quality=88)` main, q=80 thumbs. Cache key `(page, n, rs, rot)` — scale already decoupled in cache.
- **`lite/ui-lite.html:256–289, 405–411`** — Frontend uses `RS` in coord math; fetches `/page/{n}` **without `?scale=`** (always default 1.5); draws via `ctx.drawImage(curImg,0,0)` + `ctx.scale(V.k)` → bilinear blur on zoom.
- **No prior work** on quality perception (blurriness vs Foxit) in design docs or invent/ directory.

### 2. Library scan — verdict: nothing fits the architecture

| lib | claim | status | note |
|---|---|---|---|
| **PDF.js** (Mozilla) | full JS PDF viewer | viable but risky | MIT, ~360KB gz. Would bypass PyMuPDF entirely; incompatible with .bmaplan geometry (PDF-pt). High coord-math divergence. |
| **pdfium-wasm** | Chromium renderer in WASM | viable but immature | Apache 2.0. ~2–3 MB WASM. Same coord-math risk. |
| **mupdf-wasm** | same MuPDF engine in browser | viable but complex | BSD. Identical output to server-side (same engine) = no quality gain, just moves CPU load to client. |
| **paper.js / flatten-js / Kanvas** | — | wrong-shape | not PDF renderers. |

**Conclusion**: No CDN library improves render quality **within the current architecture** (PyMuPDF server → JPEG → canvas).

### 3. Incumbents — how Foxit / Bluebeam / Acrobat actually do it

- **Foxit Reader / PhantomPDF** — proprietary native engine, re-renders vector PDFs from source on every zoom (GPU-accel). Raster PDFs prescale once then upscale on zoom. No JPEG cache.
- **Adobe Acrobat** — same pattern as Foxit; "Enhance Scans" option applies sharpening to raster PDFs post-render.
- **Bluebeam Revu** — **Iterative Draw** (key pattern): renders low-res preview during pan/zoom interaction → full-res on idle. "Render Preview When Panning" toggle. Hardware (GPU) rendering optional. Never caches fixed-resolution then upscales.
- **QGIS / PlanGrid** — tile-based lazy-load (Maps pattern); not applicable to single-file inline-JS app.

**Key pattern incumbents converge on**: re-render on zoom from source (vector) OR re-render on idle (raster). **None cache a fixed-resolution JPEG then upscale on zoom** — exactly the pattern that produces lite's visible blur.

### 4. Algorithm / format tuning knobs

- **`devicePixelRatio`** — lite's canvas backing store is DPR-scaled already, but source image is not → on retina, effective resolution = `1.5 / DPR = 0.75`. Multiplying request scale by DPR gives `1.5 * DPR` source pixels per CSS px (no upscale needed).
- **Bilinear vs Lanczos resampling** — browser canvas uses bilinear by default for upscale. For line art, Lanczos > bilinear. Toggleable via `ctx.imageSmoothingQuality = 'high'` (Chrome / Edge interpret as cubic-like).
- **JPEG q=88 vs q=95 vs PNG** — q=88 saves ~20% bytes vs q=95; q=95 nearly visually lossless. PNG lossless, ~2-3× larger for photographic but **smaller for line art** (compresses runs of solid color).
- **WebP lossless** — ~26% smaller than PNG, 96%+ browser support (2026). PyMuPDF can produce via PIL bridge.
- **Progressive JPEG** — `pix.tobytes("jpeg", jpg_quality=Q, progressive=True)` — same Q, ~15-20% smaller, slightly slower decode.
- **MuPDF AA flags** — already at max (`graphics=8, text=8`). No further knob.

### 5. Competitor zoom UX

- **Bluebeam** — iterative draw, low→high res on idle. No blur at max zoom.
- **Foxit** — re-renders vector on zoom (any zoom level sharp). Raster pixelates beyond 200%.
- **Acrobat** — GPU-accelerated smooth zoom, vector re-render.
- **PlanGrid** — tile lazy-load (web maps pattern).
- **Pain point**: the **static** raster quality before any zoom. Pre-rendering at 1.5× and never refreshing = the root cause; incumbents all sidestep by re-rendering on demand.

### Verdict: **PRIOR_ART_PARTIAL**

**Math is solved**: Bluebeam's iterative-draw pattern is mature (20+ years in production). **Library question is resolved**: no CDN lib fits; we keep PyMuPDF + JPEG/PNG/WebP. **What needs invention**: integration into lite — when to trigger high-res render, how to debounce zoom, how to swap `curImg` without flicker, how to keep memory bounded after the previous `malloc failed` incident. Diverge on **timing, scope, and cache policy**, not on algorithms.

## Diverge

### A — DPR-aware static base scale (axis: scope — retina-only fix)
Frontend computes `dpr = window.devicePixelRatio` once on load and appends `&scale=${RS*dpr}` to every `/page/{n}` request. On retina (DPR=2) backend renders at 3.0× instead of 1.5×. `drawImage` is called with explicit `dw = curImg.width / dpr` and `dh = curImg.height / dpr` so the image maps back to the same CSS-pixel footprint — `V.k` and all coord math untouched. Backend already accepts `?scale=` up to 4.0 and caches by key.
- LOC: backend 0, frontend ~8
- forbidden_surface_touch: NO
- memory: DPR=2 → 4× pixels per page; sequential render only (no parallel — respects malloc constraint)
- first-load latency: DPR=1 same; DPR=2 ~3-4× encode
- bmaplan compat: full
- risk: 45 pages × DPR=2 = 180 MB worst-case imgCache; needs eviction guard

### B — PNG/WebP-lossless for line-art (axis: format)
Backend gains `?fmt=png` (or auto-pick); `pix.tobytes("png")` eliminates JPEG ringing entirely. Cache key adds `fmt`. No render-scale change.
- LOC: backend ~12, frontend ~4
- forbidden_surface_touch: NO
- memory: PNG ~3-8 MB/page A1 vs JPEG ~200-400 KB (10-20× per page) — needs byte-based eviction
- first-load latency: PNG encode ~2-3× JPEG; localhost transfer trivial
- bmaplan compat: full
- risk: 45 × 5 MB = 225 MB worst-case without byte cap

### C — Zoom-triggered re-render on idle (axis: algorithmic, Bluebeam iterative draw)
Frontend loads RS=1.5 image immediately; on `zoomEnd` (200 ms debounce) fires `refreshHighRes()` requesting `?scale=V.k*RS*dpr` (capped at 4.0); on arrival swaps `curImg`. Sequential only.
- LOC: backend 0, frontend ~45
- forbidden_surface_touch: NO
- memory: ≤2 images/page, low-res evicted after high-res arrives
- first-load latency: same; sharpening appears 200 ms after zoom-settle
- bmaplan compat: full
- risk: `imgCache` shape change from `{n: img}` to `{n: {scale,img}}` — 3-4 call sites

### D — Viewport-crop re-render (axis: representation, sub-region LOD)
New `/pagecrop/{n}?x=&y=&w=&h=&scale=` endpoint renders only visible viewport via PyMuPDF `clip`. Frontend overlays crop on base image with exact offset.
- LOC: backend ~35, frontend ~60
- forbidden_surface_touch: NO (reads pdfToC indirectly to compute clip rect — read-only)
- memory: crop ~500 KB; minimal growth
- first-load latency: same; crop arrives 100-300 ms post zoom-settle
- bmaplan compat: full
- risk: pixel-perfect overlay alignment is the hardest part — off-by-one = visible seam

### E — WebP with quality-mode backend gate (axis: integration, backend-only format+quality)
Backend heuristic: grayscale channel → lossless WebP; else WebP q=90. PyMuPDF 1.24+ supports `pix.tobytes("webp", lossless=True)`. Frontend unchanged.
- LOC: backend ~18, frontend 0
- forbidden_surface_touch: NO
- memory: lossless WebP ≈ 2× JPEG for line-art; lossy ≈ same
- first-load latency: encode ~1.5× JPEG (lossy), 2-3× (lossless)
- bmaplan compat: full
- risk: grayscale heuristic crude — colour-mode scans of B&W permits go through lossy branch

## Score

| approach | novelty | accuracy | ux | model-fit | boundary | cost | total |
|---|---|---|---|---|---|---|---|
| **A** DPR-aware base | 2 | 4 | 5 | 5 | 5 | 5 | **26** |
| **B** PNG lossless | 2 | 5 | 5 | 4 | 5 | 4 | **25** |
| **C** zoom idle re-render | 4 | 5 | 4 | 3 | 5 | 3 | **24** |
| **D** viewport crop | 5 | 5 | 3 | 2 | 4 | 2 | **21** |
| **E** WebP quality gate | 3 | 3 | 5 | 5 | 5 | 4 | **25** |

Top approach A satisfies `forbidden_surface_touch: NO` and stays in Phase 1 scope. No re-rank required.

## Recommendation

**Top: A (DPR-aware static base scale).** Lowest line count (8 frontend, 0 backend), zero forbidden-surface risk, solves the biggest single complaint (retina blur) — and approach B's data shows it can be stacked on top in a future sprint for non-retina line-art sharpness. Spike A first.

**Fallback: B (PNG lossless).** If A spike shows insufficient gain on DPR=1 (non-retina) machines where JPEG ringing dominates over upscale-blur, swap to PNG. ~16 LOC total. Memory cap mitigated by tightening `MAX_IMAGE_CACHE` to byte-based.

## Spike

### Setup
- Artifact files: `lite/sandbox/invent-lite-pdf-render-quality.html` (visual viewer) + `lite/sandbox/invent-lite-pdf-render-quality/render_variants.py` (renderer) + 5 pre-rendered variants + `stats.json`
- Test PDFs: TWO of them, intentionally different in content profile (the cross-PDF behaviour matters)

### Test PDF #1 — `20250616 RAMA4 APARTMENT PERMIT rev 1.pdf` page 3
2384×1684 pt landscape, rotation=90°, dense floor plan, thin walls + dimension text (worst case for JPEG line-art ringing).

| variant | pixmap | bytes | encode_ms | vs baseline |
|---|---|---|---|---|
| current (RS=1.5 JPEG q=88) | 3576×2526 | 1067.6 KB | 303 ms | 1.00× / 1.00× |
| A (scale=3.0 JPEG q=88) | 7152×5052 | 2900.9 KB | 1101 ms | 2.72× / 3.63× |
| B (RS=1.5 PNG) | 3576×2526 | 1004.7 KB | 215 ms | **0.94× / 0.71×** |
| A+B (scale=3.0 PNG) | 7152×5052 | 2413.1 KB | 739 ms | 2.26× / 2.44× |
| scale=3.0 JPEG q=95 | 7152×5052 | 3522.8 KB | 1078 ms | 3.30× / 3.56× |

### Test PDF #2 — `/Users/nucifer/Downloads/ผัง.pdf` (user-supplied, 2026-05-27)
1191×842 pt A3 landscape, rotation=0°, ONE page. Lighter line-art + coloured fills (different content profile).

| variant | pixmap | bytes | encode_ms | vs baseline |
|---|---|---|---|---|
| current (RS=1.5 JPEG q=88) | 1787×1263 | 296.5 KB | 105 ms | 1.00× / 1.00× |
| A (scale=3.0 JPEG q=88) | 3573×2526 | 918.9 KB | 366 ms | 3.10× / 3.49× |
| B (RS=1.5 PNG) | 1787×1263 | 1778.8 KB | 195 ms | **6.00× / 1.86×** |
| A+B (scale=3.0 PNG) | 3573×2526 | 4220.3 KB | 467 ms | 14.23× / 4.45× ⚠ |
| scale=3.0 JPEG q=95 | 3573×2526 | 1520.1 KB | 415 ms | 5.13× / 3.95× |

### Cross-PDF observation (key insight — reverses the original "surprise")

| metric | PDF #1 (RAMA4 permit) | PDF #2 (ผัง.pdf) | takeaway |
|---|---|---|---|
| PNG vs JPEG bytes at RS=1.5 | PNG 0.94× JPEG | PNG 6.00× JPEG | **PNG size depends heavily on content profile** — wins on sparse line-art, loses on coloured-fill pages |
| PNG vs JPEG encode at RS=1.5 | PNG 0.71× JPEG | PNG 1.86× JPEG (vs baseline JPEG); but PNG 1.86× vs JPEG 1.00× = PNG STILL faster encode in absolute ms (195 < 105? NO — 195>105). Wait: 195 ms PNG, 105 ms JPEG → PNG is **slower** here in absolute ms. The PDF #1 PNG-faster result was specific to high-resolution dense pages where JPEG DCT dominates. | Encode-time advantage of PNG is content-dependent too |
| SC-4 (encode ≤4× baseline) for **A** | 3.63× PASS | 3.49× PASS | A is **safely within budget on both PDFs** |
| SC-4 (encode ≤4× baseline) for **A+B** | 2.44× PASS | 4.45× ⚠ marginal | A+B can EXCEED budget on smaller PDFs |

### Success criteria results

- **SC-1 (visual sharpness vs Foxit):** REQUIRES HUMAN EYEBALL — open `lite/sandbox/invent-lite-pdf-render-quality.html` and click V.k=2.0 and V.k=4.0. Compare each cell against Foxit showing the same page at the same zoom.
- **SC-2 (memory bounded):** PASS on both PDFs — single-render, no concurrent dual-scale. PDF #1 worst-case A+B = 2.41 MB × 24-cache = 58 MB per case. PDF #2 worst-case A+B = 4.22 MB × 24-cache = 101 MB per case — still well within the malloc-failed threshold (which required *concurrent* renders, not just sequential cache).
- **SC-3 (coord math invariant):** PASS by construction on both PDFs — Approach A scales source image to `(CSS_W * V.k, CSS_H * V.k)` in `drawImage`. World→CSS mapping is independent of srcScale. The HTML coord-check section verifies all 5 variants produce identical CSS-px per meter.
- **SC-4 (encode ≤ 4× baseline):** A PASSES on both PDFs (3.63× and 3.49×). **A+B FAILS on PDF #2 (4.45×)** — combined approach exceeds budget on smaller/coloured PDFs. Pure A is the safer GO target.

### Revised recommendation (after cross-PDF data)

The earlier "PNG is universally smaller AND faster" claim was overfitted to PDF #1. On PDF #2 (more typical A3 plan size with coloured fills), PNG is **6× bigger and 1.86× slower** than JPEG, and A+B violates SC-4. **A alone (scale=RS×DPR, JPEG q=88) is the only approach that passes SC-4 on both PDFs tested.** Recommend GO for **A as the sprint target**, treat B/PNG as a deferred follow-up to revisit only after measuring on a representative sample of customer PDFs.

### Spike verdict (v1 — Approach A)

**APPROACH A SPIKE PASS** on both PDFs tested. Visual sharpness at V.k=2.0 / V.k=4.0 to be confirmed by human eyeball at checkpoint. All numeric criteria for A PASS. No forbidden-surface edits. No `.bmaplan` schema impact. A+B/PNG demoted to future sprint pending more PDF samples.

### Spike v2 — Approach G (PDF.js client-side) — added after user reframed the concept

**Trigger.** At the v1 checkpoint the user reframed the goal: "Concept: open the same PDF in Chrome, zoom 500% — still sharp." That is server-side fixed-resolution raster (the basis of A/B/F) inherently CANNOT achieve, because no single pre-rendered raster stays crisp at 500% zoom. The only approaches that fit this concept are **C (zoom-triggered server re-render)** and **G (PDF.js client-side, re-rasterize from vector at requested zoom)**. A focused follow-up research pass confirmed PDF.js is the recommended path (verdict `SPIKE_PDFJS_NOW`); PDFium-WASM is conceptually closer to Chrome but bundle size unverified and ecosystem fragmented.

**Spike artifact.** `lite/sandbox/invent-lite-pdf-render-quality-pdfjs.html`.

**What it tests.**
- Loads PDF.js 4.0.379 from jsDelivr CDN (file:// compatible because CDN serves CORS-permissive)
- User picks PDF via file input — any PDF works (e.g., `/Users/nucifer/Downloads/ผัง.pdf` or the RAMA4 permit)
- Render at zoom 1×, 2×, 5×, 10× via `getViewport({scale: RS * V.k})`
- Rotation 0°, 90°, 180°, 270° via `getViewport({rotation})`
- DPR-correct sizing: canvas attr = `viewport.width * dpr` device-pixels, canvas style = `viewport.width` CSS-pixels — single DPR application, no double-apply
- Stale-paint filter: monotonic `renderTaskId` + `RenderingCancelledException` handler. Status sidebar shows count of stale tasks dropped (the user can rapid-click zoom buttons to provoke them)

**Measurement-contract probe.**
A 100pt × 100pt PDF-pt rectangle anchored at `(100, 100)`-`(200, 200)` is drawn on a separate overlay canvas via `viewport.convertToViewportPoint()`. At every zoom and rotation the spike asserts:
- expected canvas-CSS diagonal = `100 × √2 × RS × V.k`
- measured diagonal must be within 0.5 CSS-px
- side panel reports PASS / FAIL with the exact delta

This is the analogue of lite's `ptToScreen` contract. If this PASSES at all zoom + rotation combos, the renderer swap to PDF.js does NOT break the measurement math.

**What the human verifies (the actual GO criterion).**
1. Visual sharpness — open ผัง.pdf in BOTH the spike (Chrome at file://) AND Chrome's built-in PDF viewer (separate window) at zoom 5×. Are they comparably sharp? Same at 10×?
2. Contract PASS at all 16 combos: zoom (1/2/5/10) × rotation (0/90/180/270). Side panel must show ✓ at every combo.
3. Rapid-zoom test: click 1× → 5× → 1× → 10× → 1× quickly. The "stale dropped" counter should rise (indicating PDF.js is correctly cancelling in-flight renders). The displayed result must always match the last button clicked, never a stale older one.

**If all three pass → recommend GO** with a `LITE-PDFJS-SWITCH` sprint card to migrate `lite/ui-lite.html` display layer to PDF.js. Estimated ~120 LOC frontend, 0 backend, measurement code untouched. PyMuPDF retained server-side for export.

## Decision

**PAUSED 2026-05-28** — spike v3 PASS, GO not yet given. User said "เก็บไว้ทำต่อ" — keep WIP, resume later.

### State at pause

- Spike artifacts (3 HTML + render_variants.py + drive scripts + screenshots + stats) all **uncommitted** in `lite/sandbox/invent-lite-pdf-render-quality*` — keep them, this is the evidence of GO
- Sprint #1 (PDFJS-PREP-EXTRACT-RENDERER) **WIP uncommitted**:
  - `lite/ui-lite.html` modified: 1195 → 1100 (95 lines extracted out)
  - `lite/static/js/page-renderer.js` new (98 lines, owns imgCache / curImg / pageRot / loadPage / fit / resize / drawImage)
  - `lite/static/js/export-annotate.js` new (87 lines, owns exportXlsx / exportPdfOverlay / openReport)
  - `py_compile` PASS, forbidden surfaces verified intact, function bodies byte-identical
  - **Not yet committed** — user paused before commit
- Sprint #2 (PDFJS-VIEWPORT-CLIPPED-INTEGRATION) **not started** — design captured in this artifact, ~250 LOC estimated, would land in page-renderer.js

### Pre-existing housekeeping debt blocking resume

`lite/tests/test_pf_kind_folders.py` (and likely other Playwright tests) FAIL with `arcHUDText is not defined` because:
- `lite/static/js/draw-arc.js` deleted from disk (git status: `D`)
- but `ui-lite.html:221` still has `<script src="static/js/draw-arc.js"></script>` reference

5-line fix in ui-lite.html — not part of this invent, but blocks Sprint #2 regression testing. **Fix this before resuming Sprint #2.**

### How to resume

1. `git status` — confirm uncommitted changes still present (slice 1 + spike artifacts)
2. Run `lite/tests/test_pf_kind_folders.py` once to confirm slice 1 didn't break anything beyond the pre-existing arcHUDText issue
3. If slice 1 still clean → commit `feat(lite): PDFJS-PREP-EXTRACT-RENDERER — extract page-renderer + export-annotate from ui-lite.html`
4. Then: fix arcHUDText debt (separate small commit)
5. Then: invoke `/bma-lite-dev` again for Sprint #2 (PDFJS-VIEWPORT-CLIPPED-INTEGRATION) — spec lives in this artifact's Spike v2 section + the spike code in `lite/sandbox/invent-lite-pdf-render-quality-pdfjs-v3.html` is the reference implementation

### Why not committed yet

User chose to pause after seeing the slice-1 review. Likely revisiting whether the 2-sprint plan is the right order (e.g. fix arcHUDText first? do a different feature first? validate v3 spike in own browser before committing the refactor groundwork?).
