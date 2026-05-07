import FreeCAD as App
import Part

# Panel E — battery bay, left half
# Cyberdeck chassis bottom-left battery row panel
# Battery slides in/out from the bottom (open bottom face)

PANEL_W = 152.5      # width (X) — left half of chassis
PANEL_H = 136.7      # depth (Y) — front to back (matches all rows for flat rear wall)
PANEL_T = 40.0       # thickness (Z) — 5mm top wall + 35mm battery cavity

BATTERY_L = 134.0    # battery long dimension (X, left-right)
BATTERY_D = 70.0     # battery depth (Y, front-to-back)
BATTERY_T = 34.0     # battery thickness (Z, up-down in section)
CLEARANCE = 1.0      # clearance each side
CHASSIS_W = 305.0    # full chassis width (for centering)

# Cavity dimensions with clearance
cav_w = BATTERY_L + 2 * CLEARANCE   # 136mm total
cav_h = BATTERY_D + 2 * CLEARANCE   # 72mm
cav_d = BATTERY_T + CLEARANCE       # 35mm (open at bottom)
top_wall = PANEL_T - cav_d          # 5mm top wall

# Battery centered in chassis
battery_x = (CHASSIS_W - cav_w) / 2.0   # 84.5mm from chassis left
battery_y = (PANEL_H - cav_h) / 2.0     # 32.35mm from front edge

# In Panel E, cavity goes from battery_x to PANEL_W (seam)
cav_w_in_e = PANEL_W - battery_x    # ~68mm

doc = App.newDocument("panel_e")

base = Part.makeBox(PANEL_W, PANEL_H, PANEL_T)

# Battery cavity — open at bottom (z=0), closed at top
# Cut from bottom up to cav_d, leaving top_wall intact
cavity = Part.makeBox(cav_w_in_e, cav_h, cav_d)
cavity.Placement.Base = App.Vector(battery_x, battery_y, 0)
panel = base.cut(cavity)

# M3 hardware
INSERT_D     = 4.5
INSERT_DEPTH = 6.0
PIN_D        = 2.5
PIN_DEPTH    = 5.0

# --- Front face heat insert hole (Y direction, for CD-EF angle bracket lower leg) ---
# Front face fully solid at y=0 (battery cavity starts at y=9.5mm)
front_ins = Part.makeCylinder(INSERT_D/2, INSERT_DEPTH, App.Vector(25, 0, 20), App.Vector(0, 1, 0))
panel = panel.cut(front_ins)

# --- Rear face heat insert holes (Y direction, for rear wall M3 bolts) ---
# Rear face at y=PANEL_H=136.7mm — battery cavity ends at y=104.35mm, rear face is solid
# x=17mm: left solid wall (battery cavity starts at x=84.5mm)
# x=60mm: also left solid wall (< battery_x=84.5mm)
ins1 = Part.makeCylinder(INSERT_D/2, INSERT_DEPTH, App.Vector(17, PANEL_H, 20), App.Vector(0, -1, 0))
panel = panel.cut(ins1)
ins2 = Part.makeCylinder(INSERT_D/2, INSERT_DEPTH, App.Vector(60, PANEL_H, 20), App.Vector(0, -1, 0))
panel = panel.cut(ins2)

# --- Alignment pin hole at right seam face (mates with Panel F, X direction) ---
# y=15mm is in front solid section (battery cavity starts at y=32.35mm) — solid throughout Z
pin = Part.makeCylinder(PIN_D/2, PIN_DEPTH, App.Vector(PANEL_W, 15, 20), App.Vector(-1, 0, 0))
panel = panel.cut(pin)

obj = doc.addObject("Part::Feature", "Panel_E")
obj.Shape = panel
doc.recompute()

save_path = "/home/bwoodwar/Projects/cyberdeck/cad/panel_e.FCStd"
doc.saveAs(save_path)
print(f"Panel E saved to {save_path}")
print(f"Outer: {PANEL_W} x {PANEL_H} x {PANEL_T} mm")
print(f"Battery cavity: {cav_w_in_e:.1f} x {cav_h} x {cav_d} mm at x={battery_x}, y={battery_y:.1f}")
print(f"Top wall thickness: {top_wall}mm")
print(f"Rear inserts: (x=17,z=20) and (x=60,z=20), depth={INSERT_DEPTH}mm")
print(f"Alignment pin: seam face x={PANEL_W}, y=15, z=20, depth={PIN_DEPTH}mm")
