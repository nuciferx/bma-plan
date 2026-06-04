/*
 * page-model-v2.js — SPIKE v2 (lite-invent: GoodNotes/ABBYY page management)
 * Approach D (optimistic client, stable page-ID, deferred server sync).
 *
 * Re-pass 2026-05-29 ("ต้องเพิ่มไรอีกไหม"). v1 (page-model.js) proved the core
 * identity idea on 4 per-page dicts + one happy 5-page scenario (E1..E6, all
 * happy-path). The re-pass recon of the REAL lite codebase found v1 was missing
 * the things most likely to corrupt a real save. v2 closes them and the eval
 * taxonomy (eval-v2.js) adds the edge + adversarial cases the skill mandates.
 *
 * WHAT THE RECON CHANGED vs v1 (all verified against lite/ on 2026-05-29):
 *  G-STATE  lite has 7 number-keyed per-page containers, not 4. v1 modelled
 *           pageStore/tag/rot/excl only. MISSING: pageFloorKind, pageFloorNum,
 *           pageNames. v2 folds every scalar into ONE id-keyed record so "we
 *           forgot a dict" becomes structurally impossible. (lite save schema:
 *           ui-lite.html L1100-1110)
 *  G-FOLDER liteGroups (page folders) store membership as ARRAYS OF PAGE NUMBERS
 *           (page-folder-layers.js:6 "groups several PDF pages (by number)",
 *           e.g. pages [3,4,5,6]; g.pages). Reorder/delete/duplicate silently
 *           corrupt these. v1 never modelled groups at all. v2 stores membership
 *           by id internally; numbers are derived on save.
 *  G-RENDER approach D shows the new order INSTANTLY but the page IMAGE still
 *           comes from the server, whose PDF is unchanged until flush. So a
 *           render/thumb request for display-page n must hit the page's ORIGINAL
 *           server number, not n. v1 had originNum but never used it for render.
 *           v2 adds serverNum(n) + srcServer for dup/merge pages.
 *  G-REFLUSH users save many times per session. After a flush the server PDF IS
 *           the new order, so the NEXT journal must replay from the post-flush
 *           baseline, not the original. v1 set _initialIds once and never reset.
 *           v2 has applyFlush() that re-baselines (originNum := new index,
 *           pending := [], _initialIds := current order).
 *  G-GUARD  v1 let you delete down to zero pages. v2 refuses to delete the last
 *           page (a doc must have ≥1 page).
 *
 * Still a SPIKE in lite/sandbox/ — pure data model, no DOM/server/PDF. Does NOT
 * touch lite/ui-lite.html, server_lite.py, measure-engine.js, RS, pdfToC/cToPdf,
 * or the live .bmaplan path. save/load mimics lite's ADDITIVE .bmaplan rules.
 */
