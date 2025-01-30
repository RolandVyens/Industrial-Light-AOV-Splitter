bl_info = {
    "name": "Industrial Light AOV Splitter",
    "author": "Roland Vyens",
    "version": (0, 5, 0),  # bump doc_url as well!
    "blender": (3, 6, 0),
    "location": "Viewlayer tab in properties panel.",
    "description": "Auto generate outputs for advanced compositing.",
    "category": "Render",
    "doc_url": "https://github.com/RolandVyens/Industrial-Light-AOV-Splitter",
    "tracker_url": "https://github.com/RolandVyens/Industrial-Light-AOV-Splitter",
}

import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import BoolProperty
from .auto_lightgroup import auto_lightgroup, auto_lightaov
from .auto_aov_renderscript import auto_assignlight_scene, auto_restorelight_scene


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


class LAS_OT_InitAOV(bpy.types.Operator):
    bl_idname = "object.initlightaov"
    bl_label = "Make Light AOVs For Current Layer"
    bl_description = 'This will look for all enabled collections which name starts with "lgt_" and create splitted light aovs for all lights in it'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        auto_lightgroup()
        auto_lightaov()
        self.report(
            {"INFO"}, bpy.app.translations.pgettext("Created For Current Viewlayer")
        )

        return {"FINISHED"}


class LAS_OT_CloudMode(bpy.types.Operator):
    bl_idname = "object.cloudmodelas"
    bl_label = "Renderfarm Prepare"
    bl_description = "Precreate all lights in order to send to render farm"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        auto_assignlight_scene(bpy.context.scene)
        self.report({"INFO"}, bpy.app.translations.pgettext("Pre-created All Lights"))

        return {"FINISHED"}


class LAS_PT_oPanel_Base:

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.scale_y = 3
        col.operator(LAS_OT_InitAOV.bl_idname, icon="OUTLINER_OB_LIGHT")
        col.operator(LAS_OT_CloudMode.bl_idname, icon="SCREEN_BACK")


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
    bl_idname = "3DVIEW_PT_industrialsplitter"
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
    LAS_OT_InitAOV,
    LAS_PT_oPanel,
    LAS_PT_oPanel_COMP,
    LAS_PT_oPanel_N,
    LAS_OT_CloudMode
]


def register():
    for i in reg_clss:
        bpy.utils.register_class(i)
    # bpy.app.translations.register(__package__, language_dict)
    bpy.app.handlers.render_init.append(auto_assignlight_scene)
    bpy.app.handlers.render_cancel.append(auto_restorelight_scene)
    bpy.app.handlers.render_complete.append(auto_restorelight_scene)


def unregister():
    for i in reg_clss:
        bpy.utils.unregister_class(i)
    # bpy.app.translations.unregister(__package__)
    bpy.app.handlers.render_init.remove(auto_assignlight_scene)
    bpy.app.handlers.render_cancel.remove(auto_restorelight_scene)
    bpy.app.handlers.render_complete.remove(auto_restorelight_scene)


if __name__ == "__main__":
    register()
