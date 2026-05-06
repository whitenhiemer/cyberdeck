import FreeCAD as App
import Part
import math

# Panel A — Go cradle, left half
# Contains left controller rail channel and left half of Legion Go wedge cradle

TILT_DEG = 15.0          # screen tilt angle (degrees); TBD, 10-15° per design
tilt = math.radians(TILT_DEG)

CHASSIS_W = 305.0
PANEL_W = 152.5          # width (X) — left half of chassis
PANEL_H = 136.7          # depth (Y) — front to back (controller height sets row depth)

# Legion Go base dimensions
GO_W = 210.0
GO_D = 131.0             # front to back
GO_T = 20.1              # thickness (Z)
CLEARANCE = 1.0
FLOOR = 3.0              # floor thickness below Go

# Controller dimensions
CTRL_T = 42.25           # controller thickness (Z); exceeds Go body (40.7mm) by 1.55mm
CTRL_OUTER_WALL = 3.0    # chassis left outer wall thickness

# Derived
tilt_rise = math.tan(tilt) * GO_D            # ~35mm height gain front-to-rear
PANEL_T = math.ceil(FLOOR + GO_T + CLEARANCE + tilt_rise) + 2  # ~62mm

# Go cavity: centered in chassis X, full panel depth in Y
go_cav_x = (CHASSIS_W - (GO_W + 2 * CLEARANCE)) / 2.0  # ~46.5mm from chassis/panel left
go_cav_w_in_a = PANEL_W - go_cav_x                       # ~106mm (extends to seam)

# Controller rail pocket
CTRL_T_CLEAR = CTRL_T + CLEARANCE    # 43.25mm in Z
ctrl_pocket_w = go_cav_x - CTRL_OUTER_WALL  # ~43.5mm in X

doc = App.newDocument("panel_a")

base = Part.makeBox(PANEL_W, PANEL_H, PANEL_T)

# --- Go cradle: wedge cavity, open at top ---
# Floor slopes from FLOOR (front, y=0) to FLOOR+tilt_rise (rear, y=PANEL_H)
# Ceiling is flat at PANEL_T throughout
# Part.makeWedge(xmin,ymin,zmin,z2min,x2min, xmax,ymax,zmax,z2max,x2max)
#   At y=ymin: rectangle x=[xmin,xmax], z=[zmin,zmax]
#   At y=ymax: rectangle x=[x2min,x2max], z=[z2min,z2max]
go_cradle = Part.makeWedge(
    go_cav_x, 0, FLOOR, FLOOR + tilt_rise, go_cav_x,
    PANEL_W, PANEL_H, PANEL_T, PANEL_T, PANEL_W
)
panel = base.cut(go_cradle)

# --- Controller rail channel: open at bottom, exits downward for slide-out removal ---
# Placeholder rectangular pocket — actual rail groove cross-section TBD (needs calipers)
ctrl_pocket = Part.makeBox(ctrl_pocket_w, PANEL_H, CTRL_T_CLEAR)
ctrl_pocket.Placement.Base = App.Vector(CTRL_OUTER_WALL, 0, 0)
panel = panel.cut(ctrl_pocket)

# M3 hardware
INSERT_D     = 4.5    # heat insert outer diameter (mm)
INSERT_DEPTH = 6.0    # heat insert hole depth
PIN_D        = 2.5    # alignment pin diameter
PIN_DEPTH    = 5.0    # pin hole depth per panel

# --- Front face heat insert hole (Y direction, for AB-CD angle bracket upper leg) ---
# x=25mm (above controller pocket, z=50mm > CTRL_T_CLEAR=43.25mm — solid at y=0)
front_ins = Part.makeCylinder(INSERT_D/2, INSERT_DEPTH, App.Vector(25, 0, 50), App.Vector(0, 1, 0))
panel = panel.cut(front_ins)

# --- Rear face heat insert holes (Y direction, for rear wall M3 bolts) ---
# x=17mm: above controller pocket (z=52mm > CTRL_T_CLEAR=43.25mm — solid)
ins1 = Part.makeCylinder(INSERT_D/2, INSERT_DEPTH, App.Vector(17, PANEL_H, 52), App.Vector(0, -1, 0))
panel = panel.cut(ins1)
# x=90mm: below Go cradle floor at rear face (floor at y=PANEL_H is 38.1mm, z=20mm < 38.1mm — solid)
ins2 = Part.makeCylinder(INSERT_D/2, INSERT_DEPTH, App.Vector(90, PANEL_H, 20), App.Vector(0, -1, 0))
panel = panel.cut(ins2)

# --- Alignment pin hole at right seam face (mates with Panel B, X direction) ---
# y=89mm rear margin — solid below cradle floor (floor at y=89mm is 25.9mm, z=10mm < 25.9mm)
pin = Part.makeCylinder(PIN_D/2, PIN_DEPTH, App.Vector(PANEL_W, 89, 10), App.Vector(-1, 0, 0))
panel = panel.cut(pin)

obj = doc.addObject("Part::Feature", "Panel_A")
obj.Shape = panel
doc.recompute()

save_path = "/home/bwoodwar/Projects/cyberdeck/cad/panel_a.FCStd"
doc.saveAs(save_path)
print(f"Panel A saved to {save_path}")
print(f"Outer: {PANEL_W} x {PANEL_H} x {PANEL_T} mm")
print(f"Tilt: {TILT_DEG}° → tilt_rise = {tilt_rise:.1f}mm")
print(f"Go cradle cavity: {go_cav_w_in_a:.1f} x {PANEL_H} mm (floor: {FLOOR}mm front → {FLOOR + tilt_rise:.1f}mm rear)")
print(f"Controller pocket: {ctrl_pocket_w:.1f} x {PANEL_H} x {CTRL_T_CLEAR}mm (open at bottom)")
print(f"Rear inserts: (x=17,z=52) and (x=90,z=20), depth={INSERT_DEPTH}mm")
print(f"Alignment pin: seam face x={PANEL_W}, y=89, z=10, depth={PIN_DEPTH}mm")
print(f"NOTE: Rail groove cross-section TBD — needs calipers on Go side rail before finalizing")
