"""
apply_chamfers.py — post-processing pass for all chassis panels.

Applies a 1.5mm chamfer to every user-visible outer corner edge.
Seam faces (where panels mate with each other or the rear wall) are left sharp.

Rules per panel:
  - Chamfer only edges whose midpoint lies on y=YMin (front face) OR
    the outer side x-face of that panel.
  - Always skip: y=YMax (rear wall seam), seam-x face (left/right panel seam),
    and any z-face that mates with an adjacent row.

Run with:  FreeCADCmd apply_chamfers.py
"""
import FreeCAD as App
import Part
import os

CAD_DIR = os.path.dirname(os.path.abspath(__file__))
CHAMFER  = 1.5   # mm — outer corner chamfer size

# (script, doc_name, seam_x_is_max, skip_zmin, skip_zmax)
#   seam_x_is_max: True  → seam face is at x=XMax (panels A, C, E — left half)
#                  False → seam face is at x=XMin (panels B, D, F — right half)
#   skip_zmin: True → z=ZMin face is a row-seam (panel sits above another row)
#   skip_zmax: True → z=ZMax face is a row-seam (panel sits below another row)
PANEL_CONFIGS = [
    ("panel_a.py", "panel_a", True,  True,  False),  # AB row, left — top exposed
    ("panel_b.py", "panel_b", False, True,  False),  # AB row, right
    ("panel_c.py", "panel_c", True,  True,  True),   # CD row, left — both z seams
    ("panel_d.py", "panel_d", False, True,  True),   # CD row, right
    ("panel_e.py", "panel_e", True,  False, True),   # EF row, left — bottom exposed
    ("panel_f.py", "panel_f", False, False, True),   # EF row, right
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
    """
    Return outer straight edges suitable for chamfering.
    Only edges on the front face (y=YMin) or the outer side (non-seam x-face).
    """
    bb     = shape.BoundBox
    seam_x = 'xmax' if seam_x_is_max  else 'xmin'
    outer_x = 'xmin' if seam_x_is_max else 'xmax'

    result = []
    for edge in shape.Edges:
        if type(edge.Curve).__name__ != 'Line':
            continue
        if len(edge.Vertexes) < 2:
            continue

        mid = edge.CenterOfMass
        pl  = planes_of(mid, bb, tol)

        if len(pl) < 2:          continue   # not a corner edge
        if 'ymax' in pl:         continue   # rear-wall seam
        if seam_x in pl:         continue   # left/right panel seam
        if skip_zmin and 'zmin' in pl: continue   # row seam below
        if skip_zmax and 'zmax' in pl: continue   # row seam above

        # Only edges that touch front face or the outer side face
        if 'ymin' not in pl and outer_x not in pl:
            continue

        result.append(edge)
    return result

def apply_chamfer_to_shape(shape, edges, size):
    """Try bulk chamfer, fall back to individual edges on failure."""
    try:
        return shape.makeChamfer(size, edges), len(edges)
    except Exception as bulk_err:
        result  = shape
        applied = 0
        for e in edges:
            try:
                result   = result.makeChamfer(size, [e])
                applied += 1
            except Exception:
                pass
        return result, applied

# ── main ───────────────────────────────────────────────────────────────────
for script_name, doc_name, seam_x_is_max, skip_zmin, skip_zmax in PANEL_CONFIGS:
    print(f"\n── {script_name} ──")
    script_path = os.path.join(CAD_DIR, script_name)

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

    chamfered, n_applied = apply_chamfer_to_shape(shape, edges, CHAMFER)
    print(f"  {n_applied}/{len(edges)} chamfers applied ({CHAMFER}mm)")

    # Save as _chamfered variant
    out_doc  = App.newDocument(f"{doc_name}_ch")
    feat     = out_doc.addObject("Part::Feature", doc_name.title().replace("_", ""))
    feat.Shape = chamfered
    out_doc.recompute()

    save_path = os.path.join(CAD_DIR, f"{doc_name}_chamfered.FCStd")
    out_doc.saveAs(save_path)
    print(f"  saved → {save_path}")

    App.closeDocument(doc.Name)
    App.closeDocument(out_doc.Name)

print("\n✓  All panels chamfered.")
