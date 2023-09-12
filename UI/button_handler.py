import json
import tkinter as tk
from tkinter import colorchooser, messagebox, ttk
from operations import globalVars as globalVars
import UI.helper_functions as hf
import network.Ethernet_Cable
import network.PC
import network.Router
import network.Switch
from UI.EthernetCableCanvasObject import EthernetCableCanvasObject
from UI.LabelCanvasObject import LabelCanvasObject
from UI.PCCanvasObject import PCCanvasObject
from UI.RectangleCanvasObject import RectangleCanvasObject
from UI.RouterCanvasObject import RouterCanvasObject
from UI.SwitchCanvasObject import SwitchCanvasObject
from UI import loadIcons


def create_pc(popup, canvas, generation, master, icons, time_class):
    pc = PCCanvasObject(canvas, hf.get_next_pc(generation), icons, network.PC.PC(generation), master, time_class)
    globalVars.objects.append(pc)
    globalVars.pc_objects.append(pc)
    popup.destroy()
    globalVars.open_TL_pc = False


def create_switch(popup, canvas, icons, switch_type, master, time_class):
    if switch_type == "TSA1000X":
        switch = SwitchCanvasObject(canvas, hf.get_next_switch(), icons, network.Switch.Switch(), master, time_class)
        globalVars.objects.append(switch)
        globalVars.sw_objects.append(switch)
    elif switch_type == "RTSA1000X":
        pass

    popup.destroy()
    globalVars.open_TL_sw = False


def create_router(popup, canvas, icons, master, time_class):
    router = RouterCanvasObject(canvas, hf.get_next_router(), icons, network.Router.Router(), master, time_class)
    globalVars.objects.append(router)
    globalVars.ro_objects.append(router)
    popup.destroy()
    globalVars.open_TL_ro = False


def create_rectangle(canvas):
    color_code = colorchooser.askcolor(title="Choose Box Color")
    if color_code[0]:
        rectangle = RectangleCanvasObject(canvas, color_code, hf.get_next_rectangle(canvas))
        globalVars.canvas_rectangles.append(rectangle)


def create_label(popup, canvas, text):
    if text:
        label = LabelCanvasObject(canvas, hf.get_next_label(canvas), text)
        globalVars.canvas_labels.append(label)
        popup.destroy()
    else:
        messagebox.showerror('Invalid Parameter', 'Please Enter Some Text', parent=popup)
    globalVars.open_TL_lb = False


