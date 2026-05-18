import sys

with open("proto/ui.html", "r", encoding="utf-8") as f:
    content = f.read()

replacements = [
    # Redraw
    ("ds=[8/zoom,4/zoom];mLines.forEach(s=>{", "ds=[8/zoom,4/zoom];if(layerState.lines.visible)mLines.forEach(s=>{"),
    ("drawRefLines();", "if(layerState.refs.visible)drawRefLines();"),
    ("drawParking();mPolys.forEach(poly=>{", "drawParking();if(layerState.polys.visible)mPolys.forEach(poly=>{"),
    ("});mOpenings.forEach(op=>{", "});if(layerState.openings.visible)mOpenings.forEach(op=>{"),
    
    # hitVertex
    ("let hit=scanPts(\"ref\",mRefs);", "let hit=layerState.refs.visible&&!layerState.refs.locked?scanPts(\"ref\",mRefs):null;"),
    ("hit=scanPts(\"line\",mLines);", "if(!hit&&layerState.lines.visible&&!layerState.lines.locked)hit=scanPts(\"line\",mLines);"),
    ("return scanPoly(\"opening\",mOpenings)||scanPoly(\"poly\",mPolys);", "return (layerState.openings.visible&&!layerState.openings.locked?scanPoly(\"opening\",mOpenings):null)||(layerState.polys.visible&&!layerState.polys.locked?scanPoly(\"poly\",mPolys):null);"),

    # hitTest
    ("for(let i=mRefs.length-1", "if(layerState.refs.visible&&!layerState.refs.locked)for(let i=mRefs.length-1"),
    ("for(let i=mOpenings.length-1", "if(layerState.openings.visible&&!layerState.openings.locked)for(let i=mOpenings.length-1"),
    ("for(let i=mPolys.length-1", "if(layerState.polys.visible&&!layerState.polys.locked)for(let i=mPolys.length-1"),
    ("for(let i=mLines.length-1", "if(layerState.lines.visible&&!layerState.lines.locked)for(let i=mLines.length-1")
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f"Patched: {old[:20]}...")
    else:
        print(f"NOT FOUND: {old[:20]}...")

with open("proto/ui.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Done patching ui.html")
