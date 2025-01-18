bl_info = {
    "name": "Industrial Light Splitter",
    "author": "Roland Vyens",
    "version": (0, 1, 0),  # bump doc_url as well!
    "blender": (4, 0, 0),
    "location": "Viewlayer tab in properties panel.",
    "description": "Auto generate outputs for advanced compositing.",
    "category": "Render",
    "doc_url": "https://github.com/RolandVyens/Industrial-AOV-Connector",
    "tracker_url": "https://github.com/RolandVyens/Industrial-AOV-Connector/issues",
}

import bpy
from .auto_lightgroup import auto_lightgroup, auto_lightaov
from .auto_aov_renderscript import auto_assignlight_scene, auto_restorelight_scene


class LAS_OT_InitAOV(bpy.types.Operator):
    bl_idname = "object.initlightaov"
    bl_label = "Make Light AOVs For Current Layer"
    bl_description = 'This will look for all enabled collections which name starts with "lgt_" and create splitted light aovs for all lights in it'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        auto_lightgroup()
        auto_lightaov()
        

class LAS_PT_oPanel_Base:

    def draw(self, context):
        layout=self.layout
        col = layout.column()
        col.scale_y = 3
