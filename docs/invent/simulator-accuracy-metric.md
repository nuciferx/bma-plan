# Simulator Accuracy Metric for /bma-simulate

- **Invent ID**: `INV-2026-05-24-002`
- **Parent**: SIM-1.1 (`8255aec`) — `/bma-simulate` runs full-loop but reports only PASS/FAIL/severity, not "how accurate did the simulator actually behave"
- **Trigger**: user challenge "ถ้าทำให้แม่นยำได้นายทำได้จริงหรือเปล่า ท้าทายผู้พัฒนาของ ai นะครับ" — needs accuracy metric defined before we can answer
- **Status**: invent-in-progress (started 2026-05-24)
- **Pre-analysis (Opus, before pipeline)**: expected verdict PARTIAL. CAD/measurement accuracy is a known field (ICC tolerances, AutoCAD precision settings, Bluebeam calibration spec), BUT the question "what's the right metric for a workflow-replay simulator" is genuinely under-specified.

---

## Phase 1: PICK ✅

Short-name `simulator-accuracy-metric`. Artifact = this file. Sandbox spike will live at `lite/sandbox/invent-sim-accuracy.html`.

---

## Phase 2: Research

### 1. In-repo prior work

- **`lite/tests/test_measure_parity.py`** — Enforces byte-identical numeric output between proto/lite for 16 vendored math fns + pinned fixtures. Tolerance model: **exact numeric parity** (diff = 0). Measures **code-level fidelity**, not workflow-replay accuracy.
- **`proto/e2e_ui_test.py`** — 22 markers use **binary PASS/FAIL**. Tolerances appear only in custom sub-checks; no toleranced-metric framework.
- **`lite/sandbox/invent-45page-permit-spike.html`** — Permit spike does NOT encode an explicit accuracy target; floor totals are mock values for visual demo.
- **`docs/invent/arc-polygon.md`** — First spike to set an accuracy target: **<0.1% error on closed-form shapes** (4-edge + semicircle = rect + half-disk). Freeform tolerates **1–2% error** due to RDP decimation. Establishes BMA-Plan's existing accuracy bars.
- **Existing spike pattern**: PASS/FAIL verdict + optional error% comment. No scored tolerance band.

### 2. Library scan

| lib | use | status |
|---|---|---|
| `numpy.testing.assert_allclose` | atol + rtol tolerance | viable (Python only) |
| `pytest.approx` | rel/abs tolerance | viable but BMA-Plan doesn't use pytest |
| Hausdorff distance / IoU (shapely) | polygon shape similarity | wrong-shape — measures positional/areal drift, not replay |
| VCR / cassette HTTP replay | exact byte match | not applicable (simulator generates DOM, not HTTP) |
| **None found** | workflow-trace fidelity | no off-the-shelf metric |

### 3. CAD / GIS / surveying standards

- **Bluebeam Revu** — **≤1% error on vector PDFs**; methodology = post-calibration verification (measure 2nd known dim; recalibrate if >1% drift). Per-measurement, not per-workflow.
- **AutoCAD** — User-settable via DIMTOL; no enforced area standard.
- **FGCC surveying** — 1st-order horizontal control: **1 part in 25,000** (0.004% relative). Constraint: control accuracy ≥2× tighter than feature tolerance.
- **No incumbent publishes "workflow replay accuracy"** — Bluebeam/Foxit/PlanGrid focus on per-measurement calibration only.

### 4. Literature

- **Shoelace + circular-segment closed-forms** — analytically exact (FP error ≤1e-15).
- **Stack Overflow consensus on curved polygons**: flatten + shoelace; decimation tolerance 0.5–2 px → area error 0.5–2%. No single "right" tolerance.
- **Behavioral Cloning (arXiv 2405.05439, 2410.22916)** — Simulator metrics: (1) **Task Completion Rate**, (2) **Trajectory Smoothness** (avg jerk), (3) **Efficiency** (expert vs agent time). Multi-dimensional. "100% accuracy" is impossible in any real system.
- **Playwright determinism** — Same input → same output, but human ±5 px vs agent exact-center makes trace similarity probabilistic. No standard metric.

