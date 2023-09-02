import threading
import tkinter
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk
from tkinter import messagebox
from UI import helper_functions as hf
from ttkwidgets.frames import Tooltip


class PCCanvasObject(object):
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
        self.config_icon = self.icons[1]
        self.terminal_icon = self.icons[2]
        self.ethernet_del_icon = self.icons[3]
        self.x_node_icon = self.icons[4]

        # Assigned to canvas_object to allow to delete
        self.canvas_object = self.canvas.create_image(x, y, image=self.icon, tags=(self.block_name, "PC"))
        self.canvas.photo = self.icon
        # Icon Stuff

        # Hover menu Stuff
        self.hover_area = self.canvas.create_polygon(x - 50, y - 50, x + 50, y - 50, x + 50, y - 75, x + 90, y - 75,
                                                     x + 90, y + 65, x + 50, y + 65, x + 50, y + 50, x - 50, y + 50,
                                                     fill="")
        self.canvas.lower(self.hover_area)
        self.menu_buttons = self.canvas.create_polygon(x + 40, y - 5, x + 50, y - 5, x + 50, y - 72, x + 92, y - 72,
                                                       x + 92, y + 72, x + 50,
                                                       y + 72, x + 50, y + 5, outline="black", fill="navajo white",
                                                       width=1)
        self.canvas.itemconfigure(self.menu_buttons, state='hidden')

        self.config_button = tk.Button(self.canvas, width=25, height=25, image=self.config_icon)
        self.terminal_button = tk.Button(self.canvas, width=25, height=25, image=self.terminal_icon)
        self.disconnect_button = tk.Button(self.canvas, width=25, height=25, image=self.ethernet_del_icon)
        self.delete_button = tk.Button(self.canvas, width=25, height=25, image=self.x_node_icon)

        self.config_button.config(background='gray75', foreground="white", relief=tk.GROOVE)
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
        self.cli = None
        self.cli_busy = False
        self.cli_text = "PC> "
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

    def motion(self, event):

        # Hide the menu
        self.unbind_menu_temporarily()

        # Move the object
        self.canvas.coords(self.block_name, self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

        # Move the hover area and menu buttons
        self.canvas.coords(self.hover_area, self.canvas.canvasx(event.x) - 50, self.canvas.canvasy(event.y) - 50,
                           self.canvas.canvasx(event.x) + 50, self.canvas.canvasy(event.y) - 50,
                           self.canvas.canvasx(event.x) + 50, self.canvas.canvasy(event.y) - 75,
                           self.canvas.canvasx(event.x) + 90, self.canvas.canvasy(event.y) - 75,
                           self.canvas.canvasx(event.x) + 90, self.canvas.canvasy(event.y) + 65,
                           self.canvas.canvasx(event.x) + 50, self.canvas.canvasy(event.y) + 65,
                           self.canvas.canvasx(event.x) + 50, self.canvas.canvasy(event.y) + 50,
                           self.canvas.canvasx(event.x) - 50, self.canvas.canvasy(event.y) + 50)

        self.canvas.coords(self.menu_buttons, self.canvas.canvasx(event.x) + 40, self.canvas.canvasy(event.y),
                           self.canvas.canvasx(event.x) + 50, self.canvas.canvasy(event.y) - 5,
                           self.canvas.canvasx(event.x) + 50, self.canvas.canvasy(event.y) - 72,
                           self.canvas.canvasx(event.x) + 92, self.canvas.canvasy(event.y) - 72,
                           self.canvas.canvasx(event.x) + 92, self.canvas.canvasy(event.y) + 72,
                           self.canvas.canvasx(event.x) + 50, self.canvas.canvasy(event.y) + 72,
                           self.canvas.canvasx(event.x) + 50, self.canvas.canvasy(event.y) + 5)

        # Move the Label
        self.canvas.coords(self.block_name + "_tag", self.canvas.canvasx(event.x), self.canvas.canvasy(event.y) + 60)

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

                self.canvas.tag_lower(self.l1)
                self.canvas.tag_lower(self.l2)
                self.canvas.tag_lower(line)

                if 0 <= abs(self.canvas.canvasx(event.x) - self.canvas.coords(line)[0]) <= 30 and 0 <= abs(
                        self.canvas.canvasy(event.y) - self.canvas.coords(line)[1]) <= 30:
                    self.canvas.coords(line, self.canvas.canvasx(event.x), self.canvas.canvasy(event.y),
                                       self.canvas.coords(line)[2], self.canvas.coords(line)[3])

                    self.canvas.itemconfig(self.l1, fill=hf.get_color_from_op(self.interface_1.get_is_operational()))
                    self.canvas.itemconfig(self.l2, fill=hf.get_color_from_op(self.interface_2.get_is_operational()))

                elif 0 <= abs(self.canvas.canvasx(event.x) - self.canvas.coords(line)[2]) <= 30 and 0 <= abs(
                        self.canvas.canvasy(event.y) - self.canvas.coords(line)[3]) <= 30:
                    self.canvas.coords(line, self.canvas.coords(line)[0], self.canvas.coords(line)[1],
                                       self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

                    self.canvas.itemconfig(self.l2, fill=hf.get_color_from_op(self.interface_1.get_is_operational()))
                    self.canvas.itemconfig(self.l1, fill=hf.get_color_from_op(self.interface_2.get_is_operational()))

        except StopIteration:
            pass

        self._x = event.x
        self._y = event.y
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
        self.delete_button.bind('<Button-1>', self.menu_delete)

        self.on_start_hover(event)

    def hide_menu(self):
        self.canvas.itemconfigure(self.menu_buttons, state='hidden')
        self.config_button.place_forget()
        self.terminal_button.place_forget()
        self.disconnect_button.place_forget()
        self.delete_button.place_forget()

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

        popup = tk.Toplevel(self.canvas)
        popup.geometry("%dx%d+%d+%d" % (700, 350, 600, 200))

        popup.wm_iconphoto(False, self.icons[1])
        popup.wm_title("Configure PC")

        configure_menu = ttk.Notebook(popup)
        general_tab = ttk.Frame(configure_menu)
        interface_tab = ttk.Frame(configure_menu)

        configure_menu.add(general_tab, text='General Configuration')
        configure_menu.add(interface_tab, text='Interface Configuration')
        configure_menu.pack(expand=1, fill="both")

        # General Tab
        tk.Label(general_tab, text="Hostname:").place(x=50, y=75)
        hostname = tk.Entry(general_tab, width=20)
        hostname.insert(0, self.class_object.get_host_name())
        hostname.place(x=150, y=75)

        tk.Label(general_tab, text="MAC Address:").place(x=50, y=150)
        mac_address = tk.Entry(general_tab, width=20)
        mac_address.insert(0, self.class_object.get_mac_address())
        mac_address.place(x=150, y=150)
        # General Tab

        # Interface Tab
        tk.Label(interface_tab, text="IPv4 Address:").place(x=50, y=75)
        ipv4 = tk.Entry(interface_tab, width=20)
        ipv4.insert(0, self.class_object.get_ipv4_address())
        ipv4.place(x=150, y=75)

        tk.Label(interface_tab, text="Subnet Mask:").place(x=325, y=75)
        netmask = tk.Entry(interface_tab, width=20)
        netmask.insert(0, self.class_object.get_netmask())
        netmask.place(x=415, y=75)

        tk.Label(interface_tab, text="IPv6 Address:").place(x=50, y=150)
        ipv6 = tk.Entry(interface_tab, width=20)
        ipv6.insert(0, self.class_object.get_ipv6_address())
        ipv6.place(x=150, y=150)

        tk.Label(interface_tab, text="/").place(x=275, y=150)
        prefix = tk.Entry(interface_tab, width=3)
        prefix.insert(0, self.class_object.get_prefix())
        prefix.place(x=290, y=150)

        tk.Label(interface_tab, text="Default Gateway:").place(x=50, y=225)
        gateway = tk.Entry(interface_tab, width=20)
        gateway.insert(0, self.class_object.get_default_gateway())
        gateway.place(x=150, y=225)
        # Interface Tab

        # Save Button
        tk.Button(configure_menu, width=10, height=1, text="Save",
                  command=lambda: self.save_general_parameters(hostname.get(), mac_address.get(), ipv4.get(),
                                                               netmask.get(),
                                                               ipv6.get(), prefix.get(), gateway.get(), popup)).place(
            x=590, y=300)
        # Save Button

        popup.focus_set()
        self.hide_menu()

    def disconnect_cable(self, event):
        try:
            self.class_object.get_interfaces()[0].get_canvas_cable().delete_canvas_cable()
        except (tk.TclError, AttributeError):
            pass

        self.hide_menu()

        # Disable the hover area when disconnect cable is clicked because mouse lands on the hover area causing the menu
        # to reappear instantly. It is re-enabled in self.on_end_hover()
        self.canvas.itemconfigure(self.hover_area, state="hidden")

    def menu_delete(self, event):

        answer = messagebox.askokcancel("Delete PC", "Delete this PC?")
        if answer:
            self.hide_menu()
            self.disconnect_cable(event)
            self.canvas.delete(self.canvas_object)
            self.canvas.delete(self.hover_area)
            self.canvas.delete(self.menu_buttons)
            self.canvas.delete()
            self.class_object = None
        self.hide_menu()

    def save_general_parameters(self, hostname, mac_address, ipv4, netmask, ipv6, prefix, default_route, parent):

        hostname_flag = True
        ipv4_flag = True
        ipv6_flag = True
        netmask_flag = True
        default_route_flag = True

        if not hostname:
            hostname_flag = False

        # check mac address
        mac_address_flag = hf.check_mac_address(mac_address)

        # check ipv4 address
        if ipv4:  # Check if ipv4 address is provided, since it is optional
            ipv4_flag = hf.check_ipv4(ipv4)
            netmask_flag = hf.check_subnet_mask(netmask)  # Changed here if valid subnet

        if default_route:
            default_route_flag = hf.check_ipv4(default_route)

        # TODO Implement IPv6 Checking

        if hostname_flag and mac_address_flag and ipv4_flag and ipv6_flag and netmask_flag and default_route_flag:
            self.class_object.set_host_name(hostname)
            self.class_object.set_mac_address(mac_address)
            self.class_object.set_ipv4_address(ipv4)
            self.class_object.set_netmask(netmask)
            self.class_object.set_ipv6_address(ipv6)
            self.class_object.set_prefix(prefix)
            self.class_object.set_default_gateway(default_route)
            parent.destroy()
        else:
            if not hostname_flag:
                messagebox.showerror('Invalid Parameter', 'Please Enter a Hostname', parent=parent)
            elif not mac_address_flag:
                messagebox.showerror('Invalid Parameter', 'Please Enter a valid MAC Address', parent=parent)
            elif not ipv4_flag:
                messagebox.showerror('Invalid Parameter', 'Please Enter a valid IPv4 Address', parent=parent)
            elif not ipv6_flag:
                messagebox.showerror('Invalid Parameter', 'Please Enter a valid IPv6 Address', parent=parent)
            elif not netmask_flag:
                messagebox.showerror('Invalid Parameter', 'Please Enter a valid Subnet Mask', parent=parent)
            elif not default_route_flag:
                messagebox.showerror('Invalid Parameter', 'Please Enter a valid Default Gateway', parent=parent)

    def menu_pc_cli(self, main_event):

        # plus two for ">" and " "
        cli_hostname_prefix_length = "+" + str(len(self.class_object.get_host_name()) + 2) + "c"

        # Disallow deleting line break
        def no_del_mov_illegal(event):

            # get last line
            cli_pos = float(self.cli.index('end-1c linestart')) - 1
            line = self.cli.get(cli_pos, tk.END).split('\n')[-1]

            # if more than 1 > on line, allow delete
            if line.count(">") > 1:
                return

            # else
            if self.cli.get("insert-2c") == ">" and self.cli.get("insert-1c") == " ":
                return "break"

        def carriage_return(event):

            # Get entered command and process
            cli_pos = float(self.cli.index('end-1c linestart')) - 1
            line = self.cli.get(cli_pos, tk.END).split('\n')[1]
            line = line[line.find('>') + 2:]
            self.process_command(line)

            # Reset command history index
            self.command_history_index = -1

            return "break"

        def command_history_up(event):
            if self.command_history_index < len(self.command_history) - 1:
                self.command_history_index += 1
            else:
                return "break"
            self.cli.delete('current linestart' + cli_hostname_prefix_length, 'current lineend')
            self.cli.insert(tk.END, self.command_history[self.command_history_index])
            return "break"

        def command_history_down(event):
            if self.command_history_index > 0:
                self.cli.delete('current linestart' + cli_hostname_prefix_length, 'current lineend+1c')
                self.command_history_index -= 1
                self.cli.insert(tk.END, self.command_history[self.command_history_index])
            elif self.command_history_index == 0:
                self.command_history_index = -1
                self.cli.delete('current linestart' + cli_hostname_prefix_length, 'current lineend+1c')
                self.cli.insert(tk.END, "")
            return "break"

        # Parent widget
        popup = tk.Toplevel(self.canvas)
        popup.geometry("%dx%d+%d+%d" % (700, 800, 600, 125))
        popup.protocol("WM_DELETE_WINDOW", lambda: self.on_closing(popup))
        popup.wm_iconphoto(False, self.icons[2])
        popup.wm_title("Terminal")
        popup.focus_set()


        # Parent widget

        # CLI initial config
        self.cli = tk.Text(popup, height=100, width=600, background="black", foreground="white",
                           insertbackground="white")
        self.cli.pack(padx=20, pady=10)
        self.cli.insert(tk.END, "Welcome\n")
        self.cli.insert(tk.END, self.cli_text)
        pos = self.cli.index(tk.END)
        self.cli.mark_set("insert", pos)
        self.cli.see(tk.END)
        # CLI initial config

        # Key bindings
        self.cli.bind('<BackSpace>', no_del_mov_illegal)
        self.cli.bind('<Left>', no_del_mov_illegal)
        self.cli.bind('<Return>', carriage_return)
        self.cli.bind('<Up>', command_history_up)
        self.cli.bind('<Down>', command_history_down)
        # Key bindings

        self.hide_menu()

    def process_command(self, command):

        valid_command = True

        if command.startswith("add arp "):
            args = command.split('add arp ')[1]
            ip = args.split(' ')[0]
            mac = args.split(' ')[1]
            self.class_object.add_arp_entry(ip, mac, "STATIC")

        if not command:
            self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "> ")
            valid_command = False

        elif command == "ipconfig":
            configurations = self.class_object.get_configurations()
            self.cli.insert(tk.END, "\n")
            for i in configurations:
                output = "\n" + i + "   " + configurations[i]
                self.cli.insert(tk.END, output)
            self.cli.insert(tk.END, "\n\n" + self.class_object.get_host_name() + "> ")

        elif command.startswith("ping"):
            args = command.split("ping ")[1]

            count = 4
            if "-n " in args:
                ip_address = args.split(" -n ")[0]
                count = int(args.split(" -n ")[1])
            else:
                ip_address = args

            is_valid = hf.check_ipv4(ip_address)
            if is_valid:
                self.cli.insert(tk.END, "\n\n")
                self.cli.insert(tk.END,
                                "Sending " + str(count) + " pings to " + ip_address + " with 32 bytes of data:\n")
                threading.Thread(target=self.class_object.icmp_echo_request, args=(ip_address, count)).start()
            else:
                self.cli.insert(tk.END, "\n")
                self.cli.insert(tk.END, "Unknown Command")
                self.cli.insert(tk.END, "\n\n" + self.class_object.get_host_name() + "> ")

        elif command == "arp -a":
            arp_table = self.class_object.get_arp_table()
            self.cli.insert(tk.END, "\n")
            self.cli.insert(tk.END, arp_table)
            self.cli.insert(tk.END, "\n\n" + self.class_object.get_host_name() + "> ")

        elif command == "cls":
            self.cli.delete("1.0", tk.END)
            self.cli.insert(tk.END, self.class_object.get_host_name() + "> ")

        else:
            self.cli.insert(tk.END, "\nUnknown Command\n" + "\n" + self.class_object.get_host_name() + "> ")
            valid_command = False

        if valid_command:
            if self.command_history:
                if self.command_history[0] != command:
                    self.command_history.insert(0, command)
            else:
                self.command_history.insert(0, command)

        pos = self.cli.index(tk.END)
        self.cli.mark_set("insert", pos)
        self.cli.see(tk.END)

    def get_class_object(self):
        return self.class_object

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

    def on_closing(self, popup):
        # Save CLI text
        self.cli_text = self.cli.get("2.0", "end-1c")
        popup.destroy()

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
        if type(self.master.focus_displayof()) == tkinter.Tk:  # If the root has focus
            self.canvas.itemconfigure(self.menu_buttons, state='normal')  # Add the frame to the canvas
            self.config_button.place(x=self._x + 57, y=self._y - 65)
            self.terminal_button.place(x=self._x + 57, y=self._y - 31)
            self.disconnect_button.place(x=self._x + 57, y=self._y + 3)
            self.delete_button.place(x=self._x + 57, y=self._y + 37)
        return

    def on_end_hover(self, event):
        self.canvas.itemconfigure(self.menu_buttons, state='hidden')
        self.config_button.place_forget()
        self.terminal_button.place_forget()
        self.disconnect_button.place_forget()
        self.delete_button.place_forget()

        # The hover area is disabled when a cable is disconnected because the mouse will land in the hove area and
        # make the menu reappear instantly. This line re-enables it.
        self.canvas.itemconfigure(self.hover_area, state="normal")
        return

    def get_lights(self, ignored):
        return self.l1, self.l2

    def config_button_bg_enter(self, event):
        self.on_start_hover(event)
        Tooltip(self.config_button, text="Configure this PC", showheader=False, offset=(22, -18), background="#feffcd",
                timeout=0.5)
        self.config_button.config(background='gray89', foreground="white", relief=tk.SUNKEN)

    def config_button_bg_leave(self, event):
        self.config_button.config(background='gray75', foreground="white", relief=tk.GROOVE)

    def terminal_button_bg_enter(self, event):
        self.on_start_hover(event)
        Tooltip(self.terminal_button, text="Open the Terminal", showheader=False, offset=(22, -18), background="#feffcd"
                , timeout=0.5)
        self.terminal_button.config(background='gray89', foreground="white", relief=tk.SUNKEN)

    def terminal_button_bg_leave(self, event):
        self.terminal_button.config(background='gray75', foreground="white", relief=tk.GROOVE)

    def disconnect_button_bg_enter(self, event):
        self.on_start_hover(event)
        Tooltip(self.disconnect_button, text="Disconnect Connection", showheader=False, offset=(22, -18),
                background="#feffcd", timeout=0.5)
        self.disconnect_button.config(background='gray89', foreground="white", relief=tk.SUNKEN)

    def disconnect_button_bg_leave(self, event):
        self.disconnect_button.config(background='gray75', foreground="white", relief=tk.GROOVE)

    def delete_button_bg_enter(self, event):
        self.on_start_hover(event)
        Tooltip(self.delete_button, text="Delete this Node", showheader=False, offset=(22, -18), background="#feffcd",
                timeout=0.5)
        self.delete_button.config(background='gray89', foreground="white", relief=tk.SUNKEN)

    def delete_button_bg_leave(self, event):
        self.delete_button.config(background='gray75', foreground="white", relief=tk.GROOVE)
