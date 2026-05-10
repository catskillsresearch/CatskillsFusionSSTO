import bpy
import os

GLTF_FILE = os.path.abspath("orbitron_lab_v5.gltf")
AC3D_FILE = os.path.abspath("./Orbitron-TestStand/Models/orbitron.ac")

def execute_pipeline():
    print("--- STARTING AUTOMATED GUI PIPELINE ---")

    bpy.ops.preferences.addon_enable(module="io_scene_ac3d")

    # Clear scene
    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Import
    print(f"Importing {GLTF_FILE}...")
    bpy.ops.import_scene.gltf(filepath=GLTF_FILE)

    # Shading
    flat_objects =["Operator_Console", "Optics_Table"]
    for obj in bpy.context.scene.objects:
        if any(target in obj.name for target in flat_objects):
            for poly in obj.data.polygons:
                poly.use_smooth = False

    # UV Mapping
    screen_obj = bpy.data.objects.get("Screen")
    if screen_obj:
        bpy.context.view_layer.objects.active = screen_obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project()
        bpy.ops.object.mode_set(mode='OBJECT')

    # Prep for Export
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = bpy.context.scene.objects[0]

    # THE FIX: Using the exact operator name we discovered in the dictionary dump
    print(f"Exporting to {AC3D_FILE}...")
    bpy.ops.export_scene.export_ac3d('EXEC_DEFAULT', filepath=AC3D_FILE)

    print("Closing Blender...")
    bpy.ops.wm.quit_blender()
    return None

print("Waiting for Blender UI to load...")
bpy.app.timers.register(execute_pipeline, first_interval=1.0)
