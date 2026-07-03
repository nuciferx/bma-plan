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

The preflight also runs the DEVELOPMENT_V2_BLUEPRINT U5 "executable-truth"
gate (scripts/check_executable_truth.py): line caps, the vendored measure-engine
hash pin, the SHIPS.jsonl marker inventory, roadmap reconcile, and ledger
commit existence. A stale documented fact blocks the run. Skip with
--no-truth-check only if the checker itself is broken.

Usage:
    py -3 lite/tests/run_all_tests.py                 # run everything
    py -3 lite/tests/run_all_tests.py --tier t0       # math-only tier (~seconds, no browser)
    py -3 lite/tests/run_all_tests.py --tier t1       # server-endpoint tier (requests, no Playwright)
    py -3 lite/tests/run_all_tests.py --filter cfss   # substring filter
    py -3 lite/tests/run_all_tests.py --fail-fast     # stop on first failure
    py -3 lite/tests/run_all_tests.py --timeout 600   # per-test seconds
    py -3 lite/tests/run_all_tests.py --changed       # impact-map: only tests hit by changed files (+t0)
    py -3 lite/tests/run_all_tests.py --changed --dry-run              # print selection, run nothing
    py -3 lite/tests/run_all_tests.py --changed --changed-against HEAD~3   # diff vs older ref

Tiers (DEVELOPMENT_V2_BLUEPRINT U2 — test pyramid):
    t0 = pure measure-math via Node (parity + property-based) — run on EVERY change
    t1 = HTTP endpoint tests (requests, no browser)
    t2 = everything else (Playwright UI) — default `all` includes every tier

--changed (DEVELOPMENT_V2_BLUEPRINT U2 — impact map): unions `git diff` (working +
staged) and untracked files, maps each changed SOURCE file through IMPACT_MAP (top
of this file) to a minimal test set, ALWAYS unions the t0 safety net, and runs just
that set. It prints which files were detected, which tests were selected and WHY,
and — critically — any changed source file that matched NO rule (catch-all) so
silent under-selection is visible. A change to a BROAD BLAST RADIUS file
(measure-engine.js / ui-lite.html / server_lite.py / this runner / scripts/) widens
to the whole suite and says why. Mutually exclusive with --tier.

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
REPO_ROOT = TESTS_DIR.parent.parent
TRUTH_CHECK = REPO_ROOT / "scripts" / "check_executable_truth.py"
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


