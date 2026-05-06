import FreeCAD as App
import Part
import math

# Rear Wall — structural back panel of the chassis
# Spans full chassis width and height; vent cutout clears Go exhaust zone
#
# Positioning note: rear wall inner face sits at y=141.7mm (PANEL_H 136.7mm + 5mm kickstand
# clearance gap), ensuring the folded kickstand is not crushed against the wall.

TILT_DEG = 15.0
tilt = math.radians(TILT_DEG)

CHASSIS_W = 305.0
WALL_T = 4.0             # wall thickness (Y)

# Row thicknesses (Z, stacked bottom to top)
ROW_BATTERY = 40.0       # Panel E/F
ROW_PLANCK  = 36.0       # Panel C/D
ROW_GO      = 62.0       # Panel A/B
CHASSIS_H   = ROW_BATTERY + ROW_PLANCK + ROW_GO   # 138mm total

# Go base dimensions
GO_W  = 210.0
GO_D  = 131.0
GO_T  = 20.1
FLOOR = 3.0

# Vent cutout — aligned to Go exhaust zone
# X: full Go base width, centered in chassis
go_x_start = (CHASSIS_W - GO_W) / 2.0   # 47.5mm
go_x_end   = go_x_start + GO_W           # 257.5mm
VENT_W     = GO_W                        # 210mm

# Z: from Go cradle rear floor level up to chassis top
tilt_rise      = math.tan(tilt) * GO_D
go_row_base_z  = ROW_BATTERY + ROW_PLANCK   # 76mm from chassis bottom
vent_z_bot     = go_row_base_z + FLOOR + tilt_rise   # ~114mm
vent_z_top     = CHASSIS_H                            # 138mm (open to chassis top)
VENT_H         = vent_z_top - vent_z_bot             # ~24mm

CLEARANCE_D = 3.2   # M3 clearance hole diameter

# Clearance hole positions (chassis X, chassis Z) — match panel insert locations
# AB row (panel local z + row_base_z=76mm): inserts at local z=52 and z=20
# CD row (panel local z + row_base_z=40mm): inserts at local z=18
# EF row (panel local z + row_base_z=0mm):  inserts at local z=20
BOLT_HOLES = [
    # AB row — left panel (A): chassis x=17 (above ctrl pocket), x=90 (cradle floor)
    (17,  ROW_BATTERY + ROW_PLANCK + 52),   # chassis z=128
    (90,  ROW_BATTERY + ROW_PLANCK + 20),   # chassis z=96
    # AB row — right panel (B): chassis x=215 (cradle floor), x=288 (above ctrl pocket)
    (215, ROW_BATTERY + ROW_PLANCK + 20),   # chassis z=96
    (288, ROW_BATTERY + ROW_PLANCK + 52),   # chassis z=128
    # CD row — left panel (C): chassis x=17, x=90
    (17,  ROW_BATTERY + 18),                # chassis z=58
    (90,  ROW_BATTERY + 18),                # chassis z=58
    # CD row — right panel (D): chassis x=152.5+17=169.5→use 170, x=152.5+135=287.5→use 288
    (170, ROW_BATTERY + 18),                # chassis z=58
    (288, ROW_BATTERY + 18),                # chassis z=58
    # EF row — left panel (E): chassis x=17, x=60
    (17,  20),                              # chassis z=20
    (60,  20),                              # chassis z=20
    # EF row — right panel (F): chassis x=152.5+17=170, x=152.5+135=288
    (170, 20),                              # chassis z=20
    (288, 20),                              # chassis z=20
]

doc = App.newDocument("rear_wall")

base = Part.makeBox(CHASSIS_W, WALL_T, CHASSIS_H)

# Vent cutout — full open rectangle aligned to Go exhaust
vent = Part.makeBox(VENT_W, WALL_T, VENT_H)
vent.Placement.Base = App.Vector(go_x_start, 0, vent_z_bot)
wall = base.cut(vent)

# M3 clearance holes (Y direction, through wall thickness)
for (bx, bz) in BOLT_HOLES:
    hole = Part.makeCylinder(CLEARANCE_D/2, WALL_T, App.Vector(bx, 0, bz), App.Vector(0, 1, 0))
    wall = wall.cut(hole)

obj = doc.addObject("Part::Feature", "Rear_Wall")
obj.Shape = wall
doc.recompute()

save_path = "/home/bwoodwar/Projects/cyberdeck/cad/rear_wall.FCStd"
doc.saveAs(save_path)
print(f"Rear wall saved to {save_path}")
print(f"Outer: {CHASSIS_W} x {WALL_T} x {CHASSIS_H} mm")
print(f"Vent cutout: {VENT_W} x {WALL_T} x {VENT_H:.1f} mm (z={vent_z_bot:.1f}–{vent_z_top}mm)")
print(f"M3 clearance holes: {len(BOLT_HOLES)} holes through wall at positions:")
for (bx, bz) in BOLT_HOLES:
    print(f"  (x={bx}, z={bz})")
print(f"Kickstand clearance: 5mm gap between panel rear face and wall inner face")
