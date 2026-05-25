/* ============================================================
   CROSS-FLOOR SHARED SHAPES — metric-master + per-floor instances (CFSS-1)
   Plain-globals module. No IIFE, no export, no bundler.
   Dynamically loaded by page-folder-layers.js via __cfss_script__ tag.

   Approach A (metric-master in MASTERS global):
     Geometry stored in metric units (m). Instances hold only an offsetPt
     (in PDF points, page-local). On draw/area-compute, master.metricPts
     are scaled by current page pts_per_m — never cached.

   This is NOT editing polyAreaM2 / measure-engine.js. instanceAreaM2 is
   a new shoelace function on metric inputs (no ppm divisor needed), placed
   next to forbidden surfaces per the "add new functions next to them" rule.

   Public API (all on window):
     MASTERS                — Map<id, master>; preserved on reload
     addMaster(name, metricPts, color, opts)
     updateMaster(id, patch)
     removeMaster(id)
     masterById(id)
     mastersInOrder()
     makeInstance(masterId, offsetPt)
     isInstance(obj)
     resolveInstancePts(instance, ppm)
     instanceAreaM2(instance, ppm)
     freezeOrphansForMaster(masterId, allPages)
   ============================================================ */

/* Idempotent reload guard — preserves MASTERS and counter across re-injection */
if (window.__cfss_loaded__) {
  /* already loaded; skip re-definition but leave MASTERS intact */
} else {
window.__cfss_loaded__ = true;

/* ------------------------------------------------------------------ */
/* MASTERS storage — preserved on reload via ||                        */
/* ------------------------------------------------------------------ */
window.MASTERS = window.MASTERS || {};
window.__cfss_nextMasterIdN = window.__cfss_nextMasterIdN || 1;

/* ------------------------------------------------------------------ */
/* Internal helper — shallow-clone metricPts array                     */
/* ------------------------------------------------------------------ */
function _cfssClonePts(pts) {
  if (!pts || !pts.length) return [];
  var out = [];
  for (var i = 0; i < pts.length; i++) {
    out.push({x_m: Number(pts[i].x_m), y_m: Number(pts[i].y_m)});
  }
  return out;
}

/* ------------------------------------------------------------------ */
/* Internal helper — validate metricPts (array of >=3 {x_m, y_m})    */
/* ------------------------------------------------------------------ */
function _cfssValidatePts(pts) {
  if (!Array.isArray(pts) || pts.length < 3) return false;
  for (var i = 0; i < pts.length; i++) {
    if (typeof pts[i].x_m !== 'number' || typeof pts[i].y_m !== 'number') return false;
    if (!isFinite(pts[i].x_m) || !isFinite(pts[i].y_m)) return false;
  }
  return true;
}

/* ================================================================== */
/* Master CRUD                                                         */
/* ================================================================== */

/**
 * addMaster(name, metricPts, color, opts)
 * Validates metricPts: array of >=3 {x_m:number, y_m:number}.
 * Returns string id like 'm1', 'm2', ... or null on validation failure.
 */
function addMaster(name, metricPts, color, opts) {
  if (typeof name !== 'string') return null;
  if (!_cfssValidatePts(metricPts)) return null;
  var id = 'm' + (window.__cfss_nextMasterIdN++);
  var master = {
    id: id,
    name: name,
    metricPts: _cfssClonePts(metricPts),
    color: (typeof color === 'string' && color) ? color : '#888',
    createdAt: Date.now()
  };
  /* merge any extra opts (e.g. catId for future use) */
  if (opts && typeof opts === 'object') {
    for (var k in opts) {
      if (Object.prototype.hasOwnProperty.call(opts, k) &&
          k !== 'id' && k !== 'metricPts' && k !== 'createdAt') {
        master[k] = opts[k];
      }
    }
  }
  window.MASTERS[id] = master;
  return id;
}

/**
 * updateMaster(id, patch)
 * Merges patch onto MASTERS[id]. Clones metricPts on assignment.
 * Returns updated master or null if id missing.
 */
function updateMaster(id, patch) {
  var master = window.MASTERS[id];
  if (!master) return null;
  if (!patch || typeof patch !== 'object') return master;
  for (var k in patch) {
    if (!Object.prototype.hasOwnProperty.call(patch, k)) continue;
    if (k === 'id' || k === 'createdAt') continue; /* immutable fields */
    if (k === 'metricPts') {
      if (_cfssValidatePts(patch.metricPts)) {
        master.metricPts = _cfssClonePts(patch.metricPts);
      }
    } else {
      master[k] = patch[k];
    }
  }
  return master;
}

/**
 * removeMaster(id)
 * Deletes MASTERS[id]. Returns true/false.
 * Caller MUST call freezeOrphansForMaster(id, allPages) BEFORE this.
 */
function removeMaster(id) {
  if (!window.MASTERS[id]) return false;
  delete window.MASTERS[id];
  return true;
}

/** masterById(id) — returns master or undefined */
function masterById(id) {
  return window.MASTERS[id];
}

/** mastersInOrder() — sorted by createdAt ascending, returns array */
function mastersInOrder() {
  var arr = [];
  for (var k in window.MASTERS) {
    if (Object.prototype.hasOwnProperty.call(window.MASTERS, k)) {
      arr.push(window.MASTERS[k]);
    }
  }
  arr.sort(function(a, b) {
    return (a.createdAt || 0) - (b.createdAt || 0);
  });
  return arr;
}

/* ================================================================== */
/* Instance helpers                                                    */
/* ================================================================== */

/**
 * makeInstance(masterId, offsetPt)
 * Returns {kind:'instance', masterId, offsetPt:{x,y}}.
 * Does NOT push anywhere — caller does PS[pg].objects.push(makeInstance(...)).
 */
function makeInstance(masterId, offsetPt) {
  var ox = offsetPt && typeof offsetPt.x === 'number' ? Number(offsetPt.x) : 0;
  var oy = offsetPt && typeof offsetPt.y === 'number' ? Number(offsetPt.y) : 0;
  return {
    kind: 'instance',
    masterId: String(masterId),
    offsetPt: {x: ox, y: oy}
  };
}

/**
 * isInstance(obj)
 * Returns true iff obj is a valid instance descriptor.
 */
function isInstance(obj) {
  return !!(obj &&
    typeof obj === 'object' &&
    obj.kind === 'instance' &&
    typeof obj.masterId === 'string');
}

/**
 * resolveInstancePts(instance, ppm)
 * Returns {pts:[{x,y}...], bbox:{x,y,w,h}} or null if master missing or ppm<=0.
 * pts[i].x = master.metricPts[i].x_m * ppm + instance.offsetPt.x
 * pts[i].y = master.metricPts[i].y_m * ppm + instance.offsetPt.y
 */
function resolveInstancePts(instance, ppm) {
  if (!isInstance(instance)) return null;
  var master = window.MASTERS[instance.masterId];
  if (!master) return null;
  if (!(ppm > 0)) return null;
  var ox = (instance.offsetPt && typeof instance.offsetPt.x === 'number') ? instance.offsetPt.x : 0;
  var oy = (instance.offsetPt && typeof instance.offsetPt.y === 'number') ? instance.offsetPt.y : 0;
  var mp = master.metricPts;
  var pts = [];
  var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (var i = 0; i < mp.length; i++) {
    var x = mp[i].x_m * ppm + ox;
    var y = mp[i].y_m * ppm + oy;
    pts.push({x: x, y: y});
    if (x < minX) minX = x;
    if (y < minY) minY = y;
    if (x > maxX) maxX = x;
    if (y > maxY) maxY = y;
  }
  var bbox = {x: minX, y: minY, w: maxX - minX, h: maxY - minY};
  return {pts: pts, bbox: bbox};
}

/* ================================================================== */
/* Area math — NEW function, does NOT edit polyAreaM2                  */
/* ================================================================== */

/**
 * instanceAreaM2(instance, ppm)
 * ppm is accepted for API symmetry but UNUSED in area computation.
 * Area = metric-shoelace on master.metricPts directly (already in m).
 * Result is ppm-independent by construction.
 * Returns null if master missing or <3 pts.
 */
function instanceAreaM2(instance, ppm) {
  if (!isInstance(instance)) return null;
  var master = window.MASTERS[instance.masterId];
  if (!master) return null;
  var mp = master.metricPts;
  if (!mp || mp.length < 3) return null;
  var n = mp.length;
  var a = 0;
  for (var i = 0; i < n; i++) {
    var j = (i + 1) % n;
    a += mp[i].x_m * mp[j].y_m - mp[j].x_m * mp[i].y_m;
  }
  return Math.abs(a) / 2;
}

/* ================================================================== */
/* Orphan-freeze                                                       */
/* ================================================================== */

/**
 * freezeOrphansForMaster(masterId, allPages)
 * allPages = [{page: {objects:[...]}, ppm: number}, ...]
 * For every instance of masterId: resolves pts, converts to plain poly,
 * sets orphan:true + fromMasterId.
 * Returns count of objects frozen.
 */
function freezeOrphansForMaster(masterId, allPages) {
  if (!Array.isArray(allPages)) return 0;
  var count = 0;
  for (var pi = 0; pi < allPages.length; pi++) {
    var entry = allPages[pi];
    if (!entry || !entry.page) continue;
    var objs = entry.page.objects;
    if (!Array.isArray(objs)) continue;
    var ppm = Number(entry.ppm) || 1;
    for (var oi = 0; oi < objs.length; oi++) {
      var obj = objs[oi];
      if (!isInstance(obj) || obj.masterId !== masterId) continue;
      var resolved = resolveInstancePts(obj, ppm);
      var frozenPts = resolved ? resolved.pts.slice() : [];
      obj.kind = 'poly';
      obj.pts = frozenPts;
      obj.orphan = true;
      obj.fromMasterId = masterId;
      delete obj.masterId;
      delete obj.offsetPt;
      count++;
    }
  }
  return count;
}

/* ================================================================== */
/* CFSS-2: Persist — save/load monkey-patches                         */
/* ================================================================== */

/**
 * cfssWrapSave()
 * Wraps the #mi-save onclick to:
 *   1. Strip instance objects from PS before buildPageStore() serialises them
 *      (instances have no .pts and would produce broken poly entries).
 *   2. Temporarily wrap JSON.stringify to inject masters + instances into the
 *      emitted doc. The wrap is scoped — restored in finally even on throw.
 */
function cfssWrapSave() {
  var btn = document.getElementById('mi-save');
  if (!btn || btn.__cfssSaveWrapped) return;
  var origHandler = btn.onclick;
  if (typeof origHandler !== 'function') return; // not yet bound; bootstrap retries via DOMContentLoaded
  btn.__cfssSaveWrapped = true;
  btn.onclick = function(e) {
    // 1. Strip instances out of PS so buildPageStore doesn't see them.
    //    Collect their descriptors into dump[] for the new top-level key.
    var stash = {}; // { pageKey: original objects array }
    var dump  = []; // [{page, masterId, offsetPt:{x,y}}]
    Object.keys(window.PS || {}).forEach(function(k) {
      var objs = window.PS[k] && window.PS[k].objects;
      if (!objs || !objs.some(isInstance)) return;
      stash[k] = objs.slice();
      window.PS[k].objects = objs.filter(function(o) {
        if (!isInstance(o)) return true;
        dump.push({
          page: +k,
          masterId: o.masterId,
          offsetPt: {x: o.offsetPt.x, y: o.offsetPt.y}
        });
        return false;
      });
    });

    // 2. Temporarily wrap JSON.stringify to inject masters + instances.
    //    Guard: only mutates the actual doc object (app + version + !masters).
    var origStringify = JSON.stringify;
    JSON.stringify = function(value, replacer, indent) {
      if (value &&
          value.app === 'bma-plan-lite' &&
          value.version === 1 &&
          !value.masters) {
        value = Object.assign({}, value, {
          masters: window.MASTERS || {},
          instances: dump
        });
      }
      return origStringify.call(JSON, value, replacer, indent);
    };

    try {
      origHandler.call(btn, e);
    } finally {
      JSON.stringify = origStringify;
      // Restore stripped instance objects back into PS
      Object.keys(stash).forEach(function(k) {
        window.PS[k].objects = stash[k];
      });
    }
  };
}

/**
 * cfssWrapLoad()
 * Wraps window.loadProto to restore masters + instances after the standard
 * loadProto finishes. Handles:
 *   - Legacy files (no masters/instances keys): MASTERS = {}, no instances.
 *   - Forward-compat: unknown extra keys on master entries are carried through.
 *   - Counter resume: __cfss_nextMasterIdN set to max(existing N) + 1.
 */
function cfssWrapLoad() {
  if (typeof window.loadProto !== 'function' || window.loadProto.__cfssWrapped) return;
  var origLoad = window.loadProto;
  window.loadProto = function(doc) {
    origLoad(doc);

    // Reset MASTERS then restore from saved doc
    window.MASTERS = {};
    if (doc.masters && typeof doc.masters === 'object') {
      Object.keys(doc.masters).forEach(function(id) {
        var m = doc.masters[id];
        if (!m || !Array.isArray(m.metricPts)) return;
        var entry = {
          id: id,
          name: m.name || '',
          metricPts: m.metricPts.map(function(p) {
            return {x_m: Number(p.x_m), y_m: Number(p.y_m)};
          }),
          color: m.color || '#888',
          createdAt: m.createdAt || Date.now()
        };
        // Carry forward any extra additive fields (e.g. catId)
        Object.keys(m).forEach(function(k) {
          if (['id', 'name', 'metricPts', 'color', 'createdAt'].indexOf(k) === -1) {
            entry[k] = m[k];
          }
        });
        window.MASTERS[id] = entry;
      });
    }

    // Resume id counter to max(existing) + 1
    var maxN = 0;
    Object.keys(window.MASTERS).forEach(function(id) {
      var m = /^m(\d+)$/.exec(id);
      if (m) {
        var n = parseInt(m[1], 10);
        if (n > maxN) maxN = n;
      }
    });
    window.__cfss_nextMasterIdN = maxN + 1;

    // Re-inject instances into PS[pg].objects[]
    var insts = Array.isArray(doc.instances) ? doc.instances : [];
    insts.forEach(function(rec) {
      if (!rec || typeof rec.page !== 'number' || !rec.masterId) return;
      var pg = rec.page;
      if (!window.PS[pg]) return; // page not in PS — drop silently
      window.PS[pg].objects.push(
        makeInstance(rec.masterId, rec.offsetPt || {x: 0, y: 0})
      );
    });
  };
  window.loadProto.__cfssWrapped = true;
}

/* ================================================================== */
/* CFSS-3: UI — render, hit-test, context-menu, promote dialog        */
/* ================================================================== */

/* --- CSS for the promote dialog (injected once, scoped to #cfss-*) --- */
function _cfssInjectCSS() {
  if (document.getElementById('cfss-style')) return;
  var s = document.createElement('style');
  s.id = 'cfss-style';
  s.textContent = [
    '#cfss-overlay{position:fixed;inset:0;background:rgba(6,8,12,.72);z-index:310;',
    '  display:flex;align-items:center;justify-content:center;}',
    '#cfss-dlg{background:#161a22;border:1px solid #2a3140;border-radius:12px;',
    '  padding:18px 20px;width:360px;max-height:80vh;display:flex;flex-direction:column;',
    '  color:#e7ecf3;font-family:"Segoe UI",system-ui,sans-serif;font-size:13px;}',
    '#cfss-dlg h4{margin:0 0 8px;font-size:14px;color:#4c8dff;}',
    '#cfss-dlg .cfss-info{font-size:11px;color:#8b97a8;margin-bottom:10px;}',
    '#cfss-dlg .cfss-field{margin-bottom:10px;}',
    '#cfss-dlg .cfss-field label{display:block;color:#8b97a8;font-size:11px;margin-bottom:3px;}',
    '#cfss-dlg .cfss-field input{width:100%;background:#0c0f14;border:1px solid #2a3140;',
    '  color:#e7ecf3;border-radius:6px;padding:6px 9px;font-size:13px;}',
    '#cfss-pages{flex:1;overflow-y:auto;max-height:220px;margin-bottom:12px;',
    '  border:1px solid #2a3140;border-radius:6px;padding:6px;}',
    '#cfss-pages .cfss-pg-row{display:flex;align-items:center;gap:8px;',
    '  padding:5px 6px;border-radius:5px;font-size:12px;cursor:pointer;}',
    '#cfss-pages .cfss-pg-row:hover{background:#222a37;}',
    '#cfss-pages .cfss-pg-warn{font-size:11px;color:#ffb454;padding:4px 6px;}',
    '#cfss-dlg .cfss-btns{display:flex;gap:8px;justify-content:flex-end;}',
    '#cfss-dlg .cfss-btn{padding:6px 14px;border-radius:7px;border:1px solid #2a3140;',
    '  background:#222a37;color:#e7ecf3;cursor:pointer;font-size:12px;}',
    '#cfss-dlg .cfss-btn.pri{background:#4c8dff;border-color:#4c8dff;color:#fff;}',
    '#cfss-dlg .cfss-btn:hover{filter:brightness(1.15);}',
    '#cfss-dlg .cfss-row{display:flex;gap:8px;margin-bottom:8px;}',
    '#cfss-dlg .cfss-row > .cfss-field{flex:1;}',
    '#cfss-dlg .cfss-field input[type=color]{padding:2px;height:28px;cursor:pointer;}',
    '#cfss-dlg .cfss-field input:disabled{opacity:.4;cursor:not-allowed;}',
    '#cfss-dlg .cfss-hint{color:#8b97a8;font-size:11px;margin-top:-4px;margin-bottom:8px;}'
  ].join('\n');
  document.head.appendChild(s);
}

/* --- Render hook (second pass after original draw) --- */
function cfssRenderInstances() {
  var canvas = document.getElementById('cv');
  if (!canvas) return;
  var ctx2 = canvas.getContext('2d');
  if (!ctx2) return;
  var pg = window.curPage;
  if (!window.PS || !window.PS[pg]) return;
  var objs = window.PS[pg].objects;
  if (!objs || !objs.length) return;
  var scale = (window.PS[pg] && window.PS[pg].scale) ? window.PS[pg].scale : null;
  var ppm = scale && scale.pts_per_m > 0 ? scale.pts_per_m : null;

  for (var i = 0; i < objs.length; i++) {
    var inst = objs[i];
    if (!isInstance(inst)) continue;
    var master = masterById(inst.masterId);
    if (!master) continue; // orphaned but not yet frozen — skip
    var resolved = ppm ? resolveInstancePts(inst, ppm) : null;
    if (!resolved || !resolved.pts || resolved.pts.length < 2) continue;
    _cfssDrawInstance(ctx2, inst, master, resolved, ppm);
  }
}

function _cfssDrawInstance(ctx2, inst, master, resolved, ppm) {
  if (!window.ptToScreen) return;
  var pts = resolved.pts;
  var sel = (window.state && (window.state.sel === inst ||
             (window.state.selSet && window.state.selSet.indexOf(inst) >= 0)));
  var color = master.color || '#4c8dff';

  // Draw dashed outline
  var scr = pts.map(window.ptToScreen);
  ctx2.save();
  ctx2.setLineDash([6, 4]);
  ctx2.beginPath();
  ctx2.moveTo(scr[0].x, scr[0].y);
  for (var j = 1; j < scr.length; j++) ctx2.lineTo(scr[j].x, scr[j].y);
  ctx2.closePath();
  // semi-transparent fill
  var hex = color.replace('#','');
  var nr = parseInt(hex.slice(0,2),16)||0, ng = parseInt(hex.slice(2,4),16)||0, nb = parseInt(hex.slice(4,6),16)||0;
  ctx2.fillStyle = 'rgba('+nr+','+ng+','+nb+','+(sel?0.26:0.12)+')';
  ctx2.fill();
  ctx2.strokeStyle = color;
  ctx2.lineWidth = sel ? 2.5 : 1.5;
  ctx2.stroke();
  ctx2.setLineDash([]);
  ctx2.restore();

  // Label at bbox center
  cfssRenderInstanceLabel(ctx2, inst, master, resolved, ppm);
}

function cfssRenderInstanceLabel(ctx2, inst, master, resolved, ppm) {
  var area = instanceAreaM2(inst, ppm);
  var areaStr = area !== null ? area.toFixed(2) + ' m²' : '—';
  var txt = '📏 ' + (master.name || 'Master') + '  ' + areaStr;
  var bbox = resolved.bbox;
  var cx = bbox.x + bbox.w / 2, cy = bbox.y + bbox.h / 2;
  if (!window.ptToScreen) return;
  var cp = window.ptToScreen({x: cx, y: cy});
  ctx2.save();
  ctx2.font = '600 11px Segoe UI';
  ctx2.textAlign = 'center'; ctx2.textBaseline = 'middle';
  var w = ctx2.measureText(txt).width + 10, h = 17;
  // background pill
  ctx2.fillStyle = 'rgba(15,17,21,.85)';
  _cfssRR(ctx2, cp.x - w/2, cp.y - h/2, w, h, 4);
  ctx2.fill();
  ctx2.fillStyle = '#9cd4ff';
  ctx2.fillText(txt, cp.x, cp.y);
  ctx2.restore();
}

/* rounded-rect helper (mirrors rr() in ui-lite, used without accessing it) */
function _cfssRR(c, x, y, w, h, r) {
  c.beginPath(); c.moveTo(x+r,y); c.arcTo(x+w,y,x+w,y+h,r); c.arcTo(x+w,y+h,x,y+h,r);
  c.arcTo(x,y+h,x,y,r); c.arcTo(x,y,x+w,y,r); c.closePath();
}

/* --- Hit-test hook (second pass after original pick) --- */
function cfssPickInstance(sx, sy) {
  var pg = window.curPage;
  if (!window.PS || !window.PS[pg]) return null;
  var objs = window.PS[pg].objects;
  if (!objs) return null;
  var scale = window.PS[pg].scale;
  var ppm = scale && scale.pts_per_m > 0 ? scale.pts_per_m : null;
  if (!ppm) return null;
  if (!window.ptToScreen) return null;

  // iterate in reverse (top-most visually)
  for (var i = objs.length - 1; i >= 0; i--) {
    var inst = objs[i];
    if (!isInstance(inst)) continue;
    var master = masterById(inst.masterId);
    if (!master) continue;
    var resolved = resolveInstancePts(inst, ppm);
    if (!resolved) continue;
    var scrPts = resolved.pts.map(window.ptToScreen);
    if (_cfssInPoly(sx, sy, scrPts)) return inst;
  }
  return null;
}

function _cfssInPoly(x, y, poly) {
  var c = false;
  for (var i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    var xi = poly[i].x, yi = poly[i].y, xj = poly[j].x, yj = poly[j].y;
    if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) c = !c;
  }
  return c;
}

