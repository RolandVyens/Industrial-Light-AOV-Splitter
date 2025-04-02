# Industrial Light AOV Splitter / 工业化灯光AOV创建器

### 更细化的灯光aov，工业化灯光AOV创建器

### Materialized light group auto builder for blender
======================

<img width="306" alt="屏幕截图 2025-03-24 002000" src="https://github.com/user-attachments/assets/ced546ac-6e82-4bd8-beea-53676840df0f" />

**插件面板位置：属性面板→视图层**

**Plugin panel location: Properties Panel→View Layer**

Install on [blender extensions](https://extensions.blender.org/add-ons/industrial-light-aov-splitter/)

recommended to use with [Industrial AOV Connector](https://github.com/RolandVyens/Industrial-AOV-Connector)

======================

目前支持3.6 - 最新版 Supports blender 3.6 - newest by now (2025.01.31)

通过基本无感的方式，自动给符合条件的灯创建灯光组，把灯光分离成diffuse, specular, transmission, volume四个通道(如diffuse_env, specular_env...)，以取得与行业接轨的可控性（合成软件内）。也可一键给场景内的世界环境和发光物体打上灯光组。

Separate the light groups into four channels: diffuse, specular, transmission, and volume (e.g., diffuse_env, specular_env...) with one click, to achieve industry-standard controllability during the compositing stage. Also can automatically give light groups to world and emissive objects.

**有配套的nuke自动shuffle脚本！**

**Comes with a nuke auto-shuffle-combine script!**

join our [discord](https://discord.gg/wGzAAQSMce)

---
**Update Log:**

2025.3.24: version 0.6.0

- fix some bug
- add more debug output for render script
- added button for auto assign light group to emissive objects and world environment
- added simple light group assign
- update nuke script, now you can create light group aov tree from any node

2025.1.31: version 0.5.0

1. initial release, with basic functions.

---

### HOW TO USE:

1. **Blender light group aovs are stored at viewlayer level, so this plugin runs per viewlayer by now. In 4.4 there will be a new method to create all light groups in a scene**
![屏幕截图 2025-01-31 235127](https://github.com/user-attachments/assets/195364a8-76fe-4985-9933-1f84b849efd5)

3. **Put your lights in collections whose name starts with "lgt_".**
4. **Naming your light properly with letters and numbers only. Do not use any "_"**
5. **Press one of the function button to generate current viewlayer's light group. Note that only enabled collection will count. Now you can assign traditional light group as well.**
6. **If you want to reuse light group between multiple lights, just duplicate the lights and keep their auto-generated ".001" number suffix, they'll be ignored and revert back to the desired name.**
6. **To test the generated light groups, you may need to use the test button in viewport shading mode, if nothing goes wrong, you won't see any change in lighting. Remember to restore the operation.**
7. **To quickly assign emission objects and world environment light group, there is a button to do so.**

---

### 使用方法：

1. **Blender灯光组AOV存储在视图层级别，因此目前此插件按视图层运行。在4.4版本中，将有一种新方法来创建场景中的所有灯光组。**
![屏幕截图 2025-01-31 235127](https://github.com/user-attachments/assets/195364a8-76fe-4985-9933-1f84b849efd5)
3. **将你的灯光放入名称以“lgt_”开头的集合中。**
4. **正确命名你的灯光，仅使用字母和数字。不要使用任何下划线（“_”）。**
5. **点击其中一个功能按钮为当前视图层生成灯光组。注意只有启用的集合才会被处理。现在你也可以一键生成传统灯光组。**
6. **如果你想在多个灯光之间重用灯光组，只需复制灯光并保留其自动生成的“.001”编号后缀。它们将被忽略并恢复为所需的名称。**
6. **为了测试生成的灯光组，你需要在视窗渲染模式下点击测试按钮，如果没问题的话，灯光效果不会发生任何改变。记得撤回操作。**
7. **现在有专门的按钮用于一键赋予所有发光物体和世界环境灯光组。**

---

### [Fr. document](https://github.com/RolandVyens/Industrial-Light-AOV-Splitter/blob/main/misc/Industrial_Light_AOV_slitter_manual_French.pdf)

---

### Nuke auto shuffle script installation

[**Download**](https://github.com/RolandVyens/Industrial-Light-AOV-Splitter/releases/download/release0.5.0/nuke_blender_autoaov.py)

<img width="1920" alt="屏幕截图 2025-02-24 140802" src="https://github.com/user-attachments/assets/1e684633-bf7c-4e89-ae0e-237df29db643" />

1. copy the `nuke_blender_autoaov.py` to your .nuke directory
2. in your `menu.py` (create one if there's no such file in .nuke), paste the following code:
   ```
   import nuke_blender_autoaov
   utilitiesMenu = nuke.menu('Nuke').addMenu('Industrial')
   utilitiesMenu.addCommand('nuke_blender_autoaov','nuke_blender_autoaov.shuffle_and_combine_light_groups()')
   ```

---

### Nuke自动shuffle脚本安装

1. 将 `nuke_blender_autoaov.py` 复制到你的 .nuke 目录中
2. 在你的 `menu.py` 文件中（如果 .nuke 中没有此文件，请创建一个），粘贴以下代码：
   ```
   import nuke_blender_autoaov
   utilitiesMenu = nuke.menu('Nuke').addMenu('Industrial')
   utilitiesMenu.addCommand('nuke_blender_autoaov','nuke_blender_autoaov.shuffle_and_combine_light_groups()')
   ```
