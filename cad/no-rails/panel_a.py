import FreeCAD as App
import Part
import math

# Panel A (no-rails) — Go cradle, left half
# Controller rail channels removed; left outer wall is solid (43.5mm).
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

tilt_rise = math.tan(tilt) * GO_D            # ~35mm
PANEL_T = math.ceil(FLOOR + GO_T + CLEARANCE + tilt_rise) + 2  # 62mm

# Go cavity: centered in chassis
go_cav_x = (CHASSIS_W - (GO_W + 2 * CLEARANCE)) / 2.0   # 46.5mm
go_cav_w_in_a = PANEL_W - go_cav_x                        # ~106mm

doc = App.newDocument("panel_a_nr")

base = Part.makeBox(PANEL_W, PANEL_H, PANEL_T)

# Go cradle wedge — same as original
go_cradle = Part.makeWedge(
    go_cav_x, 0, FLOOR, FLOOR + tilt_rise, go_cav_x,
    PANEL_W, PANEL_H, PANEL_T, PANEL_T, PANEL_W
)
panel = base.cut(go_cradle)

# No controller rail channel — left outer wall (x=0..46.5mm) is solid throughout

# M3 hardware
INSERT_D     = 4.5
INSERT_DEPTH = 6.0
PIN_D        = 2.5
PIN_DEPTH    = 5.0

# --- Front face heat insert (Y direction, for AB-CD angle bracket upper leg) ---
# x=25mm in solid left wall (go_cav_x=46.5mm); z=50mm matches bracket AB-CD span
front_ins = Part.makeCylinder(INSERT_D/2, INSERT_DEPTH, App.Vector(25, 0, 50), App.Vector(0, 1, 0))
panel = panel.cut(front_ins)

# --- Rear face heat insert holes ---
# x=17: in solid left wall (x < go_cav_x=46.5), z=52 (any z works — fully solid)
ins1 = Part.makeCylinder(INSERT_D/2, INSERT_DEPTH, App.Vector(17, PANEL_H, 52), App.Vector(0, -1, 0))
panel = panel.cut(ins1)
# x=90: in cradle region; z=20 < cradle floor at rear (~38mm) — solid
ins2 = Part.makeCylinder(INSERT_D/2, INSERT_DEPTH, App.Vector(90, PANEL_H, 20), App.Vector(0, -1, 0))
panel = panel.cut(ins2)

# --- Alignment pin at right seam face (mates with Panel B) ---
pin = Part.makeCylinder(PIN_D/2, PIN_DEPTH, App.Vector(PANEL_W, 89, 10), App.Vector(-1, 0, 0))
panel = panel.cut(pin)

obj = doc.addObject("Part::Feature", "Panel_A_NR")
obj.Shape = panel
doc.recompute()

save_path = "/home/bwoodwar/Projects/cyberdeck/cad/no-rails/panel_a.FCStd"
doc.saveAs(save_path)
print(f"Panel A (no-rails) saved to {save_path}")
print(f"Outer: {PANEL_W} x {PANEL_H} x {PANEL_T} mm")
print(f"Tilt: {TILT_DEG}° → tilt_rise = {tilt_rise:.1f}mm")
print(f"Go cradle: {go_cav_w_in_a:.1f} x {PANEL_H} mm (floor: {FLOOR}mm front → {FLOOR + tilt_rise:.1f}mm rear)")
print(f"Left outer wall: {go_cav_x:.1f}mm solid (no rail channel)")
print(f"Rear inserts: (x=17,z=52) and (x=90,z=20), depth={INSERT_DEPTH}mm")
print(f"Alignment pin: seam face x={PANEL_W}, y=89, z=10, depth={PIN_DEPTH}mm")
