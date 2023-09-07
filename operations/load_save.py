from tkinter.filedialog import asksaveasfile, askopenfilename
from operations import globalVars
import json
from UI.EthernetCableCanvasObject import EthernetCableCanvasObject
from UI.LabelCanvasObject import LabelCanvasObject
from UI.PCCanvasObject import PCCanvasObject
from UI.RectangleCanvasObject import RectangleCanvasObject
from UI.RouterCanvasObject import RouterCanvasObject
from UI.SwitchCanvasObject import SwitchCanvasObject
from UI import loadIcons, button_handler
from network.Physical_Interface import PhysicalInterface
from network.Switch import Switch
from network.Ethernet_Cable import EthernetCable
from network.PC import PC
from network.Router import Router


def save_file():
    f = asksaveasfile(initialdir=globalVars.file_directory, initialfile='.json',
                      defaultextension=".json", filetypes=[("json", ".json")])
    if f:
        save(f.name)


def load_file(canvas, master):
    f = askopenfilename(initialdir=globalVars.file_directory)
    if f:
        load(canvas, master, f)


def save(file_name):
    save_info = {'node_number': globalVars.node_number, 'PC': [], 'SW': [], 'RO': [], 'ETH': [], 'RECT': [], 'LBL': [],
                 'OTHER': {}}

    for i in globalVars.pc_objects:
        temp = i.get_save_info()
        save_info['PC'].append({'x_coord': temp[0], 'y_coord': temp[1], 'block_name': temp[2], 'cli_text': temp[3],
                                'command_history': temp[4], 'command_history_index': temp[5], 'tag_1': temp[6],
                                'tag_2': temp[7], 'light_1': temp[8], 'light_2': temp[9], 'class_info': temp[10]})

    for i in globalVars.sw_objects:
        temp = i.get_save_info()
        save_info['SW'].append({'x': temp[0], 'y': temp[1], 'block_name': temp[2], 'cli_text': temp[3],
                                'class_info': temp[4]})

    for i in globalVars.ro_objects:
        temp = i.get_save_info()
        save_info['RO'].append({'x': temp[0], 'y': temp[1], 'block_name': temp[2], 'cli_text': temp[3],
                                'class_info': temp[4]})

    for i in globalVars.cable_objects:
        temp = i.get_save_info()
        if temp[1] and all(temp[0] != c for c in save_info['ETH']):
            save_info['ETH'].append({'block_name': temp[0], 'obj1_coords': temp[1], 'obj2_coords': temp[2],
                                     'obj1_tag': temp[3], 'obj2_tag': temp[4],
                                     'intf_1_name': temp[5], 'intf_2_name': temp[6], 'line_count': temp[7]})

    for i in globalVars.canvas_rectangles:
        temp = i.get_save_info()
        save_info['RECT'].append({'color_code': temp[0], 'block_name': temp[1], 'x': temp[2], 'y': temp[3],
                                  'a': temp[4], 'b': temp[5]})

    for i in globalVars.canvas_labels:
        temp = i.get_save_info()
        save_info['LBL'].append({'block_name': temp[0], 'text': temp[1], 'x': temp[2], 'y': temp[3],
                                 'a': temp[4], 'b': temp[5], 'label_x': temp[6], 'label_y': temp[7]})

    save_info['OTHER']['Light_State'] = globalVars.light_state
    save_info['OTHER']['Label_State'] = globalVars.label_state
    save_info['OTHER']['Time'] = globalVars.internal_clock.get_time()

    # Write json to file
    with open(file_name, 'a') as F:
        F.write(json.dumps(save_info))


