"""
Manual smoke probe — verifies lite's NEW PDF.js render path works end-to-end
on the real lite server with a real PDF (no curImg dummy shim involved).

Boots server_lite.py, opens Chromium headless, uploads RAMA4 PDF, asserts:
  1. PDF.js loaded successfully (no console errors during navigation)
  2. PageRenderer.ready() returns true after upload
  3. Canvas has non-empty rendered content (sample-pixel test)
  4. Rotating the view (V.rot += 90) does NOT crash
  5. Rotating the PAGE (pageRot[curPage] = 90) does NOT crash
     and canvas still has non-empty content
  6. Console error count == 0 throughout

Run from repo root:
    python3.11 lite/sandbox/invent-lite-pdf-render-quality/smoke_pdfjs_live.py
"""
import subprocess, sys, time, socket, pathlib, shutil, tempfile, signal
from playwright.sync_api import sync_playwright

ROOT     = pathlib.Path(__file__).resolve().parents[3]
PDF_SRC  = ROOT / "20250616_RAMA4 APARTMENT PERMIT rev 1.pdf"
TMP_PDF  = pathlib.Path(tempfile.gettempdir()) / "smoke_pdfjs_test.pdf"

if not PDF_SRC.exists():
    print(f"FATAL: test PDF not found at {PDF_SRC}")
    sys.exit(1)
shutil.copy(PDF_SRC, TMP_PDF)
print(f"[setup] PDF copy at {TMP_PDF} ({TMP_PDF.stat().st_size/1e6:.1f} MB)")

# find a free port
def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

PORT = free_port()

# Start server_lite as subprocess (uvicorn)
import os
env = os.environ.copy()
env["LITE_PORT"] = str(PORT)  # in case launcher reads it
launch_cmd = [sys.executable, "-m", "uvicorn", "lite.server_lite:app",
              "--host", "127.0.0.1", "--port", str(PORT), "--log-level", "warning"]
