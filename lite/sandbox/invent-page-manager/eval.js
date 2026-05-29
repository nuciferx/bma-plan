/*
 * eval.js — RUNNABLE EVAL for the lite-page-manager spike.
 * Run: node lite/sandbox/invent-page-manager/eval.js
 * PASS = 6/6 hard asserts (E1..E6), tolerance 0 (data integrity = no partial).
 *
 * Tests the page-identity data model ONLY (no PDF render, no server). This IS
 * the phase-6 acceptance gate for the invention pass.
 */
var PageModel = require('./page-model.js');
var eq = PageModel.deepEq;

var results = [];
function check(id, desc, cond) {
  results.push({ id: id, desc: desc, pass: !!cond });
}

/* ---- SETUP: synthetic 5-page state, distinct data per page ---- */
function makeInitialDoc() {
  // markers A..E on pages 1..5; tag/rot/excl all distinct so any shift shows up
  return {
    version: 1,
    pageStore: {
      '1': { objects: ['A'] }, '2': { objects: ['B'] }, '3': { objects: ['C'] },
      '4': { objects: ['D'] }, '5': { objects: ['E'] },
    },
    pageTags: { '1': 'tA', '2': 'tB', '3': 'tC', '4': 'tD', '5': 'tE' },
    pageRot:  { '1': 0, '2': 90, '3': 180, '4': 270, '5': 0 },
    excluded: { '2': true, '4': true },   // B and D excluded
    pageIdentities: ['idA', 'idB', 'idC', 'idD', 'idE'],
  };
}

var m = new PageModel();
m.load(makeInitialDoc());

// capture id per marker for identity assertions
function idByMarker(model, mk) {
  for (var i = 0; i < model.pageOrder.length; i++) {
    var id = model.pageOrder[i];
    if (model.PS_by_id[id] && model.PS_by_id[id].objects.indexOf(mk) >= 0) return id;
  }
  return null;
}
var ID = { A: idByMarker(m, 'A'), B: idByMarker(m, 'B'), C: idByMarker(m, 'C'),
           D: idByMarker(m, 'D'), E: idByMarker(m, 'E') };

// snapshot original per-marker data (by identity) for E1
function dataOf(model, id) {
  return { ps: model.PS_by_id[id], tag: model.tag_by_id[id],
           rot: model.rot_by_id[id], excl: !!model.excl_by_id[id] };
}
var ORIG = {}; ['A','B','C','D','E'].forEach(function (k) { ORIG[k] = dataOf(m, ID[k]); });

/* ---- SEQUENCE (deterministic) ---- */
// 1. reorder: move page5 (E, index 4) -> position 2 (index 1)  => A,E,B,C,D
m.reorder(4, 1);
// 2. delete marker "C" permanently  (C now at display index 3)  => A,E,B,D
m.del(m.numOf(ID.C) - 1);
// 3. duplicate marker "B" (B at display index 2)  => A,E,B,B',D
m.duplicate(m.numOf(ID.B) - 1);

/* ---- ASSERTS ---- */

// E1: every surviving marker keeps correct object/tag/rot/excl BY IDENTITY
var e1 = ['A', 'B', 'D', 'E'].every(function (k) { return eq(dataOf(m, ID[k]), ORIG[k]); });
// and display order is exactly A,E,B,B',D
var orderMarkers = m.pageOrder.map(function (id) { return m.PS_by_id[id].objects[0]; });
e1 = e1 && eq(orderMarkers, ['A', 'E', 'B', 'B', 'D']);  // B' also has objects ['B'] until edited
check('E1', 'survivors keep correct object/tag/rot/excluded by identity (no shift)', e1);

// E2: marker "C" fully gone — no id, no orphan in any dict
var cId = ID.C;
var e2 = m.pageOrder.indexOf(cId) < 0 && !(cId in m.PS_by_id) && !(cId in m.tag_by_id) &&
         !(cId in m.rot_by_id) && !(cId in m.excl_by_id) && !(cId in m.originNum) &&
         idByMarker(m, 'C') === null;
check('E2', '"C" and all its data fully removed, zero orphans', e2);

// E3: duplicate "B'" is an INDEPENDENT copy (editing B' does not touch B)
var bpIdx = m.numOf(ID.B);            // B' sits right after B
var bpId  = m.pageOrder[bpIdx];       // index = display num of B (0-based after) => the copy
var e3a = bpId !== ID.B && eq(m.PS_by_id[bpId].objects, ['B']);
m.PS_by_id[bpId].objects.push('EDIT');               // mutate the copy
var e3 = e3a && eq(m.PS_by_id[bpId].objects, ['B', 'EDIT']) &&
         eq(m.PS_by_id[ID.B].objects, ['B']);          // original untouched
check('E3', 'duplicate is an independent deep copy (edit copy ≠ edit original)', e3);

// E4: save -> reload deep-equal (full per-page data in display order)
var before = m.snapshotByOrder();
var doc = m.save();
var m2 = new PageModel(); m2.load(doc);
var e4 = eq(before, m2.snapshotByOrder()) && eq(m.pageOrder, m2.pageOrder);
check('E4', 'save→.bmaplan→reload round-trips deep-equal', e4);

// E5: legacy save (number-keyed, NO pageIdentities) loads + auto-migrates to id-keyed
var legacy = makeInitialDoc();
delete legacy.pageIdentities;                          // legacy file
var m3 = new PageModel(); m3.load(legacy);
var e5 = m3._migratedFromLegacy === true && m3.count() === 5 &&
         eq(m3.pageOrder.map(function (id) { return m3.PS_by_id[id].objects[0]; }),
            ['A', 'B', 'C', 'D', 'E']) &&
         m3.pageOrder.every(function (id) { return typeof id === 'string'; }) &&
         // ids are freshly minted (not the literal 'idA'..), proving migration
         m3.pageOrder.indexOf('idA') < 0;
check('E5', 'legacy number-keyed save loads + auto-migrates to id-keyed', e5);

// E6: the renumber-map the server would return matches the live UI index 1:1
var flush = m.simulateFlush(5);
var liveMap = {};
m.pageOrder.forEach(function (id, i) {
  if (m.originNum[id] != null) liveMap[m.originNum[id]] = i + 1;
});
var e6 = eq(flush.renumberMap, liveMap) &&
         // and the journal-replayed order equals the live order
         eq(flush.order, m.pageOrder);
check('E6', 'server renumber-map (journal replay) == live UI index 1:1', e6);

/* ---- REPORT ---- */
var pass = results.filter(function (r) { return r.pass; }).length;
console.log('\n=== lite-page-manager SPIKE eval ===');
results.forEach(function (r) {
  console.log((r.pass ? 'PASS' : 'FAIL') + '  ' + r.id + '  ' + r.desc);
});
console.log('-----------------------------------');
console.log('RESULT: ' + pass + '/6  ' + (pass === 6 ? 'ACCEPT (spike meets eval)' : 'REJECT'));
console.log('extra: live order after sequence =', m.pageOrder.map(function (id) {
  return m.PS_by_id[id].objects[0] + (m.originNum[id] == null ? "'" : '');
}).join(','));
console.log('extra: renumberMap (origNum→newNum) =', JSON.stringify(flush.renumberMap));
process.exit(pass === 6 ? 0 : 1);
