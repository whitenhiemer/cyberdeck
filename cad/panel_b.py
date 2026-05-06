import FreeCAD as App
import Part
import math

# Panel B — Go cradle, right half
# Contains right controller rail channel and right half of Legion Go wedge cradle
# Mirrors Panel A: Go cavity starts at seam (x=0 local), controller pocket on right outer wall

TILT_DEG = 15.0          # screen tilt angle (degrees); TBD, 10-15° per design
tilt = math.radians(TILT_DEG)

CHASSIS_W = 305.0
PANEL_W = 152.5          # width (X) — right half of chassis
PANEL_H = 136.7          # depth (Y) — front to back (controller height sets row depth)

# Legion Go base dimensions
GO_W = 210.0
GO_D = 131.0             # front to back
GO_T = 20.1              # thickness (Z)
CLEARANCE = 1.0
FLOOR = 3.0              # floor thickness below Go

# Controller dimensions
CTRL_T = 42.25           # controller thickness (Z); exceeds Go body (40.7mm) by 1.55mm
CTRL_OUTER_WALL = 3.0    # chassis right outer wall thickness

# Derived
tilt_rise = math.tan(tilt) * GO_D            # ~35mm height gain front-to-rear
PANEL_T = math.ceil(FLOOR + GO_T + CLEARANCE + tilt_rise) + 2  # ~62mm

# Panel B starts at chassis x=PANEL_W (the seam)
# Go cavity: centered in chassis, right portion falls in Panel B
go_cav_x_chassis = (CHASSIS_W - (GO_W + 2 * CLEARANCE)) / 2.0  # 46.5mm from chassis left
go_right_chassis = go_cav_x_chassis + GO_W + 2 * CLEARANCE      # 258.5mm from chassis left
go_cav_w_in_b = go_right_chassis - PANEL_W                       # ~106mm from seam

# Controller rail pocket (right side)
ctrl_pocket_start = go_cav_w_in_b                # x where Go cavity ends (~106mm)
ctrl_pocket_end = PANEL_W - CTRL_OUTER_WALL      # x leaving 3mm outer wall (~149.5mm)
ctrl_pocket_w = ctrl_pocket_end - ctrl_pocket_start  # ~43.5mm

CTRL_T_CLEAR = CTRL_T + CLEARANCE    # 43.25mm in Z

doc = App.newDocument("panel_b")

base = Part.makeBox(PANEL_W, PANEL_H, PANEL_T)

# --- Go cradle: wedge cavity, open at top ---
# Starts at seam face (x=0 local), floor slopes from FLOOR (front) to FLOOR+tilt_rise (rear)
# Part.makeWedge(xmin,ymin,zmin,z2min,x2min, xmax,ymax,zmax,z2max,x2max)
#   At y=ymin: rectangle x=[xmin,xmax], z=[zmin,zmax]
#   At y=ymax: rectangle x=[x2min,x2max], z=[z2min,z2max]
go_cradle = Part.makeWedge(
    0, 0, FLOOR, FLOOR + tilt_rise, 0,
    go_cav_w_in_b, PANEL_H, PANEL_T, PANEL_T, go_cav_w_in_b
)
panel = base.cut(go_cradle)

# --- Controller rail channel: open at bottom, exits downward for slide-out removal ---
# Placeholder rectangular pocket — actual rail groove cross-section TBD (needs calipers)
ctrl_pocket = Part.makeBox(ctrl_pocket_w, PANEL_H, CTRL_T_CLEAR)
ctrl_pocket.Placement.Base = App.Vector(ctrl_pocket_start, 0, 0)
panel = panel.cut(ctrl_pocket)

# M3 hardware
INSERT_D     = 4.5
INSERT_DEPTH = 6.0
PIN_D        = 2.5
PIN_DEPTH    = 5.0

# --- Front face heat insert hole (Y direction, for AB-CD angle bracket upper leg) ---
# x=128mm local = chassis x=280.5mm (above right controller pocket, z=50mm > 43.25mm — solid)
front_ins = Part.makeCylinder(INSERT_D/2, INSERT_DEPTH, App.Vector(128, 0, 50), App.Vector(0, 1, 0))
panel = panel.cut(front_ins)

# --- Rear face heat insert holes (Y direction, for rear wall M3 bolts) ---
# x=62.5mm: below Go cradle floor at rear (chassis x=215mm; floor at y=PANEL_H is 38.1mm, z=20mm — solid)
ins1 = Part.makeCylinder(INSERT_D/2, INSERT_DEPTH, App.Vector(62.5, PANEL_H, 20), App.Vector(0, -1, 0))
panel = panel.cut(ins1)
# x=135.5mm: above right controller pocket (chassis x=288mm; z=52mm > CTRL_T_CLEAR=43.25mm — solid)
ins2 = Part.makeCylinder(INSERT_D/2, INSERT_DEPTH, App.Vector(135.5, PANEL_H, 52), App.Vector(0, -1, 0))
panel = panel.cut(ins2)

# --- Alignment pin hole at left seam face (mates with Panel A, X direction) ---
# y=89mm rear margin — solid below cradle floor
pin = Part.makeCylinder(PIN_D/2, PIN_DEPTH, App.Vector(0, 89, 10), App.Vector(1, 0, 0))
panel = panel.cut(pin)

obj = doc.addObject("Part::Feature", "Panel_B")
obj.Shape = panel
doc.recompute()

save_path = "/home/bwoodwar/Projects/cyberdeck/cad/panel_b.FCStd"
doc.saveAs(save_path)
print(f"Panel B saved to {save_path}")
print(f"Outer: {PANEL_W} x {PANEL_H} x {PANEL_T} mm")
print(f"Tilt: {TILT_DEG}° → tilt_rise = {tilt_rise:.1f}mm")
print(f"Go cradle cavity: {go_cav_w_in_b:.1f} x {PANEL_H} mm (floor: {FLOOR}mm front → {FLOOR + tilt_rise:.1f}mm rear)")
print(f"Controller pocket: {ctrl_pocket_w:.1f} x {PANEL_H} x {CTRL_T_CLEAR}mm at x={ctrl_pocket_start:.1f}mm (open at bottom)")
print(f"Rear inserts: (x=62.5,z=20) and (x=135.5,z=52), depth={INSERT_DEPTH}mm")
print(f"Alignment pin: seam face x=0, y=89, z=10, depth={PIN_DEPTH}mm")
print(f"NOTE: Rail groove cross-section TBD — needs calipers on Go side rail before finalizing")