print(f"[server] starting on http://127.0.0.1:{PORT} …")
server = subprocess.Popen(launch_cmd, env=env, cwd=str(ROOT),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# Wait for server to be ready
for _ in range(50):
    try:
        with socket.create_connection(("127.0.0.1", PORT), timeout=0.2):
            break
    except Exception:
        time.sleep(0.1)
else:
    print("FATAL: server didn't start")
    server.terminate(); sys.exit(1)
print(f"[server] up")

errors_during_session = []
checks = {}

try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1600, "height": 900},
                                  device_scale_factor=2.0)
        page = ctx.new_page()

        def on_console(msg):
            if msg.type in ("error",):
                errors_during_session.append(f"[{msg.type}] {msg.text}")
        def on_pageerror(err):
            errors_during_session.append(f"[pageerror] {err}")
        page.on("console", on_console)
        page.on("pageerror", on_pageerror)

        url = f"http://127.0.0.1:{PORT}/"
        page.goto(url)
        page.wait_for_function("typeof PageRenderer !== 'undefined'", timeout=15000)
        print("[1] PageRenderer defined")

        # Upload PDF
        page.set_input_files('#file-pdf', str(TMP_PDF))
        # Wait for PageRenderer.ready() to be true
        page.wait_for_function("PageRenderer.ready() === true", timeout=45000)
        checks["1_pdfjs_loaded"] = True
        checks["2_renderer_ready"] = True
        print("[2] PDF uploaded, PageRenderer.ready() === true")

        # Give PDF.js a moment to render and let any async render task complete
        page.wait_for_timeout(2000)

        # Verify canvas has non-empty content via sample pixel check
        sample_check = page.evaluate("""() => {
          const cv = document.getElementById('cv');
          const ctx = cv.getContext('2d');
          const w = cv.width, h = cv.height;
          // Sample 9 points across the canvas
          const pts = [
            [w*0.2, h*0.2], [w*0.5, h*0.2], [w*0.8, h*0.2],
            [w*0.2, h*0.5], [w*0.5, h*0.5], [w*0.8, h*0.5],
            [w*0.2, h*0.8], [w*0.5, h*0.8], [w*0.8, h*0.8]
          ];
          let nonBg = 0;
          for (const [x,y] of pts) {
            const px = ctx.getImageData(x, y, 1, 1).data;
            // Background colors are dark (#0f1116) or placeholder (#1a1e28).
            // If sampled pixel is brighter than both, it's PDF content.
            const brightness = (px[0] + px[1] + px[2]) / 3;
            if (brightness > 80) nonBg++;
          }
          return { nonBg, total: pts.length, canvas_w: w, canvas_h: h };
        }""")
        print(f"[3] canvas sample-pixel: {sample_check['nonBg']}/{sample_check['total']} non-background pixels")
        checks["3_canvas_has_content"] = sample_check["nonBg"] >= 4  # at least half should be content

        # Test V.rot=90
        page.evaluate("() => { V.rot = 90; fit(); }")
        page.wait_for_timeout(1500)
        sample_after_vrot = page.evaluate("""() => {
          const cv = document.getElementById('cv');
          const ctx = cv.getContext('2d');
          const w = cv.width, h = cv.height;
          let nonBg = 0;
          for (let i = 0; i < 9; i++) {
            const px = ctx.getImageData(w*((i%3+1)*0.2), h*((Math.floor(i/3)+1)*0.2), 1, 1).data;
            if ((px[0]+px[1]+px[2])/3 > 80) nonBg++;
          }
          return { nonBg, vrot: V.rot };
        }""")
        print(f"[4] after V.rot=90: {sample_after_vrot['nonBg']}/9 non-bg pixels (V.rot={sample_after_vrot['vrot']})")
        checks["4_vrot_90_works"] = sample_after_vrot["nonBg"] >= 4

        # Reset V.rot, test pageRot=90
        page.evaluate("() => { V.rot = 0; pageRot[curPage] = 90; if(window.pageCache) delete pageCache[curPage]; loadPage(curPage); }")
        # rotatePage clears pageCache + reloads. wait for ready again
        page.wait_for_function("PageRenderer.ready() === true", timeout=15000)
        page.wait_for_timeout(2000)
        sample_after_pgrot = page.evaluate("""() => {
          const cv = document.getElementById('cv');
          const ctx = cv.getContext('2d');
          const w = cv.width, h = cv.height;
          let nonBg = 0;
          for (let i = 0; i < 9; i++) {
            const px = ctx.getImageData(w*((i%3+1)*0.2), h*((Math.floor(i/3)+1)*0.2), 1, 1).data;
            if ((px[0]+px[1]+px[2])/3 > 80) nonBg++;
          }
          return { nonBg, pgRot: pageRot[curPage] };
        }""")
        print(f"[5] after pageRot=90: {sample_after_pgrot['nonBg']}/9 non-bg pixels (pageRot={sample_after_pgrot['pgRot']})")
        checks["5_pagerot_90_works"] = sample_after_pgrot["nonBg"] >= 4

        # Test pageRot=270
        page.evaluate("() => { pageRot[curPage] = 270; if(window.pageCache) delete pageCache[curPage]; loadPage(curPage); }")
        page.wait_for_function("PageRenderer.ready() === true", timeout=15000)
        page.wait_for_timeout(2000)
        sample_after_pgrot270 = page.evaluate("""() => {
          const cv = document.getElementById('cv');
          const ctx = cv.getContext('2d');
          const w = cv.width, h = cv.height;
          let nonBg = 0;
          for (let i = 0; i < 9; i++) {
            const px = ctx.getImageData(w*((i%3+1)*0.2), h*((Math.floor(i/3)+1)*0.2), 1, 1).data;
            if ((px[0]+px[1]+px[2])/3 > 80) nonBg++;
          }
          return { nonBg, pgRot: pageRot[curPage] };
        }""")
        print(f"[6] after pageRot=270: {sample_after_pgrot270['nonBg']}/9 non-bg pixels (pageRot={sample_after_pgrot270['pgRot']})")
        checks["6_pagerot_270_works"] = sample_after_pgrot270["nonBg"] >= 4

        # Zoom test: V.k = 5
        page.evaluate("() => { pageRot[curPage] = 0; if(window.pageCache) delete pageCache[curPage]; loadPage(curPage); }")
        page.wait_for_function("PageRenderer.ready() === true", timeout=15000)
        page.wait_for_timeout(1500)
        page.evaluate("() => { V.k = 5; draw(); }")
        page.wait_for_timeout(2000)
        sample_zoom = page.evaluate("""() => {
          const cv = document.getElementById('cv');
          const ctx = cv.getContext('2d');
          const w = cv.width, h = cv.height;
          let nonBg = 0;
          for (let i = 0; i < 9; i++) {
            const px = ctx.getImageData(w*((i%3+1)*0.2), h*((Math.floor(i/3)+1)*0.2), 1, 1).data;
            if ((px[0]+px[1]+px[2])/3 > 80) nonBg++;
          }
          return { nonBg, vk: V.k };
        }""")
        print(f"[7] V.k=5 zoom: {sample_zoom['nonBg']}/9 non-bg pixels (V.k={sample_zoom['vk']})")
        checks["7_zoom_5x_works"] = sample_zoom["nonBg"] >= 4

        checks["8_no_console_errors"] = len(errors_during_session) == 0

        browser.close()
finally:
    server.send_signal(signal.SIGTERM if hasattr(signal, "SIGTERM") else signal.CTRL_BREAK_EVENT)
    try: server.wait(timeout=5)
    except Exception: server.kill()

print("\n" + "="*70)
print("SMOKE PDFJS LIVE RESULTS")
print("="*70)
for name, ok in checks.items():
    print(f"  {'✓' if ok else '✗'}  {name}")

if errors_during_session:
    print("\nConsole errors during session:")
    for e in errors_during_session:
        print(f"  {e}")

all_pass = all(checks.values())
if all_pass:
    print("\nSMOKE_PDFJS_LIVE_OK")
    sys.exit(0)
else:
    failed = [k for k,v in checks.items() if not v]
    print(f"\nSMOKE_PDFJS_LIVE_FAIL — {len(failed)} checks failed: {failed}")
    sys.exit(1)