def handle_button_click(master, canvas, device_type, time_class):
    if device_type == "endhost":

        if not globalVars.open_TL_pc:

            globalVars.open_TL_pc = True

            pc_icons = loadIcons.get_pc_icons()

            globalVars.TL_pc = tk.Toplevel(master)
            globalVars.TL_pc.title("Add End Host")
            globalVars.TL_pc.iconphoto(False, pc_icons[0])
            globalVars.TL_pc.protocol("WM_DELETE_WINDOW", lambda w=globalVars.TL_pc: hf.window_closed(w))
            globalVars.TL_pc.resizable(False, False)

            x = (globalVars.screen_width / 2) - (450 / 2)
            y = (globalVars.screen_height / 2) - (325 / 2) - 100
            globalVars.TL_pc.geometry('%dx%d+%d+%d' % (450, 325, x, y))

            frame = tk.LabelFrame(globalVars.TL_pc, padx=5, pady=5)
            frame.place(x=10, y=10, height=300, width=425)

            pc_button = tk.Button(frame, width=10, height=5, text="Create PC", relief=tk.GROOVE,
                                  command=lambda: create_pc(globalVars.TL_pc, canvas, "SecondGen", master, pc_icons, time_class))
            pc_button.place(x=165, y=80)
            pc_button.bind('<Enter>', lambda e, btn=pc_button: hf.button_enter(e, btn))
            pc_button.bind('<Leave>', lambda e, btn=pc_button: hf.button_leave(e, btn))

            tk.Label(frame, text="One Gigabit Ethernet Interface\n(1000 mbps)").place(x=126, y=180)
            globalVars.TL_pc.focus_set()
        else:
            globalVars.TL_pc.focus_set()

    elif device_type == "switch":

        if not globalVars.open_TL_sw:

            globalVars.open_TL_sw = True

            sw_icons = loadIcons.get_sw_icons()

            globalVars.TL_sw = tk.Toplevel(master)
            globalVars.TL_sw.title("Add Switch")
            globalVars.TL_sw.iconphoto(False, sw_icons[0])
            globalVars.TL_sw.protocol("WM_DELETE_WINDOW", lambda w=globalVars.TL_sw: hf.window_closed(w))
            globalVars.TL_sw.resizable(False, False)

            x = (globalVars.screen_width / 2) - (550 / 2)
            y = (globalVars.screen_height / 2) - (325 / 2) - 100
            globalVars.TL_sw.geometry('%dx%d+%d+%d' % (550, 325, x, y))

            frame = tk.LabelFrame(globalVars.TL_sw, padx=5, pady=5)
            frame.place(x=10, y=10, height=300, width=525)

            l2sw_btn = tk.Button(frame, width=10, height=5, text="Create Switch\n(Layer 2)", relief=tk.GROOVE,
                                 command=lambda: create_switch(globalVars.TL_sw, canvas, sw_icons, "TSA1000X", master, time_class))
            l2sw_btn.place(x=100, y=30)
            l2sw_btn.bind('<Enter>', lambda e, btn=l2sw_btn: hf.button_enter(e, btn))
            l2sw_btn.bind('<Leave>', lambda e, btn=l2sw_btn: hf.button_leave(e, btn))

            l3sw_btn = tk.Button(frame, width=10, height=5, text="Create Switch\n(Layer 3)", relief=tk.GROOVE,
                                 command=lambda: create_switch(globalVars.TL_sw, canvas, sw_icons, "RTSA1000X", master, time_class))
            l3sw_btn.place(x=340, y=30)
            # l3sw_btn.bind('<Enter>', lambda e, btn=l3sw_btn: button_enter(e, btn))
            # l3sw_btn.bind('<Leave>', lambda e, btn=l3sw_btn: button_leave(e, btn))
            l3sw_btn.config(state="disabled")

            tk.Label(frame, text="10 Fast Ethernet Interfaces\n(100 mbps)").place(x=60, y=130)
            tk.Label(frame, text="12 Gigabit Ethernet Interface\n(1000 mbps)").place(x=60, y=180)
            tk.Label(frame, text="2 10G Ethernet Interface\n(1000 mbps)").place(x=70, y=230)

            tk.Label(frame, text="20 Gigabit Ethernet Interfaces\n(1000 mbps)").place(x=300, y=130)
            tk.Label(frame, text="4 10G Ethernet Interfaces\n(10 gbps)").place(x=315, y=180)
            tk.Label(frame, text="Routing Capabilities\n(Multilayer Switch)").place(x=325, y=230)

            globalVars.TL_sw.focus_set()
        else:
            globalVars.TL_sw.focus_set()

    elif device_type == "router":

        if not globalVars.open_TL_ro:

            globalVars.open_TL_ro = True

            r_icons = loadIcons.get_router_icons()

            globalVars.TL_ro = tk.Toplevel(master)
            globalVars.TL_ro.title("Add Router")
            globalVars.TL_ro.iconphoto(False, r_icons[0])
            globalVars.TL_ro.protocol("WM_DELETE_WINDOW", lambda w=globalVars.TL_ro: hf.window_closed(w))
            globalVars.TL_ro.resizable(False, False)

            x = (globalVars.screen_width / 2) - (450 / 2)
            y = (globalVars.screen_height / 2) - (325 / 2) - 100
            globalVars.TL_ro.geometry('%dx%d+%d+%d' % (450, 325, x, y))

            frame = tk.LabelFrame(globalVars.TL_ro, padx=5, pady=5)
            frame.place(x=10, y=10, height=300, width=425)

            ro_btn = tk.Button(frame, width=10, height=5, text="Create Router", relief=tk.GROOVE,
                               command=lambda: create_router(globalVars.TL_ro, canvas, r_icons, master, time_class))
            ro_btn.place(x=165, y=80)
            ro_btn.bind('<Enter>', lambda e, btn=ro_btn: hf.button_enter(e, btn))
            ro_btn.bind('<Leave>', lambda e, btn=ro_btn: hf.button_leave(e, btn))

            tk.Label(frame, text="8 Gigabit Ethernet Interface\n(1000 mbps)").place(x=125, y=180)

            globalVars.TL_ro.focus_set()
        else:
            globalVars.TL_ro.focus_set()

    # elif device_type == "l3sw":
    #     pass

    elif device_type == "Eth_cable":
        eth_icon = loadIcons.get_ethernet_icon()[0]
        cable = EthernetCableCanvasObject(canvas, hf.get_next_cable(canvas), eth_icon,
                                          network.Ethernet_Cable.EthernetCable(), master)
        globalVars.cable_objects.append(cable)

    elif device_type == "Label":

        if not globalVars.open_TL_lb:

            globalVars.open_TL_lb = True

            globalVars.tl_lb = tk.Toplevel(master)
            globalVars.tl_lb.title("Add Label")
            globalVars.tl_lb.iconphoto(False, loadIcons.get_label_icon()[0])
            globalVars.tl_lb.protocol("WM_DELETE_WINDOW", lambda w=globalVars.tl_lb: hf.window_closed(w))
            globalVars.tl_lb.resizable(False, False)

            x = (globalVars.screen_width / 2) - (250 / 2)
            y = (globalVars.screen_height / 2) - (150 / 2) - 100
            globalVars.tl_lb.geometry('%dx%d+%d+%d' % (250, 150, x, y))

            frame = tk.LabelFrame(globalVars.tl_lb, padx=5, pady=5)
            frame.place(x=10, y=10, height=130, width=230)

            tk.Label(frame, text="Label Text:").place(x=10, y=30)
            text = tk.Entry(frame, width=19)
            text.place(x=80, y=30)

            label_btn = tk.Button(frame, width=10, height=1, text="Create Label", relief=tk.GROOVE,
                                  command=lambda: create_label(globalVars.tl_lb, canvas, text.get()))
            label_btn.place(x=67, y=75)
            label_btn.bind('<Enter>', lambda e, btn=label_btn: hf.button_enter(e, btn))
            label_btn.bind('<Leave>', lambda e, btn=label_btn: hf.button_leave(e, btn))

            globalVars.tl_lb.focus_set()

        else:
            globalVars.tl_lb.focus_set()


