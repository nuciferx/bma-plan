"""
SPIKE: lite-pdf-render-quality — render the SAME PDF page in 4 configurations
so the HTML viewer can compare them side-by-side at V.k=1.0 and V.k=2.0.

Run once from repo root:
    python3.11 lite/sandbox/invent-lite-pdf-render-quality/render_variants.py

Outputs into the same directory:
    phang_p01_scale1.5_jpegQ88.jpg   (current lite — baseline)
    phang_p01_scale3.0_jpegQ88.jpg   (Approach A — DPR=2, scale=RS*2)
    phang_p01_scale1.5_png.png       (Approach B — lossless, base scale)
    phang_p01_scale3.0_png.png       (Approach A+B — DPR=2 lossless)
    stats.json                    (bytes + encode_ms per variant)

PDF used: 20250616_RAMA4 APARTMENT PERMIT rev 1.pdf (page 3, the floor plan page).
"""
import fitz, json, time, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
PDF  = pathlib.Path("/Users/nucifer/Downloads/ผัง.pdf")   # user-supplied test PDF (2026-05-27)
OUT  = pathlib.Path(__file__).resolve().parent
PAGE_IDX = 0  # 0-based -> page 1 (only page in this file)

VARIANTS = [
    {"name": "phang_p01_scale1.5_jpegQ88",  "scale": 1.5, "fmt": "jpeg", "q": 88, "ext": ".jpg"},
    {"name": "phang_p01_scale3.0_jpegQ88",  "scale": 3.0, "fmt": "jpeg", "q": 88, "ext": ".jpg"},
    {"name": "phang_p01_scale1.5_png",      "scale": 1.5, "fmt": "png",  "q": None, "ext": ".png"},
    {"name": "phang_p01_scale3.0_png",      "scale": 3.0, "fmt": "png",  "q": None, "ext": ".png"},
    {"name": "phang_p01_scale3.0_jpegQ95",  "scale": 3.0, "fmt": "jpeg", "q": 95, "ext": ".jpg"},
]

def main():
    if not PDF.exists():
        raise SystemExit(f"PDF not found: {PDF}")
    doc = fitz.open(str(PDF))
    page = doc[PAGE_IDX]
    print(f"PDF: {PDF.name}")
    print(f"Page {PAGE_IDX+1} rect: {page.rect} rotation={page.rotation}")
    print()
    stats = {}
    for v in VARIANTS:
        t0 = time.perf_counter()
        mat = fitz.Matrix(v["scale"], v["scale"])
        pix = page.get_pixmap(matrix=mat)
        t_pix = (time.perf_counter() - t0) * 1000
        t0 = time.perf_counter()
        if v["fmt"] == "jpeg":
            data = pix.tobytes("jpeg", jpg_quality=v["q"])
        else:
            data = pix.tobytes("png")
        t_enc = (time.perf_counter() - t0) * 1000
        out_path = OUT / (v["name"] + v["ext"])
        out_path.write_bytes(data)
        stats[v["name"]] = {
            "scale":      v["scale"],
            "fmt":        v["fmt"],
            "quality":    v["q"],
            "pix_w":      pix.width,
            "pix_h":      pix.height,
            "bytes":      len(data),
            "pix_ms":     round(t_pix, 1),
            "encode_ms":  round(t_enc, 1),
            "total_ms":   round(t_pix + t_enc, 1),
            "ext":        v["ext"],
        }
        print(f"  {v['name']:35s} {pix.width:5d}x{pix.height:5d}  "
              f"{len(data)/1024:7.1f} KB  pix={t_pix:5.1f}ms enc={t_enc:5.1f}ms")
    (OUT / "stats.json").write_text(json.dumps(stats, indent=2))
    print("\nstats.json written.")
    # success-criterion check: scale=3.0 encode <= 4x scale=1.5 encode (same format)
    j15 = stats["phang_p01_scale1.5_jpegQ88"]["encode_ms"]
    j30 = stats["phang_p01_scale3.0_jpegQ88"]["encode_ms"]
    ratio = j30 / j15 if j15 > 0 else float("inf")
    print(f"\nSC-4 encode-time ratio scale=3.0/scale=1.5 (jpeg q=88): {ratio:.2f}x  "
          f"({'PASS' if ratio <= 4.0 else 'FAIL'} — budget ≤4×)")

if __name__ == "__main__":
    main()
