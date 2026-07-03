/* LAYER-MOVE — move-object-to-layer UI (B4, INV-20260703-layer-linkage).
   Plain-globals. Dynamically loaded by page-folder-layers.js (__lmove_script__)
   — avoids editing ui-lite.html (1200-line cap; LOVS DOM-injection+wrap pattern).
   H1 fix: re-file an already-drawn object (or CFSS master, or multi-selection)
   onto another layer in place instead of delete+redraw; object-agg.js reads
   catId live every call -> instantly consistent everywhere by construction.
   DESIGN: sets BOTH o.catId AND o.semanticTag = target layer's role tag
   (resolveSemanticTag) — a couple of legacy fallback branches read semanticTag
   directly, so keep both in lockstep (value change on fields, still additive).
   CFSS instances have no catId of their own (rollupCatId semantics) — a move
   retargets the MASTER via updateMaster(), so EVERY instance moves together;
   UI confirm()s this. Public API (window): moveObjectToLayer(obj,layerId),
   moveObjectsToLayer(objs,layerId), buildMoveMenuItems(obj) -> layers other
   than obj's current one, defaults first then customs, in layersInOrder(). */
if (window.__lmove_loaded__) { /* already loaded */ } else {
window.__lmove_loaded__ = true;
function buildMoveMenuItems(obj) {
  var curId = (typeof rollupCatId === "function") ? rollupCatId(obj) : (obj && obj.catId);
  var all = (typeof layersInOrder === "function") ? layersInOrder() : [], defaults = [], customs = [];
  all.forEach(function (l) { if (l.id !== curId) (isDefaultLayer(l.id) ? defaults : customs).push({id: l.id, name: l.name, color: l.color, role: l.role}); });
  return defaults.concat(customs); }
/* Batch move — ONE pushUndo/dirty/redraw (matches duplicateSel/delete convention).
   CFSS instances collapse onto their shared master (deduplicated); ONE confirm()
   covers the batch, decline aborts the WHOLE move. Returns count of distinct
   targets (objects+masters) actually changed. */
function moveObjectsToLayer(objs, layerId) {
  var layer = (typeof layerById === "function") ? layerById(layerId) : null;
  if (!layer || !objs || !objs.length) return 0;
  var tag = (typeof resolveSemanticTag === "function") ? resolveSemanticTag(layerId) : layer.tag;
  var plainObjs = [], masterIds = {};
  objs.forEach(function (o) { if (typeof isInstance === "function" && isInstance(o)) masterIds[o.masterId] = true; else plainObjs.push(o); });
  var masterIdList = Object.keys(masterIds);
  if (!plainObjs.length && !masterIdList.length) return 0;
  if (masterIdList.length && typeof window.confirm === "function") {
    var msg = "ย้ายมาสเตอร์ข้ามชั้น" + (masterIdList.length > 1 ? " (" + masterIdList.length + " มาสเตอร์)" : "") + " ไปเลเยอร์ \"" + layer.name + "\"? ทุก instance ของมาสเตอร์นี้บนทุกชั้นจะย้ายตามด้วย";
    if (!window.confirm(msg)) return 0;
  }
  if (typeof pushUndo === "function") pushUndo();
  var changed = 0;
  plainObjs.forEach(function (o) { o.catId = layerId; o.semanticTag = tag; changed++; });
  masterIdList.forEach(function (mid) { if (typeof updateMaster === "function") { updateMaster(mid, {catId: layerId, semanticTag: tag}); changed++; } });
  if (changed) {
    if (typeof state !== "undefined") { state.dirty = true; if (typeof window.showProps === "function") window.showProps(state.sel || null); }
    if (typeof buildPicker === "function") buildPicker();
    if (typeof draw === "function") draw(); }
  return changed; }
function moveObjectToLayer(obj, layerId) { return moveObjectsToLayer([obj], layerId); }
window.moveObjectToLayer = moveObjectToLayer; window.moveObjectsToLayer = moveObjectsToLayer; window.buildMoveMenuItems = buildMoveMenuItems;
/* ---- UI wiring: DOM injection (LOVS pattern) + idempotent wraps ---- */
var _lmoveMenuEl = null, _lmoveMenuOutside = null;
function _lmoveCloseMenu() {
  if (_lmoveMenuEl) { _lmoveMenuEl.remove(); _lmoveMenuEl = null; }
  if (_lmoveMenuOutside) { document.removeEventListener("click", _lmoveMenuOutside, true); _lmoveMenuOutside = null; } }
/* Secondary chooser popup at the objmenu row's own anchor (the row's own click
   already closed the objmenu, so a true nested submenu is awkward — documented
   alternative per spec). */
function showMoveMenu(cx, cy, objs) {
  _lmoveCloseMenu(); if (!objs || !objs.length) return;
  var items = buildMoveMenuItems(objs[0]), m = document.createElement("div"); m.className = "objmenu";
  items.forEach(function (it) {
    var r = document.createElement("div"); r.className = "objmenu-row";
    r.innerHTML = '<span style="display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:6px;background:' + it.color + '"></span>' + it.name;
    r.addEventListener("click", function (e) { e.stopPropagation(); _lmoveCloseMenu(); moveObjectsToLayer(objs, it.id); });
    m.appendChild(r);
  });
  var vw = window.innerWidth, vh = window.innerHeight, mw = 180, mh = items.length * 32 + 8;
  m.style.left = Math.min(cx, vw - mw - 8) + "px"; m.style.top = Math.min(cy, vh - mh - 8) + "px";
  document.body.appendChild(m); _lmoveMenuEl = m;
  _lmoveMenuOutside = function (e) { if (!m.contains(e.target)) _lmoveCloseMenu(); };
  setTimeout(function () { document.addEventListener("click", _lmoveMenuOutside, true); }, 0); }
window.__lmoveShowMenu = showMoveMenu;
/* Wrap showObjMenu() to append a "ย้ายไปเลเยอร์ ▸" row (CFSS-3 wrap pattern). */
function _lmoveWrapShowObjMenu() {
  if (typeof window.showObjMenu !== "function" || window.showObjMenu.__lmoveWrapped) return;
  var orig = window.showObjMenu;
  window.showObjMenu = function (cx, cy, obj) {
    orig.apply(this, arguments);
    var menus = document.querySelectorAll(".objmenu"); if (!menus.length) return;
    var m = menus[menus.length - 1], st = (typeof state !== "undefined") ? state : null;
    var multi = !!(st && st.selSet && st.selSet.length > 1 && st.selSet.indexOf(obj) >= 0);
    var targets = multi ? st.selSet.slice() : [obj], r = document.createElement("div"); r.className = "objmenu-row";
    r.textContent = multi ? ("ย้ายทั้งหมด (" + targets.length + ") ไปเลเยอร์ ▸") : "ย้ายไปเลเยอร์ ▸";
    r.addEventListener("click", function (e) { e.stopPropagation(); if (typeof window.closeObjMenu === "function") window.closeObjMenu(); showMoveMenu(cx, cy, targets); });
    m.appendChild(r);
  };
  for (var k in orig) { if (Object.prototype.hasOwnProperty.call(orig, k)) window.showObjMenu[k] = orig[k]; } // preserve prior wrap flags (e.g. CFSS's __cfssWrapped)
  window.showObjMenu.__lmoveWrapped = true; }
/* Property-panel <select> — injected once into #props (LOVS pattern); synced via the showProps() wrap below. */
function _lmoveEnsurePropsSelect() {
  var existing = document.getElementById("p-move"); if (existing) return existing;
  var box = document.getElementById("props"); if (!box) return null;
  var sel = document.createElement("select"); sel.id = "p-move"; sel.title = "ย้ายไปเลเยอร์"; sel.style.marginLeft = "6px";
  var delBtn = document.getElementById("p-del"); if (delBtn) box.insertBefore(sel, delBtn); else box.appendChild(sel);
  sel.addEventListener("change", function () {
    var val = sel.value, st = (typeof state !== "undefined") ? state : null; if (!val) return;
    var targets = (st && st.selSet && st.selSet.length > 1) ? st.selSet.slice() : (st && st.sel ? [st.sel] : []);
    if (targets.length) moveObjectsToLayer(targets, val);
  });
  return sel; }
function _lmoveSyncPropsSelect() {
  var sel = _lmoveEnsurePropsSelect(); if (!sel) return;
  var st = (typeof state !== "undefined") ? state : null, multi = !!(st && st.selSet && st.selSet.length > 1);
  var refObj = multi ? st.selSet[0] : (st && (st.sel || (st.selSet && st.selSet[0])));
  if (!refObj) { sel.style.display = "none"; sel.innerHTML = ""; return; }
  var items = buildMoveMenuItems(refObj);
  sel.innerHTML = '<option value="">' + (multi ? ("ย้าย " + st.selSet.length + " รายการไปเลเยอร์…") : "ย้ายไปเลเยอร์…") + '</option>' +
    items.map(function (it) { return '<option value="' + it.id + '">' + it.name + '</option>'; }).join("");
  sel.style.display = ""; }
window.__lmoveSyncPropsSelect = _lmoveSyncPropsSelect;
/* Wrap showProps() to keep the select in sync (cap-avoidance: no ui-lite.html edit). */
function _lmoveWrapShowProps() {
  if (typeof window.showProps !== "function" || window.showProps.__lmoveWrapped) return;
  var orig = window.showProps;
  window.showProps = function (o) { orig.apply(this, arguments); _lmoveSyncPropsSelect(); };
  window.showProps.__lmoveWrapped = true; }
function _lmoveBootstrap() { _lmoveEnsurePropsSelect(); _lmoveWrapShowObjMenu(); _lmoveWrapShowProps(); }
/* Dynamically-injected scripts usually run AFTER DOMContentLoaded already fired;
   setTimeout(0) lets any in-progress script finish first (LOVS pattern). */
if (document.readyState === "loading") { document.addEventListener("DOMContentLoaded", _lmoveBootstrap); } else { setTimeout(_lmoveBootstrap, 0); }
} /* end __lmove_loaded__ guard */
