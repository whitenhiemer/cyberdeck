import FreeCAD as App
import Part

# Panel C — Planck bay, left half
# Cyberdeck chassis bottom-left panel

PANEL_W = 152.5       # width (X) — left half of chassis
PANEL_H = 91.0        # depth (Y) — front to back
PANEL_T = 36.0        # thickness (Z) — 3mm floor + 33mm Planck recess

PLANCK_POCKET_W = 236.0   # 234mm Planck + 1mm clearance each side
PLANCK_POCKET_H = 83.0    # 81mm Planck + 1mm clearance each side
PLANCK_POCKET_D = 33.0    # full Planck case depth
CHASSIS_W = 305.0         # full chassis width (for centering)

planck_x = (CHASSIS_W - PLANCK_POCKET_W) / 2.0   # 34.5mm from chassis left
planck_y = (PANEL_H - PLANCK_POCKET_H) / 2.0     # 4.0mm from front edge
pocket_z = PANEL_T - PLANCK_POCKET_D              # 3.0mm floor remains below pocket

# pocket in Panel C goes from planck_x to the seam at PANEL_W
pocket_w_in_c = PANEL_W - planck_x   # ~118mm

doc = App.newDocument("panel_c")

base = Part.makeBox(PANEL_W, PANEL_H, PANEL_T)

pocket = Part.makeBox(pocket_w_in_c, PLANCK_POCKET_H, PLANCK_POCKET_D)
pocket.Placement.Base = App.Vector(planck_x, planck_y, pocket_z)
panel = base.cut(pocket)

obj = doc.addObject("Part::Feature", "Panel_C")
obj.Shape = panel
doc.recompute()

save_path = "/home/bwoodwar/Projects/cyberdeck/cad/panel_c.FCStd"
doc.saveAs(save_path)
print(f"Panel C saved to {save_path}")
print(f"Outer: {PANEL_W} x {PANEL_H} x {PANEL_T} mm")
print(f"Planck pocket in this panel: {pocket_w_in_c:.1f} x {PLANCK_POCKET_H} x {PLANCK_POCKET_D} mm")
print(f"Pocket starts at x={planck_x}, y={planck_y}, z={pocket_z}")
