# BMA-Plan Lite

Standalone, minimal measurement face of BMA-Plan — a **true sibling** of `/proto/`,
not a feature flag inside it. Built per invent decision **INV-2026-05-21-001
(Approach A)**. See `docs/invent/bma-plan-lite-standalone.md` for the full frame,
research, and the locked function scope.

## Why a separate tree

`proto/ui.html` is ~4,230 lines. Lite ships the F11/focus-mode workflow (single-row
top menu + full canvas + corner HUDs) as its own lightweight tree so the main app
stays untouched and lite can be packaged/distributed independently.

## The vendoring contract (Approach A)

Lite does **not** import proto. The measurement math
(`RS`, `pdfToC`, `cToPdf`, `polyAreaM2`, `polyMetrics`, `polySelfIntersects`,
`pathAreaM2`, `flattenPathToPoints`, helpers) is **vendored verbatim** into
`static/js/measure-engine.js`. It must stay **byte-identical** to `proto/ui.html`
so that `.bmaplan` files cross-open between lite and proto with identical area
values.

**`tests/test_measure_parity.py` enforces this.** It extracts the functions from
both `proto/ui.html` and `lite/static/js/measure-engine.js`, asserts the source
lines match, and runs pinned fixtures through Node to assert identical numeric
output. **This test must pass before any proto commit that touches those 9
functions.** On failure: re-sync `measure-engine.js` from proto and re-run.

Forbidden: editing `proto/*` from here; renaming/removing `.bmaplan` fields;
changing the vendored math.

## Layout

```
lite/
  ui-lite.html              # single-page UI (LITE-0 scaffold; chrome lands LITE-2)
  server_lite.py            # fresh minimal FastAPI (LITE-0 skeleton; endpoints LITE-1)
  launch_lite.py            # free-port launcher (port 8100+), opens browser
  static/js/measure-engine.js   # VENDORED math — do not edit
  tests/
    test_measure_parity.py  # anti-drift parity gate
    fixtures/measure_parity_v1.json
```

## Size discipline (hard rule — 2026-05-22)

Lite stays lean by contract. Runtime source files have a hard line cap:

| File | Cap | Why |
|---|---|---|
| `ui-lite.html` | **1200 lines** | the single-page UI shell — bulk logic belongs in `static/js/*.js`, not inline |
| every other runtime file (`server_lite.py`, `lite-report.html`, `static/js/*.js`) | **1000 lines** | one cohesive region per module |

**When a file crosses its cap, the next slice MUST split it** — extract one cohesive
region into a new `static/js/<region>.js` (the `layer-system.js` / `layer-panel.js`
pattern), not bolt more onto the offender. No new feature lands while a file is over cap.

- Test files (`tests/*.py`) are **exempt** from the hard cap, but a single test file
  over 1000 lines is a smell — split it by feature.
- Enforced at the `/bma-lite-dev` REVIEW gate: `wc -l` is checked before finalize; a
  diff that pushes a file over cap is sent back to extract first.
- Verify anytime: `wc -l ui-lite.html server_lite.py lite-report.html static/js/*.js`.

> Headroom note (2026-05-22): `ui-lite.html` is at 1120 / 1200 (80 lines left). The next
> slice (L2c-3 custom-layer UI panel) must land its panel logic in `static/js/layer-panel.js`,
> not inline in `ui-lite.html`.

## Run

**One-click (Windows):** double-click **`lite/run.bat`** — it finds Python, installs the
few dependencies the first time, starts the server, and opens your browser. Close the
window (or Ctrl+C) to stop.

**One-click (macOS):** double-click **`lite/run.command`** — same behaviour. First time only,
make it executable in Terminal: `chmod +x lite/run.command`. (If Finder shows "cannot be
opened because it is from an unidentified developer", right-click → Open → Open.)

**Manual:**
```bash
pip install fastapi uvicorn aiofiles python-multipart pymupdf
python lite/launch_lite.py            # serves on a free port 8100+, opens browser
python lite/tests/test_measure_parity.py   # drift gate — prints MEASURE_PARITY_OK
```
Requires Python 3.11+ (and Node.js for the parity test). `openpyxl` is only needed
later for LITE-6 XLSX export.

### Use it
Open PDF → press **S** and click two points on a known dimension, enter its length in
metres (Set Scale) → press **A** and click a polygon, double-click to finish → the
area appears. **D** = distance, **N** = count, **R** = reference line. **⌘K** search
pages, **F12** overview, **F** focus mode. Right-click a shape to hide/show its
dimensions. Ctrl+S saves a `.bmaplan`.

## Roadmap (sub-sprints — see PHASE_INDEX INV-2026-05-21-001)

LITE-0 scaffold ✅ · LITE-1 backend endpoints · LITE-2 single-row chrome ·
LITE-3 measure tools · LITE-4 dimension rendering · LITE-5 save/load + count ·
LITE-6 export · LITE-7 packaging.
