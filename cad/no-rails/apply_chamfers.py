"""
apply_chamfers.py (no-rails) — chamfer pass for panels A and B only.

Same rules as the main apply_chamfers.py; panels C-F are unchanged
and should be chamfered via the main script.

Run:  FreeCADCmd cad/no-rails/apply_chamfers.py
"""
import FreeCAD as App
import Part
import os, sys

NR_DIR  = os.path.dirname(os.path.abspath(__file__))
CHAMFER = 1.5

PANEL_CONFIGS = [
    ("panel_a.py", "panel_a_nr", True,  True,  False),  # AB left, top exposed
    ("panel_b.py", "panel_b_nr", False, True,  False),  # AB right
]

def planes_of(p, bb, tol=0.5):
    pl = set()
    if abs(p.x - bb.XMin) < tol: pl.add('xmin')
    if abs(p.x - bb.XMax) < tol: pl.add('xmax')
    if abs(p.y - bb.YMin) < tol: pl.add('ymin')
    if abs(p.y - bb.YMax) < tol: pl.add('ymax')
    if abs(p.z - bb.ZMin) < tol: pl.add('zmin')
    if abs(p.z - bb.ZMax) < tol: pl.add('zmax')
    return pl

def chamfer_candidates(shape, seam_x_is_max, skip_zmin, skip_zmax, tol=0.5):
    bb      = shape.BoundBox
    seam_x  = 'xmax' if seam_x_is_max else 'xmin'
    outer_x = 'xmin' if seam_x_is_max else 'xmax'
    result  = []
    for edge in shape.Edges:
        if type(edge.Curve).__name__ != 'Line': continue
        if len(edge.Vertexes) < 2:              continue
        mid = edge.CenterOfMass
        pl  = planes_of(mid, bb, tol)
        if len(pl) < 2:                              continue
        if 'ymax' in pl:                             continue
        if seam_x in pl:                             continue
        if skip_zmin and 'zmin' in pl:               continue
        if skip_zmax and 'zmax' in pl:               continue
        if 'ymin' not in pl and outer_x not in pl:   continue
        result.append(edge)
    return result

def apply_chamfer_to_shape(shape, edges, size):
    try:
        return shape.makeChamfer(size, edges), len(edges)
    except Exception:
        result, applied = shape, 0
        for e in edges:
            try:
                result   = result.makeChamfer(size, [e])
                applied += 1
            except Exception:
                pass
        return result, applied

for script_name, doc_name, seam_x_is_max, skip_zmin, skip_zmax in PANEL_CONFIGS:
    print(f"\n── {script_name} (no-rails) ──")
    script_path = os.path.join(NR_DIR, script_name)
    ns = {"__file__": script_path}
    exec(open(script_path).read(), ns)
    doc = ns.get("doc") or App.ActiveDocument

    shape = next((o.Shape for o in doc.Objects if hasattr(o, "Shape")), None)
    if shape is None:
        print("  no shape found — skipped")
        App.closeDocument(doc.Name)
        continue

    edges = chamfer_candidates(shape, seam_x_is_max, skip_zmin, skip_zmax)
    print(f"  {len(edges)} chamfer edges identified")

    chamfered, n = apply_chamfer_to_shape(shape, edges, CHAMFER)
    print(f"  {n}/{len(edges)} chamfers applied ({CHAMFER}mm)")

    out_doc  = App.newDocument(f"{doc_name}_ch")
    feat     = out_doc.addObject("Part::Feature", doc_name.title().replace("_", ""))
    feat.Shape = chamfered
    out_doc.recompute()

    save_path = os.path.join(NR_DIR, f"{doc_name}_chamfered.FCStd")
    out_doc.saveAs(save_path)
    print(f"  saved → {save_path}")

    App.closeDocument(doc.Name)
    App.closeDocument(out_doc.Name)

print("\n✓  No-rails panels A/B chamfered.")
