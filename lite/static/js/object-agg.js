/* ============================================================
   OBJECT-AGG — single object-tuple aggregation engine
   (INV-20260703-layer-linkage, approach B, slice B0 — groundwork ONLY).
   Plain-globals module. No IIFE, no export, no bundler.
   Loaded AFTER layer-system.js / layer-tree.js / page-folder-layers.js /
   report-vars.js / cross-floor-shapes.js (dynamically loaded by
   page-folder-layers.js), BEFORE the inline script.

   Depends on (all read via typeof guard — some load dynamically):
     PS, pageTags, pageFloorNum, pageFloorKind, excluded  (inline script state)
     layerById                                            (layer-system.js)
     rollupCatId, rollupAreaM2                             (cross-floor-shapes.js)
     computeSummary                                        (inline script)
     rollupAggByRole, ROLE_DEFS                             (report-vars.js / layer-system.js)

   PURPOSE: a single flat tuple stream {pg, catId, role, floorKey, area,
   counting, count} from which every existing rollup (byRole, byFloor,
   per-folder totals, ...) can in principle be derived by a plain group-sum.
   NOTHING is rerouted to this stream yet (that is slice B1/B2). This file
   only builds the stream + a parity oracle (assertEnginesAgree) proving it
   agrees with the existing computeSummary()/rollupAggByRole() engine BEFORE
   any consumer is touched. This is invariant I11 groundwork.

   Never edits measure-engine.js / polyAreaM2 / polyMetrics / pdfToC / cToPdf.

   Public API: window.ObjectAgg = {
     floorKeyOfPage, objectTuples, aggTuples, byRole, byFloor, byFloorRole,
     assertEnginesAgree
   }
   ============================================================ */

/* Stable floor-bucket key for a page, mirroring pageFolderIdFor's floor/site
   designation (page-folder-layers.js) but WITHOUT the "PF_" prefix and using
   ':' instead of '_' so keys read as "floor:2" / "basement:1" / "site".
   "" = untagged, non-floor tag (plan/parking/amenity/detail/excluded), or a
   floor-tagged page with no floor# yet — same "not a bucket yet" treatment
   pageFolderIdFor gives those cases (PF_excluded). */
function floorKeyOfPage(pg) {
  var tag = (typeof pageTags !== "undefined") ? pageTags[pg] : undefined;
  if (tag === "site") return "site";
  if (tag !== "floor") return "";
  var kind = ((typeof pageFloorKind !== "undefined") ? pageFloorKind[pg] : undefined) || "normal";
  var floorNum = (typeof pageFloorNum !== "undefined") ? pageFloorNum[pg] : undefined;
  if (kind === "rooftop" || floorNum === "roof") return "roof";
  if (floorNum === undefined || floorNum === null || floorNum === "") return "";
  switch (kind) {
    case "basement":   return "basement:" + floorNum;
    case "mezzanine":  return "mezz:" + floorNum;
    case "mechanical": return "mech:" + floorNum;
    case "normal":
    default:           return "floor:" + floorNum;
  }
}

/* Flatten every measurable object across all non-excluded PS pages into a
   flat tuple stream. Mirrors computeSummary()'s inclusion rules exactly
   (arc + CFSS-instance inclusive area via rollupAreaM2/rollupCatId, skip
   null area/catId) but additionally skips excluded[] pages, consistent
   with _lovsLayerArea (overview-setup.js). computeSummary() itself does
   NOT skip excluded pages (pre-existing gap, out of scope for B0) — so
   assertEnginesAgree() below is only exact when the fixture has no
   objects on excluded pages; excluded-page skipping is asserted directly
   against objectTuples()/byRole() instead. */
function objectTuples() {
  var out = [];
  if (typeof PS === "undefined") return out;
  Object.keys(PS).forEach(function(k) {
    var pg = +k;
    if (typeof excluded !== "undefined" && excluded[pg]) return;
    var objs = (PS[k] && PS[k].objects) || [];
    var floorKey = floorKeyOfPage(pg);
    for (var i = 0; i < objs.length; i++) {
      var o = objs[i];
      if (o.counting) {
        if (o.catId == null) continue;
        var crole = (typeof layerById === "function" && layerById(o.catId)) ? layerById(o.catId).role : null;
        out.push({pg: pg, catId: o.catId, role: crole, floorKey: floorKey, area: null, counting: true, count: 1});
        continue;
      }
      var catId = (typeof rollupCatId === "function") ? rollupCatId(o) : o.catId;
      var area = (typeof rollupAreaM2 === "function") ? rollupAreaM2(o, pg)
        : (o.kind === "poly" && typeof polyMetricsAnyShape === "function" ? polyMetricsAnyShape(o, pg).area : null);
      if (area == null || catId == null) continue;
      var role = (typeof layerById === "function" && layerById(catId)) ? layerById(catId).role : null;
      out.push({pg: pg, catId: catId, role: role, floorKey: floorKey, area: area, counting: false, count: 0});
    }
  });
  return out;
}

