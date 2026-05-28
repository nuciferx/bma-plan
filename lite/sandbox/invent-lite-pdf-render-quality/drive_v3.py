"""
SPIKE v3 driver — Playwright-drives the spike against ผัง.pdf and reports.

Starts a tiny localhost HTTP server (so the spike's ESM imports + CDN worker
load cleanly; file:// can be flaky with PDF.js worker), opens the v3 spike in
headed Chromium, loads ผัง.pdf, then steps through zoom + rotation combos
reading the sidebar status for each combo. Saves screenshots + a summary.

Run from repo root:
    python3.11 lite/sandbox/invent-lite-pdf-render-quality/drive_v3.py

Headed by default so the user can watch.
"""
import http.server, socketserver, threading, time, json, pathlib, sys
from playwright.sync_api import sync_playwright

ROOT     = pathlib.Path(__file__).resolve().parents[3]
SANDBOX  = ROOT / "lite" / "sandbox"
PDF_PATH = pathlib.Path("/tmp/phang.pdf")   # ASCII-safe copy of ผัง.pdf
OUT_DIR  = SANDBOX / "invent-lite-pdf-render-quality" / "v3-results"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PORT = 8765
HEADED = True   # set False for headless

# --- start local http server in background, serving lite/sandbox/ ---
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

httpd = socketserver.TCPServer(("127.0.0.1", PORT), QuietHandler,
                               bind_and_activate=False)
httpd.allow_reuse_address = True
httpd.server_bind()
httpd.server_activate()
# Serve from sandbox dir
import os
os.chdir(str(SANDBOX))
server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
server_thread.start()
print(f"[server] http://127.0.0.1:{PORT}/  serving  {SANDBOX}")

ZOOMS = [1, 2, 5, 10, 20, 50, 100]
ROTS  = [0, 90, 180, 270]

