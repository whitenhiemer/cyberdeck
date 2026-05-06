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
print(f"Outer right wall: {PANEL_W - ctrl_pocket_end:.1f}mm")
print(f"NOTE: Rail groove cross-section TBD — needs calipers on Go side rail before finalizing")