(function (root) {
  'use strict';

  var _idc = 0;
  function newId() { return 'pg' + (_idc++); }          // deterministic for byte-stable round-trips
  function deepCopy(o) { return o == null ? o : JSON.parse(JSON.stringify(o)); }
  function deepEq(a, b) { return JSON.stringify(a) === JSON.stringify(b); }

  // the per-page scalar record. ONE place — adding a new per-page field later
  // means adding it here + in save()/load() fan-out, never a new parallel dict.
  function blankMeta() {
    return { tag: '', rot: 0, excl: false, floorKind: '', floorNum: null, name: '' };
  }

  function PageModel() {
    this.pageOrder  = [];   // [id,...] display order; number = index+1
    this.PS_by_id   = {};   // id -> { objects:[...] }  (measurement store; kept separate, it's the big one)
    this.meta_by_id = {};   // id -> { tag, rot, excl, floorKind, floorNum, name }  (the other 6 scalars)
    this.groups     = [];   // [{ id, name, kind, pages:[id,...] }]  liteGroups; membership BY ID internally
    this.originNum  = {};   // id -> page number in the CURRENT server PDF (null = client-new, not on server yet)
    this.srcServer  = {};   // id -> server page to RENDER FROM until flush (for dup; null=merge placeholder)
    this.pending    = [];   // mutation journal, flushed at save/export
    this.undoStack  = [];   // Ctrl+Z snapshots
    this.undoCap    = 30;   // G: bound undo memory (v1 was unbounded; 45-page docs blow up)
    this.curPage    = 1;
    this._initialIds = [];  // baseline order for the CURRENT server PDF (reset by applyFlush)
    this._migratedFromLegacy = false;
  }

  /* ---- accessors ---- */
  PageModel.prototype.idAt  = function (n)  { return this.pageOrder[n - 1]; };
  PageModel.prototype.numOf = function (id) { return this.pageOrder.indexOf(id) + 1; };
  PageModel.prototype.count = function ()   { return this.pageOrder.length; };
  PageModel.prototype.PSn   = function (n)  { return this.PS_by_id[this.idAt(n)]; };
  PageModel.prototype.metaN = function (n)  { return this.meta_by_id[this.idAt(n)]; };
  // G-RENDER: which SERVER page number to render/thumb for display page n, pre-flush.
  // original page -> its server number; duplicate -> its source's server number;
  // merged page (no source in current PDF) -> null (caller shows a "pending merge" placeholder).
  PageModel.prototype.serverNum = function (n) {
    var id = this.idAt(n);
    if (this.originNum[id] != null) return this.originNum[id];
    return (id in this.srcServer) ? this.srcServer[id] : null;
  };
  // groups a page belongs to (by id), in declared order — for the folder UI
  PageModel.prototype.groupsOf = function (id) {
    return this.groups.filter(function (g) { return g.pages.indexOf(id) >= 0; });
  };

  /* ---- undo ---- */
  PageModel.prototype._snap = function () {
    this.undoStack.push(deepCopy({
      pageOrder: this.pageOrder, PS_by_id: this.PS_by_id, meta_by_id: this.meta_by_id,
      groups: this.groups, originNum: this.originNum, srcServer: this.srcServer,
      pending: this.pending, curPage: this.curPage,
    }));
    if (this.undoStack.length > this.undoCap) this.undoStack.shift();   // bound memory
  };
  PageModel.prototype.undo = function () {
    if (!this.undoStack.length) return false;
    var s = this.undoStack.pop();
    this.pageOrder = s.pageOrder; this.PS_by_id = s.PS_by_id; this.meta_by_id = s.meta_by_id;
    this.groups = s.groups; this.originNum = s.originNum; this.srcServer = s.srcServer;
    this.pending = s.pending; this.curPage = s.curPage;
    return true;
  };

  /* ---- mutations (instant; server synced on flush) ---- */

  PageModel.prototype.reorder = function (from, to) {
    this._snap();
    var id = this.pageOrder.splice(from, 1)[0];
    this.pageOrder.splice(to, 0, id);
    this.pending.push({ type: 'reorder', order: this.pageOrder.slice() });
    // groups: membership is by id → follows automatically. nothing to do.
  };

  PageModel.prototype.del = function (at) {
    if (this.count() <= 1) return false;                 // G-GUARD: never delete the last page
    this._snap();
    var id = this.pageOrder.splice(at, 1)[0];
    delete this.PS_by_id[id]; delete this.meta_by_id[id];
    delete this.srcServer[id];
    var origin = this.originNum[id]; delete this.originNum[id];
    // G-FOLDER: drop the id from every folder so no folder points at a dead page
    this.groups.forEach(function (g) {
      var i = g.pages.indexOf(id); if (i >= 0) g.pages.splice(i, 1);
    });
    this.pending.push({ type: 'delete', id: id, origin: origin });
    if (this.curPage > this.count()) this.curPage = Math.max(1, this.count());
    return true;
  };

  PageModel.prototype.duplicate = function (at) {
    this._snap();
    var src = this.pageOrder[at];
    var nid = newId();
    this.pageOrder.splice(at + 1, 0, nid);
    this.PS_by_id[nid]   = deepCopy(this.PS_by_id[src]);     // independent deep copy
    this.meta_by_id[nid] = deepCopy(this.meta_by_id[src]);
    this.originNum[nid]  = null;                              // not on server yet
    // G-RENDER: until flush, the copy renders from the SAME server page as its source
    this.srcServer[nid]  = (this.originNum[src] != null) ? this.originNum[src] : this.srcServer[src];
    // G-FOLDER decision (documented): a duplicate inherits its source's folder memberships
    this.groups.forEach(function (g) {
      var i = g.pages.indexOf(src); if (i >= 0) g.pages.splice(i + 1, 0, nid);
    });
    this.pending.push({ type: 'duplicate', srcId: src, newId: nid });
  };

  // merge: append `n` pages from a foreign PDF (GoodNotes "import file"). v1 scope
  // = append-then-reorder (NOT insert-at-position). Merged pages have no source in
  // the current server PDF → srcServer=null (UI shows a placeholder until flush).
  PageModel.prototype.merge = function (n) {
    this._snap();
    var ids = [];
    for (var i = 0; i < n; i++) {
      var nid = newId();
      this.pageOrder.push(nid);
      this.PS_by_id[nid]   = { objects: [] };
      this.meta_by_id[nid] = blankMeta();
      this.originNum[nid]  = null;
      this.srcServer[nid]  = null;                           // comes from the merged file, not current PDF
      ids.push(nid);
    }
    this.pending.push({ type: 'merge', ids: ids.slice(), count: n });
    return ids;
  };

  /* ---- server flush replay (what POST /apply-page-mutations would return) ----
   * Replays the journal against _initialIds and returns
   * { renumberMap:{oldNum->newNum for ORIGINAL pages}, order:[ids] }.
   * Handles merge tokens (orig=null, like duplicates).
   */
  PageModel.prototype.simulateFlush = function () {
    var tokens = this._initialIds.map(function (id, idx) { return { id: id, orig: idx + 1 }; });
    this.pending.forEach(function (m) {
      if (m.type === 'reorder') {
        tokens = m.order.map(function (id) {
          for (var k = 0; k < tokens.length; k++) if (tokens[k].id === id) return tokens[k];
          return { id: id, orig: null };                     // dup/merge created earlier
        });
      } else if (m.type === 'delete') {
        tokens = tokens.filter(function (t) { return t.id !== m.id; });
      } else if (m.type === 'duplicate') {
        var pos = -1;
        for (var k = 0; k < tokens.length; k++) if (tokens[k].id === m.srcId) { pos = k; break; }
        tokens.splice(pos + 1, 0, { id: m.newId, orig: null });
      } else if (m.type === 'merge') {
        m.ids.forEach(function (id) { tokens.push({ id: id, orig: null }); });
      }
    });
    var renumberMap = {};
    tokens.forEach(function (t, i) { if (t.orig != null) renumberMap[t.orig] = i + 1; });
    return { renumberMap: renumberMap, order: tokens.map(function (t) { return t.id; }) };
  };

  // G-REFLUSH: after the server applies the mutations, the case PDF == current
  // order. Re-baseline so the NEXT save replays from here, not from the original.
  PageModel.prototype.applyFlush = function () {
    var self = this;
    this.pageOrder.forEach(function (id, i) { self.originNum[id] = i + 1; });
    this.srcServer = {};                 // every page now exists on the server
    this.pending = [];
    this._initialIds = this.pageOrder.slice();
    return true;
  };

  /* ---- .bmaplan save/load — mirrors REAL lite schema (ui-lite.html L1095-1111),
   *      ADDITIVE: adds pageIdentities; everything else number-keyed by display
   *      index so proto/legacy still read it. liteGroups.pages saved as NUMBERS. ---- */
  PageModel.prototype.save = function () {
    var self = this;
    var doc = {
      version: 1, app: 'bma-plan-lite',
      pageIdentities: this.pageOrder.slice(),               // NEW additive field
      pageStore: {}, pageRotations: {}, pageTags: {}, pageNames: {},
      excludedPages: [], pageFloorKind: {}, pageFloorNum: {},
      liteGroups: [],
    };
    var numById = {};
    this.pageOrder.forEach(function (id, i) {
      var n = i + 1, key = String(n); numById[id] = n;
      var mt = self.meta_by_id[id] || blankMeta();
      doc.pageStore[key] = deepCopy(self.PS_by_id[id]);
      if (mt.rot)        doc.pageRotations[key] = mt.rot;
      if (mt.tag)        doc.pageTags[key]      = mt.tag;
      if (mt.name)       doc.pageNames[key]     = mt.name;
      if (mt.floorKind)  doc.pageFloorKind[key] = mt.floorKind;
      if (mt.floorNum != null) doc.pageFloorNum[key] = mt.floorNum;
      if (mt.excl)       doc.excludedPages.push(n);
    });
    // liteGroups: id-membership -> number-membership, in display order
    doc.liteGroups = this.groups.map(function (g) {
      var nums = g.pages.map(function (id) { return numById[id]; })
                        .filter(function (x) { return x != null; })
                        .sort(function (a, b) { return a - b; });
      return { id: g.id, name: g.name, kind: g.kind, pages: nums };
    });
    return doc;
  };

  PageModel.prototype.load = function (doc) {
    this.pageOrder = []; this.PS_by_id = {}; this.meta_by_id = {};
    this.groups = []; this.originNum = {}; this.srcServer = {};
    this.pending = []; this.undoStack = []; this.curPage = 1;
    var self = this;
    var nums = Object.keys(doc.pageStore || {}).map(Number).sort(function (a, b) { return a - b; });
    var hasIds = Array.isArray(doc.pageIdentities) && doc.pageIdentities.length === nums.length;
    // excluded can be the lite ARRAY (excludedPages) OR a legacy dict (excluded)
    var exclSet = {};
    if (Array.isArray(doc.excludedPages)) doc.excludedPages.forEach(function (n) { exclSet[n] = true; });
    else if (doc.excluded) Object.keys(doc.excluded).forEach(function (k) { if (doc.excluded[k]) exclSet[+k] = true; });

    var numToId = {};
    nums.forEach(function (n, i) {
      var id = hasIds ? doc.pageIdentities[i] : newId();   // legacy: mint fresh ids (auto-migrate)
      var key = String(n);
      self.pageOrder.push(id); numToId[n] = id;
      self.PS_by_id[id] = deepCopy(doc.pageStore[key]);
      var mt = blankMeta();
      mt.rot       = (doc.pageRotations || doc.pageRot || {})[key] || 0;
      mt.tag       = (doc.pageTags  || {})[key] || '';
      mt.name      = (doc.pageNames || {})[key] || '';
      mt.floorKind = (doc.pageFloorKind || {})[key] || '';
      var fn = (doc.pageFloorNum || {})[key];
      mt.floorNum  = (fn === undefined ? null : fn);
      mt.excl      = !!exclSet[n];
      self.meta_by_id[id] = mt;
      self.originNum[id]  = i + 1;
    });
    // liteGroups: number-membership -> id-membership (legacy/proto already number-keyed)
    this.groups = (doc.liteGroups || []).map(function (g) {
      return {
        id: g.id, name: g.name, kind: g.kind,
        pages: (g.pages || []).map(function (n) { return numToId[n]; })
                              .filter(function (x) { return x != null; }),   // drop refs to missing pages
      };
    });
    this._initialIds = this.pageOrder.slice();
    this._migratedFromLegacy = !hasIds;
    return this;
  };

  /* full ordered snapshot for deep-equal round-trip checks */
  PageModel.prototype.snapshotByOrder = function () {
    var self = this;
    return this.pageOrder.map(function (id) {
      return { ps: self.PS_by_id[id], meta: self.meta_by_id[id] };
    });
  };
  // group membership as marker-letters in display order — for folder integrity checks
  PageModel.prototype.groupMarkers = function () {
    var self = this;
    return this.groups.map(function (g) {
      return { name: g.name, pages: g.pages.map(function (id) {
        var ps = self.PS_by_id[id]; return ps && ps.objects[0]; }) };
    });
  };

  PageModel.deepEq = deepEq;
  PageModel.newId = newId;
  PageModel.blankMeta = blankMeta;
  root.PageModelV2 = PageModel;
  if (typeof module !== 'undefined' && module.exports) module.exports = PageModel;
})(typeof window !== 'undefined' ? window : globalThis);
