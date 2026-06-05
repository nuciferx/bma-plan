"""Eval for D2-spike (jspreadsheet-CE + CUSTOM Excel cell-click picker).

Unlike -d-eval.py which only proved the formula engine evaluates strings,
this eval DRIVES THE PICKER VIA DOM EVENTS — opens the editor with a real
dblclick, types '=', dispatches a real mousedown on another cell, and
asserts the editor value got the cell ref inserted. That closes the
"eval saw PASS but UX was broken" gap from the -d.html spike.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HTML = Path(__file__).resolve().parent / "invent-lite-editable-report-d2.html"
TOL = 0.01


def near(a, b):
    try:
        return a is not None and abs(float(a) - b) <= TOL
    except Exception:
        return False


def main():
    res = []
    with sync_playwright() as pw:
        br = pw.chromium.launch(headless=True)
        pg = br.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(HTML.as_uri())
        pg.wait_for_function("window.JSSAPI && true")
        pg.wait_for_timeout(400)

        # =====================================================================
        # CASE 1 — PICKER (the actual claim: =, click B1, +, click B2 → "=B1+B2")
        # =====================================================================
        c1 = pg.evaluate("""() => {
            var A = JSSAPI; A.reset();
            // insert empty subtotal row -> becomes row index 4 (y=4), col B (x=1)
            A.insertSubtotalFormula('รวม', '');
            // open editor on the new B5 cell via real dblclick
            var opened = A.openEditor(1, 4);
            // type '=' to enter formula mode -> picker should activate
            A.typeIntoEditor('=');
            var v1 = A.editorValue();
            var pa = A.pickerActive();
            // click B1 (x=1, y=0) -> picker should insert "B1"
            A.clickCell(1, 0);
            var v2 = A.editorValue();
            // press the '+' operator button (proves op buttons wired)
            A.clickOp('+');
            var v3 = A.editorValue();
            // click B2 (x=1, y=1) -> picker should insert "B2"
            A.clickCell(1, 1);
            var v4 = A.editorValue();
            // commit
            A.commitEditor();
            var finalVal = A.get('B5');
            return {opened: opened, v1: v1, pa: pa, v2: v2, v3: v3, v4: v4, finalVal: finalVal};
        }""")
        ok1 = (
            c1["opened"] is True
            and c1["v1"] == "="
            and c1["pa"] is True
            and c1["v2"] == "=B1"
            and c1["v3"] == "=B1+"
            and c1["v4"] == "=B1+B2"
            and near(c1["finalVal"], 86.93)
        )
        res.append((
            "PICKER  =, click B1, +, click B2 -> '=B1+B2' -> 86.93 (DOM-driven, not string-injection)",
            ok1,
            f"opened={c1['opened']} v1={c1['v1']!r} pickerActive={c1['pa']} "
            f"v2={c1['v2']!r} v3={c1['v3']!r} v4={c1['v4']!r} final={c1['finalVal']} (exp 86.93)",
        ))

        # =====================================================================
        # CASE 2 — PICKER with '-' op and override (matches -d.html EDGE case)
        # Override B1 -> 60 first, then build "=B1-B4" via cell-click; expect 50.
        # =====================================================================
        c2 = pg.evaluate("""() => {
            var A = JSSAPI; A.reset();
            // direct override on B1 -> 60 (skip picker for this part)
            A.setCell('B1', 60);
            // insert subtotal row at index 4
            A.insertSubtotalFormula('รวมหัก', '');
            A.openEditor(1, 4);
            A.typeIntoEditor('=');
            A.clickCell(1, 0);     // B1
            var v1 = A.editorValue();
            A.clickOp('-');
            var v2 = A.editorValue();
            A.clickCell(1, 3);     // B4
            var v3 = A.editorValue();
            A.commitEditor();
            var sb = A.get('B5');
            // now recompute -> override on B1 should stay, but go stale
            A.recompute({0: 48.20});
            return {
                v1: v1, v2: v2, v3: v3,
                sb: sb,
                kept: A.get('B1'),
                stale: A.isStale('B1'),
                sAfter: A.get('B5'),
            };
        }""")
        ok2 = (
            c2["v1"] == "=B1"
            and c2["v2"] == "=B1-"
            and c2["v3"] == "=B1-B4"
            and near(c2["sb"], 50.00)
            and near(c2["kept"], 60.00)
            and c2["stale"] is True
            and near(c2["sAfter"], 50.00)
        )
        res.append((
            "EDGE    picker '-' op + override kept + stale after recompute",
            ok2,
            f"v1={c2['v1']!r} v2={c2['v2']!r} v3={c2['v3']!r} "
            f"sb={c2['sb']} kept={c2['kept']} stale={c2['stale']} sAfter={c2['sAfter']} (exp 50 60 True 50)",
        ))

        # =====================================================================
        # CASE 3 — picker should NOT swallow click on non-numeric column (x=0).
        # Click on label column while editor open with '=' must NOT insert "A1"
        # (column A is text labels — picker only intercepts column B / x=1).
        # =====================================================================
        c3 = pg.evaluate("""() => {
            var A = JSSAPI; A.reset();
            A.insertSubtotalFormula('รวม', '');
            A.openEditor(1, 4);
            A.typeIntoEditor('=');
            A.clickCell(1, 0);   // insert B1 -> "=B1"
            var v1 = A.editorValue();
            A.clickCell(0, 1);   // click on label cell (x=0) -> picker MUST NOT insert "A2"
            var v2 = A.editorValue();
            return {v1: v1, v2: v2};
        }""")
        # Acceptable outcomes for v2:
        #   - editor still open with v2 == "=B1"  (picker ignored x=0; editor stayed)
        #   - editor closed (v2 may be null) AND no A-ref was inserted (jss may commit on outside click)
        # The hard requirement: 'A2' must NEVER appear in any captured value.
        ok3 = (c3["v1"] == "=B1") and (c3["v2"] is None or ("A2" not in (c3["v2"] or "")))
        res.append((
            "GUARD   click on label column (x=0) must NOT inject 'A2' into formula",
            ok3,
            f"after B1 click v1={c3['v1']!r} (exp '=B1'); after label-col click v2={c3['v2']!r} (must not contain 'A2')",
        ))

        # =====================================================================
        # CASE 4 — ADVERSARIAL: picker still builds a CORRECT FORMULA STRING
        # even when an upstream cell holds non-numeric junk. The numeric
        # NaN-resilience of the *evaluator* is a jss-CE library trait (the
        # original -d-eval.py also shows nan for this case) — orthogonal to
        # whether the picker UX works. Split the assertion:
        #   picker:   editor.value must equal '=B1+B3' built via clicks
        #   lib:      subtotal value is honestly captured (may be NaN; that's
        #             handled at the app layer via NaN-guard, not here).
        # =====================================================================
        c4 = pg.evaluate("""() => {
            var A = JSSAPI; A.reset();
            A.setCell('B1', 'abc');
            A.insertSubtotalFormula('รวม', '');
            A.openEditor(1, 4);
            A.typeIntoEditor('=');
            A.clickCell(1, 0);   // B1
            A.clickOp('+');
            A.clickCell(1, 2);   // B3
            var v = A.editorValue();
            A.commitEditor();
            var sub = A.get('B5');
            return {v: v, sub: sub, finite: isFinite(sub)};
        }""")
        # The picker requirement: it builds '=B1+B3' correctly regardless of upstream value.
        ok4 = (c4["v"] == "=B1+B3")
        res.append((
            "ADVERS  picker builds '=B1+B3' even when B1='abc' (lib NaN-eval is captured but not gated)",
            ok4,
            f"picker built v={c4['v']!r} (exp '=B1+B3'); lib evaluated sub={c4['sub']} finite={c4['finite']} (informational — handled by app-layer NaN-guard later)",
        ))

        # =====================================================================
        # CASE 5 — ADVERSARIAL: delete a referenced row (D's KNOWN risk).
        # Capture honestly whether picker-built formulas behave the same as
        # string-injected formulas under deletion (they should — jss has one
        # formula engine; picker is just an input-time helper).
        # =====================================================================
        c5 = pg.evaluate("""() => {
            var A = JSSAPI; A.reset();
            A.insertSubtotalFormula('รวม', '');
            A.openEditor(1, 4);
            A.typeIntoEditor('=');
            A.clickCell(1, 0);   // B1
            A.clickOp('+');
            A.clickCell(1, 2);   // B3
            A.commitEditor();
            var before = A.get('B5');           // 50.45 + 26.16 = 76.61
            A.deleteRow(2);                     // delete row index 2 (B3 / 'ทางเดิน')
            var afterRaw = null, afterProc = null;
            try { afterRaw = A.rawGet('B4'); afterProc = A.get('B4'); }
            catch (e) { afterRaw = 'ERR:' + e; }
            return {before: before, afterRaw: afterRaw, afterProc: afterProc};
        }""")
        ref_ok = (
            c5["afterProc"] is not None
            and str(c5["afterRaw"]).find("#REF") < 0
            and near(c5["before"], 76.61)
        )
        res.append((
            "ADVERS  delete referenced row (jss positional-ref risk) — capture honest behaviour",
            ref_ok,
            f"before(=B1+B3)={c5['before']} (exp 76.61); after delete row3: "
            f"rawCell={c5['afterRaw']!r} processed={c5['afterProc']}",
        ))

        br.close()

    print("\n=== EVAL: D2 (CE + custom Excel cell-click picker) ===")
    all_ok = True
    for n, ok, d in res:
        all_ok = all_ok and ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {n}\n         {d}")
    if errs:
        print("  pageerrors:", errs[:4])
    passed = sum(1 for _, o, _ in res if o)
    total = len(res)
    print(
        "\n"
        + (
            f"D2_SPIKE_OK  {passed}/{total}"
            if all_ok
            else f"D2_SPIKE_PARTIAL  {passed}/{total}  (see FAIL — picker or known-risk surface)"
        )
    )
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
