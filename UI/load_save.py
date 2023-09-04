from tkinter.filedialog import asksaveasfile, askopenfilename
import globalVars
import json
from PCCanvasObject import PCCanvasObject
from SwitchCanvasObject import SwitchCanvasObject
from RectangleCanvasObject import RectangleCanvasObject
from LabelCanvasObject import LabelCanvasObject
from UI import loadIcons
from network.Physical_Interface import PhysicalInterface
from network.Switch import Switch
from network.Ethernet_Cable import EthernetCable
from network.PC import PC


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
    save_info = {'node_number': globalVars.node_number, 'PC': [], 'SW': [], 'RO': [], 'ETH': [], 'RECT': [], 'LBL': []}
    for i in globalVars.pc_objects:
        temp = i.get_save_info()
        save_info['PC'].append({'x_coord': temp[0], 'y_coord': temp[1], 'block_name': temp[2], 'cli_text': temp[3],
                                'command_history': temp[4], 'command_history_index': temp[5], 'tag_1': temp[6],
                                'tag_2': temp[7], 'light_1': temp[8], 'light_2': temp[9], 'class_info': temp[10]})

    for i in globalVars.sw_objects:
        temp = i.get_save_info()
        save_info['SW'].append({'x': temp[0], 'y': temp[1], 'block_name': temp[2], 'cli_text': temp[3],
                                'class_info': temp[4]})

    for i in globalVars.cable_objects:
        temp = i.get_save_info()
        save_info['ETH'].append({'block_name': temp[0], 'obj1_coords': temp[1], 'obj2_coords': temp[2],
                                 'obj1_tag': temp[3], 'obj2_tag': temp[4], 'class_info': temp[5]})

    for i in globalVars.canvas_rectangles:
        temp = i.get_save_info()
        save_info['RECT'].append({'color_code': temp[0], 'block_name': temp[1], 'x': temp[2], 'y': temp[3],
                                  'a': temp[4], 'b': temp[5]})

    for i in globalVars.canvas_labels:
        temp = i.get_save_info()
        save_info['LBL'].append({'block_name': temp[0], 'text': temp[1], 'x': temp[2], 'y': temp[3],
                                 'a': temp[4], 'b': temp[5], 'label_x': temp[6], 'label_y': temp[7]})

    # Write json to file
    with open(file_name, 'a') as F:
        F.write(json.dumps(save_info))


def load(canvas, master, file):
    # Clear everything first
    canvas.delete("all")

    with open(file, 'r') as F:
        # Use the json dumps method to write the list to disk
        configuration = json.load(F)

    globalVars.node_number = configuration['node_number']

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
        intf = PhysicalInterface(PhysicalInterface.set_name(pc_interface_info[0]), pc_interface_info[0], pc_obj)
        intf.set_bandwidth(pc_interface_info[1])
        intf.set_is_connected(pc_interface_info[4])
        intf.set_connected_to(pc_interface_info[5])
        intf.set_operational(pc_interface_info[6], load=True)
        intf.set_administratively_down(pc_interface_info[7], load=True)
        pc_obj.set_interfaces_on_load(intf)
        # ----- Rebuild Interfaces ----- #

        # ----- Rebuild Canvas PC ----- #
        pc_canvas_obj = PCCanvasObject(canvas, pc['block_name'], pc_icons, pc_obj, master, load=True)
        pc_canvas_obj.set_pos(pc['x_coord'], pc['y_coord'])
        # ----- Rebuild Canvas PC ----- #

        globalVars.objects.append(pc_canvas_obj)
        globalVars.pc_objects.append(pc_canvas_obj)

    sw_icons = loadIcons.get_sw_icons()
    for sw in configuration['SW']:

        # return [self.Host_Name, self.MAC_Address, self.CAM_table, interfaces]
        sw_class_info = sw['class_info']
        sw_interface_info = sw['class_info'][3]

        # ----- Rebuild SW ----- #
        sw_obj = Switch(sw_class_info[0])
        sw_obj.set_mac_address(sw_class_info[1])
        sw_obj.set_cam_table(sw_class_info[2])
        # ----- Rebuild SW ----- #

        # ----- Rebuild Interfaces ----- #
        for interface in sw_interface_info:
            intf = PhysicalInterface(PhysicalInterface.set_name(interface[0]), interface[0], sw_obj)
            intf.set_bandwidth(interface[1])
            intf.set_is_connected(interface[4])
            intf.set_connected_to(interface[5])
            intf.set_operational(interface[6], load=True)
            intf.set_administratively_down(interface[7], load=True)
            sw_obj.set_interfaces_on_load(intf)
        # ----- Rebuild Interfaces ----- #

        # ----- Rebuild Canvas SW ----- #
        sw_canvas_object = SwitchCanvasObject(canvas, sw['block_name'], sw_icons, sw_obj, master, load=True)
        sw_canvas_object.set_pos(sw['x'], sw['y'])
        # ----- Rebuild Canvas SW ----- #

        globalVars.objects.append(sw_canvas_object)
        globalVars.sw_objects.append(sw_canvas_object)

    for rect in configuration['RECT']:
        rectangle_canvas_object = RectangleCanvasObject(canvas, rect['color_code'], rect['block_name'], load=True)
        rectangle_canvas_object.set_is_set(True)
        rectangle_canvas_object.set_coords(rect['x'], rect['y'], rect['a'], rect['b'])
        globalVars.canvas_rectangles.append(rectangle_canvas_object)

    for label in configuration['LBL']:
        label_canvas_object = LabelCanvasObject(canvas, label['block_name'], label['text'], load=True)
        label_canvas_object.set_coords(label['x'], label['y'], label['a'], label['b'],
                                       label['label_x'], label['label_y'])
        globalVars.canvas_labels.append(label_canvas_object)
