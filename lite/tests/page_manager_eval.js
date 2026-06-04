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
// E17–E20 (Slice 2: seedFromGlobals + projectToGlobals bridge)
// ============================================================

// E17: seed→project round-trip on UNMUTATED model reproduces the input globals
(function () {
  resetIds();
  // Build a representative globals snapshot (live-app form)
  var g = {
    pageCount: 5,
    pageIdentities: ['idA', 'idB', 'idC', 'idD', 'idE'],
    PS: {
      1: { objects: ['A'] }, 2: { objects: ['B'] }, 3: { objects: ['C'] },
      4: { objects: ['D'] }, 5: { objects: ['E'] },
    },
    pageTags:      { 1: 'site', 2: 'floor', 3: 'floor', 4: 'parking', 5: 'detail' },
    pageFloorKind: { 2: 'normal', 3: 'basement' },
    pageFloorNum:  { 2: 1, 3: -1 },
    pageNames:     { 1: 'nA', 2: 'nB', 3: 'nC', 4: 'nD', 5: 'nE' },
    pageRot:       { 2: 90, 3: 180 },
    excluded:      { 2: true, 4: true },
  };

  var m = new PageModel();
  m.seedFromGlobals(g);
  var out = m.projectToGlobals();

  // pageCount + pageIdentities
  var countOk = out.pageCount === 5 && eq(out.pageIdentities, g.pageIdentities);

  // All 5 PS entries have the right objects
  var psOk = [1,2,3,4,5].every(function (n) {
    return out.PS[n] && eq(out.PS[n].objects, g.PS[n].objects);
  });

  // pageTags round-trips (only truthy entries in input)
  var tagsOk = eq(out.pageTags[1], 'site') && eq(out.pageTags[2], 'floor') &&
               eq(out.pageTags[3], 'floor') && eq(out.pageTags[4], 'parking') &&
               eq(out.pageTags[5], 'detail');

  // pageFloorKind + pageFloorNum round-trip for pages that have them
  var fkOk = eq(out.pageFloorKind[2], 'normal') && eq(out.pageFloorKind[3], 'basement') &&
             eq(out.pageFloorNum[2], 1) && eq(out.pageFloorNum[3], -1);

  // pageNames round-trip
  var namesOk = [1,2,3,4,5].every(function (n) { return out.pageNames[n] === 'n' + ['A','B','C','D','E'][n-1]; });

  // pageRot round-trip (only truthy)
  var rotOk = out.pageRot[2] === 90 && out.pageRot[3] === 180 &&
              !out.pageRot[1] && !out.pageRot[4] && !out.pageRot[5];

  // excluded dict: pages 2 and 4 are true; 1,3,5 absent
  var exclOk = out.excluded[2] === true && out.excluded[4] === true &&
               !out.excluded[1] && !out.excluded[3] && !out.excluded[5];

  check('E17', 'happy',
    'seed→project round-trip on unmutated model reproduces all 7 input globals (+ pageCount + pageIdentities)',
    countOk && psOk && tagsOk && fkOk && namesOk && rotOk && exclOk);
})();