/* --- Wrap objectsInZOrder to filter instances out (CFSS-3) --- */
function cfssWrapZOrder() {
  if (typeof window.objectsInZOrder !== 'function' || window.objectsInZOrder.__cfssWrapped) return;
  var orig = window.objectsInZOrder;
  window.objectsInZOrder = function(objs) {
    var filtered = Array.isArray(objs) ? objs.filter(function(o) { return !isInstance(o); }) : objs;
    return orig.call(this, filtered);
  };
  window.objectsInZOrder.__cfssWrapped = true;
}

/* --- Wrap draw() to append instance render pass (CFSS-3) --- */
function cfssWrapDraw() {
  if (typeof window.draw !== 'function' || window.draw.__cfssWrapped) return;
  var origDraw = window.draw;
  window.draw = function() {
    origDraw.apply(this, arguments);
    try { cfssRenderInstances(); } catch(e) { /* fail-safe */ }
  };
  window.draw.__cfssWrapped = true;
}

/* --- Wrap pick() to fall back to instance hit-test (CFSS-3) --- */
function cfssWrapPick() {
  if (typeof window.pick !== 'function' || window.pick.__cfssWrapped) return;
  var origPick = window.pick;
  window.pick = function(sx, sy) {
    var result = origPick.apply(this, arguments);
    if (result !== null && result !== undefined) return result;
    return cfssPickInstance(sx, sy);
  };
  window.pick.__cfssWrapped = true;
}

