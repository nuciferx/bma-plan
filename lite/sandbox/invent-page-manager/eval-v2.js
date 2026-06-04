/*
 * eval-v2.js — EXTENDED RUNNABLE EVAL for the lite-page-manager spike (re-pass).
 * Run: node lite/sandbox/invent-page-manager/eval-v2.js
 *
 * v1 eval.js = E1..E6, all HAPPY-path on one 5-page dense scenario. The skill's
 * own rule: "Eval taxonomy, not one case: ≥3 cases (happy + edge + adversarial)".
 * This file adds the EDGE + ADVERSARIAL cases the re-pass identified, each aimed
 * at a real corruption mode found in the lite codebase recon (2026-05-29):
 *
 *   E7  (edge)        all 7 per-page fields survive by identity (incl floorKind/Num/name)
 *   E8  (ADVERSARIAL) liteGroups page-folder membership stays correct + saves as numbers
 *   E9  (ADVERSARIAL) double flush — 2nd renumberMap is relative to the post-flush PDF
 *   E10 (ADVERSARIAL) render-source: serverNum(n) points at the ORIGINAL server page pre-flush
 *   E11 (edge)        merge appends foreign pages; flush renumbers originals + assigns merged
 *   E12 (edge)        delete-last guard + legacy excludedPages-array migration
 *
 * tolerance 0 (data integrity = no partial). This IS the phase-6 acceptance gate.
 */
var PageModel = require('./page-model-v2.js');
var eq = PageModel.deepEq;

var results = [];
function check(id, kind, desc, cond) { results.push({ id: id, kind: kind, desc: desc, pass: !!cond }); }

/* ---- a FULL lite-shaped doc: 7 per-page fields + 2 page folders ---- */
function fullDoc() {
  return {
    version: 1, app: 'bma-plan-lite',
    pageIdentities: ['idA', 'idB', 'idC', 'idD', 'idE'],
    pageStore: { '1': { objects: ['A'] }, '2': { objects: ['B'] }, '3': { objects: ['C'] },
                 '4': { objects: ['D'] }, '5': { objects: ['E'] } },
    pageRotations: { '1': 0, '2': 90, '3': 180, '4': 270, '5': 0 },
    pageTags:   { '1': 'site', '2': 'floor', '3': 'plan', '4': 'parking', '5': 'detail' },
    pageNames:  { '1': 'nA', '2': 'nB', '3': 'nC', '4': 'nD', '5': 'nE' },
    pageFloorKind: { '2': 'normal', '3': 'mechanical', '4': 'basement' },
    pageFloorNum:  { '2': 1, '3': 2, '4': -1 },
    excludedPages: [2, 4],                                  // lite ARRAY form
    liteGroups: [
      { id: 'g1', name: 'Plans',  kind: 'plan',  pages: [1, 3, 5] },   // A,C,E
      { id: 'g2', name: 'Floors', kind: 'floor', pages: [2, 4] },      // B,D
    ],
  };
}

function idByMarker(m, mk) {
  for (var i = 0; i < m.pageOrder.length; i++) {
    var id = m.pageOrder[i];
    if (m.PS_by_id[id] && m.PS_by_id[id].objects.indexOf(mk) >= 0) return id;
  }
  return null;
}
function markerOrder(m) { return m.pageOrder.map(function (id) { return m.PS_by_id[id].objects[0]; }); }

/* ===================== E7 — edge: all 7 fields survive by identity ===================== */
(function () {
  var m = new PageModel(); m.load(fullDoc());
  var ID = {}; ['A','B','C','D','E'].forEach(function (k) { ID[k] = idByMarker(m, k); });
  var origMeta = {}; ['A','B','C','D','E'].forEach(function (k) { origMeta[k] = JSON.stringify(m.meta_by_id[ID[k]]); });
  // move E(5)->pos2, delete C, duplicate B
  m.reorder(4, 1);
  m.del(m.numOf(ID.C) - 1);
  m.duplicate(m.numOf(ID.B) - 1);
  var survivorsKeepAll = ['A','B','D','E'].every(function (k) {
    return JSON.stringify(m.meta_by_id[ID[k]]) === origMeta[k];   // tag+rot+excl+floorKind+floorNum+name all intact
  });
  // explicitly assert the 3 fields v1 DID NOT model are correct on a shifted page
  var dPage = m.numOf(ID.D);
  var dMetaOk = m.metaN(dPage).floorKind === 'basement' && m.metaN(dPage).floorNum === -1 &&
                m.metaN(dPage).name === 'nD' && m.metaN(dPage).excl === true;
  check('E7', 'edge', 'all 7 per-page fields (incl floorKind/floorNum/name) survive reorder/delete/dup by identity',
        survivorsKeepAll && dMetaOk && eq(markerOrder(m), ['A','E','B','B','D']));
})();

