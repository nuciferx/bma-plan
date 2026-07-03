#!/usr/bin/env node
/* ============================================================================
   SPIKE — INV-20260703-layer-floorkey (Pack H phase 6)
   Approach A (layer.floorKey additive override) + parity/behaviour proofs.

   This is a STANDALONE Node harness. It COPIES (does not import) the relevant
   derivation logic from:
     lite/static/js/object-agg.js        (floorKeyOfPage, objectTuples,
                                           aggTuples, byRole/byFloor/byFloorRole)
     lite/static/js/layer-system.js      (layerById, role model)
     lite/static/js/cross-floor-shapes.js(rollupCatId, rollupAreaM2,
                                           instanceAreaM2, isInstance)
   It never imports the live files (so the concurrent UX-batch-3 edits can't
   affect it) and never mutates anything outside this process.

   The PROPOSED derivation:
     floorKeyOfObject(o, pg): layerOf(o.catId).floorKey ?? floorKeyOfPage(pg)
       - additive override: a layer's own floorKey wins; page tag = fallback.
       - CFSS master may carry floorKey:"multi" -> resolve per-instance page
         (today's behaviour).

   4 PROOFS, each prints PASS/FAIL + numbers:
     1. Legacy parity   (no layer.floorKey anywhere -> byte/number-identical)
     2. Re-tag follows layer (layer.floorKey pins; divergence detected)
     3. Two gfa layers, different floors, same page (distinct buckets)
     4. CFSS master floorKey:"multi" -> per-instance page (identical to today)

   Run:  node spike.js
   ========================================================================== */

'use strict';

/* ---------------------------------------------------------------------------
   MUTABLE STATE (reset per proof) — mirrors the ui-lite inline-script globals
   the real object-agg.js reads via typeof-guard.
   ------------------------------------------------------------------------- */
var PS, pageTags, pageFloorNum, pageFloorKind, excluded, LAYERS, MASTERS;

/* ---------------------------------------------------------------------------
   COPIED: layer / master accessors (layer-system.js + cross-floor-shapes.js)
   ------------------------------------------------------------------------- */
function layerById(id) {
  for (var i = 0; i < LAYERS.length; i++) if (LAYERS[i].id === id) return LAYERS[i];
  return null;
}
function masterById(id) { return MASTERS[id]; }

/* ---------------------------------------------------------------------------
   COPIED: area math (metric shoelace) — stand-ins for the live functions.
   polyMetricsAnyShape divides pt-shoelace by ppm^2 (mirrors real pt->m).
   instanceAreaM2 is metric-shoelace on master.metricPts (ppm-independent,
   verbatim algorithm from cross-floor-shapes.js).
   BOTH derivations use these identically, so parity is about floorKey only.
   ------------------------------------------------------------------------- */
function shoelace(pts) {
  var n = pts.length, a = 0;
  for (var i = 0; i < n; i++) { var j = (i + 1) % n; a += pts[i].x * pts[j].y - pts[j].x * pts[i].y; }
  return Math.abs(a) / 2;
}
function polyMetricsAnyShape(o, pg) {
  var ppm = (PS[pg] && PS[pg].scale && PS[pg].scale.pts_per_m) || 1;
  return { area: shoelace(o.pts) / (ppm * ppm) };
}
function instanceAreaM2(inst) {
  var m = MASTERS[inst.masterId];
  if (!m || !m.metricPts || m.metricPts.length < 3) return null;
  var mp = m.metricPts, n = mp.length, a = 0;
  for (var i = 0; i < n; i++) { var j = (i + 1) % n; a += mp[i].x_m * mp[j].y_m - mp[j].x_m * mp[i].y_m; }
  return Math.abs(a) / 2;
}

/* COPIED verbatim: instance predicate + rollup dispatch (cross-floor-shapes.js) */
function isInstance(o) { return !!(o && o.kind === 'instance' && typeof o.masterId === 'string'); }
function rollupAreaM2(o, pg) {
  if (!o) return null;
  if (o.kind === 'instance') return instanceAreaM2(o);
  if (o.kind === 'poly') return polyMetricsAnyShape(o, pg).area;
  return null;
}
function rollupCatId(o) {
  if (!o) return null;
  if (o.catId != null) return o.catId;
  if (o.kind === 'instance') { var m = masterById(o.masterId); return (m && m.catId != null) ? m.catId : null; }
  return null;
}

