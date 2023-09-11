import tkinter as tk
import UI.helper_functions as hf
from UI.DeviceCLI import DeviceCli
from network.SubInterface import SubInterface
from operations import globalVars
import network.show_commands.RouterShowCommands as Show


class RouterCli(DeviceCli):
    def __init__(self, canvas_object, class_object,  popup, cli_text, prefix, text_color, cursor_color, files):
        super().__init__(canvas_object, class_object, popup, cli_text, prefix, text_color, cursor_color, files)

    def process_command(self, command):

        valid_command = True
        globalVars.prompt_save = True

        if not command:
            self.cli.insert(tk.END, "\n" + self.cli_text)
            valid_command = False

        if not self.interface_configuration and not self.sub_interface_configuration:

            if command == "show interfaces":
                interfaces = Show.interfaces(self.class_object.get_interfaces())
                self.cli.insert(tk.END, "\n")
                self.cli.insert(tk.END, interfaces)
                self.cli.insert(tk.END, "\n\n" + self.cli_text)

            elif command == "show routing-table":
                routes = Show.routing_table(self.class_object.get_routing_table())
                self.cli.insert(tk.END, "\n")
                self.cli.insert(tk.END, routes)
                self.cli.insert(tk.END, "\n\n" + self.cli_text)

            elif command == "show arp":
                arp_table = Show.arp_table(self.class_object.get_arp_table())
                self.cli.insert(tk.END, "\n")
                self.cli.insert(tk.END, arp_table)
                self.cli.insert(tk.END, "\n\n" + self.class_object.get_host_name() + "> ")

            elif command.startswith("interface "):

                try:
                    interface = command.split("interface ")[1].split('.')[0]
                    sub_intf = '.' + command.split("interface ")[1].split('.')[1]
                except IndexError:
                    interface = command.split("interface ")[1]
                    sub_intf = None

                self.working_interface = self.class_object.get_interface_by_name(interface)

                if self.working_interface and sub_intf:  # If true, sub interface config
                    self.sub_interface_configuration = True
                    self.working_sub_interface = SubInterface(self.working_interface, sub_intf)
                    self.working_interface.add_sub_interface(self.working_sub_interface)
                    self.cli_text = self.class_object.get_host_name() + "(sub-int-config)> "
                    self.cli.insert(tk.END, "\n" + self.cli_text)

                elif self.working_interface:
                    self.interface_configuration = True
                    self.cli_text = self.class_object.get_host_name() + "(int-config)> "
                    self.cli.insert(tk.END, "\n" + self.cli_text)

                else:
                    self.cli.insert(tk.END, "\nInterface Not Found")
                    self.cli.insert(tk.END, "\n" + self.cli_text)

            elif command == "clear":
                self.cli.delete("1.0", tk.END)
                self.cli.insert(tk.END, "Welcome\n")
                self.cli.insert(tk.END, self.cli_text)

            else:
                self.cli.insert(tk.END, "\nUnknown Command\n" + "\n" + self.cli_text)
                valid_command = False

        elif self.interface_configuration:

            if command == "shutdown":
                self.working_interface.set_administratively_down(True)
                self.cli.insert(tk.END, "\nInterface " + self.working_interface.get_shortened_name()
                                + " operational state set to false.\n")
                self.cli.insert(tk.END, "\n" + self.cli_text)

            elif command == "exit":
                self.interface_configuration = False
                self.cli_text = self.class_object.get_host_name() + "> "
                self.cli.insert(tk.END, "\n" + self.cli_text)

            elif command == "clear":
                self.cli.delete("1.0", tk.END)
                self.cli.insert(tk.END, "Welcome\n")
                self.cli.insert(tk.END, self.cli_text)

            elif command.startswith("ip address "):
                ip = command.split(" ")[-2]
                netmask = command.split(" ")[-1]

                if not hf.check_ipv4(ip):
                    self.cli.insert(tk.END, "\nInvalid IP Address\n" + "\n" + self.cli_text)
                    valid_command = False
                elif not hf.check_subnet_mask(netmask):
                    self.cli.insert(tk.END, "\nInvalid Subnet Mask\n" + "\n" + self.cli_text)
                    valid_command = False
                else:
                    self.working_interface.set_ipv4_address(ip)
                    self.working_interface.set_netmask(netmask)
                    self.cli.insert(tk.END, "\nIP Address configured for " + self.working_interface.get_shortened_name()
                                    + "\n" + self.cli_text)
                    self.class_object.update_routing_table(self.working_interface, ip, netmask)

            elif command.startswith("no "):
                next_command = command.split("no ")[1]

                if next_command == "shutdown":
                    self.working_interface.set_administratively_down(False)
                    self.cli.insert(tk.END, "\nInterface " + self.working_interface.get_shortened_name()
                                    + " operational state set to true.\n")
                    self.cli.insert(tk.END, "\n" + self.cli_text)

            elif command.startswith("interface "):
                interface = command.split("interface ")[1]
                try:
                    interface = interface.replace(" ", "")
                except IndexError:
                    pass

                self.working_interface = self.class_object.get_interface_by_name(interface)
                if self.working_interface:
                    self.interface_configuration = True
                    self.cli_text = self.class_object.get_host_name() + "(int-config)> "
                    self.cli.insert(tk.END, "\n" + self.cli_text)
                else:
                    self.cli.insert(tk.END, "\nInterface Not Found")
                    self.cli.insert(tk.END, "\n" + self.cli_text)

            else:
                self.cli.insert(tk.END, "\nUnknown Command\n" + "\n" + self.cli_text)
                valid_command = False

        elif self.sub_interface_configuration:
            if command.startswith("encapsulation dot1q "):
                info = command.split("encapsulation dot1q ")

                try:
                    try:
                        v_id = int(info[1].split(" ")[0])
                        self.working_sub_interface.set_vlan_id(v_id)

                        native_vlan = int(info[1].split(" ")[1])
                        self.working_sub_interface.set_native_vlan(native_vlan)

                    except IndexError:
                        v_id = int(info[1])
                        self.working_sub_interface.set_vlan_id(v_id)

                except ValueError:
                    self.cli.insert(tk.END, "\nInvalid Command\n" + "\n" + self.cli_text)
                    valid_command = False

                self.cli_text = self.class_object.get_host_name() + "(sub-int-config)> "
                self.cli.insert(tk.END, "\n" + self.cli_text)

            elif command.startswith("ip address "):
                ip = command.split(" ")[-2]
                netmask = command.split(" ")[-1]

                if not hf.check_ipv4(ip):
                    self.cli.insert(tk.END, "\nInvalid IP Address\n" + "\n" + self.cli_text)
                    valid_command = False
                elif not hf.check_subnet_mask(netmask):
                    self.cli.insert(tk.END, "\nInvalid Subnet Mask\n" + "\n" + self.cli_text)
                    valid_command = False
                else:
                    self.working_sub_interface.set_ipv4_address(ip)
                    self.working_sub_interface.set_netmask(netmask)
                    self.cli.insert(tk.END, "\nIP Address configured for " +
                                    self.working_sub_interface.get_shortened_name() + "\n" + self.cli_text)
                    self.class_object.update_routing_table(self.working_sub_interface, ip, netmask)

            elif command.startswith("interface "):

                try:
                    interface = command.split("interface ")[1].split('.')[0]
                    sub_intf = '.' + command.split("interface ")[1].split('.')[1]
                except IndexError:
                    interface = command.split("interface ")[1]
                    sub_intf = None

                self.working_interface = self.class_object.get_interface_by_name(interface)
                if self.working_interface and sub_intf:  # If true, sub interface config
                    self.sub_interface_configuration = True
                    self.working_sub_interface = SubInterface(self.working_interface, sub_intf)
                    self.working_interface.add_sub_interface(self.working_sub_interface)
                    self.cli_text = self.class_object.get_host_name() + "(sub-int-config)> "
                    self.cli.insert(tk.END, "\n" + self.cli_text)

                elif self.working_interface:
                    self.interface_configuration = True
                    self.cli_text = self.class_object.get_host_name() + "(int-config)> "
                    self.cli.insert(tk.END, "\n" + self.cli_text)

                else:
                    self.cli.insert(tk.END, "\nInterface Not Found")
                    self.cli.insert(tk.END, "\n" + self.cli_text)

            elif command == 'exit':
                self.sub_interface_configuration = False
                self.cli_text = self.class_object.get_host_name() + "> "
                self.cli.insert(tk.END, "\n" + self.cli_text)

            else:
                self.cli.insert(tk.END, "\nUnknown Command\n" + "\n" + self.cli_text)
                valid_command = False

        if valid_command:
            if self.command_history:
                if self.command_history[0] != command:
                    self.command_history.insert(0, command)
            else:
                self.command_history.insert(0, command)

        position = self.cli.index(tk.END)
        self.cli.mark_set("insert", position)
        self.cli.see(tk.END)
