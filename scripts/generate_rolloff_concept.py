"""Build the REPSA Roll Off concept GLB used by the website's 3D scroll study.

This is an intentionally stylized, non-engineering model. Replace it with an
approved CAD-derived Blender model when drawings and measurements are supplied.
"""

import bpy
import math
from mathutils import Vector


OUTPUT = "assets/models/repsa-rolloff-concept.glb"
TECHNICIAN_OUTPUT = "assets/models/repsa-welding-technician-concept.glb"


def material(name, color, metallic=0.0, roughness=0.5, emission=None):
    value = bpy.data.materials.new(name)
    value.use_nodes = True
    node = next((item for item in value.node_tree.nodes if item.type == "BSDF_PRINCIPLED"), None)
    if node is None:
        raise RuntimeError(f"No Principled BSDF node available for {name}")
    node.inputs["Base Color"].default_value = (*color, 1)
    node.inputs["Metallic"].default_value = metallic
    node.inputs["Roughness"].default_value = roughness
    if emission:
        node.inputs["Emission Color"].default_value = (*emission, 1)
        node.inputs["Emission Strength"].default_value = 2.2
    return value


WHITE = material("REPSA White", (0.72, 0.78, 0.86), 0.35, 0.24)
STEEL = material("Powder-coated Steel", (0.018, 0.035, 0.055), 0.78, 0.24)
RUBBER = material("Industrial Rubber", (0.008, 0.012, 0.016), 0.04, 0.72)
WINDOW = material("Safety Glass", (0.018, 0.13, 0.22), 0.65, 0.12)
ORANGE = material("REPSA Safety Orange", (1.0, 0.22, 0.008), 0.24, 0.28, (1.0, 0.06, 0.0))
CHROME = material("Machined Aluminium", (0.44, 0.5, 0.58), 0.92, 0.18)


def activate(obj, name, material_value):
    obj.name = name
    obj.data.materials.append(material_value)
    return obj


def rounded_box(name, location, dimensions, material_value, bevel=0.06):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = activate(bpy.context.object, name, material_value)
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    modifier = obj.modifiers.new("Soft industrial edges", "BEVEL")
    modifier.width = bevel
    modifier.segments = 3
    modifier.limit_method = "ANGLE"
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    return obj


def cylinder(name, location, radius, depth, material_value, rotation=(math.pi / 2, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = activate(bpy.context.object, name, material_value)
    bevel = obj.modifiers.new("Tire edge", "BEVEL")
    bevel.width = 0.025
    bevel.segments = 2
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    return obj


def pipe_between(name, start, end, radius, material_value):
    start_vector = Vector(start)
    end_vector = Vector(end)
    direction = end_vector - start_vector
    midpoint = (start_vector + end_vector) / 2
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=radius, depth=direction.length, location=midpoint)
    obj = activate(bpy.context.object, name, material_value)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(direction.normalized())
    return obj


def vertical_cylinder(name, location, radius, depth, material_value):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=radius, depth=depth, location=location)
    obj = activate(bpy.context.object, name, material_value)
    bevel = obj.modifiers.new("Soft garment edge", "BEVEL")
    bevel.width = 0.035
    bevel.segments = 2
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    return obj


def sphere(name, location, scale, material_value):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=location)
    obj = activate(bpy.context.object, name, material_value)
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    return obj