/* ---------------------------------------------------------------------------
   COPIED verbatim: floorKeyOfPage (object-agg.js lines 77-92)
   ------------------------------------------------------------------------- */
function floorKeyOfPage(pg) {
  var tag = pageTags[pg];
  if (tag === 'site') return 'site';
  if (tag !== 'floor') return '';
  var kind = pageFloorKind[pg] || 'normal';
  var floorNum = pageFloorNum[pg];
  if (kind === 'rooftop' || floorNum === 'roof') return 'roof';
  if (floorNum === undefined || floorNum === null || floorNum === '') return '';
  switch (kind) {
    case 'basement':   return 'basement:' + floorNum;
    case 'mezzanine':  return 'mezz:' + floorNum;
    case 'mechanical': return 'mech:' + floorNum;
    case 'normal':
    default:           return 'floor:' + floorNum;
  }
}

/* ---------------------------------------------------------------------------
   NEW (the proposed derivation): floorKeyOfObject
     layer.floorKey (additive override)  ??  floorKeyOfPage(pg)  (fallback)
   CFSS: a master carrying floorKey:"multi" (or none) -> per-instance page.
         a master carrying a concrete floorKey would pin all its instances.
   ------------------------------------------------------------------------- */
function floorKeyOfObject(o, pg) {
  // CFSS instance: master's own floorKey wins unless "multi" (=cross-floor).
  if (o.kind === 'instance') {
    var m = masterById(o.masterId);
    if (m && m.floorKey && m.floorKey !== 'multi') return m.floorKey;
    // master floorKey absent or "multi": fall through to layer-of-catId, then page.
  }
  var catId = rollupCatId(o);
  var layer = layerById(catId);
  var lfk = layer && layer.floorKey;
  if (lfk && lfk !== 'multi') return lfk;   // layer override
  return floorKeyOfPage(pg);                 // page-tag fallback (today's behaviour)
}

/* ---------------------------------------------------------------------------
   COPIED: objectTuples — but parameterised by a floorKey deriver so BOTH the
   old and new derivations share the exact same body. deriveFK(o,pg) is the
   ONLY point of variation, which is precisely what the spike is proving.
   (Verbatim except the floorKey field now calls deriveFK.)
   ------------------------------------------------------------------------- */
function objectTuples(deriveFK) {
  var out = [];
  Object.keys(PS).forEach(function (k) {
    var pg = +k;
    if (excluded[pg]) return;
    var objs = (PS[k] && PS[k].objects) || [];
    for (var i = 0; i < objs.length; i++) {
      var o = objs[i];
      if (o.counting) {
        if (o.catId == null) continue;
        var crole = layerById(o.catId) ? layerById(o.catId).role : null;
        out.push({ pg: pg, catId: o.catId, role: crole, floorKey: deriveFK(o, pg), area: null, counting: true, count: 1 });
        continue;
      }
      var catId = rollupCatId(o);
      var area = rollupAreaM2(o, pg);
      if (area == null || catId == null) continue;
      var role = layerById(catId) ? layerById(catId).role : null;
      out.push({ pg: pg, catId: catId, role: role, floorKey: deriveFK(o, pg), area: area, counting: false, count: 0 });
    }
  });
  return out;
}
var deriveOld = function (o, pg) { return floorKeyOfPage(pg); };   // TODAY
var deriveNew = function (o, pg) { return floorKeyOfObject(o, pg); }; // PROPOSED

/* ---------------------------------------------------------------------------
   COPIED verbatim: group-sum engines (object-agg.js)
   ------------------------------------------------------------------------- */
function aggTuples(tuples, keyFn) {
  var out = {};
  (tuples || []).forEach(function (t) {
    var k = keyFn(t);
    if (k == null) return;
    if (!out[k]) out[k] = { area: 0, count: 0 };
    if (t.area != null) out[k].area += t.area;
    out[k].count += (t.count || 0);
  });
  return out;
}
function byRole(t)  { return aggTuples(t, function (x) { return x.role; }); }
function byFloor(t) { return aggTuples(t, function (x) { return x.floorKey; }); }
function byFloorRole(t) {
  var out = {};
  (t || []).forEach(function (x) {
    if (x.floorKey == null || x.role == null) return;
    if (!out[x.floorKey]) out[x.floorKey] = {};
    if (!out[x.floorKey][x.role]) out[x.floorKey][x.role] = { area: 0, count: 0 };
    if (x.area != null) out[x.floorKey][x.role].area += x.area;
    out[x.floorKey][x.role].count += (x.count || 0);
  });
  return out;
}

