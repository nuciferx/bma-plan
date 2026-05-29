#!/usr/bin/env python3
"""
BMA-Plan Lite — /apply-page-mutations pure-function test (INV-2026-05-29-LPM Slice 4).

Tests the pure function `_apply_page_mutations` from server_lite directly — no HTTP
server required.  Builds a tiny 5-page in-memory PDF with unique text markers
"P1".."P5" so page identity is checkable via page.get_text().

Cases:
  T1 reorder   — order=[1,2,5,3,4]: page 3 of result == "P5"
  T2 delete    — order=[1,2,4,5]:   "P3" absent; renumber_map has no key 3
  T3 duplicate — order=[1,2,2,3,4,5]: new_count==6; two pages carry "P2"
  T4 combined  — order=[5,1,1,4]:   new_count==4; pages1="P5",2&3="P1",4="P4"
  T5 guard     — empty order raises ValueError from the pure function

Run:  python lite/tests/test_apply_page_mutations.py
Exits 0 + prints LITE_APPLY_MUTATIONS_OK on success; exits 1 on any failure.
"""
import sys
import os

# Make server_lite importable from any CWD.
HERE = os.path.dirname(os.path.abspath(__file__))
LITE = os.path.dirname(HERE)
sys.path.insert(0, LITE)

import fitz  # PyMuPDF

from server_lite import _apply_page_mutations


# ---------------------------------------------------------------------------
# Helper: build a 5-page in-memory PDF with text markers "P1".."P5"
# ---------------------------------------------------------------------------

def _build_test_doc(n_pages=5):
    doc = fitz.open()
    for i in range(1, n_pages + 1):
        page = doc.new_page()
        page.insert_text(fitz.Point(50, 100), f"P{i}", fontsize=24)
    return doc


def _page_texts(doc):
    """Return list of page texts (stripped) in order."""
    return [doc[i].get_text().strip() for i in range(len(doc))]


def _contains_text(doc, text):
    """True if *any* page in doc contains text."""
    return any(text in t for t in _page_texts(doc))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

failures = []


def check(label, condition, detail=""):
    if not condition:
        msg = f"FAIL {label}" + (f": {detail}" if detail else "")
        failures.append(msg)
        print(msg)
    else:
        print(f"  PASS {label}")


# T1 — reorder: [1,2,5,3,4]
def t1():
    doc = _build_test_doc()
    new_doc, rmap, new_count = _apply_page_mutations(doc, [1, 2, 5, 3, 4])
    texts = _page_texts(new_doc)
    check("T1 new_count==5", new_count == 5, f"got {new_count}")
    check("T1 page3==P5", texts[2] == "P5", f"got {texts[2]!r}")
    check("T1 renumber_map[5]==3", rmap.get(5) == 3, f"rmap={rmap}")
    check("T1 renumber_map[3]==4", rmap.get(3) == 4, f"rmap={rmap}")
    check("T1 renumber_map[4]==5", rmap.get(4) == 5, f"rmap={rmap}")
    doc.close(); new_doc.close()


# T2 — delete page 3: [1,2,4,5]
def t2():
    doc = _build_test_doc()
    new_doc, rmap, new_count = _apply_page_mutations(doc, [1, 2, 4, 5])
    check("T2 new_count==4", new_count == 4, f"got {new_count}")
    check("T2 P3 absent", not _contains_text(new_doc, "P3"),
          f"pages: {_page_texts(new_doc)}")
    check("T2 renumber_map no key 3", 3 not in rmap, f"rmap={rmap}")
    check("T2 renumber_map[4]==3", rmap.get(4) == 3, f"rmap={rmap}")
    check("T2 renumber_map[5]==4", rmap.get(5) == 4, f"rmap={rmap}")
    doc.close(); new_doc.close()


# T3 — duplicate page 2: [1,2,2,3,4,5]
def t3():
    doc = _build_test_doc()
    new_doc, rmap, new_count = _apply_page_mutations(doc, [1, 2, 2, 3, 4, 5])
    texts = _page_texts(new_doc)
    check("T3 new_count==6", new_count == 6, f"got {new_count}")
    p2_occurrences = sum(1 for t in texts if "P2" in t)
    check("T3 two pages P2", p2_occurrences == 2, f"found {p2_occurrences}")
    # renumber_map[2] == 2 (first occurrence)
    check("T3 renumber_map[2]==2 (first occ)", rmap.get(2) == 2, f"rmap={rmap}")
    doc.close(); new_doc.close()


# T4 — combined: [5,1,1,4]
def t4():
    doc = _build_test_doc()
    new_doc, rmap, new_count = _apply_page_mutations(doc, [5, 1, 1, 4])
    texts = _page_texts(new_doc)
    check("T4 new_count==4", new_count == 4, f"got {new_count}")
    check("T4 page1==P5", texts[0] == "P5", f"got {texts[0]!r}")
    check("T4 page2==P1", texts[1] == "P1", f"got {texts[1]!r}")
    check("T4 page3==P1 (dup)", texts[2] == "P1", f"got {texts[2]!r}")
    check("T4 page4==P4", texts[3] == "P4", f"got {texts[3]!r}")
    check("T4 P2 absent", not _contains_text(new_doc, "P2"),
          f"pages: {texts}")
    check("T4 P3 absent", not _contains_text(new_doc, "P3"),
          f"pages: {texts}")
    check("T4 renumber_map[5]==1", rmap.get(5) == 1, f"rmap={rmap}")
    check("T4 renumber_map[1]==2 (first occ)", rmap.get(1) == 2, f"rmap={rmap}")
    check("T4 renumber_map[4]==4", rmap.get(4) == 4, f"rmap={rmap}")
    doc.close(); new_doc.close()


# T5 — guard: empty order must raise ValueError
def t5():
    doc = _build_test_doc()
    raised = False
    try:
        _apply_page_mutations(doc, [])
    except ValueError:
        raised = True
    check("T5 empty order raises ValueError", raised)
    doc.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Running T1 (reorder)...")
    t1()
    print("Running T2 (delete)...")
    t2()
    print("Running T3 (duplicate)...")
    t3()
    print("Running T4 (combined)...")
    t4()
    print("Running T5 (guard: empty order)...")
    t5()

    if failures:
        print()
        for f in failures:
            print(f)
        print("LITE_APPLY_MUTATIONS_FAIL")
        sys.exit(1)

    print()
    print("LITE_APPLY_MUTATIONS_OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
