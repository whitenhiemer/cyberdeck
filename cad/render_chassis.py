"""
Render assembled cyberdeck chassis from STL files using trimesh + matplotlib.
Panels positioned at their actual chassis coordinates, viewed from 3 angles.
"""
import trimesh
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import os

STL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")

# Row Z offsets in assembled chassis
ROW_EF_Z = 0       # Battery bay
ROW_CD_Z = 40      # Planck bay
ROW_AB_Z = 76      # Go cradle

# Each panel: (stl_filename, translation_xyz, color_rgba)
PANELS = [
    # Battery row
    ("panel_e.stl", [0,    0, ROW_EF_Z], [0.25, 0.45, 0.65, 0.85]),
    ("panel_f.stl", [152.5, 0, ROW_EF_Z], [0.25, 0.45, 0.65, 0.85]),
    # Planck row
    ("panel_c.stl", [0,    0, ROW_CD_Z], [0.30, 0.55, 0.40, 0.85]),
    ("panel_d.stl", [152.5, 0, ROW_CD_Z], [0.30, 0.55, 0.40, 0.85]),
    # Go cradle row
    ("panel_a.stl", [0,    0, ROW_AB_Z], [0.55, 0.35, 0.25, 0.85]),
    ("panel_b.stl", [152.5, 0, ROW_AB_Z], [0.55, 0.35, 0.25, 0.85]),
    # Rear wall: Y=PANEL_H from front face, X=0, Z=0
    ("rear_wall.stl", [0, 91, 0], [0.45, 0.45, 0.45, 0.70]),
]

def load_and_translate(stl_file, translation):
    path = os.path.join(STL_DIR, stl_file)
    mesh = trimesh.load(path)
    mesh.apply_translation(translation)
    return mesh

def tri_to_poly3d(mesh):
    verts = mesh.vertices
    faces = mesh.faces
    return verts[faces]

fig = plt.figure(figsize=(18, 12))
fig.patch.set_facecolor("#1a1a1a")

VIEWS = [
    ("Front (Y=0 face)",   25,  -90),
    ("Isometric",          30,  -50),
    ("Rear / top",         45,  130),
]

meshes_colors = []
for stl_file, trans, color in PANELS:
    try:
        m = load_and_translate(stl_file, trans)
        meshes_colors.append((m, color))
    except Exception as e:
        print(f"  skip {stl_file}: {e}")

for i, (title, elev, azim) in enumerate(VIEWS):
    ax = fig.add_subplot(1, 3, i + 1, projection="3d")
    ax.set_facecolor("#1a1a1a")

    for mesh, color in meshes_colors:
        polys = tri_to_poly3d(mesh)
        pc = Poly3DCollection(polys, alpha=color[3], linewidths=0)
        pc.set_facecolor(color[:3])
        ax.add_collection3d(pc)

    # Chassis bounding box approx: 305 x 91 x 138
    ax.set_xlim(0, 305)
    ax.set_ylim(0, 137)
    ax.set_zlim(0, 140)
    ax.set_box_aspect([305, 137, 140])

    ax.set_xlabel("X (mm)", color="grey", fontsize=7)
    ax.set_ylabel("Y (mm)", color="grey", fontsize=7)
    ax.set_zlabel("Z (mm)", color="grey", fontsize=7)
    ax.tick_params(colors="grey", labelsize=6)
    for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
        pane.fill = False
        pane.set_edgecolor("#333")
    ax.grid(True, color="#333", linewidth=0.4)

    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title, color="white", fontsize=10, pad=8)

legend_labels = [
    ("panel_a / panel_b  — Go cradle row",  [0.55, 0.35, 0.25]),
    ("panel_c / panel_d  — Planck/dock row", [0.30, 0.55, 0.40]),
    ("panel_e / panel_f  — Battery row",    [0.25, 0.45, 0.65]),
    ("rear_wall",                            [0.45, 0.45, 0.45]),
]
from matplotlib.patches import Patch
handles = [Patch(facecolor=c, label=l, alpha=0.85) for l, c in legend_labels]
fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=8,
           facecolor="#2a2a2a", edgecolor="#555", labelcolor="white",
           framealpha=0.9)

fig.suptitle("Cyberdeck Chassis — Panel Assembly Preview", color="white",
             fontsize=13, y=0.97)

out = os.path.join(os.path.dirname(STL_DIR), "chassis_preview.png")
plt.tight_layout(rect=[0, 0.06, 1, 0.96])
plt.savefig(out, dpi=150, facecolor=fig.get_facecolor())
print(f"Saved: {out}")
plt.show()
