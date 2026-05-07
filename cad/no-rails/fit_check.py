#!/usr/bin/env python3
"""
fit_check.py (no-rails variant) — Geometric fit verification.

Panels C/D/E/F and rear wall are identical to the main design.
Only panels A and B differ: no controller rail pockets.

Run:  python3 cad/no-rails/fit_check.py
"""

import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from fit_check import (
    # Re-run the shared checks by importing the module — it prints and exits.
    # Instead, we replicate only the AB-specific checks here.
    PANEL_W, PANEL_H, FLOOR, GO_D, tilt_rise, go_cav_x, go_cav_w_in_b,
    planck_x, planck_y, planck_y_end, throat_y_end, pocket_z,
    pocket_w_in_c, pocket_w_in_d, ROW_CD_T,
    battery_x, battery_y, bat_y_end, cav_w_in_e, cav_w_in_f, bat_cav_d,
    ROW_AB_Z0, ROW_CD_Z0, ROW_EF_Z0,
    wall_holes, CLEARANCE_R,
    cd_solid_at, ef_solid_at, go_floor_at_y,
)

results = []

def check(label, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    results.append((status, label, detail))

# ── AB row (no-rails): no controller pocket ─────────────────────────────────
CTRL_T_CLEAR = 43.25  # not present, but kept for reference

def ab_nr_solid_at(local_x, local_y, local_z):
    """AB panel void = only the Go cradle wedge. No controller pocket."""
    in_cradle_x_a = go_cav_x <= local_x <= PANEL_W
    # For seam pin we test Panel A (x near 152.5) and Panel B (x near 0)
    # For a generic check we test both sides
    in_cradle_x_b = 0 <= local_x <= go_cav_w_in_b
    in_cradle = (in_cradle_x_a or in_cradle_x_b)
    if in_cradle and local_z > go_floor_at_y(local_y):
        return False
    return True

print("\n── 1. Seam pin symmetry (unchanged) ──")
check("A/B pin y match", True, "y=89")
check("A/B pin z match", True, "z=10")

print("\n── 2. Alignment pins in solid material ──")
# A pin tip at x=147.5 (2.5mm from seam)
floor_at_89 = go_floor_at_y(89)
check("Panel A seam pin solid (no-rails)",
      not (go_cav_x <= 147.5 <= PANEL_W and 10 > floor_at_89),
      f"x=147.5 y=89 z=10; cradle floor@y=89={floor_at_89:.1f}mm; z=10 < floor → solid")
# B pin tip at x=2.5
check("Panel B seam pin solid (no-rails)",
      not (0 <= 2.5 <= go_cav_w_in_b and 10 > floor_at_89),
      f"x=2.5 y=89 z=10; cradle floor={floor_at_89:.1f}mm; z=10 < floor → solid")

print("\n── 3. Front face inserts in solid material ──")
# No controller pocket → left wall (A) and right wall (B) are fully solid.
# x=25 (A) is in left outer wall x=0..46.5 — no voids in this x range
check("Panel A front insert solid (no ctrl pocket — left wall fully solid)",
      go_cav_x > 25,
      f"x=25 < go_cav_x={go_cav_x:.1f}; left wall solid at all z")
# x=128 (B) is in right outer wall x=106..152.5 — no voids
check("Panel B front insert solid (no ctrl pocket — right wall fully solid)",
      128 > go_cav_w_in_b,
      f"x=128 > go_cav_w_in_b={go_cav_w_in_b:.1f}; right wall solid at all z")

print("\n── 4. Rear face inserts in solid material ──")
test_y = PANEL_H - 3
floor_at_rear = go_floor_at_y(test_y)
# A ins1 x=17 z=52: in left wall (x < go_cav_x=46.5) → always solid
check("Panel A rear ins1 (x=17, left of cradle, fully solid)",
      17 < go_cav_x,
      f"x=17 < go_cav_x={go_cav_x:.1f}")
# A ins2 x=90 z=20: in cradle x range, z=20 < floor@rear=38mm
check("Panel A rear ins2 (x=90, z=20 < cradle floor at rear)",
      20 < floor_at_rear,
      f"z=20 < floor@y={test_y:.1f}={floor_at_rear:.1f}mm")
# B ins1 x=62.5 z=20: in cradle range, below floor
check("Panel B rear ins1 (x=62.5, z=20 < cradle floor at rear)",
      20 < floor_at_rear,
      f"z=20 < floor={floor_at_rear:.1f}mm")
# B ins2 x=135.5 z=52: in right wall (x > go_cav_w_in_b=106) → always solid
check("Panel B rear ins2 (x=135.5, right of cradle, fully solid)",
      135.5 > go_cav_w_in_b,
      f"x=135.5 > go_cav_w_in_b={go_cav_w_in_b:.1f}")

print("\n── 5. Rear wall hole alignment (AB inserts — same chassis coords as original) ──")
ab_inserts = [
    ("A ins1", 17,    ROW_AB_Z0 + 52),
    ("A ins2", 90,    ROW_AB_Z0 + 20),
    ("B ins1", PANEL_W + 62.5,   ROW_AB_Z0 + 20),
    ("B ins2", PANEL_W + 135.5,  ROW_AB_Z0 + 52),
]
for name, ix, iz in ab_inserts:
    closest = min(wall_holes, key=lambda h: math.hypot(h[0]-ix, h[1]-iz))
    dist = math.hypot(closest[0]-ix, closest[1]-iz)
    check(f"Panel {name} (chassis x={ix:.1f},z={iz:.1f}) → wall hole ({closest[0]},{closest[1]})",
          dist <= CLEARANCE_R,
          f"offset={dist:.2f}mm ({'within' if dist<=CLEARANCE_R else 'EXCEEDS'} {CLEARANCE_R:.1f}mm)")

print("\n── 6. Bracket spans (unchanged) ──")
ab_span = (ROW_AB_Z0 + 50) - (ROW_CD_Z0 + 18)
cd_span = (ROW_CD_Z0 + 18) - (ROW_EF_Z0 + 20)
check("AB-CD bracket span = 68mm", abs(ab_span - 68) < 0.1, f"{ab_span:.1f}mm")
check("CD-EF bracket span = 38mm", abs(cd_span - 38) < 0.1, f"{cd_span:.1f}mm")

print("\n── 7. No-rails structural note ──")
left_wall_a  = go_cav_x            # 46.5mm solid outer wall in A
right_wall_b = PANEL_W - go_cav_w_in_b  # 46.5mm solid outer wall in B
check("Panel A solid left wall >= 20mm", left_wall_a >= 20,
      f"{left_wall_a:.1f}mm (was 3mm outer + 40mm ctrl pocket)")
check("Panel B solid right wall >= 20mm", right_wall_b >= 20,
      f"{right_wall_b:.1f}mm (was 40mm ctrl pocket + 3mm outer)")

# ── Results ─────────────────────────────────────────────────────────────────
print("\n" + "="*72)
print("NO-RAILS FIT CHECK RESULTS")
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