def make_cab_shell():
    vertices = [
        (-0.78, -0.82, 0.0), (0.72, -0.82, 0.0), (0.72, -0.82, 1.24), (-0.30, -0.82, 1.53), (-0.80, -0.82, 0.94),
        (-0.78, 0.82, 0.0), (0.72, 0.82, 0.0), (0.72, 0.82, 1.24), (-0.30, 0.82, 1.53), (-0.80, 0.82, 0.94),
    ]
    faces = [
        (0, 1, 2, 3, 4), (5, 9, 8, 7, 6), (0, 5, 6, 1), (1, 6, 7, 2),
        (2, 7, 8, 3), (3, 8, 9, 4), (4, 9, 5, 0),
    ]
    mesh = bpy.data.meshes.new("Cab shell mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("REPSA cab", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(WHITE)
    obj.location = (-2.22, 0, 0.63)
    bevel = obj.modifiers.new("Cab radius", "BEVEL")
    bevel.width = 0.08
    bevel.segments = 3
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    obj.select_set(False)
    return obj


def build_rolloff():
    root = bpy.data.objects.new("REPSA Roll Off Concept", None)
    bpy.context.collection.objects.link(root)

    components = []
    components.append(rounded_box("Main chassis", (0.1, 0, 0.55), (5.6, 1.52, 0.36), STEEL, 0.09))
    components.append(rounded_box("Front bumper", (-3.04, 0, 0.62), (0.22, 1.62, 0.3), STEEL, 0.05))
    components.append(make_cab_shell())
    components.append(rounded_box("Hood", (-2.75, 0, 1.06), (0.34, 1.54, 0.44), WHITE, 0.06))
    components.append(rounded_box("Windshield", (-2.59, 0, 1.67), (0.08, 1.34, 0.46), WINDOW, 0.025))
    components.append(rounded_box("Driver window", (-2.18, -0.838, 1.64), (0.76, 0.025, 0.42), WINDOW, 0.018))
    components.append(rounded_box("Passenger window", (-2.18, 0.838, 1.64), (0.76, 0.025, 0.42), WINDOW, 0.018))
    components.append(rounded_box("Grille", (-2.95, 0, 0.91), (0.035, 1.15, 0.27), STEEL, 0.018))
    components.append(rounded_box("Left headlamp", (-3.01, -0.53, 1.11), (0.04, 0.24, 0.13), ORANGE, 0.018))
    components.append(rounded_box("Right headlamp", (-3.01, 0.53, 1.11), (0.04, 0.24, 0.13), ORANGE, 0.018))
    components.append(rounded_box("Fuel tank", (-1.03, 0.98, 0.68), (1.15, 0.24, 0.49), CHROME, 0.08))

    for axle in (-1.86, 0.36, 1.84):
        for side in (-0.92, 0.92):
            components.append(cylinder("Truck tire", (axle, side, 0.54), 0.57, 0.38, RUBBER))
            components.append(cylinder("Polished wheel", (axle, side * 1.018, 0.54), 0.24, 0.4, WHITE))
            components.append(cylinder("Wheel hub", (axle, side * 1.04, 0.54), 0.075, 0.42, ORANGE))

    for side in (-0.62, 0.62):
        components.append(rounded_box("Roll off rail", (0.6, side, 1.24), (3.95, 0.16, 0.16), STEEL, 0.035))
        components.append(rounded_box("Safety rail", (0.56, side, 1.55), (3.35, 0.09, 0.08), CHROME, 0.02))
        components.append(rounded_box("Reflective stripe", (0.6, side * 1.13, 1.1), (2.7, 0.025, 0.06), ORANGE, 0.012))

    components.append(pipe_between("Hydraulic arm", (-0.64, 0, 1.17), (1.66, 0, 2.2), 0.11, STEEL))
    components.append(pipe_between("Hydraulic piston", (-0.18, 0, 1.08), (1.2, 0, 1.84), 0.055, CHROME))
    components.append(rounded_box("Rear hook", (2.83, 0, 1.35), (0.4, 1.25, 0.22), STEEL, 0.05))
    components.append(rounded_box("Rear hazard bar", (2.96, 0, 0.82), (0.16, 1.86, 0.18), ORANGE, 0.04))
    components.append(rounded_box("Left rear lamp", (2.99, -0.66, 1.05), (0.08, 0.18, 0.13), ORANGE, 0.02))
    components.append(rounded_box("Right rear lamp", (2.99, 0.66, 1.05), (0.08, 0.18, 0.13), ORANGE, 0.02))

    for component in components:
        component.parent = root
    return root


def build_technician():
    root = bpy.data.objects.new("REPSA Welding Technician Concept", None)
    bpy.context.collection.objects.link(root)
    blue = material("Technician blue coverall", (0.035, 0.22, 0.52), 0.28, 0.32)
    dark_blue = material("Technician trouser", (0.01, 0.035, 0.09), 0.18, 0.5)
    skin = material("Technician skin", (0.3, 0.1, 0.04), 0.03, 0.62)
    glove = material("Technician gloves", (0.5, 0.58, 0.62), 0.45, 0.3)

    pieces = []
    pieces.append(rounded_box("Coverall torso", (0, 0, 1.63), (0.9, 0.62, 1.1), blue, 0.12))
    pieces.append(vertical_cylinder("Left leg", (-0.25, 0, 0.65), 0.22, 1.08, dark_blue))
    pieces.append(vertical_cylinder("Right leg", (0.25, 0, 0.65), 0.22, 1.08, dark_blue))
    pieces.append(rounded_box("Left boot", (-0.27, 0.1, 0.1), (0.48, 0.72, 0.24), RUBBER, 0.09))
    pieces.append(rounded_box("Right boot", (0.27, 0.1, 0.1), (0.48, 0.72, 0.24), RUBBER, 0.09))
    pieces.append(sphere("Head", (0, 0, 2.43), (0.28, 0.28, 0.33), skin))
    pieces.append(sphere("Welding helmet", (0.04, 0, 2.54), (0.4, 0.38, 0.38), STEEL))
    pieces.append(rounded_box("Welding visor", (0.34, 0, 2.46), (0.1, 0.53, 0.25), WINDOW, 0.035))

    pieces.append(pipe_between("Forward upper arm", (0.35, 0, 1.96), (0.68, 0, 1.58), 0.145, blue))
    pieces.append(pipe_between("Forward forearm", (0.68, 0, 1.58), (1.0, 0, 1.26), 0.115, glove))
    pieces.append(sphere("Forward glove", (1.04, 0, 1.22), (0.15, 0.14, 0.13), glove))
    pieces.append(pipe_between("Rear upper arm", (-0.35, 0, 1.96), (-0.54, 0, 1.56), 0.145, blue))
    pieces.append(pipe_between("Rear forearm", (-0.54, 0, 1.56), (-0.14, 0, 1.26), 0.11, glove))
    pieces.append(sphere("Rear glove", (-0.1, 0, 1.23), (0.14, 0.13, 0.12), glove))
    pieces.append(pipe_between("Welding torch", (1.04, 0, 1.22), (1.45, 0, 1.12), 0.045, STEEL))
    pieces.append(sphere("Welding arc", (1.5, 0, 1.1), (0.08, 0.08, 0.08), ORANGE))
    pieces.append(rounded_box("Welding workpiece", (1.55, 0, 0.87), (0.14, 1.05, 1.1), STEEL, 0.035))
    pieces.append(rounded_box("Workpiece seam", (1.46, 0, 1.1), (0.025, 0.8, 0.06), ORANGE, 0.012))

    for piece in pieces:
        piece.parent = root
    return root


bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
build_rolloff()
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(
    filepath=OUTPUT,
    export_format="GLB",
    use_selection=True,
    export_apply=True,
    export_materials="EXPORT",
    export_cameras=False,
    export_lights=False,
    export_yup=True,
)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
build_technician()
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(
    filepath=TECHNICIAN_OUTPUT,
    export_format="GLB",
    use_selection=True,
    export_apply=True,
    export_materials="EXPORT",
    export_cameras=False,
    export_lights=False,
    export_yup=True,
)
