/*
 * page_manager_eval.js — Combined eval E1–E16 against the PRODUCTION module.
 * Run: node lite/tests/page_manager_eval.js
 *
 * Ported from:
 *   lite/sandbox/invent-page-manager/eval.js     (E1–E6)
 *   lite/sandbox/invent-page-manager/eval-v2.js  (E7–E12)
 *   lite/sandbox/invent-page-manager/eval-v3.js  (E13–E16)
 *
 * All three suites run against the PRODUCTION module:
 *   lite/static/js/page-manager.js
 *
 * Adaptations from the sandbox originals (required by Re-pass #2 corrections):
 *   E1/E2: v1 used separate tag_by_id/rot_by_id/excl_by_id dicts.
 *          Production uses meta_by_id. dataOf() adapted accordingly.
 *   E6:    v1 passed page count to simulateFlush(). Production takes no arg.
 *   E8:    v2 tested groupMarkers() (folder membership stored internally).
 *          Production drops groups — folder membership is DERIVED.
 *          E8 now tests: (a) liteGroups round-trip persists correctly via save/load,
 *          and (b) deriveFolderMap() correctly reflects membership after mutations.
 *   E13/E14/E16: ported verbatim (already targeted production module's contract).
 *   All other cases (E3–E5, E7, E9–E12, E15): ported with minimal mechanical fixes.
 *
 * Prints one line per case (PASS/FAIL id desc).
 * Final line: LITE_PAGE_MANAGER_OK (exit 0) or FAIL list (exit 1).
 */

'use strict';

var path   = require('path');
var PageModel = require(path.join(__dirname, '..', 'static', 'js', 'page-manager.js'));
var eq = PageModel.deepEq;

var results = [];
function check(id, kind, desc, cond) {
  results.push({ id: id, kind: kind, desc: desc, pass: !!cond });
}

// Reset the id counter before each eval block so ids are deterministic.
function resetIds() { PageModel._resetIdc(); }

// ============================================================
// Shared fixtures
// ============================================================

// v1-style initial doc (E1–E6)
function makeInitialDocV1() {
  return {
    version: 1,
    pageStore: {
      '1': { objects: ['A'] }, '2': { objects: ['B'] }, '3': { objects: ['C'] },
      '4': { objects: ['D'] }, '5': { objects: ['E'] },
    },
    pageTags:  { '1': 'tA', '2': 'tB', '3': 'tC', '4': 'tD', '5': 'tE' },
    pageRot:   { '1': 0, '2': 90, '3': 180, '4': 270, '5': 0 },
    excluded:  { '2': true, '4': true },   // B and D excluded (legacy dict form)
    pageIdentities: ['idA', 'idB', 'idC', 'idD', 'idE'],
  };
}

// full v2-style doc with all 7 per-page fields + liteGroups (E7–E12)
function fullDocV2() {
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
    excludedPages: [2, 4],
    liteGroups: [
      { id: 'g1', name: 'Plans',  kind: 'plan',  pages: [1, 3, 5] },   // A,C,E
      { id: 'g2', name: 'Floors', kind: 'floor', pages: [2, 4] },      // B,D
    ],
  };
}

// v3-style doc: tags that map to real page-folders, liteGroups empty (E13–E16)
function fullDocV3() {
  return {
    version: 1, app: 'bma-plan-lite',
    pageIdentities: ['idA', 'idB', 'idC', 'idD', 'idE'],
    pageStore: { '1': { objects: ['A'] }, '2': { objects: ['B'] }, '3': { objects: ['C'] },
                 '4': { objects: ['D'] }, '5': { objects: ['E'] } },
    pageRotations: { '1': 0, '2': 90, '3': 180, '4': 270, '5': 0 },
    pageTags:   { '1': 'site', '2': 'floor', '3': 'floor', '4': 'floor', '5': 'site' },
    pageNames:  { '1': 'nA', '2': 'nB', '3': 'nC', '4': 'nD', '5': 'nE' },
    pageFloorKind: { '2': 'normal', '3': 'normal', '4': 'basement' },
    pageFloorNum:  { '2': 1, '3': 2, '4': 1 },
    excludedPages: [],
    liteGroups: [],   // page-folders are DERIVED, not stored as membership
  };
}

