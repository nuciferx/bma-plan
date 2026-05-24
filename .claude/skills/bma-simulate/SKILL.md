---
name: bma-simulate
description: |
  Multi-model workflow simulator for BMA-Plan **lite**. Given a PDF (or default to the canonical 45-page permit), runs the full real-user workflow (open → set scale → measure → save → reopen → export) with model-splitting for accuracy: **Opus (main)** plans the scenario + verifies the result, **sonnet (`bma-sim-driver`)** executes Playwright deterministically against `lite/ui-lite.html`. Past-run logs in `artifacts/sim/lite/` are fed back as few-shot context so each run can learn from the last 1-3 outcomes (prompt-side, not weight-side — Anthropic does not expose Claude fine-tuning).

  Purpose: **test the lite system end-to-end** at a level synthetic markers can't reach. Severity-tagged report (CRASH / BROKEN / FRICTION / COSMETIC) like the existing journey-testers, PLUS a per-phase model usage breakdown so you can see where Opus vs sonnet was actually used.

  Trigger phrases (Thai): "/bma-simulate", "ลอง simulate lite", "ทดสอบ workflow lite แบบ multi-model", "simulate การเปิดไฟล์วัดพื้นที่"
  Trigger phrases (English): "/bma-simulate", "simulate lite workflow", "multi-model lite test"

  Do NOT use for: marker pass/fail (use lite/tests/* directly), single-customer-PDF triage (use `/lite-sandbox-test`), proto-side journey (use `/bma-human-test`).
---

# bma-simulate — multi-model lite workflow simulator

## What this is

A 4-phase orchestrator that walks lite through a real user workflow with explicit model-split, so each phase uses the most cost-effective model that's still smart enough for that phase's job:

| Phase | Owner | Model | Why |
|---|---|---|---|
| A — PLAN | this skill (you) | **Opus** (main agent) | Generating a SCENARIO_PLAN from PDF metadata + past-run patterns requires judgment about edge cases. Worth Opus. |
| B — DRIVE | `bma-sim-driver` subagent | **sonnet** | Mechanically executing Playwright steps and capturing observables. Sonnet is fast + faithful — Opus would burn tokens here. |
| C — VERIFY | this skill (you) | **Opus** (main agent) | Mapping STEP_LOG → severity-tagged findings is a judgment call. Defer to Opus. |
| D — REPORT | this skill (you) | **Opus** (main agent) | Synthesize + append past-run log. Cheap. |

This pattern is "**model-routed orchestration**" — same shape as Pack G (`/bma-sandbox-test` → `bma-sandbox-journey-tester` + `bma-issue-triager`), but explicitly multi-model rather than all-sonnet.

## When to use

Use `/bma-simulate` when you want to know "does the full lite workflow STILL hang together end-to-end with the current code", with a fuller picture than `/lite-sandbox-test` provides:

- `/lite-sandbox-test` runs ALL PDFs in `sandbox/`, shallow (Tier 1) + maybe deep (Tier 2). Coverage > depth.
- `/bma-simulate` runs ONE scenario deeply, with model-routed plan/drive/verify, and stores the run in a long-lived history so successive runs can compare. Depth + history > coverage.

Use both at different times. They are not redundant.

## Steps

### Phase A — PLAN (Opus, in-skill)

1. **Resolve target PDF**. If user gave `pdf_path`, use it. Else default to `20250616_RAMA4 APARTMENT PERMIT rev 1.pdf` at repo root (the canonical 45-page permit). If neither exists → emit `SIM_NO_PDF` and stop.
2. **Read PDF metadata** cheaply — file size, modified time. Do NOT render the PDF in the planning phase; that's the driver's job.
3. **Read past-run history** from `artifacts/sim/lite/`. Take the last 1-3 runs' final summary JSON files (NOT full logs — too big). If the dir is empty, that's a first run; note it.
4. **Generate a SCENARIO_PLAN** as a JSON list of step specs. **Pick the right scenario class for the goal** — do NOT default to the smoke plan when the user is testing real-world workflow.

   **Scenario class A — `*-smoke` (~7 steps, ~30 s)** — dev sanity. Opens PDF, sets scale, draws ONE test polygon on page 1, saves+reopens. Useful to prove the driver/lite boot still works. NOT useful as a real workflow test.

   **Scenario class B — `*-full-loop` (~12-20 steps, ~3-5 min)** — real user workflow. Walks every MEASURABLE page (skipping cover/legend/section/detail/schedule), draws a per-page polygon, then opens the Report Review and verifies per-floor totals roll up. THIS is the default for any "simulate lite end-to-end" request.

   Baseline `permit-45p-full-loop` (for the canonical RAMA4 45-page permit):
   ```json
   [
     { "step": "boot_lite",     "expect": { "server_up": true, "port_range": [8240, 8299] } },
     { "step": "open_pdf",      "args": { "path": "<resolved>" }, "expect": { "pages_ge": 45 } },
     { "step": "tag_pages",     "args": { "fixture": "permit-45p-tags.json", "fallback_inline": {
         "site": [5, 7, 8],
         "floor": [11, 12, 13, 14, 15, 16],
         "ignore": "all-others"
       }}, "expect": { "tagged_count_ge": 9 } },
     { "step": "set_scale",     "args": { "page": 11, "pt_per_m": 30.0, "via": "page.evaluate" }, "expect": { "scale_state": "manual" } },
     { "step": "measure_loop",  "args": { "pages": [5, 7, 8, 11, 12, 13, 14, 15, 16], "polygon_strategy": "page-quad-80%" }, "expect": { "objects_per_page_ge": 1, "areas_nonzero": true } },
     { "step": "open_report_review", "expect": { "report_panel_visible": true } },
     { "step": "verify_report_totals", "args": { "expect_floor_count_ge": 5, "expect_site_present": true, "tolerance_pct": 50 }, "expect": { "totals_render": true } },
     { "step": "save_bmaplan",  "expect": { "blob_size_gt": 1000 } },
     { "step": "reopen_bmaplan","expect": { "object_count_per_page_match": true, "total_area_unchanged_within_pct": 0.1 } },
     { "step": "export_xlsx",   "expect": { "file_nonempty": true, "sheet_count_ge": 1 } }
   ]
   ```

   The measurable-pages list `[5, 7, 8, 11, 12, 13, 14, 15, 16]` is the **same classification** the sandbox spike `lite/sandbox/invent-45page-permit-spike.html` uses (p5/7/8 = site, p11-16 = floor + roof). If a real fixture file `lite/tests/fixtures/permit-45p-tags.json` exists, prefer that; otherwise use the inline fallback shown above.

   `polygon_strategy: "page-quad-80%"` = inscribe an axis-aligned quad covering 80% of the page raster (driver computes from canvas dimensions at runtime). Not "the right area" — just "a measurable polygon big enough to prove the measure tool worked on this page". Real accuracy comes later via INV-SIM-2.

   For NON-`permit-45p` PDFs, Opus must either: (a) consult past-run history for a known plan for this PDF, OR (b) generate a smoke plan + flag in the report that "full-loop needs page classification — please tag pages manually OR supply a tags fixture".

   Keep total ≤20 steps so the driver stays under its 5-min cap. The measure_loop step itself counts as 1 step but the driver expands it internally to N navigate+draw+verify sub-actions; the per-step 90-second cap applies to each sub-action.
5. **Pick a `scenario_id`** in kebab-case (e.g. `permit-45p-baseline`, `permit-45p-arc-edge-probe`).
6. Create `artifacts/sim/lite/<scenario_id>-<timestamp>/` directory.

### Phase B — DRIVE (delegate to `bma-sim-driver`, sonnet)

Spawn `bma-sim-driver` (subagent_type) with the SCENARIO_PLAN + past-run summaries (≤3 inline) + the artifacts dir path. The driver:
- Boots lite (mirrors `lite/tests/test_pan_controls.py`'s boot block)
- Executes each step in order via Playwright + `page.evaluate`
- Returns the STEP_LOG JSON + a ≤15-line human summary
- Writes `driver.py`, `run.log`, optional screenshots into the artifacts dir
- Time-boxed: 90 s/step, 5 min/scenario total

If the driver returns `SIM_DRIVE_ABORTED:<reason>` → record the abort in the report and skip Phase C; go directly to Phase D with a CRASH-level finding.

### Phase C — VERIFY (Opus, in-skill)

Read the STEP_LOG. For each step:
- If `status === "pass"` AND `observed` matches the `expect` block within tolerance → ✅
- If `status === "fail"` OR a critical `observed` is missing → derive severity:
  - **CRASH** — `boot_lite` failed, uvicorn died, browser tab errored
  - **BROKEN** — wrong/missing result (area mismatch beyond tolerance, polygon lost on reopen, empty export)
  - **FRICTION** — works but slow/confusing (per-step > 30 s, error messages in browser console even if step passed)
  - **COSMETIC** — visual / polish only
- Console errors + network 5xx across all steps are aggregated and reported even if the step they belong to "passed".

Severity definitions match the existing `bma-human-journey-tester` so reports are comparable.

### Phase D — REPORT (Opus, in-skill)

1. **Write per-run summary JSON** to `artifacts/sim/lite/<scenario_id>-<timestamp>/summary.json`:
   ```json
   {
     "scenario_id": "...",
     "timestamp": "...",
     "pdf_path": "...",
     "model_split": { "plan": "opus", "drive": "sonnet", "verify": "opus" },
     "step_results": [ ... ],
     "findings": [ { "severity": "BROKEN", "step": "reopen_bmaplan", "what": "...", "what_should_happen": "..." } ],
     "verdict": "SIM_OK | SIM_ISSUES | SIM_CRASH"
   }
   ```
2. **Append the summary into `artifacts/sim/lite/history.jsonl`** (one line per run; this is the few-shot source for future runs).
3. **Print a ≤25-line report to the user**, format:
   ```
   ### Lite Simulator Report — <date> · scenario=<scenario_id>

   model split: opus(plan) → sonnet(drive) → opus(verify)
   PDF: <name> (<size>, <pages>)

   #### Step results
   | step | status | note |
   |---|---|---|
   | boot_lite       | ✅ | port 8242 |
   | open_pdf        | ✅ | 45 pages |
   | set_scale       | ✅ | pts_per_m=1.0 |
   | draw_polygon    | ⚠ | area 9998.7 m² (expected 10000 ±1) → still within ±2% (FRICTION) |
   | export_xlsx     | ❌ | 0-byte file (BROKEN) |
   | save_bmaplan    | ✅ | 12.4 KB |
   | reopen_bmaplan  | ✅ | 1 object restored |

   #### Findings
   1 BROKEN · 1 FRICTION

   Verdict: SIM_ISSUES
   Artifacts: artifacts/sim/lite/<scenario_id>-<timestamp>/
   ```
4. Stop. Do **not** auto-file findings into `PHASE_INDEX.md`. The human reads the report and decides whether to file follow-up sprints. (Compare: `/bma-sandbox-test` DOES auto-file via `bma-issue-triager`; this skill doesn't, because per-run cadence is different and we don't want PHASE_INDEX clutter on every run.)

## Few-shot learning loop

After each run, `summary.json` is appended to `artifacts/sim/lite/history.jsonl`. Phase A of the NEXT run reads the last 1-3 lines and feeds them to both itself (Opus) and the driver (sonnet) as context. This is "**learning**" in the prompt-cache sense: the orchestrator notices "the last 3 runs all failed at `reopen_bmaplan` with edges loss" and biases its SCENARIO_PLAN to probe that specific regression. No weight updates, no fine-tuning.

If `history.jsonl` exceeds 100 lines (a year+ of weekly runs), prune to last 30 + keep a monthly digest at the top. Not implemented v1 — flag if it ever matters.

## Hard rules

- **Lite-only.** This skill targets `lite/ui-lite.html` + `lite/server_lite.py`. Do not point it at `proto/`. Proto has its own journey-tester.
- **Never edit `lite/` or `proto/` files.** Read-only on app code. Skill writes ONLY to `artifacts/sim/lite/`.
- **Model split is fixed at v1.** Opus(plan) + sonnet(drive) + Opus(verify). If you want different split, change this SKILL.md — don't do it ad-hoc per run.
- **One scenario per invocation.** Multi-scenario campaigns = multiple `/bma-simulate` calls (orchestrate by the human or another skill).
- **No auto-file to PHASE_INDEX.** Findings are surfaced in the report only. Human files follow-ups manually.
- **No commit from this skill.** Artifacts are gitignored (`artifacts/` already is). History file is gitignored.
- **Boot pattern reused from tests.** Skill+driver use the same uvicorn/port-scan/playwright boot as `lite/tests/test_pan_controls.py`. Do not invent a new launcher.

## Stop conditions

| # | Condition | Emit |
|---|---|---|
| 1 | Run completed, no CRASH or BROKEN | `SIM_OK` |
| 2 | Run completed, has BROKEN or FRICTION | `SIM_ISSUES` |
| 3 | `boot_lite` failed OR driver returned `SIM_DRIVE_ABORTED` | `SIM_CRASH` |
| 4 | No PDF resolvable | `SIM_NO_PDF` |
| 5 | `artifacts/sim/lite/` dir cannot be written (permission) | `SIM_ARTIFACTS_BLOCKED` |
