"""Eval for lite-page-tagging-workflow spike — Spike C (dual-mode grid: page-order <-> grouped-by-tag,
floor-auto-number Apply, overwrite-confirm, single-undo wrap) + minimal-A (inline JIT banner on a mock
canvas panel).

Opens the standalone spike via file://, clicks "Run Eval" (the spike runs all 3 cases in-page,
driving interactions through real DOM events dispatched inside the page's own JS — click/dblclick/
shift-click/change — never API injection or hardcoded pass values), waits for window.__evalResults,
prints a per-case actual-vs-expected table, captures 3 screenshots (page-order view, grouped view,
JIT banner open), and exits 0 only if all 3 cases pass with zero page errors.
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HTML = Path(__file__).resolve().parent / "invent-lite-page-tagging-workflow.html"
ARTDIR = Path(__file__).resolve().parents[2] / "artifacts" / "invent" / "lite-page-tagging-workflow"
ARTDIR.mkdir(parents=True, exist_ok=True)


def main():
    errs = []
    console_logs = []
    with sync_playwright() as pw:
        br = pw.chromium.launch(headless=True)
        pg = br.new_page(viewport={"width": 1300, "height": 900})
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: console_logs.append(m.text))
        pg.goto(HTML.as_uri())
        pg.wait_for_selector("#btn-run-eval")
        pg.click("#btn-run-eval")
        pg.wait_for_function("window.__evalResults && true", timeout=30000)
        results = pg.evaluate("window.__evalResults")
        page_errors = pg.evaluate("window.__pageErrors")

        # screenshots: page-order view, grouped view, JIT banner open
        pg.evaluate("window.__demoOrder()")
        pg.wait_for_timeout(100)
        pg.screenshot(path=str(ARTDIR / "demo-page-order.png"), full_page=True)

        pg.evaluate("window.__demoGrouped()")
        pg.wait_for_timeout(100)
        pg.screenshot(path=str(ARTDIR / "demo-grouped-by-tag.png"), full_page=True)

        pg.evaluate("window.__demoJIT()")
        pg.wait_for_timeout(100)
        pg.screenshot(path=str(ARTDIR / "demo-jit-banner.png"), full_page=True)

        (ARTDIR / "eval-results.json").write_text(
            json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        (ARTDIR / "console.log").write_text("\n".join(console_logs), encoding="utf-8")
        br.close()

    def line(name, ok, detail):
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}\n         {detail}")

    print("\n=== EVAL: lite-page-tagging-workflow — Spike C + minimal-A ===")
    all_ok = bool(results["allPass"])

    c1 = results["case1"]
    line(
        "CASE1 happy — JIT + range efficiency (actionCount<=8, per-page gate always refuses first)",
        c1["pass"],
        f"actionCount={c1['actionCount']} (exp <=8) floorMap={c1['actualFloorMap']} exp={c1['expectedFloorMap']} "
        f"refusedGenerality={c1['refusedGenerality']} refused1={c1['refused1']} armedAfterJit={c1['armedAfterJit']} "
        f"confirmShown={c1['confirmShown']} allFloorTag={c1['allFloorTag']} refusedAgain={c1['refusedAgain']}",
    )

    c2 = results["case2"]
    line(
        "CASE2 edge — mezzanine mid-range skip-numbering + overwrite-confirm (no silent overwrite)",
        c2["pass"],
        f"mezzMatches={c2['mezzMatches']} actualAfterMezz={c2['actualAfterMezz']} "
        f"confirmShownOnOverlap={c2['confirmShownOnOverlap']} overlapCountShown={c2['overlapCountShown']} "
        f"cancelIsNoOp={c2['cancelIsNoOp']} finalMatches={c2['finalMatches']} actualFinal={c2['actualFinal']}",
    )
    if not c2["mezzMatches"]:
        print(f"         expected={c2['expectedAfterMezz']}")
    if not c2["finalMatches"]:
        print(f"         expected={c2['expectedFinal']}")

    c3 = results["case3"]
    line(
        "CASE3 adversarial — fearless retag (objects preserved, folder remap) + verify-grid + undo deep-equal",
        c3["pass"],
        f"visuallyInFloorGroup={c3['visuallyInFloorGroup']} contentMarkerVisible={c3['contentMarkerVisible']} "
        f"retagFromGridWorks={c3['retagFromGridWorks']} objectsPreserved={c3['objectsPreserved']} "
        f"({c3['objCountBefore12']}->{c3['objCountAfter12']}) folderRemapped={c3['folderRemapped']} "
        f"({c3['folderBefore12']}->{c3['folderAfter12']}) rebucketedLive={c3['rebucketedLive']} "
        f"undoOk={c3['undoOk']} deepEqualRestore={c3['deepEqualRestore']} folderRestored={c3['folderRestored']}",
    )

    total_cases = 3
    passed_cases = sum(1 for c in (c1, c2, c3) if c["pass"])

    if errs:
        print("\n  pageerrors:", errs[:5])
        all_ok = False
    if page_errors:
        print("\n  window.__pageErrors:", page_errors[:5])
        all_ok = False

    print(f"\n{passed_cases}/{total_cases} cases passed. allPass={all_ok}")
    print(f"artifacts written to: {ARTDIR}")

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