/* Generic group-sum: {key -> {area, count}}. keyFn(t) may return null/undefined
   to drop a tuple from the grouping. */
function aggTuples(tuples, keyFn) {
  var out = {};
  (tuples || []).forEach(function(t) {
    var k = keyFn(t);
    if (k == null) return;
    if (!out[k]) out[k] = {area: 0, count: 0};
    if (t.area != null) out[k].area += t.area;
    out[k].count += (t.count || 0);
  });
  return out;
}

function byRole(tuples) {
  return aggTuples(tuples || objectTuples(), function(t) { return t.role; });
}
function byFloor(tuples) {
  return aggTuples(tuples || objectTuples(), function(t) { return t.floorKey; });
}
/* Nested {floorKey -> {role -> {area, count}}} — per-floor role separation
   that no existing engine (computeSummary/_lovsFolderArea/_lovsRoleArea)
   currently provides in one call. */
function byFloorRole(tuples) {
  var out = {};
  (tuples || objectTuples()).forEach(function(t) {
    if (t.floorKey == null || t.role == null) return;
    if (!out[t.floorKey]) out[t.floorKey] = {};
    if (!out[t.floorKey][t.role]) out[t.floorKey][t.role] = {area: 0, count: 0};
    if (t.area != null) out[t.floorKey][t.role].area += t.area;
    out[t.floorKey][t.role].count += (t.count || 0);
  });
  return out;
}

/* TEST ORACLE (invariant I11 groundwork) — never throws, never alerts.
   Compares (a) byRole() role totals vs rollupAggByRole(computeSummary().all)
   role totals, and (b) sum of all tuple areas vs sum of computeSummary().all
   values. Returns {ok, diffs:[...]}. */
function assertEnginesAgree(epsilon) {
  var eps = (typeof epsilon === "number") ? epsilon : 1e-6;
  var diffs = [];
  try {
    var tuples = objectTuples();
    var br = byRole(tuples);

    var summaryAll = {};
    if (typeof computeSummary === "function") {
      var s = computeSummary();
      summaryAll = (s && s.all) || {};
    }
    var rolled = (typeof rollupAggByRole === "function") ? rollupAggByRole(summaryAll) : summaryAll;

    var roleIds = (typeof ROLE_DEFS !== "undefined") ? ROLE_DEFS.map(function(r) { return r.id; }) : Object.keys(br);
    roleIds.forEach(function(role) {
      var a = (br[role] && br[role].area) || 0;
      var b = rolled[role] || 0;
      var tol = eps * Math.max(1, Math.abs(b));
      var diff = Math.abs(a - b);
      if (diff > tol) diffs.push({type: "role", role: role, tupleArea: a, summaryArea: b, diff: diff});
    });

    var tupleTotal = 0;
    tuples.forEach(function(t) { if (t.area != null) tupleTotal += t.area; });
    var summaryTotal = 0;
    Object.keys(summaryAll).forEach(function(k) { summaryTotal += summaryAll[k]; });
    var totalTol = eps * Math.max(1, Math.abs(summaryTotal));
    var totalDiff = Math.abs(tupleTotal - summaryTotal);
    if (totalDiff > totalTol) diffs.push({type: "total", tupleTotal: tupleTotal, summaryTotal: summaryTotal, diff: totalDiff});

    return {ok: diffs.length === 0, diffs: diffs};
  } catch (e) {
    return {ok: false, diffs: [{type: "exception", message: String((e && e.message) || e)}]};
  }
}

var _ObjectAgg = {
  floorKeyOfPage: floorKeyOfPage,
  objectTuples: objectTuples,
  aggTuples: aggTuples,
  byRole: byRole,
  byFloor: byFloor,
  byFloorRole: byFloorRole,
  assertEnginesAgree: assertEnginesAgree
};
if (typeof window !== "undefined") window.ObjectAgg = _ObjectAgg;
if (typeof module !== "undefined" && module.exports) module.exports = _ObjectAgg;
