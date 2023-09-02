import tkinter as tk
from tkinter import colorchooser, messagebox
import network.PC
import network.Switch
import network.Ethernet_Cable
import network.Router
from PCCanvasObject import PCCanvasObject
from SwitchCanvasObject import SwitchCanvasObject
from EthernetCableCanvasObject import EthernetCableCanvasObject
from RouterCanvasObject import RouterCanvasObject
from RectangleCanvasObject import RectangleCanvasObject
from LabelCanvasObject import LabelCanvasObject
import helper_functions as hf
from UI import loadIcons

objects = []
cable_objects = []
canvas_rectangles = []
canvas_labels = []
number = 0

light_state = False


def get_next_pc(generation):
    return generation + "_PC_" + str(hf.get_next_number())


def get_next_switch():
    return "SW_" + str(hf.get_next_number())


def get_next_router():
    return "Router_" + str(hf.get_next_number())


def get_next_cable(canvas):
    return "Eth_" + str(len(canvas.find_withtag('Ethernet')) + 1)


def get_next_rectangle(canvas):
    return "Rectangle_" + str(len(canvas.find_withtag('Rectangle')) + 1)


def get_next_label(canvas):
    return "Label_" + str(len(canvas.find_withtag('Label')) + 1)


def create_pc(popup, canvas, generation, master, icons):
    pc = PCCanvasObject(canvas, get_next_pc(generation), icons, network.PC.PC(generation), master)
    objects.append(pc)
    popup.destroy()


def create_switch(popup, canvas, icons, switch_type, master):
    if switch_type == "TSA1000X":
        switch = SwitchCanvasObject(canvas, get_next_switch(), icons, network.Switch.Switch(), master)
        objects.append(switch)
    elif switch_type == "RTSA1000X":
        pass

    popup.destroy()


def create_router(popup, canvas, icons, master):
    router = RouterCanvasObject(canvas, get_next_router(), icons, network.Router.Router(), master)
    objects.append(router)
    popup.destroy()


def handle_button_click(master, canvas, device_type):
    if device_type == "endhost":

        pc_icons = loadIcons.get_pc_icons()

        popup = tk.Toplevel(master)
        popup.title("Add End Host")
        popup.iconphoto(False, pc_icons[0])

        popup.geometry("%dx%d+%d+%d" % (450, 325, 740, 300))
        # popup.attributes('-toolwindow', True)

        frame = tk.LabelFrame(popup, padx=5, pady=5)
        frame.place(x=10, y=10, height=300, width=425)

        pc_button = tk.Button(frame, width=10, height=5, text="PC", relief=tk.GROOVE,
                              command=lambda: create_pc(popup, canvas, "SecondGen", master, pc_icons))
        pc_button.place(x=165, y=80)
        pc_button.bind('<Enter>', lambda e, btn=pc_button: hf.button_enter(e, btn))
        pc_button.bind('<Leave>', lambda e, btn=pc_button: hf.button_leave(e, btn))

        tk.Label(frame, text="One Gigabit Ethernet Interface\n(1000 mbps)").place(x=126, y=180)
        popup.focus_set()

    elif device_type == "switch":

        sw_icons = loadIcons.get_sw_icons()

        popup = tk.Toplevel(master)
        popup.title("Add Switch")
        popup.geometry("%dx%d+%d+%d" % (550, 325, 675, 300))
        popup.iconphoto(False, sw_icons[0])
        # popup.attributes('-toolwindow', True)

        frame = tk.LabelFrame(popup, padx=5, pady=5)
        frame.place(x=10, y=10, height=300, width=525)

        l2sw_btn = tk.Button(frame, width=10, height=5, text="TSA1000X", relief=tk.GROOVE,
                             command=lambda: create_switch(popup, canvas, sw_icons, "TSA1000X", master))
        l2sw_btn.place(x=100, y=30)
        l2sw_btn.bind('<Enter>', lambda e, btn=l2sw_btn: hf.button_enter(e, btn))
        l2sw_btn.bind('<Leave>', lambda e, btn=l2sw_btn: hf.button_leave(e, btn))

        l3sw_btn = tk.Button(frame, width=10, height=5, text="RTSA1000X", relief=tk.GROOVE,
                             command=lambda: create_switch(popup, canvas, sw_icons, "RTSA1000X", master))
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

        popup.focus_set()

    elif device_type == "router":

        r_icons = loadIcons.get_router_icons()

        popup = tk.Toplevel(master)
        popup.title("Add Router")
        popup.geometry("%dx%d+%d+%d" % (450, 325, 740, 300))
        popup.iconphoto(False, r_icons[0])
        # popup.attributes('-toolwindow', True)

        frame = tk.LabelFrame(popup, padx=5, pady=5)
        frame.place(x=10, y=10, height=300, width=425)

        ro_btn = tk.Button(frame, width=10, height=5, text="R94X", relief=tk.GROOVE,
                           command=lambda: create_router(popup, canvas, r_icons, master))
        ro_btn.place(x=165, y=80)
        ro_btn.bind('<Enter>', lambda e, btn=ro_btn: hf.button_enter(e, btn))
        ro_btn.bind('<Leave>', lambda e, btn=ro_btn: hf.button_leave(e, btn))

        tk.Label(frame, text="Standard Router").place(x=158, y=180)

        popup.focus_set()

    # elif device_type == "l3sw":
    #     pass

    elif device_type == "Eth_cable":
        eth_icon = "icons/ethernet.png"
        cable = EthernetCableCanvasObject(canvas, get_next_cable(canvas), eth_icon,
                                          network.Ethernet_Cable.EthernetCable())
        cable_objects.append(cable)

    elif device_type == "Label":
        popup = tk.Toplevel(master)
        popup.title("Add Label")
        popup.geometry("%dx%d+%d+%d" % (250, 150, 825, 350))
        popup.iconphoto(False, loadIcons.get_label_icon()[0])
        # popup.attributes('-toolwindow', True)

        frame = tk.LabelFrame(popup, padx=5, pady=5)
        frame.place(x=10, y=10, height=130, width=230)

        tk.Label(frame, text="Label Text:").place(x=10, y=30)
        text = tk.Entry(frame, width=19)
        text.place(x=80, y=30)

        label_btn = tk.Button(frame, width=10, height=1, text="Create Label", relief=tk.GROOVE,
                              command=lambda: create_label(popup, canvas, text.get()))
        label_btn.place(x=67, y=75)
        label_btn.bind('<Enter>', lambda e, btn=label_btn: hf.button_enter(e, btn))
        label_btn.bind('<Leave>', lambda e, btn=label_btn: hf.button_leave(e, btn))

        popup.focus_set()


