#!/usr/bin/env python3
"""reconcile_roadmap.py — read-only roadmap/ledger consistency checker.

Dependency-free stdlib. Run from anywhere; paths resolve relative to the repo root
(this file lives in <root>/scripts/).

Checks (all read-only):
  (a) PHASE_INDEX.md status-tables must not contain ✅ rows — those belong in
      ROADMAP_DONE.md. A "status-table" is any markdown pipe-table whose header
      row has a cell named exactly "status". Tables without a status column
      (Discovered-backlog / Known-leftovers) are intentionally NOT checked.
  (b) ids listed in a SHIPS.jsonl entry's "closes" that are STILL present as an
      active (queued / in-flight) row id in PHASE_INDEX.md  -> candidate stale.
  (c) commit hashes referenced in PHASE_INDEX.md, ROADMAP_DONE.md and SHIPS.jsonl
      that do not exist in git (git cat-file).

Exit 1 if any finding, 0 if clean.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHASE_INDEX = os.path.join(ROOT, "docs", "status", "PHASE_INDEX.md")
ROADMAP_DONE = os.path.join(ROOT, "docs", "status", "ROADMAP_DONE.md")
SHIPS = os.path.join(ROOT, "docs", "status", "SHIPS.jsonl")

HASH_RE = re.compile(r"`([0-9a-f]{7,40})`")


def read_lines(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return f.read().split("\n")


def cells(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def is_pipe(line):
    return line.lstrip().startswith("|")


def is_sep(line):
    c = cells(line)
    return bool(c) and all(x and set(x) <= set("-: ") for x in c)


def iter_status_tables(lines):
    """Yield (header_cells, status_idx, [(lineno, cells, raw), ...]) for each
    pipe-table whose header has a 'status' column."""
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if is_pipe(line) and i + 1 < n and is_pipe(lines[i + 1]) and is_sep(lines[i + 1]):
            hdr = cells(line)
            status_idx = next((j for j, h in enumerate(hdr) if h.lower() == "status"), None)
            rows = []
            j = i + 2
            while j < n and is_pipe(lines[j]):
                rows.append((j + 1, cells(lines[j]), lines[j]))
                j += 1
            if status_idx is not None:
                yield hdr, status_idx, rows
            i = j
            continue
        i += 1


def status_cell(hdr, status_idx, row_cells):
    # embedded pipes push early cells; trailing columns stay aligned, so shift.
    idx = status_idx + (len(row_cells) - len(hdr))
    return row_cells[idx] if 0 <= idx < len(row_cells) else ""


def git_missing(hashes):
    """Return the subset of hashes that are NOT commits in git."""
    if not hashes:
        return []
    query = "\n".join(h + "^{commit}" for h in hashes) + "\n"
    try:
        p = subprocess.run(
            ["git", "-C", ROOT, "cat-file", "--batch-check"],
            input=query, capture_output=True, text=True,
        )
    except FileNotFoundError:
        print("  ! git not found — skipping hash existence check")
        return []
    missing = []
    for h, out in zip(hashes, p.stdout.splitlines()):
        # a resolvable commit prints "<sha> commit <size>"; otherwise "... missing"
        if " commit " not in out:
            missing.append(h)
    return missing


def main():
    findings = []
    pi = read_lines(PHASE_INDEX)
    rd = read_lines(ROADMAP_DONE)

    # ---- (a) ✅ rows still in PHASE_INDEX status-tables ----
    active_ids = set()
    a_hits = []
    for hdr, sidx, rows in iter_status_tables(pi):
        for lineno, c, raw in rows:
            if is_sep(raw) or (c and c[0].lower() in ("id", "phase", "item")):
                continue
            st = status_cell(hdr, sidx, c)
            rid = c[0] if c else ""
            if "✅" in st:
                a_hits.append((lineno, rid, st[:60]))
            elif rid:
                active_ids.add(rid)
    if a_hits:
        findings.append("(a) ✅ done rows still in PHASE_INDEX.md (move to ROADMAP_DONE.md):")
        for lineno, rid, st in a_hits:
            findings.append(f"      L{lineno} {rid} :: {st}")

    # ---- (b) SHIPS 'closes' ids still queued in PHASE_INDEX ----
    ships = []
    if os.path.exists(SHIPS):
        for ln, line in enumerate(read_lines(SHIPS), 1):
            line = line.strip()
            if not line:
                continue
            try:
                ships.append((ln, json.loads(line)))
            except json.JSONDecodeError as e:
                findings.append(f"(ships) SHIPS.jsonl:{ln} invalid JSON: {e}")
    b_hits = []
    for ln, s in ships:
        for cid in s.get("closes", []) or []:
            if cid in active_ids:
                b_hits.append((s.get("id", f"line{ln}"), cid))
    if b_hits:
        findings.append("(b) SHIPS 'closes' ids that are STILL queued in PHASE_INDEX (candidate stale):")
        for sid, cid in b_hits:
            findings.append(f"      ship {sid} closes '{cid}' but it is still an active row")

    # ---- (d) queued card ids that already have a fix/feat/test commit ----
    # Root cause found 2026-07-03: fix commits land carrying the card-id in the
    # subject, but the docs follow-up that flips the row status sometimes never
    # happens (3 stale cards found that way). Only fix/feat/test/perf subjects
    # count — docs()/chore() commits that merely FILE a card must not trigger.
    d_hits = []
    for rid in sorted(active_ids):
        if not re.fullmatch(r"[A-Za-z0-9_.:-]{6,60}", rid.strip("`* ")):
            continue
        rid_clean = rid.strip("`* ")
        try:
            out = subprocess.run(
                ["git", "log", "--all", "--oneline", "--grep", rid_clean, "-5"],
                capture_output=True, text=True, cwd=ROOT, timeout=15).stdout
        except (OSError, subprocess.TimeoutExpired):
            continue
        for line in out.splitlines():
            subj = line.split(" ", 1)[1] if " " in line else ""
            if re.match(r"(fix|feat|test|perf)[(!:]", subj):
                d_hits.append((rid_clean, line.strip()))
                break
    if d_hits:
        findings.append("(d) queued cards with a fix/feat/test commit already referencing them (stale?):")
        for rid, line in d_hits:
            findings.append(f"      {rid} :: {line[:90]}")

    # ---- (c) commit hashes that don't exist in git ----
    refs = {}  # hash -> list of "doc" labels
    for label, lines in (("PHASE_INDEX.md", pi), ("ROADMAP_DONE.md", rd)):
        for line in lines:
            for h in HASH_RE.findall(line):
                refs.setdefault(h, set()).add(label)
    for ln, s in ships:
        for h in s.get("commits", []) or []:
            if re.fullmatch(r"[0-9a-f]{7,40}", h):
                refs.setdefault(h, set()).add("SHIPS.jsonl")
    missing = git_missing(sorted(refs))
    if missing:
        findings.append("(c) commit hashes referenced but not found in git:")
        for h in missing:
            findings.append(f"      {h}  (in {', '.join(sorted(refs[h]))})")

    # ---- summary ----
    print("reconcile_roadmap.py")
    print(f"  PHASE_INDEX active status-table rows : {len(active_ids)}")
    print(f"  SHIPS.jsonl entries                  : {len(ships)}")
    print(f"  distinct commit hashes checked       : {len(refs)}")
    if findings:
        print(f"\nFINDINGS ({sum(1 for f in findings if not f.startswith('      '))} groups):")
        for f in findings:
            print("  " + f)
        print("\nRESULT: FAIL")
        return 1
    print("\nRESULT: clean (a/b/c/d all pass)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
