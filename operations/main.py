import json
import threading
from tkinter import *
from PIL import Image, ImageTk
from UI import button_handler
from operations import load_save as ls, globalVars
import operations.backgroundProcesses as bp


def create_menu(canvas_obj, master):
    menu_bar = Menu(tk)
    file_menu = Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="New")
    file_menu.add_command(label="Open", command=lambda c=canvas_obj, m=master: ls.load_file(c, m))
    file_menu.add_command(label="Save", command=ls.save_file)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=tk.quit)
    menu_bar.add_cascade(label="File", menu=file_menu)

    preferences_menu = Menu(menu_bar, tearoff=0)
    preferences_menu.add_command(label="Edit Preferences",
                                 command=lambda m=tk, c=canvas_obj: button_handler.preferences_menu(m, c))
    menu_bar.add_cascade(label="Preferences", menu=preferences_menu)

    help_menu = Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="Help", command=lambda m=master: button_handler.open_help_menu(m))
    help_menu.add_command(label="About/Email me/Suggestions/Even needed?")
    menu_bar.add_cascade(label="Help", menu=help_menu)

    return menu_bar


# window configuration
tk = Tk()
tk.overrideredirect()
width = tk.winfo_screenwidth()
height = tk.winfo_screenheight()
tk.geometry("%dx%d" % (width - 10, height - 10))
tk.state('zoomed')

# Canvas
canvas = Canvas(tk, bg="white", scrollregion=(0, 0, width * 2, height * 2))
canvas.pack(expand=YES, fill=BOTH)

scroll_x = Scrollbar(canvas, orient="horizontal", command=canvas.xview)
scroll_x.pack(expand=NO, fill=BOTH, side=BOTTOM)
scroll_y = Scrollbar(canvas, orient="vertical", command=canvas.yview)
scroll_y.pack(expand=NO, fill=BOTH, side=RIGHT)

canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
canvas.configure(scrollregion=canvas.bbox("all"))

# create top menu
menubar = create_menu(canvas, tk)
tk.config(menu=menubar)

# bottom frame
action_frame = Frame(tk, highlightbackground="grey22", highlightthickness=1.5, height=(height * 0.25))
action_frame.pack(expand=NO, fill=BOTH)

# device buttons and logic
device_frame = LabelFrame(action_frame, text="Devices", padx=5, pady=5)
device_frame.place(x=30, y=(((height * 0.25) - 175) / 2), height=175, width=175)

cable_frame = LabelFrame(action_frame, text="Cables", padx=5, pady=5)
cable_frame.place(x=225, y=(((height * 0.25) - 175) / 2), height=175, width=82)

pc = Image.open("icons/desktop-computer.png")
sw = Image.open("icons/switch.png")
ro = Image.open("icons/router.png")
fw = Image.open("icons/firewall.png")
eth_cable = Image.open("icons/ethernet.png")
ser_cable = Image.open("icons/serial.png")
rectangle = Image.open("icons/rectangle.png")
label = Image.open("icons/label.png")
x = Image.open("icons/x.png")

pc = pc.resize((50, 50))
sw = sw.resize((50, 50))
ro = ro.resize((50, 50))
fw = fw.resize((45, 45))
eth_cable = eth_cable.resize((40, 40))
ser_cable = ser_cable.resize((40, 40))
rectangle = rectangle.resize((50, 50))
label = label.resize((35, 35))
x = x.resize((27, 27))

pc1 = ImageTk.PhotoImage(pc)
sw1 = ImageTk.PhotoImage(sw)
ro1 = ImageTk.PhotoImage(ro)
fw1 = ImageTk.PhotoImage(fw)
eth_cable1 = ImageTk.PhotoImage(eth_cable)
ser_cable1 = ImageTk.PhotoImage(ser_cable)
rectangle1 = ImageTk.PhotoImage(rectangle)
label1 = ImageTk.PhotoImage(label)
x1 = ImageTk.PhotoImage(x)