def toggle_link_lights(canvas, checkbox=False):
    if canvas:

        # Only not the variable when this function is called from the toggle button, not the preferences menu
        if not checkbox:
            globalVars.light_state = not globalVars.light_state

        lights = canvas.find_withtag("light")
        for i in lights:
            if not globalVars.light_state:
                canvas.itemconfig(i, state='hidden')
            else:
                canvas.itemconfig(i, state='normal')


def toggle_labels(canvas):

    for i in globalVars.canvas_labels:
        i.toggle_label(False)

    # Check if all labels are in the same state. If not, show them all to reset the state.
    labels = canvas.find_withtag("Label")
    if any(canvas.itemcget(i, 'state') == 'hidden' for i in labels) and any(
            canvas.itemcget(i, 'state') == 'normal' for i in labels):
        for i in globalVars.canvas_labels:
            i.toggle_label(True)

        globalVars.label_state = False


def delete_object(canvas, icon):
    def motion(event):
        canvas.coords(canvas_object, canvas.canvasx(event.x), canvas.canvasy(event.y))

    def delete(event):
        overlap = canvas.find_overlapping(canvas.canvasx(event.x), canvas.canvasy(event.y),
                                          canvas.canvasx(event.x), canvas.canvasy(event.y))
        canvas_object_tag = ""
        for i in overlap:
            if i in canvas.find_withtag("PC"):
                canvas_object_tag = canvas.itemcget(i, "tags").split(" ")[0]

            elif i in canvas.find_withtag("Switch"):
                canvas_object_tag = canvas.itemcget(i, "tags").split(" ")[0]

            elif i in canvas.find_withtag("Router"):
                canvas_object_tag = canvas.itemcget(i, "tags").split(" ")[0]

            # elif i in canvas.find_withtag("Ethernet"):
            #     canvas_object_tag = canvas.itemcget(i, "tags").split(" ")[0]

            elif i in canvas.find_withtag("Rectangle"):
                canvas_object_tag = canvas.itemcget(i, "tags").split(" ")[0]

            elif i in canvas.find_withtag("Label"):
                canvas_object_tag = canvas.itemcget(i, "tags").split(" ")[0]

        # On click, check what was clicked, and delete cable
        if str(event.type) == "4":
            # if cable clicked on nothing
            if len(overlap) < 2:
                canvas.delete(canvas_object)
                return

            for i in globalVars.objects:
                if i.get_block_name() == canvas_object_tag:
                    try:
                        globalVars.objects.remove(i)
                        globalVars.pc_objects.remove(i)
                        globalVars.sw_objects.remove(i)
                        globalVars.ro_objects.remove(i)
                        globalVars.fw_objects.remove(i)
                    except ValueError:
                        pass
                    i.menu_delete(None, True)
                    return

            # for i in cable_objects:
            #     if i.get_block_name() == canvas_object_tag:
            #         i.menu_delete()
            #         return

            for i in globalVars.canvas_rectangles:
                if i.get_block_name() == canvas_object_tag:
                    globalVars.canvas_rectangles.remove(i)
                    i.delete()
                    return

            for i in globalVars.canvas_labels:
                if i.get_block_name() == canvas_object_tag:
                    globalVars.canvas_labels.remove(i)
                    i.delete()
                    return
            return

    hf.move_mouse_to(1100, 600)
    x = canvas.canvasx(canvas.winfo_pointerx() - canvas.winfo_rootx())
    y = canvas.canvasy(canvas.winfo_pointery() - canvas.winfo_rooty())

    canvas_object = canvas.create_image(x, y, image=icon)
    canvas.photo = icon

    canvas.tag_bind(canvas_object, "<Motion>", motion)
    canvas.tag_bind(canvas_object, "<Button-1>", delete)


