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

    return light_list


def auto_lightaov():
    view_layer = bpy.context.view_layer
    lightgroups = [lg.name for lg in view_layer.lightgroups]
    light_objects = [
        obj for obj in bpy.context.view_layer.objects if obj.type == "LIGHT"
    ]
    real_lights = []
    for light in light_objects:
        if light.lightgroup in lightgroups:
            real_lights.append(light.lightgroup)
            light.lightgroup = str()
    if real_lights:
        bpy.ops.scene.view_layer_remove_unused_lightgroups()
    else:
        return {"finished"}
    real_lights = list(set(real_lights))
    lightdict = {}
    visible_set = []
    for light in real_lights:
        lightobj = bpy.context.view_layer.objects.get(light)
        visible_set = [
            lightobj.visible_diffuse,
            lightobj.visible_glossy,
            lightobj.visible_transmission,
            lightobj.visible_volume_scatter,
        ]
        lightdict[light] = visible_set
        visible_set = []
        if lightdict[light][0] is True:
            bpy.ops.scene.view_layer_add_lightgroup(name=f"diffuse_{light}")
        if lightdict[light][1] is True:
            bpy.ops.scene.view_layer_add_lightgroup(name=f"specular_{light}")
        if lightdict[light][2] is True:
            bpy.ops.scene.view_layer_add_lightgroup(name=f"transmission_{light}")
        if lightdict[light][3] is True:
            bpy.ops.scene.view_layer_add_lightgroup(name=f"volume_{light}")
    # print(lightdict)

    return {"finished"}
