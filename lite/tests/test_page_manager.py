#!/usr/bin/env python3
"""
BMA-Plan Lite — page-manager module test (INV-2026-05-29-LPM Slice 1).

Runs the combined E1–E16 eval suite against the PRODUCTION module:
  lite/static/js/page-manager.js

All 17 cases (E1..E16 + E13b) must PASS. Prints LITE_PAGE_MANAGER_OK on
success and exits 0; prints failing case ids and exits 1 on any failure.

Run: python lite/tests/test_page_manager.py
Requires: Node.js on PATH.
"""
import os
import subprocess
import sys


def find_node():
    """Locate node executable, same discovery pattern as test_measure_parity.py."""
    import shutil
    node = shutil.which("node")
    if node:
        return node
    # Windows fallback locations
    for candidate in [
        r"C:\Program Files\nodejs\node.exe",
        r"C:\Program Files (x86)\nodejs\node.exe",
    ]:
        if os.path.isfile(candidate):
            return candidate
    sys.exit("FAIL: node not found on PATH. Install Node.js to run this test.")


HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))   # repo root (bma-plan/)
EVAL_JS  = os.path.join(HERE, "page_manager_eval.js")
MODULE   = os.path.join(ROOT, "lite", "static", "js", "page-manager.js")


def main():
    # Sanity checks
    if not os.path.isfile(MODULE):
        sys.exit("FAIL: production module not found: " + MODULE)
    if not os.path.isfile(EVAL_JS):
        sys.exit("FAIL: eval script not found: " + EVAL_JS)

    node = find_node()

    result = subprocess.run(
        [node, EVAL_JS],
        capture_output=True,
        text=True,
    )

    # Echo node output (pass + fail lines) so the caller can see per-case results.
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)

    if result.returncode != 0:
        sys.exit(1)

    # Double-check the sentinel is present in output.
    if "LITE_PAGE_MANAGER_OK" not in result.stdout:
        print("FAIL: node exited 0 but sentinel LITE_PAGE_MANAGER_OK not found in output",
              file=sys.stderr)
        sys.exit(1)

    print("LITE_PAGE_MANAGER_OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
