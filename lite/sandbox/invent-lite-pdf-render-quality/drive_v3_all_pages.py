"""
SPIKE v3 driver — full-document speed sweep on the biggest construction PDF.

Loads `251121_CHH_Submission_REV2 - Copy.pdf` (95 pages × A1 2384×1684 pt, 95 MB)
into the v3 PDF.js viewport-clipped spike, then renders every page at zoom 1×
(typical load) and a sampled set at zoom 5× (deep inspection). Records per-page
render time. Prints a summary + saves results.json.

Run from repo root:
    python3.11 lite/sandbox/invent-lite-pdf-render-quality/drive_v3_all_pages.py
"""
import http.server, socketserver, threading, time, json, pathlib, sys, statistics
from playwright.sync_api import sync_playwright

ROOT     = pathlib.Path(__file__).resolve().parents[3]
SANDBOX  = ROOT / "lite" / "sandbox"
PDF_PATH = ROOT / "sandbox" / "251121_CHH_Submission_REV2 - Copy.pdf"
OUT_DIR  = SANDBOX / "invent-lite-pdf-render-quality" / "v3-all-pages-results"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PORT = 8766

# --- start local http server (background) ---
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

httpd = socketserver.TCPServer(("127.0.0.1", PORT), QuietHandler, bind_and_activate=False)
httpd.allow_reuse_address = True
httpd.server_bind()
httpd.server_activate()
import os
os.chdir(str(SANDBOX))
threading.Thread(target=httpd.serve_forever, daemon=True).start()
print(f"[server] http://127.0.0.1:{PORT}/ → {SANDBOX}")
print(f"[pdf]    {PDF_PATH.name} ({PDF_PATH.stat().st_size/1024/1024:.1f} MB)")

# copy PDF into served dir (HTTP server can only serve files under cwd)
import shutil
serve_pdf = SANDBOX / "_drive_chh.pdf"
print(f"[copy]   {PDF_PATH.name} → {serve_pdf.name}")
shutil.copy(str(PDF_PATH), str(serve_pdf))

results_by_page = []

