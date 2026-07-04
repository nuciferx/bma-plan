"""Eval for lite-layer-menu-ui-fix spike — Approach B (context-scoped panel + global floor search)
now with 3 proportion presets (P1 Compact 190 / P2 Balanced 260 / P3 Anchor 320).

Opens the standalone spike via file://, clicks "Run Eval" (the spike runs the full
3-case suite once PER PRESET, driving interactions through real DOM events — search
input, result click, vis-toggle click — never API injection), waits for
window.__evalResults, prints a per-preset PASS/FAIL table, and captures one
screenshot per preset (100-floor demo data) into artifacts/. Exits 0 only if all
3 cases pass under ALL 3 presets and there were zero page errors.
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HTML = Path(__file__).resolve().parent / "invent-lite-layer-menu-ui-fix.html"
ARTDIR = Path(__file__).resolve().parents[2] / "artifacts" / "invent" / "lite-layer-menu-ui-fix"
ARTDIR.mkdir(parents=True, exist_ok=True)

PRESETS = ["P1", "P2", "P3"]


def main():
    errs = []
    console_logs = []
    with sync_playwright() as pw:
        br = pw.chromium.launch(headless=True)
        pg = br.new_page(viewport={"width": 1200, "height": 900})
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: console_logs.append(m.text))
        pg.goto(HTML.as_uri())
        pg.wait_for_selector("#btn-run-eval")
        pg.click("#btn-run-eval")
        pg.wait_for_function("window.__evalResults && true", timeout=30000)
        results = pg.evaluate("window.__evalResults")
        page_errors = pg.evaluate("window.__pageErrors")

        # one screenshot per preset, same 100-floor demo data (jump to a mid floor
        # so the panel shows a representative "ชั้น 57" layer set)
        pg.evaluate("buildProject(100); renderFloorRail(); jumpToFloor('PF_floor_57')")
        for pid in PRESETS:
            pg.evaluate(f"window.__applyPreset('{pid}')")
            pg.wait_for_timeout(120)  # let layout settle
            pg.locator("#app").screenshot(path=str(ARTDIR / f"proportion-{pid.lower()}.png"))
        pg.evaluate("window.__applyPreset('P2')")  # restore default
        pg.screenshot(path=str(ARTDIR / "spike-b-eval.png"), full_page=True)

        (ARTDIR / "eval-results.json").write_text(
            json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        (ARTDIR / "console.log").write_text("\n".join(console_logs), encoding="utf-8")
        br.close()

    def line(name, ok, detail):
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}\n         {detail}")

    print("\n=== EVAL: lite-layer-menu-ui-fix — Approach B x 3 proportion presets ===")
    all_ok = bool(results["allPass"])
    total_cases = 0
    passed_cases = 0
    for pid in PRESETS:
        pr = results["presets"][pid]
        c1, c2, c3 = pr["case1"], pr["case2"], pr["case3"]
        print(f"\n--- preset {pid} ({'ALL PASS' if pr['allPass'] else 'HAS FAILURES'}) ---")
        line(
            "CASE1 happy — 100-floor perf(<150ms) / DOM(<800) / actions(<=3)",
            c1["pass"],
            f"renderMs={c1['renderMs']:.2f} (exp <150) domNodes={c1['domNodes']} (exp <800) "
            f"actionCount={c1['actionCount']} (exp <=3) foundFloorResult={c1['foundFloorResult']} "
            f"foundVisBtn={c1['foundVisBtn']} jumpedCorrectly={c1['jumpedCorrectly']} toggled={c1['toggled']}",
        )
        line(
            "CASE2 edge — kind-aware order / same-name isolation / zero-orphan",
            c2["pass"],
            f"orderMatches={c2['orderMatches']} namesLiterallyWall={c2['namesLiterallyWall']} "
            f"distinctIds={c2['distinctIds']} isolationOk={c2['isolationOk']} "
            f"orphanCount={c2['orphanCount']}/{c2['objectCount']}",
        )
        if not c2["orderMatches"]:
            print(f"         expected(head/tail)={c2['expectedOrder'][:3]}...{c2['expectedOrder'][-3:]}")
            print(f"         actual  (head/tail)={c2['actualOrder'][:3]}...{c2['actualOrder'][-3:]}")
        line(
            "CASE3 adversarial — v1 round-trip losslessness (additions-only diff)",
            c3["pass"],
            f"orphansAfterLoad={c3['orphansAfterLoad']} diff adds/rems/changes="
            f"{c3['diffAdds']}/{c3['diffRems']}/{c3['diffChanges']} (exp rems=0,changes=0) "
            f"v1ReaderOrphans={c3['v1ReaderOrphans']} v1VisOk={c3['v1VisOk']} v1LockOk={c3['v1LockOk']}",
        )
        for c in (c1, c2, c3):
            total_cases += 1
            passed_cases += 1 if c["pass"] else 0

    if errs:
        print("\n  pageerrors:", errs[:5])
        all_ok = False
    if page_errors:
        print("\n  window.__pageErrors:", page_errors[:5])
        all_ok = False

    print(f"\n  screenshots: {', '.join('proportion-' + p.lower() + '.png' for p in PRESETS)} -> {ARTDIR}")
    print(
        "\n"
        + (
            f"SPIKE_B_OK {passed_cases}/{total_cases} (3 cases x 3 presets)"
            if all_ok
            else f"SPIKE_B_PARTIAL {passed_cases}/{total_cases}"
            + ("  (+page errors)" if (errs or page_errors) else "")
        )
    )
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
