from tkinter.filedialog import asksaveasfile, askopenfilename
import globalVars
import json
from PCCanvasObject import PCCanvasObject
import network.PC
from network.Physical_Interface import PhysicalInterface
from UI.RectangleCanvasObject import RectangleCanvasObject
from network.Ethernet_Cable import EthernetCable
from UI import loadIcons


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
    save_info = {'node_number': globalVars.node_number, 'PC': [], 'SW': [], 'RO': [], 'RECT': []}
    for i in globalVars.objects:
        temp = i.get_save_info()
        save_info['PC'].append({'x_coord': temp[0], 'y_coord': temp[1], 'block_name': temp[2], 'cli_text': temp[3],
                                'command_history': temp[4],
                                'command_history_index': temp[5], 'line_connections': temp[6], 'tag_1': temp[7],
                                'tag_2': temp[8], 'interface_1': temp[9], 'interface_2': temp[10], 'light_1': temp[11],
                                'light_2': temp[12], 'class_info': temp[13]})

    for i in globalVars.canvas_rectangles:
        temp = i.get_save_info()
        save_info['RECT'].append({'color_code': temp[0], 'block_name': temp[1], 'x': temp[2], 'y': temp[3],
                                  'a': temp[4], 'b': temp[5]})

    # Write json to file
    with open(file_name, 'a') as F:
        F.write(json.dumps(save_info))


def load(canvas, master, file):
    # Clear everything first
    canvas.delete("all")
    #
    # for i in globalVars.node_buttons:
    #     i.place_forget()

    with open(file, 'r') as F:
        # Use the json dumps method to write the list to disk
        configuration = json.load(F)

    globalVars.node_number = configuration['node_number']

    pc_icons = loadIcons.get_pc_icons()
    for pc in configuration['PC']:
        pc_class_info = pc['class_info']
        pc_interface_info = pc['class_info'][9]

        # ----- Rebuild PC ----- #
        pc_obj = network.PC.PC(host_name=pc_class_info[0])
        pc_obj.set_mac_address(pc_class_info[1])
        pc_obj.set_ipv4_address(pc_class_info[3])
        pc_obj.set_netmask(pc_class_info[4])
        pc_obj.set_ipv6_address(pc_class_info[5])
        pc_obj.set_prefix(pc_class_info[6])
        pc_obj.set_default_gateway(pc_class_info[7])
        pc_obj.set_arp_table(pc_class_info[8])
        # ----- Rebuild PC ----- #

        # ----- Rebuild Interfaces ----- #
        intf = network.Physical_Interface.PhysicalInterface(PhysicalInterface.set_name(pc_interface_info[0]),
                                                            pc_interface_info[0], pc_obj)
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

    sw_icons = loadIcons.get_sw_icons()
    for sw in configuration['SW']:
        pass

    for rect in configuration['RECT']:
        rectangle_canvas_object = RectangleCanvasObject(canvas, rect['color_code'], rect['block_name'], load=True)
        rectangle_canvas_object.set_is_set(True)
        rectangle_canvas_object.set_coords(rect['x'], rect['y'], rect['a'], rect['b'])
        globalVars.canvas_rectangles.append(rectangle_canvas_object)
