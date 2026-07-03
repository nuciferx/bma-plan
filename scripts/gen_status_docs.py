#!/usr/bin/env python3
"""gen_status_docs.py — U3 ledger-first doc generator (stdlib only).

Regenerates the *mechanical* body of four derived status docs from the single
source of truth `docs/status/SHIPS.jsonl`, so `/bma-sprint-finalize` no longer
needs to spawn the ~200-260K-token `bma-sprint-writer` subagent for them.

Targets (only the region between the GEN markers is ever rewritten):
  - PATCH_SUMMARY.md            per-ship id/date/area/summary/commits+subjects/files
  - TEST_RESULT.md              per-ship guard-marker PASS table + closes[]
  - FINAL_REPORT_FOR_CHATGPT.md per-ship one-paragraph outcome
  - docs/status/LATEST_STATUS.md  a machine table (id / date / area / guards / commits)

Human-authored docs (log.md context/lessons, CURRENT_STATUS.md one-liner) are
NEVER touched. Within the 4 targets, everything OUTSIDE the markers
  <!-- GEN:START gen_status_docs -->  ...  <!-- GEN:END -->
is preserved verbatim (header archive-pointer lines, footer archive comments,
LATEST_STATUS prose). On first run, if a file has no markers yet, they are
inserted at the top of the derived section and all other content is kept.

Design rules:
  * Idempotent — output derived purely from the ledger (+ git), never from now().
  * Marker-delimited — hand-written content is never clobbered.
  * Graceful — a missing git object or absent optional field degrades to a note,
    never a crash.

Usage:
  python scripts/gen_status_docs.py --check   # regen in memory, diff vs disk; exit 1 on drift
  python scripts/gen_status_docs.py --write   # write regenerated regions to disk
  (no flag defaults to --check)
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHIPS = os.path.join(ROOT, "docs", "status", "SHIPS.jsonl")

PATCH_SUMMARY = os.path.join(ROOT, "PATCH_SUMMARY.md")
TEST_RESULT = os.path.join(ROOT, "TEST_RESULT.md")
FINAL_REPORT = os.path.join(ROOT, "FINAL_REPORT_FOR_CHATGPT.md")
LATEST_STATUS = os.path.join(ROOT, "docs", "status", "LATEST_STATUS.md")

GEN_START = "<!-- GEN:START gen_status_docs -->"
GEN_END = "<!-- GEN:END -->"


# --------------------------------------------------------------------------- #
# ledger + git helpers
# --------------------------------------------------------------------------- #
def load_ships():
    """Parse SHIPS.jsonl into a list, newest-first (last appended line = Latest)."""
    ships = []
    if not os.path.exists(SHIPS):
        return ships
    with open(SHIPS, encoding="utf-8", newline="") as f:
        for raw in f.read().split("\n"):
            line = raw.strip().strip("\r")
            if not line:
                continue
            try:
                ships.append(json.loads(line))
            except json.JSONDecodeError:
                # skip malformed lines rather than crash
                continue
    ships.reverse()  # append-only ledger: last line is the most recent ship
    return ships


_subject_cache = {}
_files_cache = {}


def git_subject(h):
    if h in _subject_cache:
        return _subject_cache[h]
    subj = ""
    try:
        out = subprocess.run(
            ["git", "-C", ROOT, "log", "--format=%s", "-1", h],
            capture_output=True, text=True, timeout=20,
        )
        if out.returncode == 0:
            subj = out.stdout.strip().split("\n")[0].strip()
    except Exception:
        subj = ""
    _subject_cache[h] = subj
    return subj


def git_files(h):
    if h in _files_cache:
        return _files_cache[h]
    files = []
    try:
        out = subprocess.run(
            ["git", "-C", ROOT, "show", "--name-only", "--format=", h],
            capture_output=True, text=True, timeout=20,
        )
        if out.returncode == 0:
            files = [ln.strip() for ln in out.stdout.split("\n") if ln.strip()]
    except Exception:
        files = []
    _files_cache[h] = files
    return files


def ship_files(ship):
    """Union of files touched across all of a ship's commits, sorted."""
    seen = set()
    for h in ship.get("commits", []):
        for fp in git_files(h):
            seen.add(fp)
    return sorted(seen)


def is_lite(area):
    return "lite" in (area or "").lower()


def fmt_list(items):
    items = [str(i) for i in (items or []) if str(i).strip()]
    return ", ".join(items) if items else "—"


