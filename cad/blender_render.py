"""
Blender 5.x headless render — cyberdeck chassis assembly.
Run with: blender --background --python cad/blender_render.py

Renders 4 views with EEVEE, composites into a single PNG.
"""
import bpy
import os
import math
import sys
from mathutils import Vector, Matrix

# ── paths ──────────────────────────────────────────────────────────────────
CAD_DIR = os.path.dirname(os.path.abspath(__file__))
STL_DIR = os.path.join(CAD_DIR, "stl")
TMP_DIR = os.path.join(CAD_DIR, "_render_tmp")
OUT_PNG = os.path.join(CAD_DIR, "chassis_blender.png")
os.makedirs(TMP_DIR, exist_ok=True)

# ── chassis constants (mm → m) ──────────────────────────────────────────────
MM = 0.001

PANELS = [
    ("panel_e.stl", (0,       0,     0    )),
    ("panel_f.stl", (152.5,   0,     0    )),
    ("panel_c.stl", (0,       0,     40.0 )),
    ("panel_d.stl", (152.5,   0,     40.0 )),
    ("panel_a.stl", (0,       0,     76.0 )),
    ("panel_b.stl", (152.5,   0,     76.0 )),
    ("rear_wall.stl",(0,      136.7, 0    )),
]

CHASSIS_CENTER = Vector((152.5 * MM / 2, 136.7 * MM / 2, 138.0 * MM / 2))

# ── scene setup ────────────────────────────────────────────────────────────
def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=True)
    for col in bpy.data.collections:
        bpy.data.collections.remove(col)

def make_material():
    mat = bpy.data.materials.new("chassis_pla")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out   = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf  = nt.nodes.new("ShaderNodeBsdfPrincipled")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    bump  = nt.nodes.new("ShaderNodeBump")
    tc    = nt.nodes.new("ShaderNodeTexCoord")

    # Matte dark grey — PLA-like
    bsdf.inputs["Base Color"].default_value    = (0.28, 0.28, 0.30, 1.0)
    bsdf.inputs["Roughness"].default_value     = 0.82
    bsdf.inputs["Specular IOR Level"].default_value = 0.12

    # Subtle surface noise for micro-texture
    noise.inputs["Scale"].default_value  = 900.0
    noise.inputs["Detail"].default_value = 8.0
    noise.inputs["Roughness"].default_value = 0.7
    bump.inputs["Strength"].default_value = 0.04
    bump.inputs["Distance"].default_value = 0.001

    nt.links.new(tc.outputs["Object"],    noise.inputs["Vector"])
    nt.links.new(noise.outputs["Fac"],    bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"],  bsdf.inputs["Normal"])
    nt.links.new(bsdf.outputs["BSDF"],    out.inputs["Surface"])

    out.location   = (300, 0)
    bsdf.location  = (0,   0)
    noise.location = (-300, -150)
    bump.location  = (-100, -150)
    tc.location    = (-500, -150)
    return mat

def import_panels(mat):
    objects = []
    for filename, (tx, ty, tz) in PANELS:
        filepath = os.path.join(STL_DIR, filename)
        bpy.ops.wm.stl_import(filepath=filepath)
        obj = bpy.context.selected_objects[0]
        obj.name = filename.replace(".stl", "")

        # STL is in mm; scale to metres and apply translation
        obj.scale = (MM, MM, MM)
        obj.location = Vector((tx * MM, ty * MM, tz * MM))
        bpy.ops.object.transform_apply(scale=True, location=False)

        # Apply Y→depth axis flip: our CAD Y = Blender Y (both front-to-back)
        # No flip needed — coordinate systems match.
        obj.data.materials.append(mat)
        objects.append(obj)

    # Join into single mesh for cleaner shading
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    chassis = bpy.context.active_object
    chassis.name = "Chassis"
    return chassis

def add_ground(z_offset=0.0):
    bpy.ops.mesh.primitive_plane_add(size=2.0, location=(CHASSIS_CENTER.x, CHASSIS_CENTER.y, z_offset))
    gnd = bpy.context.active_object
    gnd.name = "Ground"
    mat = bpy.data.materials.new("ground")
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.04, 0.04, 0.05, 1.0)
    bsdf.inputs["Roughness"].default_value  = 1.0
    bsdf.inputs["Specular IOR Level"].default_value = 0.0
    gnd.data.materials.append(mat)
    return gnd

def add_lights():
    cx, cy, cz = CHASSIS_CENTER

    lights = [
        # (name, type, energy, color, location)
        ("Key",   "AREA",  180, (1.00, 0.96, 0.90), (cx - 0.45, cy - 0.55, cz + 0.55)),
        ("Fill",  "AREA",   60, (0.75, 0.85, 1.00), (cx + 0.50, cy - 0.20, cz + 0.30)),
        ("Back",  "AREA",   40, (0.90, 0.92, 1.00), (cx + 0.10, cy + 0.55, cz + 0.45)),
        ("Rim",   "AREA",   25, (1.00, 0.98, 0.95), (cx - 0.20, cy + 0.40, cz - 0.10)),
    ]

    for name, ltype, energy, color, loc in lights:
        bpy.ops.object.light_add(type=ltype, location=loc)
        light = bpy.context.active_object
        light.name = name
        light.data.energy = energy
        light.data.color  = color
        light.data.size   = 0.3
        # Point toward chassis center
        direction = Vector(loc) - CHASSIS_CENTER
        rot = direction.to_track_quat("Z", "Y")
        light.rotation_euler = rot.to_euler()