/* --- Wrap showObjMenu() to append CFSS rows (CFSS-3) --- */
function cfssWrapShowObjMenu() {
  if (typeof window.showObjMenu !== 'function' || window.showObjMenu.__cfssWrapped) return;
  var origShowObjMenu = window.showObjMenu;
  window.showObjMenu = function(cx, cy, obj) {
    origShowObjMenu.apply(this, arguments);
    // Append extra rows to the menu element after original builds it
    cfssExtendObjMenu(obj);
  };
  window.showObjMenu.__cfssWrapped = true;
}

/* --- Context-menu extension --- */
function cfssExtendObjMenu(obj) {
  // Find the most recently added objmenu
  var menus = document.querySelectorAll('.objmenu');
  if (!menus.length) return;
  var m = menus[menus.length - 1];

  if (isInstance(obj)) {
    var master = masterById(obj.masterId);
    if (master) {
      // Edit row (before delete row)
      var rEdit = document.createElement('div');
      rEdit.className = 'objmenu-row';
      rEdit.textContent = '✏️ แก้ไขมาสเตอร์';
      rEdit.style.color = '#9cd4ff';
      rEdit.addEventListener('click', function(e) {
        e.stopPropagation();
        if (typeof window.closeObjMenu === 'function') window.closeObjMenu();
        cfssOpenEditDialog(obj.masterId);
      });
      m.appendChild(rEdit);
    }
    // Instance: offer delete-master
    var r = document.createElement('div');
    r.className = 'objmenu-row';
    r.textContent = '📏 ลบมาสเตอร์ (instance ทุกหน้าเป็นอิสระ)';
    r.style.color = '#ff6b6b';
    r.addEventListener('click', function(e) {
      e.stopPropagation();
      // close menu
      if (typeof window.closeObjMenu === 'function') window.closeObjMenu();
      cfssDeleteMaster(obj.masterId);
    });
    m.appendChild(r);
  } else if (obj && obj.kind === 'poly' && Array.isArray(obj.pts) && obj.pts.length >= 3 && !obj.orphan) {
    // Non-counting polygon: offer promote
    var r2 = document.createElement('div');
    r2.className = 'objmenu-row';
    r2.textContent = '📏 ทำเป็นต้นแบบข้ามชั้น'; // ทำเป็นต้นแบบข้ามชั้น
    r2.style.color = '#00aaff';
    r2.addEventListener('click', function(e) {
      e.stopPropagation();
      if (typeof window.closeObjMenu === 'function') window.closeObjMenu();
      cfssOpenPromoteDialog(obj);
    });
    m.appendChild(r2);
  }
}