def toggle_link_lights(canvas):
    global light_state

    lights = canvas.find_withtag("light")
    for i in lights:
        if not light_state:
            canvas.itemconfig(i, state='hidden')
        else:
            canvas.itemconfig(i, state='normal')

    light_state = not light_state


def toggle_labels(canvas):
    for i in canvas_labels:
        i.toggle_label(False)

    # Check if all labels are in the same state. If not, show them all to reset the state.
    labels = canvas.find_withtag("Label")
    if any(canvas.itemcget(i, 'state') == 'hidden' for i in labels) and any(
            canvas.itemcget(i, 'state') == 'normal' for i in labels):
        for i in canvas_labels:
            i.toggle_label(True)


def create_rectangle(canvas):
    color_code = colorchooser.askcolor(title="Choose Box Color")
    rectangle = RectangleCanvasObject(canvas, color_code, get_next_rectangle(canvas))
    canvas_rectangles.append(rectangle)


def create_label(popup, canvas, text):
    if text:
        label = LabelCanvasObject(canvas, get_next_label(canvas), text)
        canvas_labels.append(label)
        popup.destroy()
    else:
        messagebox.showerror('Invalid Parameter', 'Please Enter Some Text', parent=popup)


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

            for i in objects:
                if i.get_block_name() == canvas_object_tag:
                    i.menu_delete(None)
                    return

            # for i in cable_objects:
            #     if i.get_block_name() == canvas_object_tag:
            #         i.menu_delete()
            #         return

            for i in canvas_rectangles:
                if i.get_block_name() == canvas_object_tag:
                    i.delete()
                    return

            for i in canvas_labels:
                if i.get_block_name() == canvas_object_tag:
                    i.delete()
                    return
            return

    hf.move_mouse_to(1400, 800)
    x = canvas.canvasx(canvas.winfo_pointerx() - canvas.winfo_rootx())
    y = canvas.canvasy(canvas.winfo_pointery() - canvas.winfo_rooty())

    canvas_object = canvas.create_image(x, y, image=icon)
    canvas.photo = icon

    canvas.tag_bind(canvas_object, "<Motion>", motion)
    canvas.tag_bind(canvas_object, "<Button-1>", delete)
