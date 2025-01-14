import bpy


def auto_lightgroup():
    light_list = []
    # Iterate through all collections in the current Blender scene
    for lc in bpy.context.view_layer.layer_collection.children:
        # Collection object
        collection = lc.collection

        # Filter collections based on name
        if (
            "lgt_" in collection.name
            and lc.exclude is False
            and lc.hide_viewport is False
        ):
            for obj in collection.all_objects:
                if obj.type == "LIGHT":
                    light_list.append(obj.name)
                    bpy.ops.scene.view_layer_add_lightgroup(name=f"{obj.name}")
                    obj.lightgroup = obj.name
    print(light_list)

    return {"FINISHED"}