def setup_world():
    world = bpy.data.worlds["World"]
    world.use_nodes = True
    nt = world.node_tree
    bg = nt.nodes["Background"]
    bg.inputs["Color"].default_value   = (0.02, 0.02, 0.025, 1.0)
    bg.inputs["Strength"].default_value = 1.0

def setup_render(W=1200, H=800, samples=64):
    scene = bpy.context.scene
    scene.render.engine       = "BLENDER_EEVEE"
    scene.render.resolution_x = W
    scene.render.resolution_y = H
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode  = "RGBA"

    eevee = scene.eevee
    eevee.taa_render_samples     = samples
    eevee.use_fast_gi             = True
    eevee.direct_light_intensity  = 1.0
    eevee.indirect_light_intensity = 1.0

def place_camera(eye: Vector, target: Vector, fov_deg=38.0):
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens_unit = "FOV"
    cam_data.angle     = math.radians(fov_deg)
    cam_data.clip_end  = 10.0

    cam_obj = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    cam_obj.location = eye

    # Point camera at target
    direction = (target - eye).normalized()
    quat = direction.to_track_quat("-Z", "Y")
    cam_obj.rotation_euler = quat.to_euler()
    return cam_obj

def render_view(eye_mm, target_mm, fov, name):
    # Remove old cameras
    for obj in bpy.data.objects:
        if obj.type == "CAMERA":
            bpy.data.objects.remove(obj, do_unlink=True)

    eye    = Vector(v * MM for v in eye_mm)
    target = Vector(v * MM for v in target_mm)
    place_camera(eye, target, fov)

    outpath = os.path.join(TMP_DIR, f"{name}.png")
    bpy.context.scene.render.filepath = outpath
    bpy.ops.render.render(write_still=True)
    print(f"  rendered: {outpath}")
    return outpath

# ── main ───────────────────────────────────────────────────────────────────
print("\n=== Cyberdeck Blender Render ===")

clear_scene()
setup_world()
mat     = make_material()
chassis = import_panels(mat)
add_ground(z_offset=-0.002)
add_lights()
setup_render(W=1280, H=860, samples=96)

cx, cy, cz = 152.5, 68.35, 69.0   # chassis centre (mm)

VIEWS = [
    # name, eye_mm, target_mm, fov
    ("front_iso",  (cx - 340, cy - 500, cz + 290), (cx, cy, cz + 10), 38),
    ("rear_iso",   (cx + 380, cy + 470, cz + 260), (cx, cy, cz + 10), 38),
    ("front_face", (cx,       cy - 560, cz + 30),  (cx, cy, cz + 20), 32),
    ("top_down",   (cx + 20,  cy - 20,  cz + 490), (cx, cy, cz + 30), 36),
]

paths = {}
for name, eye, target, fov in VIEWS:
    print(f"Rendering {name}…")
    paths[name] = render_view(eye, target, fov, name)

# ── composite with PIL ─────────────────────────────────────────────────────
from PIL import Image, ImageDraw

W, H   = 1280, 860
GAP    = 4
BAR_H  = 56
GW     = W * 2 + GAP
GH     = H * 2 + GAP + BAR_H

canvas = Image.new("RGB", (GW, GH), (10, 10, 12))
draw   = ImageDraw.Draw(canvas)

positions = {
    "front_iso":  (0,       BAR_H),
    "rear_iso":   (W + GAP, BAR_H),
    "front_face": (0,       BAR_H + H + GAP),
    "top_down":   (W + GAP, BAR_H + H + GAP),
}

labels = {
    "front_iso":  "Front / Left  (user view)",
    "rear_iso":   "Rear / Right  (back panel + vent)",
    "front_face": "Front face  (panel structure)",
    "top_down":   "Top down  (Go cradle open)",
}

for name, (px, py) in positions.items():
    img = Image.open(paths[name]).convert("RGB")
    canvas.paste(img, (px, py))
    draw.rectangle([px, py, px + W - 1, py + 18], fill=(0, 0, 0))
    draw.text((px + 8, py + 3), labels[name], fill=(190, 190, 200))

# Title bar
draw.rectangle([0, 0, GW, BAR_H - 1], fill=(14, 14, 18))
draw.text((20, 10),  "Cyberdeck Chassis — Blender Assembly Render", fill=(215, 215, 225))
draw.text((20, 30), "305 × 136.7 × 138 mm   6 panels + rear wall   15° screen tilt", fill=(120, 120, 135))

canvas.save(OUT_PNG)
print(f"\nComposite saved: {OUT_PNG}")

# clean up tmp
import shutil
shutil.rmtree(TMP_DIR)