try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1600, "height": 900},
                                  device_scale_factor=2.0)
        page = ctx.new_page()
        page.set_default_timeout(120_000)
        page.on("console", lambda m: None if m.type == "log" else print(f"  [console.{m.type}] {m.text[:160]}"))

        url = f"http://127.0.0.1:{PORT}/invent-lite-pdf-render-quality-pdfjs-v3.html"
        print(f"[playwright] open {url}")
        page.goto(url)
        page.wait_for_function("typeof window.__spikeLoadPdfBuffer === 'function'", timeout=20_000)
        print(f"[playwright] PDF.js ready")

        # Load the big PDF
        print(f"[playwright] feeding 95 MB PDF...")
        t0 = time.perf_counter()
        result = page.evaluate("""async () => {
            const t0 = performance.now();
            const resp = await fetch('/_drive_chh.pdf');
            const buf  = await resp.arrayBuffer();
            const ok   = await window.__spikeLoadPdfBuffer(buf, 'chh.pdf');
            return { ok, bytes: buf.byteLength, ms: Math.round(performance.now() - t0) };
        }""")
        load_ms = round((time.perf_counter() - t0) * 1000)
        print(f"  loaded: {result}  outer={load_ms} ms")
        if not result.get("ok"):
            raise RuntimeError("PDF load failed")

        # Expose helpers in the page for fast per-page driving (avoid clicking 95 times)
        page.evaluate("""() => {
            window.__driveSweep = async (pageNum, zoom) => {
                const pdfjsLib = await import('https://cdn.jsdelivr.net/npm/pdfjs-dist@4.0.379/build/pdf.min.mjs');
                const t0 = performance.now();
                // we use the spike's internal state — peek + render
                window.curPageNum = pageNum;          // not strictly needed; spike owns its own state
                // Switch page via spike's PDF doc directly (we have curPdf in module scope but inaccessible).
                // Workaround: call spike's controls. The spike exposes loader only; we need to drive via clicks
                // but we can also re-call loader with same buffer and then jump pages.
                return { error: 'use button-driving instead' };
            };
        }""")

        # Wait for module-script to expose driver API
        page.wait_for_function("typeof window.__spike === 'object' && window.__spike.pageCount > 0", timeout=20_000)
        total_pages = page.evaluate("() => window.__spike.pageCount")
        print(f"[playwright] total pages = {total_pages}")

        # === Sweep at zoom 1× over all pages ===
        print(f"\n=== Sweep at zoom=1× (typical 'page open' timing) ===")
        page.evaluate("() => window.__spike.setZoom(1)")
        time.sleep(0.3)

        for p in range(1, total_pages + 1):
            ms = page.evaluate(f"() => window.__spike.gotoPage({p})")
            stats = page.evaluate("() => window.__spike.getRenderStats()")
            results_by_page.append({
                "page": p, "zoom": 1, "total_ms": ms,
                "pdf_rect": stats["pdf_view"][2:],
                "canvas_w": stats["canvas_w"], "canvas_h": stats["canvas_h"],
            })
            if p % 10 == 0 or p == 1 or p == total_pages:
                print(f"  page {p:3d}/{total_pages}  total={ms:6.1f}ms  pdf={stats['pdf_view'][2]:.0f}x{stats['pdf_view'][3]:.0f}pt")

        # === Sample pages at zoom 5× ===
        print(f"\n=== Sample pages at zoom=5× (deep-inspect timing) ===")
        page.evaluate("() => window.__spike.setZoom(5)")
        time.sleep(0.3)
        sample_pages = [1, total_pages // 4, total_pages // 2, 3 * total_pages // 4, total_pages]
        z5_results = []
        for p in sample_pages:
            ms = page.evaluate(f"() => window.__spike.gotoPage({p})")
            z5_results.append({"page": p, "zoom": 5, "total_ms": ms})
            print(f"  page {p:3d}/{total_pages} @ zoom 5×  total={ms:6.1f}ms")

        browser.close()

finally:
    try: serve_pdf.unlink()
    except: pass
    httpd.shutdown()

# === SUMMARY ===
print(f"\n=== SUMMARY ===")
print(f"PDF: {PDF_PATH.name}")
print(f"     {PDF_PATH.stat().st_size/1024/1024:.1f} MB, {len(results_by_page)} pages, all 2384×1684 pt A1")

times = [r["total_ms"] for r in results_by_page]
print(f"\nZoom 1× (typical load) — {len(times)} pages timed:")
print(f"  min    = {min(times):.1f} ms")
print(f"  max    = {max(times):.1f} ms")
print(f"  mean   = {statistics.mean(times):.1f} ms")
print(f"  median = {statistics.median(times):.1f} ms")
print(f"  stdev  = {statistics.stdev(times):.1f} ms")
print(f"  p95    = {sorted(times)[int(0.95 * len(times))]:.1f} ms")

# Identify slowest pages
slowest = sorted(results_by_page, key=lambda r: -r["total_ms"])[:5]
print(f"\nSlowest 5 pages:")
for r in slowest:
    print(f"  page {r['page']:3d}  {r['total_ms']:7.1f} ms")

# Zoom 5x stats
print(f"\nZoom 5× (deep inspect) on sampled pages:")
for r in z5_results:
    print(f"  page {r['page']:3d}  {r['total_ms']:7.1f} ms")

out = {
    "pdf": str(PDF_PATH),
    "pdf_size_mb": round(PDF_PATH.stat().st_size / 1024 / 1024, 1),
    "total_pages": len(results_by_page),
    "zoom_1x_stats": {
        "min": min(times), "max": max(times),
        "mean": round(statistics.mean(times), 1),
        "median": round(statistics.median(times), 1),
        "stdev": round(statistics.stdev(times), 1),
        "p95": sorted(times)[int(0.95 * len(times))],
    },
    "by_page_zoom_1x": results_by_page,
    "by_page_zoom_5x": z5_results,
}
with open(OUT_DIR / "results.json", "w") as fh:
    json.dump(out, fh, indent=2)
print(f"\n  → {OUT_DIR}/results.json")
