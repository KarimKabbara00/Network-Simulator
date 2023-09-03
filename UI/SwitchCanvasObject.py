import tkinter
import tkinter as tk
from tkinter import messagebox, ttk
import UI.helper_functions as hf
from PCCanvasObject import PCCanvasObject
from SwitchCLI import SwitchCli
import globalVars


class SwitchCanvasObject:

    def __init__(self, canvas, block_name, icons, class_object, master):
        self._x = None
        self._y = None
        self.canvas = canvas
        self.block_name = block_name
        self.class_object = class_object
        self.class_object.set_canvas_object(self)
        self.master = master
        self.icons = icons

        # Cursor Location when object is created
        x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
        y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
        # Cursor Location when object is created

        # Icon Stuff
        self.icon = self.icons[0]
        self.terminal_icon = self.icons[1]
        self.ethernet_del_icon = self.icons[2]
        self.x_node_icon = self.icons[3]
        # Assigned to canvas_object to allow delete
        self.canvas_object = self.canvas.create_image(x, y, image=self.icon, tags=(self.block_name, "Switch"))
        self.canvas.photo = self.icon
        # Icon Stuff

        # Hover menu Stuff
        self.hover_area = self.canvas.create_polygon(x - 50, y - 35, x + 45, y - 35, x + 45, y - 55, x + 97, y - 55,
                                                     x + 97, y + 65,
                                                     x + 45, y + 65, x + 45, y + 45, x - 50, y + 45, fill="")
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
        self.cli_window = None
        self.created_terminal = False
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
                           self.canvas.canvasx(event_x) + 45, self.canvas.canvasy(event_y) - 35,
                           self.canvas.canvasx(event_x) + 45, self.canvas.canvasy(event_y) - 55,
                           self.canvas.canvasx(event_x) + 97, self.canvas.canvasy(event_y) - 55,
                           self.canvas.canvasx(event_x) + 97, self.canvas.canvasy(event_y) + 65,
                           self.canvas.canvasx(event_x) + 45, self.canvas.canvasy(event_y) + 65,
                           self.canvas.canvasx(event_x) + 45, self.canvas.canvasy(event_y) + 45,
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

        self.terminal_button.bind('<Enter>', self.terminal_button_bg_enter)
        self.terminal_button.bind('<Leave>', self.terminal_button_bg_leave)
        self.terminal_button.bind('<Button-1>', self.menu_switch_cli)

        self.disconnect_button.bind('<Enter>', self.disconnect_button_bg_enter)
        self.disconnect_button.bind('<Leave>', self.disconnect_button_bg_leave)
        self.disconnect_button.bind('<Button-1>', self.disconnect_cable)

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

    def disconnect_cable(self, main_event):

        def button_enter(event):
            button.config(background='gray89', relief=tk.SUNKEN)

        def button_leave(event):
            button.config(background='SystemButtonFace', relief=tk.GROOVE)

        def enable_button(event):
            button.config(state='normal')
            button.bind('<Enter>', button_enter)
            button.bind('<Leave>', button_leave)

        def disconnect(event):
            for selected_item in tree.selection():
                items = tree.item(selected_item)['values']
                try:
                    self.class_object.get_interface_by_name(items[0]).get_canvas_cable().delete_canvas_cable()
                    tree.delete(selected_item)
                except (tk.TclError, AttributeError):
                    pass

        popup = tk.Toplevel(self.master)
        popup.geometry("%dx%d+%d+%d" % (560, 300, 600, 300))
        popup.wm_title("Disconnect Cable")
        popup.wm_iconphoto(False, self.icons[2])
        popup.focus_set()

        frame = tk.LabelFrame(popup, padx=5, pady=5)
        frame.place(x=10, y=10, height=245, width=541)

        button = tk.Button(popup, text='Disconnect', relief=tk.GROOVE, width=76)
        button.bind('<Button-1>', disconnect)
        button.place(x=10, y=265)
        button.config(state='disabled')  # Initially, the button is disabled. It is enabled when a row is pressed.

        # Build tree
        columns = ('l_interface', 'r_hostname', 'r_interface', 'operational')
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        tree.heading('l_interface', text='Local Interface')
        tree.column("l_interface", minwidth=0, width=100)
        tree.heading('r_hostname', text='Remote Hostname')
        tree.column("r_hostname", minwidth=0, width=150)
        tree.heading('r_interface', text='Remote Interface')
        tree.column("r_interface", minwidth=0, width=150)
        tree.heading('operational', text='Status')
        tree.column("operational", minwidth=0, width=110)

        tree.bind('<<TreeviewSelect>>', enable_button)

        # Insert connected interfaces
        for i in self.class_object.get_interfaces():
            if i.get_is_connected():
                c1 = i.get_canvas_cable().get_cable_end_1().get_shortened_name()
                c2 = i.get_canvas_cable().get_cable_end_2().get_shortened_name()

                operational = 'Non-operational'
                if i.get_is_operational():
                    operational = 'Operational'

                remote_hostname = i.get_canvas_cable().get_class_object_1().get_host_name()
                if remote_hostname == self.class_object.get_host_name():
                    remote_hostname = i.get_canvas_cable().get_class_object_2().get_host_name()

                # TODO: ADD REMOTE LINK STATUS
                if c1 == i.get_shortened_name():
                    tree.insert('', tk.END, values=(c1, remote_hostname, c2, operational))
                else:
                    tree.insert('', tk.END, values=(c2, remote_hostname, c1, operational))

        tree.grid(row=0, column=0, sticky='nsew')

        # add a scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)  # was yscroll=
        scrollbar.grid(row=0, column=1, sticky='ns')

        self.hide_menu()

    def menu_delete(self, event):

        if globalVars.ask_before_delete:
            answer = messagebox.askokcancel("Delete Switch", "Delete this Switch?")
        else:
            answer = True

        if answer:
            try:
                for i in self.class_object.get_interfaces():
                    if i.get_is_connected():
                        i.get_canvas_cable().delete_canvas_cable()

            except (tk.TclError, AttributeError):
                pass

            self.canvas.delete(self.canvas_object)
            self.canvas.delete(self.hover_area)
            self.canvas.delete(self.menu_buttons)
            self.canvas.delete()
            self.class_object = None

            # In case, remove all tooltips
            [self.canvas.delete(i) for i in self.canvas.find_withtag("Terminal_Tooltip")]
            [self.canvas.delete(i) for i in self.canvas.find_withtag("Disconnect_Tooltip")]
            [self.canvas.delete(i) for i in self.canvas.find_withtag("Delete_Tooltip")]

        self.hide_menu()

    def menu_switch_cli(self, event):

        def hide_window():
            self.cli_window.withdraw()

        if not self.created_terminal:
            self.cli_window = tk.Toplevel(self.canvas)
            self.cli_window.geometry("%dx%d+%d+%d" % (700, 800, 600, 125))
            self.cli_window.wm_iconphoto(False, self.icons[1])
            self.cli_window.wm_title("Terminal")
            self.cli_window.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(self.cli_window))
            self.cli_window.protocol('WM_DELETE_WINDOW', hide_window)
            self.cli_window.focus_set()
            self.cli_object = SwitchCli(self, self.class_object, self.cli_window, self.cli_text,
                                        "Switch> ", self.cli_command_files)
            self.created_terminal = True
        else:
            self.cli_window.deiconify()

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
        return

    def terminal_button_bg_enter(self, event):
        self.on_start_hover(event)
        self.canvas.after(600, lambda c=self.canvas, b=self.terminal_button, text="Open the Terminal",
                                      tag="Terminal_Tooltip", p=(self._x + 57, self._y - 42),
                                      offset=(1, 0): hf.create_tooltip(c, b, text, tag, p, offset))
        self.terminal_button.config(background='gray89', foreground="white", relief=tk.SUNKEN)

    def terminal_button_bg_leave(self, event):
        self.terminal_button.config(background='gray75', foreground="white", relief=tk.GROOVE)
        [self.canvas.delete(i) for i in self.canvas.find_withtag("Terminal_Tooltip")]

    def disconnect_button_bg_enter(self, event):
        self.on_start_hover(event)
        self.canvas.after(600, lambda c=self.canvas, b=self.disconnect_button, text="Disconnect Connections",
                                      tag="Disconnect_Tooltip", p=(self._x + 57, self._y - 9),
                                      offset=(20, 0): hf.create_tooltip(c, b, text, tag, p, offset))
        self.disconnect_button.config(background='gray89', foreground="white", relief=tk.SUNKEN)

    def disconnect_button_bg_leave(self, event):
        self.disconnect_button.config(background='gray75', foreground="white", relief=tk.GROOVE)
        [self.canvas.delete(i) for i in self.canvas.find_withtag("Disconnect_Tooltip")]

    def delete_button_bg_enter(self, event):
        self.on_start_hover(event)
        self.canvas.after(600, lambda c=self.canvas, b=self.delete_button, text="Delete PC", tag="Delete_Tooltip",
                                      p=(self._x + 57, self._y + 24), offset=(-20, 0): hf.create_tooltip(c, b, text,
                                                                                                         tag, p,
                                                                                                         offset))
        self.delete_button.config(background='gray89', foreground="white", relief=tk.SUNKEN)

    def delete_button_bg_leave(self, event):
        self.delete_button.config(background='gray75', foreground="white", relief=tk.GROOVE)
        [self.canvas.delete(i) for i in self.canvas.find_withtag("Delete_Tooltip")]
