# Industrial Light AOV Splitter / 工业化灯光AOV创建器

### 更细化的灯光aov，工业化灯光AOV创建器

### Materialized light group auto builder for blender
======================

![屏幕截图 2025-01-31 233806](https://github.com/user-attachments/assets/39c8bdc9-a9c3-46f8-bbdf-9fe23bd8cf6a)

**插件面板位置：属性面板→视图层**

**Plugin panel location: Properties Panel→View Layer**

recommended to use with [Industrial AOV Connector](https://github.com/RolandVyens/Industrial-AOV-Connector)

======================

目前支持3.6 - 最新版 Supports blender 3.6 - newest by now (2025.01.31)

通过基本无感的方式，自动给符合条件的灯创建灯光组，把灯光分离成diffuse, specular, transmission, volume四个通道(如diffuse_env, specular_env...)，以取得与行业接轨的可控性（合成软件内）。

Separate the lights into four channels: diffuse, specular, transmission, and volume (e.g., diffuse_env, specular_env...) with one click, to achieve industry-standard controllability during the compositing stage.

**有配套的nuke自动shuffle脚本！**

**Comes with a nuke auto-shuffle-combine script!**

join our [discord](https://discord.gg/UNHGnFEK)

---
**Update Log:**
2025.1.31: version 0.5.0

1. initial release, with basic functions.

---

### HOW TO USE:

1. **Blender light group aovs are stored at viewlayer level, so this plugin runs per viewlayer by now. In 4.4 there will be a new method to create all light groups in a scene**
![屏幕截图 2025-01-31 235127](https://github.com/user-attachments/assets/195364a8-76fe-4985-9933-1f84b849efd5)

3. **Put your lights in collections whose name starts with "lgt_".**
4. **Naming your light properly with letters and numbers only. Do not use any "_"**
5. **Press the one and only function button to generate current viewlayer's light group. Note that only enabled collection will count.**
6. **If you want to reuse light group between multiple lights, just duplicate the lights and keep their auto-generated ".001" number suffix, they'll be ignored and revert back to the desired name.**

---

### 使用方法：

1. **Blender灯光组AOV存储在视图层级别，因此目前此插件按视图层运行。在4.4版本中，将有一种新方法来创建场景中的所有灯光组。**
![屏幕截图 2025-01-31 235127](https://github.com/user-attachments/assets/195364a8-76fe-4985-9933-1f84b849efd5)
3. **将你的灯光放入名称以“lgt_”开头的集合中。**
4. **正确命名你的灯光，仅使用字母和数字。不要使用任何下划线（“_”）。**
5. **点击唯一的功能按钮为当前视图层生成灯光组。注意只有启用的集合才会被处理。**
6. **如果你想在多个灯光之间重用灯光组，只需复制灯光并保留其自动生成的“.001”编号后缀。它们将被忽略并恢复为所需的名称。**

---

### Nuke auto shuffle script installation

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