/* ---------------------------------------------------------------------------
   ORACLE — self-contained b/c partition checks (mirrors assertEnginesAgree's
   (b) total-partition and (c) floorRole-partition, minus the computeSummary
   comparison which has no Node equivalent). Never throws.
   (b) sum(tuple areas) == sum(byRole areas) == sum(byFloor areas)
   (c) for every role: sum over floorKeys of byFloorRole == byRole[role]
   ------------------------------------------------------------------------- */
function oracle(tuples) {
  var eps = 1e-9, diffs = [];
  var br = byRole(tuples), bf = byFloor(tuples), bfr = byFloorRole(tuples);

  var tupleTotal = 0; tuples.forEach(function (t) { if (t.area != null) tupleTotal += t.area; });
  var roleTotal = 0; Object.keys(br).forEach(function (r) { roleTotal += br[r].area; });
  var floorTotal = 0; Object.keys(bf).forEach(function (f) { floorTotal += bf[f].area; });
  if (Math.abs(tupleTotal - roleTotal) > eps)  diffs.push({ type: 'b:tuple-vs-role', tupleTotal: tupleTotal, roleTotal: roleTotal });
  if (Math.abs(tupleTotal - floorTotal) > eps) diffs.push({ type: 'b:tuple-vs-floor', tupleTotal: tupleTotal, floorTotal: floorTotal });

  var frSums = {};
  Object.keys(bfr).forEach(function (fk) {
    Object.keys(bfr[fk]).forEach(function (r) { frSums[r] = (frSums[r] || 0) + bfr[fk][r].area; });
  });
  var roles = {};
  Object.keys(br).forEach(function (r) { roles[r] = 1; });
  Object.keys(frSums).forEach(function (r) { roles[r] = 1; });
  Object.keys(roles).forEach(function (r) {
    var a = (br[r] && br[r].area) || 0, b = frSums[r] || 0;
    if (Math.abs(a - b) > eps) diffs.push({ type: 'c:floorRole-partition', role: r, byRole: a, floorRoleSum: b });
  });
  return { ok: diffs.length === 0, diffs: diffs };
}

/* Divergence detector — the data feed for the reconcile banner (proof 2).
   Lists objects whose layer.floorKey disagrees with their page's floorKey. */
function detectDivergence() {
  var out = [];
  Object.keys(PS).forEach(function (k) {
    var pg = +k;
    if (excluded[pg]) return;
    (PS[k].objects || []).forEach(function (o, idx) {
      var catId = o.counting ? o.catId : rollupCatId(o);
      var layer = layerById(catId);
      var lfk = layer && layer.floorKey;
      if (lfk && lfk !== 'multi') {
        var pfk = floorKeyOfPage(pg);
        if (lfk !== pfk) out.push({ pg: pg, idx: idx, catId: catId, name: o.name || o.kind, layerFloorKey: lfk, pageFloorKey: pfk });
      }
    });
  });
  return out;
}

/* ---------------------------------------------------------------------------
   Canonical comparison helpers (round numbers, sort keys, deep-equal)
   ------------------------------------------------------------------------- */
function canon(v) {
  if (typeof v === 'number') return Math.round(v * 1e9) / 1e9;
  if (Array.isArray(v)) return v.map(canon);
  if (v && typeof v === 'object') { var o = {}; Object.keys(v).sort().forEach(function (k) { o[k] = canon(v[k]); }); return o; }
  return v;
}
function eq(a, b) { return JSON.stringify(canon(a)) === JSON.stringify(canon(b)); }
function fmtFloor(agg) {
  return Object.keys(agg).sort().map(function (k) {
    return (k === '' ? '(none)' : k) + '=' + agg[k].area.toFixed(2) + (agg[k].count ? '/' + agg[k].count : '');
  }).join('  ');
}
function fmtRole(agg) {
  return Object.keys(agg).sort().map(function (k) {
    return k + '=' + agg[k].area.toFixed(2) + (agg[k].count ? '/' + agg[k].count : '');
  }).join('  ');
}
function total(t) { var s = 0; t.forEach(function (x) { if (x.area != null) s += x.area; }); return s; }

