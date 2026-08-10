# SPIKE_RESULTS — lite packaging (invent pipeline Phase 6)

Date: 2026-08-10 · Machine: Windows 10 Home 10.0.19045 · System Python 3.14.3 (`C:\Python314`)
Machine-readable: `results.json` (+ raw per-artifact `results_A.json`, `results_B.json`)

## PASS/FAIL matrix

| Case | Artifact A (one-file exe) | Artifact B (portable embed folder) |
|---|---|---|
| 1 — zero-Python launch | **PASS** — cold start **20.91 s** (2nd launch 8.29 s) | **PASS** — cold start **6.54 s** |
| 2 — 45-page permit, Thai path/name | **PASS** — all 200, XLSX parses | **PASS** — all 200, XLSX parses |
| 3 — double launch | **PASS** — 8100 + 8101, #1 kept serving | **PASS** — 8100 + 8101, #1 kept serving |
| Side-check E — pywebview/WebView2 | **YES** — window opened, full lite UI loaded, clean exit | (shared check, ran against repo lite) |

## Artifact A — PyInstaller one-file exe

- **File:** `dist/BMA-Plan-Lite-A.exe` — **77.7 MB** (81,478,161 bytes)
- **Toolchain:** PyInstaller **6.22.0 on Python 3.14.3 — built first try, no 3.14 failures**, ~160 s build.
- **Build cmd:** `build_onefile.bat` → `python -m PyInstaller spike_onefile.spec --noconfirm --distpath "<sandbox>\dist" --workpath "%TEMP%\bma_lite_build_a"` (workpath deliberately on local disk — Google Drive is far too slow for build churn).
- **Design (spec = `spike_onefile.spec`, entry = `launch_wrapper_a.py`):**
  - `lite/launch_lite.py` resolves app_dir via `Path(__file__).parent`, which breaks under `sys._MEIPASS` → per the task rules a **sandbox-only wrapper** re-implements the identical launch logic (same `_free_port(8100)` scan, same `uvicorn.run("server_lite:app", app_dir=...)`) and resolves `sys._MEIPASS/lite` when frozen. `lite/` files were **not modified**.
  - `server_lite.py`, `ui-lite.html`, `lite-report.html`, `static/**` bundled as **datas** under `lite/`; uvicorn's import-string form then imports `server_lite` from the extraction dir — confirmed by runtime log `[lite][static] serving from: C:\Users\...\Temp\_MEI...\lite\static`.
  - `collect_all` for pymupdf/uvicorn/fastapi/starlette (proto precedent) **+ openpyxl** (lazy import inside `/export-xlsx`) **+ aiofiles + anyio**; hidden imports `fitz`, `multipart`, `python_multipart`.
  - `launch_lite.py` has **no** browser-suppress flag → wrapper adds `BMA_LITE_NO_BROWSER=1` (eval-only nicety).

### A evals (env: PATH=`C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem;C:\Windows\System32\WindowsPowerShell\v1.0`, PYTHONHOME/PYTHONPATH unset)

- **Case 1 PASS** — `dist\BMA-Plan-Lite-A.exe` → port 8100, `/health` 200 at **20.91 s** from process start (dominated by one-file self-extraction of the 78 MB archive to `%TEMP%\_MEI...`; the Case-3 second launch with warm OS cache took 8.29 s).
- **Case 2 PASS** — `POST /upload` of `แบบทดสอบ\โครงการทดสอบ_แบบก่อสร้าง.pdf` (19.2 MB, 45 pages, Thai name echoed back intact): upload 0.13 s → `pageinfo/1` 200 → `page/1` 200 (0.43 s, 246 KB) → **upload+first render 0.56 s** → `page/20` 200 (0.95 s, 1.05 MB) → `thumb/45` 200 (0.07 s) → `POST /export-xlsx` 200 (0.76 s, 5,514 B) and **openpyxl parses it** (sheets `Measurements` + `Summary`, 1 data row). Server working set after Case 2 (tasklist, current not peak): **115.9 MB** child + 6.6 MB bootloader parent.
- **Case 3 PASS** — expected behavior per `launch_lite.py`: `_free_port` scans from 8100, so instance 2 must bind 8101. Observed: instance 2 → `http://127.0.0.1:8101/`, healthy in 8.29 s, while instance 1 on 8100 still answered `/health` 200.

## Artifact B — portable embeddable-Python folder