// ---- helpers ----
function idByMarker(m, mk) {
  for (var i = 0; i < m.pageOrder.length; i++) {
    var id = m.pageOrder[i];
    if (m.PS_by_id[id] && m.PS_by_id[id].objects.indexOf(mk) >= 0) return id;
  }
  return null;
}
function markerOrder(m) {
  return m.pageOrder.map(function (id) { return m.PS_by_id[id].objects[0]; });
}

// Production dataOf: reads from meta_by_id (collapsed from v1's 4 separate dicts).
function dataOf(m, id) {
  var mt = m.meta_by_id[id] || PageModel.blankMeta();
  return {
    ps:   m.PS_by_id[id],
    tag:  mt.tag,
    rot:  mt.rot,
    excl: !!mt.excl,
  };
}

// ============================================================
// E1–E6 (happy-path suite, ported from eval.js)
// ============================================================
(function () {
  resetIds();
  var m = new PageModel();
  m.load(makeInitialDocV1());

  var ID = {
    A: idByMarker(m, 'A'), B: idByMarker(m, 'B'), C: idByMarker(m, 'C'),
    D: idByMarker(m, 'D'), E: idByMarker(m, 'E'),
  };

  // Capture original per-marker data for E1
  var ORIG = {};
  ['A','B','C','D','E'].forEach(function (k) { ORIG[k] = dataOf(m, ID[k]); });

  // Sequence: move p5->pos2 ; delete C ; duplicate B
  m.reorder(4, 1);                           // A,E,B,C,D
  m.del(m.numOf(ID.C) - 1);                 // A,E,B,D
  m.duplicate(m.numOf(ID.B) - 1);           // A,E,B,B',D

  // E1: survivors keep correct object/tag/rot/excl BY IDENTITY
  var e1 = ['A','B','D','E'].every(function (k) { return eq(dataOf(m, ID[k]), ORIG[k]); });
  var orderMarkers = m.pageOrder.map(function (id) { return m.PS_by_id[id].objects[0]; });
  e1 = e1 && eq(orderMarkers, ['A','E','B','B','D']);
  check('E1', 'happy', 'survivors keep correct object/tag/rot/excluded by identity (no shift)', e1);

  // E2: C fully gone — no id, no orphan in any dict
  var cId = ID.C;
  var e2 = m.pageOrder.indexOf(cId) < 0 &&
           !(cId in m.PS_by_id) && !(cId in m.meta_by_id) && !(cId in m.originNum) &&
           idByMarker(m, 'C') === null;
  check('E2', 'happy', '"C" and all its data fully removed, zero orphans', e2);

  // E3: duplicate B' is an INDEPENDENT copy
  var bpIdx = m.numOf(ID.B);
  var bpId  = m.pageOrder[bpIdx];
  var e3a = bpId !== ID.B && eq(m.PS_by_id[bpId].objects, ['B']);
  m.PS_by_id[bpId].objects.push('EDIT');
  var e3 = e3a && eq(m.PS_by_id[bpId].objects, ['B','EDIT']) &&
           eq(m.PS_by_id[ID.B].objects, ['B']);
  check('E3', 'happy', 'duplicate is an independent deep copy (edit copy ≠ edit original)', e3);

  // E4: save -> reload deep-equal
  var before = m.snapshotByOrder();
  var doc = m.save();
  var m2 = new PageModel(); m2.load(doc);
  var e4 = eq(before, m2.snapshotByOrder()) && eq(m.pageOrder, m2.pageOrder);
  check('E4', 'happy', 'save→.bmaplan→reload round-trips deep-equal', e4);

  // E5: legacy (no pageIdentities) loads + auto-migrates
  var legacy = makeInitialDocV1();
  delete legacy.pageIdentities;
  var m3 = new PageModel(); m3.load(legacy);
  var e5 = m3._migratedFromLegacy === true && m3.count() === 5 &&
           eq(m3.pageOrder.map(function (id) { return m3.PS_by_id[id].objects[0]; }),
              ['A','B','C','D','E']) &&
           m3.pageOrder.every(function (id) { return typeof id === 'string'; }) &&
           m3.pageOrder.indexOf('idA') < 0;
  check('E5', 'happy', 'legacy number-keyed save loads + auto-migrates to id-keyed', e5);

  // E6: journal replay renumber-map matches live UI index 1:1
  // Production simulateFlush() takes no argument (v1 eval passed page count — dropped).
  var flush = m.simulateFlush();
  var liveMap = {};
  m.pageOrder.forEach(function (id, i) {
    if (m.originNum[id] != null) liveMap[m.originNum[id]] = i + 1;
  });
  var e6 = eq(flush.renumberMap, liveMap) && eq(flush.order, m.pageOrder);
  check('E6', 'happy', 'server renumber-map (journal replay) == live UI index 1:1', e6);
})();

