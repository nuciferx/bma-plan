"""xlsx_helpers.py — geometry helpers for PDF annotation export and XLSX reports."""
import math


def _hex_to_rgb(h: str):
    h = h.lstrip("#")
    if len(h) != 6:
        return (1, 1, 0)
    return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))


def _poly_area_pt2(pts: list[dict]) -> float:
    if len(pts) < 3:
        return 0.0
    area = 0.0
    for i, p1 in enumerate(pts):
        p2 = pts[(i + 1) % len(pts)]
        area += p1["x"] * p2["y"] - p2["x"] * p1["y"]
    return abs(area) / 2.0


def _line_points(line: dict) -> list[dict]:
    if isinstance(line.get("pts"), list) and len(line["pts"]) >= 2:
        return line["pts"]
    x0 = line.get("x0", 0); y0 = line.get("y0", 0)
    x1 = line.get("x1", 0); y1 = line.get("y1", 0)
    return [{"x": x0, "y": y0}, {"x": x1, "y": y1}]


def _line_length_pt(pts: list[dict]) -> float:
    total = 0.0
    for i in range(len(pts) - 1):
        dx = pts[i+1]["x"] - pts[i]["x"]
        dy = pts[i+1]["y"] - pts[i]["y"]
        total += math.hypot(dx, dy)
    return total


def _nearest_on_segment(px: float, py: float,
                         x0: float, y0: float,
                         x1: float, y1: float) -> dict:
    dx = x1 - x0; dy = y1 - y0
    len2 = dx*dx + dy*dy
    if len2 < 1e-12:
        return {"x": x0, "y": y0, "t": 0.0}
    t = max(0.0, min(1.0, ((px - x0)*dx + (py - y0)*dy) / len2))
    return {"x": x0 + t*dx, "y": y0 + t*dy, "t": t}


def _object_points_for_ref_report(kind: str, obj: dict) -> list[dict]:
    if kind == "parking":
        return [{"x": obj.get("x", 0), "y": obj.get("y", 0)}]
    if kind in ("poly", "opening"):
        pts = obj.get("pts") or []
        if not pts:
            return []
        cx = sum(p["x"] for p in pts) / len(pts)
        cy = sum(p["y"] for p in pts) / len(pts)
        return [{"x": cx, "y": cy}]
    # line / ref
    raw = _line_points(obj)
    if len(raw) >= 2:
        mid = raw[len(raw) // 2]
        return [{"x": mid["x"], "y": mid["y"]}]
    return []


def _distance_to_ref(pt: dict, ref: dict) -> dict | None:
    raw = _line_points(ref)
    if len(raw) < 2:
        return None
    best = None
    best_d2 = math.inf
    for i in range(len(raw) - 1):
        hit = _nearest_on_segment(pt["x"], pt["y"],
                                   raw[i]["x"], raw[i]["y"],
                                   raw[i+1]["x"], raw[i+1]["y"])
        d2 = (hit["x"] - pt["x"])**2 + (hit["y"] - pt["y"])**2
        if d2 < best_d2:
            best_d2 = d2
            best = {"x": hit["x"], "y": hit["y"], "dist_pt": math.sqrt(d2)}
    return best


def _m2_to_rwu(m2: float):
    if m2 <= 0:
        return (0, 0, 0)
    rai = int(m2 // 1600)
    rem = m2 % 1600
    ngan = int(rem // 400)
    sqwa = round((rem % 400) / 4, 2)
    return (rai, ngan, sqwa)
