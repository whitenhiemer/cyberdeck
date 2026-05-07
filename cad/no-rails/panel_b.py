import FreeCAD as App
import Part
import math

# Panel B (no-rails) — Go cradle, right half
# Controller rail channels removed; right outer wall is solid (46.5mm).
# Use when Go will be removed from chassis to play as a handheld.

TILT_DEG = 15.0
tilt = math.radians(TILT_DEG)

CHASSIS_W = 305.0
PANEL_W = 152.5
PANEL_H = 136.7

GO_W = 210.0
GO_D = 131.0
GO_T = 20.1
CLEARANCE = 1.0
FLOOR = 3.0

tilt_rise = math.tan(tilt) * GO_D
PANEL_T = math.ceil(FLOOR + GO_T + CLEARANCE + tilt_rise) + 2  # 62mm

# Go cavity: centered in chassis; Panel B starts at chassis x=PANEL_W
go_cav_x_chassis = (CHASSIS_W - (GO_W + 2 * CLEARANCE)) / 2.0  # 46.5mm
go_right_chassis = go_cav_x_chassis + GO_W + 2 * CLEARANCE      # 258.5mm
go_cav_w_in_b = go_right_chassis - PANEL_W                       # ~106mm

doc = App.newDocument("panel_b_nr")

base = Part.makeBox(PANEL_W, PANEL_H, PANEL_T)

# Go cradle wedge — same as original
go_cradle = Part.makeWedge(
    0, 0, FLOOR, FLOOR + tilt_rise, 0,
    go_cav_w_in_b, PANEL_H, PANEL_T, PANEL_T, go_cav_w_in_b
)
panel = base.cut(go_cradle)

# No controller rail channel — right outer wall (x=106..152.5mm) is solid throughout

# M3 hardware
INSERT_D     = 4.5
INSERT_DEPTH = 6.0
PIN_D        = 2.5
PIN_DEPTH    = 5.0

# --- Front face heat insert (Y direction, for AB-CD angle bracket upper leg) ---
# x=128mm in solid right wall (go_cav_w_in_b=106mm); z=50mm matches bracket AB-CD span
front_ins = Part.makeCylinder(INSERT_D/2, INSERT_DEPTH, App.Vector(128, 0, 50), App.Vector(0, 1, 0))
panel = panel.cut(front_ins)

# --- Rear face heat insert holes ---
# x=62.5: cradle region; z=20 < cradle floor at rear (~38mm) — solid
ins1 = Part.makeCylinder(INSERT_D/2, INSERT_DEPTH, App.Vector(62.5, PANEL_H, 20), App.Vector(0, -1, 0))
panel = panel.cut(ins1)
# x=135.5: in solid right wall (x > go_cav_w_in_b=106), z=52 (any z works — fully solid)
ins2 = Part.makeCylinder(INSERT_D/2, INSERT_DEPTH, App.Vector(135.5, PANEL_H, 52), App.Vector(0, -1, 0))
panel = panel.cut(ins2)

# --- Alignment pin at left seam face (mates with Panel A) ---
pin = Part.makeCylinder(PIN_D/2, PIN_DEPTH, App.Vector(0, 89, 10), App.Vector(1, 0, 0))
panel = panel.cut(pin)

obj = doc.addObject("Part::Feature", "Panel_B_NR")
obj.Shape = panel
doc.recompute()

save_path = "/home/bwoodwar/Projects/cyberdeck/cad/no-rails/panel_b.FCStd"
doc.saveAs(save_path)
print(f"Panel B (no-rails) saved to {save_path}")
print(f"Outer: {PANEL_W} x {PANEL_H} x {PANEL_T} mm")
print(f"Tilt: {TILT_DEG}° → tilt_rise = {tilt_rise:.1f}mm")
print(f"Go cradle: {go_cav_w_in_b:.1f} x {PANEL_H} mm (floor: {FLOOR}mm front → {FLOOR + tilt_rise:.1f}mm rear)")
print(f"Right outer wall: {PANEL_W - go_cav_w_in_b:.1f}mm solid (no rail channel)")
print(f"Rear inserts: (x=62.5,z=20) and (x=135.5,z=52), depth={INSERT_DEPTH}mm")
print(f"Alignment pin: seam face x=0, y=89, z=10, depth={PIN_DEPTH}mm")
