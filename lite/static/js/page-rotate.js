/* page-rotate.js — LROTATE-1
   Render-rotation per page. pageRot[n] is persisted in .bmaplan as pageRotations.
   getRot(pg) is NOT changed — coordinate math stays in rot-0 PDF space.
   The rendered raster is fetched with ?rot=N so the server pre-rotates the JPEG.
*/
function rotatePage(delta){
  if(!pageCount||!curPage)return;
  pageRot=pageRot||{};
  var cur=(pageRot[curPage]||0)+delta;
  while(cur<0)cur+=360;
  while(cur>=360)cur-=360;
  pageRot[curPage]=cur;
  state.dirty=true;
  // Invalidate PDF.js page proxy so next loadPage re-fetches with new rotation
  if (typeof pageCache !== "undefined") delete pageCache[curPage];
  loadPage(curPage);
}
