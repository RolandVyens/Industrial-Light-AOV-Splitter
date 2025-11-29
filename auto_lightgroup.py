import bpy
from mathutils import Vector, Matrix


# Global dictionary removed - using bpy.context.view_layer.las_created_lightgroups instead

def setup_driver(source_obj, target_obj, data_path):
    """
    Sets up a driver on target_obj.data_path to copy source_obj.data_path.
    Handles both single values and array properties (like color).
    """
    try:
        # driver_add returns a single FCurve or a list of FCurves (for arrays)
        fcurves = target_obj.driver_add(data_path)
    except TypeError:
        # Property not animatable
        print(f"Property {data_path} is not animatable.")
        return
    except Exception as e:
        print(f"Error adding driver for {data_path}: {e}")
        return

    # Normalize to list
    if not isinstance(fcurves, list):
        fcurves = [fcurves]
        
    for fcurve in fcurves:
        driver = fcurve.driver
        driver.type = 'AVERAGE'
        
        # Remove existing variables to start fresh
        for var in driver.variables:
            driver.variables.remove(var)
            
        # Create new variable
        var = driver.variables.new()
        var.name = "var"
        var.type = 'SINGLE_PROP'
        
        # Target the source object
        target = var.targets[0]
        target.id_type = 'OBJECT'
        target.id = source_obj
        
        # Construct data path with index if applicable
        if fcurve.array_index >= 0:
             target.data_path = f"data.{data_path}[{fcurve.array_index}]"
        else:
             target.data_path = f"data.{data_path}"

# Comprehensive list of properties to drive for each light type
LIGHT_PROPERTIES = {
    'POINT': [
        'color', 'energy', 'specular_factor', 'diffuse_factor', 'transmission_factor', 'volume_factor',
        'use_shadow', 'shadow_soft_size', 'shadow_buffer_clip_start', 
        'use_custom_distance', 'cutoff_distance', 'use_soft_falloff'
    ],
    'SPOT': [
        'color', 'energy', 'specular_factor', 'diffuse_factor', 'transmission_factor', 'volume_factor',
        'use_shadow', 'shadow_soft_size', 'shadow_buffer_clip_start',
        'use_custom_distance', 'cutoff_distance', 'use_soft_falloff',
        'spot_size', 'spot_blend', 'show_cone', 'use_square'
    ],
    'AREA': [
        'color', 'energy', 'specular_factor', 'diffuse_factor', 'transmission_factor', 'volume_factor',
        'use_shadow', 'shadow_soft_size', 'shadow_buffer_clip_start',
        'use_custom_distance', 'cutoff_distance',
        'shape', 'size', 'size_y', 'spread'
    ],
    'SUN': [
        'color', 'energy', 'specular_factor', 'diffuse_factor', 'transmission_factor', 'volume_factor',
        'use_shadow', 'shadow_soft_size', 'shadow_buffer_clip_start',
        'angle', 
        'shadow_cascade_max_distance', 'shadow_cascade_count', 'shadow_cascade_exponent', 'shadow_cascade_fade'
    ]
}

