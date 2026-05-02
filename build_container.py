"""
Build a 20ft ISO shipping container in Blender with mural textures
applied to: front (long side), both end caps. Back long side + roof + floor
are matte container-paint colour.

Run: blender -b -P build_container.py -- <front_texture> <output.glb>
"""
import bpy
import sys
import os
import math
from mathutils import Vector

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
if len(argv) < 2:
    print("usage: ... -- <front_texture.jpg> <output.glb>")
    sys.exit(1)

FRONT_TEX = os.path.abspath(argv[0])
OUTPUT = os.path.abspath(argv[1])
END_TEX = os.path.abspath(os.path.join(os.path.dirname(__file__), "textures", "mural-3-square.jpg"))

# ISO 20ft external dims (metres)
L = 6.058   # length (X)
W = 2.438   # width  (Y)
H = 2.591   # height (Z)

# wipe scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# --- Container shell as 6 separate flat planes so each can carry its own material cleanly ---

def make_plane(name, verts, uvs):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
    mesh.update()
    uv_layer = mesh.uv_layers.new(name="UVMap")
    for i, uv in enumerate(uvs):
        uv_layer.data[i].uv = uv
    return obj


# faces (verts in CCW from outside)
# Front (long side, -Y in Blender → +Z in glTF, faces default camera) — landscape mural
front = make_plane(
    "FrontPanel",
    [(+L/2, -W/2, 0), (-L/2, -W/2, 0), (-L/2, -W/2, H), (+L/2, -W/2, H)],
    [(1, 0), (0, 0), (0, 1), (1, 1)],
)
# Back (long side, +Y) — solid colour
back = make_plane(
    "BackPanel",
    [(-L/2, +W/2, 0), (+L/2, +W/2, 0), (+L/2, +W/2, H), (-L/2, +W/2, H)],
    [(1, 0), (0, 0), (0, 1), (1, 1)],
)
# Left end (-X) — square mural
end_left = make_plane(
    "EndLeftPanel",
    [(-L/2, -W/2, 0), (-L/2, +W/2, 0), (-L/2, +W/2, H), (-L/2, -W/2, H)],
    [(1, 0), (0, 0), (0, 1), (1, 1)],
)
# Right end (+X) — square mural
end_right = make_plane(
    "EndRightPanel",
    [(+L/2, +W/2, 0), (+L/2, -W/2, 0), (+L/2, -W/2, H), (+L/2, +W/2, H)],
    [(1, 0), (0, 0), (0, 1), (1, 1)],
)
# Roof (+Z) — solid colour
roof = make_plane(
    "RoofPanel",
    [(-L/2, +W/2, H), (+L/2, +W/2, H), (+L/2, -W/2, H), (-L/2, -W/2, H)],
    [(1, 0), (0, 0), (0, 1), (1, 1)],
)
# Floor (-Z) — solid colour (rarely seen but close it for proper occlusion)
floor = make_plane(
    "FloorPanel",
    [(-L/2, -W/2, 0), (+L/2, -W/2, 0), (+L/2, +W/2, 0), (-L/2, +W/2, 0)],
    [(1, 0), (0, 0), (0, 1), (1, 1)],
)


def make_image_material(name, image_path):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.85
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(image_path)
    tex.image.colorspace_settings.name = "sRGB"
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    return mat


def make_solid_material(name, rgb, roughness=0.6):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    return mat


# Reference container colour (typical sun-bleached storage container blue-grey)
mat_metal = make_solid_material("ContainerMetal", (0.42, 0.47, 0.50))
mat_floor = make_solid_material("ContainerUnder", (0.18, 0.18, 0.18), roughness=0.9)
mat_front = make_image_material("Mural_Front", FRONT_TEX)
mat_end = make_image_material("Mural_End", END_TEX)

front.data.materials.append(mat_front)
back.data.materials.append(mat_metal)
end_left.data.materials.append(mat_end)
end_right.data.materials.append(mat_end)
roof.data.materials.append(mat_metal)
floor.data.materials.append(mat_floor)

# --- Ground plane (concrete-ish) ---
bpy.ops.mesh.primitive_plane_add(size=20.0, location=(0, 0, -0.01))
ground = bpy.context.active_object
ground.name = "Ground"
mat_ground = make_solid_material("Ground", (0.55, 0.55, 0.52), roughness=0.95)
ground.data.materials.append(mat_ground)

# --- Lights so the GLB has a fallback look even without env map ---
bpy.ops.object.light_add(type="SUN", location=(4, -4, 8))
sun = bpy.context.active_object
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(0), math.radians(-30))

# --- Export ---
# Select everything for export
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(
    filepath=OUTPUT,
    export_format="GLB",
    export_apply=True,
    export_lights=False,  # model-viewer brings its own lighting
    export_cameras=False,
)

print(f"\n[OK] wrote {OUTPUT}")
print(f"     front mural: {FRONT_TEX}")
print(f"     end mural:   {END_TEX}")