// ============================================================
// E7–E12 (edge + adversarial, ported from eval-v2.js)
// ============================================================

// E7: all 7 per-page fields survive by identity
(function () {
  resetIds();
  var m = new PageModel(); m.load(fullDocV2());
  var ID = {};
  ['A','B','C','D','E'].forEach(function (k) { ID[k] = idByMarker(m, k); });
  var origMeta = {};
  ['A','B','C','D','E'].forEach(function (k) { origMeta[k] = JSON.stringify(m.meta_by_id[ID[k]]); });

  m.reorder(4, 1);
  m.del(m.numOf(ID.C) - 1);
  m.duplicate(m.numOf(ID.B) - 1);

  var survivorsKeepAll = ['A','B','D','E'].every(function (k) {
    return JSON.stringify(m.meta_by_id[ID[k]]) === origMeta[k];
  });
  var dPage = m.numOf(ID.D);
  var dMetaOk = m.metaN(dPage).floorKind === 'basement' &&
                m.metaN(dPage).floorNum  === -1 &&
                m.metaN(dPage).name      === 'nD' &&
                m.metaN(dPage).excl      === true;
  check('E7', 'edge',
    'all 7 per-page fields (incl floorKind/floorNum/name) survive reorder/delete/dup by identity',
    survivorsKeepAll && dMetaOk && eq(markerOrder(m), ['A','E','B','B','D']));
})();

// E8: liteGroups persist correctly on save/load + deriveFolderMap reflects correct membership.
// ADAPTATION from eval-v2.js E8: production drops internal id-keyed group maintenance.
// Test now verifies: (a) liteGroups raw array passes through save/load unchanged,
// (b) deriveFolderMap() reflects correct page-number membership by tag/floor metadata
//     for pages that have tag='site' or 'floor' (the two it can derive).
// Note: the fullDocV2() doc uses tags like 'plan'/'parking'/'detail' that don't map to
// real page-folders (they fall into PF_excluded). Site page (A, tag='site') maps to PF_site.
// Floor-tagged pages (B, tag='floor', floorKind='normal', floorNum=1) maps to PF_floor_1.
(function () {
  resetIds();
  var m = new PageModel(); m.load(fullDocV2());
  var ID = {};
  ['A','B','C','D','E'].forEach(function (k) { ID[k] = idByMarker(m, k); });

  // (a) liteGroups round-trip: save → reload preserves liteGroups verbatim
  var saved1 = m.save();
  var m2 = new PageModel(); m2.load(saved1);
  var groupsRoundTrip = eq(m2._savedGroups, m._savedGroups);

  // (b) After mutations, deriveFolderMap reflects correct membership for
  //     pages with known tags (A=site->PF_site; B=floor/normal/1->PF_floor_1).
  m.reorder(4, 1);                    // A,E,B,C,D
  m.del(m.numOf(ID.C) - 1);          // A,E,B,D  (C with tag='plan' gone)
  m.duplicate(m.numOf(ID.B) - 1);    // A,E,B,B',D (B' inherits floor-1 meta)

  // After mutations: order = A(1),E(2),B(3),B'(4),D(5)
  // A: tag='site' -> PF_site at page 1
  // E: tag='detail' -> PF_excluded at page 2
  // B: tag='floor', normal, 1 -> PF_floor_1 at page 3
  // B': same meta as B -> PF_floor_1 at page 4
  // D: tag='parking' -> PF_excluded at page 5
  var dfm = m.deriveFolderMap();
  var siteOk    = eq(dfm['PF_site'],    [1]);
  var floor1Ok  = eq(dfm['PF_floor_1'], [3, 4]);
  var excludedOk = eq(dfm['PF_excluded'].sort(function(a,b){return a-b;}), [2,5]);

  check('E8', 'adversarial',
    'liteGroups round-trip via save/load + deriveFolderMap() reflects correct membership after mutation',
    groupsRoundTrip && siteOk && floor1Ok && excludedOk);
})();

