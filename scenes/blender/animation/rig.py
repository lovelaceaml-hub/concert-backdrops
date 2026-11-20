"""Visible original gold-form humanoid, with a reusable deformation armature."""
from __future__ import annotations

import math
from dataclasses import dataclass

import bpy
from mathutils import Matrix, Vector

from pipeline.motion.character import HumanoidPerformance, REST_BONES


@dataclass
class CharacterRig:
    armature: object
    mesh: object
    seed: int


def _gold_material(name):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (0.72, 0.39, 0.10, 1.0)
    shader.inputs["Metallic"].default_value = 0.45
    shader.inputs["Roughness"].default_value = 0.32
    shader.inputs["Emission Color"].default_value = (0.72, 0.39, 0.10, 1.0)
    shader.inputs["Emission Strength"].default_value = 0.8
    return material


def create_character(name="Light figure", *, location=(0.0, 0.0, 0.0), scale=1.0, material=None, seed=2026):
    """Create a 1.85 m Z-up stand-in, facing -Y, with soft bent limb segments.

    Every visible piece is generated here and weighted to a real armature.
    Fingers are a relaxed grouped form, not an articulated close-up hand rig.
    """
    if not math.isfinite(scale) or scale <= 0:
        raise ValueError("character scale must be positive")
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    data = bpy.data.armatures.new(f"{name} skeleton")
    armature = bpy.data.objects.new(f"{name} rig", data)
    bpy.context.collection.objects.link(armature)
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    for bone_name, (head, tail, parent) in REST_BONES.items():
        bone = data.edit_bones.new(bone_name)
        bone.head, bone.tail = head, tail
        if parent:
            bone.parent = data.edit_bones[parent]
        bone.use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    armature.location = location
    armature.scale = (scale, scale, scale)
    armature.show_in_front = True
    for bone in armature.pose.bones:
        bone.rotation_mode = "QUATERNION"

    vertices, faces, groups = [], [], {}

    def ellipsoid(bone_name, center, radii, rotation=None, segments=12, rings=8):
        start = len(vertices)
        rotation = rotation or Matrix.Identity(3)
        # Separate polar vertices avoid degenerate quads at the poles.
        vertices.append(tuple(Vector(center) + rotation @ Vector((0.0, 0.0, radii[2]))))
        for ring in range(1, rings):
            phi = math.pi * ring / rings
            for index in range(segments):
                theta = math.tau * index / segments
                vector = Vector((radii[0] * math.sin(phi) * math.cos(theta), radii[1] * math.sin(phi) * math.sin(theta), radii[2] * math.cos(phi)))
                vertices.append(tuple(Vector(center) + rotation @ vector))
        bottom = len(vertices)
        vertices.append(tuple(Vector(center) + rotation @ Vector((0.0, 0.0, -radii[2]))))
        for index in range(segments):
            nxt = (index + 1) % segments
            faces.append((start, start + 1 + index, start + 1 + nxt))
            for ring in range(rings - 2):
                a = start + 1 + ring * segments + index
                b = start + 1 + ring * segments + nxt
                faces.append((a, a + segments, b + segments, b))
            last = start + 1 + (rings - 2) * segments
            faces.append((bottom, last + nxt, last + index))
        groups.setdefault(bone_name, []).extend(range(start, len(vertices)))

    ellipsoid("pelvis", (0.0, 0.0, 1.0), (0.17, 0.12, 0.16))
    ellipsoid("spine", (0.0, 0.0, 1.25), (0.20, 0.115, 0.25))
    ellipsoid("neck", (0.0, 0.0, 1.51), (0.06, 0.06, 0.10))
    ellipsoid("head", (0.0, -0.012, 1.73), (0.115, 0.10, 0.15), segments=16, rings=12)
    for side in ("L", "R"):
        for part, radius in (("upper_arm", 0.062), ("forearm", 0.050), ("thigh", 0.079), ("shin", 0.062)):
            bone_name = f"{part}.{side}"
            head, tail, _ = REST_BONES[bone_name]
            a, b = Vector(head), Vector(tail)
            rotation = (b - a).to_track_quat("Z", "Y").to_matrix()
            ellipsoid(bone_name, (a + b) * 0.5, (radius, radius * 0.9, (b - a).length * 0.56), rotation)
        hand_name, foot_name = f"hand.{side}", f"foot.{side}"
        for bone_name, radius in ((hand_name, 0.040),):
            a, b = (Vector(v) for v in REST_BONES[bone_name][:2])
            rotation = (b - a).to_track_quat("Z", "Y").to_matrix()
            ellipsoid(bone_name, (a + b) * 0.5, (radius, radius * 0.62, (b - a).length * 0.60), rotation)
        foot_x = REST_BONES[foot_name][0][0]
        ellipsoid(foot_name, (foot_x, -0.08, 0.065), (0.057, 0.135, 0.065))
        # Short, softened grouped fingers make a readable relaxed hand without
        # pretending this foundation is a production close-up finger rig.
        a, b = (Vector(v) for v in REST_BONES[hand_name][:2])
        rotation = (b - a).to_track_quat("Z", "Y").to_matrix()
        for finger in range(4):
            offset = rotation @ Vector(((finger - 1.5) * 0.014, 0.0, 0.026))
            ellipsoid(hand_name, b + offset, (0.010, 0.010, 0.027 - abs(finger - 1.5) * 0.003), rotation, segments=8, rings=6)

    mesh_data = bpy.data.meshes.new(f"{name} code geometry")
    mesh_data.from_pydata(vertices, [], faces)
    mesh_data.update()
    mesh = bpy.data.objects.new(f"{name} gold form", mesh_data)
    bpy.context.collection.objects.link(mesh)
    mesh.parent = armature
    mesh.data.materials.append(material or _gold_material(f"{name} warm gold"))
    for polygon in mesh.data.polygons:
        polygon.use_smooth = True
    for bone_name, indices in groups.items():
        mesh.vertex_groups.new(name=bone_name).add(indices, 1.0, "REPLACE")
    modifier = mesh.modifiers.new("Skeletal deformation", "ARMATURE")
    modifier.object = armature
    modifier.use_deform_preserve_volume = True
    return CharacterRig(armature, mesh, int(seed))


class CharacterPerformance:
    def __init__(self, rig, *, action="conduct", strength=0.7, fps=60.0, events=()):
        self.rig = rig
        self.motion = HumanoidPerformance(action=action, strength=strength, seed=rig.seed, fps=fps, events=events)

    def apply(self, seconds):
        pose = self.motion.sample(seconds)
        desired = {}
        for name, (head, tail, parent) in REST_BONES.items():
            bone = self.rig.armature.data.bones[name]
            a, b = (Vector(v) for v in pose.bones[name])
            rest_direction = Vector(tail) - Vector(head)
            orientation = rest_direction.rotation_difference(b - a).to_matrix() @ bone.matrix_local.to_3x3()
            matrix = orientation.to_4x4()
            matrix.translation = a
            desired[name] = matrix
            if parent:
                basis = bone.convert_local_to_pose(matrix, bone.matrix_local, parent_matrix=desired[parent], parent_matrix_local=self.rig.armature.data.bones[parent].matrix_local, invert=True)
            else:
                basis = bone.convert_local_to_pose(matrix, bone.matrix_local, invert=True)
            self.rig.armature.pose.bones[name].matrix_basis = basis
        return pose
