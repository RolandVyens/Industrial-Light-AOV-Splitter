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
            and lc.hide_render is False
        ):
            for obj in collection.all_objects:
                if obj.type == "LIGHT":
                    light_list.append(obj.name)
                    bpy.ops.scene.view_layer_add_lightgroup(name=f"{obj.name}")
                    obj.lightgroup = obj.name
    print(light_list)
    bpy.ops.scene.view_layer_remove_unused_lightgroups()

    return {"finished"}


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


def auto_assignlight():
    view_layer = bpy.context.view_layer
    lightgroups = [lg.name for lg in view_layer.lightgroups]
    light_objects = [
        obj for obj in bpy.context.view_layer.objects if obj.type == "LIGHT"
    ]
    temp_light = []
    for lightgroup in lightgroups:
        for lobe in ["diffuse_", "specular_", "transmission_", "volume_"]:
            if lightgroup.startswith(f"{lobe}"):
                light = lightgroup.removeprefix(f"{lobe}")
                for light_object in light_objects:
                    if light_object.name == light or light_object.name[:-4] == light:
                        obj = bpy.data.objects.get(light_object.name)
                        duplicate = obj.copy()
                        duplicate.data = obj.data.copy()
                        bpy.context.scene.collection.objects.link(duplicate)
                        duplicate.name = f"{lobe}{light}"
                        duplicate.lightgroup = lightgroup
                        temp_light.append(light)
    for light in temp_light:
        obj = bpy.data.objects.get(light)
        obj.hide_render = True

    return {"finished"}


def auto_assignlight_scene():
    lightgroup_dict = {}
    lightcollection_dict = {}
    light_dict = {}
    for viewlayer in bpy.context.scene.view_layers:
        if viewlayer.name[:7] != "-_-exP_" and "_DATA" not in viewlayer.name:
            lightgroups = []
            for lightgroup in viewlayer.lightgroups:
                lightgroups.append(lightgroup.name)
            lightgroup_dict[viewlayer.name] = lightgroups
        for collection in viewlayer.layer_collection.children:
            light_collection = []
            if collection.name.startswith("lgt_") and collection.exclude == False:
                light_collection.append(collection.name)
                lightcollection_dict[viewlayer.name] = light_collection
                lights = []
                for object in bpy.data.collections[collection.name].all_objects:
                    if object.type == "LIGHT":
                        lights.append(object.name)
                light_dict[viewlayer.name] = lights
    LAS_originLight = []
    LAS_newLight = []
    for key in lightgroup_dict.keys():
        for lightgroup in lightgroup_dict[key]:
            for lobe in ["diffuse_", "specular_", "transmission_", "volume_"]:
                if lightgroup.startswith(f"{lobe}"):
                    light = lightgroup.removeprefix(f"{lobe}")
                    for light_object_name in light_dict[key]:
                        light_object = bpy.context.scene.objects.get(light_object_name)
                        if (
                            light_object.name == light
                            or light_object.name[:-4] == light
                        ):
                            obj = bpy.data.objects.get(light_object.name)
                            duplicate = obj.copy()
                            duplicate.data = obj.data.copy()
                            bpy.data.collections[
                                lightcollection_dict[key][0]
                            ].objects.link(duplicate)
                            duplicate.name = f"{lobe}{light}"
                            duplicate.lightgroup = lightgroup
                            duplicate.visible_diffuse = False
                            duplicate.visible_glossy = False
                            duplicate.visible_transmission = False
                            duplicate.visible_volume_scatter = False
                            LAS_newLight.append(duplicate.name)
                            if lobe == "diffuse_":
                                duplicate.visible_diffuse = True
                            if lobe == "specular_":
                                duplicate.visible_glossy = True
                            if lobe == "transmission_":
                                duplicate.visible_transmission = True
                            if lobe == "volume_":
                                duplicate.visible_volume_scatter = True
                            LAS_originLight.append(light)
    for light in LAS_originLight:
        obj = bpy.data.objects.get(light)
        obj.hide_render = True

    print(lightgroup_dict)
    print(lightcollection_dict)
    print(light_dict)

    return {"finished"}
