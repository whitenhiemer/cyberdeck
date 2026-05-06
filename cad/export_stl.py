"""
Run under FreeCADCmd to generate all panel FCStd files and export STL for rendering.
Usage: FreeCADCmd export_stl.py
"""
import FreeCAD as App
import Part
import os
import sys
import math

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
STL_DIR = os.path.join(SCRIPTS_DIR, "stl")
os.makedirs(STL_DIR, exist_ok=True)

PANELS = [
    "panel_a", "panel_b",
    "panel_c", "panel_d",
    "panel_e", "panel_f",
    "rear_wall",
]

for panel in PANELS:
    script = os.path.join(SCRIPTS_DIR, f"{panel}.py")
    ns = {"__file__": script}
    exec(open(script).read(), ns)
    doc = ns.get("doc") or App.ActiveDocument
    # find the first Part::Feature shape
    for o in doc.Objects:
        if hasattr(o, "Shape"):
            stl_path = os.path.join(STL_DIR, f"{panel}.stl")
            o.Shape.exportStl(stl_path)
            print(f"Exported {panel}.stl")
            break
    App.closeDocument(doc.Name)

print("All STLs written to", STL_DIR)
