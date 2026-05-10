import bpy, os, sys

GLTF_FILE = os.path.abspath("orbitron_lab_v5.gltf")
AC3D_FILE = os.path.abspath("./Orbitron-TestStand/Models/orbitron.ac")

def execute_pipeline():
    print("--- STARTING AUTOMATED GUI PIPELINE ---")
    bpy.ops.preferences.addon_enable(module="io_scene_ac3d")

    # 1. Clean & Import
    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    bpy.ops.import_scene.gltf(filepath=GLTF_FILE)

    # 2. Flatten & Transform
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # 3. Clean Empties
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH':
            obj.select_set(True)
    bpy.ops.object.delete()

    # 4. Snap to Ground perfectly
    min_z = float('inf')
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            for v in obj.data.vertices:
                co_z = (obj.matrix_world @ v.co).z
                if co_z < min_z:
                    min_z = co_z
                    
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            obj.location.z -= min_z
            
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

    # -------------------------------------------------------------
    # 5. FLAWLESS COLOR SYNC (No Exporter Hacking)
    # -------------------------------------------------------------
    for mat in bpy.data.materials:
        if mat.use_nodes and mat.node_tree:
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf and 'Base Color' in bsdf.inputs:
                c = bsdf.inputs['Base Color'].default_value
                
                # Apply a slight curve to the raw data so dark greys are visible
                r = min(1.0, c[0] ** 0.6)
                g = min(1.0, c[1] ** 0.6)
                b = min(1.0, c[2] ** 0.6)
                
                # Safely copy to the exporter target. We LEAVE THE NODES ON so it doesn't break.
                mat.diffuse_color = (r, g, b, 1.0)

    # -------------------------------------------------------------
    # 6. PHYSICAL GEOMETRY REPAIR (No Normal Flipping!)
    # -------------------------------------------------------------
    flat_objects = ["Operator_Console", "Optics_Table", "Screen"]
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            bpy.context.view_layer.objects.active = obj
            
            if any(target in obj.name for target in flat_objects):
                # FIX 1: Give the flat planes physical 3D thickness so they cannot vanish!
                bpy.ops.object.modifier_add(type='SOLIDIFY')
                obj.modifiers["Solidify"].thickness = 0.02  # 2cm thick
                bpy.ops.object.modifier_apply(modifier="Solidify")
                
                # FIX 2: Give the desk sharp, hard edges so it doesn't look mushy
                bpy.ops.object.modifier_add(type='EDGE_SPLIT')
                obj.modifiers["EdgeSplit"].split_angle = 0.52  # ~30 degrees
                bpy.ops.object.modifier_apply(modifier="EdgeSplit")

    # 7. Screen UV Unwrap
    screen_obj = bpy.data.objects.get("Screen")
    if screen_obj:
        bpy.ops.object.select_all(action='DESELECT')
        screen_obj.select_set(True)
        bpy.context.view_layer.objects.active = screen_obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project()
        bpy.ops.object.mode_set(mode='OBJECT')

    # 8. Export Natively
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = bpy.context.scene.objects[0]
    bpy.ops.export_scene.export_ac3d('EXEC_DEFAULT', filepath=AC3D_FILE)
    
    # -------------------------------------------------------------
    # 9. POST-PROCESS: Kill Fake Shine & Set Natural Shadows
    # -------------------------------------------------------------
    with open(AC3D_FILE, 'r') as f:
        lines = f.readlines()

    with open(AC3D_FILE, 'w') as f:
        for line in lines:
            if line.startswith("MATERIAL"):
                parts = line.split()
                try:
                    if "rgb" in parts:
                        idx = parts.index("rgb")
                        r = float(parts[idx+1])
                        g = float(parts[idx+2])
                        b = float(parts[idx+3])
                        
                        # Shadows match the exact color of the object, just slightly darker
                        if "amb" in parts:
                            i = parts.index("amb")
                            parts[i+1], parts[i+2], parts[i+3] = f"{r*0.6:.3f}", f"{g*0.6:.3f}", f"{b*0.6:.3f}"
                            
                        # Kill the shiny plastic look entirely
                        if "emis" in parts:
                            i = parts.index("emis")
                            parts[i+1], parts[i+2], parts[i+3] = "0.0", "0.0", "0.0"
                        if "spec" in parts:
                            i = parts.index("spec")
                            parts[i+1], parts[i+2], parts[i+3] = "0.05", "0.05", "0.05"
                            
                        line = " ".join(parts) + "\n"
                except Exception:
                    pass
                    
            f.write(line)
    
    print("--- PIPELINE COMPLETE ---")
    bpy.ops.wm.quit_blender()
    return None

bpy.app.timers.register(execute_pipeline, first_interval=1.0)
