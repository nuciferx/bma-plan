"""build_docs.py — BMA-Plan content bundle builder for /static/docs/

Walks the canonical content sources and emits proto/static/docs/content.json:
  - proto/manual/*.md         → group "Manual / คู่มือผู้ใช้"
  - log.md (## YYYY-MM-DD)    → group "Dev Log / บันทึกการพัฒนา" (most recent 10 sessions)
  - sprints/completed/**      → group "Sprints / Sprint Cards" (most recent 10)
  - docs/process/ANTI_PATTERNS.md → group "Design / Anti-patterns"
  - docs/process/TROUBLESHOOTING.md → group "Design / Troubleshooting"

Wire into /bma-sprint-finalize so the bundle stays fresh. Standalone test:
  python scripts/build_docs.py
  → writes proto/static/docs/content.json

Zero runtime deps. Stdlib only.
"""
from __future__ import annotations
import json
import re
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_FILE = REPO_ROOT / "proto" / "static" / "docs" / "content.json"


def read_md(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def first_h1(body: str, fallback: str) -> str:
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()
    return fallback


def collect_manual() -> list[dict]:
    manual_dir = REPO_ROOT / "proto" / "manual"
    pages = []
    if not manual_dir.exists():
        return pages
    for md in sorted(manual_dir.glob("*.md")):
        body = read_md(md)
        if not body.strip():
            continue
        pages.append({
            "slug": f"manual/{md.stem}",
            "title": first_h1(body, md.stem),
            "body": body,
        })
    return pages


def collect_log_sessions(limit: int = 10) -> list[dict]:
    """Split root log.md by '## YYYY-MM-DD' headings; return most recent N."""
    log_path = REPO_ROOT / "log.md"
    if not log_path.exists():
        return []
    text = read_md(log_path)
    sessions = []
    # Split by ## YYYY-MM-DD with the date in match
    pattern = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})", re.M)
    matches = list(pattern.finditer(text))
    for i, m in enumerate(matches):
        date = m.group(1)
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        title = f"{date} session"
        # First ### heading inside, if any, becomes the title detail
        sub = re.search(r"^###\s+(.*)", body, re.M)
        if sub:
            title = f"{date} — {sub.group(1).strip()}"
        sessions.append({
            "slug": f"log/{date}",
            "title": title,
            "body": body,
        })
    sessions.reverse()  # most recent first
    return sessions[:limit]


def collect_sprints(limit: int = 10) -> list[dict]:
    """One page per sprint card under sprints/completed/<dir>/RUN_*.md"""
    sprints_dir = REPO_ROOT / "sprints" / "completed"
    if not sprints_dir.exists():
        return []
    cards = []
    for sub in sprints_dir.iterdir():
        if not sub.is_dir():
            continue
        run_files = list(sub.glob("RUN_*.md"))
        if not run_files:
            continue
        run = run_files[0]
        body = read_md(run)
        if not body.strip():
            continue
        cards.append({
            "slug": f"sprint/{sub.name}",
            "title": first_h1(body, sub.name),
            "body": body,
            "_dirname": sub.name,
        })
    cards.sort(key=lambda c: c["_dirname"], reverse=True)
    return [{k: v for k, v in c.items() if k != "_dirname"} for c in cards[:limit]]


def collect_design() -> list[dict]:
    """A small curated subset of design docs."""
    targets = [
        ("docs/process/ANTI_PATTERNS.md", "design/anti-patterns"),
        ("docs/process/TROUBLESHOOTING.md", "design/troubleshooting"),
    ]
    pages = []
    for rel, slug in targets:
        p = REPO_ROOT / rel
        if not p.exists():
            continue
        body = read_md(p)
        if not body.strip():
            continue
        pages.append({
            "slug": slug,
            "title": first_h1(body, slug),
            "body": body,
        })
    return pages


def build_bundle() -> dict:
    return {
        "site": {
            "title": "BMA-Plan Dev Site",
            "subtitle": "เครื่องมือวัดพื้นที่ + dev log + คู่มือ",
            "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        },
        "groups": [
            {"title": "Manual / คู่มือผู้ใช้", "pages": collect_manual()},
            {"title": "Dev Log / บันทึกการพัฒนา", "pages": collect_log_sessions(limit=12)},
            {"title": "Sprints / การ์ดสปรินต์", "pages": collect_sprints(limit=12)},
            {"title": "Design / สถาปัตยกรรม", "pages": collect_design()},
        ],
    }


def main():
    bundle = build_bundle()
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    total_pages = sum(len(g["pages"]) for g in bundle["groups"])
    print(f"[build_docs] wrote {OUT_FILE.relative_to(REPO_ROOT)} — {total_pages} pages across {len(bundle['groups'])} groups")


if __name__ == "__main__":
    main()
