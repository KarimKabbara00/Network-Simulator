import tkinter as tk
import helper_functions as hf
from abc import ABC, abstractmethod


class DeviceCli(ABC):

    def __init__(self, canvas_object, class_object, popup, cli_text, prefix, files):
        self.canvas_object = canvas_object
        self.class_object = class_object
        self.cli_index = None
        self.cli_command_files = files

        # CLI Stuff
        self.cli = None
        self.cli_text = prefix
        self.command_history = []
        self.command_history_index = -1
        # CLI Stuff

        # CLI initial config
        self.cli = tk.Text(popup, height=100, width=600, background="black", foreground="orange",
                           insertbackground="orange")
        self.cli.pack(padx=20, pady=10)
        self.cli.insert(tk.END, "Welcome\n")
        self.cli.insert(tk.END, cli_text)
        pos = self.cli.index(tk.END)
        self.cli.mark_set("insert", pos)
        self.cli.see(tk.END)
        # CLI initial config

        # Interface Configuration
        self.interface_configuration = False
        self.working_interface = None
        # Interface Configuration

        # Key bindings
        self.cli.bind('<BackSpace>', self.no_del_mov_illegal)
        self.cli.bind('<Left>', self.no_del_mov_illegal)
        self.cli.bind('<Return>', self.carriage_return)
        self.cli.bind('<Up>', self.command_history_up)
        self.cli.bind('<Down>', self.command_history_down)
        self.cli.bind('<question>', self.context_help)
        self.cli.bind('<Tab>', self.auto_complete)
        # Key bindings

        # plus two for ">" and " "
        self.cli_hostname_prefix_length = "+" + str(len(self.class_object.get_host_name()) + 2) + "c"

    # Disallow deleting line break
    def no_del_mov_illegal(self, event):

        # get last line
        cli_pos = float(self.cli.index('end-1c linestart')) - 1
        line = self.cli.get(cli_pos, tk.END).split('\n')[-1]

        # if more than 1 > on line, allow delete
        if line.count(">") > 1:
            return

        # else
        if self.cli.get("insert-2c") == ">" and self.cli.get("insert-1c") == " ":
            return "break"

    def carriage_return(self, event):

        # Get entered command and process
        cli_pos = float(self.cli.index('end-1c linestart')) - 1
        line = self.cli.get(cli_pos, tk.END).split('\n')[1]
        line = line[line.find('>') + 2:]

        # Remove space from end of command if it exists
        if line and line[-1] == " ":
            line = line[:-1]

        self.process_command(line)

        # Reset command history index
        self.command_history_index = -1

        return "break"

    def command_history_up(self, event):
        if self.command_history_index < len(self.command_history) - 1:
            self.command_history_index += 1
        else:
            return "break"
        self.cli.delete('current linestart' + self.cli_hostname_prefix_length, 'current lineend')
        self.cli.insert(tk.END, self.command_history[self.command_history_index])
        return "break"

    def command_history_down(self, event):
        if self.command_history_index > 0:
            self.cli.delete('current linestart' + self.cli_hostname_prefix_length, 'current lineend+1c')
            self.command_history_index -= 1
            self.cli.insert(tk.END, self.command_history[self.command_history_index])
        elif self.command_history_index == 0:
            self.command_history_index = -1
            self.cli.delete('current linestart' + self.cli_hostname_prefix_length, 'current lineend+1c')
            self.cli.insert(tk.END, "")
        return "break"

    def context_help(self, event):
        cli_pos = float(self.cli.index('end-1c linestart')) - 1
        line = self.cli.get(cli_pos, tk.END).split('\n')[1]
        line = line[line.find('>') + 2:]
        possible_commands = self.get_possible_commands(line)
        self.cli.insert(tk.END, "?")

        for i in possible_commands:
            self.cli.insert(tk.END, "\n" + i)

        self.cli.insert(tk.END, "\n" + self.cli_text)
        self.cli.insert(tk.END, line)

        position = self.cli.index(tk.END)
        self.cli.mark_set("insert", position)
        self.cli.see(tk.END)

        return "break"

    def auto_complete(self, event):
        cli_pos = float(self.cli.index('end-1c linestart')) - 1
        line = self.cli.get(cli_pos, tk.END).split('\n')[1]
        line = line[line.find('>') + 2:]
        possible_commands = self.get_possible_commands(line)

        try:
            possible_commands[0] = line + possible_commands[0].replace(line.split(" ")[-1], '')
        except IndexError:
            try:
                possible_commands[0] = line + possible_commands[0].replace(line, '')
            except IndexError:
                pass

        if len(possible_commands) == 1:
            self.cli.insert(tk.END, "\n" + self.cli_text + possible_commands[0] + " ")

        return "break"

    def get_possible_commands(self, line):
        if not self.interface_configuration:
            return hf.get_possible_commands(line, self.cli_command_files[0])
        else:
            return hf.get_possible_commands(line, self.cli_command_files[1])

    def on_closing(self):
        # Save CLI text
        return self.cli.get("2.0", "end-1c")

    @abstractmethod
    def process_command(self, command):
        raise NotImplementedError("Implement in subclass")