def load(canvas, master, file):

    # Clear everything first
    globalVars.clear_all_objects()
    globalVars.internal_clock.clear_all()
    canvas.delete("all")

    # Use the json dumps method to write data to file
    with open(file, 'r') as F:
        configuration = json.load(F)

    # Set the internal clock
    globalVars.internal_clock.set_time(configuration['OTHER']['Time'])

    globalVars.node_number = configuration['node_number']

    # Load All Nodes
    pc_interface_to_light_mapping = {}
    pc_icons = loadIcons.get_pc_icons()
    for pc in configuration['PC']:
        pc_class_info = pc['class_info']
        pc_interface_info = pc['class_info'][9]

        # ----- Rebuild PC ----- #
        pc_obj = PC(host_name=pc_class_info[0])
        pc_obj.set_mac_address(pc_class_info[1])
        pc_obj.set_ipv4_address(pc_class_info[3])
        pc_obj.set_netmask(pc_class_info[4])
        pc_obj.set_ipv6_address(pc_class_info[5])
        pc_obj.set_prefix(pc_class_info[6])
        pc_obj.set_default_gateway(pc_class_info[7])
        pc_obj.set_arp_table(pc_class_info[8])
        # ----- Rebuild PC ----- #

        # ----- Rebuild Interfaces ----- #
        intf = PhysicalInterface(pc_interface_info[2][1:], pc_interface_info[0], pc_obj)
        intf.set_bandwidth(pc_interface_info[1])
        pc_obj.set_interfaces_on_load(intf)
        pc_interface_to_light_mapping[intf] = [pc_interface_info[6], pc_interface_info[7]]
        # ----- Rebuild Interfaces ----- #

        # ----- Rebuild Canvas PC ----- #

        pc_canvas_obj = PCCanvasObject(canvas, pc['block_name'], pc_icons, pc_obj, master, globalVars.internal_clock,
                                       load=True)
        pc_canvas_obj.set_pos(pc['x_coord'], pc['y_coord'])
        # ----- Rebuild Canvas PC ----- #

        globalVars.objects.append(pc_canvas_obj)
        globalVars.pc_objects.append(pc_canvas_obj)
        globalVars.internal_clock.add_pc(pc_canvas_obj)

    sw_interface_to_light_mapping = {}
    sw_icons = loadIcons.get_sw_icons()
    for sw in configuration['SW']:

        sw_class_info = sw['class_info']
        sw_interface_info = sw['class_info'][3]

        # ----- Rebuild SW ----- #
        sw_obj = Switch(sw_class_info[0], load=True)
        sw_obj.set_mac_address(sw_class_info[1])
        # ----- Rebuild SW ----- #

        # ----- Rebuild Interfaces ----- #
        for interface in sw_interface_info:
            t = interface[2].split('/')  # Split the name of the interface to pass it in next line
            intf = PhysicalInterface(t[0][-1] + '/' + t[-1], interface[0], sw_obj)
            intf.set_bandwidth(interface[1])
            intf.set_switchport_type(interface[8])
            intf.set_access_vlan_id(interface[9])
            intf.set_allowed_trunk_vlans(interface[10])
            sw_obj.set_interfaces_on_load(intf)
            sw_interface_to_light_mapping[intf] = [interface[6], interface[7]]
        # ----- Rebuild Interfaces ----- #

        # ----- Rebuild CAM Table ----- #
        cam_table = {}
        for entry in sw_class_info[2]:
            cam_table[int(entry)] = [sw_class_info[2][entry][0], sw_class_info[2][entry][1], sw_class_info[2][entry][2],
                                     sw_obj.get_interface_by_name(sw_class_info[2][entry][3]), sw_class_info[2][entry][4]]
        sw_obj.set_cam_table(cam_table)
        # ----- Rebuild CAM Table ----- #

        # ----- Rebuild Canvas SW ----- #
        sw_canvas_object = SwitchCanvasObject(canvas, sw['block_name'], sw_icons, sw_obj, master,
                                              globalVars.internal_clock, load=True)
        sw_canvas_object.set_pos(sw['x'], sw['y'])
        # ----- Rebuild Canvas SW ----- #

        globalVars.objects.append(sw_canvas_object)
        globalVars.sw_objects.append(sw_canvas_object)
        globalVars.internal_clock.add_switch(sw_canvas_object)

    ro_interface_to_light_mapping = {}
    ro_icons = loadIcons.get_router_icons()
    for ro in configuration['RO']:

        ro_class_info = ro['class_info']
        ro_interface_info = ro['class_info'][4]

        # ----- Rebuild RO ----- #
        ro_obj = Router(ro_class_info[0], True)
        ro_obj.set_mac_address(ro_class_info[1])
        ro_obj.set_arp_table(ro_class_info[2])
        # ----- Rebuild RO ----- #

        # ----- Rebuild Interfaces ----- #
        for interface in ro_interface_info:
            t = interface[2].split('/')  # Split the name of the interface to pass it in next line
            intf = PhysicalInterface(t[0][-1] + '/' + t[-1], interface[0], ro_obj)
            intf.set_bandwidth(interface[1])
            intf.set_ipv4_address(interface[8])
            intf.set_netmask(interface[9])
            ro_obj.set_interfaces_on_load(intf)
            ro_interface_to_light_mapping[intf] = [interface[6], interface[7]]
        # ----- Rebuild Interfaces ----- #

        # ----- Rebuild Routing Table ----- #
        routing_table = {}
        for intf in ro_class_info[3]:
            interface_name = ro_obj.get_interface_by_name(intf)
            routing_table[interface_name] = []
            for route in ro_class_info[3][intf]:
                routing_table[interface_name].append([route[0], route[1], route[2]])
        ro_obj.set_routing_table(routing_table)
        # ----- Rebuild Routing Table ----- #

        # ----- Rebuild Canvas RO ----- #
        ro_canvas_object = RouterCanvasObject(canvas, ro['block_name'], ro_icons, ro_obj, master,
                                              globalVars.internal_clock, load=True)
        ro_canvas_object.set_pos(ro['x'], ro['y'])
        # ----- Rebuild Canvas RO ----- #

        globalVars.ro_objects.append(ro_canvas_object)
        globalVars.objects.append(ro_canvas_object)
        globalVars.internal_clock.add_router(ro_canvas_object)

    eth_icon = loadIcons.get_ethernet_icon()  # Don't really need the icon
    for eth in configuration['ETH']:
        eth_object = EthernetCable()
        eth_canvas_object = EthernetCableCanvasObject(canvas, eth['block_name'], eth_icon,
                                                      eth_object, master, load=True)
        eth_canvas_object.set_pos(eth['obj1_coords'][0], eth['obj1_coords'][1],
                                  eth['obj2_coords'][0], eth['obj2_coords'][1], eth['obj1_tag'], eth['obj2_tag'],
                                  eth['intf_1_name'], eth['intf_2_name'], eth['line_count'])

        globalVars.cable_objects.append(eth_canvas_object)

    for rect in configuration['RECT']:
        rectangle_canvas_object = RectangleCanvasObject(canvas, rect['color_code'], rect['block_name'], load=True)
        rectangle_canvas_object.set_is_set(True)
        rectangle_canvas_object.set_coords(rect['x'], rect['y'], rect['a'], rect['b'])
        globalVars.canvas_rectangles.append(rectangle_canvas_object)

    # Set the saved label state
    globalVars.label_state = configuration['OTHER']['Label_State']
    for label in configuration['LBL']:
        label_canvas_object = LabelCanvasObject(canvas, label['block_name'], label['text'], load=True)
        label_canvas_object.set_coords(label['x'], label['y'], label['a'], label['b'],
                                       label['label_x'], label['label_y'])
        globalVars.canvas_labels.append(label_canvas_object)
        # label_canvas_object.toggle_label()

    # ----- Set Lights ----- #
    for i in pc_interface_to_light_mapping:
        if i.get_is_connected():
            i.set_operational(pc_interface_to_light_mapping[i][0])
            i.set_administratively_down(pc_interface_to_light_mapping[i][1])

    for i in sw_interface_to_light_mapping:
        if i.get_is_connected():
            i.set_operational(sw_interface_to_light_mapping[i][0])
            i.set_administratively_down(sw_interface_to_light_mapping[i][1])

    for i in ro_interface_to_light_mapping:
        if i.get_is_connected():
            i.set_operational(ro_interface_to_light_mapping[i][0])
            i.set_administratively_down(ro_interface_to_light_mapping[i][1])

    # Set the light state
    globalVars.light_state = configuration['OTHER']['Light_State']

    button_handler.toggle_link_lights(canvas, checkbox=True)
    # ----- Set Lights ----- #
