"""
run_all_tests.py — one-shot runner for the entire lite test suite.

Discovers every lite/tests/test_*.py, runs each as its own process (the lite
convention: standalone script, prints MARKER_OK / exits 1), and prints a
summary table + final verdict. Fills the "no aggregate runner" gap from the
2026-07-02 audit (NEXT_ACTIONS card: all-tests runner).

Also runs a PREFLIGHT before anything else (NEXT_ACTIONS card: free-space
preflight): the 2026-07-02 incident showed that when C: fills up, Google
Drive File Stream cannot hydrate files and every read on the repo drive
fails with ENOSPC — tests then fail confusingly or corrupt state. The
preflight fails fast with a clear message instead.

Usage:
    py -3 lite/tests/run_all_tests.py                 # run everything
    py -3 lite/tests/run_all_tests.py --tier t0       # math-only tier (~seconds, no browser)
    py -3 lite/tests/run_all_tests.py --tier t1       # server-endpoint tier (requests, no Playwright)
    py -3 lite/tests/run_all_tests.py --filter cfss   # substring filter
    py -3 lite/tests/run_all_tests.py --fail-fast     # stop on first failure
    py -3 lite/tests/run_all_tests.py --timeout 600   # per-test seconds

Tiers (DEVELOPMENT_V2_BLUEPRINT U2 — test pyramid):
    t0 = pure measure-math via Node (parity + property-based) — run on EVERY change
    t1 = HTTP endpoint tests (requests, no browser)
    t2 = everything else (Playwright UI) — default `all` includes every tier

Exit code: 0 only if preflight passes AND every test exits 0.
Prints LITE_RUN_ALL_OK / LITE_RUN_ALL_FAIL as the last line.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
MIN_FREE_GB = 2.0

MARKER_RE = re.compile(r"\b[A-Z][A-Z0-9_]*_(?:OK|FAIL)\b")

# V2 test pyramid (DEVELOPMENT_V2_BLUEPRINT U2). t2 = everything not listed.
TIERS = {
    "t0": {  # measure math through Node — no server, no browser
        "test_measure_parity.py",
        "test_pbt_measure.py",
    },
    "t1": {  # server endpoints via requests — uvicorn but no Playwright
        "test_export_endpoints.py",
        "test_case_lock.py",
    },
}


def preflight():
    """Fail fast on the known environment killers. Returns list of problems."""
    problems = []

    # 1. Free space — repo drive AND system drive (Drive File Stream cache
    #    lives on the system drive; if it is full, reads on the repo drive
    #    fail with ENOSPC even when the repo drive itself has space).
    checked = set()
    targets = [str(TESTS_DIR)]
    if os.name == "nt":
        targets.append(os.environ.get("SystemDrive", "C:") + "\\")
    for t in targets:
        try:
            anchor = Path(t).resolve().anchor or str(t)
            if anchor in checked:
                continue
            checked.add(anchor)
            free_gb = shutil.disk_usage(t).free / 1e9
            if free_gb < MIN_FREE_GB:
                problems.append(
                    f"low disk space on {anchor} ({free_gb:.1f} GB free < {MIN_FREE_GB} GB) — "
                    "Google Drive File Stream needs system-drive cache space; "
                    "clear caches (npm/pip/Temp) before running tests"
                )
        except OSError as ex:
            problems.append(f"cannot stat disk {t}: {ex}")

    # 2. Required runtime deps for the suite.
    for mod, hint in [
        ("uvicorn", "pip install uvicorn"),
        ("playwright", "pip install playwright && playwright install chromium"),
        ("fitz", "pip install pymupdf"),
    ]:
        try:
            __import__(mod)
        except ImportError:
            problems.append(f"missing dependency '{mod}' ({hint})")

    # 3. Node.js — required by test_measure_parity (drift gate).
    if shutil.which("node") is None:
        problems.append("node not on PATH — test_measure_parity (drift gate) will fail")

    return problems


def discover(filter_sub, tier="all"):
    tests = sorted(p for p in TESTS_DIR.glob("test_*.py"))
    if tier == "t0":
        tests = [p for p in tests if p.name in TIERS["t0"]]
    elif tier == "t1":
        tests = [p for p in tests if p.name in TIERS["t1"]]
    elif tier == "t2":
        known = TIERS["t0"] | TIERS["t1"]
        tests = [p for p in tests if p.name not in known]
    if filter_sub:
        tests = [p for p in tests if filter_sub in p.name]
    return tests


def run_one(path, timeout_s):
    t0 = time.time()
    try:
        proc = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout_s, cwd=str(TESTS_DIR.parent.parent),
        )
        dur = time.time() - t0
        out = (proc.stdout or "") + (proc.stderr or "")
        markers = MARKER_RE.findall(out)
        marker = markers[-1] if markers else ""
        return proc.returncode, dur, marker, out
    except subprocess.TimeoutExpired as ex:
        dur = time.time() - t0
        out = ((ex.stdout or b"").decode("utf-8", "replace") if isinstance(ex.stdout, bytes)
               else (ex.stdout or ""))
        return "TIMEOUT", dur, "", out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--filter", default="", help="only run tests whose filename contains this substring")
    ap.add_argument("--tier", default="all", choices=["all", "t0", "t1", "t2"],
                    help="test-pyramid tier (t0=math/Node, t1=endpoints, t2=UI)")
    ap.add_argument("--timeout", type=int, default=420, help="per-test timeout in seconds")
    ap.add_argument("--fail-fast", action="store_true", help="stop at the first failing test")
    args = ap.parse_args()

    print("== PREFLIGHT ==")
    problems = preflight()
    if problems:
        for p in problems:
            print(f"  PREFLIGHT_FAIL: {p}")
        print("LITE_RUN_ALL_FAIL")
        sys.exit(1)
    print("  ok (disk space / deps / node)")

    tests = discover(args.filter, args.tier)
    if not tests:
        print(f"no tests matched filter '{args.filter}' tier '{args.tier}'")
        print("LITE_RUN_ALL_FAIL")
        sys.exit(1)

    print(f"\n== RUNNING {len(tests)} TESTS (tier {args.tier}, timeout {args.timeout}s each) ==")
    results = []
    t_start = time.time()
    for i, path in enumerate(tests, 1):
        code, dur, marker, out = run_one(path, args.timeout)
        ok = code == 0
        status = "PASS" if ok else ("TIMEOUT" if code == "TIMEOUT" else f"FAIL({code})")
        print(f"  [{i:2d}/{len(tests)}] {path.name:42s} {status:10s} {dur:6.1f}s  {marker}", flush=True)
        results.append((path.name, ok, status, dur, marker, out))
        if not ok and args.fail_fast:
            break

    total_dur = time.time() - t_start
    failed = [r for r in results if not r[1]]

    print(f"\n== SUMMARY: {len(results) - len(failed)}/{len(results)} passed in {total_dur/60:.1f} min ==")
    if failed:
        for name, _, status, dur, marker, out in failed:
            print(f"\n---- {name} ({status}) — last 15 output lines ----")
            for line in out.splitlines()[-15:]:
                print(f"  {line}")
        print("\nLITE_RUN_ALL_FAIL")
        sys.exit(1)
    print("LITE_RUN_ALL_OK")


if __name__ == "__main__":
    main()
