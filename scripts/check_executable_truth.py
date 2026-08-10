#!/usr/bin/env python3
"""check_executable_truth.py — U5 "executable truth" gate (DEVELOPMENT_V2_BLUEPRINT §U5).

Turns facts that today live ONLY in prose docs/comments into assertions that FAIL
when they stop being true. Runs inside the run_all_tests.py preflight so it blocks a
test run the moment a documented fact rots — auto-replacing the *mechanical* part of
the quarterly `bma-doc-auditor` drift scan (line caps, "vendored byte-identical",
marker inventory, card status, commit existence).

stdlib only, read-only over the repo (writes nothing but its own stdout). Fast (<5s).

Checks (each = one named assertion; ALL run, failures are collected, a table is
printed, exit 1 on any failure else 0):

  1. line-caps        lite/ui-lite.html <= UI_LITE_CAP; every lite/static/js/*.js
                      <= JS_CAP, EXCEPT files in JS_ALLOWLIST (pre-existing over-cap,
                      each carries a reason + a HARD ceiling it may not exceed — so an
                      allowed file still fails if it GROWS past its ceiling).
  2. measure-vendor   measure-engine.js is the drift-locked vendored copy. A full-file
                      byte compare against a proto/ui.html *region* is NOT the right
                      unit (the file extracts named functions, it is not a contiguous
                      region copy). So this check proves the guard is real instead:
                      (a) test_measure_parity.py EXISTS, (b) it is REGISTERED in the
                      runner's t0 tier, (c) measure-engine.js hashes to a PINNED sha256.
                      The parity test itself enforces byte-identity of each vendored
                      function line vs proto/ui.html on every run; this check guards
                      that that guard still exists and the file has not silently moved.
  3. marker-inventory every guard marker listed in SHIPS.jsonl must have at least one
                      emitter under lite/tests/ OR scripts/ that contains (can emit) it
                      — catches a ledger claiming a guard whose test does not exist.
                      (scripts/ is scanned too so process-tooling ships whose proof
                      marker is emitted from a script, e.g. TRUTH_CHECK_OK, resolve.)
  4. roadmap-recon    delegates to scripts/reconcile_roadmap.py (subprocess); its exit
                      code becomes this check's result. No logic is duplicated.
  5. ships-commits    every commit hash in every SHIPS.jsonl entry's commits[] resolves
                      to a real commit in git (git cat-file). May overlap (4); kept
                      local so this script stands alone.

Usage:
    python scripts/check_executable_truth.py            # run all checks
    python scripts/check_executable_truth.py --verbose  # also list every counted item

Exit 0 = all truths hold; 1 = at least one documented fact is now false.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rp(*parts):
    return os.path.join(ROOT, *parts)


# ---- check-1 config: line caps -------------------------------------------------
UI_LITE = "lite/ui-lite.html"
UI_LITE_CAP = 1200
JS_DIR = "lite/static/js"
JS_CAP = 1000
# Pre-existing over-cap modules. Each is allowed ONLY up to `ceiling` — if it grows
# past that, this check fails and the next sprint MUST extract it. Counts read from
# reality on 2026-07-03 (U5 baseline).
JS_ALLOWLIST = {
    "overview-setup.js": {
        "ceiling": 1080,
        "reason": "pre-existing over-cap (1059 lines at U5 baseline 2026-07-03); "
                  "allowed but hard-capped at 1080 to force extraction before further growth",
    },
}

# ---- check-1b config: max-line-length ratchet (2026-08-10 governance fix) ------
# Line caps alone are gameable: one 855-char line adds unbounded code at zero
# line-cost (the loophole that let ui-lite.html hit 109KB at 1189 "lines").
# Standard pair (ESLint max-lines + max-len): cap line LENGTH too. Retrofit as a
# RATCHET: existing long lines are frozen as baseline; a file may only hold its
# baseline or fewer lines >MAXLEN chars. New files / files not listed = 0 allowed.
# Baseline maintenance: an extraction sprint MAY move baseline between files but
# the TOTAL across all files must never increase (recount + edit this dict in the
# same commit, with the sprint id in a comment).
MAXLEN = 300
MAXLEN_BASELINE = {
    # measured 2026-08-10 (ratchet introduction)
    "ui-lite.html": 10,
    "measure-engine.js": 11,   # vendored + sha-pinned — cannot change by definition
}

# ---- check-2 config: vendored measure engine -----------------------------------
MEASURE_ENGINE = "lite/static/js/measure-engine.js"
# Pinned sha256 of the drift-locked vendored file. If measure-engine.js is edited
# (even a whitespace tweak), this changes and the check fails until re-pinned AND
# test_measure_parity.py has been re-run to prove the edit kept parity with proto.
MEASURE_ENGINE_SHA256 = "d0804e378ca3f8fc0349252ac87fffaeb80e80d81ac53bc65eb1aae40dc5a9de"
PARITY_TEST = "lite/tests/test_measure_parity.py"
RUNNER = "lite/tests/run_all_tests.py"

# ---- check-3/5 config: ledger --------------------------------------------------
SHIPS = "docs/status/SHIPS.jsonl"
TESTS_DIR = "lite/tests"
SCRIPTS_DIR = "scripts"

# ---- check-4 config: delegated roadmap reconcile -------------------------------
RECONCILE = "scripts/reconcile_roadmap.py"

HASH_RE = re.compile(r"^[0-9a-f]{7,40}$")


class Result:
    """One named check's outcome."""

    def __init__(self, key):
        self.key = key
        self.ok = True
        self.summary = ""
        self.items = []       # (label, ok) — printed under --verbose
        self.failures = []    # strings — always printed when the check fails

    def item(self, label, ok=True):
        self.items.append((label, ok))
        return self

    def fail(self, msg):
        self.ok = False
        self.failures.append(msg)
        return self