# ---------------------------------------------------------------------------
# IMPACT MAP (DEVELOPMENT_V2_BLUEPRINT U2 — `--changed` mode)
# ---------------------------------------------------------------------------
# Declarative source-glob -> affected-test coupling. `--changed` maps each
# changed source file through this table to a minimal test set (plus the t0
# safety net, ALWAYS). Keep this as data — EXTEND IT whenever you add a new
# module<->test coupling (a new lite/static/js/<x>.js with its own test_<x>.py).
#
# Two rule kinds:
#   {"glob": <fnmatch pat vs repo-root-relative path>, "tests": [<name substrings>], "why": ...}
#       -> selects every discovered test whose FILENAME contains any substring.
#   {"glob": ..., "broad": True, "why": ...}
#       -> BROAD BLAST RADIUS: a foundational file whose edit can break anything.
#          `--changed` widens to the WHOLE suite and says why, so `--changed`
#          never gives false confidence on a core edit.
#
# Globs are matched against forward-slash, repo-root-relative paths
# (e.g. "lite/static/js/measure-engine.js"). Order does not matter — a file
# may match several rules and the selected tests are unioned. A changed SOURCE
# file that matches NO rule falls to the catch-all -> treated as broad + printed
# loudly (no-silent-caps discipline: silent under-selection must be visible).
IMPACT_MAP = [
    # --- broad blast radius (edit -> run everything) --------------------------
    {"glob": "lite/static/js/measure-engine.js", "broad": True,
     "why": "core + vendored measure math; every T0 and every UI measurement depends on it"},
    {"glob": "lite/ui-lite.html", "broad": True,
     "why": "single-file UI shell; essentially every T2 Playwright test loads it"},
    {"glob": "lite/server_lite.py", "broad": True,
     "why": "backend used by every T1 endpoint test and booted by every T2/journey test"},
    {"glob": "lite/launch_lite.py", "broad": True,
     "why": "app launcher; affects any test that boots the server"},
    {"glob": "lite/tests/run_all_tests.py", "broad": True,
     "why": "the runner itself — a change here can mis-select or mis-report any test"},
    {"glob": "scripts/*.py", "broad": True,
     "why": "preflight truth-check / reconcile run scripts/; a foundational edit could let anything pass"},
    {"glob": "lite/static/js/vendor/*", "broad": True,
     "why": "vendored libs (pdfjs / jspreadsheet) — affect render + report broadly"},

    # --- targeted couplings (edit -> just the affected suite + t0) ------------
    {"glob": "lite/static/js/draw-arc.js", "tests": ["arc"],
     "why": "arc drawing -> arc edge + arc parity"},
    {"glob": "lite/static/js/cross-floor-shapes.js", "tests": ["cfss"],
     "why": "cross-floor-shapes model -> all CFSS + cfss parity"},
    {"glob": "lite/static/js/cfss-dialogs.js", "tests": ["cfss"],
     "why": "CFSS dialogs -> CFSS suite"},
    {"glob": "lite/static/js/layer-*.js", "tests": ["layer", "tree", "zorder",
                                                     "b1_", "b2_", "b3_", "b4_", "b5_"],
     "why": "layer system / dnd / move / panel / tree -> layer + B-series + tree suites"},
    {"glob": "lite/static/js/object-agg.js", "tests": ["object_tuples", "rollup", "summary", "tree_"],
     "why": "object aggregation -> object tuples, rollups, summary parity, tree rollup"},
    {"glob": "lite/lite-report.html", "tests": ["report"],
     "why": "report render surface -> report suite"},
    {"glob": "lite/static/js/report-*.js", "tests": ["report"],
     "why": "report edit / vars -> report + report_vars suites"},
    {"glob": "lite/static/js/overview-setup.js", "tests": ["overview", "setup"],
     "why": "overview / setup wizard -> overview + force-setup"},
    {"glob": "lite/static/js/wiz-auto.js", "tests": ["wiz"],
     "why": "auto-wizard -> wiz suite"},
    {"glob": "lite/static/js/page-manager*.js", "tests": ["page_manager", "pm_"],
     "why": "page manager (+ ui) -> page_manager + pm_* suites"},
    {"glob": "lite/static/js/page-renderer.js",
     "tests": ["render", "thumb", "prefetch", "pagecache", "worker", "pdfjs", "warm"],
     "why": "render pipeline -> render / thumb / prefetch / cache / worker / pdfjs suites"},
    {"glob": "lite/static/js/page-rotate.js", "tests": ["rotate", "pagerot"],
     "why": "page rotation -> rotate + rotation-registration"},
    {"glob": "lite/static/js/page-folder-layers.js", "tests": ["page_folder", "pf_"],
     "why": "page-folder layers -> page_folder + pf_* suites"},
    {"glob": "lite/static/js/export-annotate.js", "tests": ["export", "annot"],
     "why": "export + annotation -> export endpoints/submenu + annot suites"},
    {"glob": "lite/static/js/annot-style.js", "tests": ["annot"],
     "why": "annotation styling -> annot suites"},
    {"glob": "lite/static/js/menu-flyout.js", "tests": ["menu"],
     "why": "menu / flyout -> menu suites"},
    {"glob": "lite/static/js/snap-types.js", "tests": ["snap"],
     "why": "snap types -> snap + centerline-snap"},
    {"glob": "lite/static/js/centerline-snap.js", "tests": ["centerline", "snap"],
     "why": "centerline snap -> centerline + snap"},
    {"glob": "lite/static/js/ortho-mode.js", "tests": ["ortho"],
     "why": "ortho mode -> ortho suite"},
    {"glob": "lite/static/js/verify-scale.js", "tests": ["verify_scale"],
     "why": "scale verification -> verify_scale"},
    {"glob": "lite/static/js/cheatsheet.js", "tests": ["cheatsheet"],
     "why": "cheatsheet overlay -> cheatsheet"},
    {"glob": "lite/static/js/empty-hub.js", "tests": ["empty_hub"],
     "why": "empty-state hub -> empty_hub"},
]

# A changed file matching one of these globs is a SOURCE file: if it also matches
# NO IMPACT_MAP rule it must NOT be silently dropped — it triggers the broad
# fallback and is printed as an unmapped source file. Non-source changes (docs,
# images, .gsheet, sandbox artifacts) are reported as ignored, never selected.
SOURCE_GLOBS = [
    "lite/static/js/**",   # ** = any depth (covers vendor/ subdirs)
    "lite/*.py",
    "lite/*.html",
    "scripts/*.py",
]


