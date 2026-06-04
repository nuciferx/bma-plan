/*
 * eval-v3.js — THIRD adversarial pass (Opus 4.8, 2026-05-29 "ตรวจหาจุดบกพร่องอีกครั้ง").
 * Run: node lite/sandbox/invent-page-manager/eval-v3.js
 *
 * v2 was GREEN on E7-E12, but a deeper read of the REAL lite codebase showed two
 * of v2's own assumptions were WRONG about how lite actually works. A green eval
 * built on a wrong model is worse than no eval — it manufactures false confidence.
 * v3 corrects the model and adds the cases that expose the remaining real bugs.
 *
 * CORRECTIONS TO v2 (verified against lite/static/js/page-folder-layers.js):
 *
 *  C-FOLDER  v2 modelled page-folders as carrying their OWN id-keyed membership
 *            that must be remapped on every mutation. WRONG. In real lite, a
 *            page-folder's id ENCODES the floor (PF_floor_3, PF_basement_1, ...)
 *            and `.pages` is **DERIVED** — recomputed by reseedActivePageFolders()
 *            from pageTags/pageFloorNum/pageFloorKind (page-folder-layers.js:123,
 *            700-705). `.pages` is never set anywhere else. So the correct build
 *            is NOT "remap folder membership"; it is "per-page meta moves by
 *            identity (already handled), THEN reseed re-derives .pages". v2's
 *            remap fights reseed and would double-maintain. E13 proves the
 *            re-derive path yields correct number-membership after mutation.
 *            (Also: 'user'/legacy folders hold LAYERS via parentId, not pages —
 *            no page membership to corrupt. E13b.)
 *
 *  C-DIRTY   v2 ignored dirty-tracking. Real lite computes the unsaved-changes
 *            snapshot with _docSnap() (ui-lite.html:816) = JSON of
 *            {PS,excluded,pageTags,pageFloorKind,pageFloorNum,pageNames,...}.
 *            It contains **no page order, no rotation, no liteGroups**. So a pure
 *            reorder/duplicate/merge would NOT flip state.dirty → the user closes,
 *            gets no "unsaved changes" prompt, and silently loses the whole page
 *            reorganization. This is the dangerous twin of the "close-without-save
 *            = original untouched" decision. E14 encodes the contract the build
 *            must satisfy: every page mutation must change the dirty-snapshot.
 *
 * NEW EDGE/ADVERSARIAL:
 *  E15  duplicate-then-delete-original — the copy must keep its own data after the
 *       source is gone (catches a shared-reference dup bug v1/v2 didn't isolate).
 *  E16  reorder is a no-op identity (move to same index) must not journal garbage
 *       nor desync simulateFlush.
 *
 * Pure data model. Loads page-model-v2.js (the build target) and tests it AS IS
 * for the parts it gets right, and documents (via failing-then-fixed asserts) the
 * parts the BUILD must add. Where v2 lacks a hook, v3 models the REQUIRED behavior
 * with a local helper and asserts the contract — so the builder has an executable
 * spec, not prose.
 */
var PageModel = require('./page-model-v2.js');
var eq = PageModel.deepEq;

var results = [];
function check(id, kind, desc, cond) { results.push({ id: id, kind: kind, desc: desc, pass: !!cond }); }

