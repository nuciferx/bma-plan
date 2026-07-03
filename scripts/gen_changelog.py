#!/usr/bin/env python3
"""gen_changelog.py — U6 release-ritual CHANGELOG generator (stdlib only).

Generates CHANGELOG.md from the single source of truth `docs/status/SHIPS.jsonl`,
so cutting a release never needs hand-curation — the ledger already holds every
ship (id / date / area / summary / commits / guards / closes).

Output is grouped by date (newest first), one bullet per ship. Everything the
CHANGELOG needs is derivable from the ledger; there is no separate human step.

Design rules (same contract as gen_status_docs.py):
  * Idempotent — output derived purely from the ledger, never from now().
  * Marker-delimited — only the region between
        <!-- GEN:START gen_changelog -->  ...  <!-- GEN:END -->
    is rewritten; a hand-written preamble above the markers is preserved.
  * Graceful — a malformed ledger line is skipped, never a crash.

Usage:
  python scripts/gen_changelog.py --check   # regen in memory, diff vs disk; exit 1 on drift
  python scripts/gen_changelog.py --write    # write regenerated region to disk
  (no flag defaults to --check)
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHIPS = os.path.join(ROOT, "docs", "status", "SHIPS.jsonl")
CHANGELOG = os.path.join(ROOT, "docs", "CHANGELOG.md")

GEN_START = "<!-- GEN:START gen_changelog -->"
GEN_END = "<!-- GEN:END -->"

PREAMBLE = """# CHANGELOG — BMA-Plan lite

Generated from `docs/status/SHIPS.jsonl` by `scripts/gen_changelog.py` — do not
hand-edit the region between the GEN markers; append a ship line to the ledger
and re-run `python scripts/gen_changelog.py --write`. Anything above the START
marker is hand-written and preserved.

"""


def read_ships():
    ships = []
    if not os.path.exists(SHIPS):
        return ships
    with open(SHIPS, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ships.append(json.loads(line))
            except (ValueError, json.JSONDecodeError):
                continue  # graceful: skip a malformed line
    return ships


def render(ships):
    # newest date first; within a date, preserve ledger order reversed (last appended first)
    by_date = {}
    order = []
    for d in reversed(ships):
        dt = d.get("date", "unknown")
        if dt not in by_date:
            by_date[dt] = []
            order.append(dt)
        by_date[dt].append(d)

    lines = [GEN_START, ""]
    for dt in sorted(order, reverse=True):
        lines.append(f"## {dt}")
        lines.append("")
        for d in by_date[dt]:
            sid = d.get("id", "(no id)")
            area = d.get("area", "")
            summary = d.get("summary", "").strip()
            commits = d.get("commits", []) or []
            guards = d.get("guards", []) or []
            closes = d.get("closes", []) or []
            head = f"- **{sid}**"
            if area:
                head += f" _{area}_"
            lines.append(head)
            if summary:
                lines.append(f"  - {summary}")
            meta = []
            if commits:
                meta.append("commits " + ", ".join(f"`{c}`" for c in commits))
            if guards:
                meta.append("guards " + ", ".join(guards))
            if closes:
                meta.append("closes " + ", ".join(closes))
            if meta:
                lines.append("  - " + " · ".join(meta))
        lines.append("")
    lines.append(GEN_END)
    return "\n".join(lines) + "\n"


def build_full():
    gen = render(read_ships())
    # preserve a hand-written preamble if the file already has one above the marker
    if os.path.exists(CHANGELOG):
        cur = open(CHANGELOG, encoding="utf-8").read()
        if GEN_START in cur:
            pre = cur.split(GEN_START, 1)[0]
            return pre + gen
    return PREAMBLE + gen


def main():
    mode = "--check"
    for a in sys.argv[1:]:
        if a in ("--check", "--write"):
            mode = a
    new = build_full()
    cur = open(CHANGELOG, encoding="utf-8").read() if os.path.exists(CHANGELOG) else None
    if mode == "--write":
        with open(CHANGELOG, "w", encoding="utf-8", newline="") as f:
            f.write(new)
        print(f"[gen_changelog] wrote docs/CHANGELOG.md ({new.count(chr(10))} lines)")
        return 0
    # --check
    if cur == new:
        print("[gen_changelog] in-sync : CHANGELOG.md")
        print("[gen_changelog] OK")
        return 0
    print("[gen_changelog] DRIFT : CHANGELOG.md out of sync with SHIPS.jsonl — run --write")
    return 1


if __name__ == "__main__":
    sys.exit(main())
