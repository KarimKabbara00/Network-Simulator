import tkinter as tk
from UI.DeviceCLI import DeviceCli
import network.show_commands.SwitchShowCommands as Show
from network.Switch.VLAN import VLAN
from operations import globalVars


class SwitchCli(DeviceCli):
    def __init__(self, canvas_object, class_object, popup, cli_text, prefix, text_color, cursor_color, files):
        super().__init__(canvas_object, class_object, popup, cli_text, prefix, text_color, cursor_color, files)

    def process_command(self, command):

        valid_command = True
        globalVars.prompt_save = True

        if not command:
            self.cli.insert(tk.END, "\n" + self.cli_text)
            return

        if not self.interface_configuration and not self.vlan_configuration:

            if command == "show mac-address-table":
                mac_table = Show.cam_table(self.class_object.get_cam_table())
                self.cli.insert(tk.END, "\n")
                self.cli.insert(tk.END, mac_table)
                self.cli.insert(tk.END, "\n\n" + self.cli_text)

            elif command == "show interfaces":
                interfaces = Show.interfaces(self.class_object.get_interfaces())
                self.cli.insert(tk.END, "\n")
                self.cli.insert(tk.END, interfaces)
                self.cli.insert(tk.END, "\n\n" + self.cli_text)

            elif command == "show interfaces trunk":
                trunk_interfaces = Show.interfaces_trunk(self.class_object.get_interfaces())
                self.cli.insert(tk.END, "\n")
                self.cli.insert(tk.END, trunk_interfaces)
                self.cli.insert(tk.END, "\n\n" + self.cli_text)

            elif command == "show vlans":
                vlan_information = Show.vlans(self.class_object.get_vlans())
                self.cli.insert(tk.END, "\n")
                self.cli.insert(tk.END, vlan_information)
                self.cli.insert(tk.END, "\n\n" + self.cli_text)

            elif command.startswith("interface "):
                interface = command.split("interface ")[1]
                try:
                    interface = interface.replace(" ", "")
                except IndexError:
                    pass

                self.working_interface = self.class_object.get_interface_by_name(interface)
                if self.working_interface:
                    self.interface_configuration = True
                    self.vlan_configuration = False
                    self.cli_text = self.class_object.get_host_name() + "(int-config)> "
                    self.cli.insert(tk.END, "\n" + self.cli_text)
                else:
                    self.cli.insert(tk.END, "\nInterface Not Found")
                    self.cli.insert(tk.END, "\n" + self.cli_text)

            elif command.startswith('vlan '):
                try:
                    vlan_id = int(command.split(' ')[1])
                    self.working_vlan = self.class_object.get_vlan_by_id(vlan_id)
                    if self.working_vlan:
                        self.vlan_configuration = True
                        self.interface_configuration = False
                        self.cli_text = self.class_object.get_host_name() + "(vlan-config)> "
                        self.cli.insert(tk.END, "\n" + self.cli_text)
                    else:
                        self.cli.insert(tk.END, "\nError entering VLAN configuration")
                        self.cli.insert(tk.END, "\n" + self.cli_text)

                except ValueError:
                    self.cli.insert(tk.END, "\nMust be a numbered VLAN")
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

            elif command.startswith("interface "):
                interface = command.split("interface ")[1]
                try:
                    interface = interface.replace(" ", "")
                except IndexError:
                    pass

                self.working_interface = self.class_object.get_interface_by_name(interface)
                if self.working_interface:
                    self.interface_configuration = True
                    self.vlan_configuration = False
                    self.cli_text = self.class_object.get_host_name() + "(int-config)> "
                    self.cli.insert(tk.END, "\n" + self.cli_text)
                else:
                    self.cli.insert(tk.END, "\nInterface Not Found")
                    self.cli.insert(tk.END, "\n" + self.cli_text)

            elif command.startswith("switchport"):
                next_command = command.split("switchport ")[1]
                self.cli.insert(tk.END, "\n" + self.cli_text)

                if next_command.startswith("mode "):
                    try:
                        mode = next_command.split("mode ")[1].capitalize()
                        if mode != "Access" and mode != "Trunk":
                            raise IndexError
                        self.working_interface.set_switchport_type(mode)
                    except IndexError:
                        self.cli.insert(tk.END, "\nIncomplete Command\n" + "\n" + self.cli_text)
                        valid_command = False

                elif next_command.startswith("access vlan "):
                    try:
                        vlan_id = int(next_command.split("access vlan ")[1])
                        self.working_interface.set_access_vlan_id(vlan_id)
                        self.class_object.add_vlan(VLAN(vlan_id), self.working_interface)
                    except IndexError:
                        self.cli.insert(tk.END, "\nIncomplete Command\n" + "\n" + self.cli_text)
                        valid_command = False
                    except ValueError:
                        self.cli.insert(tk.END, "\nInvalid VLAN\n" + "\n" + self.cli_text)
                        valid_command = False

                elif next_command.startswith("trunk allowed-vlans add "):
                    try:
                        vlan_ids = [int(i) for i in next_command.split("trunk allowed-vlans add ")[1].split(',')]
                        self.working_interface.add_allowed_trunk_vlan(vlan_ids)
                    except IndexError:
                        self.cli.insert(tk.END, "\nIncomplete Command\n" + "\n" + self.cli_text)
                        valid_command = False
                    except ValueError:
                        self.cli.insert(tk.END, "\nInvalid VLAN(s)\n" + "\n" + self.cli_text)
                        valid_command = False

                elif next_command.startswith("trunk allowed-vlans remove "):
                    try:
                        vlan_ids = [int(i) for i in next_command.split("trunk allowed-vlans remove ")[1].split(',')]
                        self.working_interface.remove_allowed_trunk_vlan(vlan_ids)
                    except IndexError:
                        self.cli.insert(tk.END, "\nIncomplete Command\n" + "\n" + self.cli_text)
                        valid_command = False
                    except ValueError:
                        self.cli.insert(tk.END, "\nInvalid VLAN(s)\n" + "\n" + self.cli_text)
                        valid_command = False

                elif next_command.startswith("trunk allowed-vlans "):
                    try:
                        vlan_ids = [int(i) for i in next_command.split("trunk allowed-vlans ")[1].split(',')]
                        self.working_interface.set_allowed_trunk_vlan(vlan_ids)
                    except IndexError:
                        self.cli.insert(tk.END, "\nIncomplete Command\n" + "\n" + self.cli_text)
                        valid_command = False
                    except ValueError:
                        self.cli.insert(tk.END, "\nInvalid VLAN(s)\n" + "\n" + self.cli_text)
                        valid_command = False

                elif next_command.startswith("trunk native-vlan "):
                    try:
                        vlan_id = next_command.split("trunk native-vlan ")[1]
                        self.working_interface.set_native_vlan(int(vlan_id))
                    except IndexError:
                        self.cli.insert(tk.END, "\nIncomplete Command\n" + "\n" + self.cli_text)
                        valid_command = False
                    except ValueError:
                        self.cli.insert(tk.END, "\nInvalid Native VLAN\n" + "\n" + self.cli_text)
                        valid_command = False

            elif command.startswith("no "):
                next_command = command.split("no ")[1]

                if next_command == "shutdown":
                    self.working_interface.set_administratively_down(False)
                    self.cli.insert(tk.END, "\nInterface " + self.working_interface.get_shortened_name()
                                    + " operational state set to true.\n")
                    self.cli.insert(tk.END, "\n" + self.cli_text)

            else:
                self.cli.insert(tk.END, "\nUnknown Command\n" + "\n" + self.cli_text)
                valid_command = False

        elif self.vlan_configuration:
            if command.startswith("name "):
                name = command.split("name ")[1]
                self.working_vlan.set_name(name)
                self.cli_text = self.class_object.get_host_name() + "(vlan-config)> "
                self.cli.insert(tk.END, "\n" + self.cli_text)
            elif command == 'exit':
                self.vlan_configuration = False
                self.cli_text = self.class_object.get_host_name() + "> "
                self.cli.insert(tk.END, "\n" + self.cli_text)

            elif command == "clear":
                self.cli.delete("1.0", tk.END)
                self.cli.insert(tk.END, "Welcome\n")
                self.cli.insert(tk.END, self.cli_text)

        if valid_command:
            if self.command_history:
                if self.command_history[0] != command:
                    self.command_history.insert(0, command)
            else:
                self.command_history.insert(0, command)

        position = self.cli.index(tk.END)
        self.cli.mark_set("insert", position)
        self.cli.see(tk.END)
