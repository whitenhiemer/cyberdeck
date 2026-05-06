import FreeCAD as App
import Part

# Angle bracket clips — horizontal seam connections (AB-CD and CD-EF)
# Simple rectangular plate, 20x4mm cross-section, two M3 clearance holes.
# Mounts to chassis front face (y=0); bolts into heat inserts in panel front faces.
# Print 2 of each size (one left, one right per seam).
#
# Bolt center positions (chassis Z):
#   AB-CD: upper=126mm (Panel A/B, z=50mm local), lower=58mm (Panel C/D, z=18mm local)
#   CD-EF: upper=58mm  (Panel C/D, z=18mm local), lower=20mm (Panel E/F, z=20mm local)
# Panel C/D front face insert at z=18mm serves both brackets (shared position).

BRACKET_W  = 20.0   # width (X)
BRACKET_T  = 4.0    # thickness (Y) — presses against panel front face
BOLT_D     = 3.2    # M3 clearance hole diameter
MARGIN     = 4.0    # mm from bolt hole center to bracket end

# --- Generate both sizes ---
BRACKETS = [
    {"name": "bracket_ab_cd", "span": 68.0, "seam": "AB-CD (chassis z=58–126mm)"},
    {"name": "bracket_cd_ef", "span": 38.0, "seam": "CD-EF (chassis z=20–58mm)"},
]

for br in BRACKETS:
    BRACKET_H = br["span"] + 2 * MARGIN

    doc = App.newDocument(br["name"])

    base = Part.makeBox(BRACKET_W, BRACKET_T, BRACKET_H)

    # Lower bolt hole — MARGIN from bottom
    lower_hole = Part.makeCylinder(
        BOLT_D / 2, BRACKET_T,
        App.Vector(BRACKET_W / 2, 0, MARGIN),
        App.Vector(0, 1, 0)
    )
    bracket = base.cut(lower_hole)

    # Upper bolt hole — MARGIN from top
    upper_hole = Part.makeCylinder(
        BOLT_D / 2, BRACKET_T,
        App.Vector(BRACKET_W / 2, 0, BRACKET_H - MARGIN),
        App.Vector(0, 1, 0)
    )
    bracket = bracket.cut(upper_hole)

    obj = doc.addObject("Part::Feature", br["name"])
    obj.Shape = bracket
    doc.recompute()

    save_path = f"/home/bwoodwar/Projects/cyberdeck/cad/{br['name']}.FCStd"
    doc.saveAs(save_path)
    print(f"{br['name']} saved to {save_path}")
    print(f"  Seam: {br['seam']}")
    print(f"  Outer: {BRACKET_W} x {BRACKET_T} x {BRACKET_H} mm")
    print(f"  Bolt holes at z={MARGIN:.0f}mm (lower) and z={BRACKET_H - MARGIN:.0f}mm (upper)")
    print(f"  Print 2x — one per side of chassis")
    print()
