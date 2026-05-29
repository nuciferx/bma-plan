/*
 * page-model.js — SPIKE (lite-invent: GoodNotes/ABBYY-style page management)
 * Approach D (optimistic client, stable page-ID, deferred server sync).
 *
 * PURE DATA MODEL ONLY — no DOM, no server, no PDF render. Runs in node AND
 * browser. Proves the page-identity accessor layer that lets reorder / delete /
 * duplicate happen WITHOUT corrupting number-keyed per-page measurement data.
 *
 * This is a SPIKE in lite/sandbox/ — it does NOT touch lite/ui-lite.html,
 * lite/server_lite.py, measure-engine.js, RS, pdfToC/cToPdf, or the live
 * .bmaplan path. The save/load here mimics lite's ADDITIVE .bmaplan rules.
 *
 * Core idea: every page gets a stable id. The UI/order is an ordered array of
 * ids (pageOrder). All per-page state is keyed by id (PS_by_id / tag_by_id /
 * rot_by_id / excl_by_id), NOT by page number. Page NUMBER = index in
 * pageOrder + 1, derived on read. Reorder/delete/duplicate mutate pageOrder +
 * the id-keyed dicts; numbers re-derive automatically → zero renumber bugs.
 *
 * Server sync is deferred: mutations are journalled in `pending` and only
 * flushed (→ /apply-page-mutations) at save/export. undo() = snapshot restore.
 */
