import tkinter as tk
from PIL import Image, ImageTk
import UI.helper_functions as hf
from RouterCLI import RouterCli
from UI.PCCanvasObject import PCCanvasObject


class RouterCanvasObject:
    def __init__(self, canvas, block_name, icon, class_object):
        self.canvas = canvas
        self.block_name = block_name
        self.class_object = class_object
        self.class_object.set_canvas_object(self)
        self.delete_info = []  # Store information when line is created for when delete is needed

        # Submenu Stuff
        self.submenu = tk.Menu(self.canvas, tearoff=0)
        self.disconnect_menu = tk.Menu(self.submenu, tearoff=0)  # Submenu for disconnecting interfaces
        self.submenu.add_command(label="Terminal", command=self.menu_router_cli)
        self.submenu.add_cascade(label="Disconnect", menu=self.disconnect_menu)
        self.submenu.add_separator()
        self.submenu.add_command(label="Delete Router", command=self.menu_delete)
        # Submenu Stuff

        # Current Cursor Location
        # For placing the new widget under the mouse
        x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
        y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
        # Current Cursor Location

        # Icon Stuff
        self.icon = icon
        self.icon = Image.open(self.icon)
        self.icon = self.icon.resize((70, 70))
        self.icon = ImageTk.PhotoImage(self.icon)
        # Assigned to canvas_object to allow delete
        self.canvas_object = self.canvas.create_image(x, y, image=self.icon,
                                                      tags=(self.block_name, "Router"))
        self.canvas.photo = self.icon
        # Icon Stuff

        # Button Bindings
        self.canvas.tag_bind(self.block_name, '<Motion>', self.motion)  # When creating the object
        self.canvas.tag_bind(self.block_name, '<Button-1>', self.motion)  # When creating the object
        self.canvas.tag_bind(self.block_name, '<B1-Motion>', self.motion)  # When moving the object after it is created
        self.canvas.tag_bind(self.block_name, '<Button-3>', self.sub_menu)  # For the object menu
        # Button Bindings

        # CLI Stuff
        self.cli_object = None
        self.cli_command_files = ["..\\commands/ro_general_command_list", "..\\commands/ro_interface_command_list"]
        # CLI Stuff

        # Device Label
        # self.device_label = tk.Label(self.canvas, text="Router " + str(hf.increment_ro_id()), background="gray88",
        #                              font=("Arial", 10))
        # self.canvas_label = self.canvas.create_window(x, y + 60, window=self.device_label, tag=self.block_name + "_tag")
        # self.hidden_label = False
        # Device Label

        # Light Stuff
        self.line_connections = {}
        self.x_flag = None
        self.y_flag = None
        self.line_interface_relations = {}
        # Light Stuff

        # To save CLI text
        self.cli_text = "Router> "
        # To save CLI text

    def motion(self, event=None):

        # Not event is true when the object being moved calls the other objects motion function
        if not event:
            event_x = self.canvas.coords(self.block_name)[0] + 0.000005
            event_y = self.canvas.coords(self.block_name)[1] + 0.000005
        else:
            event_x = event.x
            event_y = event.y

        # Move the object
        self.canvas.coords(self.block_name, self.canvas.canvasx(event_x), self.canvas.canvasy(event_y))

        # Move the Label
        self.canvas.coords(self.block_name + "_tag", self.canvas.canvasx(event_x), self.canvas.canvasy(event_y) + 60)

        try:
            for i in self.line_connections:

                # Shift the other object to adjust the lines
                if event:

                    # make sure not calling self, and not calling a PC object
                    if self.block_name == i.get_obj_2().get_block_name() and type(
                            i.get_obj_2()) != PCCanvasObject and type(i.get_obj_1()) != PCCanvasObject:
                        i.get_obj_1().motion()
                    elif type(i.get_obj_2()) != PCCanvasObject and type(i.get_obj_1()) != PCCanvasObject:
                        i.get_obj_2().motion()

                line_count = self.get_line_connection_count(self.line_connections[i][0], self.line_connections[i][1])
                for j in range(line_count[0]):

                    line = self.canvas.find_withtag(self.line_connections[i][0] + "_line_"
                                                    + self.line_connections[i][1] + "_" + str(j))

                    light_1 = self.canvas.find_withtag(
                        self.line_connections[i][0] + "_light_" + self.line_connections[i][1] + "_" + str(j))
                    light_2 = self.canvas.find_withtag(
                        self.line_connections[i][1] + "_light_" + self.line_connections[i][0] + "_" + str(j))

                    c = self.canvas.coords(line)

                    # /// Line Shits and Corrections
                    if c[0] < c[2]:
                        x_flag = True
                    else:
                        x_flag = False
                    if c[1] < c[3]:
                        y_flag = True
                    else:
                        y_flag = False

                    self.x_flag = x_flag
                    self.y_flag = y_flag
                    # Fixing overlapping lines

                    # How to shift the new line based on the line relations
                    x_shift = 0
                    y_shift = 0
                    if self.x_flag and not self.y_flag:  # Left and Under
                        x_shift = 6 * j
                        y_shift = 6 * j
                    elif self.x_flag and self.y_flag:  # Left and Above
                        x_shift = 6 * j
                        y_shift = -6 * j
                    elif not self.x_flag and not self.y_flag:  # Right and Under
                        x_shift = -6 * j
                        y_shift = 6 * j
                    elif not self.x_flag and self.y_flag:  # Right and Above
                        x_shift = -6 * j
                        y_shift = -6 * j
                    # /// Line Shits and Corrections

                    if line:

                        l1 = None
                        l2 = None
                        if event:
                            self.canvas.delete(light_1)
                            l1 = hf.draw_circle(self.canvas.coords(line)[0], self.canvas.coords(line)[1],
                                                self.canvas.coords(line)[2],
                                                self.canvas.coords(line)[3], 4, self.canvas,
                                                self.line_connections[i][0] + "_light_" + self.line_connections[i][
                                                    1] + "_" + str(j))
                            self.canvas.delete(light_2)
                            l2 = hf.draw_circle(self.canvas.coords(line)[2], self.canvas.coords(line)[3],
                                                self.canvas.coords(line)[0],
                                                self.canvas.coords(line)[1], 4, self.canvas,
                                                self.line_connections[i][1] + "_light_" + self.line_connections[i][
                                                    0] + "_" + str(j))

                        if 0 <= abs(self.canvas.canvasx(event_x) - self.canvas.coords(line)[0]) <= 30 and 0 <= abs(
                                self.canvas.canvasy(event_y) - self.canvas.coords(line)[1]) <= 30:

                            self.canvas.coords(line, self.canvas.canvasx(event_x) + x_shift,
                                               self.canvas.canvasy(event_y) + y_shift,
                                               self.canvas.coords(line)[2], self.canvas.coords(line)[3])

                            if event:
                                self.canvas.itemconfig(l1, fill=hf.get_color_from_op(
                                    self.line_interface_relations[line[0]][0].get_is_operational()))
                                self.canvas.itemconfig(l2, fill=hf.get_color_from_op(
                                    self.line_interface_relations[line[0]][1].get_is_operational()))

                        elif 0 <= abs(self.canvas.canvasx(event_x) - self.canvas.coords(line)[2]) <= 30 and 0 <= abs(
                                self.canvas.canvasy(event_y) - self.canvas.coords(line)[3]) <= 30:

                            self.canvas.coords(line, self.canvas.coords(line)[0], self.canvas.coords(line)[1],
                                               self.canvas.canvasx(event_x) + x_shift,
                                               self.canvas.canvasy(event_y) + y_shift)

                            if event:
                                self.canvas.itemconfig(l2, fill=hf.get_color_from_op(
                                    self.line_interface_relations[line[0]][0].get_is_operational()))
                                self.canvas.itemconfig(l1, fill=hf.get_color_from_op(
                                    self.line_interface_relations[line[0]][1].get_is_operational()))

        except StopIteration:
            pass

        # Unbind after created
        if event and str(event.type) == "4":
            self.canvas.tag_unbind(self.block_name, "<Motion>")
            self.canvas.tag_unbind(self.block_name, "<Button-1>")
        return

    def sub_menu(self, event):
        self.submenu.tk_popup(event.x_root, event.y_root)

    def add_to_disconnect_menu(self, interface):
        self.disconnect_menu.add_command(label=interface.get_shortened_name(),
                                         command=lambda: self.disconnect_cable(interface))

    def disconnect_cable(self, interface):
        try:
            self.disconnect_menu.delete(interface.get_shortened_name())
            interface.get_canvas_cable().delete()
        except tk.TclError:
            pass

    def menu_delete(self):
        self.canvas.delete(self.canvas_object)
        # self.canvas.delete(self.canvas_label)

        self.class_object = None

    def menu_router_cli(self):
        # Parent widget
        popup = tk.Toplevel(self.canvas)
        popup.geometry("%dx%d+%d+%d" % (700, 800, 600, 125))
        popup.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(popup))
        # Parent widget

        self.cli_object = RouterCli(self, self.class_object, popup, self.cli_text, "Router> ", self.cli_command_files)

    def get_block_name(self):
        return self.block_name

    def get_class_object(self):
        return self.class_object

    def on_closing(self, popup):
        # Save CLI text
        self.cli_text = self.cli_object.on_closing()
        popup.destroy()

    # def toggle_label(self):
        # self.hidden_label = not self.hidden_label
        # if self.hidden_label:
            # self.canvas.itemconfigure(self.canvas_label, state='hidden')
        # else:
            # self.canvas.itemconfigure(self.canvas_label, state='normal')

    def add_line_connection(self, tag1, tag2, light1, light2, canvas_cable_object):
        self.line_connections[canvas_cable_object] = [tag1, tag2, light1, light2]

    def get_line_connection_count(self, tag1, tag2):

        count = 0
        lines = {}

        for i in self.line_connections:
            if self.line_connections[i][0] == tag1 and self.line_connections[i][1] == tag2:
                count += 1
                lines[i] = [self.line_connections[i][0], self.line_connections[i][1], self.line_connections[i][2],
                            self.line_connections[i][3]]
            elif self.line_connections[i][0] == tag2 and self.line_connections[i][1] == tag1:
                count += 1
                lines[i] = [self.line_connections[i][1], self.line_connections[i][0], self.line_connections[i][3],
                            self.line_connections[i][2]]

        if count > 0:
            return count, lines
        else:
            return 0, None

    def set_interfaces(self, line, int1, int2):
        self.line_interface_relations[line] = [int1, int2]
