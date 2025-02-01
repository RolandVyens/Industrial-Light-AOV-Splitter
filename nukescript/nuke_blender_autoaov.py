import nuke


def shuffle_and_combine_light_groups():
    selected_nodes = nuke.selectedNodes("Read")
    if not selected_nodes:
        nuke.message("Please select a Read node containing the EXR file.")
        return

    read_node = selected_nodes[0]
    oriX = read_node.xpos()
    oriY = read_node.ypos()
    read_node.setSelected(False)

    channels = read_node.channels()

    light_groups = []
    for channel in channels:
        if "RGBA_" in channel:
            light_groups.append(channel.split(".")[0])

    light_group_channels = list(set(light_groups))
    # print(light_group_channels)

    if not light_group_channels:
        nuke.message("No light group AOVs found in the selected EXR.")
        return
    lights = []
    for lightgroup in light_group_channels:
        lights.append(lightgroup.rsplit("_", 1)[-1])
    lights = list(set(lights))
    print(lights)

    def sort_light_group_channels(light_group_channels, lights):
        # Define the order for prefixes
        prefix_order = {"diffuse": 0, "specular": 1, "transmission": 2, "volume": 3}

        # Custom sort function
        def custom_sort_key(channel):
            # Extract the suffix (e.g., 'sun') and prefix (e.g., 'diffuse')
            parts = channel.split("_")
            prefix = parts[1]  # The part after 'RGBA_'
            suffix = parts[-1]

            # Determine the sort keys: first by lights order, then by prefix order
            light_index = lights.index(suffix) if suffix in lights else float("inf")
            prefix_index = prefix_order.get(prefix, float("inf"))

            return light_index, prefix_index

        # Sort the list using the custom key
        sorted_channels = sorted(light_group_channels, key=custom_sort_key)
        return sorted_channels

    sorted_channels = sort_light_group_channels(light_group_channels, lights)
    print(sorted_channels)

    # Get screen size of dot and shuffle node
    tmpShuffle = nuke.createNode("Shuffle", inpanel=False)
    [sWidth, sHeight] = [tmpShuffle.screenWidth(), tmpShuffle.screenHeight()]
    nuke.delete(tmpShuffle)
    tmpDot = nuke.createNode("Dot", inpanel=False)
    [dWidth, dHeight] = [tmpDot.screenWidth(), tmpDot.screenHeight()]
    nuke.delete(tmpDot)

    y_offset = 150
    x_offset = 150

    dot = nuke.createNode("Dot", inpanel=False)
    dot.setInput(0, read_node)
    dot.setSelected(False)
    dot.setXYpos(int(oriX + 0.5 * (sWidth - dWidth)), oriY + y_offset)

    unpremult = nuke.createNode("Unpremult", inpanel=False)
    unpremult["channels"].setValue("all")
    unpremult.setSelected(False)
    unpremult.setInput(0, dot)
    unpremult.setXYpos(oriX, int(dot.ypos() + y_offset * 0.4))

    channel_by_light = {key: [] for key in lights}
    for idx, element in enumerate(sorted_channels):
        # Split the element into parts using underscores
        parts = element.split("_")
        # Extract the suffix (last part of the split)
        suffix = parts[-1]
        # Check if the suffix exists in list1
        if suffix in lights:
            channel_by_light[suffix].append(idx)
    print(channel_by_light)

    own_light = [key for key, value in channel_by_light.items() if len(value) == 1]
    print(own_light)

    lastDot = ""  # Define the last dot first
    shuffles = []
    for i, light_group in enumerate(sorted_channels):
        if i == 0:
            dot1 = nuke.createNode("Dot", inpanel=False)
            dot1.setInput(0, unpremult)
            dot1.setSelected(False)
            dot1.setXYpos(
                int(oriX + 0.5 * (sWidth - dWidth)),
                unpremult.ypos() + int(y_offset * 0.7),
            )
            lastDot = dot1
            shuffle = nuke.createNode("Shuffle2", inpanel=False)
            shuffle["in1"].setValue(light_group)
            shuffle.setInput(0, dot1)
            shuffle.setSelected(False)
            shuffle.setXYpos(oriX, dot1.ypos() + int(y_offset * 0.7))
            shuffle["label"].setValue("[value in1]")
            shuffles.append(shuffle)
        else:
            dot2 = nuke.createNode("Dot", inpanel=False)
            dot2.setInput(0, lastDot)
            dot2.setSelected(False)
            dot2.setXYpos(int(lastDot.xpos() + x_offset), lastDot.ypos())
            lastDot = dot2
            shuffle2 = nuke.createNode("Shuffle2", inpanel=False)
            shuffle2["in1"].setValue(light_group)
            shuffle2.setInput(0, dot2)
            shuffle2.setSelected(False)
            shuffle2.setXYpos(
                int(lastDot.xpos() - 0.5 * (sWidth - dWidth)),
                lastDot.ypos() + int(y_offset * 0.7),
            )
            shuffle2["label"].setValue("[value in1]")
            shuffles.append(shuffle2)
    print(shuffles)

    channelmerges = {}
    for light in [x for x in lights if x not in own_light]:
        maxindex = len(channel_by_light[light]) - 1
        last_node = str()
        for i, channel in enumerate(list(reversed(channel_by_light[light]))):
            if i == 0:
                dot3 = nuke.createNode("Dot", inpanel=False)
                dot3.setInput(0, shuffles[list(reversed(channel_by_light[light]))[i]])
                dot3.setSelected(False)
                dot3.setXYpos(
                    int(
                        shuffles[list(reversed(channel_by_light[light]))[i]].xpos()
                        + 0.5 * (sWidth - dWidth)
                    ),
                    int(shuffles[0].ypos() + y_offset * 3 + 0.5 * (sHeight - dHeight)),
                )
                last_node = dot3
            elif i > 0:
                merge_light1 = nuke.createNode("Merge2", inpanel=False)
                merge_light1["operation"].setValue("plus")
                merge_light1.setInput(
                    0, shuffles[list(reversed(channel_by_light[light]))[i]]
                )
                merge_light1.setInput(1, last_node)
                merge_light1.setSelected(False)
                merge_light1.setXYpos(
                    shuffles[list(reversed(channel_by_light[light]))[i]].xpos(),
                    shuffles[0].ypos() + int(y_offset * 3),
                )
                last_node = merge_light1
                if i == maxindex:
                    channelmerges[
                        shuffles[list(reversed(channel_by_light[light]))[i]]
                    ] = merge_light1
    print(channelmerges)

    lightmerges_index = []
    lightmerges = []
    for light in lights:
        lightmerges_index.append(channel_by_light[light][0])
    print(lightmerges_index)
    for i in lightmerges_index:
        first_shuffle = shuffles[i]
        if first_shuffle in channelmerges:
            first_merge = channelmerges[first_shuffle]
            first_shuffle = first_merge
        lightmerges.append(first_shuffle)
    print(lightmerges)

    for i, light in enumerate(list(reversed(lightmerges))):
        if i == 0:
            dot4 = nuke.createNode("Dot", inpanel=False)
            dot4.setInput(0, list(reversed(lightmerges))[i])
            dot4.setSelected(False)
            dot4.setXYpos(
                int(list(reversed(lightmerges))[i].xpos() + 0.5 * (sWidth - dWidth)),
                int(shuffles[0].ypos() + y_offset * 7 + 0.5 * (sHeight - dHeight)),
            )
            last_node = dot4
        elif i > 0:
            merge_light2 = nuke.createNode("Merge2", inpanel=False)
            merge_light2["operation"].setValue("plus")
            merge_light2.setInput(0, list(reversed(lightmerges))[i])
            merge_light2.setInput(1, last_node)
            merge_light2.setSelected(False)
            merge_light2.setXYpos(
                list(reversed(lightmerges))[i].xpos(),
                shuffles[0].ypos() + int(y_offset * 7),
            )
            last_node = merge_light2

    copy = nuke.createNode("Copy", inpanel=False)
    copy.setSelected(False)
    copy.setXYpos(oriX, last_node.ypos() + y_offset)
    copy.setInput(0, last_node)

    dot5 = nuke.createNode("Dot", inpanel=False)
    dot5.setInput(0, dot)
    dot5.setSelected(False)
    dot5.setXYpos(int(dot.xpos() - x_offset), dot.ypos())

    dot6 = nuke.createNode("Dot", inpanel=False)
    dot6.setInput(0, dot5)
    dot6.setSelected(False)
    dot6.setXYpos(dot5.xpos(), int(copy.ypos() + 0.5 * (copy.screenHeight() - dHeight)))

    copy.setInput(1, dot6)

    premult = nuke.createNode("Premult", inpanel=False)
    premult.setSelected(False)
    premult.setInput(0, copy)
    premult.setXYpos(oriX, copy.ypos() + y_offset)
