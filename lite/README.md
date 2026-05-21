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

## Run

**One-click (Windows):** double-click **`lite/run.bat`** — it finds Python, installs the
few dependencies the first time, starts the server, and opens your browser. Close the
window (or Ctrl+C) to stop.

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