/* ---------------------------------------------------------------------------
   Fixture helpers
   ------------------------------------------------------------------------- */
function rect(w, h, ox, oy) {
  ox = ox || 0; oy = oy || 0;
  return [{ x: ox, y: oy }, { x: ox + w, y: oy }, { x: ox + w, y: oy + h }, { x: ox, y: oy + h }];
}
function rectM(w, h) {
  return [{ x_m: 0, y_m: 0 }, { x_m: w, y_m: 0 }, { x_m: w, y_m: h }, { x_m: 0, y_m: h }];
}
function defaultLayers() {
  return [
    { id: 'gfa', role: 'gfa' }, { id: 'use', role: 'use' }, { id: 'ded', role: 'ded' },
    { id: 'site', role: 'site' }, { id: 'open', role: 'open' }, { id: 'count', role: 'count', counting: true }
  ];
}
function pageScale1() { return { pts_per_m: 1 }; }

/* ============================================================================
   PROOF DRIVERS
   ========================================================================== */
var RESULTS = [];
function report(name, pass, lines) {
  RESULTS.push({ name: name, pass: pass });
  console.log('\n' + '='.repeat(78));
  console.log((pass ? 'PASS' : 'FAIL') + ' — ' + name);
  console.log('='.repeat(78));
  lines.forEach(function (l) { console.log('  ' + l); });
}

/* --- PROOF 1: Legacy parity (no layer.floorKey anywhere) ------------------ */
function proof1() {
  LAYERS = defaultLayers().concat([{ id: 'L1', role: 'gfa' }]); // custom, NO floorKey
  pageTags = { 1: 'floor', 2: 'floor', 3: 'floor' };
  pageFloorNum = { 1: 1, 2: 2, 3: 1 };
  pageFloorKind = { 1: 'normal', 2: 'normal', 3: 'normal' };
  excluded = {};
  MASTERS = { m1: { id: 'm1', catId: 'gfa', metricPts: rectM(3, 10) } }; // area 30, NO floorKey
  PS = {
    1: { scale: pageScale1(), objects: [
      { kind: 'poly', catId: 'gfa', pts: rect(10, 10), name: 'gfa-p1' },   // 100
      { kind: 'poly', catId: 'ded', pts: rect(2, 5), name: 'ded-p1' },      // 10
      { counting: true, catId: 'count', name: 'count-p1' },                 // count 1
      { kind: 'instance', masterId: 'm1' }                                   // 30 (page floor:1)
    ] },
    2: { scale: pageScale1(), objects: [
      { kind: 'poly', catId: 'gfa', pts: rect(10, 20), name: 'gfa-p2' },    // 200
      { kind: 'instance', masterId: 'm1' }                                   // 30 (page floor:2)
    ] },
    3: { scale: pageScale1(), objects: [
      { kind: 'poly', catId: 'L1', pts: rect(5, 10), name: 'gfaL1-p3' },    // 50 (role gfa)
      { kind: 'poly', catId: 'ded', pts: rect(1, 5), name: 'ded-p3' }        // 5
    ] }
  };

  var tOld = objectTuples(deriveOld), tNew = objectTuples(deriveNew);
  var oOld = oracle(tOld), oNew = oracle(tNew);
  var parityTuples = eq(tOld, tNew);
  var parityRole = eq(byRole(tOld), byRole(tNew));
  var parityFloor = eq(byFloor(tOld), byFloor(tNew));
  var parityFR = eq(byFloorRole(tOld), byFloorRole(tNew));
  var pass = parityTuples && parityRole && parityFloor && parityFR && oOld.ok && oNew.ok;

  report('Proof 1 — Legacy parity (no layer.floorKey anywhere)', pass, [
    'tuple count: old=' + tOld.length + ' new=' + tNew.length,
    'byRole  (new): ' + fmtRole(byRole(tNew)),
    'byFloor (old): ' + fmtFloor(byFloor(tOld)),
    'byFloor (new): ' + fmtFloor(byFloor(tNew)),
    'byFloorRole equal: ' + parityFR + '  | tupleStream equal: ' + parityTuples,
    'byRole equal: ' + parityRole + '  | byFloor equal: ' + parityFloor,
    'oracle old.ok=' + oOld.ok + '  oracle new.ok=' + oNew.ok,
    'grand total: old=' + total(tOld).toFixed(2) + ' new=' + total(tNew).toFixed(2)
  ]);
}

