import tkinter
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from UI import helper_functions as hf
from operations import globalVars
from UI.PCCLI import PCCli


class PCCanvasObject(object):
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
        self.internal_clock.add_pc(self)
        self.class_object.set_internal_clock(self.internal_clock)

        # Cursor Location when object is created
        x = self.canvas.canvasx(self.canvas.winfo_pointerx() - self.canvas.winfo_rootx())
        y = self.canvas.canvasy(self.canvas.winfo_pointery() - self.canvas.winfo_rooty())
        # Cursor Location when object is created

        # Icon Stuff
        self.icon = self.icons[0]
        self.config_icon = self.icons[1]
        self.terminal_icon = self.icons[2]
        self.ethernet_del_icon = self.icons[3]
        self.x_node_icon = self.icons[4]

        # Assigned to canvas_object to allow to delete
        self.canvas_object = self.canvas.create_image(x, y, image=self.icon, tags=(self.block_name, "PC", "Node"))
        self.canvas.photo = self.icon
        # Icon Stuff

        # Hover menu Stuff
        self.hover_area = self.canvas.create_polygon(x - 50, y - 50, x + 45, y - 50, x + 45, y - 75, x + 95, y - 75,
                                                     x + 95, y + 75, x + 45, y + 75, x + 45, y + 50, x - 50, y + 50,
                                                     fill="")

        self.menu_buttons = self.canvas.create_polygon(x + 40, y + 0, x + 50, y - 5, x + 50, y - 72, x + 92, y - 72,
                                                       x + 92, y + 72, x + 50, y + 72, x + 50, y + 5,
                                                       outline="black", fill="NavajoWhite2", width=1,
                                                       tags=('Hover_Menus', ))

        self.canvas.itemconfigure(self.menu_buttons, state='hidden')

        self.config_button = tk.Button(self.canvas, width=25, height=25, image=self.config_icon)
        self.terminal_button = tk.Button(self.canvas, width=25, height=25, image=self.terminal_icon)
        self.disconnect_button = tk.Button(self.canvas, width=25, height=25, image=self.ethernet_del_icon)
        self.delete_button = tk.Button(self.canvas, width=25, height=25, image=self.x_node_icon)

        self.config_button.config(background='gray75', foreground="white", relief=tk.GROOVE)
        self.terminal_button.config(background='gray75', foreground="white", relief=tk.GROOVE)
        self.disconnect_button.config(background='gray75', foreground="white", relief=tk.GROOVE)
        self.delete_button.config(background='gray75', foreground="white", relief=tk.GROOVE)

        self.config_button_window = self.canvas.create_window(x + 57, y - 65, window=self.config_button, state='hidden', tag="Menu_Button")
        self.terminal_button_window = self.canvas.create_window(x + 57, y - 31, window=self.terminal_button, state='hidden', tag="Menu_Button")
        self.disconnect_button_window = self.canvas.create_window(x + 57, y + 3, window=self.disconnect_button, state='hidden', tag="Menu_Button")
        self.delete_button_window = self.canvas.create_window(x + 57, y + 37, window=self.delete_button, state='hidden', tag="Menu_Button")
        # Hover menu Stuff

        # Button Bindings
        if not load:
            self.canvas.tag_bind(self.block_name, '<Motion>', self.motion)  # When creating the object
            self.canvas.tag_bind(self.block_name, '<Button-1>', self.motion)  # When creating the object
        self.canvas.tag_bind(self.block_name, '<B1-Motion>', self.motion)  # When moving the object after it is created
        self.canvas.tag_bind(self.block_name, '<ButtonRelease-1>',
                             self.button_release)  # When moving the object after it is created
        # Button Bindings

        # Config Window Stuff
        self.config_window = None
        self.ipv4_field = None          # To set focus
        self.hostname_field = None      # To set focus
        self.gateway_field = None
        self.prefix_field = None
        self.ipv6_field = None
        self.ipv6_link_local_field = None
        self.ipv6_link_local_prefix_field = None
        self.netmask_field = None
        self.auto_config_nic = tk.BooleanVar()     # DHCP
        # Config Window Stuff

        # CLI Stuff
        self.cli_window = None
        self.cli = None
        self.cli_object = None
        self.cli_busy = False
        self.cli_text = "PC> "
        self.created_terminal = False
        self.command_history = []
        self.command_history_index = -1
        # CLI Stuff

        # Light Stuff
        self.line_connections = {}
        self.tag_1 = ""
        self.tag_2 = ""
        self.interface_1 = None
        self.interface_2 = None
        self.l1 = None
        self.l2 = None
        # Light Stuff

    def motion(self, event=None):

        if not event:
            event_x = self.canvas.coords(self.block_name)[0] + 0.000005
            event_y = self.canvas.coords(self.block_name)[1] + 0.000005

        else:
            event_x = self.canvas.canvasx(event.x)
            event_y = self.canvas.canvasy(event.y)

            # Hide the menu
            self.unbind_menu_temporarily()

        # Move the object
        self.canvas.coords(self.block_name, event_x, event_y)

        # Move the hover area and menu buttons
        self.canvas.coords(self.hover_area, event_x - 50, event_y - 50,
                           event_x + 45, event_y - 50,
                           event_x + 45, event_y - 75,
                           event_x + 95, event_y - 75,
                           event_x + 95, event_y + 75,
                           event_x + 45, event_y + 75,
                           event_x + 45, event_y + 50,
                           event_x - 50, event_y + 50)

        self.canvas.coords(self.menu_buttons, event_x + 40, event_y,
                           event_x + 50, event_y - 5,
                           event_x + 50, event_y - 72,
                           event_x + 92, event_y - 72,
                           event_x + 92, event_y + 72,
                           event_x + 50, event_y + 72,
                           event_x + 50, event_y + 5)


        try:
            line = self.canvas.find_withtag(self.tag_1 + "_line_" + self.tag_2 + "_0")

            light_1 = self.canvas.find_withtag(self.tag_1 + "_light_" + self.tag_2 + "_0")
            light_2 = self.canvas.find_withtag(self.tag_2 + "_light_" + self.tag_1 + "_0")

            if line:
                self.canvas.delete(light_1)
                self.l1 = hf.draw_circle(self.canvas.coords(line)[0], self.canvas.coords(line)[1],
                                         self.canvas.coords(line)[2],
                                         self.canvas.coords(line)[3], 4, self.canvas,
                                         self.tag_1 + "_light_" + self.tag_2 + "_0")
                self.canvas.delete(light_2)
                self.l2 = hf.draw_circle(self.canvas.coords(line)[2], self.canvas.coords(line)[3],
                                         self.canvas.coords(line)[0],
                                         self.canvas.coords(line)[1], 4, self.canvas,
                                         self.tag_2 + "_light_" + self.tag_1 + "_0")

                self.canvas.tag_lower(self.l1, list(self.line_connections.keys())[0].get_obj_1().get_canvas_object())
                self.canvas.tag_lower(self.l2, list(self.line_connections.keys())[0].get_obj_2().get_canvas_object())
                [self.canvas.tag_raise(self.menu_buttons, light) for light in self.canvas.find_withtag('light')]

                if ((globalVars.show_link_lights and globalVars.light_state) or
                        (not globalVars.show_link_lights and globalVars.light_state)):
                    self.canvas.itemconfig(self.l1, state='normal')
                    self.canvas.itemconfig(self.l2, state='normal')

                elif ((globalVars.show_link_lights and not globalVars.light_state) or
                      (not globalVars.show_link_lights and not globalVars.light_state)):
                    self.canvas.itemconfig(self.l1, state='hidden')
                    self.canvas.itemconfig(self.l2, state='hidden')

                if 0 <= abs(event_x - self.canvas.coords(line)[0]) <= 30 and 0 <= abs(
                        event_y - self.canvas.coords(line)[1]) <= 30:
                    self.canvas.coords(line, event_x, event_y,
                                       self.canvas.coords(line)[2], self.canvas.coords(line)[3])

                    self.canvas.itemconfig(self.l1, fill=hf.get_color_from_op(self.interface_1.get_is_operational()))
                    self.canvas.itemconfig(self.l2, fill=hf.get_color_from_op(self.interface_2.get_is_operational()))

                elif 0 <= abs(event_x - self.canvas.coords(line)[2]) <= 30 and 0 <= abs(
                        event_y - self.canvas.coords(line)[3]) <= 30:
                    self.canvas.coords(line, self.canvas.coords(line)[0], self.canvas.coords(line)[1],
                                       event_x, event_y)

                    self.canvas.itemconfig(self.l2, fill=hf.get_color_from_op(self.interface_1.get_is_operational()))
                    self.canvas.itemconfig(self.l1, fill=hf.get_color_from_op(self.interface_2.get_is_operational()))

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

        self.config_button.bind('<Enter>', self.config_button_bg_enter)
        self.config_button.bind('<Leave>', self.config_button_bg_leave)
        self.config_button.bind('<Button-1>', self.open_config_menu)

        self.terminal_button.bind('<Enter>', self.terminal_button_bg_enter)
        self.terminal_button.bind('<Leave>', self.terminal_button_bg_leave)
        self.terminal_button.bind('<Button-1>', self.menu_pc_cli)

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

        self.canvas.itemconfigure(self.config_button_window, state='hidden')
        self.canvas.itemconfigure(self.terminal_button_window, state='hidden')
        self.canvas.itemconfigure(self.disconnect_button_window, state='hidden')
        self.canvas.itemconfigure(self.delete_button_window, state='hidden')

        self.config_button.place_forget()
        self.terminal_button.place_forget()
        self.disconnect_button.place_forget()
        self.delete_button.place_forget()

        if on_delete:
            self.config_button.destroy()
            self.terminal_button.destroy()
            self.disconnect_button.destroy()
            self.delete_button.destroy()

    def unbind_menu_temporarily(self):
        self.canvas.tag_unbind(self.hover_area, '<Enter>')
        self.canvas.tag_unbind(self.hover_area, '<Leave>')
        self.canvas.tag_unbind(self.block_name, '<Enter>')
        self.canvas.tag_unbind(self.block_name, '<Leave>')
        self.canvas.tag_unbind(self.menu_buttons, '<Enter>')
        self.canvas.tag_unbind(self.menu_buttons, '<Leave>')
        self.config_button.unbind('<Enter>')
        self.terminal_button.unbind('<Enter>')
        self.disconnect_button.unbind('<Enter>')
        self.delete_button.unbind('<Enter>')
        # Hide menu
        self.hide_menu()

    def open_config_menu(self, event):

        def hide_window():
            self.config_window.withdraw()

        self.config_window = tk.Toplevel(self.canvas)
        self.config_window.protocol('WM_DELETE_WINDOW', hide_window)

        x = (globalVars.screen_width / 2) - (700 / 2)
        y = (globalVars.screen_height / 2) - (375 / 2) - 100
        self.config_window.geometry('%dx%d+%d+%d' % (700, 375, x, y))

        self.config_window.wm_iconphoto(False, self.icons[1])
        self.config_window.wm_title("Configure PC")
        self.config_window.resizable(False, False)

        configure_menu = ttk.Notebook(self.config_window)

        general_tab = ttk.Frame(configure_menu)
        interface_tab = ttk.Frame(configure_menu)
        configure_menu.bind("<<NotebookTabChanged>>", lambda e=event: self.set_focus_on_tab_change(e))

        configure_menu.add(general_tab, text='General Configuration')
        configure_menu.add(interface_tab, text='Interface Configuration')
        configure_menu.pack(expand=1, fill="both")

        # General Tab
        tk.Label(general_tab, text="Hostname:").place(x=50, y=75)
        self.hostname_field = tk.Entry(general_tab, width=20)
        self.hostname_field.insert(0, self.class_object.get_host_name())
        self.hostname_field.place(x=150, y=75)

        tk.Label(general_tab, text="MAC Address:").place(x=50, y=150)
        mac_address = tk.Entry(general_tab, width=20)
        mac_address.insert(0, self.class_object.get_mac_address())
        mac_address.place(x=150, y=150)
        # General Tab

        # Interface Tab
        ask_b4_quick_del_check = tk.Checkbutton(interface_tab, text='Auto-configure interface settings '
                                                                    '(Requires a DHCP server)',
                                                variable=self.auto_config_nic, onvalue=True, offvalue=False,
                                                command=self.set_auto_configure)
        ask_b4_quick_del_check.place(x=50, y=25)

        tk.Label(interface_tab, text="IPv4 Address:").place(x=50, y=75)
        self.ipv4_field = tk.Entry(interface_tab, width=20)
        self.ipv4_field.insert(0, self.class_object.get_ipv4_address())
        self.ipv4_field.place(x=150, y=75)

        tk.Label(interface_tab, text="Subnet Mask:").place(x=335, y=75)
        self.netmask_field = tk.Entry(interface_tab, width=20)
        self.netmask_field.insert(0, self.class_object.get_netmask())
        self.netmask_field.place(x=435, y=75)

        tk.Label(interface_tab, text="Default Gateway:").place(x=50, y=125)
        self.gateway_field = tk.Entry(interface_tab, width=20)
        self.gateway_field.insert(0, self.class_object.get_default_gateway())
        self.gateway_field.place(x=150, y=125)

        tk.Label(interface_tab, text="IPv6 Address:").place(x=50, y=175)
        self.ipv6_field = tk.Entry(interface_tab, width=54)
        self.ipv6_field.insert(0, self.class_object.get_ipv6_address())
        self.ipv6_field.place(x=53, y=195)

        tk.Label(interface_tab, text="/").place(x=380, y=195)
        self.prefix_field = tk.Entry(interface_tab, width=3)
        self.prefix_field.insert(0, self.class_object.get_prefix())
        self.prefix_field.place(x=390, y=195)

        tk.Label(interface_tab, text="IPv6 Link Local Address:").place(x=50, y=245)
        self.ipv6_link_local_field = tk.Entry(interface_tab, width=54)
        self.ipv6_link_local_field.insert(0, self.class_object.get_ipv6_link_local_address())
        self.ipv6_link_local_field.place(x=53, y=265)

        tk.Label(interface_tab, text="/").place(x=380, y=265)
        self.ipv6_link_local_prefix_field = tk.Entry(interface_tab, width=3)
        self.ipv6_link_local_prefix_field.insert(0, self.class_object.get_link_local_prefix())
        self.ipv6_link_local_prefix_field.place(x=390, y=265)
        # Interface Tab

        # Save Button
        save_btn = tk.Button(configure_menu, width=10, height=1, text="Save", relief=tk.GROOVE,
                             command=lambda: self.save_general_parameters(self.hostname_field.get(), mac_address.get(),
                                                                          self.ipv4_field.get(),
                                                                          self.netmask_field.get(),
                                                                          self.gateway_field.get(),
                                                                          self.ipv6_field.get(),
                                                                          self.prefix_field.get(),
                                                                          self.ipv6_link_local_field.get(),
                                                                          self.ipv6_link_local_prefix_field.get(),
                                                                          self.config_window))
        save_btn.place(x=590, y=325)
        save_btn.bind('<Enter>', lambda e, btn=save_btn: hf.button_enter(e, btn))
        save_btn.bind('<Leave>', lambda e, btn=save_btn: hf.button_leave(e, btn))
        # Save Button

        self.toggle_config_fields()
        self.hide_menu()

    def set_auto_configure(self):
        self.class_object.set_auto_configure(self.auto_config_nic.get())
        self.toggle_config_fields()

    def set_fields_from_dhcp(self, ipv4_address, netmask, default_gateway):

        if not ipv4_address:
            ipv4_address = ''
        if not netmask:
            netmask = ''
        if not default_gateway:
            default_gateway = ''

        try:
            # Empty fields
            self.ipv4_field.delete('0', tk.END)
            self.netmask_field.delete('0', tk.END)
            self.gateway_field.delete('0', tk.END)

            self.ipv4_field.insert(tk.END, ipv4_address)
            self.netmask_field.insert(tk.END, netmask)
            self.gateway_field.insert(tk.END, default_gateway)
        except (AttributeError, tk.TclError):
            pass

    def toggle_config_fields(self):
        if self.auto_config_nic.get():
            self.ipv4_field.config(state= "disabled")
            self.netmask_field.config(state= "disabled")
            self.gateway_field.config(state= "disabled")
            # self.ipv6_field.config(state= "disabled")
            # self.prefix_field.config(state= "disabled")
        else:
            self.ipv4_field.config(state="normal")
            self.netmask_field.config(state="normal")
            self.gateway_field.config(state="normal")
            # self.ipv6_field.config(state="normal")
            # self.prefix_field.config(state="normal")

    def set_focus_on_tab_change(self, event):
        if event.widget.select() == '.!canvas.!toplevel.!notebook.!frame':
            self.hostname_field.focus_set()
        else:
            self.ipv4_field.focus_set()

    def disconnect_cable(self, event):
        try:
            cable = self.class_object.get_interfaces()[0].get_canvas_cable()
            cable.delete_canvas_cable()
        except (tk.TclError, AttributeError):
            pass

        self.hide_menu()
        globalVars.prompt_save = True

        # Disable the hover area when disconnect cable is clicked because mouse lands on the hover area causing the menu
        # to reappear instantly. It is re-enabled in self.on_end_hover()
        self.canvas.itemconfigure(self.hover_area, state="hidden")

    def menu_delete(self, event, is_quick_del, reset=False):

        if ((not is_quick_del and globalVars.ask_before_delete) or (is_quick_del and globalVars.ask_before_quick_delete)
                and not reset):
            answer = messagebox.askokcancel("Delete PC", "Delete this PC?")
        else:
            answer = True

        if answer:

            self.disconnect_cable(event)
            self.internal_clock.remove_pc(self)

            if not is_quick_del:
                globalVars.pc_objects.remove(self)
                globalVars.objects.remove(self)

            self.canvas.delete(self.canvas_object)
            self.canvas.delete(self.hover_area)
            self.canvas.delete(self.menu_buttons)

            self.class_object = None

            # Destroy windows when deleting node
            if self.cli_window:
                self.cli_window.destroy()

            if self.config_window:
                self.config_window.destroy()

            # In case, remove all tooltips
            [self.canvas.delete(i) for i in self.canvas.find_withtag("Config_Tooltip")]
            [self.canvas.delete(i) for i in self.canvas.find_withtag("Terminal_Tooltip")]
            [self.canvas.delete(i) for i in self.canvas.find_withtag("Disconnect_Tooltip")]
            [self.canvas.delete(i) for i in self.canvas.find_withtag("Delete_Tooltip")]

            self.hide_menu(on_delete=True)
        else:
            self.hide_menu()

        globalVars.prompt_save = True

    def save_general_parameters(self, hostname, mac_address, ipv4, netmask, default_route, ipv6, ipv6_prefix,
                                ipv6_ll, ipv6_ll_prefix, parent):

        hostname_flag = True
        ipv4_flag = True
        netmask_flag = True
        default_route_flag = True
        ipv6_flag = True
        ipv6_prefix_flag = True
        ipv6_ll_flag = True
        ipv6_ll_prefix_flag = True

        # must have a hostname
        if not hostname:
            hostname_flag = False

        # check mac address
        mac_address_flag = hf.check_mac_address(mac_address)

        # following fields are optional
        if ipv4:
            ipv4_flag = hf.check_ipv4(ipv4)
            netmask_flag = hf.check_subnet_mask(netmask)

        if default_route:
            default_route_flag = hf.check_ipv4(default_route)

        if ipv6:
            ipv6_flag = hf.check_ipv6(ipv6)
            ipv6_prefix_flag = hf.check_ipv6_prefix(ipv6_prefix)

        if ipv6_ll:
            ipv6_ll_flag = hf.check_ipv6(ipv6_ll)
            ipv6_ll_prefix_flag = hf.check_ipv6_prefix(ipv6_ll_prefix)

        if (hostname_flag and mac_address_flag and ipv4_flag and ipv6_flag and netmask_flag and default_route_flag and
                ipv6_flag and ipv6_prefix_flag and ipv6_ll_flag and ipv6_ll_prefix_flag):
            self.class_object.set_host_name(hostname)
            self.class_object.set_mac_address(mac_address)
            self.class_object.set_ipv4_address(ipv4)
            self.class_object.set_netmask(netmask)
            self.class_object.set_ipv6_address(ipv6)
            self.class_object.set_prefix(ipv6_prefix)
            self.class_object.set_default_gateway(default_route)
            self.class_object.set_ipv6_link_local_address(ipv6_ll)
            self.class_object.set_ipv6_link_local_prefix(ipv6_ll_prefix)
            parent.withdraw()
            globalVars.prompt_save = True
        else:
            if not hostname_flag:
                messagebox.showerror('Invalid Parameter', 'Please Enter a Hostname', parent=parent)
            elif not mac_address_flag:
                messagebox.showerror('Invalid Parameter', 'Please Enter a valid MAC Address', parent=parent)
            elif not ipv4_flag:
                messagebox.showerror('Invalid Parameter', 'Please Enter a valid IPv4 Address', parent=parent)
            elif not netmask_flag:
                messagebox.showerror('Invalid Parameter', 'Please Enter a valid Subnet Mask', parent=parent)
            elif not default_route_flag:
                messagebox.showerror('Invalid Parameter', 'Please Enter a valid Default Gateway', parent=parent)
            elif not ipv6_flag:
                messagebox.showerror('Invalid Parameter', 'Please Enter a valid IPv6 Address', parent=parent)
            elif not ipv6_prefix_flag:
                messagebox.showerror('Invalid Parameter', 'Please Enter a valid IPv6 Prefix', parent=parent)
            elif not ipv6_ll_flag:
                messagebox.showerror('Invalid Parameter', 'Please Enter a valid IPv6 Link Local Address', parent=parent)
            elif not ipv6_ll_prefix_flag:
                messagebox.showerror('Invalid Parameter', 'Please Enter a valid IPv6 Link Local Prefix', parent=parent)

    def menu_pc_cli(self, main_event):

        def hide_window():
            self.cli_window.withdraw()

        if not self.created_terminal:
            self.cli_window = tk.Toplevel(self.canvas)

            x = (globalVars.screen_width / 2) - (700 / 2)
            y = (globalVars.screen_height / 2) - (800 / 2) - 50
            self.cli_window.geometry("%dx%d+%d+%d" % (700, 800, x, y))

            self.cli_window.wm_iconphoto(False, self.icons[2])
            self.cli_window.wm_title("Terminal")
            self.cli_window.protocol('WM_DELETE_WINDOW', hide_window)
            self.cli_window.focus_set()
            self.cli_object = PCCli(self, self.class_object, self.cli_window, self.cli_text, "PC> ", 'white', 'white')
            self.cli = self.cli_object.get_cli()

            self.created_terminal = True
        else:
            self.cli_window.deiconify()

        self.hide_menu()

    def get_class_object(self):
        return self.class_object

    def get_canvas_object(self):
        return self.canvas_object

    def get_block_name(self):
        return self.block_name

    def get_info(self, info, linebreak, last):
        if linebreak:
            self.cli.insert(tk.END, info)
            self.cli.insert(tk.END, "\n")
        else:
            self.cli.insert(tk.END, info)

    def toggle_cli_busy(self):
        if not self.cli_busy:
            self.cli_busy = True
            self.cli.bind("<Key>", lambda e: "break")
        else:
            self.cli_busy = False
            self.cli.unbind("<Key>")
            self.cli.insert(tk.END, "\n\n" + self.class_object.get_host_name() + "> ")

    def add_line_connection(self, tag1, tag2, ignored_1, ignored_2, canvas_cable_object):
        self.line_connections[canvas_cable_object] = [tag1, tag2]
        self.tag_1 = tag1
        self.tag_2 = tag2

    def del_line_connection(self, cable):
        self.line_connections.pop(cable)

    def get_line_connection_count(self, ignored_1, ignored_2):
        if len(self.line_connections) > 0:
            return len(self.line_connections), self.line_connections
        else:
            return 0, None

    def set_interfaces(self, ignored, int1, int2):
        self.interface_1 = int1
        self.interface_2 = int2

    def on_start_hover(self, event):

        for item in globalVars.objects:
            item.hide_menu()

        try:
            if type(self.master.focus_displayof()) == tkinter.Tk:  # If the root has focus
                self.canvas.itemconfigure(self.menu_buttons, state='normal')  # Add the frame to the canvas

                self.canvas.itemconfigure(self.config_button_window, state='normal')
                self.canvas.moveto(self.config_button_window, self._x + 57, self._y - 65)

                self.canvas.itemconfigure(self.terminal_button_window, state='normal')
                self.canvas.moveto(self.terminal_button_window, self._x + 57, self._y - 31)

                self.canvas.itemconfigure(self.disconnect_button_window, state='normal')
                self.canvas.moveto(self.disconnect_button_window, self._x + 57, self._y + 3)

                self.canvas.itemconfigure(self.delete_button_window, state='normal')
                self.canvas.moveto(self.delete_button_window, self._x + 57, self._y + 37)

                self.config_button.place()
                self.terminal_button.place()
                self.disconnect_button.place()
                self.delete_button.place()

                return
        except tkinter.TclError:
            pass

        self.master.update()  # Program hangs without calling update


    def on_end_hover(self, event):
        self.config_button.place_forget()
        self.terminal_button.place_forget()
        self.disconnect_button.place_forget()
        self.delete_button.place_forget()

        self.canvas.itemconfigure(self.menu_buttons, state='hidden')
        self.canvas.itemconfigure(self.config_button_window, state='hidden')
        self.canvas.itemconfigure(self.terminal_button_window, state='hidden')
        self.canvas.itemconfigure(self.disconnect_button_window, state='hidden')
        self.canvas.itemconfigure(self.delete_button_window, state='hidden')

        # The hover area is disabled when a cable is disconnected because the mouse will land in the hove area and
        # make the menu reappear instantly. This line re-enables it.
        self.canvas.itemconfigure(self.hover_area, state="normal")

        self.master.update()  # Program hangs without calling update

        return

    def get_lights(self, ignored):
        return self.l1, self.l2

    def config_button_bg_enter(self, event):

        self.on_start_hover(event)
        self.canvas.after(600, lambda c=self.canvas, b=self.config_button, text="Configure this PC",
                                      tag="Config_Tooltip",
                                      p=(self._x + 57, self._y - 65): hf.create_tooltip(c, b, text, tag, p))
        self.config_button.config(background='gray89', foreground="white", relief=tk.SUNKEN)

    def config_button_bg_leave(self, event):
        self.config_button.config(background='gray75', foreground="white", relief=tk.GROOVE)
        [self.canvas.delete(i) for i in self.canvas.find_withtag("Config_Tooltip")]

    def terminal_button_bg_enter(self, event):
        self.on_start_hover(event)
        self.canvas.after(600, lambda c=self.canvas, b=self.terminal_button, text="Open the Terminal",
                                      tag="Terminal_Tooltip", p=(self._x + 57, self._y - 31),
                                      offset=(1, 0): hf.create_tooltip(c, b, text, tag, p, offset))
        self.terminal_button.config(background='gray89', foreground="white", relief=tk.SUNKEN)

    def terminal_button_bg_leave(self, event):
        self.terminal_button.config(background='gray75', foreground="white", relief=tk.GROOVE)
        [self.canvas.delete(i) for i in self.canvas.find_withtag("Terminal_Tooltip")]

    def disconnect_button_bg_enter(self, event):
        self.on_start_hover(event)
        self.canvas.after(600, lambda c=self.canvas, b=self.disconnect_button, text="Disconnect Connections",
                                      tag="Disconnect_Tooltip", p=(self._x + 57, self._y + 3),
                                      offset=(20, 0): hf.create_tooltip(c, b, text, tag, p, offset))
        self.disconnect_button.config(background='gray89', foreground="white", relief=tk.SUNKEN)

    def disconnect_button_bg_leave(self, event):
        self.disconnect_button.config(background='gray75', foreground="white", relief=tk.GROOVE)
        [self.canvas.delete(i) for i in self.canvas.find_withtag("Disconnect_Tooltip")]

    def delete_button_bg_enter(self, event):
        self.on_start_hover(event)
        self.canvas.after(600, lambda c=self.canvas, b=self.delete_button, text="Delete PC", tag="Delete_Tooltip",
                                      p=(self._x + 57, self._y + 37), offset=(-20, 0): hf.create_tooltip(c, b, text,
                                                                                                         tag, p,
                                                                                                         offset))
        self.delete_button.config(background='gray89', foreground="white", relief=tk.SUNKEN)

    def delete_button_bg_leave(self, event):
        self.delete_button.config(background='gray75', foreground="white", relief=tk.GROOVE)
        [self.canvas.delete(i) for i in self.canvas.find_withtag("Delete_Tooltip")]

    # -------------------------- Save & Load Methods -------------------------- #
    def get_save_info(self):
        return [self._x, self._y, self.block_name, self.cli_text, self.command_history, self.command_history_index,
                self.tag_1, self.tag_2, self.l1, self.l2, self.class_object.get_save_info()]

    def set_pos(self, x_pos, y_pos):
        self._x = x_pos
        self._y = y_pos
        self.canvas.coords(self.canvas_object, x_pos, y_pos)

        # Move the hover area and menu buttons
        self.canvas.coords(self.hover_area, self._x - 50, self._y - 50,
                           self._x + 45, self._y - 50,
                           self._x + 45, self._y - 75,
                           self._x + 95, self._y - 75,
                           self._x + 95, self._y + 75,
                           self._x + 45, self._y + 75,
                           self._x + 45, self._y + 50,
                           self._x - 50, self._y + 50)

        self.canvas.coords(self.menu_buttons, self._x + 40, self._y,
                           self._x + 50, self._y - 5,
                           self._x + 50, self._y - 72,
                           self._x + 92, self._y - 72,
                           self._x + 92, self._y + 72,
                           self._x + 50, self._y + 72,
                           self._x + 50, self._y + 5)

        self.button_release(None)

    def get_coords(self):
        return [self._x, self._y]
    # -------------------------- Save & Load Methods -------------------------- #
