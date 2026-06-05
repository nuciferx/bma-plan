"""Eval for D3-spike (CE picker + STABLE-ROW-ID mapper).

Proves the headline fix that closes RESHAPE #1/#2's known risk: jss formulas are
positional, so deleting a row silently shifts references. D3 stores subtotals as
semantic row-ids and re-projects them to current positions after every structural
mutation. This eval DRIVES THE PICKER VIA DOM EVENTS (rule 2 of lite-spike-iterate)
and asserts:
  - the picker still builds formulas (D2 regression)
  - deleting an UNREFERENCED row rewrites the formula AND keeps the value (headline)
  - deleting a REFERENCED row drops only that term + flags it (honest)
  - multi-term mixed-op formula re-projects surviving terms correctly
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HTML = Path(__file__).resolve().parent / "invent-lite-editable-report-d3.html"
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
        # CASE 1 — PICKER regression (D2): =, click B1, +, click B2 -> 86.93
        # =====================================================================
        c1 = pg.evaluate("""() => {
            var A = JSSAPI; A.reset();
            A.insertSubtotalFormula('รวม', '');
            var opened = A.openEditor(1, 4);
            A.typeIntoEditor('=');
            var pa = A.pickerActive();
            A.clickCell(1, 0); var v2 = A.editorValue();
            A.clickOp('+');    var v3 = A.editorValue();
            A.clickCell(1, 1); var v4 = A.editorValue();
            A.commitEditor();
            return {opened: opened, pa: pa, v2: v2, v3: v3, v4: v4, val: A.get('B5')};
        }""")
        ok1 = (c1["opened"] and c1["pa"] and c1["v2"] == "=B1" and
               c1["v3"] == "=B1+" and c1["v4"] == "=B1+B2" and near(c1["val"], 86.93))
        res.append((
            "PICKER  regression: =, click B1, +, click B2 -> '=B1+B2' -> 86.93 (DOM-driven)",
            ok1,
            f"opened={c1['opened']} picker={c1['pa']} v2={c1['v2']!r} v3={c1['v3']!r} v4={c1['v4']!r} val={c1['val']} (exp 86.93)",
        ))

        # =====================================================================
        # CASE 2 — HEADLINE: delete an UNREFERENCED row -> formula re-projects,
        # value is PRESERVED. Build =B1+B3 (r0+r2 = หลังคาA+ทางเดิน = 76.61) via
        # picker, then delete row index1 (r1 / หลังคา B, NOT referenced).
        # Positional naive behaviour (D2): formula stays '=B1+B3', B3 now points at
        # ช่องลิฟต์ (10.00) -> WRONG 60.45. D3 must rewrite to '=B1+B2' -> 76.61.
        # =====================================================================
        c2 = pg.evaluate("""() => {
            var A = JSSAPI; A.reset();
            A.insertSubtotalFormula('รวม', '');
            A.openEditor(1, 4);
            A.typeIntoEditor('=');
            A.clickCell(1, 0);   // B1 = r0
            A.clickOp('+');
            A.clickCell(1, 2);   // B3 = r2
            A.commitEditor();
            var before = A.get('B5');                 // 50.45 + 26.16 = 76.61
            var metaBefore = A.subMetaOf(4);          // [{r0,+},{r2,+}]
            A.deleteRow(1);                           // delete หลังคา B (r1) — unreferenced
            // subtotal row now sits at index 3 (4 rows -> 3 area + ... wait: 3 area left + subtotal = index 3)
            var idsAfter = A.rowIdsSnapshot();
            var subIdx = idsAfter.length - 1;         // subtotal still last
            var rawAfter = A.rawGet('B' + (subIdx + 1));
            var valAfter = A.get('B' + (subIdx + 1));
            return {before: before, metaBefore: metaBefore, idsAfter: idsAfter,
                    rawAfter: rawAfter, valAfter: valAfter};
        }""")
        meta_ok = (c2["metaBefore"] and len(c2["metaBefore"]) == 2 and
                   c2["metaBefore"][0]["id"] == "r0" and c2["metaBefore"][1]["id"] == "r2")
        ok2 = (near(c2["before"], 76.61) and meta_ok and
               c2["rawAfter"] == "=B1+B2" and near(c2["valAfter"], 76.61))
        res.append((
            "STABLE  delete UNREFERENCED row -> formula re-projects '=B1+B3'->'=B1+B2', value PRESERVED 76.61",
            ok2,
            f"before={c2['before']} metaBefore={c2['metaBefore']} idsAfter={c2['idsAfter']} "
            f"rawAfter={c2['rawAfter']!r} (exp '=B1+B2') valAfter={c2['valAfter']} (exp 76.61, naive-positional would be 60.45)",
        ))

        # =====================================================================
        # CASE 3 — REFERENCED-delete: drop only that term + flag. Build =B1+B3
        # (76.61), delete row index2 (r2 / ทางเดิน, IS referenced). Term r2 drops;
        # subtotal = r0 only = 50.45; dropped-flag (red bg) set.
        # =====================================================================
        c3 = pg.evaluate("""() => {
            var A = JSSAPI; A.reset();
            A.insertSubtotalFormula('รวม', '');
            A.openEditor(1, 4);
            A.typeIntoEditor('=');
            A.clickCell(1, 0);   // B1 = r0
            A.clickOp('+');
            A.clickCell(1, 2);   // B3 = r2
            A.commitEditor();
            A.deleteRow(2);      // delete ทางเดิน (r2) — referenced
            var idsAfter = A.rowIdsSnapshot();
            var subIdx = idsAfter.length - 1;
            var rawAfter = A.rawGet('B' + (subIdx + 1));
            var valAfter = A.get('B' + (subIdx + 1));
            var dropped  = A.isDropped('B' + (subIdx + 1));
            return {idsAfter: idsAfter, rawAfter: rawAfter, valAfter: valAfter, dropped: dropped};
        }""")
        ok3 = (c3["rawAfter"] == "=B1" and near(c3["valAfter"], 50.45) and c3["dropped"] is True)
        res.append((
            "STABLE  delete REFERENCED row -> term dropped, subtotal=50.45, red flag set",
            ok3,
            f"idsAfter={c3['idsAfter']} rawAfter={c3['rawAfter']!r} (exp '=B1') "
            f"valAfter={c3['valAfter']} (exp 50.45) dropped={c3['dropped']} (exp True)",
        ))

        # =====================================================================
        # CASE 4 — multi-term mixed-op re-projection. Net formula via API:
        # =B1+B2+B3-B4 = 50.45+36.48+26.16-10.00 = 103.09. Delete row index1
        # (r1 / หลังคา B, referenced). Surviving terms r0,r2,r3 re-project to
        # B1,B2,B3 -> '=B1+B2-B3' = 50.45+26.16-10.00 = 66.61; dropped flag set.
        # =====================================================================
        c4 = pg.evaluate("""() => {
            var A = JSSAPI; A.reset();
            A.insertSubtotalFormula('รวมสุทธิ', '=B1+B2+B3-B4');
            var before = A.get('B5');
            A.deleteRow(1);     // delete หลังคา B (r1) — referenced, +term
            var idsAfter = A.rowIdsSnapshot();
            var subIdx = idsAfter.length - 1;
            var rawAfter = A.rawGet('B' + (subIdx + 1));
            var valAfter = A.get('B' + (subIdx + 1));
            var dropped  = A.isDropped('B' + (subIdx + 1));
            return {before: before, rawAfter: rawAfter, valAfter: valAfter, dropped: dropped};
        }""")
        ok4 = (near(c4["before"], 103.09) and c4["rawAfter"] == "=B1+B2-B3" and
               near(c4["valAfter"], 66.61) and c4["dropped"] is True)
        res.append((
            "STABLE  multi-term mixed-op: delete referenced '+term' -> surviving terms re-project, value 66.61",
            ok4,
            f"before={c4['before']} (exp 103.09) rawAfter={c4['rawAfter']!r} (exp '=B1+B2-B3') "
            f"valAfter={c4['valAfter']} (exp 66.61) dropped={c4['dropped']} (exp True)",
        ))

        # =====================================================================
        # CASE 5 — GUARD regression (D2): click label column (x=0) must NOT inject A2
        # =====================================================================
        c5 = pg.evaluate("""() => {
            var A = JSSAPI; A.reset();
            A.insertSubtotalFormula('รวม', '');
            A.openEditor(1, 4);
            A.typeIntoEditor('=');
            A.clickCell(1, 0);  var v1 = A.editorValue();  // '=B1'
            A.clickCell(0, 1);  var v2 = A.editorValue();  // label col -> must not add A2
            return {v1: v1, v2: v2};
        }""")
        ok5 = (c5["v1"] == "=B1") and (c5["v2"] is None or "A2" not in (c5["v2"] or ""))
        res.append((
            "GUARD   regression: click label col (x=0) must NOT inject 'A2'",
            ok5,
            f"v1={c5['v1']!r} (exp '=B1') v2={c5['v2']!r} (must not contain 'A2')",
        ))

        # =====================================================================
        # CASE 6 — persistence round-trip of semantic ids: build =B1+B3, save,
        # reset+reopen, delete unreferenced row -> still re-projects to 76.61.
        # Proves subMeta survives the localStorage round-trip (build will promote
        # to additive .bmaplan later, but this proves the model serializes).
        # =====================================================================
        c6 = pg.evaluate("""() => {
            var A = JSSAPI; A.reset();
            A.insertSubtotalFormula('รวม', '=B1+B3');   // authored via API path (captures meta)
            var before = A.get('B5');
            // save -> reopen
            document.getElementById('btn-save').click();
            document.getElementById('btn-reopen').click();
            // after reopen, delete unreferenced row1, expect re-project to 76.61
            A.deleteRow(1);
            var ids = A.rowIdsSnapshot();
            var subIdx = ids.length - 1;
            var rawAfter = A.rawGet('B' + (subIdx + 1));
            var valAfter = A.get('B' + (subIdx + 1));
            return {before: before, rawAfter: rawAfter, valAfter: valAfter};
        }""")
        ok6 = (near(c6["before"], 76.61) and c6["rawAfter"] == "=B1+B2" and near(c6["valAfter"], 76.61))
        res.append((
            "PERSIST semantic subMeta survives save/reopen -> delete-unref still re-projects to 76.61",
            ok6,
            f"before={c6['before']} rawAfter={c6['rawAfter']!r} (exp '=B1+B2') valAfter={c6['valAfter']} (exp 76.61)",
        ))

        br.close()

    print("\n=== EVAL: D3 (CE picker + stable-row-id mapper) ===")
    all_ok = True
    for n, ok, d in res:
        all_ok = all_ok and ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {n}\n         {d}")
    if errs:
        print("  pageerrors:", errs[:4])
        all_ok = False
    passed = sum(1 for _, o, _ in res if o)
    total = len(res)
    clean = not errs
    print(
        "\n"
        + (f"D3_SPIKE_OK  {passed}/{total}" if (all_ok and clean)
           else f"D3_SPIKE_PARTIAL  {passed}/{total}" + ("  (+page errors)" if errs else ""))
    )
    return 0 if (all_ok and clean) else 1


if __name__ == "__main__":
    sys.exit(main())