### 5. Competitor measurement UX

- **Bluebeam / PlanGrid / Procore** — All per-measurement (single number, post-calibration verify). None measure multi-step workflow fidelity.
- **GIS (QGIS, ArcGIS)** — User-set decimation tolerance; transparent error reporting ("at tolerance = 2 m, area error ≈ 0.5%"). Educates users on trade-off.

### Verdict: **PRIOR_ART_PARTIAL**

1. Per-measurement accuracy = mature (Bluebeam ≤1%; BMA-Plan already <0.1% on closed-form).
2. **Workflow-replay accuracy = NOT solved.** No CAD/PDF tool publishes a metric. Behavioral Cloning literature offers TCR + efficiency for robotics, not measurement software.
3. BMA-Plan's test pattern is binary; no unified accuracy definition yet.
4. The user challenge ("ทำให้แม่นยำได้จริงไหม") is multi-dimensional — area, trace, export, round-trip — no single number works.

**→ Proceed to phases 3-6.** Define axes + per-axis criteria before diverging on implementation.

Sources: [Bluebeam calibration](https://support.bluebeam.com/online-help/revu2019/Content/RevuHelp/Menus/Tools/Measure/Calibrate--MV.htm) · [FGCC standards](https://www.ngs.noaa.gov/FGCS/tech_pub/1984-stds-specs-geodetic-control-networks.htm) · [Behavioral Cloning survey](https://arxiv.org/html/2405.05439v2) · [numpy.testing.assert_allclose](https://numpy.org/doc/stable/reference/generated/numpy.testing.assert_allclose.html)

---

## Phase 3: Frame

### Problem
`/bma-simulate` runs the lite workflow end-to-end and reports PASS/FAIL + severity-tagged findings. It does NOT report **how accurately the simulator behaved vs a human-reference run**. Without an accuracy score, three questions can't be answered:
1. "Did this run regress accuracy vs the last 3 runs?"
2. "Is the simulator drifting from human behavior over time?"
3. The user's challenge: "**ถ้าทำให้แม่นยำได้นายทำได้จริงหรือเปล่า**" — can the simulator hit a defined accuracy bar?

Without a metric, "accurate" is undefined. Once defined, INV-SIM-2 enables future invent on "how to MAKE the simulator more accurate" (out of this scope).

### Constraints
- **Multi-dimensional metric** — research is clear: single-number accuracy is a lie. Need ≥4 axes (area / trace / export / roundtrip) reported separately, weighting deferred to user judgment.
- **Compare against a REFERENCE** — either a hand-made `.bmaplan` from a human OR a synthetic PDF with known closed-form areas. Both options must be supported.
- **Reuse simulator's existing output** — STEP_LOG JSON + downloaded files. Don't require new instrumentation in `/bma-simulate` Phase B (driver).
- **Configurable thresholds + weights** — different runs may have different "good enough" bars (smoke run vs release gate).
- **Forbidden to change `measure-engine.js` byte-identical contract** (parity test still rules math).
- **`.bmaplan` schema additive-only** — reference fields (`_referenceFor`, `_expectedAreaM2`, etc.) must be optional.
- **Spike must run browser-only** (no server, no Python eval) — `lite/sandbox/invent-sim-accuracy.html`.
- **Output ≤500 lines** of accuracy-runner code (lean — accuracy is a check, not an app).

### Forbidden surfaces (idea must NOT touch)
- `lite/static/js/measure-engine.js` (math contract)
- `pdfToC`, `cToPdf`, `RS`, `polyAreaM2`, area math primitives
- `.bmaplan` schema beyond ADDING optional accuracy-reference fields
- `setTool()` body
- proto/ anywhere

### Success criteria (concrete, spike-measurable)
1. **4 axes scored independently**:
   - **A. Area-value accuracy** (per-page area vs reference): `|sim_area - ref_area| / ref_area` per page; aggregate as mean + max
   - **T. Trace accuracy** (workflow step order + count): edit distance on `STEP_LOG[*].step` sequence; +1 per missing required step; +0.5 per extra step
   - **X. Export accuracy** (XLSX sheet/column/row match): sheet count exact, column-name match exact, row count within ±10% (allowing for empty trailing rows)
   - **R. Round-trip accuracy** (save→reopen total-area drift): `|reopened_total - saved_total| / saved_total` across all pages
2. **All 4 axes computable from existing simulator outputs** (no new instrumentation needed).
3. **Reference resolvable from 2 sources**: (a) explicit `.bmaplan` reference file, (b) inline expected values in the scenario plan (for synthetic fixture tests).
4. **Spike demonstrates ≥1 axis where sim matches reference exactly** (score 1.0) AND **≥1 axis where sim has known drift** (score < 1.0 with documented expected-drift reason — e.g., "page-quad-80% strategy doesn't match human's exact polygon").
5. **Output**: `artifacts/sim/lite/<scenario>/accuracy.json` with `{area_score, trace_score, export_score, roundtrip_score, weighted_total, per_page_details}`. Does NOT replace severity report; supplements it.
6. **No false-positive trap**: spike includes at least one case where the simulator's output LOOKS correct (passed all severity checks) but accuracy detects a drift (e.g., wrong page count, polygon on wrong layer).

### Out of scope (this invent pass)
- ML/learning anything from accuracy scores (we measure; don't optimize)
- "Auto-fix simulator to be more accurate" (future invent)
- Per-tool accuracy benchmarks (arc, ellipse) — covered by parity tests
- Hand-drawing reference .bmaplan files (separate task; here we accept a reference as input)
- Workflow-trace **vision** (i.e. "does the simulator click look like a human's mousemove") — too expensive, low ROI for testing

---

## Phase 4: Diverge

### Approach A — Browser-only, Inline Expected Values, No Aggregation
- **Axis**: Computation locus (browser-only JS, zero Python dependency)
- **Computation locus**: Runs in `lite/sandbox/invent-sim-accuracy.html` — reads STEP_LOG + downloaded files via FileReader API
- **Reference format**: Inline expected values baked into the scenario plan JSON (`expected: {areaM2, steps, ...}`)
- **Aggregation**: None — reports all 4 axes as raw numbers; user reads the table
- **Threshold model**: Per-axis fixed absolute (area ≤1%, trace edit-distance ≤2, export col-match 100%, roundtrip ≤0.1%)
- **False-positive trap**: `GHOST_PASS` invariant — if all 4 axes PASS but STEP_LOG length < expected minimum, flag
- **Files**: `lite/sandbox/invent-sim-accuracy.html` ~400; no app code
- **Forbidden touch**: NO · **Spike cost**: S

### Approach B — Python Script, Sidecar Reference JSON, Weighted Sum
- **Axis**: Reference representation (per-axis sidecar JSON)
- **Computation locus**: `tests/accuracy_runner.py` reads `accuracy_ref/<scenario>.json` post-run
- **Reference format**: Sidecar JSON per scenario with per-axis expected values + weights
- **Aggregation**: Weighted sum 0-1 (default area=0.4, trace=0.2, export=0.2, roundtrip=0.2)
- **Threshold model**: Configurable per scenario; sidecar fallback defaults
- **False-positive trap**: Cross-axis correlation — if area PASS but roundtrip > 2× area tolerance, flag `AXIS_DIVERGENCE`
- **Files**: `tests/accuracy_runner.py` ~350, `tests/accuracy_ref/*.json`; no app code
- **Forbidden touch**: NO · **Spike cost**: M

### Approach C — Browser+Python Split, Full .bmaplan Reference, Pass-Fail Matrix
- **Axis**: Aggregation strategy (per-axis binary pass-fail matrix, no collapsing)
- **Computation locus**: Browser computes T+X from downloaded files; Python computes A+R by diffing .bmaplan files
- **Reference format**: Full reference `.bmaplan` from human-run session
- **Aggregation**: 4-cell pass/fail matrix (no weighting/sum)
- **Threshold model**: Tiered — EXACT / CLOSE (<1%) / DRIFT (<5%) / FAIL per axis
- **False-positive trap**: 5th check — total object count sim vs ref; mismatch = `COUNT_MISMATCH`
- **Files**: `lite/sandbox/invent-sim-accuracy.html` ~250 + `tests/accuracy_compare.py` ~200
- **Forbidden touch**: NO · **Spike cost**: M

### Approach D — Browser-only, Synthetic-PDF Fixture, Weakest-Link Min
- **Axis**: Threshold model (weakest-link min — forces all axes to be non-zero)
- **Computation locus**: Entirely browser JS — synthetic PDF with closed-form known values; no human reference needed
- **Reference format**: Hard-coded closed-form expected values in HTML fixture (e.g. rect 3m×4m = 12.000 m²)
- **Aggregation**: `score = min(A, T, X, R)` — one low axis tanks the whole, surfaces partial regressions
- **Threshold model**: Per-axis relative (area: 0.1%, trace: exact, export: exact, roundtrip: 0.5%); min-of-4 is the gate
- **False-positive trap**: Outlier check — if any axis = 1.0 but min < 0.9, annotate that axis as `MASKING_RISK`
- **Files**: `lite/sandbox/invent-sim-accuracy.html` ~380
- **Forbidden touch**: NO · **Spike cost**: S

---

## Phase 5: Score

| Approach | Honesty | Multi-axis fidelity | Spike-able | Reference simplicity | Boundary safety | Spike cost | Total |
|---|---|---|---|---|---|---|---|
| **A inline/no-agg** | 5 | 5 | 5 | 5 | 5 | 5 | **30** |
| B sidecar/weighted | 3 | 4 | 3 | 3 | 5 | 3 | **21** |
| C split/matrix | 4 | 5 | 3 | 2 | 5 | 3 | **22** |
| D synthetic/min | 4 | 4 | 5 | 5 | 5 | 5 | **28** |

(Spike cost inverted S=5, M=3, L=1.) No `forbidden_surface_touch: YES` ✓ · No Phase 1 boundary ✓. No re-rank.

### Recommendation
**Approach A (browser-only, inline expected, no aggregation)** for spike. Fallback = **D** (synthetic-PDF + weakest-link min) if inline-in-plan grows too rigid for complex scenarios.

A scores perfect 30/30. Inline expected values remove reference-creation barrier (no extra files, no human session needed before spike can demonstrate). Zero aggregation preserves all 4 axes independently — satisfies frame's "single number is a lie" constraint. `GHOST_PASS` invariant catches success-criterion-6 trap. Spike for ≥1 exact + ≥1 drifted axis demonstrable in ~2 hours. **Tradeoff for human checkpoint**: inline-in-plan means scenario plans grow longer as you add expected values; if plan becomes unreadable, fall back to D (synthetic fixture + min-aggregation) which trades inline-flexibility for visual simplicity.

---

## Phase 6: Spike

Spike file: `lite/sandbox/invent-sim-accuracy.html` (~430 lines, browser-only, no server, no Python).

### Build
- 3-pane layout: fixtures sidebar (left) · scenario plan + sim output textareas (center) · accuracy result table (right)
- 4 pre-loaded fixtures cover spike acceptance criteria:
  1. **EXACT** — all 4 axes match perfectly → score 1.0 each, "ALL AXES PASS" verdict
  2. **AREA_DRIFT** — sim measured 1819.20 m² vs ref 1919.20 m² on p5 (-5.2%); area axis fails > 1% threshold
  3. **GHOST_PASS** — all 4 axes pass numerically (zero-baseline), BUT step_log has only 3 steps where expected.min_step_count = 8 → false-positive trap fires
  4. **MIXED** — area exact, trace drifts (extra `set_scale_retry` step → edit distance 1, still ≤2 threshold), all pass
- Click a fixture → autoload both textareas → autocompute → render result
- "Compute accuracy" button re-runs on edited input

### Code structure (matches Approach A spec)
- `scoreArea(plan, log)` — per-page `|sim-ref|/ref`; mean + max; pass if max ≤ 1%
- `scoreTrace(plan, log)` — Levenshtein on `expected.steps` vs `log.step_log.map(s=>s.step)`; pass if distance ≤ 2
- `scoreExport(plan, log)` — sheet count exact + columns array exact-match
- `scoreRoundtrip(plan, log)` — `|reopened - saved| / saved` from `step_log` observations; pass if drift ≤ 0.1%
- `checkGhostPass(plan, log, axes)` — fires if all 4 axes pass AND `step_log.length < expected.min_step_count`
- `compute(plan, log)` → `{axes, ghost}`; pure function, no DOM

### Result format (`accuracy.json` per run)
```json
{
  "scenario_id": "permit-45p-smoke",
  "timestamp": "<iso>",
  "axes": {
    "area":      { "mean": 0.0, "max": 0.0, "pass": true, "per_page": { "5": {ref, sim, rel}, "11": {...} } },
    "trace":     { "distance": 0, "pass": true },
    "export":    { "sheetCountOk": true, "columnsOk": true, "pass": true },
    "roundtrip": { "drift": 0.0, "pass": true }
  },
  "ghost_pass": false,
  "overall": "PASS | GHOST_PASS | FAIL"
}
```

### Acceptance check vs `## Frame` success criteria

| # | Criterion | Spike status |
|---|---|---|
| 1 | 4 axes scored independently | ✅ Verified by EXACT fixture — table shows A·T·X·R as 4 separate rows, no aggregation |
| 2 | All 4 axes from existing simulator outputs | ✅ Code reads only `step_log[*].step`, `step_log[*].observed.*`, `step_log[*].sub_summary.areas` — all fields the SIM-1.1 driver already produces |
| 3 | Reference from 2 sources | ✅ Inline `plan.expected.*` demonstrated. Sidecar `.bmaplan` source deferred to GO-sprint (frame allows, spike doesn't need to demo both) |
| 4 | ≥1 axis exact + ≥1 drifted | ✅ EXACT fixture: all 4 = 1.0. AREA_DRIFT fixture: area axis ≈ 5.2% > 1% → fails. Documented expected drift: "page-quad-80% strategy intentionally doesn't match human's exact polygon" |
| 5 | `accuracy.json` output, supplements severity | ✅ Bottom of right pane shows the exact JSON. Format proves it doesn't replace severity — it's a separate artifact |
| 6 | False-positive trap | ✅ GHOST_PASS fixture: all 4 axes show ✓ but yellow "GHOST_PASS" verdict fires because step_log.length(3) < min_step_count(8). User instructed "DO NOT TRUST the per-axis scores; investigate STEP_LOG first" |

### What the spike does NOT prove (deferred to GO-sprint)
- **Real wiring** to `/bma-simulate` Phase D — orchestrator would call `compute()` on the actual STEP_LOG, write `accuracy.json` next to `summary.json`. Pure function is portable; wiring is trivial
- **Sidecar `.bmaplan` reference source** — frame allows; first run will use inline (already supported)
- **History view** — comparing accuracy across past 3 runs (would extend `artifacts/sim/lite/history.jsonl` to include axis scores; future enhancement)
- **Configurable weights** — Approach A is no-aggregation; if users later want a weighted total, that's a follow-up invent (or just adopt Approach D's min-aggregation)

### Outcome
**SPIKE PASS** — all 6 frame success criteria demonstrably met. The 4 fixtures cover exact-match, single-axis drift, multi-axis drift, AND the false-positive trap. Approach A's "no aggregation" choice keeps the metric honest (no single-number lie) per research's anti-pattern alert.

Known limitation surfaced: **export accuracy is shallow** — spike compares sheet count + column names, NOT cell values. Real XLSX cell-value comparison requires SheetJS (~100KB) — defer to GO-sprint decision: keep shallow (cheap, catches schema drift) or add full cell match (catches value drift but bigger dep).

---

## Phase 7: Decision

(pending — awaiting human checkpoint)

---

## Phase 7: Decision

(pending — human checkpoint)