def _glob_to_re(pat):
    """Slash-aware glob: '*'/'?' stay within one path segment, '**' spans
    segments. (Python's fnmatch lets '*' cross '/', which mis-matches subdirs.)"""
    out, i = [], 0
    while i < len(pat):
        if pat[i:i + 2] == "**":
            out.append(".*")
            i += 2
            if pat[i:i + 1] == "/":
                i += 1
        elif pat[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pat[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pat[i]))
            i += 1
    return re.compile("^" + "".join(out) + "$")


def _match(path, pattern):
    return _glob_to_re(pattern).match(path) is not None


def _is_source(nf):
    return any(_match(nf, g) for g in SOURCE_GLOBS)


def git_changed_files(against="HEAD"):
    """Union of changed files vs `against`: working-tree diff + staged diff +
    untracked. Returns forward-slash, repo-root-relative paths. Empty set if not
    a git repo / git missing."""
    files = set()

    def _run(cmd):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", cwd=str(REPO_ROOT))
            return r.stdout if r.returncode == 0 else ""
        except (OSError, subprocess.SubprocessError):
            return ""

    def _unquote(p):
        p = p.strip()
        if len(p) >= 2 and p[0] == '"' and p[-1] == '"':
            p = p[1:-1]
        return p.replace("\\", "/")

    for out in (_run(["git", "diff", "--name-only", against]),
                _run(["git", "diff", "--name-only", "--staged"])):
        for line in out.splitlines():
            if line.strip():
                files.add(_unquote(line))

    # untracked (?? in porcelain). Skip ignored (!!) and dirs.
    for line in _run(["git", "status", "--porcelain"]).splitlines():
        if line[:2] == "??":
            files.add(_unquote(line[3:]))

    return files


def select_by_impact(changed, all_test_paths):
    """Map changed files -> selected test names via IMPACT_MAP.
    Returns (selected {name: [reasons]}, broad [(file, why)], unmapped [files],
    ignored [files]). t0 tests are ALWAYS included as the safety net."""
    all_names = [p.name for p in all_test_paths]
    all_set = set(all_names)
    selected = {}

    def add(name, reason):
        selected.setdefault(name, [])
        if reason not in selected[name]:
            selected[name].append(reason)

    for n in TIERS["t0"]:
        if n in all_set:
            add(n, "t0 always-run safety net (parity/pbt) — per blueprint U2")

    broad, unmapped, ignored = [], [], []
    for f in sorted(changed):
        nf = f.replace("\\", "/")
        # A changed test file selects itself directly.
        if _match(nf, "lite/tests/test_*.py"):
            base = nf.rsplit("/", 1)[-1]
            if base in all_set:
                add(base, "changed test file itself")
            else:
                ignored.append(f + "  (test file not discoverable)")
            continue
        matched = False
        for rule in IMPACT_MAP:
            if _match(nf, rule["glob"]):
                matched = True
                if rule.get("broad"):
                    broad.append((f, rule["why"]))
                else:
                    for sub in rule["tests"]:
                        for n in all_names:
                            if sub in n:
                                add(n, f"{f}  ->  rule '{rule['glob']}' (substr '{sub}')")
        if not matched:
            if _is_source(nf):
                unmapped.append(f)   # source with no rule -> broad fallback (see caller)
            else:
                ignored.append(f)

    return selected, broad, unmapped, ignored