/* ============ E8 — ADVERSARIAL: page-folder (liteGroups) membership integrity ============ */
(function () {
  var m = new PageModel(); m.load(fullDoc());
  var ID = {}; ['A','B','C','D','E'].forEach(function (k) { ID[k] = idByMarker(m, k); });
  m.reorder(4, 1);                       // A,E,B,C,D
  m.del(m.numOf(ID.C) - 1);             // delete C  -> Plans folder must lose C
  m.duplicate(m.numOf(ID.B) - 1);      // dup B     -> B' inherits B's folder (Floors)
  var gm = m.groupMarkers();
  var plans  = gm.find(function (g) { return g.name === 'Plans'; });
  var floors = gm.find(function (g) { return g.name === 'Floors'; });
  // Plans had A,C,E -> C deleted -> {A,E}; Floors had B,D -> +B' -> {B,B',D}
  var plansOk  = eq(plans.pages.slice().sort(),  ['A', 'E'].sort());
  var floorsOk = eq(floors.pages.filter(Boolean).sort(), ['B', 'B', 'D'].sort());
  // and on SAVE, membership must serialise as the correct DISPLAY NUMBERS
  var doc = m.save();
  var savedPlans = doc.liteGroups.find(function (g) { return g.id === 'g1'; }).pages;
  // live order A,E,B,B',D => A=1, E=2  => Plans numbers = [1,2]
  var savedNumsOk = eq(savedPlans, [1, 2]);
  // round-trip: reload, Plans still {A,E} by identity
  var m2 = new PageModel(); m2.load(doc);
  var gm2 = m2.groupMarkers().find(function (g) { return g.name === 'Plans'; });
  var rtOk = eq(gm2.pages.slice().sort(), ['A', 'E'].sort());
  check('E8', 'adversarial', 'page-folder membership follows identity (no stale/dead page refs) + saves as correct numbers + round-trips',
        plansOk && floorsOk && savedNumsOk && rtOk);
})();

/* ============ E9 — ADVERSARIAL: double flush re-baselines the journal ============ */
(function () {
  var m = new PageModel(); m.load(fullDoc());
  var ID = {}; ['A','B','C','D','E'].forEach(function (k) { ID[k] = idByMarker(m, k); });
  // round 1: delete C, then flush (server applies, client re-baselines)
  m.del(m.numOf(ID.C) - 1);            // A,B,D,E
  var f1 = m.simulateFlush();          // originals 1,2,4,5 -> 1,2,3,4
  var f1ok = eq(f1.renumberMap, { 1: 1, 2: 2, 4: 3, 5: 4 });
  m.applyFlush();
  // round 2 on the NEW baseline: move D(now #3) to front
  var dNow = m.numOf(ID.D);            // 3
  m.reorder(dNow - 1, 0);             // D,A,B,E
  var f2 = m.simulateFlush();
  // CRITICAL: f2 must be relative to the POST-flush PDF (A=1,B=2,D=3,E=4 before move),
  // i.e. D:3->1, A:1->2, B:2->3, E:4->4 — NOT relative to the original 5-page PDF.
  var f2ok = eq(f2.renumberMap, { 3: 1, 1: 2, 2: 3, 4: 4 });
  // and pending was cleared by applyFlush (round-2 journal has only the reorder)
  var pendingClean = m.pending.length === 1 && m.pending[0].type === 'reorder';
  check('E9', 'adversarial', 'second save re-baselines: renumberMap is relative to the post-flush PDF, not the original',
        f1ok && f2ok && pendingClean);
})();