// E9: double flush re-baselines the journal
(function () {
  resetIds();
  var m = new PageModel(); m.load(fullDocV2());
  var ID = {};
  ['A','B','C','D','E'].forEach(function (k) { ID[k] = idByMarker(m, k); });

  // Round 1: delete C then flush
  m.del(m.numOf(ID.C) - 1);
  var f1 = m.simulateFlush();
  var f1ok = eq(f1.renumberMap, { 1: 1, 2: 2, 4: 3, 5: 4 });
  m.applyFlush();

  // Round 2 on the new baseline: move D (now #3) to front
  var dNow = m.numOf(ID.D);
  m.reorder(dNow - 1, 0);            // D,A,B,E
  var f2 = m.simulateFlush();
  var f2ok = eq(f2.renumberMap, { 3: 1, 1: 2, 2: 3, 4: 4 });
  var pendingClean = m.pending.length === 1 && m.pending[0].type === 'reorder';

  check('E9', 'adversarial',
    'second save re-baselines: renumberMap is relative to the post-flush PDF, not the original',
    f1ok && f2ok && pendingClean);
})();

// E10: render-source maps to original server page pre-flush
(function () {
  resetIds();
  var m = new PageModel(); m.load(fullDocV2());
  var ID = {};
  ['A','B','C','D','E'].forEach(function (k) { ID[k] = idByMarker(m, k); });

  m.reorder(4, 1);                   // display: A,E,B,C,D (server PDF still A,B,C,D,E)
  var renderE = m.serverNum(2) === 5;   // display 2 = E, original server page = 5
  var renderB = m.serverNum(3) === 2;   // display 3 = B, server page = 2

  m.duplicate(1);                    // dup display-2 (E) -> copy at display 3
  var dupRendersFromSource = m.serverNum(3) === 5;   // copy renders from E's server page (5)

  m.applyFlush();
  var afterFlush = m.serverNum(3) === 3;   // post-flush, copy is now server page 3

  check('E10', 'adversarial',
    'pre-flush render-source: serverNum(n) hits the original server page; dup renders from source; flush re-bases it',
    renderE && renderB && dupRendersFromSource && afterFlush);
})();

// E11: merge foreign pages, reorder, flush
(function () {
  resetIds();
  var m = new PageModel(); m.load(fullDocV2());   // A..E

  var merged = m.merge(2);                         // append X,Y -> A,B,C,D,E,X,Y
  m.PS_by_id[merged[0]].objects = ['X'];
  m.PS_by_id[merged[1]].objects = ['Y'];
  m.reorder(5, 0);                                 // move X to front -> X,A,B,C,D,E,Y

  var f = m.simulateFlush();
  var mapOk    = eq(f.renumberMap, { 1: 2, 2: 3, 3: 4, 4: 5, 5: 6 });
  var orderOk  = eq(f.order, m.pageOrder);
  var orderMarkers = eq(markerOrder(m), ['X','A','B','C','D','E','Y']);

  var mergePlaceholder = m.serverNum(1) === null;  // merged page has no server source pre-flush
  m.applyFlush();
  var mergeReal = m.serverNum(1) === 1;            // post-flush, page 1 on the server

  check('E11', 'edge',
    'merge appends foreign pages; flush renumbers originals + assigns merged pages; placeholder→real',
    mapOk && orderOk && orderMarkers && mergePlaceholder && mergeReal);
})();