(function (root) {
  'use strict';

  // Deterministic id generator (a counter, not crypto.randomUUID) so that
  // save→reload round-trips are byte-stable and the eval can deep-equal them.
  var _idc = 0;
  function newId() { return 'pg' + (_idc++); }

  function deepCopy(o) { return o == null ? o : JSON.parse(JSON.stringify(o)); }
  function deepEq(a, b) { return JSON.stringify(a) === JSON.stringify(b); }

  function PageModel() {
    this.pageOrder = [];   // [id, id, ...]  display order; number = index+1
    this.PS_by_id  = {};   // id -> { objects:[...] }   (measurement store)
    this.tag_by_id = {};   // id -> tag string
    this.rot_by_id = {};   // id -> rotation deg
    this.excl_by_id= {};   // id -> bool (soft exclude)
    this.originNum = {};   // id -> page number in the CURRENT server PDF (null = client-new, not yet on server)
    this.pending   = [];   // mutation journal (flushed to server at save)
    this.undoStack = [];   // snapshots for Ctrl+Z
    this.curPage   = 1;    // active display number
  }

  /* ---- accessors: number <-> id (the heart of the approach) ---- */
  PageModel.prototype.idAt   = function (n) { return this.pageOrder[n - 1]; };
  PageModel.prototype.numOf  = function (id) { return this.pageOrder.indexOf(id) + 1; };
  PageModel.prototype.count  = function () { return this.pageOrder.length; };
  // legacy-style number-keyed reads, routed through id (drop-in for PS[n] etc.)
  PageModel.prototype.PSn    = function (n) { return this.PS_by_id[this.idAt(n)]; };
  PageModel.prototype.tagN   = function (n) { return this.tag_by_id[this.idAt(n)]; };
  PageModel.prototype.rotN   = function (n) { return this.rot_by_id[this.idAt(n)]; };
  PageModel.prototype.exclN  = function (n) { return this.excl_by_id[this.idAt(n)]; };

  /* ---- undo plumbing ---- */
  PageModel.prototype._snap = function () {
    this.undoStack.push(deepCopy({
      pageOrder: this.pageOrder, PS_by_id: this.PS_by_id, tag_by_id: this.tag_by_id,
      rot_by_id: this.rot_by_id, excl_by_id: this.excl_by_id, originNum: this.originNum,
      pending: this.pending, curPage: this.curPage,
    }));
  };
  PageModel.prototype.undo = function () {
    if (!this.undoStack.length) return false;
    var s = this.undoStack.pop();
    this.pageOrder = s.pageOrder; this.PS_by_id = s.PS_by_id; this.tag_by_id = s.tag_by_id;
    this.rot_by_id = s.rot_by_id; this.excl_by_id = s.excl_by_id; this.originNum = s.originNum;
    this.pending = s.pending; this.curPage = s.curPage;
    return true;
  };

  /* ---- mutations (instant, client-authoritative; server synced on flush) ---- */

  // reorder: move page at display index `from` (0-based) to index `to` (0-based)
  PageModel.prototype.reorder = function (from, to) {
    this._snap();
    var id = this.pageOrder.splice(from, 1)[0];
    this.pageOrder.splice(to, 0, id);
    this.pending.push({ type: 'reorder', order: this.pageOrder.slice() });
  };

  // delete: remove page at display index `at` (0-based), PERMANENT (at flush)
  PageModel.prototype.del = function (at) {
    this._snap();
    var id = this.pageOrder.splice(at, 1)[0];
    delete this.PS_by_id[id]; delete this.tag_by_id[id];
    delete this.rot_by_id[id]; delete this.excl_by_id[id];
    this.pending.push({ type: 'delete', id: id, origin: this.originNum[id] });
    delete this.originNum[id];
    if (this.curPage > this.count()) this.curPage = Math.max(1, this.count());
  };

  // duplicate: copy page at display index `at`, insert independent copy after it
  PageModel.prototype.duplicate = function (at) {
    this._snap();
    var src = this.pageOrder[at];
    var nid = newId();
    this.pageOrder.splice(at + 1, 0, nid);
    this.PS_by_id[nid]   = deepCopy(this.PS_by_id[src]);   // independent copy (E3)
    this.tag_by_id[nid]  = this.tag_by_id[src];
    this.rot_by_id[nid]  = this.rot_by_id[src];
    this.excl_by_id[nid] = this.excl_by_id[src];
    this.originNum[nid]  = null;                            // new page, not on server yet
    this.pending.push({ type: 'duplicate', srcId: src, newId: nid });
  };

  /* ---- server flush: build the renumber-map the server would return ----
   * Replays the journal against the initial server page numbers [1..N] and
   * returns { renumberMap: {oldNum -> newNum}, order: [...] }. In production
   * this is what POST /apply-page-mutations returns; here we simulate it so the
   * eval can cross-check it against the live pageOrder (E6). The cross-check is
   * the real integrity test: if any mutation updated pageOrder but not the
   * journal (or vice-versa), the two derivations diverge.
   */
  PageModel.prototype.simulateFlush = function (initialCount) {
    // tokens: original pages = their number; duplicates = {dup:newId}
    var arr = [];
    for (var i = 1; i <= initialCount; i++) arr.push({ orig: i, id: '__orig' + i });
    // We need the journal to reference ids; map original ids deterministically.
    // The model assigns ids at load; we reconstruct by replaying using id refs.
    // For the spike the journal carries ids directly, so replay on id-token array:
    var tokens = this._initialIds.map(function (id, idx) { return { id: id, orig: idx + 1 }; });
    this.pending.forEach(function (m) {
      if (m.type === 'reorder') {
        tokens = m.order.map(function (id) {
          for (var k = 0; k < tokens.length; k++) if (tokens[k].id === id) return tokens[k];
          return { id: id, orig: null }; // a duplicate created earlier
        });
      } else if (m.type === 'delete') {
        tokens = tokens.filter(function (t) { return t.id !== m.id; });
      } else if (m.type === 'duplicate') {
        var pos = -1;
        for (var k = 0; k < tokens.length; k++) if (tokens[k].id === m.srcId) { pos = k; break; }
        tokens.splice(pos + 1, 0, { id: m.newId, orig: null });
      }
    });
    var renumberMap = {};
    tokens.forEach(function (t, i) { if (t.orig != null) renumberMap[t.orig] = i + 1; });
    return { renumberMap: renumberMap, order: tokens.map(function (t) { return t.id; }) };
  };

  /* ---- .bmaplan save/load (ADDITIVE: adds pageIdentities; pageStore stays
   *      number-keyed by DISPLAY index so proto/legacy can still read it) ---- */
  PageModel.prototype.save = function () {
    var doc = { version: 1, app: 'bma-plan-lite',
      pageIdentities: this.pageOrder.slice(),   // NEW additive field (ordered ids)
      pageStore: {}, pageTags: {}, pageRot: {}, excluded: {} };
    var self = this;
    this.pageOrder.forEach(function (id, i) {
      var n = String(i + 1);
      doc.pageStore[n] = deepCopy(self.PS_by_id[id]);
      if (self.tag_by_id[id] != null)  doc.pageTags[n] = self.tag_by_id[id];
      if (self.rot_by_id[id] != null)  doc.pageRot[n]  = self.rot_by_id[id];
      if (self.excl_by_id[id])         doc.excluded[n] = true;
    });
    return doc;
  };

  PageModel.prototype.load = function (doc) {
    this.pageOrder = []; this.PS_by_id = {}; this.tag_by_id = {};
    this.rot_by_id = {}; this.excl_by_id = {}; this.originNum = {};
    this.pending = []; this.undoStack = []; this.curPage = 1;
    var nums = Object.keys(doc.pageStore).map(Number).sort(function (a, b) { return a - b; });
    var hasIds = Array.isArray(doc.pageIdentities) && doc.pageIdentities.length === nums.length;
    var self = this;
    nums.forEach(function (n, i) {
      var id = hasIds ? doc.pageIdentities[i] : newId();  // legacy: mint fresh ids (E5 migrate)
      var key = String(n);
      self.pageOrder.push(id);
      self.PS_by_id[id]   = deepCopy(doc.pageStore[key]);
      self.tag_by_id[id]  = (doc.pageTags  || {})[key];
      self.rot_by_id[id]  = (doc.pageRot   || {})[key];
      self.excl_by_id[id] = !!(doc.excluded || {})[key];
      self.originNum[id]  = i + 1;
    });
    this._initialIds = this.pageOrder.slice();  // baseline for server-flush replay
    this._migratedFromLegacy = !hasIds;
    return this;
  };

  /* full ordered snapshot of per-page data (for deep-equal round-trip checks) */
  PageModel.prototype.snapshotByOrder = function () {
    var self = this;
    return this.pageOrder.map(function (id) {
      return { ps: self.PS_by_id[id], tag: self.tag_by_id[id],
               rot: self.rot_by_id[id], excl: !!self.excl_by_id[id] };
    });
  };

  PageModel.deepEq = deepEq;
  PageModel.newId = newId;
  root.PageModel = PageModel;
  if (typeof module !== 'undefined' && module.exports) module.exports = PageModel;
})(typeof window !== 'undefined' ? window : globalThis);
