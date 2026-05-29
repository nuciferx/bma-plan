/*
 * page-manager.js — lite runtime module: Approach D page-identity model.
 * (INV-2026-05-29-LPM Slice 1 — FOUNDATION ONLY, no UI wiring)
 *
 * Promoted from lite/sandbox/invent-page-manager/page-model-v2.js with
 * Re-pass #2 corrections applied:
 *   - G-FOLDER remap dropped: folder membership is DERIVED, not stored.
 *     Expose deriveFolderMap() helper instead of groups/groupsOf.
 *   - No-op reorder guard: reorder(from, to) with from===to is a true no-op.
 *   - Dirty fingerprint: dirtySnap() for integration with _docSnap().
 *   - liteGroups preserved in save/load for backward compat with existing
 *     .bmaplan files — but NOT maintained internally during mutations.
 *
 * Browser + Node dual export (same pattern as measure-engine.js):
 *   Browser: window.PageModel
 *   Node:    module.exports = PageModel
 *
 * Hard constraints respected:
 *   - NEVER touches measure-engine.js, RS, pdfToC/cToPdf, ui-lite.html,
 *     server_lite.py, or any existing static/js/*.js.
 *   - .bmaplan additions are additive only (pageIdentities); no renames/removes.
 *   - No global side effects, no DOMContentLoaded, no auto-init.
 *   - No IIFE wrap beyond the dual-export envelope; plain globals when in browser.
 */
