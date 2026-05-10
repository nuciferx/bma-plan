# AREA_SUMMARY_BY_TAG_AND_FLOOR_AUDIT.md

> Sprint: RUN_AREA_SUMMARY_BY_TAG_AND_FLOOR
> Date: 2026-05-10
> Result: No source changes needed — existing grouping is correct.

---

## Audit Findings

### Backend Export (proto/server.py)

Area summaries group by:
1. **Page** (`pg_str` integer key, displayed as `pg_name`)
2. **semanticTag** → `measurementProfile`, `objectCategory`, `reportTarget`

No layer name appears in any grouping key.
Area is calculated as: `_poly_area_pt2(poly.pts) / pts_per_m²`

```python
# server.py excerpt — report target summary sheet
key = (meta["reportTarget"] or "Unclassified",
       meta["objectCategory"] or "annotation",
       meta["countingRule"] or "reference")
```

Grouping key uses `reportTarget`, `objectCategory`, `countingRule` — none from layer.

### Frontend Summary (proto/ui.html)

`updatePageSummary(n)` sums `poly.area` from `mPolys` and `mOpenings`.
No layer name in the sum.

`updateLayerObjectCounts(pageIndex)` (added in Sprint 3) counts objects per layer
for display in the right panel. This count is display-only — not used in any area calculation.

### Cross-Page Total (proto/server.py grand_total)

`grand_total` sums all pages regardless of page type.
This is a known gap (G8 from audit) — future improvement would filter by `pageType`
or `floorCode` to separate GFA floors from site/elevation pages.
No implementation needed in this sprint; flagged for `RUN_AREA_SUMMARY_V2.md`.

---

## Conclusion

- Area summaries: driven by `pageId` + `semanticTag`/`measurementProfile`/`reportTarget` — **CORRECT**
- Layer name: not used anywhere in calculation or export grouping — **CORRECT**
- Object count per layer: display-only, not a calculation input — **CORRECT**
- Cross-page total: sums all pages (known limitation, not a correctness bug for Phase 1)

No source changes required for this sprint.

---

## Remaining Gap (for future sprint)

| Gap | Description | Sprint |
|-----|-------------|--------|
| G8 | Cross-page total does not filter by pageType/floorCode | RUN_AREA_SUMMARY_V2.md |