/* --- Delete master --- */
function cfssDeleteMaster(masterId) {
  if (!window.confirm('ลบมาสเตอร์? Instances ทุกหน้าจะกลายเป็น polygon แยกอิสระ')) return;
  // Build allPages array for freeze
  var allPages = [];
  Object.keys(window.PS || {}).forEach(function(k) {
    var pg = window.PS[k];
    var sc = pg && pg.scale;
    var ppm = sc && sc.pts_per_m > 0 ? sc.pts_per_m : 1;
    allPages.push({page: pg, ppm: ppm});
  });
  freezeOrphansForMaster(masterId, allPages);
  removeMaster(masterId);
  if (window.state) window.state.dirty = true;
  if (typeof window.draw === 'function') window.draw();
}

/* ================================================================== */
/* CFSS-4: Edit master                                                */
/* ================================================================== */

/* _cfssIsRect — true iff 4 pts form an axis-aligned rect (tol 1e-6) */
function _cfssIsRect(mp) {
  if (!Array.isArray(mp) || mp.length !== 4) return false;
  var xs = [], ys = [], tol = 1e-6;
  for (var i = 0; i < 4; i++) {
    if (typeof mp[i].x_m !== 'number' || typeof mp[i].y_m !== 'number') return false;
    xs.push(mp[i].x_m); ys.push(mp[i].y_m);
  }
  xs.sort(function(a,b){return a-b;}); ys.sort(function(a,b){return a-b;});
  return Math.abs(xs[0]-xs[1]) <= tol && Math.abs(xs[2]-xs[3]) <= tol &&
         Math.abs(xs[1]-xs[2]) > tol &&
         Math.abs(ys[0]-ys[1]) <= tol && Math.abs(ys[2]-ys[3]) <= tol &&
         Math.abs(ys[1]-ys[2]) > tol;
}
window._cfssIsRect = _cfssIsRect;

