import argparse
import math
import os
import random
import sys

import bpy
from mathutils import Vector

def args_after_separator():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="/workspace/renders")
    p.add_argument("--quality", choices=["draft", "standard", "high"], default="standard")
    p.add_argument("--title", default="NEON RUN")
    return p.parse_args(argv)

def mat(name, color, metallic=0.0, roughness=0.4, emission=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1)
    bs.inputs["Metallic"].default_value = metallic
    bs.inputs["Roughness"].default_value = roughness
    if emission:
        emission_color = bs.inputs.get("Emission Color") or bs.inputs.get("Emission")
        if emission_color:
            emission_color.default_value = (*color, 1)
        emission_strength = bs.inputs.get("Emission Strength")
        if emission_strength:
            emission_strength.default_value = emission
    return m

def cube(name, loc, scale, material, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        mod = o.modifiers.new("Soft machined edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
        o.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return o

def animate(obj, data):
    for frame, loc in data:
        obj.location = loc
        obj.keyframe_insert(data_path="location", frame=frame)

def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()

def main():
    a = args_after_separator()
    random.seed(23)
    os.makedirs(a.output, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    if a.quality == "draft":
        width, height, fps, samples = 640, 360, 8, 8
    elif a.quality == "high":
        width, height, fps, samples = 1280, 720, 12, 24
    else:
        width, height, fps, samples = 960, 540, 10, 16

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items.keys() else "BLENDER_EEVEE"
    if hasattr(scene, "eevee") and hasattr(scene.eevee, "taa_render_samples"):
        scene.eevee.taa_render_samples = samples
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    scene.frame_start = 1
    scene.frame_end = 60 * fps
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.render.image_settings.color_mode = "RGBA"

    asphalt = mat("Wet graphite asphalt", (0.018, 0.026, 0.045), 0.35, 0.22)
    concrete = mat("Blue-black architecture", (0.035, 0.055, 0.09), 0.25, 0.32)
    dark = mat("Vehicle ceramic carbon", (0.012, 0.02, 0.035), 0.75, 0.2)
    glass = mat("Smoked glass", (0.012, 0.07, 0.11), 0.8, 0.12)
    cyan = mat("Electric cyan", (0.02, 0.65, 1.0), 0.25, 0.22, 5.0)
    magenta = mat("Neon magenta", (1.0, 0.025, 0.32), 0.15, 0.25, 4.0)
    amber = mat("Warm windows", (1.0, 0.32, 0.055), 0.0, 0.4, 2.0)
    white = mat("Headlights", (0.75, 0.9, 1.0), 0.0, 0.2, 7.0)

    # Road and reflective lane guides
    cube("Endless elevated roadway", (0, 0, -0.42), (18, 150, 0.8), asphalt, 0.12)
    for x in (-3.4, 3.4):
        cube("Cyan road edge", (x, 0, 0.015), (0.055, 150, 0.025), cyan)
    for y in range(-70, 75, 8):
        cube("Lane dash", (0, y, 0.018), (0.12, 3.2, 0.025), mat("Lane paint", (0.22, 0.34, 0.42), 0.1, 0.4, 0.25))

    # Dense skyline with repeating window grids
    for side in (-1, 1):
        for i in range(24):
            y = -52 + i * 4.5
            x = side * random.uniform(8.5, 15.5)
            h = random.uniform(9, 34)
            w = random.uniform(3.0, 5.8)
            b = cube("Tower", (x, y, h / 2 - 0.1), (w, random.uniform(3, 5), h), concrete, 0.12)
            accent = cyan if (i + (side == 1)) % 3 else magenta
            cube("Tower vertical neon", (x - side * (w/2 + .035), y, h * .52), (.07, .12, h*.78), accent)
            # Window strips on the road-facing facade
            for floor in range(1, max(2, int(h // 2.8))):
                for col in range(2):
                    wx = x - side * (w * .22) + col * side * (w * .42)
                    cube("Lit window", (wx, y - 0.12, floor * 2.65), (.34, .035, .72), amber if random.random() < .22 else cyan)
    # Distant skyline silhouettes
    for i in range(28):
        x = random.choice([-1, 1]) * random.uniform(20, 34)
        y = random.uniform(-60, 65)
        h = random.uniform(14, 48)
        cube("Distant megatower", (x, y, h/2), (random.uniform(4,8), 5, h), concrete)

    # Hero vehicle, pointing toward +Y
    car = bpy.data.objects.new("Hero vehicle rig", None)
    scene.collection.objects.link(car)
    body = cube("Sculpted hypercar body", (0, 0, 0.65), (2.25, 4.6, 0.72), dark, 0.28)
    body.parent = car
    canopy = cube("Panoramic cockpit", (0, -0.05, 1.15), (1.55, 2.05, 0.62), glass, 0.25)
    canopy.parent = car
    hood = cube("Front carbon splitter", (0, 2.18, .42), (2.35, .34, .16), dark, .06)
    hood.parent = car
    for x in (-.82, .82):
        lamp = cube("Laser headlight", (x, 2.22, .78), (.42, .06, .12), white, .035)
        lamp.parent = car
        tail = cube("Rear neon light", (x, -2.26, .76), (.48, .06, .11), magenta, .025)
        tail.parent = car
        for y in (-1.45, 1.45):
            bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=.43, depth=.22, location=(x*1.18, y, .42), rotation=(math.pi/2,0,0))
            wheel = bpy.context.object
            wheel.name = "Alloy wheel"
            wheel.data.materials.append(dark)
            wheel.parent = car
    animate(car, [(1, (0, -7, 0)), (fps*15, (.35, 4, .08)), (fps*30, (-.35, 7, .03)), (fps*45, (.25, 10, .08)), (fps*60, (0, 14, 0))])

    # Floating atmospheric light bars and traffic streaks
    for i in range(34):
        y = random.uniform(-48, 65)
        side = random.choice([-1, 1])
        x = side * random.uniform(4.4, 7.2)
        z = random.uniform(1.2, 8.5)
        o = cube("Passing light streak", (x, y, z), (.045, random.uniform(1.0, 4.0), .045), cyan if i % 2 else magenta)
        animate(o, [(1, (x, y-12, z)), (scene.frame_end, (x, y+18, z))])

    # Camera chase framing
    bpy.ops.object.camera_add(location=(0, -15, 5.1))
    cam = bpy.context.object
    cam.name = "Cinematic chase camera"
    look_at(cam, (0, 2, 1))
    cam.data.lens = 34
    scene.camera = cam
    animate(cam, [(1, (0, -15, 5.1)), (fps*20, (1.2, -12, 4.2)), (fps*40, (-1.0, -10, 4.8)), (fps*60, (0, -8, 4.1))])
    for f in (1, fps*20, fps*40, fps*60):
        scene.frame_set(f)
        look_at(cam, (0, 2, .7))
        cam.keyframe_insert(data_path="rotation_euler", frame=f)

    # Lighting and world
    world = bpy.data.worlds.new("Midnight blue atmosphere") if not bpy.data.worlds else bpy.data.worlds[0]
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (.006, .012, .035, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = .35
    bpy.ops.object.light_add(type="AREA", location=(0, -3, 12))
    key = bpy.context.object
    key.data.energy = 1800
    key.data.shape = "DISK"
    key.data.size = 12
    look_at(key, (0, 4, 0))
    bpy.ops.object.light_add(type="AREA", location=(0, 15, 8))
    rim = bpy.context.object
    rim.data.energy = 2200
    rim.data.color = (.05, .3, 1)
    rim.data.size = 10
    look_at(rim, (0, 0, 0))
    scene.use_nodes = True
    nodes = scene.node_tree.nodes
    nodes.clear()
    rl = nodes.new("CompositorNodeRLayers")
    glare = nodes.new("CompositorNodeGlare")
    glare.glare_type = "FOG_GLOW"
    glare.threshold = 1.2
    glare.quality = "MEDIUM"
    comp = nodes.new("CompositorNodeComposite")
    scene.node_tree.links.new(rl.outputs["Image"], glare.inputs["Image"])
    scene.node_tree.links.new(glare.outputs["Image"], comp.inputs["Image"])

    # Opening title as emissive 3D text, fades away after the opening
    title_mat = mat("Title glow", (.15, .75, 1), 0, .3, 3.0)
    bpy.ops.object.text_add(location=(-3.1, 1.0, 5.3), rotation=(math.radians(68), 0, 0))
    title = bpy.context.object
    title.name = "Opening title"
    title.data.body = a.title[:28].upper()
    title.data.align_x = "LEFT"
    title.data.size = .62
    title.data.extrude = .008
    title.data.materials.append(title_mat)
    title.keyframe_insert(data_path="location", frame=1)
    title.location.z = 7.5
    title.keyframe_insert(data_path="location", frame=fps*5)
    title.hide_render = False
    title.keyframe_insert(data_path="hide_render", frame=1)
    title.hide_render = True
    title.keyframe_insert(data_path="hide_render", frame=fps*6)

    # Motion blur, ambient occlusion and output
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.filepath = os.path.join(a.output, "frame_")
    scene.render.use_file_extension = True
    scene.render.image_settings.color_depth = "8"
    scene.render.resolution_percentage = 100
    scene.render.use_motion_blur = False
    scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(a.output, "cinematic.blend"))
    print(f"Scene ready: {width}x{height}, {fps} fps, {scene.frame_end} frames")

if __name__ == "__main__":
    main()