def count_lines(path):
    with open(path, encoding="utf-8") as f:
        return len(f.read().splitlines())


def read_ships():
    """Return (entries, parse_errors)."""
    entries, errors = [], []
    path = rp(SHIPS)
    if not os.path.exists(path):
        errors.append(f"{SHIPS} not found")
        return entries, errors
    with open(path, encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append((ln, json.loads(line)))
            except json.JSONDecodeError as e:
                errors.append(f"{SHIPS}:{ln} invalid JSON: {e}")
    return entries, errors


# ================================ checks =======================================
def check_line_caps():
    r = Result("line-caps")

    # ui-lite.html
    p = rp(UI_LITE)
    if not os.path.exists(p):
        r.fail(f"{UI_LITE} missing")
    else:
        n = count_lines(p)
        ok = n <= UI_LITE_CAP
        r.item(f"{UI_LITE}: {n}/{UI_LITE_CAP}", ok)
        if not ok:
            r.fail(f"{UI_LITE} = {n} lines > cap {UI_LITE_CAP}")

    # js modules
    jdir = rp(JS_DIR)
    js_files = sorted(f for f in os.listdir(jdir) if f.endswith(".js")) if os.path.isdir(jdir) else []
    for name in js_files:
        n = count_lines(os.path.join(jdir, name))
        allow = JS_ALLOWLIST.get(name)
        if allow:
            ceiling = allow["ceiling"]
            ok = n <= ceiling
            r.item(f"{name}: {n} (allowlisted, ceiling {ceiling}) — {allow['reason']}", ok)
            if not ok:
                r.fail(f"{name} = {n} lines > allowlist ceiling {ceiling} "
                       f"(pre-existing over-cap file GREW; extract a region next sprint)")
        else:
            ok = n <= JS_CAP
            r.item(f"{name}: {n}/{JS_CAP}", ok)
            if not ok:
                r.fail(f"{name} = {n} lines > cap {JS_CAP} "
                       f"(add to JS_ALLOWLIST with a reason + ceiling, or extract a region)")

    kept = sum(1 for _, ok in r.items if ok)
    r.summary = f"{kept}/{len(r.items)} files within cap ({len(JS_ALLOWLIST)} allowlisted)"
    return r


def check_maxlen_ratchet():
    r = Result("maxlen-ratchet")
    targets = []
    ui = rp(UI_LITE)
    if os.path.exists(ui):
        targets.append((os.path.basename(UI_LITE), ui))
    jdir = rp(JS_DIR)
    if os.path.isdir(jdir):
        for name in sorted(f for f in os.listdir(jdir) if f.endswith(".js")):
            targets.append((name, os.path.join(jdir, name)))

    total_over = 0
    for name, path in targets:
        with open(path, encoding="utf-8") as f:
            n = sum(1 for line in f if len(line.rstrip("\n")) > MAXLEN)
        allowed = MAXLEN_BASELINE.get(name, 0)
        ok = n <= allowed
        total_over += n
        if n or allowed:
            r.item(f"{name}: {n} lines >{MAXLEN} chars (baseline {allowed})", ok)
        if not ok:
            r.fail(f"{name}: {n} lines exceed {MAXLEN} chars > baseline {allowed} "
                   f"(ratchet: split the line or extract; never add new long lines)")

    r.summary = (f"{total_over} long lines across {len(targets)} files, all within ratchet baseline"
                 if r.ok else "new over-length lines introduced")
    return r


def check_measure_vendor():
    r = Result("measure-vendor")

    # (a) parity test exists
    pt = rp(PARITY_TEST)
    if os.path.exists(pt):
        r.item(f"{PARITY_TEST} exists", True)
    else:
        r.fail(f"{PARITY_TEST} missing — the byte-identity drift guard is gone")

    # (b) parity test registered in runner t0 tier
    runner = rp(RUNNER)
    registered = False
    if os.path.exists(runner):
        src = open(runner, encoding="utf-8").read()
        # crude but robust: name appears inside a TIERS["t0"] context / anywhere in runner
        registered = "test_measure_parity.py" in src
    if registered:
        r.item("test_measure_parity.py registered in run_all_tests.py (t0 tier)", True)
    else:
        r.fail("test_measure_parity.py NOT referenced in run_all_tests.py — "
               "guard would not run in the pyramid")

    # (c) measure-engine.js pinned hash
    me = rp(MEASURE_ENGINE)
    if not os.path.exists(me):
        r.fail(f"{MEASURE_ENGINE} missing")
    else:
        digest = hashlib.sha256(open(me, "rb").read()).hexdigest()
        ok = digest == MEASURE_ENGINE_SHA256
        r.item(f"{MEASURE_ENGINE} sha256 = {digest}", ok)
        if not ok:
            r.fail(f"{MEASURE_ENGINE} hash changed\n"
                   f"      pinned : {MEASURE_ENGINE_SHA256}\n"
                   f"      actual : {digest}\n"
                   f"      -> the vendored engine was edited. Re-run test_measure_parity.py "
                   f"to prove it still matches proto/ui.html, THEN re-pin MEASURE_ENGINE_SHA256.")

    r.summary = "parity guard present + registered + engine hash pinned" if r.ok else "vendored-engine guard broken"
    return r


def check_marker_inventory():
    r = Result("marker-inventory")
    entries, errors = read_ships()
    for e in errors:
        r.fail(e)

    guards = set()
    for _, d in entries:
        for g in d.get("guards", []) or []:
            guards.add(g)

    # collect all emitter source once — lite tests AND process-tooling scripts
    # (process-tooling ships emit their proof marker from scripts/, e.g. TRUTH_CHECK_OK)
    sources = {}
    for d in (TESTS_DIR, SCRIPTS_DIR):
        sdir = rp(d)
        if not os.path.isdir(sdir):
            continue
        for name in os.listdir(sdir):
            if name.endswith(".py"):
                try:
                    sources[f"{d}/{name}"] = open(os.path.join(sdir, name), encoding="utf-8").read()
                except OSError:
                    pass

    for g in sorted(guards):
        emitters = [name for name, src in sources.items() if g in src]
        ok = bool(emitters)
        r.item(f"{g} -> {emitters if emitters else 'NO SOURCE EMITS THIS'}", ok)
        if not ok:
            r.fail(f"guard '{g}' is claimed in SHIPS.jsonl but no test under {TESTS_DIR}/ "
                   f"or script under {SCRIPTS_DIR}/ contains it")

    r.summary = f"{len(guards)} guard markers, all have an emitting test" if r.ok \
        else f"{len(guards)} guards, {sum(1 for _, ok in r.items if not ok)} without a test"
    return r


def check_roadmap_recon():
    r = Result("roadmap-recon")
    script = rp(RECONCILE)
    if not os.path.exists(script):
        r.fail(f"{RECONCILE} not found — cannot reconcile roadmap")
        r.summary = "reconcile script missing"
        return r
    proc = subprocess.run([sys.executable, script], capture_output=True, text=True)
    r._recon_output = (proc.stdout or "") + (proc.stderr or "")  # for --verbose
    if proc.returncode == 0:
        r.item("reconcile_roadmap.py exit 0 (roadmap/ledger consistent)", True)
        r.summary = "roadmap reconciled clean"
    else:
        r.fail(f"reconcile_roadmap.py exited {proc.returncode} (roadmap/ledger drift — "
               f"run `python {RECONCILE}` for the findings)")
        r.summary = "roadmap reconcile FAILED"
    return r


def check_ships_commits():
    r = Result("ships-commits")
    entries, errors = read_ships()
    for e in errors:
        r.fail(e)

    pairs = []  # (ship_id, hash)
    for _, d in entries:
        sid = d.get("id", "?")
        for h in d.get("commits", []) or []:
            pairs.append((sid, h))

    # invalid-shaped hashes fail immediately
    good = []
    for sid, h in pairs:
        if HASH_RE.match(h):
            good.append((sid, h))
        else:
            r.fail(f"ship {sid}: '{h}' is not a valid commit-hash shape")

    # batch existence query
    uniq = sorted({h for _, h in good})
    missing = set()
    if uniq:
        query = "\n".join(h + "^{commit}" for h in uniq) + "\n"
        try:
            p = subprocess.run(["git", "-C", ROOT, "cat-file", "--batch-check"],
                               input=query, capture_output=True, text=True)
            for h, out in zip(uniq, p.stdout.splitlines()):
                if " commit " not in out:
                    missing.add(h)
        except FileNotFoundError:
            r.fail("git not found — cannot verify SHIPS commit existence")

    for sid, h in good:
        ok = h not in missing
        r.item(f"{sid}: {h}", ok)
        if not ok:
            r.fail(f"ship {sid}: commit {h} does not exist in git")

    r.summary = f"{len(good)} commits across {len(entries)} ships, all exist" if r.ok \
        else f"{len(missing)} missing / bad commit hashes"
    return r


# ================================ driver =======================================
CHECKS = [
    ("line-caps", check_line_caps),
    ("maxlen-ratchet", check_maxlen_ratchet),
    ("measure-vendor", check_measure_vendor),
    ("marker-inventory", check_marker_inventory),
    ("roadmap-recon", check_roadmap_recon),
    ("ships-commits", check_ships_commits),
]


def main():
    ap = argparse.ArgumentParser(description="U5 executable-truth gate")
    ap.add_argument("--verbose", action="store_true", help="list every counted item per check")
    args = ap.parse_args()

    results = []
    for _, fn in CHECKS:
        try:
            results.append(fn())
        except Exception as ex:  # a broken check must fail loudly, not pass silently
            r = Result(fn.__name__)
            r.fail(f"check crashed: {ex!r}")
            r.summary = "check crashed"
            results.append(r)

    print("== EXECUTABLE TRUTH (DEVELOPMENT_V2_BLUEPRINT U5) ==\n")
    name_w = max(len(r.key) for r in results)
    for r in results:
        tag = "PASS" if r.ok else "FAIL"
        print(f"  [{tag}] {r.key.ljust(name_w)}  {r.summary}")
        if args.verbose:
            for label, ok in r.items:
                print(f"           {'.' if ok else 'x'} {label}")
            recon_out = getattr(r, "_recon_output", "")
            if recon_out:
                for line in recon_out.rstrip().splitlines():
                    print(f"             | {line}")

    failed = [r for r in results if not r.ok]
    if failed:
        print("\n-- FAILURES --")
        for r in failed:
            for msg in r.failures:
                print(f"  [{r.key}] {msg}")
        print(f"\nTRUTH_CHECK_FAIL ({len(failed)}/{len(results)} checks failed)")
        return 1
    print(f"\nTRUTH_CHECK_OK ({len(results)}/{len(results)} checks passed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