// E18: seed 5 pages → reorder+delete+duplicate → projectToGlobals yields correct
//      new numbers per identity and deleted page is fully gone.
(function () {
  resetIds();
  var g = {
    pageCount: 5,
    pageIdentities: ['idA', 'idB', 'idC', 'idD', 'idE'],
    PS: {
      1: { objects: ['A'] }, 2: { objects: ['B'] }, 3: { objects: ['C'] },
      4: { objects: ['D'] }, 5: { objects: ['E'] },
    },
    pageTags:      { 1: 'site', 2: 'floor', 3: 'floor', 4: 'floor', 5: 'detail' },
    pageFloorKind: { 2: 'normal', 3: 'normal', 4: 'basement' },
    pageFloorNum:  { 2: 1, 3: 2, 4: -1 },
    pageNames:     { 1: 'nA', 2: 'nB', 3: 'nC', 4: 'nD', 5: 'nE' },
    pageRot:       { 3: 90 },
    excluded:      { 4: true },
  };

  var m = new PageModel();
  m.seedFromGlobals(g);
  // IDs are the seeded identities
  var ID = { A:'idA', B:'idB', C:'idC', D:'idD', E:'idE' };

  // Operation: move page 4 (index 3, which is D) to front (index 0)
  m.reorder(3, 0);                          // order: D,A,B,C,E  (indices 0-4)
  // delete C (was index 2 in original, now at index 3 in new order D,A,B,C,E)
  m.del(m.numOf(ID.C) - 1);               // D,A,B,E
  // duplicate B (now at index 2 in D,A,B,E)
  m.duplicate(m.numOf(ID.B) - 1);         // D,A,B,B',E

  var out = m.projectToGlobals();

  // pageCount = 5 (D,A,B,B',E)
  var countOk = out.pageCount === 5;

  // pageIdentities: new order
  var idenOk = eq(out.pageIdentities, [ID.D, ID.A, ID.B, m.pageOrder[3], ID.E]);

  // Verify each surviving identity has the correct meta at its new number
  // D at n=1: floorKind=basement, floorNum=-1, excl=true, tag=floor
  var dNum = m.numOf(ID.D);  // should be 1
  var dOk = dNum === 1 &&
            out.pageFloorKind[1] === 'basement' &&
            out.pageFloorNum[1] === -1 &&
            out.excluded[1] === true &&
            out.pageTags[1] === 'floor' &&
            out.PS[1] && eq(out.PS[1].objects, ['D']);

  // A at n=2: tag=site, no excl
  var aNum = m.numOf(ID.A);  // should be 2
  var aOk = aNum === 2 &&
            out.pageTags[2] === 'site' &&
            !out.excluded[2] &&
            out.PS[2] && eq(out.PS[2].objects, ['A']);

  // B at n=3: tag=floor, floorKind=normal, floorNum=1
  var bNum = m.numOf(ID.B);  // should be 3
  var bOk = bNum === 3 &&
            out.pageTags[3] === 'floor' &&
            out.pageFloorKind[3] === 'normal' &&
            out.pageFloorNum[3] === 1 &&
            out.PS[3] && eq(out.PS[3].objects, ['B']);

  // B' at n=4: same meta as B (inherits via deepCopy in duplicate)
  var bpNum = 4;
  var bpOk = out.pageTags[4] === 'floor' &&
             out.pageFloorKind[4] === 'normal' &&
             out.pageFloorNum[4] === 1 &&
             out.PS[4] && eq(out.PS[4].objects, ['B']);

  // E at n=5: tag=detail, no excl, rot absent
  var eNum = m.numOf(ID.E);  // should be 5
  var eOk = eNum === 5 &&
            out.pageTags[5] === 'detail' &&
            !out.excluded[5] &&
            out.PS[5] && eq(out.PS[5].objects, ['E']);

  // C is fully gone: no PS at any number for C, pageIdentities has no 'idC'
  var cGone = out.pageIdentities.indexOf(ID.C) < 0 &&
              [1,2,3,4,5].every(function (n) {
                return !(out.PS[n] && eq(out.PS[n].objects, ['C']));
              });

  check('E18', 'adversarial',
    'seed+reorder+delete+duplicate: projectToGlobals places each identity at correct new number; deleted page absent',
    countOk && idenOk && dOk && aOk && bOk && bpOk && eOk && cGone);
})();