def ship_title(idx, ship):
    """Latest / Previous demotion convention for the top two, plain id after."""
    if idx == 0:
        return f"# Latest: {ship.get('id', '(no id)')}"
    if idx == 1:
        return f"# Previous: {ship.get('id', '(no id)')}"
    return f"# {ship.get('id', '(no id)')}"


# --------------------------------------------------------------------------- #
# per-doc body generators (return a list of LF lines, no surrounding markers)
# --------------------------------------------------------------------------- #
def gen_patch_summary(ships):
    out = []
    for idx, s in enumerate(ships):
        out.append(ship_title(idx, s))
        out.append("")
        out.append(f"Date: {s.get('date', '—')} · Area: {s.get('area', '—')}")
        out.append("")
        out.append(s.get("summary", "").strip() or "_(no summary in ledger)_")
        out.append("")
        # commits + subjects
        commits = s.get("commits", [])
        if commits:
            out.append("**Commits:**")
            for h in commits:
                subj = git_subject(h)
                if subj:
                    out.append(f"- `{h}` — {subj}")
                else:
                    out.append(f"- `{h}` — _(subject unavailable — object not in this checkout)_")
        else:
            out.append("**Commits:** —")
        out.append("")
        # files touched (union across commits, derived from git)
        files = ship_files(s)
        if files:
            out.append("**Files touched:** " + ", ".join(f"`{f}`" for f in files))
        elif commits:
            out.append("**Files touched:** _(unavailable — git objects not in this checkout)_")
        else:
            out.append("**Files touched:** —")
        out.append("")
        out.append(f"**Closes:** {fmt_list(s.get('closes'))}")
        if s.get("docs"):
            out.append("")
            out.append(f"**Docs:** {s['docs']}")
        out.append("")
        out.append("---")
        out.append("")
    if out and out[-1] == "":
        out.pop()
    return out


def gen_test_result(ships):
    out = []
    for idx, s in enumerate(ships):
        out.append(ship_title(idx, s))
        out.append("")
        out.append(f"Date: {s.get('date', '—')} · Area: {s.get('area', '—')}")
        if is_lite(s.get("area", "")):
            out.append("")
            out.append("_lite-only, proto untouched._")
        out.append("")
        guards = s.get("guards", [])
        if guards:
            out.append("| Marker | Result |")
            out.append("|---|---|")
            for g in guards:
                out.append(f"| {g} | PASS |")
        else:
            out.append("_No guard markers — docs / process / research ship (no dedicated marker)._")
        out.append("")
        out.append(f"Closes: {fmt_list(s.get('closes'))}")
        out.append("")
        out.append("---")
        out.append("")
    if out and out[-1] == "":
        out.pop()
    return out


def gen_final_report(ships):
    out = []
    for idx, s in enumerate(ships):
        out.append(f"{ship_title(idx, s)} — {s.get('area', '—')}")
        out.append("")
        out.append(f"**Date:** {s.get('date', '—')}")
        out.append("")
        summary = s.get("summary", "").strip() or "_(no summary in ledger)_"
        closes = s.get("closes")
        if closes:
            out.append(f"{summary} Closes: {fmt_list(closes)}.")
        else:
            out.append(summary)
        out.append("")
        out.append("---")
        out.append("")
    if out and out[-1] == "":
        out.pop()
    return out


def gen_latest_status_table(ships):
    out = []
    out.append("## Ship Ledger (generated)")
    out.append("")
    out.append("| id | date | area | guards | commits |")
    out.append("|---|---|---|---|---|")
    for s in ships:
        guards = ", ".join(s.get("guards", [])) or "—"
        commits = ", ".join(f"`{h}`" for h in s.get("commits", [])) or "—"
        out.append(
            f"| {s.get('id', '—')} | {s.get('date', '—')} | {s.get('area', '—')} "
            f"| {guards} | {commits} |"
        )
    return out


# --------------------------------------------------------------------------- #
# marker splice
# --------------------------------------------------------------------------- #
def read_file(path):
    if not os.path.exists(path):
        return "", "\n"
    with open(path, encoding="utf-8", newline="") as f:
        raw = f.read()
    eol = "\r\n" if "\r\n" in raw else "\n"
    return raw, eol


def to_lines(raw):
    """LF-normalized line list."""
    return [ln.rstrip("\r") for ln in raw.split("\n")]


