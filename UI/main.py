from tkinter import *
from PIL import Image, ImageTk
import button_handler

global img


def create_menu():
    menu_bar = Menu(tk)
    file_menu = Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="New")
    file_menu.add_command(label="Open", )
    file_menu.add_command(label="Save", )
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=tk.quit)
    menu_bar.add_cascade(label="File", menu=file_menu)

    help_menu = Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="Help Index")
    help_menu.add_command(label="About...")
    menu_bar.add_cascade(label="Help", menu=help_menu)

    return menu_bar


# window configuration
tk = Tk()
tk.overrideredirect()
width = tk.winfo_screenwidth()
height = tk.winfo_screenheight()
tk.geometry("%dx%d" % (width - 10, height - 10))

# create top menu
menubar = create_menu()

# Canvas
canvas = Canvas(tk, bg="white", height=height * 2, width=width * 2, scrollregion=(0, 0, width * 2, height * 2))
canvas.pack(expand=YES, fill=BOTH)

scroll_x = Scrollbar(tk, orient="horizontal", command=canvas.xview)
scroll_x.place(x=0, y=778, width=width)
scroll_y = Scrollbar(tk, orient="vertical", command=canvas.yview)
scroll_y.place(x=width - 17, y=0, height=777)

canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
canvas.configure(scrollregion=canvas.bbox("all"))

# bottom frame
action_frame = Frame(tk, highlightbackground="grey22", highlightthickness=1.5)
action_frame.place(x=0, y=795, width=width, height=height - 840)

# device buttons and logic
device_frame = LabelFrame(tk, text="Devices", padx=5, pady=5)
device_frame.place(x=30, y=825, height=175, width=175)

cable_frame = LabelFrame(tk, text="Cables", padx=5, pady=5)
cable_frame.place(x=225, y=825, height=175, width=82)

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

Button(device_frame, image=pc1, width=60, height=60,
       command=lambda: button_handler.handle_button_click(tk, canvas, "endhost")).grid(
    column=0, row=0,
    padx=10)
Button(device_frame, image=sw1, width=60, height=60,
       command=lambda: button_handler.handle_button_click(tk, canvas, "switch")).grid(
    column=1,
    row=0)
Button(device_frame, image=ro1, width=60, height=60,
       command=lambda: button_handler.handle_button_click(tk, canvas, "router")).grid(column=0,
                                                                                      row=1,
                                                                                      padx=10,
                                                                                      pady=5)
Button(device_frame, image=fw1, width=60, height=60,
       command=lambda: button_handler.handle_button_click(tk, canvas, "firewall")).grid(column=1,
                                                                                        row=1,
                                                                                        pady=5)

Button(cable_frame, image=eth_cable1, width=60, height=60,
       command=lambda: button_handler.handle_button_click(tk, canvas, "Eth_cable")).grid(column=0, row=0)


Button(cable_frame, image=ser_cable1, width=60, height=60).grid(column=0, row=1, pady=5)

# Toggle Button Stuff
toggle_frame = LabelFrame(tk, text="Toggle", padx=5, pady=5)
toggle_frame.place(x=width - 230, y=825, height=175, width=200)
b = Button(toggle_frame, command=button_handler.toggle_link_lights, text="Toggle Link Lights", width=25, height=3)
b.grid(column=0, row=0, pady=5)
b.config(state="disabled")


Button(toggle_frame, command=button_handler.toggle_labels, text="Toggle Labels", width=25, height=3).grid(column=0,
                                                                                                          row=1,
                                                                                                          pady=10)
# Toggle Button Stuff

# Canvas Drawing Stuff
canvas_drawing = LabelFrame(tk, text="Canvas", padx=5, pady=5)
canvas_drawing.place(x=width - 475, y=825, height=175, width=225)

Button(canvas_drawing, command=lambda: button_handler.create_rectangle(canvas), text="  Create Rectangle",
       image=rectangle1, compound="left", width=175, height=50).grid(column=0, row=0, pady=5, padx=12)

Button(canvas_drawing, command=lambda: button_handler.handle_button_click(tk, canvas, "Label"),
       text="       Create Label", image=label1, compound="left", width=175, height=50).grid(column=0, row=1, pady=10)
# Canvas Drawing Stuff

# Delete Button Stuff
canvas_delete = LabelFrame(tk, text="Delete", padx=12, pady=3)
canvas_delete.place(x=width - 567, y=925, height=75, width=75)

Button(canvas_delete, command=lambda: button_handler.delete_object(canvas, x1),
       image=x1, width=40, height=40).grid(row=0, column=0)
# Delete Button Stuff

# launch
tk.config(menu=menubar)
tk.mainloop()