def preferences_menu(master, canvas):
    preferences_popup = tk.Toplevel(master)
    preferences_popup.title("Preferences")
    preferences_popup.iconphoto(False, loadIcons.get_preferences_icon()[0])

    ws = master.winfo_screenwidth()
    hs = master.winfo_screenheight()
    x = (ws / 2) - (830 / 2)
    y = (hs / 2) - (600 / 2) - 50
    preferences_popup.geometry('%dx%d+%d+%d' % (830, 600, x, y))

    preferences_popup.focus_set()

    frame = tk.LabelFrame(preferences_popup, padx=5, pady=5)
    frame.place(x=10, y=10, width=810, height=580)

    ok_button = tk.Button(frame, text="OK", command=preferences_popup.destroy, relief=tk.GROOVE, width=10)
    ok_button.bind('<Enter>', lambda e, b=ok_button: hf.button_enter(e, b))
    ok_button.bind('<Leave>', lambda e, b=ok_button: hf.button_leave(e, b))
    ok_button.place(x=705, y=535)

    # Ask before Delete #
    ask_b4_del_var = tk.BooleanVar()
    ask_b4_del_check = tk.Checkbutton(frame, text='Ask before deleting node', variable=ask_b4_del_var, onvalue=True,
                                      offvalue=False,
                                      command=lambda i="ask_before_delete", j=ask_b4_del_var: set_preferences(i, j))
    ask_b4_del_check.grid(row=0, column=0, sticky=tk.W)
    # Ask before Delete #

    # Ask before Quick Delete #
    ask_b4_quick_del_var = tk.BooleanVar()
    ask_b4_quick_del_check = tk.Checkbutton(frame, text='Ask before quick deleting node', variable=ask_b4_quick_del_var,
                                            onvalue=True, offvalue=False,
                                            command=lambda i="ask_before_quick_delete",
                                                           j=ask_b4_quick_del_var: set_preferences(i, j))
    ask_b4_quick_del_check.grid(row=1, column=0, sticky=tk.W)
    # Ask before Quick Delete #

    # Show link lights by default #
    show_link_lights_var = tk.BooleanVar()
    show_link_lights_check = tk.Checkbutton(frame, text='Show link lights', variable=show_link_lights_var,
                                            onvalue=True, offvalue=False,
                                            command=lambda i="show_link_lights",
                                                           j=show_link_lights_var, c=canvas: set_preferences(i, j, c))
    show_link_lights_check.grid(row=2, column=0, sticky=tk.W)
    # Show link lights by default #

    # Persistent Cable Connect #
    persistent_cable_conn_var = tk.BooleanVar()
    persistent_cable_conn_check = tk.Checkbutton(frame, text='Persistent cable connection',
                                                 variable=persistent_cable_conn_var,
                                                 onvalue=True, offvalue=False,
                                                 command=lambda i="persistent_cable_con",
                                                                j=persistent_cable_conn_var: set_preferences(i, j))
    persistent_cable_conn_check.grid(row=3, column=0, sticky=tk.W)
    # Persistent Cable Connect #

    # Save/Load file directory
    label = tk.Label(frame, text='Save Directory', font=('Arial', 10, 'bold'))
    label.grid(row=4, column=0, sticky=tk.W, pady=(10, 0))

    folder_path = tk.Text(frame, width=75, height=1)
    folder_path.grid(row=5, column=0, sticky=tk.W, padx=(4, 10))
    folder_path.insert('end', globalVars.file_directory)
    folder_path.configure(state='disabled')

    browse_button = tk.Button(frame, text='Browse',
                              command=lambda popup=preferences_popup, path=folder_path: hf.open_folder_dialogue(popup,
                                                                                                                path),
                              relief=tk.GROOVE)
    browse_button.grid(row=5, column=1, sticky=tk.W)
    browse_button.bind('<Enter>', lambda e, b=browse_button: hf.button_enter(e, b))
    browse_button.bind('<Leave>', lambda e, b=browse_button: hf.button_leave(e, b))

    # Change label contents

    # Save/Load file directory

    # Check buttons that were previously set
    if globalVars.ask_before_delete:
        ask_b4_del_check.select()

    if globalVars.ask_before_quick_delete:
        ask_b4_quick_del_check.select()

    if globalVars.show_link_lights:
        show_link_lights_check.select()

    if globalVars.persistent_cable_connect:
        persistent_cable_conn_check.select()


