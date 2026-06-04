"""Eval for SPIKE invent-lite-editable-report.html (Approach B).
3 cases: happy + edge(provenance) + adversarial. Outcome-based, tol 0.01.
Run: py -3 lite/sandbox/invent-lite-editable-report-eval.py
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HTML = Path(__file__).resolve().parent / "invent-lite-editable-report.html"
TOL = 0.01

def near(a, b): return a is not None and abs(a - b) <= TOL

def main():
    results = []
    with sync_playwright() as pw:
        br = pw.chromium.launch(headless=True)
        pg = br.new_page()
        pg.goto(HTML.as_uri()); pg.wait_for_function("window.SpikeAPI && true")

        # ---- CASE 1: HAPPY ----
        c1 = pg.evaluate("""() => { var A=SpikeAPI; A.reset();
            A.insertSubtotal('s1','รวม', ['r0','r1']);
            var sub1 = A.subtotal('s1');                 // 50.45+36.48 = 86.93
            A.setOverride('r0', 60.00);
            var sub2 = A.subtotal('s1');                 // 60+36.48 = 96.48
            return {sub1:sub1, sub2:sub2};
        }""")
        ok1 = near(c1['sub1'], 86.93) and near(c1['sub2'], 96.48)
        results.append(('HAPPY  insert-subtotal + edit recomputes', ok1,
                        f"subtotal r0+r1={c1['sub1']} (exp 86.93); after r0->60 ={c1['sub2']} (exp 96.48)"))

        # ---- CASE 2: EDGE (override + deduction sign; refresh must NOT clobber override) ----
        c2 = pg.evaluate("""() => { var A=SpikeAPI; A.reset();
            A.setOverride('r0', 60.00);
            A.insertSubtotal('s2','รวมหัก', ['r0','r3']);   // 60*(+1) + 10*(-1) = 50.00
            var subBefore = A.subtotal('s2');
            A.refresh({r0: 48.20});                          // geometry recompute
            var stale = A.isStale('r0');                     // must be true
            var keptOverride = A.overrideRaw('r0');          // must still be 60 (not clobbered)
            var subAfter = A.subtotal('s2');                 // still uses 60 -> 50.00
            return {subBefore:subBefore, stale:stale, keptOverride:keptOverride, subAfter:subAfter};
        }""")
        ok2 = (near(c2['subBefore'], 50.00) and c2['stale'] is True
               and near(c2['keptOverride'], 60.00) and near(c2['subAfter'], 50.00))
        results.append(('EDGE   override+deduction sign; refresh keeps override + flags stale', ok2,
                        f"sub(before)={c2['subBefore']} (exp 50.00); stale={c2['stale']} (exp True); "
                        f"override kept={c2['keptOverride']} (exp 60.00); sub(after refresh)={c2['subAfter']} (exp 50.00)"))

        # ---- CASE 3: ADVERSARIAL (non-numeric must not NaN-poison; deleted row skipped) ----
        c3 = pg.evaluate("""() => { var A=SpikeAPI; A.reset();
            var rej = A.setOverride('r0', 'abc');            // must be rejected
            var v0  = A.value('r0');                         // unchanged 50.45
            var g   = A.grand();                             // finite number
            A.insertSubtotal('s3','รวม', ['r0','r2']);
            A.deleteRow('r2');                               // r2 gone
            var sub = A.subtotal('s3');                      // skip r2 -> r0 only = 50.45
            var g2  = A.grand();
            return {rejOk:rej.ok, v0:v0, gFinite:isFinite(g), sub:sub, g2Finite:isFinite(g2)};
        }""")
        ok3 = (c3['rejOk'] is False and near(c3['v0'], 50.45) and c3['gFinite'] is True
               and near(c3['sub'], 50.45) and c3['g2Finite'] is True)
        results.append(('ADVERS non-numeric rejected (no NaN) + deleted-row skipped', ok3,
                        f"reject={c3['rejOk']} (exp False); value unchanged={c3['v0']} (exp 50.45); "
                        f"grand finite={c3['gFinite']}; sub skip-deleted={c3['sub']} (exp 50.45); grand2 finite={c3['g2Finite']}"))

        br.close()

    print("\n=== EVAL: invent-lite-editable-report (Approach B) ===")
    allok = True
    for name, ok, detail in results:
        allok = allok and ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        print(f"         {detail}")
    print("\n" + ("EDITABLE_REPORT_SPIKE_OK  3/3" if allok else "EDITABLE_REPORT_SPIKE_FAIL"))
    return 0 if allok else 1

if __name__ == "__main__":
    sys.exit(main())
