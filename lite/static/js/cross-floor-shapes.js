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

/**
 * cfssBootstrap()
 * Called once at DOMContentLoaded (or immediately if DOM already ready).
 * Installs both wrappers. cfssWrapSave has its own guard in case onclick
 * is not yet bound when this runs — should not happen since page-folder-layers.js
 * loads synchronously, but the guard makes it safe.
 */
function cfssBootstrap() {
  cfssWrapSave();
  cfssWrapLoad();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', cfssBootstrap);
} else {
  cfssBootstrap();
}

/* end of idempotent guard */ }
