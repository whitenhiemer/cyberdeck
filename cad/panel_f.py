import FreeCAD as App
import Part

# Panel F — battery bay, right half
# Cyberdeck chassis bottom-right battery row panel
# Battery slides in/out from the bottom (open bottom face)

PANEL_W = 152.5      # width (X) — right half of chassis
PANEL_H = 136.7      # depth (Y) — front to back (matches all rows for flat rear wall)
PANEL_T = 40.0       # thickness (Z) — 5mm top wall + 35mm battery cavity

BATTERY_L = 134.0    # battery long dimension (X, left-right)
BATTERY_D = 70.0     # battery depth (Y, front-to-back)
BATTERY_T = 34.0     # battery thickness (Z, up-down in section)
CLEARANCE = 1.0      # clearance each side
CHASSIS_W = 305.0    # full chassis width (for centering)

cav_w = BATTERY_L + 2 * CLEARANCE   # 136mm total
cav_h = BATTERY_D + 2 * CLEARANCE   # 72mm
cav_d = BATTERY_T + CLEARANCE       # 35mm

# Battery centered in chassis; Panel F starts at x=152.5
battery_x_chassis = (CHASSIS_W - cav_w) / 2.0    # 84.5mm from chassis left
battery_right_chassis = battery_x_chassis + cav_w  # 220.5mm from chassis left
battery_y = (PANEL_H - cav_h) / 2.0               # 32.35mm from front edge

# In Panel F local coords (origin at seam = chassis x=152.5)
# Cavity from x=0 (seam) to x=(battery_right_chassis - PANEL_W)
cav_w_in_f = battery_right_chassis - PANEL_W   # ~68mm

doc = App.newDocument("panel_f")

base = Part.makeBox(PANEL_W, PANEL_H, PANEL_T)

# Battery cavity — open at bottom (z=0), starts at seam face (x=0)
cavity = Part.makeBox(cav_w_in_f, cav_h, cav_d)
cavity.Placement.Base = App.Vector(0, battery_y, 0)
panel = base.cut(cavity)

# USB-C port access cutout on right face
# Power bank USB-C port: ~10mm wide, 5mm tall, assume centered on right wall
# at mid-height of battery cavity
usbc_w = 12.0   # cutout width (X is depth into right wall here)
usbc_h = 8.0    # cutout height
usbc_wall = 10.0
usbc_x_start = PANEL_W - usbc_wall
usbc_y_pos = (PANEL_H / 2) - (usbc_h / 2)
usbc_z_pos = cav_d / 2 - usbc_h / 2

usbc = Part.makeBox(usbc_wall, usbc_w, usbc_h)
usbc.Placement.Base = App.Vector(usbc_x_start, usbc_y_pos, usbc_z_pos)
panel = panel.cut(usbc)

# M3 hardware
INSERT_D     = 4.5
INSERT_DEPTH = 6.0
PIN_D        = 2.5
PIN_DEPTH    = 5.0

# --- Front face heat insert hole (Y direction, for CD-EF angle bracket lower leg) ---
# x=128mm local = chassis x=280.5mm (right solid wall; front face fully solid at y=0)
front_ins = Part.makeCylinder(INSERT_D/2, INSERT_DEPTH, App.Vector(128, 0, 20), App.Vector(0, 1, 0))
panel = panel.cut(front_ins)

# --- Rear face heat insert holes (Y direction, for rear wall M3 bolts) ---
# Rear face at y=PANEL_H=136.7mm — battery cavity ends at y=104.35mm, rear face is solid
# x=17mm local = chassis x=169.5mm (left of battery cavity which starts at x=68mm in F local)
# x=135mm local = chassis x=287.5mm (right solid wall, battery cavity ends at x=68mm)
ins1 = Part.makeCylinder(INSERT_D/2, INSERT_DEPTH, App.Vector(17, PANEL_H, 20), App.Vector(0, -1, 0))
panel = panel.cut(ins1)
ins2 = Part.makeCylinder(INSERT_D/2, INSERT_DEPTH, App.Vector(135, PANEL_H, 20), App.Vector(0, -1, 0))
panel = panel.cut(ins2)

# --- Alignment pin hole at left seam face (mates with Panel E, X direction) ---
# y=15mm is in front solid section (battery cavity starts at y=32.35mm) — solid throughout Z
pin = Part.makeCylinder(PIN_D/2, PIN_DEPTH, App.Vector(0, 15, 20), App.Vector(1, 0, 0))
panel = panel.cut(pin)

obj = doc.addObject("Part::Feature", "Panel_F")
obj.Shape = panel
doc.recompute()

save_path = "/home/bwoodwar/Projects/cyberdeck/cad/panel_f.FCStd"
doc.saveAs(save_path)
print(f"Panel F saved to {save_path}")
print(f"Outer: {PANEL_W} x {PANEL_H} x {PANEL_T} mm")
print(f"Battery cavity: {cav_w_in_f:.1f} x {cav_h} x {cav_d} mm")
print(f"USB-C cutout on right face: {usbc_w} x {usbc_h} mm")
print(f"Rear inserts: (x=17,z=20) and (x=135,z=20), depth={INSERT_DEPTH}mm")
print(f"Alignment pin: seam face x=0, y=15, z=20, depth={PIN_DEPTH}mm")
