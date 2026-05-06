import FreeCAD as App
import Part
import math

# Rail extension guides — left and right
# Separate printed pieces that press-fit into the bottom of the AB panel row
# controller pockets (chassis z=76mm). Extend the Go's side rail guide by ~8mm
# downward to aid controller re-attachment while the Go is seated in the cradle.
# The controller slides ~3-5mm in -Z (relative to Go body) to disengage; user
# lifts the Go clear for full removal. These guides only need to assist alignment
# on the way back in.
#
# NOTE: GROOVE_W and GROOVE_D are placeholders — measure actual Go side rail
# profile with calipers before printing.

# Must match panel_a.py / panel_b.py constants
CHASSIS_W    = 305.0
GO_W         = 210.0
CLEARANCE    = 1.0
CTRL_OUTER_WALL = 3.0
CTRL_T       = 42.25

go_cav_x = (CHASSIS_W - (GO_W + 2 * CLEARANCE)) / 2.0   # 46.5mm
ctrl_pocket_w = go_cav_x - CTRL_OUTER_WALL               # 43.5mm

# Guide block dimensions
EXT_W   = ctrl_pocket_w - 0.2   # 43.3mm — slight clearance for press-fit in pocket
EXT_D   = 25.0                  # Y: guide depth (front portion of pocket)
EXT_H   = 8.0                   # Z: extension below AB panel face (below chassis z=76mm)
TAB_H   = 4.0                   # Z: retention tab that sits inside the pocket
WALL_T  = 3.0                   # wall thickness on outer face

# Go side-rail groove on inner face (profile TBD — needs calipers)
GROOVE_W  = 4.0    # Z height of groove
GROOVE_D  = 1.5    # X depth into inner face
# Groove centered vertically in the extension
groove_z = (EXT_H - GROOVE_W) / 2.0   # 2.0mm from bottom of extension

# Chamfer angle for entry funnel (45°, 2mm)
CHAMFER = 2.0

SIDES = [
    # name, inner_face_x (where Go's side face meets the pocket)
    ("rail_ext_left",  EXT_W),    # inner face at +X, groove cuts in from +X face
    ("rail_ext_right", 0.0),      # inner face at x=0, groove cuts in from -X face (mirrored)
]

for name, inner_x in SIDES:
    doc = App.newDocument(name)

    total_h = EXT_H + TAB_H

    # Main body: full cross-section block
    body = Part.makeBox(EXT_W, EXT_D, total_h)

    # Go-rail groove on inner face (runs full Y depth, centered in Z)
    if inner_x == EXT_W:
        # Left guide: inner face at x=EXT_W, groove cuts from right
        groove = Part.makeBox(GROOVE_D, EXT_D, GROOVE_W)
        groove.Placement.Base = App.Vector(EXT_W - GROOVE_D, 0, groove_z)
    else:
        # Right guide: inner face at x=0, groove cuts from left
        groove = Part.makeBox(GROOVE_D, EXT_D, GROOVE_W)
        groove.Placement.Base = App.Vector(0, 0, groove_z)

    body = body.cut(groove)

    # Bottom entry chamfer on inner face — 45° funnel to ease controller alignment
    # Triangle prism cut from bottom corner of inner face
    if inner_x == EXT_W:
        pts = [
            App.Vector(EXT_W - CHAMFER, 0, 0),
            App.Vector(EXT_W,           0, 0),
            App.Vector(EXT_W,           0, CHAMFER),
        ]
    else:
        pts = [
            App.Vector(0,        0, 0),
            App.Vector(CHAMFER,  0, 0),
            App.Vector(0,        0, CHAMFER),
        ]
    wire = Part.makePolygon([*pts, pts[0]])
    face = Part.Face(wire)
    chamfer_prism = face.extrude(App.Vector(0, EXT_D, 0))
    body = body.cut(chamfer_prism)

    obj = doc.addObject("Part::Feature", f"Rail_Ext_{'Left' if inner_x == EXT_W else 'Right'}")
    obj.Shape = body
    doc.recompute()

    save_path = f"/home/bwoodwar/Projects/cyberdeck/cad/{name}.FCStd"
    doc.saveAs(save_path)
    print(f"{name} saved to {save_path}")

print(f"Block: {EXT_W:.1f}(X) × {EXT_D}(Y) × {EXT_H + TAB_H}(Z) mm")
print(f"  Extension below panel: {EXT_H}mm, retention tab inside pocket: {TAB_H}mm")
print(f"  Press-fit into {ctrl_pocket_w}mm pocket (0.2mm clearance)")
print(f"  Go-rail groove: {GROOVE_W}mm tall × {GROOVE_D}mm deep (PLACEHOLDER — measure Go side rail)")
print(f"  Entry chamfer: {CHAMFER}mm × 45° on inner face bottom edge")
print(f"NOTE: Print with groove face against Go side rail. Groove profile TBD — calipers needed.")