def create_split_lights(master_obj, collection):
    """
    Creates 4 split lights (Diffuse, Specular, Transmission, Volume) for the given master light.
    Parents them to master, sets up drivers, and assigns light groups.
    """
    lobes = ["diffuse", "specular", "transmission", "volume"]
    
    # Ensure master light is hidden from render (so it doesn't double contribute)
    # But we want to keep it visible in viewport for editing.
    master_obj.hide_render = True
    
    # We need a base name for the light groups
    base_name = master_obj.name
    if "." in base_name:
        base_name = base_name.split(".")[0]
        
    for lobe in lobes:
        suffix = f"_{lobe}"
        # Check if child already exists
        child_name = f"{master_obj.name}{suffix}"
        
        # Try to find existing object
        child_obj = bpy.data.objects.get(child_name)
        
        if child_obj is None:
            # Create new light by copying master (preserves Light Linking, etc.)
            child_obj = master_obj.copy()
            child_obj.data = master_obj.data.copy()
            child_obj.name = child_name
            child_obj.data.name = f"{master_obj.data.name}{suffix}"
            
            # Clear animation data (drivers) from copy
            if child_obj.animation_data:
                child_obj.animation_data_clear()
            if child_obj.data.animation_data:
                child_obj.data.animation_data_clear()
                
            # Link to the same collection
            collection.objects.link(child_obj)
        else:
            # Ensure data is unique/copied if it was shared? 
            # Actually we want it to be a copy so we can modify visibility without affecting others
            if child_obj.data == master_obj.data:
                 child_obj.data = master_obj.data.copy()
        
        # Parent to master
        if child_obj.parent != master_obj:
            child_obj.parent = master_obj
            child_obj.matrix_parent_inverse = Matrix.Identity(4)
            
        # Reset transform (since it's parented)
        child_obj.location = (0,0,0)
        child_obj.rotation_euler = (0,0,0)
        child_obj.scale = (1,1,1)
        
        # Apply Large Scale Mode Offset
        if bpy.context.scene.LAS_fixMissingLight:
             # Offset based on lobe index to avoid z-fighting/overlap issues in large scenes
             # lobes = ["diffuse", "specular", "transmission", "volume"]
             # index 0, 1, 2, 3
             idx = lobes.index(lobe)
             z_offset = 0.002 * idx
             # Apply in local space (since it's parented)
             child_obj.location = (0, 0, z_offset)
        
        # Set Visibility
        child_obj.visible_diffuse = (lobe == "diffuse")
        child_obj.visible_glossy = (lobe == "specular")
        child_obj.visible_transmission = (lobe == "transmission")
        child_obj.visible_volume_scatter = (lobe == "volume")
        
        # Hide from Viewport (Eye icon off, Monitor icon on)
        child_obj.hide_set(True)        # Eye icon OFF
        
        # Enable Render (Camera icon ON) - Fix for user request
        child_obj.hide_render = False
        
        # Clear constraints (since we copied master, we don't want double constraints)
        child_obj.constraints.clear()
        
        # Set Light Group
        lg_name = f"{lobe}_{base_name}"
        # Ensure light group exists in view layer
        if lg_name not in bpy.context.view_layer.lightgroups:
            lg = bpy.context.view_layer.lightgroups.add()
            lg.name = lg_name
            
        # Track created lightgroup (Persistent)
        view_layer = bpy.context.view_layer
        # Check if already tracked
        already_tracked = False
        for item in view_layer.las_created_lightgroups:
            if item.name == lg_name:
                already_tracked = True
                break
        if not already_tracked:
            item = view_layer.las_created_lightgroups.add()
            item.name = lg_name
            
        child_obj.lightgroup = lg_name
        
        # Setup Drivers
        # Use the comprehensive LIGHT_PROPERTIES dict
        light_type = master_obj.data.type
        data_paths = LIGHT_PROPERTIES.get(light_type, [])
        
        # Add legacy fallback for older Blender versions if needed, or just rely on hasattr check
        if not data_paths:
             # Fallback for unknown types or if dict is missing something
             data_paths = ["color", "energy"]
             
        for path in data_paths:
            if not hasattr(child_obj.data, path):
                continue
            try:
                setup_driver(master_obj, child_obj.data, path)
            except Exception as e:
                print(f"Failed to setup driver for {path}: {e}")

def auto_lightgroup():
    """
    Assigns lightgroups to lights in 'lgt_' collections.
    Does NOT create split lights.
    """
    def process_collection_group(layer_collection):
        if layer_collection.exclude:
            return
            
        col_name = layer_collection.collection.name
        if col_name.startswith("lgt_"):
            for obj in list(layer_collection.collection.all_objects):
                if obj.type == 'LIGHT':
                    # Skip if it's a child light (has parent which is light)
                    if obj.parent and obj.parent.type == 'LIGHT':
                        continue
                        
                    # Assign LightGroup
                    lg_name = obj.name
                    if "." in lg_name:
                         lg_name = lg_name.split(".")[0]
                         
                    if lg_name not in bpy.context.view_layer.lightgroups:
                        lg = bpy.context.view_layer.lightgroups.add()
                        lg.name = lg_name
                        
                    # Track created lightgroup (Persistent)
                    view_layer = bpy.context.view_layer
                    already_tracked = False
                    for item in view_layer.las_created_lightgroups:
                        if item.name == lg_name:
                            already_tracked = True
                            break
                    if not already_tracked:
                        item = view_layer.las_created_lightgroups.add()
                        item.name = lg_name
                    
                    obj.lightgroup = lg_name
                    
        # Recurse
        for child in layer_collection.children:
            process_collection_group(child)
            
    process_collection_group(bpy.context.view_layer.layer_collection)
    # Try to remove unused lightgroups without relying on a UI/context operator
    try:
        # If Blender's operator is available in context, prefer it (backward compatibility)
        bpy.ops.scene.view_layer_remove_unused_lightgroups()
    except Exception:
        # Fallback: remove lightgroups that have no users in this view layer
        view_layer = bpy.context.view_layer
        unused = []
        for lg in list(view_layer.lightgroups):
            used = False
            # Check objects
            for obj in bpy.context.scene.objects:
                if getattr(obj, "lightgroup", "") == lg.name:
                    used = True
                    break
            # Check world
            if getattr(bpy.context.scene, "world", None) and getattr(bpy.context.scene.world, "lightgroup", "") == lg.name:
                used = True

            if not used:
                unused.append(lg)

        for lg in unused:
            try:
                view_layer.lightgroups.remove(lg)
            except Exception:
                # ignore removal failures
                pass

