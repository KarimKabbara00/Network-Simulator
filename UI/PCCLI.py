import tkinter as tk
from UI.DeviceCLI import DeviceCli
from operations import globalVars
import threading
import network.show_commands.PCShowCommands as Show
import UI.helper_functions as hf


class PCCli(DeviceCli):
    def __init__(self, canvas_object, class_object,  popup, cli_text, prefix, text_color, cursor_color, files=None):
        super().__init__(canvas_object, class_object, popup, cli_text, prefix, text_color, cursor_color, files)

    def process_command(self, command):

        valid_command = True
        globalVars.prompt_save = True

        # if command.startswith("add arp "):
        #     args = command.split('add arp ')[1]
        #     ip = args.split(' ')[0]
        #     mac = args.split(' ')[1]
        #     self.class_object.add_arp_entry(ip, mac, "STATIC")

        if not command:
            self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "> ")
            valid_command = False

        elif command == "ipconfig":
            configurations = Show.configuration(self.class_object)
            self.cli.insert(tk.END, "\n")
            self.cli.insert(tk.END, configurations)
            self.cli.insert(tk.END, "\n\n" + self.class_object.get_host_name() + "> ")

        elif command == "ipconfig /renew":
            self.class_object.renew_nic_configuration()
            self.cli.insert(tk.END, "\n\n" + self.class_object.get_host_name() + "> ")

            self.process_command("ipconfig")

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
            arp_table = Show.arp_table(self.class_object.get_arp_table())
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