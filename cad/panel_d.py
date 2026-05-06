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
right_wall_w = PANEL_W - pocket_w_in_d                     # ~34.5mm (dock space)

# USB-C cable channel through right solid wall (x=pocket_w_in_d to x=PANEL_W)
# Allows Planck cable to exit into dock space; sized to pass USB-C connector for serviceability
CABLE_CH_W = 14.0    # channel width (Y)
CABLE_CH_H = 8.0     # channel height (Z)
cable_ch_y = planck_y + (PLANCK_POCKET_H / 2) - (CABLE_CH_W / 2)  # centered in pocket
cable_ch_z = pocket_z                                                # flush with pocket floor

doc = App.newDocument("panel_d")

base = Part.makeBox(PANEL_W, PANEL_H, PANEL_T)

# Planck pocket — starts flush with seam (x=0), opens left to mate with Panel C
pocket = Part.makeBox(pocket_w_in_d, PLANCK_POCKET_H, PLANCK_POCKET_D)
pocket.Placement.Base = App.Vector(0, planck_y, pocket_z)
panel = base.cut(pocket)

# Cable channel through right wall — Planck USB-C into dock space
cable_ch = Part.makeBox(right_wall_w, CABLE_CH_W, CABLE_CH_H)
cable_ch.Placement.Base = App.Vector(pocket_w_in_d, cable_ch_y, cable_ch_z)
panel = panel.cut(cable_ch)

obj = doc.addObject("Part::Feature", "Panel_D")
obj.Shape = panel
doc.recompute()

save_path = "/home/bwoodwar/Projects/cyberdeck/cad/panel_d.FCStd"
doc.saveAs(save_path)
print(f"Panel D saved to {save_path}")
print(f"Outer: {PANEL_W} x {PANEL_H} x {PANEL_T} mm")
print(f"Planck pocket in this panel: {pocket_w_in_d:.1f} x {PLANCK_POCKET_H} x {PLANCK_POCKET_D} mm")
print(f"Solid right wall: {right_wall_w:.1f}mm wide (dock space)")
print(f"Cable channel (right wall): {right_wall_w:.1f} x {CABLE_CH_W} x {CABLE_CH_H} mm at y={cable_ch_y:.1f}, z={cable_ch_z}")