def auto_lightaov():
    """
    Creates split lights for lights in 'lgt_' collections.
    """
    def process_collection_split(layer_collection):
        if layer_collection.exclude:
            return
            
        col_name = layer_collection.collection.name
        if col_name.startswith("lgt_"):
            for obj in list(layer_collection.collection.all_objects):
                if obj is None:
                    continue
                if obj.type == 'LIGHT':
                    if obj.parent and obj.parent.type == 'LIGHT':
                        continue
                    create_split_lights(obj, layer_collection.collection)
                    
        for child in layer_collection.children:
            process_collection_split(child)
            
    process_collection_split(bpy.context.view_layer.layer_collection)

def auto_assign_world():
    stat = 0
    world = bpy.context.scene.world
    if world and not world.lightgroup:
        world.lightgroup = "env"
        stat = 1
    view_layer = bpy.context.view_layer
    if "env" not in view_layer.lightgroups:
        lg = view_layer.lightgroups.add()
        lg.name = "env"
        
    # Track created lightgroup (Persistent)
    already_tracked = False
    for item in view_layer.las_created_lightgroups:
        if item.name == "env":
            already_tracked = True
            break
    if not already_tracked:
        item = view_layer.las_created_lightgroups.add()
        item.name = "env"
        
    return stat

def assign_missing_object():
    # Keep existing logic for assigning emissive objects
    stat = 0
    objects_with_emissive_material = []
    for obj in bpy.context.scene.objects:
        if obj.material_slots and obj.lightgroup == "":
            for slot in obj.material_slots:
                if slot.material and slot.material.node_tree:
                    for node in slot.material.node_tree.nodes:
                        if node.type == "EMISSION":
                            objects_with_emissive_material.append(obj.name)
                            break
                        elif node.type == "BSDF_PRINCIPLED" and node.inputs[26].default_value > 0: # Emission strength
                             # Note: Index 26 might vary by Blender version. 
                             # 4.0+ Principled BSDF changed. Emission Strength is often named "Emission Strength".
                             # Let's try to find by name or check standard indices.
                             # For safety, let's just check if it has emission.
                             objects_with_emissive_material.append(obj.name)
                             break
                             
    if "emissive_default" not in bpy.context.view_layer.lightgroups:
        lg = bpy.context.view_layer.lightgroups.add()
        lg.name = "emissive_default"
        
    # Track created lightgroup (Persistent)
    view_layer = bpy.context.view_layer
    already_tracked = False
    for item in view_layer.las_created_lightgroups:
        if item.name == "emissive_default":
            already_tracked = True
            break
    if not already_tracked:
        item = view_layer.las_created_lightgroups.add()
        item.name = "emissive_default"
        
    for name in objects_with_emissive_material:
        obj = bpy.context.scene.objects.get(name)
        if obj:
            obj.lightgroup = "emissive_default"
            stat += 1
    return stat

def clean_split_lights(master_obj):
    """
    Removes split lights associated with the master light and restores master light visibility.
    """
    lobes = ["diffuse", "specular", "transmission", "volume"]
    
    # Restore Master Light Visibility
    master_obj.hide_render = False
    
    for lobe in lobes:
        suffix = f"_{lobe}"
        child_name = f"{master_obj.name}{suffix}"
        
        child_obj = bpy.data.objects.get(child_name)
        if child_obj:
            # Remove from scene
            bpy.data.objects.remove(child_obj, do_unlink=True)