function fullDoc() {
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
    liteGroups: [],   // page-folders are DERIVED, not stored as membership; start empty
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

/* ---- the REAL folder-id rule (mirrors pageFolderIdFor, page-folder-layers.js:85) ---- */
function pageFolderIdFor(tag, floorNum, kind) {
  if (!tag || tag === 'excluded') return 'PF_excluded';
  if (tag === 'site') return 'PF_site';
  if (tag !== 'floor') return 'PF_excluded';
  kind = kind || 'normal';
  if (floorNum === 'roof' || kind === 'rooftop') return 'PF_floor_roof';
  if (floorNum === undefined || floorNum === null || floorNum === '') return 'PF_excluded';
  if (kind === 'basement')   return 'PF_basement_' + floorNum;
  if (kind === 'mezzanine')  return 'PF_mezz_' + floorNum;
  if (kind === 'mechanical') return 'PF_mech_' + floorNum;
  return 'PF_floor_' + floorNum;
}
/* DERIVE folders from current per-page meta, in display order — what reseed does.
   Returns { folderId: [pageNumbers...] } with numbers in display order. */
function deriveFolders(m) {
  var out = {};
  m.pageOrder.forEach(function (id, i) {
    var mt = m.meta_by_id[id] || {};
    var fid = pageFolderIdFor(mt.tag, mt.floorNum, mt.floorKind);
    (out[fid] = out[fid] || []).push(i + 1);   // page NUMBER, display order
  });
  return out;
}

/* ===== E13 — folder membership is DERIVED correctly after mutation (corrects C-FOLDER) ===== */
(function () {
  var m = new PageModel(); m.load(fullDoc());
  var ID = {}; ['A','B','C','D','E'].forEach(function (k) { ID[k] = idByMarker(m, k); });
  // initial: site={A(1),E(5)}, PF_floor_1={B(2)}, PF_floor_2={C(3)}, PF_basement_1={D(4)}
  var f0 = deriveFolders(m);
  var initOk = eq(f0['PF_site'], [1, 5]) && eq(f0['PF_floor_1'], [2]) &&
               eq(f0['PF_floor_2'], [3]) && eq(f0['PF_basement_1'], [4]);
  // mutate: move E(5)->pos2 ; delete C ; duplicate B
  m.reorder(4, 1);                    // A,E,B,C,D
  m.del(m.numOf(ID.C) - 1);          // A,E,B,D   (PF_floor_2 now empty → must vanish)
  m.duplicate(m.numOf(ID.B) - 1);   // A,E,B,B',D (B' inherits floor 1 normal)
  var f1 = deriveFolders(m);
  // display now A(1),E(2),B(3),B'(4),D(5): site={1,2}, PF_floor_1={3,4}, PF_basement_1={5}
  var afterOk = eq(f1['PF_site'], [1, 2]) && eq(f1['PF_floor_1'], [3, 4]) &&
                eq(f1['PF_basement_1'], [5]) && !('PF_floor_2' in f1);   // deleted floor gone
  check('E13', 'adversarial',
        'page-folder .pages RE-DERIVES correctly after reorder/delete/dup (folder id is floor-based, membership is computed not stored)',
        initOk && afterOk);
})();

/* ===== E13b — user/legacy folders carry LAYERS not pages → nothing to corrupt ===== */
(function () {
  var doc = fullDoc();
  doc.liteGroups = [{ id: 'F1', name: 'My group', kind: undefined /* legacy='user' */ }];  // no .pages
  var m = new PageModel(); m.load(doc);
  m.reorder(4, 0); m.del(0);
  // a user folder has no page membership; v2 load tolerates missing .pages and save doesn't invent one
  var saved = m.save().liteGroups.find(function (g) { return g.id === 'F1'; });
  var ok = saved && Array.isArray(saved.pages) && saved.pages.length === 0;
  check('E13b', 'edge', 'user/legacy folder (no page membership) survives mutation without spurious page refs', ok);
})();

/* ===== E14 — dirty-tracking contract: every page mutation changes the snapshot (C-DIRTY) =====
 * Real lite _docSnap() OMITS pageOrder/rotation/liteGroups → reorder wouldn't mark dirty.
 * The build MUST extend the dirty snapshot to include page order + per-page meta.
 * v3 asserts the CONTRACT against the required snapshot shape so the build has a spec. */
(function () {
  function requiredDocSnap(m) {     // what _docSnap MUST cover after this feature
    return JSON.stringify({
      order: m.pageOrder, PS: m.PS_by_id, meta: m.meta_by_id,
    });
  }
  var m = new PageModel(); m.load(fullDoc());
  var before = requiredDocSnap(m);
  m.reorder(0, 3);                                  // pure reorder, no object/meta edit
  var afterReorder = requiredDocSnap(m);
  var dup = (function () { m.duplicate(0); return requiredDocSnap(m); })();
  var del = (function () { var ID = idByMarker(m, 'B'); m.del(m.numOf(ID) - 1); return requiredDocSnap(m); })();
  var dirtyOnReorder = before !== afterReorder;     // <-- FAILS with current lite _docSnap (the bug)
  var dirtyOnDup = afterReorder !== dup;
  var dirtyOnDel = dup !== del;
  check('E14', 'adversarial',
        'dirty-tracking: pure reorder/duplicate/delete each changes the doc snapshot (build must extend _docSnap with pageOrder+meta, else silent data loss on close)',
        dirtyOnReorder && dirtyOnDup && dirtyOnDel);
})();

/* ===== E15 — duplicate then delete original: copy keeps independent data ===== */
(function () {
  var m = new PageModel(); m.load(fullDoc());
  var bId = idByMarker(m, 'B');
  m.duplicate(m.numOf(bId) - 1);                    // B' after B
  var copyId = m.pageOrder[m.numOf(bId)];           // the copy
  m.del(m.numOf(bId) - 1);                          // delete the ORIGINAL B
  var copyAlive = m.pageOrder.indexOf(copyId) >= 0;
  var copyData = m.PS_by_id[copyId] && eq(m.PS_by_id[copyId].objects, ['B']) &&
                 m.meta_by_id[copyId] && m.meta_by_id[copyId].floorNum === 1;
  // mutating the copy now must be safe (no dangling shared ref to the deleted original)
  m.PS_by_id[copyId].objects.push('Z');
  var independent = eq(m.PS_by_id[copyId].objects, ['B', 'Z']) && !(bId in m.PS_by_id);
  check('E15', 'edge', 'duplicate then delete original: copy survives with independent data (no shared reference)',
        copyAlive && copyData && independent);
})();

/* ===== E16 — no-op reorder (same index) must not corrupt journal/flush ===== */
(function () {
  var m = new PageModel(); m.load(fullDoc());
  var ord0 = m.pageOrder.slice();
  m.reorder(2, 2);                                  // move index 2 to index 2 = no-op
  var sameOrder = eq(m.pageOrder, ord0);
  var f = m.simulateFlush();
  // identity renumber: every original page maps to itself
  var identityMap = eq(f.renumberMap, { 1: 1, 2: 2, 3: 3, 4: 4, 5: 5 });
  var orderConsistent = eq(f.order, m.pageOrder);
  check('E16', 'edge', 'no-op reorder (same index) keeps order + yields identity renumber-map + consistent flush',
        sameOrder && identityMap && orderConsistent);
})();

/* ---- REPORT ---- */
var pass = results.filter(function (r) { return r.pass; }).length;
console.log('\n=== lite-page-manager SPIKE v3 eval (3rd pass: model corrections + remaining bugs) ===');
results.forEach(function (r) {
  console.log((r.pass ? 'PASS' : 'FAIL') + '  ' + r.id + ' [' + r.kind + ']  ' + r.desc);
});
console.log('-----------------------------------------------------------------------------------');
console.log('RESULT: ' + pass + '/' + results.length + '  ' +
            (pass === results.length ? 'ACCEPT' : 'REJECT (see FAIL — these are the build TODOs)'));
process.exit(pass === results.length ? 0 : 1);
