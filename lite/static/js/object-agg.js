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
   This file builds the stream + a parity oracle (assertEnginesAgree) proving
   it agrees with the existing computeSummary()/rollupAggByRole() engine.
   This is invariant I11 groundwork.

   Never edits measure-engine.js / polyAreaM2 / polyMetrics / pdfToC / cToPdf.

   --- slice B1 (INV-20260703-layer-linkage) ---
   Rerouted consumers: report-vars.js computeReportVars(agg, {useLive:true})
   and ui-lite.html openSum()'s new per-floor block now source role totals
   from byRole()/byFloorRole() instead of the legacy computeSummary()-derived
   agg. useLive is OPT-IN (default false / legacy path) specifically so the
   pure-function contract pinned by test_report_vars*.py — arbitrary
   synthetic agg in, deterministic fold-eval out, no window/PS coupling —
   stays intact; only the real production call sites (openSum, per-floor
   block, buildReportPayload's reportVars) pass {useLive:true}.

   DECISION on the B0-flagged excluded-page asymmetry: tuple engine
   (objectTuples) skips excluded[] pages; computeSummary() does not. B1
   resolves this for the tuple-sourced consumers ONLY — report vars and the
   per-floor block now correctly exclude excluded-page objects (new, more
   correct semantics). computeSummary()'s own cur/all totals rendered in the
   openSum() category table are LEFT UNCHANGED (still include excluded
   pages) — unifying that is B2 scope, not B1.

   floorReportRows()/floorKeyLabel() are rendering-agnostic: they return
   plain row data + Thai labels; ui-lite.html maps rows -> HTML.

   --- slice B2 (INV-20260703-layer-linkage, final structural slice) ---
   Retired the second (folder-scoped) aggregation engine for its remaining
   consumers: layer-tree.js _ltOwnArea(layerId) and overview-setup.js
   _lovsLayerArea(layerId) now reduce over objectTuples() filtered by
   catId, instead of each re-walking PS with its own loop (old loops kept
   as _ltOwnAreaLegacyLoop / _lovsLayerAreaLegacy — load-order-safety
   fallback + regression-guard comparator). overview-setup.js's Review
   step (Section 3, GFA Breakdown ต่อชั้น) now sources per-floor gfa/ded
   from byFloorRole() (same floorKey semantics as the B1 Summary block)
   instead of _lovsFolderArea(floorId, role) folder-membership sums — this
   is the "M6" fix: a gfa/ded layer never filed into its PF_floor_<N>
   folder (root-unfiled) is now correctly counted on that floor's Review
   row too, where it was silently dropped before. Site+coverage (Section
   2) intentionally stays folder-scoped (PF_site membership is the actual
   intended semantics there, not a floor row). openSum-vs-Review
   convergence (H2) is now structural: both read the same byFloorRole()
   bucket, so assertEnginesAgree()'s new floorRole-partition check (c)
   below covers the Review path without a separate comparison.

   Public API: window.ObjectAgg = {
     floorKeyOfPage, objectTuples, aggTuples, byRole, byFloor, byFloorRole,
     floorKeyLabel, floorReportRows, assertEnginesAgree
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

/* floorKey -> readable Thai label. Mirrors overview-setup.js's
   _lovsFloorLabel() wording (ชั้น N / ใต้ดิน N / ดาดฟ้า) but works from a
   floorKey string (no specific page number needed) so it can label an
   aggregated per-floor row group. "" / unrecognized -> "" (caller skips). */
function floorKeyLabel(fk) {
  if (fk === "site") return "ผังบริเวณ";
  if (fk === "roof") return "ดาดฟ้า";
  if (!fk) return "";
  var parts = String(fk).split(":"), kind = parts[0], num = parts[1];
  if (kind === "basement") return "ใต้ดิน " + num;
  if (kind === "mezz")     return "ชั้นลอย " + num;
  if (kind === "mech")     return "ห้องเครื่อง " + num;
  if (kind === "floor")    return "ชั้น " + num;
  return fk;
}
var _FLOOR_KIND_RANK = {basement: 0, floor: 1, mezz: 2, mech: 3};

/* Rendering-agnostic per-floor gfa/ded/net row data (B1). Skips the ""
   bucket (untagged/non-floor pages) and floors with no gfa/ded area at all.
   Uses tuple semantics (objectTuples() default arg) -> excluded[] pages are
   OUT, resolving the B0-flagged asymmetry for this consumer (see header).
   Returns [{floorKey, label, gfa, ded, net}], sorted basement->floor->mezz
   ->mech (ascending num within each kind); site/roof/unrecognized last. */
function floorReportRows(tuples) {
  var bfr = byFloorRole(tuples), out = [];
  Object.keys(bfr).forEach(function(fk) {
    if (!fk) return;
    var gfa = (bfr[fk].gfa && bfr[fk].gfa.area) || 0;
    var ded = (bfr[fk].ded && bfr[fk].ded.area) || 0;
    if (!gfa && !ded) return;
    out.push({floorKey: fk, label: floorKeyLabel(fk), gfa: gfa, ded: ded, net: gfa - ded});
  });
  out.sort(function(a, b) {
    var pa = a.floorKey.split(":"), pb = b.floorKey.split(":");
    var ra = (pa[0] in _FLOOR_KIND_RANK) ? _FLOOR_KIND_RANK[pa[0]] : 9;
    var rb = (pb[0] in _FLOOR_KIND_RANK) ? _FLOOR_KIND_RANK[pb[0]] : 9;
    return ra !== rb ? ra - rb : (parseFloat(pa[1]) || 0) - (parseFloat(pb[1]) || 0);
  });
  return out;
}

/* TEST ORACLE (invariant I11 groundwork) — never throws, never alerts.
   Compares (a) byRole() role totals vs rollupAggByRole(computeSummary().all)
   role totals, (b) sum of all tuple areas vs sum of computeSummary().all
   values, and (c) [B2] byFloorRole()'s per-floorKey partition sums back to
   byRole() exactly for every role — the identity overview-setup.js's Review
   per-floor rows now rely on (B2 rerouted them onto byFloorRole()), proving
   Review structurally agrees with the role-level engine already checked in
   (a)/(b) with no separate "Review engine" left to diverge from (H2 closed).
   Returns {ok, diffs:[...]}. */
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

    var bfr = byFloorRole(tuples);
    var floorRoleSums = {};
    Object.keys(bfr).forEach(function(fk) {
      Object.keys(bfr[fk]).forEach(function(role) {
        floorRoleSums[role] = (floorRoleSums[role] || 0) + bfr[fk][role].area;
      });
    });
    roleIds.forEach(function(role) {
      var a2 = floorRoleSums[role] || 0;
      var b2 = (br[role] && br[role].area) || 0;
      var tol2 = eps * Math.max(1, Math.abs(b2));
      var diff2 = Math.abs(a2 - b2);
      if (diff2 > tol2) diffs.push({type: "floorRole", role: role, floorRoleTotal: a2, byRoleTotal: b2, diff: diff2});
    });

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
  floorKeyLabel: floorKeyLabel,
  floorReportRows: floorReportRows,
  assertEnginesAgree: assertEnginesAgree
};
if (typeof window !== "undefined") window.ObjectAgg = _ObjectAgg;
if (typeof module !== "undefined" && module.exports) module.exports = _ObjectAgg;