def find_markers(lines):
    start = end = None
    for i, ln in enumerate(lines):
        if ln.strip() == GEN_START:
            start = i
        elif ln.strip() == GEN_END:
            end = i
    if start is not None and end is not None and end > start:
        return start, end
    return None, None


def trailing_footer_start(lines, head_end):
    """Index where the maximal trailing run of {blank, ---, <!--comment} begins.

    Preserves the hand-maintained footer archive-comment block (and its leading
    separator) outside the generated region. Never crosses head_end.
    """
    i = len(lines)
    while i - 1 > head_end:
        s = lines[i - 1].strip()
        if s == "" or s == "---" or s.startswith("<!--"):
            i -= 1
        else:
            break
    return i


def splice_latest_previous(path, body_lines):
    """PATCH_SUMMARY / TEST_RESULT / FINAL_REPORT: header + GEN region + footer."""
    raw, eol = read_file(path)
    lines = to_lines(raw)
    gen_block = [GEN_START, ""] + body_lines + ["", GEN_END]

    start, end = find_markers(lines)
    if start is not None:
        new_lines = lines[:start] + gen_block + lines[end + 1:]
        wrapped = None
    else:
        # first run: head = up to & incl first '---'; footer = trailing comment run
        head_end = -1
        for i, ln in enumerate(lines):
            if ln.strip() == "---":
                head_end = i
                break
        foot_start = trailing_footer_start(lines, head_end)
        head = lines[: head_end + 1]
        footer = lines[foot_start:]
        wrapped = lines[head_end + 1: foot_start]
        new_lines = head + [""] + gen_block + [""] + footer
    return eol.join(new_lines), wrapped


def splice_latest_status(path, body_lines):
    """LATEST_STATUS: insert/replace a GEN machine-table block; keep all prose."""
    raw, eol = read_file(path)
    lines = to_lines(raw)
    gen_block = [GEN_START] + body_lines + [GEN_END]

    start, end = find_markers(lines)
    if start is not None:
        new_lines = lines[:start] + gen_block + lines[end + 1:]
        wrapped = None
    else:
        # first run: insert just before the first '## ' section heading, so the
        # title + intro paragraph above stay hand-owned and all prose below is kept
        anchor = None
        for i, ln in enumerate(lines):
            if ln.startswith("## "):
                anchor = i
                break
        if anchor is None:
            anchor = len(lines)
        new_lines = lines[:anchor] + gen_block + [""] + lines[anchor:]
        wrapped = []  # nothing existing wrapped; pure insertion
    return eol.join(new_lines), wrapped


# --------------------------------------------------------------------------- #
# driver
# --------------------------------------------------------------------------- #
def build_all():
    ships = load_ships()
    results = {}  # path -> (new_text, wrapped_or_None)
    results[PATCH_SUMMARY] = splice_latest_previous(PATCH_SUMMARY, gen_patch_summary(ships))
    results[TEST_RESULT] = splice_latest_previous(TEST_RESULT, gen_test_result(ships))
    results[FINAL_REPORT] = splice_latest_previous(FINAL_REPORT, gen_final_report(ships))
    results[LATEST_STATUS] = splice_latest_status(LATEST_STATUS, gen_latest_status_table(ships))
    return ships, results


def current_bytes(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def main():
    mode = "check"
    for a in sys.argv[1:]:
        if a == "--write":
            mode = "write"
        elif a == "--check":
            mode = "check"
        elif a in ("-h", "--help"):
            print(__doc__)
            return 0

    ships, results = build_all()
    if not ships:
        print("[gen_status_docs] WARNING: no ships parsed from SHIPS.jsonl", file=sys.stderr)

    drift = False
    for path, (new_text, wrapped) in results.items():
        rel = os.path.relpath(path, ROOT)
        old_text = current_bytes(path)
        if old_text == new_text:
            print(f"[gen_status_docs] in-sync : {rel}")
            continue
        drift = True
        if mode == "write":
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(new_text)
            note = ""
            if wrapped is not None and wrapped:
                note = f"  (wrapped {len([l for l in wrapped if l.strip()])} pre-existing non-blank line(s) into GEN region)"
            elif wrapped is not None:
                note = "  (inserted fresh GEN markers; no existing content wrapped)"
            print(f"[gen_status_docs] WROTE   : {rel}{note}")
        else:
            print(f"[gen_status_docs] DRIFT   : {rel}")

    if mode == "check" and drift:
        print("[gen_status_docs] --check: DRIFT detected (run with --write)")
        return 1
    print("[gen_status_docs] OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
