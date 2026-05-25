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

/* end of idempotent guard */ }