- **Folder:** `portable/` — **112.3 MB, 2,993 files** (python-embed 3.11.9 + site-packages + lite runtime copy). The folder itself is the artifact (not zipped, per spec).
- **How it was made (documented approach — direct install, not `--target`):**
  1. `python-3.11.9-embed-amd64.zip` (11.2 MB, python.org/ftp) → `portable/python-embed/`.
  2. `python311._pth` rewritten to: `python311.zip` / `.` / `Lib\site-packages` / `import site` (uncommenting `import site` + adding the site-packages line).
  3. `get-pip.py` bootstrap → pip 26.2.1 **inside the embedded interpreter**; then `portable\python-embed\python.exe -m pip install fastapi uvicorn aiofiles python-multipart pymupdf openpyxl` installs straight into `python-embed\Lib\site-packages` (works because step 2 put it on the path; `--target` not needed). Installed: fastapi 0.141.1, uvicorn 0.52.1, pymupdf 1.28.2, openpyxl 3.1.5, aiofiles 25.1.0, python-multipart 0.0.32, starlette 1.6.0, pydantic 2.13.4.
  4. `portable/lite/` = verbatim copy of `server_lite.py`, `launch_lite.py`, `ui-lite.html`, `lite-report.html`, `static/` (47 files).
  5. `portable/run.bat` clears PYTHONHOME/PYTHONPATH then runs `python-embed\python.exe lite\launch_lite.py`.

### B evals (same sanitized env)

- **Case 1 PASS** — `cmd /c portable\run.bat` → port 8100, `/health` 200 at **6.54 s**. (Default browser pops open — `launch_lite.py` has no flag; accepted per task.)
- **Case 2 PASS** — same sequence/file as A: upload 0.25 s → **upload+first render 0.68 s** → page/20 0.94 s → thumb/45 0.08 s → export-xlsx 200 (1.55 s) parses with openpyxl. Server working set after Case 2: **102.9 MB**.
- **Case 3 PASS** — instance 2 → 8101 in 5.79 s; instance 1 on 8100 answered `/health` 200 throughout.

### Deviation found & fixed during eval

The first `run.bat` was written with LF-only line endings → `cmd.exe` mis-parsed it (`'tlocal' is not recognized...`, a comment line echoed as a command). The server **still started and all 3 cases passed**, but stdout was noisy. Rewrote `run.bat` with CRLF (ASCII) and re-verified a clean launch (6.7 s, zero cmd errors). **Lesson: ship .bat files as CRLF.**

## Side-check E — pywebview / WebView2

`pip install pywebview` (6.2.1) on system 3.14 → `spike_webview.py` (uvicorn thread on port 8177 + `webview.create_window(..., gui='edgechromium')`, auto-destroy after 8 s). **Result: YES** — the WebView2 window opened and loaded the complete lite UI (server log shows every `/static/js/*.js` + pdf.js worker fetched through the window), then exited cleanly (`WEBVIEW_EXITED_CLEANLY`). No hang, no error.

## Caveats / notes

1. **Case 1 is an approximation** of a no-Python machine (sanitized PATH + unset PYTHONHOME/PYTHONPATH). VC++ runtime, WebView2 runtime and other OS DLLs already exist on this dev machine; a genuinely clean Windows box could still differ (embeddable zip does ship `vcruntime140.dll`; PyInstaller bundles its own too — risk is low but unverified).
2. **A's one-file cold start (8–21 s) is its real cost** — self-extraction of 78 MB to `%TEMP%` on every launch; AV scanning typically doubles it on customer machines. A `--onedir` build (proto's own precedent) would remove nearly all of it at the price of a folder instead of a single exe.
3. **B is 2,993 small files** — fine as a folder-on-disk artifact, but distribution requires zipping and copying is slow (the pip install onto Google Drive took ~10 min; on a local disk it's ~1 min). Also B pops the default browser on every launch until a `BMA_LITE_NO_BROWSER`-style flag is added upstream in `lite/launch_lite.py` (one-line, additive).
4. PyInstaller 6.22.0 handled **Python 3.14 without any workaround** — the anticipated 3.14 failure did not materialize.
5. Working-set figures are point-in-time tasklist samples right after Case 2, not true peaks.

## Files in this sandbox

`spike_onefile.spec`, `build_onefile.bat`, `launch_wrapper_a.py`, `dist/BMA-Plan-Lite-A.exe`, `portable/` (artifact B), `eval_driver.py`, `spike_webview.py`, `results_A.json`, `results_B.json`, `results.json`, `python-3.11.9-embed-amd64.zip`, `get-pip.py`, `แบบทดสอบ/โครงการทดสอบ_แบบก่อสร้าง.pdf` (19.2 MB test copy).
