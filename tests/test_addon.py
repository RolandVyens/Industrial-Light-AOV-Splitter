import importlib
import os
import unittest

import bpy


ADDON_MODULE = os.environ["ILAS_ADDON_MODULE"]
addon = importlib.import_module(ADDON_MODULE)
core = importlib.import_module(f"{ADDON_MODULE}.auto_lightgroup")


def lightgroup_names():
    return {lightgroup.name for lightgroup in bpy.context.view_layer.lightgroups}


class AddonTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        addon.register()

    @classmethod
    def tearDownClass(cls):
        addon.unregister()

    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        if bpy.context.scene.world is None:
            bpy.context.scene.world = bpy.data.worlds.new("World")

    def create_light_collection(self, collection_name="lgt_key", light_name="key", light_type="POINT"):
        collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(collection)
        light_data = bpy.data.lights.new(name=f"{light_name}_data", type=light_type)
        light_object = bpy.data.objects.new(light_name, light_data)
        collection.objects.link(light_object)
        return collection, light_object

    def create_emissive_object(self, object_name="emissive_cube"):
        mesh = bpy.data.meshes.new(f"{object_name}_mesh")
        obj = bpy.data.objects.new(object_name, mesh)
        bpy.context.scene.collection.objects.link(obj)

        material = bpy.data.materials.new(name=f"{object_name}_material")
        material.use_nodes = True
        principled = next(node for node in material.node_tree.nodes if node.type == "BSDF_PRINCIPLED")

        emission_strength = principled.inputs.get("Emission Strength")
        if emission_strength is not None:
            emission_strength.default_value = 3.0

        emission_color = principled.inputs.get("Emission Color")
        if emission_color is not None:
            emission_color.default_value = (0.8, 0.4, 0.2, 1.0)

        obj.data.materials.append(material)
        return obj, material, principled

    def test_register_unregister_manage_viewlayer_properties(self):
        addon.unregister()
        self.assertFalse(hasattr(bpy.types.ViewLayer, "las_created_lightgroups"))
        self.assertFalse(hasattr(bpy.types.ViewLayer, "las_test_backup"))
        self.assertFalse(hasattr(bpy.types.ViewLayer, "LAS_test_active"))

        addon.register()
        self.assertTrue(hasattr(bpy.types.ViewLayer, "las_created_lightgroups"))
        self.assertTrue(hasattr(bpy.types.ViewLayer, "las_test_backup"))
        self.assertTrue(hasattr(bpy.types.ViewLayer, "LAS_test_active"))

    def test_principled_has_emission_detects_named_sockets(self):
        _, _, principled = self.create_emissive_object()
        self.assertTrue(core._principled_has_emission(principled))

    def test_setup_driver_creates_energy_and_color_drivers(self):
        _, master = self.create_light_collection()
        target_data = master.data.copy()

        core.setup_driver(master, target_data, "energy")
        core.setup_driver(master, target_data, "color")

        drivers = list(target_data.animation_data.drivers)
        data_paths = {driver.data_path for driver in drivers}
        self.assertIn("energy", data_paths)
        self.assertIn("color", data_paths)

        energy_driver = next(driver for driver in drivers if driver.data_path == "energy")
        self.assertEqual(energy_driver.driver.variables[0].targets[0].data_path, "data.energy")

        color_paths = sorted(
            driver.driver.variables[0].targets[0].data_path
            for driver in drivers
            if driver.data_path == "color"
        )
        self.assertEqual(
            color_paths,
            ["data.color[0]", "data.color[1]", "data.color[2]"],
        )

    def test_create_split_lights_creates_children_and_groups(self):
        collection, master = self.create_light_collection(light_name="hero")

        core.create_split_lights(master, collection)

        expected_children = {
            "hero_diffuse": "diffuse_hero",
            "hero_specular": "specular_hero",
            "hero_transmission": "transmission_hero",
            "hero_volume": "volume_hero",
        }
        self.assertTrue(master.hide_render)
        self.assertTrue(set(expected_children.values()) <= lightgroup_names())

        for child_name, lightgroup in expected_children.items():
            child = bpy.data.objects.get(child_name)
            self.assertIsNotNone(child, child_name)
            self.assertEqual(child.parent, master)
            self.assertEqual(child.lightgroup, lightgroup)
            self.assertFalse(child.hide_render)

    def test_auto_lightgroup_assigns_group_to_master_light_only(self):
        collection, master = self.create_light_collection(light_name="sun")
        child_data = bpy.data.lights.new(name="sun_child_data", type="POINT")
        child = bpy.data.objects.new("sun_child", child_data)
        child.parent = master
        collection.objects.link(child)

        core.auto_lightgroup()

        self.assertEqual(master.lightgroup, "sun")
        self.assertEqual(child.lightgroup, "")
        self.assertIn("sun", lightgroup_names())

    def test_auto_lightaov_creates_split_lights_for_lgt_collections(self):
        _, master = self.create_light_collection(light_name="fill")

        core.auto_lightaov()

        self.assertTrue(master.hide_render)
        self.assertIsNotNone(bpy.data.objects.get("fill_diffuse"))
        self.assertIn("diffuse_fill", lightgroup_names())

    def test_auto_assign_world_sets_env_lightgroup(self):
        bpy.context.scene.world.lightgroup = ""

        result = core.auto_assign_world()

        self.assertEqual(result, 1)
        self.assertEqual(bpy.context.scene.world.lightgroup, "env")
        self.assertIn("env", lightgroup_names())

    def test_assign_missing_object_sets_emissive_default(self):
        obj, _, _ = self.create_emissive_object()

        result = core.assign_missing_object()

        self.assertEqual(result, 1)
        self.assertEqual(obj.lightgroup, "emissive_default")
        self.assertIn("emissive_default", lightgroup_names())

    def test_clean_split_lights_removes_children(self):
        collection, master = self.create_light_collection(light_name="rim")
        core.create_split_lights(master, collection)

        core.clean_split_lights(master)

        self.assertFalse(master.hide_render)
        self.assertIsNone(bpy.data.objects.get("rim_diffuse"))
        self.assertIsNone(bpy.data.objects.get("rim_specular"))
        self.assertIsNone(bpy.data.objects.get("rim_transmission"))
        self.assertIsNone(bpy.data.objects.get("rim_volume"))

    def test_auto_clean_lightaov_removes_split_lights_and_tracked_groups(self):
        collection, master = self.create_light_collection(light_name="kick")
        core.create_split_lights(master, collection)

        core.auto_clean_lightaov()

        self.assertFalse(master.hide_render)
        self.assertFalse({"diffuse_kick", "specular_kick"} & lightgroup_names())
        self.assertEqual(len(bpy.context.view_layer.las_created_lightgroups), 0)
        self.assertIsNone(bpy.data.objects.get("kick_diffuse"))

    def test_toggle_test_mode_hides_masters_then_restores_previous_state(self):
        collection, master = self.create_light_collection(light_name="bounce")
        core.create_split_lights(master, collection)
        child = bpy.data.objects["bounce_diffuse"]
        original_child_hidden = child.hide_get()

        entered = core.toggle_test_mode()
        self.assertTrue(entered)
        self.assertTrue(bpy.context.view_layer.LAS_test_active)
        self.assertTrue(master.hide_get())
        self.assertFalse(child.hide_get())

        restored = core.toggle_test_mode()
        self.assertTrue(restored)
        self.assertFalse(bpy.context.view_layer.LAS_test_active)
        self.assertFalse(master.hide_get())
        self.assertEqual(child.hide_get(), original_child_hidden)

    def test_operator_init_simple_executes(self):
        _, master = self.create_light_collection(light_name="simple")

        result = bpy.ops.object.initlightsimple()

        self.assertEqual({"FINISHED"}, result)
        self.assertEqual(master.lightgroup, "simple")

    def test_operator_init_advanced_executes(self):
        _, master = self.create_light_collection(light_name="advanced")

        result = bpy.ops.object.initlightaov()

        self.assertEqual({"FINISHED"}, result)
        self.assertTrue(master.hide_render)
        self.assertIsNotNone(bpy.data.objects.get("advanced_diffuse"))

    def test_operator_assign_missing_executes(self):
        obj, _, _ = self.create_emissive_object()

        result = bpy.ops.object.assignmissing()

        self.assertEqual({"FINISHED"}, result)
        self.assertEqual(obj.lightgroup, "emissive_default")
        self.assertEqual(bpy.context.scene.world.lightgroup, "env")

    def test_operator_clean_executes(self):
        _, master = self.create_light_collection(light_name="cleanup")
        core.auto_lightgroup()
        core.auto_lightaov()

        result = bpy.ops.object.cleanlightaov()

        self.assertEqual({"FINISHED"}, result)
        self.assertFalse(master.hide_render)
        self.assertIsNone(bpy.data.objects.get("cleanup_diffuse"))

    def test_operator_test_toggle_executes(self):
        collection, _ = self.create_light_collection(light_name="toggle")
        core.create_split_lights(bpy.data.objects["toggle"], collection)

        first = bpy.ops.object.testtoggle()
        second = bpy.ops.object.testtoggle()

        self.assertEqual({"FINISHED"}, first)
        self.assertEqual({"FINISHED"}, second)
        self.assertFalse(bpy.context.view_layer.LAS_test_active)