(function (root) {
  'use strict';

  var _idc = 0;
  // Deterministic id generator — counter-based for byte-stable round-trips.
  // Reset between test runs by the eval harness via PageModel._resetIdc().
  function newId() { return 'pg' + (_idc++); }

  function deepCopy(o) { return (o == null) ? o : JSON.parse(JSON.stringify(o)); }
  function deepEq(a, b) { return JSON.stringify(a) === JSON.stringify(b); }

  // The per-page scalar record — ONE place for all 6 scalars.
  // Adding a future per-page field = add here + in save()/load() fan-out.
  function blankMeta() {
    return { tag: '', rot: 0, excl: false, floorKind: '', floorNum: null, name: '' };
  }

  // -------------------------------------------------------------------------
  // Folder-id derivation rule — mirrors pageFolderIdFor() in
  // lite/static/js/page-folder-layers.js (plain-value calling convention).
  // Used by deriveFolderMap(); kept in sync with the real function by inspection.
  // -------------------------------------------------------------------------
  function _folderIdFor(tag, floorNum, kind) {
    if (!tag || tag === 'excluded') return 'PF_excluded';
    if (tag === 'site') return 'PF_site';
    if (tag !== 'floor') return 'PF_excluded';
    kind = kind || 'normal';
    if (floorNum === 'roof' || kind === 'rooftop') return 'PF_floor_roof';
    if (floorNum === undefined || floorNum === null || floorNum === '') return 'PF_excluded';
    if (kind === 'basement')   return 'PF_basement_' + floorNum;
    if (kind === 'mezzanine')  return 'PF_mezz_'     + floorNum;
    if (kind === 'mechanical') return 'PF_mech_'     + floorNum;
    return 'PF_floor_' + floorNum;
  }

  // -------------------------------------------------------------------------
  // PageModel constructor
  // -------------------------------------------------------------------------
  function PageModel() {
    this.pageOrder   = [];   // [id, ...]  display order; pageNum = index + 1
    this.PS_by_id    = {};   // id -> { objects: [...] }   (measurement store)
    this.meta_by_id  = {};   // id -> { tag, rot, excl, floorKind, floorNum, name }
    this.originNum   = {};   // id -> page# in CURRENT server PDF (null = client-new)
    this.srcServer   = {};   // id -> server page to RENDER FROM pre-flush (dup pages)
    this.pending     = [];   // mutation journal (flushed at save/export)
    this.undoStack   = [];   // Ctrl+Z snapshot stack
    this.undoCap     = 30;   // bound undo memory (45-page docs blow up an unbounded stack)
    this.curPage     = 1;    // currently-visible display page
    this._initialIds = [];   // baseline order for the CURRENT server PDF (reset by applyFlush)
    this._migratedFromLegacy = false;
    // liteGroups: kept for save/load backward compat with existing .bmaplan files.
    // NOT maintained during mutations — folder membership is DERIVED via deriveFolderMap().
    this._savedGroups = [];  // raw liteGroups from the last load(); re-emitted on save()
  }

  // -------------------------------------------------------------------------
  // Accessors
  // -------------------------------------------------------------------------
  PageModel.prototype.idAt    = function (n)   { return this.pageOrder[n - 1]; };
  PageModel.prototype.numOf   = function (id)  { return this.pageOrder.indexOf(id) + 1; };
  PageModel.prototype.count   = function ()    { return this.pageOrder.length; };
  PageModel.prototype.PSn     = function (n)   { return this.PS_by_id[this.idAt(n)]; };
  PageModel.prototype.metaN   = function (n)   { return this.meta_by_id[this.idAt(n)]; };

  // G-RENDER: which SERVER page# to render/thumb for display page n, pre-flush.
  //   original page  -> its server#
  //   duplicate      -> source's server# (renders from source until flush)
  //   merged page    -> null (no source in current server PDF; caller shows placeholder)
  PageModel.prototype.serverNum = function (n) {
    var id = this.idAt(n);
    if (this.originNum[id] != null) return this.originNum[id];
    return (id in this.srcServer) ? this.srcServer[id] : null;
  };

  // -------------------------------------------------------------------------
  // Folder-membership derivation (C-FOLDER / Re-pass #2)
  // Returns { folderId: [displayPageNumbers...] } in display order.
  // This is a pure computation from current meta — no stored state.
  // The integration slice calls reseedActivePageFolders() after mutations; this
  // helper is available for cross-checking and testing.
  // -------------------------------------------------------------------------
  PageModel.prototype.deriveFolderMap = function () {
    var out = {};
    var self = this;
    this.pageOrder.forEach(function (id, i) {
      var mt = self.meta_by_id[id] || blankMeta();
      var fid = _folderIdFor(mt.tag, mt.floorNum, mt.floorKind);
      if (!out[fid]) out[fid] = [];
      out[fid].push(i + 1);
    });
    return out;
  };

  // -------------------------------------------------------------------------
  // Dirty fingerprint (B-DIRTY / Re-pass #2)
  // Returns a JSON string covering page order + all per-page data.
  // The integration slice folds this into lite's _docSnap() so that a pure
  // reorder/dup/del marks the document dirty (no silent data loss on close).
  // -------------------------------------------------------------------------
  PageModel.prototype.dirtySnap = function () {
    return JSON.stringify({
      order: this.pageOrder,
      PS:    this.PS_by_id,
      meta:  this.meta_by_id,
    });
  };

  // -------------------------------------------------------------------------
  // Undo machinery
  // -------------------------------------------------------------------------
  PageModel.prototype._snap = function () {
    this.undoStack.push(deepCopy({
      pageOrder:  this.pageOrder,
      PS_by_id:   this.PS_by_id,
      meta_by_id: this.meta_by_id,
      originNum:  this.originNum,
      srcServer:  this.srcServer,
      pending:    this.pending,
      curPage:    this.curPage,
    }));
    if (this.undoStack.length > this.undoCap) this.undoStack.shift(); // bound memory
  };

  PageModel.prototype.undo = function () {
    if (!this.undoStack.length) return false;
    var s = this.undoStack.pop();
    this.pageOrder  = s.pageOrder;
    this.PS_by_id   = s.PS_by_id;
    this.meta_by_id = s.meta_by_id;
    this.originNum  = s.originNum;
    this.srcServer  = s.srcServer;
    this.pending    = s.pending;
    this.curPage    = s.curPage;
    return true;
  };

  // -------------------------------------------------------------------------
  // Mutations (instant; server is synced on flush)
  // -------------------------------------------------------------------------

  // B-NOOP guard (Re-pass #2): from===to is a true no-op — skip snapshot + journal.
  PageModel.prototype.reorder = function (from, to) {
    if (from === to) return;   // no-op: no snapshot, no journal entry
    this._snap();
    var id = this.pageOrder.splice(from, 1)[0];
    this.pageOrder.splice(to, 0, id);
    this.pending.push({ type: 'reorder', order: this.pageOrder.slice() });
    // Folder membership is DERIVED (not stored here) — caller calls reseedActivePageFolders().
  };

  // G-GUARD: refuse to delete the last page (doc must always have ≥1 page).
  PageModel.prototype.del = function (at) {
    if (this.count() <= 1) return false;
    this._snap();
    var id = this.pageOrder.splice(at, 1)[0];
    var origin = this.originNum[id];
    delete this.PS_by_id[id];
    delete this.meta_by_id[id];
    delete this.originNum[id];
    delete this.srcServer[id];
    this.pending.push({ type: 'delete', id: id, origin: origin });
    if (this.curPage > this.count()) this.curPage = Math.max(1, this.count());
    return true;
  };

  // Duplicate: deep-copy, independent, inherits server render source pre-flush.
  PageModel.prototype.duplicate = function (at) {
    this._snap();
    var src = this.pageOrder[at];
    var nid = newId();
    this.pageOrder.splice(at + 1, 0, nid);
    this.PS_by_id[nid]   = deepCopy(this.PS_by_id[src]);    // independent deep copy
    this.meta_by_id[nid] = deepCopy(this.meta_by_id[src]);
    this.originNum[nid]  = null;                             // not on server yet
    // G-RENDER: until flush, the copy renders from the same server page as its source.
    this.srcServer[nid]  = (this.originNum[src] != null)
                           ? this.originNum[src]
                           : this.srcServer[src];
    this.pending.push({ type: 'duplicate', srcId: src, newId: nid });
  };

  // Merge: append n foreign pages (from a merged PDF). Merged pages have no source
  // in the current server PDF — srcServer=null (UI shows a placeholder until flush).
  PageModel.prototype.merge = function (n) {
    this._snap();
    var ids = [];
    for (var i = 0; i < n; i++) {
      var nid = newId();
      this.pageOrder.push(nid);
      this.PS_by_id[nid]   = { objects: [] };
      this.meta_by_id[nid] = blankMeta();
      this.originNum[nid]  = null;
      this.srcServer[nid]  = null;   // comes from the merged file, not the current PDF
      ids.push(nid);
    }
    this.pending.push({ type: 'merge', ids: ids.slice(), count: n });
    return ids;
  };

  // -------------------------------------------------------------------------
  // Server flush
  // -------------------------------------------------------------------------

  // simulateFlush: replays the journal against _initialIds.
  // Returns { renumberMap:{origNum->newNum}, order:[ids] }.
  // Handles merge tokens (orig=null, like duplicates).
  PageModel.prototype.simulateFlush = function () {
    var tokens = this._initialIds.map(function (id, idx) {
      return { id: id, orig: idx + 1 };
    });
    this.pending.forEach(function (m) {
      if (m.type === 'reorder') {
        tokens = m.order.map(function (id) {
          for (var k = 0; k < tokens.length; k++) {
            if (tokens[k].id === id) return tokens[k];
          }
          return { id: id, orig: null };   // dup/merge token created earlier
        });
      } else if (m.type === 'delete') {
        tokens = tokens.filter(function (t) { return t.id !== m.id; });
      } else if (m.type === 'duplicate') {
        var pos = -1;
        for (var k = 0; k < tokens.length; k++) {
          if (tokens[k].id === m.srcId) { pos = k; break; }
        }
        tokens.splice(pos + 1, 0, { id: m.newId, orig: null });
      } else if (m.type === 'merge') {
        m.ids.forEach(function (id) { tokens.push({ id: id, orig: null }); });
      }
    });
    var renumberMap = {};
    tokens.forEach(function (t, i) {
      if (t.orig != null) renumberMap[t.orig] = i + 1;
    });
    return { renumberMap: renumberMap, order: tokens.map(function (t) { return t.id; }) };
  };

  // G-REFLUSH: after the server applies mutations, the case PDF IS the current order.
  // Re-baseline so the NEXT save replays from here, not from the original.
  PageModel.prototype.applyFlush = function () {
    var self = this;
    this.pageOrder.forEach(function (id, i) { self.originNum[id] = i + 1; });
    this.srcServer   = {};                   // every page now exists on the server
    this.pending     = [];
    this._initialIds = this.pageOrder.slice();
    return true;
  };

  // -------------------------------------------------------------------------
  // Save / load — mirrors real lite .bmaplan schema (ui-lite.html ~L910-912,
  // L1095-1111). ADDITIVE: adds pageIdentities. Everything else number-keyed by
  // display index for proto/legacy compat. excludedPages saved as ARRAY.
  // liteGroups: preserved from last load() for backward compat; NOT updated
  // during mutations (folder membership is DERIVED in the live app).
  // -------------------------------------------------------------------------
  PageModel.prototype.save = function () {
    var self = this;
    var doc = {
      version: 1,
      app: 'bma-plan-lite',
      pageIdentities: this.pageOrder.slice(),      // NEW additive field
      pageStore:      {},
      pageRotations:  {},
      pageTags:       {},
      pageNames:      {},
      excludedPages:  [],
      pageFloorKind:  {},
      pageFloorNum:   {},
      liteGroups:     this._savedGroups || [],     // pass through; not re-derived here
    };
    this.pageOrder.forEach(function (id, i) {
      var n   = i + 1;
      var key = String(n);
      var mt  = self.meta_by_id[id] || blankMeta();
      doc.pageStore[key] = deepCopy(self.PS_by_id[id]);
      if (mt.rot)            doc.pageRotations[key] = mt.rot;
      if (mt.tag)            doc.pageTags[key]      = mt.tag;
      if (mt.name)           doc.pageNames[key]     = mt.name;
      if (mt.floorKind)      doc.pageFloorKind[key] = mt.floorKind;
      if (mt.floorNum != null) doc.pageFloorNum[key] = mt.floorNum;
      if (mt.excl)           doc.excludedPages.push(n);
    });
    return doc;
  };

  PageModel.prototype.load = function (doc) {
    this.pageOrder   = [];
    this.PS_by_id    = {};
    this.meta_by_id  = {};
    this.originNum   = {};
    this.srcServer   = {};
    this.pending     = [];
    this.undoStack   = [];
    this.curPage     = 1;
    this._savedGroups = [];

    var self = this;
    var nums = Object.keys(doc.pageStore || {})
                     .map(Number)
                     .sort(function (a, b) { return a - b; });
    var hasIds = Array.isArray(doc.pageIdentities) &&
                 doc.pageIdentities.length === nums.length;

    // excluded: lite ARRAY form (excludedPages) OR legacy dict (excluded)
    var exclSet = {};
    if (Array.isArray(doc.excludedPages)) {
      doc.excludedPages.forEach(function (n) { exclSet[n] = true; });
    } else if (doc.excluded) {
      Object.keys(doc.excluded).forEach(function (k) {
        if (doc.excluded[k]) exclSet[+k] = true;
      });
    }

    nums.forEach(function (n, i) {
      var id  = hasIds ? doc.pageIdentities[i] : newId();  // legacy: mint fresh ids
      var key = String(n);
      self.pageOrder.push(id);
      self.PS_by_id[id] = deepCopy(doc.pageStore[key]);
      var mt = blankMeta();
      mt.rot      = (doc.pageRotations || doc.pageRot || {})[key] || 0;
      mt.tag      = (doc.pageTags      || {})[key] || '';
      mt.name     = (doc.pageNames     || {})[key] || '';
      mt.floorKind= (doc.pageFloorKind || {})[key] || '';
      var fn = (doc.pageFloorNum || {})[key];
      mt.floorNum = (fn === undefined) ? null : fn;
      mt.excl     = !!exclSet[n];
      self.meta_by_id[id] = mt;
      self.originNum[id]  = i + 1;
    });

    // Preserve liteGroups verbatim — passed through on save() for backward compat.
    // The live app re-derives folder membership via reseedActivePageFolders().
    this._savedGroups = deepCopy(doc.liteGroups || []);

    this._initialIds = this.pageOrder.slice();
    this._migratedFromLegacy = !hasIds;
    return this;
  };

  // -------------------------------------------------------------------------
  // Snapshot for deep-equal round-trip checks (used by E4 / eval harness)
  // -------------------------------------------------------------------------
  PageModel.prototype.snapshotByOrder = function () {
    var self = this;
    return this.pageOrder.map(function (id) {
      return { ps: self.PS_by_id[id], meta: self.meta_by_id[id] };
    });
  };

  // -------------------------------------------------------------------------
  // Static helpers
  // -------------------------------------------------------------------------
  PageModel.deepEq   = deepEq;
  PageModel.blankMeta = blankMeta;
  PageModel.newId    = newId;
  // For test harness: reset the id counter so eval runs are deterministic.
  PageModel._resetIdc = function () { _idc = 0; };

  // -------------------------------------------------------------------------
  // Dual export (browser global + Node module)
  // -------------------------------------------------------------------------
  root.PageModel = PageModel;
  if (typeof module !== 'undefined' && module.exports) module.exports = PageModel;

})(typeof window !== 'undefined' ? window : globalThis);
