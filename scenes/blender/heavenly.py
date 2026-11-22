"""An original procedural pavilion used to exercise the production pipeline.

This is a technical example, not a reconstruction of an approved church or film.
Blender coordinates are Z-up. The legacy p3d world remains Y-up.
"""
import math
import random

import bpy
from mathutils import Vector


def rgba(value):
    value = value.lstrip("#")
    rgb = [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in rgb) + (1,)


def material(name, colour, metallic=0, roughness=.35, emission=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = rgba(colour)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = rgba(colour)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Emission Color"].default_value = rgba(colour)
    shader.inputs["Emission Strength"].default_value = emission
    return mat


def finish(obj, name, mat, bevel=0):
    obj.name = name
    obj.data.materials.append(mat)
    if bevel:
        modifier = obj.modifiers.new("Soft architectural edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
        obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    if obj.type == "MESH":
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
    return obj


def cylinder(name, location, radius, depth, mat, bevel=.025):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=depth, location=location)
    return finish(bpy.context.object, name, mat, bevel)


def curve(name, points, mat, radius=.025, cyclic=False):
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"
    data.resolution_u = 2
    data.bevel_depth = radius
    data.bevel_resolution = 3
    spline = data.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, coordinates in zip(spline.points, points):
        point.co = (*coordinates, 1)
    spline.use_cyclic_u = cyclic
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def area(name, location, energy, colour, size):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.color = rgba(colour)[:3]
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    aim(obj, (0, 0, 1))


def build_scene(job):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = int(job.get("samples", 12))
    scene.cycles.use_denoising = True
    scene.cycles.use_adaptive_sampling = False
    scene.cycles.max_bounces = 4
    scene.cycles.diffuse_bounces = 2
    scene.cycles.glossy_bounces = 2
    scene.cycles.seed = int(job.get("seed", 2026))
    scene.cycles.use_animated_seed = False
    scene.render.film_transparent = False
    scene.render.use_persistent_data = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.image_settings.compression = 30
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.exposure = -.3
    scene.view_settings.gamma = 1
    scene.world.use_nodes = True
    world = scene.world.node_tree.nodes.get("Background")
    world.inputs["Color"].default_value = rgba("#bfd7ed")
    world.inputs["Strength"].default_value = .7

    ivory = material("Warm porcelain", "#efe2cc", .08, .28)
    gold = material("Brushed champagne gold", "#d8ad62", .72, .27)
    aqua = material("Luminous blue glass colour", "#9de5ef", .25, .24, .8)
    pearl = material("Pearl highlights", "#fff1d0", .18, .2, 1.2)
    water = material("Reflecting sea", "#8bb8c9", .4, .19)

    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -.18))
    finish(bpy.context.object, "Quiet mirror sea", water)
    for index, (radius, z, depth) in enumerate([(3.2, -.06, .22), (2.85, .1, .18), (2.5, .25, .15)]):
        cylinder(f"Terrace {index}", (0, 0, z), radius, depth, ivory)
        cylinder(f"Terrace gold rim {index}", (0, 0, z + depth * .4), radius + .014, .025, gold, .006)

    # Open front gives the camera an unobstructed view of the centre.
    for index in range(9):
        angle = math.radians(20 + index * 17.5)
        x, y = 2.06 * math.cos(angle), 2.06 * math.sin(angle)
        cylinder(f"Column {index}", (x, y, 1.35), .095, 2.1, ivory)
        cylinder(f"Column foot {index}", (x, y, .43), .15, .12, gold)
        cylinder(f"Column crown {index}", (x, y, 2.39), .14, .13, gold)
        curve(f"Column light {index}", [(x, y, .53), (x, y, 2.27)], aqua, .016)

    # A crown of nested arcs, built from code rather than a downloaded model.
    for ring in range(3):
        points = []
        for k in range(97):
            angle = math.pi * k / 96
            radius = 2.13 - ring * .13
            points.append((radius * math.cos(angle), .9 + .04 * ring, 2.3 + .85 * math.sin(angle) + .08 * ring))
        curve(f"Crown arch {ring}", points, gold if ring != 1 else pearl, .028)

    cylinder("Central light plinth", (0, .25, .46), .5, .22, ivory)
    cylinder("Central gold rim", (0, .25, .59), .51, .035, gold, .008)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=.25, location=(0, .25, 1.07))
    heart_of_light = finish(bpy.context.object, "Floating pearl of light", pearl)

    colours = ["#EA5A5E", "#F2B25E", "#F6CE46", "#5ABA5A", "#62B2FA", "#667AF6", "#9E6AF6", "#EE62A6", "#8daceb"]
    ribbons = []
    for index, colour in enumerate(colours):
        mat = material(f"Ribbon colour {index}", colour, .2, .32, 1.3)
        points = []
        for step in range(65):
            u = step / 64
            theta = u * math.pi * 1.8 + index * .16
            radius = 2.8 + .1 * index
            points.append((radius * math.cos(theta), 2.0 + radius * math.sin(theta), 1.1 + u * 2.6 + .03 * index))
        ribbons.append(curve(f"Stream of colour {index}", points, mat, .016))

    rng = random.Random(int(job.get("seed", 2026)))
    sparkles = []
    for index in range(28):
        position = (rng.uniform(-3.2, 3.2), rng.uniform(-.4, 3.4), rng.uniform(.7, 3.8))
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=rng.uniform(.008, .018), location=position)
        obj = finish(bpy.context.object, f"Soft mote {index}", pearl)
        sparkles.append((obj, position, rng.random() * math.tau))

    area("Large warm key", (0, -4, 7), 850, "#ffe6bf", 5)
    area("Soft sky fill", (-5, -1, 4), 650, "#d0e9ff", 6)
    area("Crown rim light", (1, 4, 5), 1000, "#ffdeab", 4)
    data = bpy.data.cameras.new("Pavilion camera")
    camera = bpy.data.objects.new("Pavilion camera", data)
    bpy.context.collection.objects.link(camera)
    scene.camera = camera
    data.lens = 43
    data.clip_start = .05
    data.clip_end = 300
    data.dof.use_dof = False

    if hasattr(scene, "compositing_node_group"):
        tree = bpy.data.node_groups.new("Pavilion finishing", "CompositorNodeTree")
        tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        scene.compositing_node_group = tree
    else:
        scene.use_nodes = True
        tree = scene.node_tree
    nodes = tree.nodes
    nodes.clear()
    layers = nodes.new("CompositorNodeRLayers")
    glow = nodes.new("CompositorNodeGlare")
    if hasattr(glow, "glare_type"):
        glow.glare_type = "FOG_GLOW"
        glow.quality = "MEDIUM"
        glow.threshold = 1.4
        glow.size = 7
        glow.mix = -.86
    else:
        glow.inputs["Type"].default_value = "Fog Glow"
        glow.inputs["Quality"].default_value = "Medium"
        glow.inputs["Threshold"].default_value = 1.4
        glow.inputs["Size"].default_value = .35
        glow.inputs["Strength"].default_value = .14
    composite = nodes.new("NodeGroupOutput" if hasattr(scene, "compositing_node_group") else "CompositorNodeComposite")
    tree.links.new(layers.outputs["Image"], glow.inputs["Image"])
    tree.links.new(glow.outputs["Image"], composite.inputs["Image"])

    start = int(job["shot"]["start_frame"])
    span = max(1, int(job["shot"]["end_frame_exclusive"]) - start - 1)
    fps = float(job["video"]["fps"])

    def update(frame):
        time = frame / fps
        progress = min(1, max(0, (frame - start) / span))
        ease = progress * progress * (3 - 2 * progress)
        theta = -.5 + .25 * ease
        camera.location = (12.4 * math.sin(theta), -12.4 * math.cos(theta), 4.3 - .25 * ease)
        aim(camera, (0, 1.0, 1.65))
        heart_of_light.location.z = 1.09 + .06 * math.sin(time * .7)
        for index, ribbon in enumerate(ribbons):
            ribbon.rotation_euler.z = .025 * math.sin(time * .35 + index * .15)
        for obj, base, phase in sparkles:
            obj.location = (base[0] + .035 * math.sin(time * .5 + phase), base[1], base[2] + .06 * math.sin(time * .6 + phase))

    return update
