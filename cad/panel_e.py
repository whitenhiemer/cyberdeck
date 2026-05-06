import FreeCAD as App
import Part

# Panel E — battery bay, left half
# Cyberdeck chassis bottom-left battery row panel
# Battery slides in/out from the bottom (open bottom face)

PANEL_W = 152.5      # width (X) — left half of chassis
PANEL_H = 91.0       # depth (Y) — front to back (matches C+D)
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
battery_y = (PANEL_H - cav_h) / 2.0     # 9.5mm from front edge

# In Panel E, cavity goes from battery_x to PANEL_W (seam)
cav_w_in_e = PANEL_W - battery_x    # ~68mm

doc = App.newDocument("panel_e")

base = Part.makeBox(PANEL_W, PANEL_H, PANEL_T)

# Battery cavity — open at bottom (z=0), closed at top
# Cut from bottom up to cav_d, leaving top_wall intact
cavity = Part.makeBox(cav_w_in_e, cav_h, cav_d)
cavity.Placement.Base = App.Vector(battery_x, battery_y, 0)
panel = base.cut(cavity)

obj = doc.addObject("Part::Feature", "Panel_E")
obj.Shape = panel
doc.recompute()

save_path = "/home/bwoodwar/Projects/cyberdeck/cad/panel_e.FCStd"
doc.saveAs(save_path)
print(f"Panel E saved to {save_path}")
print(f"Outer: {PANEL_W} x {PANEL_H} x {PANEL_T} mm")
print(f"Battery cavity in this panel: {cav_w_in_e:.1f} x {cav_h} x {cav_d} mm")
print(f"Cavity starts at x={battery_x}, y={battery_y:.1f}")
print(f"Top wall thickness: {top_wall}mm")