/* --- PROOF 2: Re-tag follows layer ---------------------------------------- */
function proof2() {
  // Custom layer L1 pinned to floor:1. Page 5 tagged floor 1 initially.
  LAYERS = defaultLayers().concat([{ id: 'L1', role: 'gfa', floorKey: 'floor:1' }]);
  pageTags = { 5: 'floor' };
  pageFloorNum = { 5: 1 };
  pageFloorKind = { 5: 'normal' };
  excluded = {};
  MASTERS = {};
  PS = {
    5: { scale: pageScale1(), objects: [
      { kind: 'poly', catId: 'L1', pts: rect(8, 10), name: 'pinned-L1' },  // 80, layer floor:1
      { kind: 'poly', catId: 'gfa', pts: rect(4, 10), name: 'default-gfa' } // 40, follows page
    ] }
  };

  var before = objectTuples(deriveNew);
  var bfBefore = byFloor(before);
  var totBefore = total(before);
  var divBefore = detectDivergence();

  // RE-TAG page 5 -> floor 2
  pageFloorNum[5] = 2;

  var after = objectTuples(deriveNew);
  var bfAfter = byFloor(after);
  var totAfter = total(after);
  var div = detectDivergence();

  // Expectations
  var pinnedStayed = bfAfter['floor:1'] && Math.abs(bfAfter['floor:1'].area - 80) < 1e-9;
  var defaultMoved = bfAfter['floor:2'] && Math.abs(bfAfter['floor:2'].area - 40) < 1e-9;
  var totalUnchanged = Math.abs(totBefore - totAfter) < 1e-9;
  var divergenceDetected = div.length === 1 && div[0].name === 'pinned-L1' &&
    div[0].layerFloorKey === 'floor:1' && div[0].pageFloorKey === 'floor:2';
  var noDivBefore = divBefore.length === 0;
  var oracleOk = oracle(after).ok;
  var pass = pinnedStayed && defaultMoved && totalUnchanged && divergenceDetected && noDivBefore && oracleOk;

  report('Proof 2 — Re-tag follows layer (pin + divergence feed)', pass, [
    'BEFORE re-tag  byFloor: ' + fmtFloor(bfBefore) + '  (total ' + totBefore.toFixed(2) + ', divergence ' + divBefore.length + ')',
    'AFTER  re-tag  byFloor: ' + fmtFloor(bfAfter) + '  (total ' + totAfter.toFixed(2) + ')',
    'pinned L1 stayed in floor:1 @80 = ' + pinnedStayed,
    'default gfa moved to floor:2 @40 = ' + defaultMoved,
    'grand total unchanged (' + totBefore.toFixed(2) + '==' + totAfter.toFixed(2) + ') = ' + totalUnchanged,
    'divergence rows: ' + JSON.stringify(div),
    'reconcile banner feed = layer "' + (div[0] ? div[0].catId : '-') + '" pinned ' +
      (div[0] ? div[0].layerFloorKey : '-') + ' but page is ' + (div[0] ? div[0].pageFloorKey : '-'),
    'oracle after.ok = ' + oracleOk
  ]);
}