# Node buttons
host_button = Button(device_frame, image=pc1, width=60, height=60, relief=GROOVE,
                     command=lambda: button_handler.handle_button_click(tk, canvas, "endhost",
                                                                        globalVars.internal_clock))
host_button.grid(column=0, row=0, padx=10)
host_button.bind('<Enter>', lambda e, btn=host_button: button_handler.hf.button_enter(e, btn))
host_button.bind('<Leave>', lambda e, btn=host_button: button_handler.hf.button_leave(e, btn))

switch_button = Button(device_frame, image=sw1, width=60, height=60, relief=GROOVE,
                       command=lambda: button_handler.handle_button_click(tk, canvas, "switch",
                                                                          globalVars.internal_clock))
switch_button.grid(column=1, row=0)

switch_button.bind('<Enter>', lambda e, btn=switch_button: button_handler.hf.button_enter(e, btn))
switch_button.bind('<Leave>', lambda e, btn=switch_button: button_handler.hf.button_leave(e, btn))

router_button = Button(device_frame, image=ro1, width=60, height=60, relief=GROOVE,
                       command=lambda: button_handler.handle_button_click(tk, canvas, "router",
                                                                          globalVars.internal_clock))
router_button.grid(column=0, row=1, padx=10, pady=5)
router_button.bind('<Enter>', lambda e, btn=router_button: button_handler.hf.button_enter(e, btn))
router_button.bind('<Leave>', lambda e, btn=router_button: button_handler.hf.button_leave(e, btn))

fw_button = Button(device_frame, image=fw1, width=60, height=60, relief=GROOVE,
                   command=lambda: button_handler.handle_button_click(tk, canvas, "firewall",
                                                                      globalVars.internal_clock))
fw_button.grid(column=1, row=1, pady=5)
fw_button.bind('<Enter>', lambda e, btn=fw_button: button_handler.hf.button_enter(e, btn))
fw_button.bind('<Leave>', lambda e, btn=fw_button: button_handler.hf.button_leave(e, btn))

eth_button = Button(cable_frame, image=eth_cable1, width=60, height=60, relief=GROOVE,
                    command=lambda: button_handler.handle_button_click(tk, canvas, "Eth_cable",
                                                                       globalVars.internal_clock))
eth_button.grid(column=0, row=0)
eth_button.bind('<Enter>', lambda e, btn=eth_button: button_handler.hf.button_enter(e, btn))
eth_button.bind('<Leave>', lambda e, btn=eth_button: button_handler.hf.button_leave(e, btn))

ser_button = Button(cable_frame, image=ser_cable1, width=60, height=60, relief=GROOVE)
ser_button.grid(column=0, row=1, pady=5)
ser_button.bind('<Enter>', lambda e, btn=ser_button: button_handler.hf.button_enter(e, btn))
ser_button.bind('<Leave>', lambda e, btn=ser_button: button_handler.hf.button_leave(e, btn))

# Toggle Button Stuff
toggle_frame = LabelFrame(action_frame, text="Toggle", padx=5, pady=5)
# toggle_frame.place(x=width - 230, y=825, height=175, width=200)
toggle_frame.place(x=width - 230, y=(((height * 0.25) - 175) / 2), height=175, width=200)

light_button = Button(toggle_frame, command=lambda c=canvas: button_handler.toggle_link_lights(c),
                      text="Toggle Link Lights", width=25, height=3, relief=GROOVE)
light_button.grid(column=0, row=0, pady=5)
light_button.bind('<Enter>', lambda e, btn=light_button: button_handler.hf.button_enter(e, btn))
light_button.bind('<Leave>', lambda e, btn=light_button: button_handler.hf.button_leave(e, btn))

label_button = Button(toggle_frame, command=lambda c=canvas: button_handler.toggle_labels(c),
                      text="Toggle Labels", width=25, height=3, relief=GROOVE)
