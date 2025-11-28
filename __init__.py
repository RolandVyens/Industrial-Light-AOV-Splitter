bl_info = {
    "name": "Industrial Light AOV Splitter",
    "author": "Roland Vyens",
    "version": (0, 6, 2),  # bump doc_url as well!
    "blender": (3, 6, 0),
    "location": "Viewlayer tab in properties panel.",
    "description": "Auto create better light aovs (diffuse_key, specular_key...)",
    "category": "Render",
    "doc_url": "https://github.com/RolandVyens/Industrial-Light-AOV-Splitter",
    "tracker_url": "https://github.com/RolandVyens/Industrial-Light-AOV-Splitter",
}

import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import BoolProperty
from .auto_lightgroup import (
    auto_lightgroup,
    auto_lightaov,
    auto_assign_world,
    assign_missing_object,
    auto_clean_lightaov,
)



"""配置"""


class LAS_AddonPrefs(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    UI_Show_In_Comp: BoolProperty(
        name="Show UI In N Panel",
        description="If enabled, show UI in N panel in addition to the property panel",
        default=False,
    )  # type: ignore

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "UI_Show_In_Comp")


bpy.types.Scene.LAS_fixMissingLight = bpy.props.BoolProperty(  # 是否使用修复模式
    name="Large Scale Mode",
    description="When turned on, fix missing light due to extreme large scene scale",
    default=False,
)


bpy.types.Scene.LAS_sceneMode = bpy.props.BoolProperty(  # 是否使用修复模式
    name="Whole Scene Mode",
    description="When turned on, the light aov creation will be scene-wise instead of per-viewlayer, only works on blender 4.4 and higher",
    default=False,
)


"""操作符"""


class LAS_OT_InitAOVSimple(bpy.types.Operator):
    bl_idname = "object.initlightsimple"
    bl_label = "Make Simple Light AOVs"
    bl_description = 'This will look for all enabled collections which name starts with "lgt_" and create simple light aovs for all lights in it'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        auto_lightgroup()
        self.report(
            {"INFO"}, bpy.app.translations.pgettext("Created For Current Viewlayer")
        )

        return {"FINISHED"}


class LAS_OT_InitAOV(bpy.types.Operator):
    bl_idname = "object.initlightaov"
    bl_label = "Make Advanced Light AOVs"
    bl_description = 'This will look for all enabled collections which name starts with "lgt_" and create splitted light aovs for all lights in it'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        auto_lightgroup()
        auto_lightaov()
        self.report(
            {"INFO"}, bpy.app.translations.pgettext("Created For Current Viewlayer")
        )

        return {"FINISHED"}





class LAS_OT_AssignMissing(bpy.types.Operator):
    bl_idname = "object.assignmissing"
    bl_label = "Auto Assign Emission Objects"
    bl_description = 'Find all emissive objects in the scene as well as the world, assign light groups to them.'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        world_stat = auto_assign_world()
        emissive_stat = assign_missing_object()
        infox = "Assigned light groups to "
        info1 = ""
        info2 = ""
        if world_stat is not 0:
            info1 = f"{world_stat} world, "
        if emissive_stat is not 0:
            info2 = f"{emissive_stat} object"
        infof = infox + info1 + info2
        self.report({"INFO"}, infof)

        self.report({"INFO"}, infof)

        return {"FINISHED"}


class LAS_OT_CleanAOV(bpy.types.Operator):
    bl_idname = "object.cleanlightaov"
    bl_label = "Restore / Clean AOVs"
    bl_description = 'Removes all split lights and restores master lights to renderable state.'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        auto_clean_lightaov()
        self.report(
            {"INFO"}, bpy.app.translations.pgettext("Restored Original Lights")
        )

        return {"FINISHED"}


"""面板"""


class LAS_PT_oPanel_Base:

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.scale_y = 3
        col.operator(LAS_OT_InitAOVSimple.bl_idname, icon="LIGHT")
        col.operator(LAS_OT_InitAOV.bl_idname, icon="OUTLINER_OB_LIGHT")
        col.operator(LAS_OT_CleanAOV.bl_idname, icon="TRASH")
        layout.prop(context.scene, "LAS_fixMissingLight")
        layout.label(text="Tools:")
        layout.operator(LAS_OT_AssignMissing.bl_idname, icon="APPEND_BLEND")



class LAS_PT_oPanel(bpy.types.Panel, LAS_PT_oPanel_Base):
    bl_label = "Industrial Light AOV Splitter"
    bl_idname = "RENDER_PT_industrialsplitter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "view_layer"


class LAS_PT_oPanel_COMP(bpy.types.Panel, LAS_PT_oPanel_Base):
    bl_label = "Industrial Light AOV Splitter"
    bl_idname = "COMP_PT_industrialsplitter"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Industrial"

    @classmethod
    def poll(cls, context):
        preferences = bpy.context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        # Ensure the panel only shows when in the compositor editor
        return (
            context.space_data.tree_type == "CompositorNodeTree"
            and addon_prefs.UI_Show_In_Comp is True
        )


class LAS_PT_oPanel_N(bpy.types.Panel, LAS_PT_oPanel_Base):
    bl_label = "Industrial Light AOV Splitter"
    bl_idname = "VIEW3D_PT_industrialsplitter"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Industrial"

    @classmethod
    def poll(cls, context):
        preferences = bpy.context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        # Ensure the panel only shows when in the compositor editor
        return (
            context.space_data.type == "VIEW_3D" and addon_prefs.UI_Show_In_Comp is True
        )


"""以下为注册函数"""
reg_clss = [
    LAS_AddonPrefs,
    LAS_OT_InitAOVSimple,
    LAS_OT_InitAOV,
    LAS_OT_CleanAOV,
    LAS_OT_AssignMissing,
    LAS_PT_oPanel,
    LAS_PT_oPanel_COMP,
    LAS_PT_oPanel_N,

]


def register():
    for i in reg_clss:
        bpy.utils.register_class(i)
    # bpy.app.translations.register(__package__, language_dict)



def unregister():
    for i in reg_clss:
        bpy.utils.unregister_class(i)
    # bpy.app.translations.unregister(__package__)



if __name__ == "__main__":
    register()