/* --- PROOF 3: Two gfa layers, different floors, same page ----------------- */
function proof3() {
  LAYERS = defaultLayers().concat([
    { id: 'A', role: 'gfa', floorKey: 'floor:1' },  // e.g. floor-1 slab
    { id: 'B', role: 'gfa', floorKey: 'floor:2' }   // e.g. mezzanine drawn on the floor-1 sheet
  ]);
  pageTags = { 7: 'floor' };
  pageFloorNum = { 7: 1 };
  pageFloorKind = { 7: 'normal' };
  excluded = {};
  MASTERS = {};
  PS = {
    7: { scale: pageScale1(), objects: [
      { kind: 'poly', catId: 'A', pts: rect(6, 10), name: 'floor1-slab' },  // 60 -> floor:1
      { kind: 'poly', catId: 'B', pts: rect(9, 10), name: 'mezz-on-p7' }    // 90 -> floor:2
    ] }
  };

  var t = objectTuples(deriveNew);
  var bfr = byFloorRole(t);
  var br = byRole(t);
  var f1 = (bfr['floor:1'] && bfr['floor:1'].gfa && bfr['floor:1'].gfa.area) || 0;
  var f2 = (bfr['floor:2'] && bfr['floor:2'].gfa && bfr['floor:2'].gfa.area) || 0;
  var distinct = Math.abs(f1 - 60) < 1e-9 && Math.abs(f2 - 90) < 1e-9;
  var sumEqualsRole = Math.abs((f1 + f2) - br.gfa.area) < 1e-9;
  var onePageOnly = Object.keys(PS).length === 1;
  var oracleOk = oracle(t).ok;
  var pass = distinct && sumEqualsRole && onePageOnly && oracleOk;

  report('Proof 3 — Two gfa layers, different floors, same page', pass, [
    'all objects on page 7 (single page) = ' + onePageOnly,
    'byFloorRole floor:1.gfa = ' + f1.toFixed(2) + '  floor:2.gfa = ' + f2.toFixed(2),
    'distinct buckets (60 / 90) = ' + distinct,
    'floor:1.gfa + floor:2.gfa = ' + (f1 + f2).toFixed(2) + '  vs  byRole.gfa = ' + br.gfa.area.toFixed(2) + '  -> equal = ' + sumEqualsRole,
    'oracle.ok = ' + oracleOk
  ]);
}

/* --- PROOF 4: CFSS master floorKey:"multi" -> per-instance page ------------ */
function proof4() {
  LAYERS = defaultLayers();
  pageTags = { 1: 'floor', 2: 'floor' };
  pageFloorNum = { 1: 1, 2: 2 };
  pageFloorKind = { 1: 'normal', 2: 'normal' };
  excluded = {};
  // Master carries floorKey:"multi" — the cross-floor sentinel.
  MASTERS = { m2: { id: 'm2', catId: 'gfa', floorKey: 'multi', metricPts: rectM(5, 5) } }; // area 25
  PS = {
    1: { scale: pageScale1(), objects: [{ kind: 'instance', masterId: 'm2' }] },  // floor:1
    2: { scale: pageScale1(), objects: [{ kind: 'instance', masterId: 'm2' }] }   // floor:2
  };

  // "Today" = deriveOld (instance floorKey = its page). "New" = deriveNew.
  var tOld = objectTuples(deriveOld), tNew = objectTuples(deriveNew);
  var bfrOld = byFloorRole(tOld), bfrNew = byFloorRole(tNew);
  var f1 = (bfrNew['floor:1'] && bfrNew['floor:1'].gfa && bfrNew['floor:1'].gfa.area) || 0;
  var f2 = (bfrNew['floor:2'] && bfrNew['floor:2'].gfa && bfrNew['floor:2'].gfa.area) || 0;
  var followsInstancePage = Math.abs(f1 - 25) < 1e-9 && Math.abs(f2 - 25) < 1e-9;
  var identicalToToday = eq(bfrOld, bfrNew) && eq(byFloor(tOld), byFloor(tNew));
  var oracleOk = oracle(tNew).ok && oracle(tOld).ok;
  var pass = followsInstancePage && identicalToToday && oracleOk;

  report('Proof 4 — CFSS master floorKey:"multi" -> per-instance page', pass, [
    'master m2 floorKey="multi", area 25, instances on p1(floor:1) + p2(floor:2)',
    'byFloorRole new: floor:1.gfa=' + f1.toFixed(2) + '  floor:2.gfa=' + f2.toFixed(2),
    'per-floor totals follow INSTANCE page = ' + followsInstancePage,
    'identical to today (deriveOld == deriveNew) = ' + identicalToToday,
    'oracle old.ok & new.ok = ' + oracleOk
  ]);
}

/* ============================================================================ */
console.log('SPIKE — INV-20260703-layer-floorkey  (Approach A: layer.floorKey ?? page)');
proof1(); proof2(); proof3(); proof4();

console.log('\n' + '='.repeat(78));
console.log('SUMMARY');
console.log('='.repeat(78));
var allPass = true;
RESULTS.forEach(function (r) { console.log('  ' + (r.pass ? 'PASS' : 'FAIL') + '  ' + r.name); if (!r.pass) allPass = false; });
console.log('\n  ' + (allPass ? 'ALL 4 PROOFS PASS' : 'SOME PROOFS FAILED') + '\n');
process.exit(allPass ? 0 : 1);
