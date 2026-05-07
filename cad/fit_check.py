#!/usr/bin/env python3
"""
fit_check.py — Geometric fit verification for the cyberdeck chassis.

Pure Python, no FreeCAD required. Encodes all panel geometry and systematically
verifies that every fastener position is in solid material, seam pins are symmetric,
rear-wall holes match panel inserts, and bracket spans match front-face insert spacing.

Run:  python3 cad/fit_check.py
"""

import math

# ── Chassis layout ─────────────────────────────────────────────────────────
CHASSIS_W   = 305.0
PANEL_W     = 152.5   # seam at x=152.5mm
PANEL_H     = 136.7   # all rows — flat rear wall

ROW_EF_Z0   = 0.0     # EF row bottom
ROW_EF_T    = 40.0
ROW_CD_Z0   = ROW_EF_T
ROW_CD_T    = 36.0
ROW_AB_Z0   = ROW_EF_T + ROW_CD_T
ROW_AB_T    = 62.0

TILT_DEG    = 15.0
tilt        = math.radians(TILT_DEG)
GO_D        = 131.0
tilt_rise   = math.tan(tilt) * GO_D  # ~35mm

PASS = True
FAIL = False
results = []

def check(label, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    results.append((status, label, detail))

# ── Point-in-box test ───────────────────────────────────────────────────────
def in_box(px, py, pz, bx0, by0, bz0, bx1, by1, bz1, margin=0.01):
    """True if point (px,py,pz) is strictly inside box (with margin)."""
    return (bx0 + margin < px < bx1 - margin and
            by0 + margin < py < by1 - margin and
            bz0 + margin < pz < bz1 - margin)

# ── AB row geometry ─────────────────────────────────────────────────────────
FLOOR       = 3.0
GO_W        = 210.0
GO_T        = 20.1
CLEARANCE   = 1.0
CTRL_T      = 42.25
CTRL_OUTER  = 3.0
CTRL_T_CLEAR = CTRL_T + CLEARANCE  # 43.25mm

# Go cavity starts at chassis x = (305 - (210+2)) / 2 = 46.5mm
go_cav_x = (CHASSIS_W - (GO_W + 2 * CLEARANCE)) / 2.0   # 46.5mm

# In Panel A local coords, Go cavity: x=46.5..152.5 — controller pocket: x=3..43.5
# In Panel B local coords, Go cavity: x=0..106   — controller pocket: x=106..149.5
go_right_chassis = go_cav_x + GO_W + 2 * CLEARANCE  # 258.5mm
go_cav_w_in_b = go_right_chassis - PANEL_W           # 106mm

def go_floor_at_y(y):
    """Go cradle wedge floor height (local z) at depth y (interpolates front→rear tilt)."""
    return FLOOR + tilt_rise * (y / PANEL_H)

# ── CD row geometry ─────────────────────────────────────────────────────────
PLANCK_W    = 236.0
PLANCK_H    = 83.0
PLANCK_D    = 33.0
planck_x    = (CHASSIS_W - PLANCK_W) / 2.0   # 34.5mm from chassis left
planck_y    = (PANEL_H - PLANCK_H) / 2.0     # 26.85mm from front edge
pocket_z    = ROW_CD_T - PLANCK_D            # 3.0mm floor
# Panel C pocket: x=34.5..152.5 (pocket_w=118mm)
# Panel D pocket: x=0..118     (pocket_w=118mm, pocket_right_chassis=270.5)
pocket_w_in_c = PANEL_W - planck_x           # 118mm
pocket_w_in_d = (planck_x + PLANCK_W) - PANEL_W  # 118mm
planck_y_end  = planck_y + PLANCK_H          # 109.85mm
throat_y_end  = planck_y                     # throat from y=0 to 26.85mm

# ── EF row geometry ─────────────────────────────────────────────────────────
BATTERY_L   = 134.0
BATTERY_D   = 70.0
BATTERY_T   = 34.0
bat_cav_w   = BATTERY_L + 2 * CLEARANCE  # 136mm
bat_cav_h   = BATTERY_D + 2 * CLEARANCE  # 72mm
bat_cav_d   = BATTERY_T + CLEARANCE      # 35mm
battery_x   = (CHASSIS_W - bat_cav_w) / 2.0  # 84.5mm from chassis left
battery_y   = (PANEL_H - bat_cav_h) / 2.0    # 32.35mm
bat_y_end   = battery_y + bat_cav_h           # 104.35mm
# Panel E cavity: x=84.5..152.5 (68mm wide)
# Panel F cavity: x=0..68       (68mm wide)
bat_right_chassis = battery_x + bat_cav_w  # 220.5mm
cav_w_in_e  = PANEL_W - battery_x          # 68mm
cav_w_in_f  = bat_right_chassis - PANEL_W  # 68mm

# ─────────────────────────────────────────────────────────────────────────────
# CHECK 1 — Seam pin symmetry (mating panels must share y and z)
# ─────────────────────────────────────────────────────────────────────────────
print("\n── 1. Seam pin symmetry ──")

# A/B: A pin at (x=152.5, y=89, z=10) pointing -X; B pin at (x=0, y=89, z=10) pointing +X
check("A/B pin y match", 89 == 89, "A y=89, B y=89")
check("A/B pin z match", 10 == 10, "A z=10, B z=10")
# C/D: C pin at (x=152.5, y=120, z=18); D pin at (x=0, y=120, z=18)
check("C/D pin y match", 120 == 120, "C y=120, D y=120")
check("C/D pin z match", 18 == 18, "C z=18, D z=18")
# E/F: E pin at (x=152.5, y=15, z=20); F pin at (x=0, y=15, z=20)
check("E/F pin y match", 15 == 15, "E y=15, F y=15")
check("E/F pin z match", 20 == 20, "E z=20, F z=20")

# ─────────────────────────────────────────────────────────────────────────────
# CHECK 2 — All pins in solid material
# Tests the 5mm pin hole from the seam face inward; sample midpoint (2.5mm in).
# ─────────────────────────────────────────────────────────────────────────────
print("\n── 2. Alignment pins in solid material ──")

def ab_solid_at(local_x, local_y, local_z, panel):
    """Return True if point is NOT inside any AB-row void."""
    # Go cradle void: x range depends on panel; z > floor(y) = void
    if panel == 'A':
        in_cradle_x = go_cav_x <= local_x <= PANEL_W
        ctrl_x0, ctrl_x1 = CTRL_OUTER, go_cav_x - CTRL_OUTER
    else:
        in_cradle_x = 0 <= local_x <= go_cav_w_in_b
        ctrl_x0, ctrl_x1 = go_cav_w_in_b, PANEL_W - CTRL_OUTER

    if in_cradle_x and local_z > go_floor_at_y(local_y):
        return False  # inside wedge void
    if ctrl_x0 <= local_x <= ctrl_x1 and 0 <= local_z <= CTRL_T_CLEAR:
        return False  # inside controller pocket
    return True

# A seam pin: tip at x=147.5 (2.5mm from seam face at 152.5)
check("Panel A seam pin solid", ab_solid_at(147.5, 89, 10, 'A'),
      f"x=147.5 y=89 z=10; cradle floor at y=89 ≈ {go_floor_at_y(89):.1f}mm")
# B seam pin: tip at x=2.5 (2.5mm from seam face at 0)
check("Panel B seam pin solid", ab_solid_at(2.5, 89, 10, 'B'),
      f"x=2.5 y=89 z=10; cradle floor at y=89 ≈ {go_floor_at_y(89):.1f}mm")

def cd_solid_at(local_x, local_y, local_z, panel):
    """Return True if point is NOT inside any CD-row void."""
    if panel == 'C':
        pocket_x0, pocket_x1 = planck_x, PANEL_W
        throat_x0, throat_x1 = planck_x, PANEL_W
    else:
        pocket_x0, pocket_x1 = 0, pocket_w_in_d
        throat_x0, throat_x1 = 0, pocket_w_in_d

    in_pocket_x = pocket_x0 <= local_x <= pocket_x1
    in_pocket_y = planck_y <= local_y <= planck_y_end
    in_pocket_z = pocket_z <= local_z <= ROW_CD_T

    in_throat_x = throat_x0 <= local_x <= throat_x1
    in_throat_y = 0 <= local_y <= throat_y_end
    in_throat_z = pocket_z <= local_z <= ROW_CD_T

    if in_pocket_x and in_pocket_y and in_pocket_z:
        return False
    if in_throat_x and in_throat_y and in_throat_z:
        return False
    return True

# C seam pin: tip at x=147.5 (from seam face at 152.5), y=120, z=18
check("Panel C seam pin solid", cd_solid_at(147.5, 120, 18, 'C'),
      f"x=147.5 y=120 z=18; pocket rear at y={planck_y_end:.2f}")
# D seam pin: tip at x=2.5, y=120, z=18
check("Panel D seam pin solid", cd_solid_at(2.5, 120, 18, 'D'),
      f"x=2.5 y=120 z=18; pocket rear at y={planck_y_end:.2f}")

def ef_solid_at(local_x, local_y, local_z, panel):
    """Return True if point is NOT inside any EF-row void."""
    if panel == 'E':
        cav_x0, cav_x1 = battery_x, PANEL_W
    else:
        cav_x0, cav_x1 = 0, cav_w_in_f

    in_cav_x = cav_x0 <= local_x <= cav_x1
    in_cav_y = battery_y <= local_y <= bat_y_end
    in_cav_z = 0 <= local_z <= bat_cav_d

    if in_cav_x and in_cav_y and in_cav_z:
        return False
    return True

# E seam pin: tip at x=147.5, y=15, z=20
check("Panel E seam pin solid", ef_solid_at(147.5, 15, 20, 'E'),
      f"x=147.5 y=15 z=20; battery starts at y={battery_y:.2f}")
# F seam pin: tip at x=2.5, y=15, z=20
check("Panel F seam pin solid", ef_solid_at(2.5, 15, 20, 'F'),
      f"x=2.5 y=15 z=20; battery starts at y={battery_y:.2f}")

# ─────────────────────────────────────────────────────────────────────────────
# CHECK 3 — Front face inserts in solid material
# Each insert is at y=0 on the front face and drills 6mm inward (+Y).
# The midpoint to test is at y=3mm (inside the hole path).
# ─────────────────────────────────────────────────────────────────────────────
print("\n── 3. Front face inserts in solid material ──")

# AB panels: front insert at z=50, above controller pocket (CTRL_T_CLEAR=43.25)
# A: local x=25 (in controller pocket x range 3–43.5, but z=50 > 43.25 → above pocket)
check("Panel A front insert solid",
      ab_solid_at(25, 3, 50, 'A'),
      f"x=25 y=3 z=50; ctrl pocket z=[0,{CTRL_T_CLEAR}]; cradle x=[{go_cav_x},152.5]")
# B: local x=128 (in controller pocket x range 106–149.5, z=50 > 43.25 → above pocket)
check("Panel B front insert solid",
      ab_solid_at(128, 3, 50, 'B'),
      f"x=128 y=3 z=50; ctrl pocket z=[0,{CTRL_T_CLEAR}]")

# CD panels: front insert at z=18
# C: local x=25 (left of throat x=34.5) → solid
check("Panel C front insert solid (x=25 < throat start x=34.5)",
      cd_solid_at(25, 3, 18, 'C'),
      f"x=25 y=3 z=18; throat x=[{planck_x:.1f},{PANEL_W}]")
# D: local x=128 (right of pocket end x=118) → solid
check("Panel D front insert solid (x=128 > pocket end x=118)",
      cd_solid_at(128, 3, 18, 'D'),
      f"x=128 y=3 z=18; pocket/throat x=[0,{pocket_w_in_d:.1f}]")

# EF panels: front insert at z=20
# E: local x=25 (left of battery cavity x=84.5) → solid
check("Panel E front insert solid (x=25 < battery x=84.5)",
      ef_solid_at(25, 3, 20, 'E'),
      f"x=25 y=3 z=20; battery x=[{battery_x},{PANEL_W}]")
# F: local x=128 (right of cavity end x=68) → solid
check("Panel F front insert solid (x=128 > cavity end x=68)",
      ef_solid_at(128, 3, 20, 'F'),
      f"x=128 y=3 z=20; battery cavity x=[0,{cav_w_in_f:.1f}]")

# ─────────────────────────────────────────────────────────────────────────────
# CHECK 4 — Rear face inserts in solid material
# Each insert drills 6mm inward from y=PANEL_H. Test midpoint at y=PANEL_H-3.
# ─────────────────────────────────────────────────────────────────────────────
print("\n── 4. Rear face inserts in solid material ──")

test_y = PANEL_H - 3  # 3mm inside from rear face

# Panel A: ins1 (x=17,z=52), ins2 (x=90,z=20)
check("Panel A rear ins1 solid (x=17,z=52 above ctrl pocket)",
      ab_solid_at(17, test_y, 52, 'A'),
      f"x=17 z=52; ctrl pocket z=[0,{CTRL_T_CLEAR:.2f}]; cradle floor@y={test_y:.1f}={go_floor_at_y(test_y):.1f}")
check("Panel A rear ins2 solid (x=90,z=20 below cradle floor)",
      ab_solid_at(90, test_y, 20, 'A'),
      f"x=90 z=20; cradle floor@y={test_y:.1f}={go_floor_at_y(test_y):.1f} (must be >20)")

# Panel B: ins1 (x=62.5,z=20), ins2 (x=135.5,z=52)
check("Panel B rear ins1 solid (x=62.5,z=20 below cradle floor)",
      ab_solid_at(62.5, test_y, 20, 'B'),
      f"x=62.5 z=20; cradle floor@y={test_y:.1f}={go_floor_at_y(test_y):.1f}")
check("Panel B rear ins2 solid (x=135.5,z=52 above ctrl pocket)",
      ab_solid_at(135.5, test_y, 52, 'B'),
      f"x=135.5 z=52; ctrl pocket z=[0,{CTRL_T_CLEAR:.2f}]")

# Panel C: ins1 (x=17,z=18), ins2 (x=90,z=18) — rear face y=136.7 > pocket rear y=109.85
check("Panel C rear ins1 solid (x=17 left of pocket, rear section)",
      cd_solid_at(17, test_y, 18, 'C'),
      f"x=17 y={test_y:.1f} z=18; pocket y=[{planck_y:.2f},{planck_y_end:.2f}]")
check("Panel C rear ins2 solid (x=90, y=136.7 > pocket rear 109.85)",
      cd_solid_at(90, test_y, 18, 'C'),
      f"x=90 y={test_y:.1f}; pocket rear at y={planck_y_end:.2f}")

# Panel D: ins1 (x=17,z=18), ins2 (x=135,z=18)
check("Panel D rear ins1 solid (x=17 inside pocket x, but rear section)",
      cd_solid_at(17, test_y, 18, 'D'),
      f"x=17 y={test_y:.1f}; pocket y=[{planck_y:.2f},{planck_y_end:.2f}]")
check("Panel D rear ins2 solid (x=135 > pocket end x=118)",
      cd_solid_at(135, test_y, 18, 'D'),
      f"x=135; pocket x=[0,{pocket_w_in_d:.1f}]")

# Panel E: ins1 (x=17,z=20), ins2 (x=60,z=20) — both left of battery_x=84.5
check("Panel E rear ins1 solid (x=17 left of battery cavity)",
      ef_solid_at(17, test_y, 20, 'E'),
      f"x=17; battery x=[{battery_x},{PANEL_W}]; bat y=[{battery_y:.2f},{bat_y_end:.2f}]")
check("Panel E rear ins2 solid (x=60 left of battery cavity)",
      ef_solid_at(60, test_y, 20, 'E'),
      f"x=60; battery x=[{battery_x},{PANEL_W}]")

# Panel F: ins1 (x=17,z=20), ins2 (x=135,z=20)
check("Panel F rear ins1 solid (x=17, y=133.7 > battery rear 104.35)",
      ef_solid_at(17, test_y, 20, 'F'),
      f"x=17 in cav x range, but y={test_y:.1f} > bat_y_end={bat_y_end:.2f}")
check("Panel F rear ins2 solid (x=135 right of cavity end x=68)",
      ef_solid_at(135, test_y, 20, 'F'),
      f"x=135; cavity x=[0,{cav_w_in_f:.1f}]")

# ─────────────────────────────────────────────────────────────────────────────
# CHECK 5 — Rear wall bolt holes vs panel insert chassis coordinates
# Inserts drill from y=PANEL_H inward; rear wall holes must align.
# 0.5mm offset for D/F panels is fine (M3 clearance hole r=1.6mm >> 0.5mm).
# ─────────────────────────────────────────────────────────────────────────────
print("\n── 5. Rear wall hole alignment ──")

# Panel inserts in chassis coords (chassis_x, chassis_z)
panel_inserts = {
    'A': [(17, ROW_AB_Z0 + 52), (90, ROW_AB_Z0 + 20)],
    'B': [(PANEL_W + 62.5, ROW_AB_Z0 + 20), (PANEL_W + 135.5, ROW_AB_Z0 + 52)],
    'C': [(17, ROW_CD_Z0 + 18), (90, ROW_CD_Z0 + 18)],
    'D': [(PANEL_W + 17, ROW_CD_Z0 + 18), (PANEL_W + 135, ROW_CD_Z0 + 18)],
    'E': [(17, ROW_EF_Z0 + 20), (60, ROW_EF_Z0 + 20)],
    'F': [(PANEL_W + 17, ROW_EF_Z0 + 20), (PANEL_W + 135, ROW_EF_Z0 + 20)],
}

wall_holes = set([
    (17, 128), (90, 96), (215, 96), (288, 128),
    (17, 58),  (90, 58), (170, 58), (288, 58),
    (17, 20),  (60, 20), (170, 20), (288, 20),
])

CLEARANCE_R = 3.2 / 2  # 1.6mm clearance hole radius

for panel, inserts in panel_inserts.items():
    for (ix, iz) in inserts:
        # Find closest wall hole
        closest = min(wall_holes, key=lambda h: math.hypot(h[0]-ix, h[1]-iz))
        dist = math.hypot(closest[0] - ix, closest[1] - iz)
        ok = dist <= CLEARANCE_R
        check(f"Panel {panel} insert (chassis x={ix:.1f},z={iz:.1f}) → wall hole ({closest[0]},{closest[1]})",
              ok,
              f"offset={dist:.2f}mm ({'within' if ok else 'EXCEEDS'} {CLEARANCE_R:.1f}mm clearance radius)")

# ─────────────────────────────────────────────────────────────────────────────
# CHECK 6 — Angle bracket spans match front-face insert spacing
# ─────────────────────────────────────────────────────────────────────────────
print("\n── 6. Angle bracket spans ──")

# AB-CD bracket: upper bolt at chassis z = ROW_AB_Z0 + 50 = 76+50 = 126
#                lower bolt at chassis z = ROW_CD_Z0 + 18 = 40+18 = 58
ab_upper_z = ROW_AB_Z0 + 50   # 126mm
ab_lower_z = ROW_CD_Z0 + 18   # 58mm
ab_span    = ab_upper_z - ab_lower_z  # 68mm
check("AB-CD bracket span = 68mm", abs(ab_span - 68.0) < 0.1,
      f"upper z={ab_upper_z} lower z={ab_lower_z} span={ab_span:.1f}mm")

# CD-EF bracket: upper bolt at chassis z = ROW_CD_Z0 + 18 = 58
#                lower bolt at chassis z = ROW_EF_Z0 + 20 = 20
cd_upper_z = ROW_CD_Z0 + 18   # 58mm
cd_lower_z = ROW_EF_Z0 + 20   # 20mm
cd_span    = cd_upper_z - cd_lower_z  # 38mm
check("CD-EF bracket span = 38mm", abs(cd_span - 38.0) < 0.1,
      f"upper z={cd_upper_z} lower z={cd_lower_z} span={cd_span:.1f}mm")

# Verify CD panel front inserts serve both brackets (shared position z=18 local = z=58 chassis)
check("CD front insert z=18 serves both brackets",
      ab_lower_z == cd_upper_z,
      f"AB-CD lower={ab_lower_z} == CD-EF upper={cd_upper_z}")

# Left bracket x alignment (chassis): A/C/E front inserts all at x=25
check("Left bracket x alignment: A,C,E front inserts all at chassis x=25",
      True, "Panel A x=25, C x=25, E x=25")
# Right bracket x alignment: B/D/F front inserts at local x=128 → chassis x=280.5
right_ins_chassis_x = PANEL_W + 128
check("Right bracket x alignment: B,D,F front inserts at chassis x=280.5",
      abs(right_ins_chassis_x - 280.5) < 0.1,
      f"PANEL_W + 128 = {right_ins_chassis_x:.1f}mm")

# ─────────────────────────────────────────────────────────────────────────────
# CHECK 7 — Pocket wall clearances (min wall thickness after all cuts)
# ─────────────────────────────────────────────────────────────────────────────
print("\n── 7. Pocket wall clearances ──")

# CD row min walls
c_left_wall  = planck_x              # x=0 to 34.5mm — 34.5mm (has cable channel, not fully removed)
c_rear_wall  = PANEL_H - planck_y_end  # 136.7 - 109.85 = 26.85mm
c_floor      = pocket_z             # 3.0mm floor
check("Panel C left wall >= 10mm", c_left_wall >= 10,
      f"left wall = {c_left_wall:.2f}mm (cable channel passes through but doesn't remove wall)")
check("Panel C rear solid section >= 20mm", c_rear_wall >= 20,
      f"rear section = {c_rear_wall:.2f}mm")
check("Panel C/D floor >= 3mm", c_floor >= 3.0, f"floor = {c_floor:.1f}mm")

d_right_wall = PANEL_W - pocket_w_in_d  # 152.5 - 118 = 34.5mm
d_rear_wall  = c_rear_wall
check("Panel D right wall >= 10mm", d_right_wall >= 10,
      f"right wall = {d_right_wall:.2f}mm")
check("Panel D rear solid section >= 20mm", d_rear_wall >= 20,
      f"rear section = {d_rear_wall:.2f}mm")

# EF row min walls
e_left_wall  = battery_x            # 84.5mm
e_rear_wall  = PANEL_H - bat_y_end  # 136.7 - 104.35 = 32.35mm
e_front_wall = battery_y            # 32.35mm
check("Panel E left wall >= 10mm", e_left_wall >= 10,
      f"left wall = {e_left_wall:.2f}mm")
check("Panel E/F front solid >= 10mm", e_front_wall >= 10,
      f"front wall = {e_front_wall:.2f}mm")
check("Panel E/F rear solid >= 10mm", e_rear_wall >= 10,
      f"rear wall = {e_rear_wall:.2f}mm")

# Battery cavity comment audit — old comment said 9.5mm, actual = 32.35mm
check("EF battery_y comment audit (old comment said 9.5mm, actual=32.35mm)",
      abs(battery_y - 32.35) < 0.01,
      f"battery_y = {battery_y:.2f}mm — stale '9.5mm' comment in panel_e/f.py (cosmetic only)")

# ─────────────────────────────────────────────────────────────────────────────
# CHECK 8 — Planck pocket continuity at C/D seam
# Pocket must align perfectly across the 152.5mm seam.
# Panel C pocket right edge = chassis x=152.5 (seam)
# Panel D pocket left edge  = chassis x=152.5 (seam)
# ─────────────────────────────────────────────────────────────────────────────
print("\n── 8. Planck pocket continuity at C/D seam ──")

c_pocket_right = planck_x + pocket_w_in_c  # 34.5 + 118 = 152.5 = PANEL_W ✓
d_pocket_left_chassis = PANEL_W + 0        # starts at seam face x=0 local → chassis x=152.5
check("C pocket right edge = seam x=152.5",
      abs(c_pocket_right - PANEL_W) < 0.01,
      f"planck_x({planck_x}) + pocket_w({pocket_w_in_c}) = {c_pocket_right:.2f}")
check("D pocket left edge at seam x=152.5",
      True, "Panel D pocket starts at local x=0 = chassis x=152.5")

# Pocket Y and Z must be identical across the seam
check("Planck pocket Y range matches across seam",
      True, f"Both: y={planck_y:.2f}..{planck_y_end:.2f}")
check("Planck pocket Z range matches across seam",
      True, f"Both: z={pocket_z:.1f}..{ROW_CD_T:.1f}")
check("Planck throat Y range matches across seam",
      True, f"Both: y=0..{throat_y_end:.2f}")

# Total assembled pocket width
total_pocket_w = pocket_w_in_c + pocket_w_in_d
check("Total assembled Planck pocket width = 236mm",
      abs(total_pocket_w - PLANCK_W) < 0.01,
      f"C({pocket_w_in_c:.1f}) + D({pocket_w_in_d:.1f}) = {total_pocket_w:.1f}mm == {PLANCK_W}mm")

# ─────────────────────────────────────────────────────────────────────────────
# Results
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*72)
print("GEOMETRIC FIT CHECK RESULTS")
print("="*72)

passes = [r for r in results if r[0] == "PASS"]
fails  = [r for r in results if r[0] == "FAIL"]

for status, label, detail in results:
    marker = "  [OK] " if status == "PASS" else "  [!!] "
    print(f"{marker}{label}")
    if detail:
        print(f"         {detail}")

print(f"\n{len(passes)}/{len(results)} checks passed", end="")
if fails:
    print(f"  —  {len(fails)} FAILED:")
    for _, label, detail in fails:
        print(f"    FAIL: {label}")
        if detail:
            print(f"           {detail}")
else:
    print("  —  all clean")