def truth_check():
    """DEVELOPMENT_V2_BLUEPRINT U5 — executable-truth gate. Runs the read-only
    scripts/check_executable_truth.py and returns a list of problem strings (empty
    == truths hold). Blocks the run if a documented fact (line caps, vendored-engine
    hash, marker inventory, roadmap status, ledger commits) has gone stale."""
    if not TRUTH_CHECK.exists():
        return [f"executable-truth script missing at {TRUTH_CHECK}"]
    proc = subprocess.run(
        [sys.executable, str(TRUTH_CHECK)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if proc.returncode == 0:
        return []
    out = (proc.stdout or "") + (proc.stderr or "")
    # surface only the FAILURES section so preflight stays terse
    lines = out.splitlines()
    tail = lines[lines.index("-- FAILURES --"):] if "-- FAILURES --" in lines else lines[-12:]
    return ["executable-truth check FAILED (run `python scripts/check_executable_truth.py`):"] \
        + ["    " + ln for ln in tail]


def preflight(run_truth_check=True):
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

    # 4. Executable-truth gate (U5) — docs that lie block the run. Runs by DEFAULT;
    #    skippable with --no-truth-check for the rare case the checker itself is broken.
    if run_truth_check:
        problems.extend(truth_check())

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
    ap.add_argument("--no-truth-check", action="store_true",
                    help="skip the U5 executable-truth gate (runs by default)")
    ap.add_argument("--changed", action="store_true",
                    help="impact-map mode: run only tests affected by changed files "
                         "(+ t0 safety net). Mutually exclusive with --tier.")
    ap.add_argument("--changed-against", default="HEAD", metavar="GITREF",
                    help="git ref to diff against for --changed (default HEAD; "
                         "use e.g. HEAD~3 to prove selection over recent commits)")
    ap.add_argument("--dry-run", action="store_true",
                    help="with --changed: print the selection (detected files, chosen "
                         "tests, reasons) and exit 0 WITHOUT running preflight or tests")
    args = ap.parse_args()

    # --changed and --tier are mutually exclusive.
    if args.changed and args.tier != "all":
        print("ERROR: --changed and --tier are mutually exclusive "
              f"(got --tier {args.tier}). --changed derives its own set; drop --tier.")
        print("LITE_RUN_ALL_FAIL")
        sys.exit(2)
    if args.dry_run and not args.changed:
        print("ERROR: --dry-run only applies with --changed.")
        print("LITE_RUN_ALL_FAIL")
        sys.exit(2)

    # --------------------------------------------------------------------- #
    # --changed impact-map selection (computed before preflight so --dry-run
    # can report selection without paying preflight/truth-check cost).
    # --------------------------------------------------------------------- #
    changed_tests = None
    if args.changed:
        all_test_paths = discover(args.filter, "all")
        changed = git_changed_files(args.changed_against)
        selected, broad, unmapped, ignored = select_by_impact(changed, all_test_paths)

        print(f"== IMPACT MAP (--changed, against {args.changed_against}) ==")
        if not changed:
            print("  no changed files detected (clean working tree vs "
                  f"{args.changed_against}) — running t0 safety net only")
        else:
            print(f"  detected {len(changed)} changed file(s):")
            for f in sorted(changed):
                tag = ("SOURCE" if _is_source(f.replace('\\', '/'))
                       else ("TEST" if _match(f.replace('\\', '/'),
                                              "lite/tests/test_*.py") else "other"))
                print(f"      [{tag:6s}] {f}")

        # Broad blast radius (known foundational file) OR an unmapped source file
        # -> widen to the WHOLE suite so --changed never gives false confidence.
        widen = bool(broad) or bool(unmapped)
        if broad:
            print("\n  BROAD BLAST RADIUS — widening to the WHOLE suite because:")
            for f, why in broad:
                print(f"      {f}: {why}")
        if unmapped:
            print("\n  UNMAPPED SOURCE FILE(S) — no impact rule matched (catch-all -> "
                  "widen to whole suite; ADD a rule to IMPACT_MAP):")
            for f in unmapped:
                print(f"      {f}")

        if widen:
            tests = all_test_paths
            print(f"\n  => selecting ALL {len(tests)} tests (broad fallback).")
        else:
            names = set(selected)
            tests = [p for p in all_test_paths if p.name in names]
            print(f"\n  selected {len(tests)} test(s):")
            for p in tests:
                print(f"      {p.name}")
                for reason in selected[p.name]:
                    print(f"          - {reason}")

        if ignored:
            print(f"\n  ignored {len(ignored)} non-impacting change(s): "
                  + ", ".join(ignored[:8]) + (" ..." if len(ignored) > 8 else ""))

        if args.dry_run:
            print("\n  (--dry-run: selection only, nothing executed)")
            print("LITE_RUN_ALL_OK")
            sys.exit(0)
        changed_tests = tests

    print("\n== PREFLIGHT ==")
    problems = preflight(run_truth_check=not args.no_truth_check)
    if problems:
        for p in problems:
            print(f"  PREFLIGHT_FAIL: {p}")
        print("LITE_RUN_ALL_FAIL")
        sys.exit(1)
    print("  ok (disk space / deps / node" + ("" if args.no_truth_check else " / executable-truth") + ")")

    if changed_tests is not None:
        tests = changed_tests
    else:
        tests = discover(args.filter, args.tier)
    if not tests:
        print(f"no tests matched filter '{args.filter}' tier '{args.tier}'")
        print("LITE_RUN_ALL_FAIL")
        sys.exit(1)

    tier_label = "changed" if args.changed else args.tier
    print(f"\n== RUNNING {len(tests)} TESTS (tier {tier_label}, timeout {args.timeout}s each) ==")
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
