import tkinter
import tkinter as tk
from tkinter import ttk, messagebox
import UI.helper_functions as hf
from UI.RouterCLI import RouterCli
from operations import globalVars
from UI import PCCanvasObject


class RouterCanvasObject:
    def __init__(self, canvas, block_name, icons, class_object, master, time_class, load=False):
        self._x = None
        self._y = None
        self.canvas = canvas
        self.block_name = block_name
        self.class_object = class_object
        self.class_object.set_canvas_object(self)
        self.master = master
        self.icons = icons

        self.internal_clock = time_class
        self.internal_clock.add_router(self)
        self.class_object.set_internal_clock(self.internal_clock)

        # Cursor Location when object is created
        x = self.canvas.canvasx(self.canvas.winfo_pointerx() - self.canvas.winfo_rootx())
        y = self.canvas.canvasy(self.canvas.winfo_pointery() - self.canvas.winfo_rooty())
        # Cursor Location when object is created

        # Icon Stuff
        self.icon = self.icons[0]
        self.terminal_icon = self.icons[1]
        self.ethernet_del_icon = self.icons[2]
        self.x_node_icon = self.icons[3]
        # Assigned to canvas_object to allow delete
        self.canvas_object = self.canvas.create_image(x, y, image=self.icon, tags=(self.block_name, "Router", "Node"))
        self.canvas.photo = self.icon
        # Icon Stuff

        # Hover menu Stuff
        self.hover_area = self.canvas.create_polygon(x - 50, y - 35, x + 45, y - 35, x + 45, y - 55, x + 97, y - 55,
                                                     x + 97, y + 65,
                                                     x + 45, y + 65, x + 45, y + 45, x - 50, y + 45, fill="")

        self.menu_buttons = self.canvas.create_polygon(x + 40, y - 5, x + 50, y - 5, x + 50, y - 72, x + 92, y - 72,
                                                       x + 92, y + 72, x + 50,
                                                       y + 72, x + 50, y + 5, outline="black", fill="NavajoWhite2",
                                                       width=1)
        self.canvas.itemconfigure(self.menu_buttons, state='hidden')

        self.terminal_button = tk.Button(self.canvas, width=25, height=25, image=self.terminal_icon)
        self.disconnect_button = tk.Button(self.canvas, width=25, height=25, image=self.ethernet_del_icon)
        self.delete_button = tk.Button(self.canvas, width=25, height=25, image=self.x_node_icon)

        self.terminal_button.config(background='gray75', foreground="white", relief=tk.GROOVE)
        self.disconnect_button.config(background='gray75', foreground="white", relief=tk.GROOVE)
        self.delete_button.config(background='gray75', foreground="white", relief=tk.GROOVE)

        self.terminal_button_window = self.canvas.create_window(x + 57, y - 31, window=self.terminal_button, state='hidden')
        self.disconnect_button_window = self.canvas.create_window(x + 57, y + 3, window=self.disconnect_button, state='hidden')
        self.delete_button_window = self.canvas.create_window(x + 57, y + 37, window=self.delete_button, state='hidden')
        # Hover menu Stuff

        # Button Bindings
        if not load:
            self.canvas.tag_bind(self.block_name, '<Motion>', self.motion)  # When creating the object
            self.canvas.tag_bind(self.block_name, '<Button-1>', self.motion)  # When creating the object
        self.canvas.tag_bind(self.block_name, '<B1-Motion>', self.motion)  # When moving the object after it is created
        self.canvas.tag_bind(self.block_name, '<ButtonRelease-1>',
                             self.button_release)  # When moving the object after it is created
        # Button Bindings

        self.disconnect_menu = None

        # CLI Stuff
        self.cli_object = None
        self.cli_command_files = ["commands/ro_general_command_list", "commands/ro_interface_command_list",
                                  "commands/ro_sub_interface_command_list"]
        self.cli_text = "Router> "
        self.cli_window = None
        self.created_terminal = False
        # CLI Stuff

        # Light & Line Stuff
        self.line_connections = {}
        self.x_flag = None
        self.y_flag = None
        self.line_interface_relations = {}
        # Light & Line Stuff

    def motion(self, event=None):

        # Not event is true when the object being moved calls the other objects motion function
        if not event:
            event_x = self.canvas.coords(self.block_name)[0] + 0.000005
            event_y = self.canvas.coords(self.block_name)[1] + 0.000005
        else:
            event_x = self.canvas.canvasx(event.x)
            event_y = self.canvas.canvasy(event.y)

            # Hide the menu
            self.unbind_menu_temporarily()

        # Move the hover area and menu buttons
        self.canvas.coords(self.hover_area, event_x - 50, event_y - 35,
                           event_x + 45, event_y - 35,
                           event_x + 45, event_y - 55,
                           event_x + 97, event_y - 55,
                           event_x + 97, event_y + 65,
                           event_x + 45, event_y + 65,
                           event_x + 45, event_y + 45,
                           event_x - 50, event_y + 45)

        self.canvas.coords(self.menu_buttons, event_x + 40, event_y,
                           event_x + 50, event_y - 5,
                           event_x + 50, event_y - 50,
                           event_x + 92, event_y - 50,
                           event_x + 92, event_y + 60,
                           event_x + 50, event_y + 60,
                           event_x + 50, event_y + 5)

        # Move the object
        self.canvas.coords(self.block_name, event_x, event_y)

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

                    # /// Line Shifts and Corrections
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
                    # /// Line Shifts and Corrections

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

                            self.canvas.tag_lower(l1, i.get_obj_1().get_canvas_object())
                            self.canvas.tag_lower(l2, i.get_obj_2().get_canvas_object())
                            [self.canvas.tag_raise(self.menu_buttons, light) for light in
                             self.canvas.find_withtag('light')]

                            i.set_lights(l1, l2)

                            if ((globalVars.show_link_lights and globalVars.light_state) or
                                    (not globalVars.show_link_lights and globalVars.light_state)):
                                self.canvas.itemconfig(l1, state='normal')
                                self.canvas.itemconfig(l2, state='normal')

                            elif ((globalVars.show_link_lights and not globalVars.light_state) or
                                  (not globalVars.show_link_lights and not globalVars.light_state)):
                                self.canvas.itemconfig(l1, state='hidden')
                                self.canvas.itemconfig(l2, state='hidden')

                        if 0 <= abs(event_x - self.canvas.coords(line)[0]) <= 30 and 0 <= abs(
                                event_y - self.canvas.coords(line)[1]) <= 30:

                            self.canvas.coords(line, event_x + x_shift,
                                               event_y + y_shift,
                                               self.canvas.coords(line)[2], self.canvas.coords(line)[3])

                            if event:
                                self.canvas.itemconfig(l1, fill=hf.get_color_from_op(
                                    self.line_interface_relations[line[0]][0].get_is_operational()))
                                self.canvas.itemconfig(l2, fill=hf.get_color_from_op(
                                    self.line_interface_relations[line[0]][1].get_is_operational()))

                        elif 0 <= abs(event_x - self.canvas.coords(line)[2]) <= 30 and 0 <= abs(
                                event_y - self.canvas.coords(line)[3]) <= 30:

                            self.canvas.coords(line, self.canvas.coords(line)[0], self.canvas.coords(line)[1],
                                               event_x + x_shift,
                                               event_y + y_shift)

                            if event:
                                self.canvas.itemconfig(l2, fill=hf.get_color_from_op(
                                    self.line_interface_relations[line[0]][0].get_is_operational()))
                                self.canvas.itemconfig(l1, fill=hf.get_color_from_op(
                                    self.line_interface_relations[line[0]][1].get_is_operational()))

        except StopIteration:
            pass

        self._x = event_x
        self._y = event_y
        globalVars.prompt_save = True
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
        self.terminal_button.bind('<Button-1>', self.menu_router_cli)

        self.disconnect_button.bind('<Enter>', self.disconnect_button_bg_enter)
        self.disconnect_button.bind('<Leave>', self.disconnect_button_bg_leave)
        self.disconnect_button.bind('<Button-1>', self.disconnect_cable)

        self.delete_button.bind('<Enter>', self.delete_button_bg_enter)
        self.delete_button.bind('<Leave>', self.delete_button_bg_leave)
        self.delete_button.bind('<Button-1>', lambda e, q=False: self.menu_delete(e, q))

        if event:
            self.on_start_hover(event)

    def hide_menu(self, on_delete=False):
        self.canvas.itemconfigure(self.menu_buttons, state='hidden')

        self.canvas.itemconfigure(self.terminal_button_window, state='hidden')
        self.canvas.itemconfigure(self.disconnect_button_window, state='hidden')
        self.canvas.itemconfigure(self.delete_button_window, state='hidden')

        if on_delete:
            self.terminal_button.destroy()
            self.disconnect_button.destroy()
            self.delete_button.destroy()

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

        self.disconnect_menu = tk.Toplevel(self.master)

        x = (globalVars.screen_width / 2) - (672 / 2)
        y = (globalVars.screen_height / 2) - (300 / 2) - 100
        self.disconnect_menu.geometry("%dx%d+%d+%d" % (672, 300, x, y))

        self.disconnect_menu.wm_title("Disconnect Cable")
        self.disconnect_menu.wm_iconphoto(False, self.icons[2])
        self.disconnect_menu.focus_set()
        self.disconnect_menu.resizable(False, False)

        frame = tk.LabelFrame(self.disconnect_menu, padx=5, pady=5)
        frame.place(x=10, y=10, height=245, width=653)

        button = tk.Button(self.disconnect_menu, text='Disconnect', relief=tk.GROOVE, width=92)
        button.bind('<Button-1>', disconnect)
        button.place(x=10, y=265)
        button.config(state='disabled')  # Initially, the button is disabled. It is enabled when a row is pressed.

        # Build tree
        columns = ('l_interface', 'l_status', 'r_hostname', 'r_interface', 'r_status')
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        tree.heading('l_interface', text='Local Interface')
        tree.column("l_interface", minwidth=0, width=100)
        tree.heading('l_status', text='Local Status')
        tree.column("l_status", minwidth=0, width=110)
        tree.heading('r_hostname', text='Remote Hostname')
        tree.column("r_hostname", minwidth=0, width=150)
        tree.heading('r_interface', text='Remote Interface')
        tree.column("r_interface", minwidth=0, width=150)
        tree.heading('r_status', text='Remote Status')
        tree.column("r_status", minwidth=0, width=110)

        tree.bind('<<TreeviewSelect>>', enable_button)

        # Insert connected interfaces
        for i in self.class_object.get_interfaces():
            if i.get_is_connected():
                c1 = i.get_canvas_cable().get_cable_end_1().get_shortened_name()
                c2 = i.get_canvas_cable().get_cable_end_2().get_shortened_name()

                remote_hostname = i.get_canvas_cable().get_class_object_1().get_host_name()
                remote_status = i.get_canvas_cable().get_cable_end_1().get_is_operational()
                if remote_hostname == self.class_object.get_host_name():
                    remote_hostname = i.get_canvas_cable().get_class_object_2().get_host_name()
                    remote_status = i.get_canvas_cable().get_cable_end_2().get_is_operational()

                local_status = 'Non-operational'
                if i.get_is_operational():
                    local_status = 'Operational'

                if remote_status:
                    remote_status = 'Operational'
                else:
                    remote_status = 'Non-operational'

                if c1 == i.get_shortened_name():
                    tree.insert('', tk.END, values=(c1, local_status, remote_hostname, c2, remote_status))
                else:
                    tree.insert('', tk.END, values=(c2, local_status, remote_hostname, c1, remote_status))

        tree.grid(row=0, column=0, sticky='nsew')

        # add a scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)  # was yscroll=
        scrollbar.grid(row=0, column=1, sticky='ns')

        self.hide_menu()
        globalVars.prompt_save = True

    def menu_delete(self, event, is_quick_del, reset=False):

        if ((not is_quick_del and globalVars.ask_before_delete) or (is_quick_del and globalVars.ask_before_quick_delete)
                and not reset):
            answer = messagebox.askokcancel("Delete Router", "Delete this Router?")
        else:
            answer = True

        if answer:
            try:
                for i in self.class_object.get_interfaces():
                    if i.get_is_connected():
                        i.get_canvas_cable().delete_canvas_cable()

            except (tk.TclError, AttributeError):
                pass

            self.internal_clock.remove_router(self)

            if not is_quick_del:
                globalVars.ro_objects.remove(self)
                globalVars.objects.remove(self)

            self.canvas.delete(self.canvas_object)
            self.canvas.delete(self.hover_area)
            self.canvas.delete(self.menu_buttons)

            self.class_object = None

            # Destroy windows when deleting node
            if self.cli_window:
                self.cli_window.destroy()

            if self.disconnect_menu:
                self.disconnect_menu.destroy()

            # In case, remove all tooltips
            [self.canvas.delete(i) for i in self.canvas.find_withtag("Terminal_Tooltip")]
            [self.canvas.delete(i) for i in self.canvas.find_withtag("Disconnect_Tooltip")]
            [self.canvas.delete(i) for i in self.canvas.find_withtag("Delete_Tooltip")]

            self.hide_menu(on_delete=True)
        else:
            self.hide_menu()
        globalVars.prompt_save = True

    def menu_router_cli(self, main_event):
        def hide_window():
            self.cli_window.withdraw()

        if not self.created_terminal:
            self.cli_window = tk.Toplevel(self.canvas)

            x = (globalVars.screen_width / 2) - (700 / 2)
            y = (globalVars.screen_height / 2) - (800 / 2) - 50
            self.cli_window.geometry("%dx%d+%d+%d" % (700, 800, x, y))

            self.cli_window.wm_iconphoto(False, self.icons[1])
            self.cli_window.wm_title("Terminal")
            self.cli_window.protocol('WM_DELETE_WINDOW', hide_window)
            self.cli_window.focus_set()
            self.cli_object = RouterCli(self, self.class_object, self.cli_window, self.cli_text, "Router> ",
                                        'orange', 'orange', self.cli_command_files)
            self.created_terminal = True
        else:
            self.cli_window.deiconify()

        self.hide_menu()

    def get_block_name(self):
        return self.block_name

    def get_class_object(self):
        return self.class_object

    def get_canvas_object(self):
        return self.canvas_object

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

        for item in globalVars.objects:
            item.hide_menu()

        try:
            if type(self.master.focus_displayof()) == tkinter.Tk:  # If the root has focus
                self.canvas.itemconfigure(self.menu_buttons, state='normal')  # Add the frame to the canvas

                self.canvas.itemconfigure(self.terminal_button_window, state='normal')
                self.canvas.moveto(self.terminal_button_window, self._x + 57, self._y - 42)

                self.canvas.itemconfigure(self.disconnect_button_window, state='normal')
                self.canvas.moveto(self.disconnect_button_window, self._x + 57, self._y - 9)

                self.canvas.itemconfigure(self.delete_button_window, state='normal')
                self.canvas.moveto(self.delete_button_window, self._x + 57, self._y + 24)

                self.terminal_button.place()
                self.disconnect_button.place()
                self.delete_button.place()

                return
        except tkinter.TclError:
            pass

        self.master.update()  # Program hangs without calling update

    def on_end_hover(self, event):
        self.terminal_button.place_forget()
        self.disconnect_button.place_forget()
        self.delete_button.place_forget()

        self.canvas.itemconfigure(self.menu_buttons, state='hidden')
        self.canvas.itemconfigure(self.terminal_button_window, state='hidden')
        self.canvas.itemconfigure(self.disconnect_button_window, state='hidden')
        self.canvas.itemconfigure(self.delete_button_window, state='hidden')

        self.master.update()  # Program hangs without calling update
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

    # -------------------------- Save & Load Methods -------------------------- #
    def get_save_info(self):
        return [self._x, self._y, self.block_name, self.cli_text, self.class_object.get_save_info()]

    def set_pos(self, x_pos, y_pos):
        self._x = x_pos
        self._y = y_pos
        self.canvas.coords(self.canvas_object, x_pos, y_pos)

        # Move the hover area and menu buttons
        self.canvas.coords(self.hover_area, self._x - 50, self._y - 35,
                           self._x + 45, self._y - 35,
                           self._x + 45, self._y - 55,
                           self._x + 97, self._y - 55,
                           self._x + 97, self._y + 65,
                           self._x + 45, self._y + 65,
                           self._x + 45, self._y + 45,
                           self._x - 50, self._y + 45)

        self.canvas.coords(self.menu_buttons, self._x + 40, self._y,
                           self._x + 50, self._y - 5,
                           self._x + 50, self._y - 50,
                           self._x + 92, self._y - 50,
                           self._x + 92, self._y + 60,
                           self._x + 50, self._y + 60,
                           self._x + 50, self._y + 5)

        self.button_release(None)

    def get_coords(self):
        return [self._x, self._y]
    # -------------------------- Save & Load Methods -------------------------- #
