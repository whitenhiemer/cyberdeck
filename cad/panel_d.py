import FreeCAD as App
import Part

# Panel D — Planck bay, right half
# Cyberdeck chassis bottom-right panel

PANEL_W = 152.5       # width (X) — right half of chassis
PANEL_H = 91.0        # depth (Y) — front to back
PANEL_T = 36.0        # thickness (Z) — 3mm floor + 33mm Planck recess

PLANCK_POCKET_W = 236.0   # 234mm Planck + 1mm clearance each side
PLANCK_POCKET_H = 83.0    # 81mm Planck + 1mm clearance each side
PLANCK_POCKET_D = 33.0    # full Planck case depth
CHASSIS_W = 305.0         # full chassis width (for centering)

planck_x_chassis = (CHASSIS_W - PLANCK_POCKET_W) / 2.0   # 34.5mm from chassis left
planck_y = (PANEL_H - PLANCK_POCKET_H) / 2.0             # 4.0mm from front edge
pocket_z = PANEL_T - PLANCK_POCKET_D                      # 3.0mm floor remains below

# Panel D starts at chassis x=152.5 — pocket continues from the seam
# In Panel D local coords, pocket starts at x=0 (seam face)
pocket_right_chassis = planck_x_chassis + PLANCK_POCKET_W  # 270.5mm from chassis left
pocket_w_in_d = pocket_right_chassis - PANEL_W              # ~118mm

doc = App.newDocument("panel_d")

base = Part.makeBox(PANEL_W, PANEL_H, PANEL_T)

# Planck pocket — starts flush with seam (x=0), opens left to mate with Panel C
pocket = Part.makeBox(pocket_w_in_d, PLANCK_POCKET_H, PLANCK_POCKET_D)
pocket.Placement.Base = App.Vector(0, planck_y, pocket_z)
panel = base.cut(pocket)

obj = doc.addObject("Part::Feature", "Panel_D")
obj.Shape = panel
doc.recompute()

save_path = "/home/bwoodwar/Projects/cyberdeck/cad/panel_d.FCStd"
doc.saveAs(save_path)
print(f"Panel D saved to {save_path}")
print(f"Outer: {PANEL_W} x {PANEL_H} x {PANEL_T} mm")
print(f"Planck pocket in this panel: {pocket_w_in_d:.1f} x {PLANCK_POCKET_H} x {PLANCK_POCKET_D} mm")
print(f"Solid right wall: {PANEL_W - pocket_w_in_d:.1f}mm wide")
