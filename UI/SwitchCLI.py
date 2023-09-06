import tkinter as tk
from DeviceCLI import DeviceCli


class SwitchCli(DeviceCli):
    def __init__(self, canvas_object, class_object,  popup, cli_text, prefix, files):
        super().__init__(canvas_object, class_object, popup, cli_text, prefix, files)

    def process_command(self, command):

        valid_command = True

        if not command:
            self.cli.insert(tk.END, "\n" + self.cli_text)
            return

        if not self.interface_configuration:

            if command == "show mac-address-table":
                mac_table = self.class_object.show_cam_table()
                self.cli.insert(tk.END, "\n")
                self.cli.insert(tk.END, mac_table)
                self.cli.insert(tk.END, "\n\n" + self.cli_text)

            elif command == "show interfaces":
                interfaces = self.class_object.show_interfaces()
                self.cli.insert(tk.END, "\n")
                self.cli.insert(tk.END, interfaces)
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

            elif command.startswith("switchport"):
                command = command.split("switchport ")[1]
                self.cli.insert(tk.END, "\n" + self.cli_text)

                if command.startswith("mode "):
                    try:
                        mode = command.split("mode ")[1].capitalize()
                        if mode != "Access" and mode != "Trunk":
                            raise IndexError
                        self.working_interface.set_switchport_type(mode)
                    except IndexError:
                        self.cli.insert(tk.END, "\nIncomplete Command\n" + "\n" + self.cli_text)
                        valid_command = False

                elif command.startswith("access vlan "):
                    try:
                        vlan_id = int(command.split("access vlan ")[1])
                        self.working_interface.set_access_vlan_id(vlan_id)
                    except IndexError:
                        self.cli.insert(tk.END, "\nIncomplete Command\n" + "\n" + self.cli_text)
                        valid_command = False

                elif command.startswith("trunk allowed-vlans "):
                    try:
                        vlan_id = int(command.split("trunk allowed-vlans ")[1])
                        print(vlan_id)
                        self.working_interface.add_allowed_trunk_vlan(vlan_id)
                    except IndexError:
                        self.cli.insert(tk.END, "\nIncomplete Command\n" + "\n" + self.cli_text)
                        valid_command = False

            elif command.startswith("no "):
                command = command.split("no ")[1]

                if command == "shutdown":
                    self.working_interface.set_administratively_down(False)
                    self.cli.insert(tk.END, "\nInterface " + self.working_interface.get_shortened_name()
                                    + " operational state set to true.\n")
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
