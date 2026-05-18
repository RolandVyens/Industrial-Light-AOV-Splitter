# AI Agent Guide for Industrial Light AOV Splitter

> This document provides context for AI coding assistants working on this Blender addon.  
> 本文档为AI编程助手提供此Blender插件的上下文信息。

---

## Project Overview / 项目概述

**Industrial Light AOV Splitter** is a Blender addon that automatically creates industry-standard light group AOVs (Arbitrary Output Variables) for compositing workflows. It splits lights into 4 material channels: **diffuse**, **specular**, **transmission**, and **volume**.

这是一个Blender插件，用于自动创建符合行业标准的灯光组AOV（任意输出变量），将灯光分离为4个材质通道：漫反射、高光、透射和体积。

---

## Directory Structure / 目录结构

```
Industrial-Light-AOV-Splitter/
├── __init__.py              # Addon entry point, operators, UI panels / 插件入口、操作符、面板
├── auto_lightgroup.py       # Core light splitting logic / 核心灯光分离逻辑
├── blender_manifest.toml    # Blender 4.2+ extension manifest
├── build_release.py         # Release zip builder for Blender extension packaging
├── README.md                # User documentation (bilingual)
├── LICENSE                  # GPL-3.0 license
├── lightaov_demo.blend      # Demo/test file
├── misc/                    # Additional resources
│   └── Industrial_Light_AOV_slitter_manual_French.pdf
└── nukescript/              # Companion Nuke compositing script
    └── nuke_blender_autoaov.py
```

---

## Key Components / 关键组件

### `__init__.py` - Addon Entry Point

| Component | Type | Purpose |
|-----------|------|---------|
| `bl_info` | Dict | Addon metadata (name, version, Blender requirements) |
| `LAS_AddonPrefs` | AddonPreferences | User preferences (e.g., `UI_Show_In_Comp`) |
| `LAS_LightGroupItem` | PropertyGroup | Stores lightgroup names in ViewLayer |
| `LAS_TestItem` | PropertyGroup | Stores visibility backup for test mode |
| `LAS_OT_InitAOVSimple` | Operator | Creates simple light groups (no splitting) |
| `LAS_OT_InitAOV` | Operator | Creates advanced split light AOVs |
| `LAS_OT_CleanAOV` | Operator | Removes split lights, restores masters |
| `LAS_OT_AssignMissing` | Operator | Assigns lightgroups to emissive objects/world |
| `LAS_OT_TestToggle` | Operator | Toggles test mode (hide master, show children) |
| `LAS_PT_oPanel*` | Panels | UI in Properties > View Layer, Compositor N-panel, 3D View N-panel |

**Scene Properties:**
- `Scene.LAS_fixMissingLight` - Large Scale Mode (fixes light loss in huge scenes)
- `Scene.LAS_sceneMode` - Whole Scene Mode (Blender 4.4+ only)

**ViewLayer Properties (registered at runtime):**
- `ViewLayer.las_created_lightgroups` - CollectionProperty tracking created lightgroups
- `ViewLayer.las_test_backup` - CollectionProperty for test mode visibility backup
- `ViewLayer.LAS_test_active` - BoolProperty indicating test mode state

---

### `auto_lightgroup.py` - Core Logic

#### Main Functions

| Function | Purpose |
|----------|---------|
| `auto_lightgroup()` | Assigns lightgroups to lights in `lgt_*` collections (simple mode) |
| `auto_lightaov()` | Creates split lights (diffuse/specular/transmission/volume suffixes) |
| `create_split_lights(master_obj, collection)` | Creates 4 child lights with drivers linked to master |
| `auto_clean_lightaov()` | Removes split lights and associated lightgroups |
| `clean_split_lights(master_obj)` | Removes children of a single master light |
| `auto_assign_world()` | Assigns "env" lightgroup to world |
| `assign_missing_object()` | Finds emissive objects, assigns "emissive_default" lightgroup |
| `toggle_test_mode()` | Toggles viewport visibility between master and split lights |
| `setup_driver(source_obj, target_obj, data_path)` | Creates driver linking child property to master |

#### Key Data Structures

```python
LIGHT_PROPERTIES = {
    'POINT': ['color', 'energy', 'specular_factor', ...],
    'SPOT':  ['color', 'energy', 'spot_size', 'spot_blend', ...],
    'AREA':  ['color', 'energy', 'shape', 'size', 'spread', ...],
    'SUN':   ['color', 'energy', 'angle', 'shadow_cascade_*', ...],
}
```
This dictionary defines which properties are driven from master to child lights, per light type.

#### Light Naming Convention

- Collection: Must start with `lgt_` (e.g., `lgt_key`, `lgt_fill`)
- Master light: Any name (e.g., `sun`)
- Split children: `{master_name}_{lobe}` (e.g., `sun_diffuse`, `sun_specular`, `sun_transmission`, `sun_volume`)
- Lightgroup names: `{lobe}_{base_name}` (e.g., `diffuse_sun`, `specular_sun`)

#### Test Mode Flow

1. **Enter test mode**: Store current visibility states → Hide masters → Show split children
2. **Exit test mode**: Restore previous visibility states from `las_test_backup`

---

### `nukescript/nuke_blender_autoaov.py` - Nuke Companion

A standalone Nuke script that:
1. Reads EXR channels from selected Read node
2. Identifies `RGBA_*` light group channels
3. Creates Shuffle2 nodes for each channel
4. Creates Merge (plus) nodes to recombine lobes per light
5. Creates final merge to combine all lights

**Not imported by Blender** - this is a separate utility for Nuke compositing.

---

## Blender API Patterns Used / 使用的Blender API模式

### Operator ID Naming
All operators use `object.*` prefix: `object.initlightsimple`, `object.initlightaov`, etc.