results = []

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=not HEADED)
    ctx = browser.new_context(viewport={"width": 1600, "height": 900},
                              device_scale_factor=2.0)   # simulate retina
    page = ctx.new_page()
    page.set_default_timeout(15_000)
    # capture console errors so we know if PDF.js fails silently
    page.on("console", lambda m: print(f"  [console.{m.type}] {m.text[:200]}"))
    page.on("pageerror", lambda e: print(f"  [pageerror] {e}"))
    url = f"http://127.0.0.1:{PORT}/invent-lite-pdf-render-quality-pdfjs-v3.html"
    print(f"[playwright] open  {url}")
    page.goto(url)

    # Wait for the spike module script to finish (loader is exposed last).
    try:
        page.wait_for_function("typeof window.__spikeLoadPdfBuffer === 'function'", timeout=20_000)
    except Exception:
        lib_status = page.locator("#lib-status").inner_text()
        print(f"FATAL — spike loader not exposed. lib-status = {lib_status}")
        browser.close(); httpd.shutdown(); sys.exit(1)
    lib_status = page.locator("#lib-status").inner_text()
    print(f"[playwright] {lib_status.strip()}")

    # Load the PDF — fetch via same origin then call exposed loader directly.
    print(f"[playwright] fetching PDF + calling window.__spikeLoadPdfBuffer")
    import shutil
    serve_pdf = SANDBOX / "_drive_phang.pdf"
    shutil.copy(str(PDF_PATH), str(serve_pdf))
    try:
        ok = page.evaluate("""async () => {
            if (!window.__spikeLoadPdfBuffer) return {error: 'loader not exposed'};
            const resp = await fetch('/_drive_phang.pdf');
            const buf  = await resp.arrayBuffer();
            const ok = await window.__spikeLoadPdfBuffer(buf, 'phang.pdf');
            return {ok, bytes: buf.byteLength};
        }""")
        print(f"  load result = {ok}")
    finally:
        try: serve_pdf.unlink()
        except: pass
    # Wait for first render to settle — longer timeout, log progress on failure
    try:
        page.wait_for_function(
            "document.getElementById('render-info').textContent.includes('render time')",
            timeout=30_000)
    except Exception as e:
        print(f"[playwright] wait for render TIMED OUT — current state:")
        st = page.evaluate("""() => ({
            lib: document.getElementById('lib-status').innerText,
            render: document.getElementById('render-info').innerText,
            mode: document.getElementById('mode-info').innerText,
            mem: document.getElementById('mem-info').innerText,
        })""")
        for k,v in st.items():
            print(f"  {k}: {v[:200]}")
        print("aborting.")
        browser.close(); httpd.shutdown(); sys.exit(1)
    time.sleep(0.5)

    # CLIPPED mode is default. Test each zoom + rotation combo.
    for mode in ["clipped", "full"]:
        print(f"\n=== mode = {mode} ===")
        page.locator(f".m[data-m='{mode}']").click()
        time.sleep(0.4)
        for z in ZOOMS:
            # FULL mode: skip extreme zooms that would crash the browser.
            if mode == "full" and z > 5:
                results.append({"mode": mode, "zoom": z, "rot": 0,
                                "skipped": True, "reason": "would crash >5× in FULL"})
                continue
            page.locator(f".z[data-z='{z}']").click()
            time.sleep(0.6 if z <= 10 else 1.2)   # give render time
            try:
                page.wait_for_function(
                    "document.getElementById('render-info').textContent.includes('render time')",
                    timeout=10_000)
            except:
                results.append({"mode": mode, "zoom": z, "rot": 0,
                                "skipped": False, "render_failed": True})
                continue

            status = page.evaluate("""() => ({
                contract:    document.getElementById('contract').innerText,
                mem:         document.getElementById('mem-info').innerText,
                render:      document.getElementById('render-info').innerText,
                pan:         document.getElementById('pan-info').innerText
            })""")

            # parse out the contract verdict + delta + memory
            contract_pass = "contract PASS" in status["contract"]
            delta_match = [ln for ln in status["contract"].split("\n") if "delta" in ln.lower()]
            mem_match = [ln for ln in status["mem"].split("\n") if "MB" in ln]
            render_ms_match = [ln for ln in status["render"].split("\n") if "render time" in ln.lower()]

            row = {
                "mode": mode, "zoom": z, "rot": 0,
                "contract_pass": contract_pass,
                "delta_line": delta_match[0].strip() if delta_match else "?",
                "mem_line":   mem_match[0].strip() if mem_match else "?",
                "render_line": render_ms_match[0].strip() if render_ms_match else "?",
            }
            results.append(row)
            print(f"  zoom={z:4d}× rot=0  {'✓' if contract_pass else '✗'}  {row['mem_line']}  {row['render_line']}")

            # screenshot this combo
            page.screenshot(path=str(OUT_DIR / f"{mode}_zoom{z}_rot0.png"),
                            full_page=False)

    # Now test rotation at zoom=5 in clipped mode (most useful contract check)
    print(f"\n=== rotation sweep at zoom=5, mode=clipped ===")
    page.locator(f".m[data-m='clipped']").click()
    time.sleep(0.3)
    page.locator(f".z[data-z='5']").click()
    time.sleep(0.6)
    for r in ROTS:
        page.locator(f".r[data-r='{r}']").click()
        time.sleep(0.7)
        status = page.evaluate("""() => ({
            contract: document.getElementById('contract').innerText
        })""")
        contract_pass = "contract PASS" in status["contract"]
        delta_match = [ln for ln in status["contract"].split("\n") if "delta" in ln.lower()]
        results.append({
            "mode": "clipped", "zoom": 5, "rot": r,
            "contract_pass": contract_pass,
            "delta_line": delta_match[0].strip() if delta_match else "?"
        })
        print(f"  zoom=5× rot={r:3d}°  {'✓' if contract_pass else '✗'}  {delta_match[0].strip() if delta_match else ''}")
        page.screenshot(path=str(OUT_DIR / f"clipped_zoom5_rot{r}.png"))

    browser.close()

httpd.shutdown()

# === Summary ===
print("\n=== SUMMARY ===")
print(f"  total combos tested: {len(results)}")
passes = [r for r in results if r.get("contract_pass")]
fails  = [r for r in results if "contract_pass" in r and not r["contract_pass"]]
skips  = [r for r in results if r.get("skipped")]
print(f"  contract PASS: {len(passes)} / {len(results) - len(skips)}")
print(f"  contract FAIL: {len(fails)}")
print(f"  skipped (FULL >5×): {len(skips)}")

if fails:
    print("\n  Failures:")
    for f in fails:
        print(f"    {f}")

with open(OUT_DIR / "results.json", "w") as fh:
    json.dump(results, fh, indent=2, ensure_ascii=False)
print(f"\n  → {OUT_DIR}/results.json")
print(f"  → screenshots in {OUT_DIR}/")