def auto_clean_lightaov():
    """
    Iterates through 'lgt_' collections and cleans up split lights.
    Also removes lightgroups created by this addon.
    """
    # Get list of groups to remove (Persistent)
    groups_to_remove = set()
    view_layer = bpy.context.view_layer
    if hasattr(view_layer, "las_created_lightgroups"):
        for item in view_layer.las_created_lightgroups:
            groups_to_remove.add(item.name)

    def process_collection_clean(layer_collection):
        if layer_collection.exclude:
            return
            
        col_name = layer_collection.collection.name
        if col_name.startswith("lgt_"):
            for obj in list(layer_collection.collection.all_objects):
                try:
                    if obj is None:
                        continue
                    if obj.type == 'LIGHT':
                        # Clear LightGroup if it's one we created
                        if obj.lightgroup in groups_to_remove:
                            obj.lightgroup = ""
                            
                        # Skip if it's a child light (has parent which is light)
                        # Although we are deleting them, we should target the master
                        if obj.parent and obj.parent.type == 'LIGHT':
                            continue
                        clean_split_lights(obj)
                except ReferenceError:
                    # Object might have been removed in a previous iteration (e.g. it was a split light of a processed master)
                    continue
                    
        for child in layer_collection.children:
            process_collection_clean(child)
            
    process_collection_clean(bpy.context.view_layer.layer_collection)
    
    # Targeted Light Group Removal (Persistent)
    if hasattr(view_layer, "las_created_lightgroups"):
        to_remove = []
        for item in view_layer.las_created_lightgroups:
            lg = view_layer.lightgroups.get(item.name)
            if lg:
                to_remove.append(lg)
        
        for lg in to_remove:
            try:
                view_layer.lightgroups.remove(lg)
            except Exception as e:
                print(f"Failed to remove lightgroup {lg.name}: {e}")
                
        # Clear the persistent list after removal
        view_layer.las_created_lightgroups.clear()

    # Try to remove unused lightgroups without relying strictly on context-sensitive operator
    try:
        bpy.ops.scene.view_layer_remove_unused_lightgroups()
    except Exception:
        view_layer = bpy.context.view_layer
        unused = []
        for lg in list(view_layer.lightgroups):
            used = False
            for obj in bpy.context.scene.objects:
                if getattr(obj, "lightgroup", "") == lg.name:
                    used = True
                    break
            if getattr(bpy.context.scene, "world", None) and getattr(bpy.context.scene.world, "lightgroup", "") == lg.name:
                used = True

            if not used:
                unused.append(lg)

        for lg in unused:
            try:
                view_layer.lightgroups.remove(lg)
            except Exception:
                pass

# --- Test/restore helpers -------------------------------------------------
def toggle_test_mode():
    """
    Toggle a 'test' viewport state for all lights in collections that start with 'lgt_'.

    When entering test mode: master lights are hidden in viewport (eye off) and their
    split children (named with _diffuse/_specular/_transmission/_volume suffixes) are
    made visible. The previous state for affected objects is stored in
    view_layer.las_test_backup so we can restore later.

    When exiting test mode: restores previous hide/visibility states and clears the
    backup.
    """
    view_layer = bpy.context.view_layer

    # Ensure backup property exists. If it's not registered on the ViewLayer, try
    # to create it dynamically (only possible if the PropertyGroup type has been
    # registered on bpy.types as LAS_TestItem). This helps when the addon was
    # reloaded and properties weren't present for some reason.
    if not hasattr(view_layer, "las_test_backup"):
        if hasattr(bpy.types, "LAS_TestItem"):
            try:
                bpy.types.ViewLayer.las_test_backup = bpy.props.CollectionProperty(type=bpy.types.LAS_TestItem)
                bpy.types.ViewLayer.LAS_test_active = bpy.props.BoolProperty(default=False)
            except Exception:
                return False
        else:
            return False

    active = getattr(view_layer, "LAS_test_active", False)

    if active:
        # restore
        for item in list(view_layer.las_test_backup):
            obj = bpy.data.objects.get(item.name)
            if obj is None:
                continue
            try:
                # hide_get/hide_set manage the "eye" override state in the viewport
                if hasattr(obj, "hide_set"):
                    obj.hide_set(item.hide_eye)
            except Exception:
                # ignore problematic restores
                pass

        view_layer.las_test_backup.clear()
        view_layer.LAS_test_active = False
        return True

    # Enter test mode: store state and apply changes
    view_layer.las_test_backup.clear()
    lobes = ["diffuse", "specular", "transmission", "volume"]

    def process(layer_collection):
        if layer_collection.exclude:
            return

        col_name = layer_collection.collection.name
        if col_name.startswith("lgt_"):
            for obj in list(layer_collection.collection.all_objects):
                if obj is None or obj.type != 'LIGHT':
                    continue

                # skip child lights
                if obj.parent and obj.parent.type == 'LIGHT':
                    continue

                # backup master
                item = view_layer.las_test_backup.add()
                item.name = obj.name
                item.hide_eye = obj.hide_get() if hasattr(obj, "hide_get") else False

                # hide the master in viewport
                if hasattr(obj, "hide_set"):
                    obj.hide_set(True)

                # find children and make them visible
                for lobe in lobes:
                    child = bpy.data.objects.get(f"{obj.name}_{lobe}")
                    if not child:
                        continue
                    child_item = view_layer.las_test_backup.add()
                    child_item.name = child.name
                    child_item.hide_eye = child.hide_get() if hasattr(child, "hide_get") else False

                    if hasattr(child, "hide_set"):
                        child.hide_set(False)

        for child in layer_collection.children:
            process(child)

    process(bpy.context.view_layer.layer_collection)

    view_layer.LAS_test_active = True
    return True