def set_preferences(option, value, canvas=None):
    match option:
        case "ask_before_delete":
            if value.get():
                globalVars.ask_before_delete = True
            else:
                globalVars.ask_before_delete = False

        case "ask_before_quick_delete":
            if value.get():
                globalVars.ask_before_quick_delete = True
            else:
                globalVars.ask_before_quick_delete = False

        case "show_link_lights":
            if value.get():
                globalVars.show_link_lights = True
                globalVars.light_state = True
            else:
                globalVars.show_link_lights = False
                globalVars.light_state = False

            toggle_link_lights(canvas, checkbox=True)

        case "persistent_cable_con":
            if value.get():
                globalVars.persistent_cable_connect = True
            else:
                globalVars.persistent_cable_connect = False

        case _:
            raise Exception()

    # Save preferences when anything changes
    with open('../preferences.json', 'w') as F:
        F.write(json.dumps([globalVars.file_directory, globalVars.ask_before_delete, globalVars.ask_before_quick_delete,
                            globalVars.show_link_lights, globalVars.persistent_cable_connect]))


def open_help_menu(master):
    def show_help_description(event):
        selected_item = help_items.focus()
        selected_item = help_items.item(selected_item)['text']
        hf.show_info(selected_item, help_menu)

    icon = loadIcons.get_help_menu_icon()

    help_menu = tk.Toplevel(master)
    help_menu.title("Help Menu")
    help_menu.iconphoto(False, icon)
    help_menu.resizable(False, False)

    x = (globalVars.screen_width / 2) - (800 / 2)
    y = (globalVars.screen_height / 2) - (610 / 2) - 50
    help_menu.geometry('%dx%d+%d+%d' % (800, 610, x, y))

    help_menu.focus_set()

    style = ttk.Style()
    style.configure("Treeview", font=('Arial', 10, 'bold'), rowheight=50)
    style.configure("Treeview.Heading", font=('Arial', 12, 'bold'), rowheight=50)

    help_items = ttk.Treeview(help_menu, height=11)
    help_items.heading("#0", text='Help Menu')

    # Top level #
    help_items.insert("", 1, text="Network Simulator")
    nodes = help_items.insert("", 2, text="Nodes")
    help_items.insert("", 3, text="Connecting Nodes")
    draw = help_items.insert("", 4, text="Creating Areas and Labels")
    help_items.insert("", 5, text="Deleting Things")
    help_items.grid(row=0, column=0, padx=(5, 0), pady=(5, 0))

    # Sub Tree views
    help_items.insert(nodes, 1, text="PCs")
    help_items.insert(nodes, 2, text="Switches")
    help_items.insert(nodes, 3, text="Routers")
    help_items.insert(nodes, 4, text="Firewalls")

    help_items.insert(draw, 1, text="Areas")
    help_items.insert(draw, 2, text="Labels")

    help_items.bind('<<TreeviewSelect>>', show_help_description)