// E19: seedFromGlobals tolerates SPARSE PS — pages without PS entry become blank
(function () {
  resetIds();
  var g = {
    pageCount: 5,
    pageIdentities: ['idA', 'idB', 'idC', 'idD', 'idE'],
    // Only pages 1 and 3 have PS entries; 2, 4, 5 are absent (sparse)
    PS: {
      1: { objects: ['A'] },
      3: { objects: ['C'] },
    },
    pageTags:      { 1: 'site' },
    pageFloorKind: {},
    pageFloorNum:  {},
    pageNames:     {},
    pageRot:       {},
    excluded:      {},
  };

  var m = new PageModel();
  m.seedFromGlobals(g);

  // All 5 ids must exist in pageOrder
  var allExist = m.count() === 5 && m.pageOrder.length === 5;

  // Pages 1 and 3 have their data; pages 2, 4, 5 are blank {objects:[]}
  var p1ok = m.PS_by_id['idA'] && eq(m.PS_by_id['idA'].objects, ['A']);
  var p3ok = m.PS_by_id['idC'] && eq(m.PS_by_id['idC'].objects, ['C']);
  var p2ok = m.PS_by_id['idB'] && eq(m.PS_by_id['idB'], { objects: [] });
  var p4ok = m.PS_by_id['idD'] && eq(m.PS_by_id['idD'], { objects: [] });
  var p5ok = m.PS_by_id['idE'] && eq(m.PS_by_id['idE'], { objects: [] });

  // projectToGlobals also emits all 5 pages
  var out = m.projectToGlobals();
  var projCount = out.pageCount === 5;
  var projIds   = eq(out.pageIdentities, ['idA', 'idB', 'idC', 'idD', 'idE']);
  var projSparse = out.PS[1] && eq(out.PS[1].objects, ['A']) &&
                   out.PS[3] && eq(out.PS[3].objects, ['C']) &&
                   out.PS[2] && eq(out.PS[2], { objects: [] }) &&
                   out.PS[4] && eq(out.PS[4], { objects: [] }) &&
                   out.PS[5] && eq(out.PS[5], { objects: [] });

  check('E19', 'edge',
    'sparse PS (pageCount=5 but PS has only keys 1,3): all 5 ids exist, missing pages normalised to {objects:[]}',
    allExist && p1ok && p3ok && p2ok && p4ok && p5ok && projCount && projIds && projSparse);
})();

// E20: excluded dict round-trips through reorder — same pages (by identity) are
//      marked excluded at their NEW display numbers in projectToGlobals().
(function () {
  resetIds();
  var g = {
    pageCount: 5,
    pageIdentities: ['idA', 'idB', 'idC', 'idD', 'idE'],
    PS: {
      1: { objects: ['A'] }, 2: { objects: ['B'] }, 3: { objects: ['C'] },
      4: { objects: ['D'] }, 5: { objects: ['E'] },
    },
    pageTags:      {},
    pageFloorKind: {},
    pageFloorNum:  {},
    pageNames:     {},
    pageRot:       {},
    excluded:      { 2: true, 4: true },   // B and D are excluded
  };

  var m = new PageModel();
  m.seedFromGlobals(g);
  var ID = { A:'idA', B:'idB', C:'idC', D:'idD', E:'idE' };

  // Before reorder: B at n=2 and D at n=4 are excluded
  var before = m.projectToGlobals();
  var beforeOk = before.excluded[2] === true && before.excluded[4] === true &&
                 !before.excluded[1] && !before.excluded[3] && !before.excluded[5];

  // Reorder: move E (index 4) to front → E,A,B,C,D
  m.reorder(4, 0);
  // Now: E(n=1), A(n=2), B(n=3), C(n=4), D(n=5)
  // B is still excluded → must appear at n=3
  // D is still excluded → must appear at n=5

  var after = m.projectToGlobals();

  var bNewNum = m.numOf(ID.B);  // should be 3
  var dNewNum = m.numOf(ID.D);  // should be 5

  var afterOk = bNewNum === 3 && dNewNum === 5 &&
                after.excluded[3] === true &&   // B at its new position
                after.excluded[5] === true &&   // D at its new position
                !after.excluded[1] && !after.excluded[2] && !after.excluded[4];

  // No spurious excluded entries
  var noOrphans = Object.keys(after.excluded).length === 2;

  check('E20', 'edge',
    'excluded round-trips through reorder: same identities (B,D) remain excluded at their new display numbers (3,5)',
    beforeOk && afterOk && noOrphans);
})();

// ============================================================
// REPORT
// ============================================================
var pass = results.filter(function (r) { return r.pass; }).length;
var total = results.length;

console.log('\n=== page-manager production module eval (E1–E20) ===');
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