label_button.grid(column=0, row=1, pady=10)
label_button.bind('<Enter>', lambda e, btn=label_button: button_handler.hf.button_enter(e, btn))
label_button.bind('<Leave>', lambda e, btn=label_button: button_handler.hf.button_leave(e, btn))
# Toggle Button Stuff

# Canvas Drawing Stuff
canvas_drawing = LabelFrame(action_frame, text="Canvas", padx=5, pady=5)
canvas_drawing.place(x=width - 475, y=(((height * 0.25) - 175) / 2), height=175, width=225)

rect_button = Button(canvas_drawing, command=lambda: button_handler.create_rectangle(canvas), text="  Create Rectangle",
                     image=rectangle1, compound="left", width=175, height=50, relief=GROOVE)
rect_button.grid(column=0, row=0, pady=5, padx=12)
rect_button.bind('<Enter>', lambda e, btn=rect_button: button_handler.hf.button_enter(e, btn))
rect_button.bind('<Leave>', lambda e, btn=rect_button: button_handler.hf.button_leave(e, btn))

new_label_button = Button(canvas_drawing, command=lambda: button_handler.handle_button_click(tk, canvas, "Label",
                                                                                             globalVars.internal_clock),
                          text="       Create Label", image=label1, compound="left", width=175, height=50,
                          relief=GROOVE)
new_label_button.grid(column=0, row=1, pady=10)
new_label_button.bind('<Enter>', lambda e, btn=new_label_button: button_handler.hf.button_enter(e, btn))
new_label_button.bind('<Leave>', lambda e, btn=new_label_button: button_handler.hf.button_leave(e, btn))
# Canvas Drawing Stuff

# Delete Button Stuff
canvas_delete = LabelFrame(action_frame, text="Quick Delete", padx=16, pady=3)
canvas_delete.place(x=width - 567, y=((height * 0.25) / 2) + 11, height=75, width=75)

del_button = Button(canvas_delete, command=lambda: button_handler.delete_object(canvas, x1),
                    image=x1, width=40, height=40, relief=GROOVE)
del_button.grid(row=0, column=0)
del_button.bind('<Enter>', lambda e, btn=del_button: button_handler.hf.button_enter(e, btn))
del_button.bind('<Leave>', lambda e, btn=del_button: button_handler.hf.button_leave(e, btn))
# Delete Button Stuff

# Load Preferences
try:
    with open('../preferences.json', 'r+') as F:
        preferences = json.load(F)
        globalVars.file_directory = preferences[0]
        globalVars.ask_before_delete = preferences[1]
        globalVars.ask_before_quick_delete = preferences[2]
        globalVars.show_link_lights = preferences[3]
        globalVars.persistent_cable_connect = preferences[4]
except FileNotFoundError:
    with open('../preferences.json', 'w+') as F:
        F.write('["/", true, true, true, true]')

# Threads
time_counter = threading.Thread(target=bp.count_time, daemon=True, args=(globalVars.internal_clock,))
time_counter.start()

arp_mac_aging = threading.Thread(target=bp.arp_mac_aging, args=(globalVars.internal_clock,), daemon=True)
arp_mac_aging.start()


# launch
tk.mainloop()

# TODO Order:
#   - Trunk ports / ROAS
#   - hf.window_close
#   - Center node menus like other menus
#   - Are you sure you want to exit? / Prompt save if anything changes
#           (global var, set true in any class if something happens)
#   - Preferences: Generate random MAC and IP for end hosts: provide an option for subnet mask?
#   7. Cable connect: Switch, then cancel (Same ethernet obj), then pc to switch --> ERROR!
#   8. Add About/Feedback menu
#   9. Reboot devices (Introduce startup/running configs) --> See if packet tracer saves configuration after closing
#                                                             but not writing to mem.
#   10. Disconnect menu button
#   11. Other TODOs
