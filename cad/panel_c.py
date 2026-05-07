import FreeCAD as App
import Part

# Panel C — Planck bay, left half
# Cyberdeck chassis bottom-left panel

PANEL_W = 152.5       # width (X) — left half of chassis
PANEL_H = 136.7       # depth (Y) — front to back (matches all rows for flat rear wall)
PANEL_T = 36.0        # thickness (Z) — 3mm floor + 33mm Planck recess

PLANCK_POCKET_W = 236.0   # 234mm Planck + 1mm clearance each side
PLANCK_POCKET_H = 83.0    # 81mm Planck + 1mm clearance each side
PLANCK_POCKET_D = 33.0    # full Planck case depth
CHASSIS_W = 305.0         # full chassis width (for centering)

planck_x = (CHASSIS_W - PLANCK_POCKET_W) / 2.0   # 34.5mm from chassis left
planck_y = (PANEL_H - PLANCK_POCKET_H) / 2.0     # 26.85mm from front edge
pocket_z = PANEL_T - PLANCK_POCKET_D              # 3.0mm floor remains below pocket

# pocket in Panel C goes from planck_x to the seam at PANEL_W
pocket_w_in_c = PANEL_W - planck_x   # ~118mm

# USB-C cable channel through left solid wall (x=0 to planck_x)
# Allows Planck cable to exit left face; sized to pass USB-C connector for serviceability
CABLE_CH_W = 14.0    # channel width (Y)
CABLE_CH_H = 8.0     # channel height (Z)
cable_ch_y = planck_y + (PLANCK_POCKET_H / 2) - (CABLE_CH_W / 2)  # centered in pocket
cable_ch_z = pocket_z                                                # flush with pocket floor

doc = App.newDocument("panel_c")

base = Part.makeBox(PANEL_W, PANEL_H, PANEL_T)

pocket = Part.makeBox(pocket_w_in_c, PLANCK_POCKET_H, PLANCK_POCKET_D)
pocket.Placement.Base = App.Vector(planck_x, planck_y, pocket_z)
panel = base.cut(pocket)

# Front-face throat: opens keyboard bay to the user
# Removes the 26.85mm solid lip between the front face and the Planck pocket,
# creating a recessed keyboard bay with palm-rest depth.
throat = Part.makeBox(pocket_w_in_c, planck_y, PLANCK_POCKET_D)
throat.Placement.Base = App.Vector(planck_x, 0, pocket_z)
panel = panel.cut(throat)

# Cable channel through left wall — Planck USB-C exit, left side
cable_ch = Part.makeBox(planck_x, CABLE_CH_W, CABLE_CH_H)
cable_ch.Placement.Base = App.Vector(0, cable_ch_y, cable_ch_z)
panel = panel.cut(cable_ch)

# M3 hardware
INSERT_D     = 4.5
INSERT_DEPTH = 6.0
PIN_D        = 2.5
PIN_DEPTH    = 5.0

# --- Front face heat insert hole (Y direction, shared by AB-CD lower and CD-EF upper brackets) ---
# x=25mm is in the left solid wall (throat cut starts at x=planck_x=34.5mm) — solid at y=0
front_ins = Part.makeCylinder(INSERT_D/2, INSERT_DEPTH, App.Vector(25, 0, 18), App.Vector(0, 1, 0))
panel = panel.cut(front_ins)

# --- Rear face heat insert holes (Y direction, for rear wall M3 bolts) ---
# Rear face at y=PANEL_H=136.7mm is solid (Planck pocket ends at y=109.85mm)
ins1 = Part.makeCylinder(INSERT_D/2, INSERT_DEPTH, App.Vector(17, PANEL_H, 18), App.Vector(0, -1, 0))
panel = panel.cut(ins1)
ins2 = Part.makeCylinder(INSERT_D/2, INSERT_DEPTH, App.Vector(90, PANEL_H, 18), App.Vector(0, -1, 0))
panel = panel.cut(ins2)

# --- Alignment pin hole at right seam face (mates with Panel D, X direction) ---
# y=120mm is in rear solid section (pocket ends at y=109.85mm, throat cut ends at y=26.85mm)
pin = Part.makeCylinder(PIN_D/2, PIN_DEPTH, App.Vector(PANEL_W, 120, 18), App.Vector(-1, 0, 0))
panel = panel.cut(pin)

obj = doc.addObject("Part::Feature", "Panel_C")
obj.Shape = panel
doc.recompute()

save_path = "/home/bwoodwar/Projects/cyberdeck/cad/panel_c.FCStd"
doc.saveAs(save_path)
print(f"Panel C saved to {save_path}")
print(f"Outer: {PANEL_W} x {PANEL_H} x {PANEL_T} mm")
print(f"Planck pocket: {pocket_w_in_c:.1f} x {PLANCK_POCKET_H} x {PLANCK_POCKET_D} mm")
print(f"Cable channel (left wall): {planck_x} x {CABLE_CH_W} x {CABLE_CH_H} mm at y={cable_ch_y:.1f}")
print(f"Rear inserts: (x=17,z=18) and (x=90,z=18), depth={INSERT_DEPTH}mm")
print(f"Throat cut: x={planck_x}..{PANEL_W}, y=0..{planck_y:.2f}, z={pocket_z}..{PANEL_T} mm")
print(f"Alignment pin: seam face x={PANEL_W}, y=120, z=18, depth={PIN_DEPTH}mm")
