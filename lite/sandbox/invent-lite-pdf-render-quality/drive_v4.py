"""
SPIKE v4 driver — proves PDF.js render aligns with lite's ptToScreen contract.

Runs window.__spike4.runContractSweep() across 24 combos (6 zooms × 4 rotations).
Each combo verifies:
  C1 (math)   max|T*viewport(p) - ptToScreen(p)| < 0.01 CSS-px over 9 sampled PDF-pts
  C2 (visual) overlay rectangle diagonal == 100*sqrt(2)*RS*V.k within 0.5 CSS-px

If 24/24 PASS → PDF.js can drive lite's existing ptToScreen/screenToPt unchanged
                → safe to start Sprint #2 PDFJS-VIEWPORT-CLIPPED-INTEGRATION.

Run from repo root:
    python3.11 lite/sandbox/invent-lite-pdf-render-quality/drive_v4.py
"""
import http.server, socketserver, threading, json, pathlib, shutil, os, sys, tempfile
from playwright.sync_api import sync_playwright

ROOT     = pathlib.Path(__file__).resolve().parents[3]
SANDBOX  = ROOT / "lite" / "sandbox"
PDF_SRC  = ROOT / "20250616_RAMA4 APARTMENT PERMIT rev 1.pdf"

# Use a temp ASCII-safe copy so file:// upload through Playwright is robust
TMP = pathlib.Path(tempfile.gettempdir()) / "spike_v4_test.pdf"
if not PDF_SRC.exists():
    print(f"FATAL: test PDF not found at {PDF_SRC}")
    sys.exit(1)
shutil.copy(PDF_SRC, TMP)
print(f"[setup] PDF copy at {TMP} ({TMP.stat().st_size/1e6:.1f} MB)")

PORT = 8766
HEADED = "--headed" in sys.argv

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

httpd = socketserver.TCPServer(("127.0.0.1", PORT), QuietHandler,
                               bind_and_activate=False)
httpd.allow_reuse_address = True
httpd.server_bind(); httpd.server_activate()
os.chdir(str(SANDBOX))
threading.Thread(target=httpd.serve_forever, daemon=True).start()
print(f"[server] http://127.0.0.1:{PORT}/  serving  {SANDBOX}")

passCount = 0
total = 0
results = None

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=not HEADED)
    ctx = browser.new_context(viewport={"width": 1600, "height": 900},
                              device_scale_factor=2.0)  # simulate retina
    page = ctx.new_page()
    page.on("console", lambda m: print(f"[js {m.type}] {m.text}") if m.type in ("error","warning") else None)

    url = f"http://127.0.0.1:{PORT}/invent-lite-pdf-render-quality-pdfjs-v4.html"
    page.goto(url)
    page.wait_for_function("window.__spike4 !== undefined", timeout=15000)
    print("[loaded] spike v4 page")

    page.set_input_files("#file-input", str(TMP))
    page.wait_for_function("window.__spike4.curPageNum >= 1 && window.__spike4.getStats().c1 !== undefined", timeout=20000)
    print("[loaded] PDF in spike")

    print("[sweep] running 24-combo contract sweep…")
    sweep = page.evaluate("() => window.__spike4.runContractSweep()")
    if not sweep:
        print("FATAL: sweep returned null")
        sys.exit(1)
    passCount = sweep["passCount"]
    total = sweep["total"]
    results = sweep["results"]

    if HEADED:
        print("[headed] sweep done — press Enter to close")
        try: input()
        except EOFError: pass
    browser.close()

print("\n" + "="*70)
print(f"SPIKE_V4 RESULTS  {passCount}/{total} combos PASS")
print("="*70)
for r in results:
    ok = "✓" if (r["c1_pass"] and r["c2_pass"]) else "✗"
    print(f"  {ok}  z={r['zoom']:>3}×  r={r['rot']:>3}°   "
          f"C1Δ={r['c1_maxDelta']:.6f}  C2Δ={r['c2_delta']:.3f}  "
          f"render={r['renderMs']}ms")

if passCount == total:
    print("\n✓ SPIKE_V4 CONTRACT PASS — PDF.js can drive lite's ptToScreen unchanged")
    print("  → safe to proceed with Sprint #2 PDFJS-VIEWPORT-CLIPPED-INTEGRATION")
    sys.exit(0)
else:
    fails = [r for r in results if not (r["c1_pass"] and r["c2_pass"])]
    print(f"\n✗ SPIKE_V4 CONTRACT FAIL — {len(fails)} combos diverge:")
    for r in fails:
        print(f"  ✗ z={r['zoom']}× r={r['rot']}°  C1Δ={r['c1_maxDelta']:.6f}  C2Δ={r['c2_delta']:.3f}")
    print("  → Sprint #2 needs further design work before implementation")
    sys.exit(1)