/* cfssCommitEdit(masterId, patch={name?,color?,widthM?,heightM?})
   Routes through updateMaster. Returns updated master or null. */
function cfssCommitEdit(masterId, patch) {
  var master = masterById(masterId);
  if (!master) return null;
  if (!patch || typeof patch !== 'object') return master;
  var computed = {};
  if (typeof patch.name === 'string') computed.name = patch.name;
  if (typeof patch.color === 'string') computed.color = patch.color;
  if (typeof patch.widthM === 'number' && typeof patch.heightM === 'number' &&
      patch.widthM > 0 && patch.heightM > 0 && _cfssIsRect(master.metricPts)) {
    computed.metricPts = [{x_m:0,y_m:0},{x_m:patch.widthM,y_m:0},
                          {x_m:patch.widthM,y_m:patch.heightM},{x_m:0,y_m:patch.heightM}];
  }
  var updated = updateMaster(masterId, computed);
  if (updated && window.state) window.state.dirty = true;
  return updated;
}
window.cfssCommitEdit = cfssCommitEdit;
window.__cfssTestEdit = cfssCommitEdit;

/* --- Edit dialog --- */
var _cfssEditDlgEl = null;

function cfssOpenEditDialog(masterId) {
  _cfssInjectCSS();
  if (_cfssEditDlgEl) { _cfssEditDlgEl.remove(); _cfssEditDlgEl = null; }
  var master = masterById(masterId);
  if (!master) return;

  var isRect = _cfssIsRect(master.metricPts);
  // Compute bbox W/H from metricPts
  var wxMin = Infinity, wxMax = -Infinity, wyMin = Infinity, wyMax = -Infinity;
  (master.metricPts || []).forEach(function(p) {
    if (p.x_m < wxMin) wxMin = p.x_m; if (p.x_m > wxMax) wxMax = p.x_m;
    if (p.y_m < wyMin) wyMin = p.y_m; if (p.y_m > wyMax) wyMax = p.y_m;
  });
  var wM = isRect ? (wxMax - wxMin).toFixed(3) : '';
  var hM = isRect ? (wyMax - wyMin).toFixed(3) : '';

  var overlay = document.createElement('div');
  overlay.id = 'cfss-overlay';
  var dlg = document.createElement('div');
  dlg.id = 'cfss-dlg';

  var dimHint = isRect ? '' : '<div class="cfss-hint">ไม่ใช่สี่เหลี่ยมแกนตรง — ขนาด W/H ไม่สามารถแก้ได้</div>';
  dlg.innerHTML = [
    '<h4>✏️ แก้ไขมาสเตอร์</h4>',
    '<div class="cfss-field"><label>ชื่อ</label>',
    '<input id="cfss-edit-name" type="text" value="' + (master.name || '').replace(/"/g, '&quot;') + '"></div>',
    '<div class="cfss-field"><label>สี</label>',
    '<input id="cfss-edit-color" type="color" value="' + (master.color || '#888888') + '"></div>',
    '<div class="cfss-row">',
    '<div class="cfss-field"><label>กว้าง (m)</label>',
    '<input id="cfss-edit-w" type="number" step="0.001" min="0.001"' + (!isRect ? ' disabled' : '') + ' value="' + wM + '"></div>',
    '<div class="cfss-field"><label>สูง (m)</label>',
    '<input id="cfss-edit-h" type="number" step="0.001" min="0.001"' + (!isRect ? ' disabled' : '') + ' value="' + hM + '"></div>',
    '</div>',
    dimHint,
    '<div class="cfss-btns">',
    '<button class="cfss-btn" id="cfss-edit-cancel">ยกเลิก</button>',
    '<button class="cfss-btn pri" id="cfss-edit-save">บันทึก</button>',
    '</div>'
  ].join('');

  overlay.appendChild(dlg);
  document.body.appendChild(overlay);
  _cfssEditDlgEl = overlay;

  function closeEdit() { overlay.remove(); _cfssEditDlgEl = null; }

  dlg.querySelector('#cfss-edit-cancel').addEventListener('click', closeEdit);
  overlay.addEventListener('click', function(e) { if (e.target === overlay) closeEdit(); });
  document.addEventListener('keydown', function esc(e) {
    if (e.key === 'Escape') { closeEdit(); document.removeEventListener('keydown', esc); }
  });

  dlg.querySelector('#cfss-edit-save').addEventListener('click', function() {
    var patch = {};
    var nameVal = (dlg.querySelector('#cfss-edit-name').value || '').trim();
    if (nameVal) patch.name = nameVal;
    patch.color = dlg.querySelector('#cfss-edit-color').value;
    if (isRect) {
      var wv = parseFloat(dlg.querySelector('#cfss-edit-w').value);
      var hv = parseFloat(dlg.querySelector('#cfss-edit-h').value);
      if (wv > 0 && hv > 0) { patch.widthM = wv; patch.heightM = hv; }
    }
    cfssCommitEdit(masterId, patch);
    closeEdit();
    if (typeof window.draw === 'function') window.draw();
  });
}
window.cfssOpenEditDialog = cfssOpenEditDialog;

/* --- Promote: internal commit logic (testability hook) --- */
function cfssCommitPromote(sourcePoly, name, targetPageNumbers) {
  if (!sourcePoly || !Array.isArray(sourcePoly.pts) || sourcePoly.pts.length < 3) return null;

  // Find which page contains sourcePoly
  var srcPg = null;
  var srcIdx = -1;
  var pgKeys = Object.keys(window.PS || {});
  for (var ki = 0; ki < pgKeys.length; ki++) {
    var k = pgKeys[ki];
    var objs = window.PS[k] && window.PS[k].objects;
    if (!objs) continue;
    var idx = objs.indexOf(sourcePoly);
    if (idx >= 0) { srcPg = +k; srcIdx = idx; break; }
  }
  if (srcPg === null || srcIdx < 0) return null;

  var srcScale = window.PS[srcPg] && window.PS[srcPg].scale;
  var ppm = srcScale && srcScale.pts_per_m > 0 ? srcScale.pts_per_m : null;
  if (!ppm) return null;

  // Compute bbox in pt-space of sourcePoly.pts
  var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  sourcePoly.pts.forEach(function(p) {
    if (p.x < minX) minX = p.x;
    if (p.y < minY) minY = p.y;
    if (p.x > maxX) maxX = p.x;
    if (p.y > maxY) maxY = p.y;
  });

  // metricPts: 0-anchored in metric space
  var metricPts = sourcePoly.pts.map(function(p) {
    return {x_m: (p.x - minX) / ppm, y_m: (p.y - minY) / ppm};
  });

  var masterId = addMaster(name || 'Master', metricPts, sourcePoly.color || '#888');
  if (!masterId) return null;

  // Replace source poly with instance (offset = bbox min in pt-space)
  var srcInstance = makeInstance(masterId, {x: minX, y: minY});
  window.PS[srcPg].objects[srcIdx] = srcInstance;

  // Place on target pages
  if (Array.isArray(targetPageNumbers)) {
    targetPageNumbers.forEach(function(tgtPg) {
      tgtPg = +tgtPg;
      if (tgtPg === srcPg) return;
      if (!window.PS[tgtPg]) return;
      window.PS[tgtPg].objects.push(makeInstance(masterId, {x: minX, y: minY}));
    });
  }

  if (window.state) window.state.dirty = true;
  return masterId;
}

/* Testability hook — called by tests directly, also by dialog UI */
window.__cfssTestPromote = cfssCommitPromote;

/* --- Promote dialog --- */
var _cfssDlgEl = null;

function cfssOpenPromoteDialog(sourcePoly) {
  _cfssInjectCSS();
  // Close any previous dialog
  if (_cfssDlgEl) { _cfssDlgEl.remove(); _cfssDlgEl = null; }

  // Find source page and ppm
  var srcPg = null;
  var pgKeys = Object.keys(window.PS || {});
  for (var ki = 0; ki < pgKeys.length; ki++) {
    var k = pgKeys[ki];
    var objs = window.PS[k] && window.PS[k].objects;
    if (objs && objs.indexOf(sourcePoly) >= 0) { srcPg = +k; break; }
  }
  var srcScale = srcPg && window.PS[srcPg] && window.PS[srcPg].scale;
  var ppm = srcScale && srcScale.pts_per_m > 0 ? srcScale.pts_per_m : null;

  // Compute bbox for info display
  var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  (sourcePoly.pts || []).forEach(function(p) {
    if (p.x < minX) minX = p.x; if (p.y < minY) minY = p.y;
    if (p.x > maxX) maxX = p.x; if (p.y > maxY) maxY = p.y;
  });
  var wM = ppm ? ((maxX - minX) / ppm).toFixed(2) : '—';
  var hM = ppm ? ((maxY - minY) / ppm).toFixed(2) : '—';
  var aM = ppm ? instanceAreaM2(
    makeInstance('__tmp__', {x: minX, y: minY}),
    ppm
  ) : null;
  // Use a quick shoelace on source pts directly (master not created yet)
  if (ppm) {
    var n = sourcePoly.pts.length, a2 = 0;
    for (var ii = 0; ii < n; ii++) {
      var jj = (ii + 1) % n;
      a2 += (sourcePoly.pts[ii].x / ppm) * (sourcePoly.pts[jj].y / ppm)
           - (sourcePoly.pts[jj].x / ppm) * (sourcePoly.pts[ii].y / ppm);
    }
    aM = (Math.abs(a2) / 2).toFixed(2);
  }

  var defaultName = sourcePoly.name || ('Master ' + (window.__cfss_nextMasterIdN || 1));

  var overlay = document.createElement('div');
  overlay.id = 'cfss-overlay';
  var dlg = document.createElement('div');
  dlg.id = 'cfss-dlg';

  dlg.innerHTML = [
    '<h4>📏 ทำเป็นต้นแบบข้ามชั้น — เลือกหน้าที่จะติด</h4>',
    '<div class="cfss-info">',
    (ppm
      ? (wM + ' m × ' + hM + ' m = ' + aM + ' m²')
      : '<span style="color:#ffb454">⚠ ยังไม่ได้ตั้งสเกลหน้านี้</span>'),
    '</div>',
    '<div class="cfss-field"><label>ชื่อ (ชื่อมาสเตอร์)</label>',
    '<input id="cfss-name-inp" type="text" value="' + defaultName.replace(/"/g,'&quot;') + '"></div>',
    '<div id="cfss-pages"></div>',
    '<div class="cfss-btns">',
    '<button class="cfss-btn" id="cfss-cancel">ยกเลิก</button>',
    '<button class="cfss-btn pri" id="cfss-install">ติดตั้ง</button>',
    '</div>'
  ].join('');

  // Build page list
  var pagesDiv = dlg.querySelector('#cfss-pages');
  var totalPages = window.pageCount || 1;
  var hasNoScalePage = false;
  for (var pg = 1; pg <= totalPages; pg++) {
    if (pg === srcPg) continue;
    var pgScale = window.PS[pg] && window.PS[pg].scale;
    var pgPpm = pgScale && pgScale.pts_per_m > 0;
    var label = 'หน้า ' + pg; // หน้า N
    // Add floor label if available
    var tg = window.pageTags && window.pageTags[pg];
    if (tg === 'floor') {
      var fk = window.pageFloorKind && window.pageFloorKind[pg];
      var fnum = window.pageFloorNum && window.pageFloorNum[pg];
      var fLabel = window.FLOOR_KIND_LABELS && fk && window.FLOOR_KIND_LABELS[fk]
                   ? window.FLOOR_KIND_LABELS[fk] : '';
      if (fLabel) label += ' — ' + fLabel + (fnum ? (' ' + fnum) : '') + (fk !== 'custom' ? '' : '');
    }
    var row = document.createElement('div');
    row.className = 'cfss-pg-row';
    if (!pgPpm) {
      row.innerHTML = '<span style="color:#ffb454">⚠ หน้า ' + pg + ' — ยังไม่มีสเกล</span>';
      row.title = 'ตั้งสเกลหน้านี้ก่อนจึงจะติดได้';
      hasNoScalePage = true;
    } else {
      var cb = document.createElement('input');
      cb.type = 'checkbox'; cb.value = pg; cb.id = 'cfss-pg-' + pg;
      var lbl = document.createElement('label');
      lbl.htmlFor = 'cfss-pg-' + pg; lbl.textContent = label; lbl.style.cursor = 'pointer';
      row.appendChild(cb); row.appendChild(lbl);
      row.addEventListener('click', function(ev) {
        if (ev.target.tagName !== 'INPUT') {
          var inp = row.querySelector('input[type=checkbox]');
          if (inp) inp.checked = !inp.checked;
        }
      });
    }
    pagesDiv.appendChild(row);
  }
  if (hasNoScalePage) {
    var warn = document.createElement('div');
    warn.className = 'cfss-pg-warn';
    warn.textContent = '⚠ หน้าที่ไม่มีสเกลจะไม่ถูกเลือก';
    pagesDiv.appendChild(warn);
  }

  overlay.appendChild(dlg);
  document.body.appendChild(overlay);
  _cfssDlgEl = overlay;

  dlg.querySelector('#cfss-cancel').addEventListener('click', function() {
    overlay.remove(); _cfssDlgEl = null;
  });
  overlay.addEventListener('click', function(e) {
    if (e.target === overlay) { overlay.remove(); _cfssDlgEl = null; }
  });

  dlg.querySelector('#cfss-install').addEventListener('click', function() {
    var nameVal = (dlg.querySelector('#cfss-name-inp').value || '').trim() || 'Master';
    var targetPgs = [];
    pagesDiv.querySelectorAll('input[type=checkbox]:checked').forEach(function(cb) {
      targetPgs.push(+cb.value);
    });
    cfssCommitPromote(sourcePoly, nameVal, targetPgs);
    overlay.remove(); _cfssDlgEl = null;
    if (typeof window.draw === 'function') window.draw();
  });
}

/**
 * cfssBootstrap()
 * Called once at DOMContentLoaded (or immediately if DOM already ready).
 * Installs all wrappers. Each has its own idempotent guard.
 */
function cfssBootstrap() {
  cfssWrapSave();
  cfssWrapLoad();
  cfssWrapZOrder();
  cfssWrapDraw();
  cfssWrapPick();
  cfssWrapShowObjMenu();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', cfssBootstrap);
} else {
  cfssBootstrap();
}

/* end of idempotent guard */ }