// E12: delete-last guard + legacy excludedPages-array migration
(function () {
  resetIds();
  // Delete-last guard
  var one = new PageModel();
  one.load({ pageStore: { '1': { objects: ['Z'] } } });
  var refused = (one.del(0) === false) && one.count() === 1;

  // Legacy migration: no pageIdentities, excludedPages as ARRAY, sparse floor map
  var legacy = fullDocV2();
  delete legacy.pageIdentities;
  var m = new PageModel(); m.load(legacy);
  var migrated = m._migratedFromLegacy === true && m.count() === 5 &&
                 eq(markerOrder(m), ['A','B','C','D','E']) &&
                 m.pageOrder.indexOf('idA') < 0 &&
                 m.metaN(2).excl === true &&
                 m.metaN(4).excl === true &&
                 m.metaN(4).floorKind === 'basement';

  // liteGroups round-trip from legacy (number-keyed groups still load via _savedGroups)
  var g = m._savedGroups.find(function (x) { return x.name === 'Plans'; });
  var groupsMigrated = g && eq(g.pages.slice().sort(function(a,b){return a-b;}), [1,3,5]);

  check('E12', 'edge',
    'delete-last refused (doc keeps ≥1 page) + legacy (no ids, excludedPages-array, folders) migrates',
    refused && migrated && groupsMigrated);
})();

// ============================================================
// E13–E16 (3rd-pass corrections, ported from eval-v3.js)
// ============================================================

// E13: folder membership is DERIVED correctly after mutation (C-FOLDER)
(function () {
  resetIds();
  var m = new PageModel(); m.load(fullDocV3());
  var ID = {};
  ['A','B','C','D','E'].forEach(function (k) { ID[k] = idByMarker(m, k); });

  // Initial: site={A(1),E(5)}, PF_floor_1={B(2)}, PF_floor_2={C(3)}, PF_basement_1={D(4)}
  var f0 = m.deriveFolderMap();
  var initOk = eq(f0['PF_site'], [1, 5]) && eq(f0['PF_floor_1'], [2]) &&
               eq(f0['PF_floor_2'], [3]) && eq(f0['PF_basement_1'], [4]);

  // Mutate: move E(5)->pos2; delete C; duplicate B
  m.reorder(4, 1);                   // A,E,B,C,D
  m.del(m.numOf(ID.C) - 1);         // A,E,B,D  (PF_floor_2 now empty → must vanish)
  m.duplicate(m.numOf(ID.B) - 1);   // A,E,B,B',D (B' inherits floor-1 normal)

  // Display now A(1),E(2),B(3),B'(4),D(5):
  // site={1,2}, PF_floor_1={3,4}, PF_basement_1={5}
  var f1 = m.deriveFolderMap();
  var afterOk = eq(f1['PF_site'], [1, 2]) &&
                eq(f1['PF_floor_1'], [3, 4]) &&
                eq(f1['PF_basement_1'], [5]) &&
                !('PF_floor_2' in f1);   // deleted floor gone

  check('E13', 'adversarial',
    'page-folder .pages RE-DERIVES correctly after reorder/delete/dup (folder id is floor-based, membership is computed not stored)',
    initOk && afterOk);
})();

// E13b: user/legacy folders carry LAYERS not pages → nothing to corrupt
(function () {
  resetIds();
  var doc = fullDocV3();
  doc.liteGroups = [{ id: 'F1', name: 'My group', kind: undefined }];  // no .pages
  var m = new PageModel(); m.load(doc);
  m.reorder(4, 0);
  m.del(0);
  // A user folder has no page membership; save passes it through without inventing .pages
  var saved = m.save().liteGroups.find(function (g) { return g.id === 'F1'; });
  // Production save emits _savedGroups verbatim, so pages is undefined/missing on the raw group.
  // The v3 spec accepts: saved.pages is either empty array OR undefined (no spurious page refs).
  var ok = saved && (!saved.pages || (Array.isArray(saved.pages) && saved.pages.length === 0));
  check('E13b', 'edge',
    'user/legacy folder (no page membership) survives mutation without spurious page refs', ok);
})();

