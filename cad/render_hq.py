"""
High-quality chassis render using pyrender (EGL offscreen).
Generates a 4-view composite: front-iso, rear-iso, front face, top-down.
"""
import os
os.environ["PYOPENGL_PLATFORM"] = "egl"

import numpy as np
import trimesh
import pyrender
from PIL import Image, ImageDraw, ImageFont

STL_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chassis_hq.png")

# Chassis geometry
ROW_EF_Z  = 0.0
ROW_CD_Z  = 40.0
ROW_AB_Z  = 76.0
CHASSIS_W = 305.0
CHASSIS_D = 136.7
CHASSIS_H = 138.0

# mm → metres for pyrender
S = 0.001

PANELS = [
    ("panel_e.stl", [0,       0, ROW_EF_Z]),
    ("panel_f.stl", [152.5,   0, ROW_EF_Z]),
    ("panel_c.stl", [0,       0, ROW_CD_Z]),
    ("panel_d.stl", [152.5,   0, ROW_CD_Z]),
    ("panel_a.stl", [0,       0, ROW_AB_Z]),
    ("panel_b.stl", [152.5,   0, ROW_AB_Z]),
    ("rear_wall.stl", [0,     136.7, 0]),
]

# Single material — dark grey PLA-like
MATERIAL = pyrender.MetallicRoughnessMaterial(
    baseColorFactor=[0.30, 0.30, 0.32, 1.0],
    metallicFactor=0.04,
    roughnessFactor=0.80,
)

def load_panel(filename, translation):
    path = os.path.join(STL_DIR, filename)
    mesh = trimesh.load(path, force="mesh")
    mesh.apply_translation(translation)
    # scale to metres
    mesh.apply_scale(S)
    mesh.fix_normals()
    return pyrender.Mesh.from_trimesh(mesh, material=MATERIAL, smooth=True)

def look_at(eye, target, up=np.array([0, 0, 1])):
    """Return a 4x4 camera pose (OpenGL convention, camera looks -Z)."""
    eye    = np.array(eye,    dtype=float)
    target = np.array(target, dtype=float)
    up     = np.array(up,     dtype=float)
    f = target - eye;  f /= np.linalg.norm(f)   # forward (+Z into scene)
    r = np.cross(f, up); r /= np.linalg.norm(r)  # right
    u = np.cross(r, f)                             # up (recomputed)
    # OpenGL camera: looks down -Z, so flip forward
    pose = np.eye(4)
    pose[:3, 0] =  r
    pose[:3, 1] =  u
    pose[:3, 2] = -f   # camera -Z = scene forward
    pose[:3, 3] =  eye
    return pose

def render_view(meshes, eye_mm, target_mm, W=1200, H=800, fov_deg=35, up=(0,0,1)):
    scene = pyrender.Scene(
        bg_color=[0.06, 0.06, 0.08, 1.0],
        ambient_light=[0.35, 0.35, 0.37],
    )
    for m in meshes:
        scene.add(m)

    # Lights
    key   = pyrender.DirectionalLight(color=[1.00, 0.97, 0.92], intensity=6.0)
    fill  = pyrender.DirectionalLight(color=[0.70, 0.82, 1.00], intensity=2.5)
    back  = pyrender.DirectionalLight(color=[0.90, 0.92, 1.00], intensity=1.5)
    rim   = pyrender.DirectionalLight(color=[1.00, 0.95, 0.85], intensity=1.0)

    cx, cy, cz = (CHASSIS_W/2*S, CHASSIS_D/2*S, CHASSIS_H/2*S)
    scene.add(key,  pose=look_at([cx-0.5, cy-0.9, cz+1.1], [cx, cy, cz]))
    scene.add(fill, pose=look_at([cx+1.0, cy-0.2, cz+0.4], [cx, cy, cz]))
    scene.add(back, pose=look_at([cx+0.3, cy+1.0, cz+0.7], [cx, cy, cz]))
    scene.add(rim,  pose=look_at([cx-0.2, cy-0.5, cz-0.5], [cx, cy, cz]))

    # Camera
    cam  = pyrender.PerspectiveCamera(yfov=np.radians(fov_deg), aspectRatio=W/H)
    eye_m    = np.array(eye_mm)    * S
    target_m = np.array(target_mm) * S
    scene.add(cam, pose=look_at(eye_m, target_m, up=np.array(up)*1.0))

    renderer = pyrender.OffscreenRenderer(W, H,
                                          point_size=1.0)
    color, _ = renderer.render(scene, flags=pyrender.RenderFlags.RGBA)
    renderer.delete()
    return Image.fromarray(color, "RGBA")

def main():
    print("Loading meshes…")
    meshes = [load_panel(f, t) for f, t in PANELS]

    cx = CHASSIS_W / 2
    cy = CHASSIS_D / 2
    cz = CHASSIS_H / 2

    print("Rendering views…")

    views = [
        # (label, eye_mm, target_mm, fov, up)
        ("Front / Left  (user view)",
         [cx - 380, cy - 560, cz + 310],
         [cx, cy, cz + 10], 34, (0, 0, 1)),

        ("Rear / Right  (back panel + vent)",
         [cx + 420, cy + 530, cz + 280],
         [cx, cy, cz + 10], 34, (0, 0, 1)),

        ("Front face  (panel structure)",
         [cx, cy - 600, cz + 40],
         [cx, cy, cz + 20], 30, (0, 0, 1)),

        ("Top down  (Go cradle open)",
         [cx + 30, cy, cz + 550],
         [cx, cy, cz + 40], 34, (0, -1, 0)),
    ]

    W, H = 1100, 750
    imgs = []
    for label, eye, target, fov, up in views:
        print(f"  {label}…")
        img = render_view(meshes, eye, target, W, H, fov, up)
        imgs.append((label, img))

    # Composite: 2×2 grid
    GW, GH = W * 2 + 6, H * 2 + 6 + 60
    canvas = Image.new("RGBA", (GW, GH), (12, 12, 16, 255))

    positions = [(0, 60), (W + 6, 60), (0, H + 66), (W + 6, H + 66)]
    for (label, img), (px, py) in zip(imgs, positions):
        canvas.paste(img, (px, py))
        draw = ImageDraw.Draw(canvas)
        draw.rectangle([px, py, px + W - 1, py + 20], fill=(0, 0, 0, 160))
        draw.text((px + 8, py + 4), label, fill=(200, 200, 210))

    # Title bar
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 0, GW, 54], fill=(18, 18, 22, 255))
    draw.text((GW // 2 - 180, 14),
              "Cyberdeck Chassis  —  Assembly Preview",
              fill=(210, 210, 220))
    draw.text((GW // 2 - 130, 34),
              "305 × 136.7 × 138 mm  |  6 panels + rear wall  |  15° screen tilt",
              fill=(130, 130, 145))

    canvas = canvas.convert("RGB")
    canvas.save(OUT_PATH, dpi=(150, 150))
    print(f"\nSaved: {OUT_PATH}")

if __name__ == "__main__":
    main()