### Property Registration
```python
# Scene-level (in module body, auto-registered)
bpy.types.Scene.LAS_fixMissingLight = bpy.props.BoolProperty(...)

# ViewLayer-level (in register function)
bpy.types.ViewLayer.las_created_lightgroups = bpy.props.CollectionProperty(type=LAS_LightGroupItem)
```

### Driver Setup Pattern
```python
fcurves = target_obj.driver_add(data_path)  # Returns FCurve or list[FCurve]
for fcurve in fcurves:
    driver = fcurve.driver
    driver.type = 'AVERAGE'
    var = driver.variables.new()
    var.targets[0].id = source_obj
    var.targets[0].data_path = f"data.{data_path}"
```

### Collection Traversal Pattern
```python
def process(layer_collection):
    if layer_collection.exclude:
        return
    if layer_collection.collection.name.startswith("lgt_"):
        # Process objects
        pass
    for child in layer_collection.children:
        process(child)

process(bpy.context.view_layer.layer_collection)
```

---

## Known Issues & Technical Debt / 已知问题

1. **Principled BSDF emission lookup**:
   Prefer named socket lookup for emission inputs because socket indices can shift between Blender releases.

2. **Duplicated helper pattern** - Lightgroup tracking logic is repeated 5+ times:
   ```python
   already_tracked = False
   for item in view_layer.las_created_lightgroups:
       if item.name == lg_name:
           already_tracked = True
           break
   if not already_tracked:
       item = view_layer.las_created_lightgroups.add()
       item.name = lg_name
   ```
   Recommend extracting to `_track_lightgroup(view_layer, name)`.

3. **Duplicated unused lightgroup removal** - Same fallback logic in `auto_lightgroup()` and `auto_clean_lightaov()`.

4. **Missing type hints** - No Python type annotations.

5. **Context dependency** - Functions use `bpy.context` directly. Consider accepting context/view_layer as parameters for render-farm compatibility.

---

## Version Compatibility / 版本兼容性

| Blender Version | Status |
|-----------------|--------|
| 4.1 - 4.3 | ✅ Fully supported |
| 4.4+ | ✅ Supported + Whole Scene Mode |
| 5.0 | ✅ Supported |
| 5.2 | ✅ Supported |

**Cycles-specific properties**: `cycles.is_caustics_light`, `cycles.is_portal` are only available when Cycles is the active render engine.

---

## Common Modification Scenarios / 常见修改场景

### Adding a New Light Property to Drive

1. Add property path to `LIGHT_PROPERTIES` dict in `auto_lightgroup.py`
2. Handle nested paths (e.g., `cycles.new_property`) with dot notation

### Adding a New Operator

1. Create class inheriting from `bpy.types.Operator`
2. Add to `reg_clss` list in `__init__.py`
3. Add button to `LAS_PT_oPanel_Base.draw()`

### Adding a New Scene/ViewLayer Property

1. Define property on `bpy.types.Scene` or `bpy.types.ViewLayer`
2. If ViewLayer property, register in `register()` and clean up in `unregister()`

---

## Testing Recommendations / 测试建议

1. Use `lightaov_demo.blend` for manual testing
2. Test with different light types: POINT, SPOT, AREA, SUN
3. Test Large Scale Mode with scene scales > 1000 units
4. Test cleanup/restore functionality
5. Test driver updates when modifying master light properties

---

## Packaging for Distribution

### Release Workflow

1. Update version numbers in both:
   - `__init__.py` -> `bl_info["version"]`
   - `blender_manifest.toml` -> `version`
2. Update user-facing release notes when needed:
   - `README.md` update log and support range
3. Run automated validation in the Blender 5.2 test build:
   - `& 'C:\Program Files\Blender Foundation\blender-vfx-5.2-2026-04-22\blender.exe' --background --factory-startup --python-exit-code 1 --python tests/run_blender_tests.py`
4. Build the release zip:
   - `python build_release.py`
5. Confirm the output exists:
   - `dist/Industrial-Light-AOV-Splitter <version>.zip`
6. If the release is accepted, commit the source changes. The built zip is an output artifact and does not need to be committed unless explicitly requested.

### Packaging Rules

- Use `build_release.py` for packaging.
- Use Python `zipfile`, not PowerShell `Compress-Archive`.
- Blender extension installs are sensitive to archive paths; the zip must use forward slashes and include the root directory entry.
- The current package intentionally follows the historical structure from `Industrial-Light-AOV-Splitter 1.0.1.zip`.

### Expected Zip Structure

- `Industrial-Light-AOV-Splitter/`
- `Industrial-Light-AOV-Splitter/__init__.py`
- `Industrial-Light-AOV-Splitter/auto_lightgroup.py`
- `Industrial-Light-AOV-Splitter/blender_manifest.toml`

### Packaging Script Notes

- Script path: `build_release.py`
- Output naming pattern: `dist/Industrial-Light-AOV-Splitter <version>.zip`
- Current include list is intentionally minimal and runtime-only:
  - `__init__.py`
  - `auto_lightgroup.py`
  - `blender_manifest.toml`
- Do not add dev-only content such as `tests/`, `__pycache__/`, `.git/`, or `AGENT.md` to the release archive unless the packaging target changes.

---

## File Modification Checklist / 文件修改检查清单

When modifying this addon:

- [ ] Ensure `bl_info["version"]` is updated for releases
- [ ] Update `blender_manifest.toml` version for extension releases
- [ ] Test with multiple Blender versions (4.1, 4.4, 5.0, 5.2)
- [ ] Verify all operators have `bl_options = {"REGISTER", "UNDO"}`
- [ ] Check error handling for missing properties (version differences)
- [ ] Update README.md if user-facing behavior changes
