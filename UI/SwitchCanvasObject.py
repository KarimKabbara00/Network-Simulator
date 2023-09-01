import tkinter as tk

from ttkwidgets.frames import Tooltip

import UI.helper_functions as hf
from PCCanvasObject import PCCanvasObject
from SwitchCLI import SwitchCli
import tkinter


class SwitchCanvasObject:

    def __init__(self, canvas, block_name, icons, class_object, master):
        self._x = None
        self._y = None
        self.canvas = canvas
        self.block_name = block_name
        self.class_object = class_object
        self.class_object.set_canvas_object(self)
        self.master = master

        # Cursor Location when object is created
        x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
        y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
        # Cursor Location when object is created

        # Icon Stuff
        self.icon = icons[0]
        self.terminal_icon = icons[1]
        self.ethernet_del_icon = icons[2]
        self.x_node_icon = icons[3]
        # Assigned to canvas_object to allow delete
        self.canvas_object = self.canvas.create_image(x, y, image=self.icon, tags=(self.block_name, "Switch"))
        self.canvas.photo = self.icon
        # Icon Stuff

        # Hover menu Stuff
        self.hover_area = self.canvas.create_polygon(x - 50, y - 35, x + 50, y - 35, x + 50, y - 50, x + 90, y - 50,
                                                     x + 90, y + 60,
                                                     x + 50, y + 60, x + 50, y + 45, x - 50, y + 45, fill="")
        self.canvas.lower(self.hover_area)
        self.menu_buttons = self.canvas.create_polygon(x + 40, y - 5, x + 50, y - 5, x + 50, y - 72, x + 92, y - 72,
                                                       x + 92, y + 72, x + 50,
                                                       y + 72, x + 50, y + 5, outline="black", fill="navajo white",
                                                       width=1)
        self.canvas.itemconfigure(self.menu_buttons, state='hidden')

        self.terminal_button = tk.Button(self.canvas, width=25, height=25, image=self.terminal_icon)
        self.disconnect_button = tk.Button(self.canvas, width=25, height=25, image=self.ethernet_del_icon)
        self.delete_button = tk.Button(self.canvas, width=25, height=25, image=self.x_node_icon)

        self.terminal_button.config(background='gray75', foreground="white", relief=tk.GROOVE)
        self.disconnect_button.config(background='gray75', foreground="white", relief=tk.GROOVE)
        self.delete_button.config(background='gray75', foreground="white", relief=tk.GROOVE)
        # Hover menu Stuff

        # Button Bindings
        self.canvas.tag_bind(self.block_name, '<Motion>', self.motion)  # When creating the object
        self.canvas.tag_bind(self.block_name, '<Button-1>', self.motion)  # When creating the object
        self.canvas.tag_bind(self.block_name, '<B1-Motion>', self.motion)  # When moving the object after it is created
        self.canvas.tag_bind(self.block_name, '<ButtonRelease-1>',
                             self.button_release)  # When moving the object after it is created
        # Button Bindings

        # CLI Stuff
        self.cli_object = None
        self.cli_command_files = ['commands/sw_general_command_list', 'commands/sw_interface_command_list']
        # CLI Stuff

        # Light & Line Stuff
        self.line_connections = {}
        self.x_flag = None
        self.y_flag = None
        self.line_interface_relations = {}
        # Light & Line Stuff

        # To save CLI text
        self.cli_text = "Switch> "
        # To save CLI text

    def motion(self, event=None):

        # Not event is true when the object being moved calls the other objects motion function
        if not event:
            event_x = self.canvas.coords(self.block_name)[0] + 0.000005
            event_y = self.canvas.coords(self.block_name)[1] + 0.000005
        else:
            event_x = event.x
            event_y = event.y

        # Hide the menu
        self.unbind_menu_temporarily()

        # Move the hover area and menu buttons
        self.canvas.coords(self.hover_area, self.canvas.canvasx(event_x) - 50, self.canvas.canvasy(event_y) - 35,
                           self.canvas.canvasx(event_x) + 50, self.canvas.canvasy(event_y) - 35,
                           self.canvas.canvasx(event_x) + 50, self.canvas.canvasy(event_y) - 50,
                           self.canvas.canvasx(event_x) + 90, self.canvas.canvasy(event_y) - 50,
                           self.canvas.canvasx(event_x) + 90, self.canvas.canvasy(event_y) + 60,
                           self.canvas.canvasx(event_x) + 50, self.canvas.canvasy(event_y) + 60,
                           self.canvas.canvasx(event_x) + 50, self.canvas.canvasy(event_y) + 45,
                           self.canvas.canvasx(event_x) - 50, self.canvas.canvasy(event_y) + 45)

        self.canvas.coords(self.menu_buttons, self.canvas.canvasx(event_x) + 40, self.canvas.canvasy(event_y),
                           self.canvas.canvasx(event_x) + 50, self.canvas.canvasy(event_y) - 5,
                           self.canvas.canvasx(event_x) + 50, self.canvas.canvasy(event_y) - 50,
                           self.canvas.canvasx(event_x) + 92, self.canvas.canvasy(event_y) - 50,
                           self.canvas.canvasx(event_x) + 92, self.canvas.canvasy(event_y) + 60,
                           self.canvas.canvasx(event_x) + 50, self.canvas.canvasy(event_y) + 60,
                           self.canvas.canvasx(event_x) + 50, self.canvas.canvasy(event_y) + 5)

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

                            self.canvas.tag_lower(l1)
                            self.canvas.tag_lower(l2)
                            self.canvas.tag_lower(line)

                            # COULD THIS CAUSE A LIGHT ISSUE (COLORS)
                            i.set_lights(l1, l2)

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

        self._x = event_x
        self._y = event_y
        return

    def button_release(self, event):

        self.canvas.tag_unbind(self.block_name, "<Motion>")
        self.canvas.tag_unbind(self.block_name, "<Button-1>")

        # For the object menu
        self.canvas.tag_bind(self.hover_area, '<Enter>', self.on_start_hover)
        self.canvas.tag_bind(self.hover_area, '<Leave>', self.on_end_hover)
        self.canvas.tag_bind(self.block_name, '<Enter>', self.on_start_hover)
        self.canvas.tag_bind(self.block_name, '<Leave>', self.on_end_hover)
        self.canvas.tag_bind(self.menu_buttons, '<Enter>', self.on_start_hover)
        self.canvas.tag_bind(self.menu_buttons, '<Leave>', self.on_end_hover)

        self.terminal_button.bind('<Enter>', self.terminal_button_bg_enter)
        self.terminal_button.bind('<Leave>', self.terminal_button_bg_leave)
        self.terminal_button.bind('<Button-1>', self.menu_switch_cli)

        self.disconnect_button.bind('<Enter>', self.disconnect_button_bg_enter)
        self.disconnect_button.bind('<Leave>', self.disconnect_button_bg_leave)
        # self.disconnect_button.bind('<Button-1>', self.disconnect_cable)

        self.delete_button.bind('<Enter>', self.delete_button_bg_enter)
        self.delete_button.bind('<Leave>', self.delete_button_bg_leave)
        self.delete_button.bind('<Button-1>', self.menu_delete)

        self.on_start_hover(event)

    def hide_menu(self):
        self.canvas.itemconfigure(self.menu_buttons, state='hidden')
        self.terminal_button.place_forget()
        self.disconnect_button.place_forget()
        self.delete_button.place_forget()

    def unbind_menu_temporarily(self):
        self.canvas.tag_unbind(self.hover_area, '<Enter>')
        self.canvas.tag_unbind(self.hover_area, '<Leave>')
        self.canvas.tag_unbind(self.block_name, '<Enter>')
        self.canvas.tag_unbind(self.block_name, '<Leave>')
        self.terminal_button.unbind('<Enter>')
        self.disconnect_button.unbind('<Enter>')
        self.delete_button.unbind('<Enter>')
        # Hide menu
        self.hide_menu()

    def disconnect_cable(self, event, cable_name):

        ## menu of some kind

        self.hide_menu()

        # Disable the hover area when disconnect cable is clicked because mouse lands on the hover area causing the menu
        # to reappear instantly. It is re-enabled in self.on_end_hover()
        self.canvas.itemconfigure(self.hover_area, state="hidden")

    def menu_delete(self, event):
        self.hide_menu()
        try:
            for i in self.class_object.get_interfaces():
                if i.get_is_connected():
                    i.get_canvas_cable().delete_canvas_cable()

        except (tk.TclError, AttributeError):
            pass

        self.hide_menu()

        self.canvas.delete(self.canvas_object)
        self.canvas.delete(self.hover_area)
        self.canvas.delete(self.menu_buttons)
        self.canvas.delete()
        self.class_object = None

    def menu_switch_cli(self, event):
        # Parent widget
        popup = tk.Toplevel(self.canvas)
        popup.geometry("%dx%d+%d+%d" % (700, 800, 600, 125))
        popup.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(popup))
        popup.focus_set()
        self.cli_object = SwitchCli(self, self.class_object, popup, self.cli_text, "Switch> ", self.cli_command_files)
        self.hide_menu()

    def on_closing(self, popup):
        # Save CLI text
        self.cli_text = self.cli_object.on_closing()
        popup.destroy()

    def get_block_name(self):
        return self.block_name

    def get_class_object(self):
        return self.class_object

    def add_line_connection(self, tag1, tag2, light1, light2, canvas_cable_object):
        self.line_connections[canvas_cable_object] = [tag1, tag2, light1, light2]

    def del_line_connection(self, cable):
        self.line_connections.pop(cable)

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

    def get_lights(self, line_obj):
        return self.line_connections[line_obj][2], self.line_connections[line_obj][3]
        # TODO: Do i need to update [2] & [3] in the motion def?

    def on_start_hover(self, event):
        if type(self.master.focus_displayof()) == tkinter.Tk:  # If the root has focus
            self.canvas.itemconfigure(self.menu_buttons, state='normal')  # Add the frame to the canvas
            self.terminal_button.place(x=self._x + 57, y=self._y - 42)
            self.disconnect_button.place(x=self._x + 57, y=self._y - 9)
            self.delete_button.place(x=self._x + 57, y=self._y + 24)
        return

    def on_end_hover(self, event):
        self.canvas.itemconfigure(self.menu_buttons, state='hidden')
        self.terminal_button.place_forget()
        self.disconnect_button.place_forget()
        self.delete_button.place_forget()

        # The hover area is disabled when a cable is disconnected because the mouse will land in the hove area and
        # make the menu reappear instantly. This line re-enables it.
        self.canvas.itemconfigure(self.hover_area, state="normal")
        return

    def terminal_button_bg_enter(self, event):
        self.on_start_hover(event)
        Tooltip(self.terminal_button, text="Open the Terminal", showheader=False, offset=(22, -18), background="#feffcd"
                , timeout=0.5)
        self.terminal_button.config(background='gray89', foreground="white", relief=tk.GROOVE)

    def terminal_button_bg_leave(self, event):
        self.terminal_button.config(background='gray75', foreground="white", relief=tk.GROOVE)

    def disconnect_button_bg_enter(self, event):
        self.on_start_hover(event)
        Tooltip(self.disconnect_button, text="Disconnect Connection", showheader=False, offset=(22, -18),
                background="#feffcd", timeout=0.5)
        self.disconnect_button.config(background='gray89', foreground="white", relief=tk.GROOVE)

    def disconnect_button_bg_leave(self, event):
        self.disconnect_button.config(background='gray75', foreground="white", relief=tk.GROOVE)

    def delete_button_bg_enter(self, event):
        self.on_start_hover(event)
        Tooltip(self.delete_button, text="Delete this Node", showheader=False, offset=(22, -18), background="#feffcd",
                timeout=0.5)
        self.delete_button.config(background='gray89', foreground="white", relief=tk.GROOVE)

    def delete_button_bg_leave(self, event):
        self.delete_button.config(background='gray75', foreground="white", relief=tk.GROOVE)