/* ============ E10 — ADVERSARIAL: render-source maps to original server page pre-flush ============ */
(function () {
  var m = new PageModel(); m.load(fullDoc());
  var ID = {}; ['A','B','C','D','E'].forEach(function (k) { ID[k] = idByMarker(m, k); });
  m.reorder(4, 1);                      // display: A,E,B,C,D   (server PDF still A,B,C,D,E)
  // display page 2 is now E, whose ORIGINAL server page was 5 -> render must fetch /page/5
  var renderE = m.serverNum(2) === 5;
  var renderB = m.serverNum(3) === 2;  // display 3 = B, server 2
  m.duplicate(1);                       // duplicate display-2 (E) -> copy renders from E's server page (5)
  var copyNum = m.numOf(m.pageOrder[2]); // the new copy sits at display 3
  var dupRendersFromSource = m.serverNum(3) === 5;
  // after flush the copy is a real server page; serverNum becomes its own new index
  m.applyFlush();
  var afterFlush = m.serverNum(3) === 3;
  check('E10', 'adversarial', 'pre-flush render-source: serverNum(n) hits the original server page; dup renders from source; flush re-bases it',
        renderE && renderB && dupRendersFromSource && afterFlush);
})();

/* ============ E11 — edge: merge foreign pages, reorder, flush ============ */
(function () {
  var m = new PageModel(); m.load(fullDoc());   // A..E
  var merged = m.merge(2);                        // append X,Y  -> A,B,C,D,E,X,Y
  m.PS_by_id[merged[0]].objects = ['X'];
  m.PS_by_id[merged[1]].objects = ['Y'];
  m.reorder(5, 0);                                // move X to front -> X,A,B,C,D,E,Y
  var f = m.simulateFlush();
  // originals A..E were 1..5; after [merge X,Y][move X→front]: X,A,B,C,D,E,Y
  // so 1->2,2->3,3->4,4->5,5->6 ; merged pages get 1 (X) and 7 (Y), no orig entry
  var mapOk = eq(f.renumberMap, { 1: 2, 2: 3, 3: 4, 4: 5, 5: 6 });
  var orderOk = eq(f.order, m.pageOrder);        // journal replay == live order
  var orderMarkers = eq(markerOrder(m), ['X', 'A', 'B', 'C', 'D', 'E', 'Y']);
  // merged pages render-source is null pre-flush (placeholder), real after flush
  var mergePlaceholder = m.serverNum(1) === null;
  m.applyFlush();
  var mergeReal = m.serverNum(1) === 1;
  check('E11', 'edge', 'merge appends foreign pages; flush renumbers originals + assigns merged pages; placeholder→real',
        mapOk && orderOk && orderMarkers && mergePlaceholder && mergeReal);
})();

/* ============ E12 — edge: delete-last guard + legacy excludedPages-array migration ============ */
(function () {
  // delete-last guard
  var one = new PageModel(); one.load({ pageStore: { '1': { objects: ['Z'] } } });
  var refused = (one.del(0) === false) && one.count() === 1;
  // legacy migration: NO pageIdentities, excluded as ARRAY, a sparse floor map
  var legacy = fullDoc(); delete legacy.pageIdentities;
  var m = new PageModel(); m.load(legacy);
  var migrated = m._migratedFromLegacy === true && m.count() === 5 &&
                 eq(markerOrder(m), ['A', 'B', 'C', 'D', 'E']) &&
                 m.pageOrder.indexOf('idA') < 0 &&                 // fresh ids minted
                 m.metaN(2).excl === true && m.metaN(4).excl === true &&   // excludedPages array honoured
                 m.metaN(4).floorKind === 'basement';
  // groups still resolved by number even without ids
  var g = m.groupMarkers().find(function (x) { return x.name === 'Plans'; });
  var groupsMigrated = eq(g.pages.slice().sort(), ['A', 'C', 'E'].sort());
  check('E12', 'edge', 'delete-last refused (doc keeps ≥1 page) + legacy (no ids, excludedPages-array, folders) migrates',
        refused && migrated && groupsMigrated);
})();

/* ---- REPORT ---- */
var pass = results.filter(function (r) { return r.pass; }).length;
console.log('\n=== lite-page-manager SPIKE v2 eval (edge + adversarial taxonomy) ===');
results.forEach(function (r) {
  console.log((r.pass ? 'PASS' : 'FAIL') + '  ' + r.id + ' [' + r.kind + ']  ' + r.desc);
});
console.log('-------------------------------------------------------------------');
console.log('RESULT: ' + pass + '/' + results.length + '  ' +
            (pass === results.length ? 'ACCEPT (v2 closes the gaps)' : 'REJECT'));
process.exit(pass === results.length ? 0 : 1);
