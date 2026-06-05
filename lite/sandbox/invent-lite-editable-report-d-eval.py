"""Eval for D-spike (jspreadsheet + Excel formula). Honestly captures jss behavior,
incl. the adversarial delete-row case (D's known formula-ref risk)."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HTML=Path(__file__).resolve().parent/"invent-lite-editable-report-d.html"
TOL=0.01
def near(a,b):
    try: return a is not None and abs(float(a)-b)<=TOL
    except: return False

def main():
    res=[]
    with sync_playwright() as pw:
        br=pw.chromium.launch(headless=True); pg=br.new_page()
        errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
        pg.goto(HTML.as_uri()); pg.wait_for_function("window.JSSAPI&&true"); pg.wait_for_timeout(400)

        # CASE 1 HAPPY
        c1=pg.evaluate("""()=>{var A=JSSAPI;A.reset();
            A.insertSubtotalFormula('รวม','=B1+B2');
            var s1=A.get('B5');
            A.setCell('B1',60); var s2=A.get('B5');
            return {s1:s1,s2:s2};}""")
        ok1=near(c1['s1'],86.93) and near(c1['s2'],96.48)
        res.append(("HAPPY  Excel formula subtotal + edit recomputes",ok1,
                    f"=B1+B2 -> {c1['s1']} (exp 86.93); after B1=60 -> {c1['s2']} (exp 96.48)"))

        # CASE 2 EDGE (override + deduction formula; recompute keeps override + stale)
        c2=pg.evaluate("""()=>{var A=JSSAPI;A.reset();
            A.setCell('B1',60);
            A.insertSubtotalFormula('รวมหัก','=B1-B4');
            var sb=A.get('B5');
            A.recompute({0:48.20});
            return {sb:sb, kept:A.get('B1'), stale:A.isStale('B1'), sAfter:A.get('B5')};}""")
        ok2=near(c2['sb'],50.00) and near(c2['kept'],60.00) and c2['stale'] is True and near(c2['sAfter'],50.00)
        res.append(("EDGE   override+deduction formula; recompute keeps override + stale",ok2,
                    f"=B1-B4 -> {c2['sb']} (exp 50.00); override kept={c2['kept']} (exp 60); "
                    f"stale={c2['stale']} (exp True); after recompute -> {c2['sAfter']} (exp 50.00)"))

        # CASE 3a ADVERSARIAL non-numeric
        c3=pg.evaluate("""()=>{var A=JSSAPI;A.reset();
            A.setCell('B1','abc');
            var v1=A.rawGet('B1'); var p1=A.get('B1');
            A.insertSubtotalFormula('รวม','=B1+B3');
            var sub=A.get('B5');
            return {raw:v1, proc:p1, sub:sub, subFinite:isFinite(A.get('B5'))};}""")
        # pass = non-numeric did not produce a NaN subtotal (sub is finite)
        ok3=bool(c3['subFinite'])
        res.append(("ADVERS non-numeric must not NaN-poison subtotal",ok3,
                    f"B1 raw={c3['raw']!r} processed={c3['proc']}; =B1+B3 -> {c3['sub']} finite={c3['subFinite']}"))

        # CASE 3b ADVERSARIAL delete referenced row (D's KNOWN RISK — capture truth)
        c4=pg.evaluate("""()=>{var A=JSSAPI;A.reset();
            A.insertSubtotalFormula('รวม','=B1+B3');   // refs row1 + row3
            var before=A.get('B5');                     // 50.45+26.16=76.61
            A.deleteRow(2);                             // delete 3rd row (index2 = ทางเดิน/B3)
            var afterRaw=null, afterProc=null;
            try{ afterRaw=A.rawGet('B4'); afterProc=A.get('B4'); }catch(e){ afterRaw='ERR:'+e; }
            return {before:before, afterRaw:afterRaw, afterProc:afterProc};}""")
        # Honest capture: does the formula survive deletion or show #REF / shift?
        ref_ok = c4['afterProc'] is not None and str(c4['afterRaw']).find('#REF')<0
        res.append(("ADVERS delete referenced row (D risk) — does formula survive?",ref_ok,
                    f"before(=B1+B3)={c4['before']} (exp 76.61); after delete row3: rawCell={c4['afterRaw']!r} processed={c4['afterProc']}"))

        br.close()

    print("\n=== EVAL: Approach D (jspreadsheet + Excel formula) ===")
    allok=True
    for n,ok,d in res:
        allok=allok and ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {n}\n         {d}")
    if errs: print("  pageerrors:",errs[:4])
    print("\n"+("D_SPIKE_OK  "+str(sum(1 for _,o,_ in res if o))+"/"+str(len(res)) if allok
                 else "D_SPIKE_PARTIAL  "+str(sum(1 for _,o,_ in res if o))+"/"+str(len(res))+"  (see FAIL — likely the delete-row formula-ref risk)"))
    return 0
if __name__=="__main__": sys.exit(main())