// E14: dirty-tracking contract — every page mutation changes the snapshot
(function () {
  resetIds();
  var m = new PageModel(); m.load(fullDocV3());
  var ID = {};
  ['A','B','C','D','E'].forEach(function (k) { ID[k] = idByMarker(m, k); });

  var before       = m.dirtySnap();
  m.reorder(0, 3);
  var afterReorder = m.dirtySnap();
  m.duplicate(0);
  var afterDup     = m.dirtySnap();
  m.del(m.numOf(ID.B) - 1);
  var afterDel     = m.dirtySnap();

  check('E14', 'adversarial',
    'dirty-tracking: pure reorder/duplicate/delete each changes the doc snapshot (build must expose dirtySnap() covering pageOrder+meta)',
    before !== afterReorder && afterReorder !== afterDup && afterDup !== afterDel);
})();

// E15: duplicate then delete original — copy keeps independent data
(function () {
  resetIds();
  var m = new PageModel(); m.load(fullDocV3());
  var bId = idByMarker(m, 'B');
  m.duplicate(m.numOf(bId) - 1);                // B' after B
  var copyId = m.pageOrder[m.numOf(bId)];       // the copy sits right after B
  m.del(m.numOf(bId) - 1);                      // delete the ORIGINAL B

  var copyAlive = m.pageOrder.indexOf(copyId) >= 0;
  var copyData  = m.PS_by_id[copyId] && eq(m.PS_by_id[copyId].objects, ['B']) &&
                  m.meta_by_id[copyId] && m.meta_by_id[copyId].floorNum === 1;
  m.PS_by_id[copyId].objects.push('Z');
  var independent = eq(m.PS_by_id[copyId].objects, ['B','Z']) && !(bId in m.PS_by_id);

  check('E15', 'edge',
    'duplicate then delete original: copy survives with independent data (no shared reference)',
    copyAlive && copyData && independent);
})();

// E16: no-op reorder (same index) must not corrupt journal/flush (B-NOOP)
(function () {
  resetIds();
  var m = new PageModel(); m.load(fullDocV3());
  var ord0 = m.pageOrder.slice();

  m.reorder(2, 2);                               // move index 2 to index 2 = no-op

  var sameOrder = eq(m.pageOrder, ord0);
  var f = m.simulateFlush();
  var identityMap = eq(f.renumberMap, { 1: 1, 2: 2, 3: 3, 4: 4, 5: 5 });
  var orderConsistent = eq(f.order, m.pageOrder);
  // No snapshot should have been taken (undoStack stays empty)
  var noSnapshot = m.undoStack.length === 0;

  check('E16', 'edge',
    'no-op reorder (same index) keeps order + yields identity renumber-map + no snapshot taken',
    sameOrder && identityMap && orderConsistent && noSnapshot);
})();

// ============================================================
// REPORT
// ============================================================
var pass = results.filter(function (r) { return r.pass; }).length;
var total = results.length;

console.log('\n=== page-manager production module eval (E1–E16) ===');
results.forEach(function (r) {
  console.log((r.pass ? 'PASS' : 'FAIL') + '  ' + r.id + ' [' + r.kind + ']  ' + r.desc);
});
console.log('----------------------------------------------------');
console.log('RESULT: ' + pass + '/' + total);

if (pass === total) {
  console.log('LITE_PAGE_MANAGER_OK');
  process.exit(0);
} else {
  var failing = results.filter(function (r) { return !r.pass; }).map(function (r) { return r.id; });
  console.log('FAIL cases: ' + failing.join(', '));
  process.exit(1);
}
