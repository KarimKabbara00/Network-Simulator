import tkinter as tk
import UI.helper_functions as hf
from UI.DeviceCLI import DeviceCli
from network.Interface_Operations.SubInterface import SubInterface
from network.Router.DHCP_Pool import DHCPpool
from operations import globalVars
import network.show_commands.RouterShowCommands as Show


class RouterCli(DeviceCli):
    def __init__(self, canvas_object, class_object, popup, cli_text, prefix, text_color, cursor_color, files):
        super().__init__(canvas_object, class_object, popup, cli_text, prefix, text_color, cursor_color, files)

    def process_command(self, command):

        valid_command = True
        globalVars.prompt_save = True

        if not command:
            self.cli.insert(tk.END, "\n" + self.cli_text)
            return

        if not self.interface_configuration and not self.sub_interface_configuration and not self.dhcp_configuration:

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
                    valid_command = False

            elif command.startswith("ip route "):

                try:
                    destination = command.split("ip route ")[1].split(" ")[0]
                    netmask = command.split("ip route ")[1].split(" ")[1]
                    next_hop_or_exit_interface = command.split("ip route ")[1].split(" ")[2]

                    if not hf.check_ipv4(destination):
                        self.cli.insert(tk.END, "\nInvalid Destination Address\n")
                        valid_command = False
                    elif not hf.check_subnet_mask(netmask):
                        self.cli.insert(tk.END, "\nInvalid Subnet Mask\n")
                        valid_command = False
                    else:
                        if '/' in next_hop_or_exit_interface:  # interface names will contain /
                            interface = self.class_object.get_interface_by_name(next_hop_or_exit_interface)
                            self.class_object.update_routing_table(interface, destination, netmask, route_type='STATIC',
                                                                   next_hop_or_exit_interface=interface.get_shortened_name())
                        else:
                            if not hf.check_ipv4(next_hop_or_exit_interface):
                                self.cli.insert(tk.END, "\nInvalid Next Hop Address\n")
                                valid_command = False
                            else:
                                interface = self.class_object.get_interface_by_next_hop(next_hop_or_exit_interface)
                                self.class_object.update_routing_table(interface, destination, netmask,
                                                                       route_type='STATIC',
                                                                       next_hop_or_exit_interface=next_hop_or_exit_interface)
                except IndexError:
                    self.cli.insert(tk.END, "\nIncomplete Command\n")
                    valid_command = False

                self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "> ")

            elif command.startswith('ip dhcp'):

                try:
                    next_command = command.split('ip dhcp ')[1]

                    if next_command.startswith('pool '):
                        try:
                            pool_name = next_command.split('pool ')[1]
                            if all(i == ' ' for i in pool_name):
                                raise IndexError
                            pool_name = pool_name.strip()  # Remove trailing and leading spaces

                            self.working_dhcp_pool = DHCPpool(self.class_object, pool_name)
                            self.class_object.get_dhcp_server().add_dhcp_pool(self.working_dhcp_pool)
                            self.dhcp_configuration = True

                            self.cli_text = self.class_object.get_host_name() + "(dhcp-config)> "
                            self.cli.insert(tk.END, "\n" + self.cli_text)

                        except IndexError:
                            self.cli.insert(tk.END, "\nIncomplete Command\n")
                            self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "> ")
                            valid_command = False

                    elif next_command.startswith('excluded-address'):
                        try:
                            excluded_ips = next_command.split('excluded-address ')[1]
                            try:
                                ip_start, ip_end = excluded_ips.split(' ')[0], excluded_ips.split(' ')[1]
                                is_range = True
                            except IndexError:
                                ip_start, ip_end = excluded_ips, None
                                is_range = False

                            if hf.check_ipv4(ip_start):
                                if not ip_end:
                                    self.class_object.get_dhcp_server().exclude_ip_range_from_dhcp_pools(ip_start,
                                                                                                         ip_end,
                                                                                                         is_range)
                                    self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "> ")
                                elif ip_end and hf.check_ipv4(ip_end):
                                    self.class_object.get_dhcp_server().exclude_ip_range_from_dhcp_pools(ip_start,
                                                                                                         ip_end,
                                                                                                         is_range)
                                    self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "> ")
                                else:
                                    self.cli.insert(tk.END, "\nInvalid IP Address(es)\n")
                                    self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "> ")
                                    valid_command = False
                            else:
                                self.cli.insert(tk.END, "\nInvalid IP Address(es)\n")
                                self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "> ")
                                valid_command = False

                        except IndexError:
                            self.cli.insert(tk.END, "\nIncomplete Command\n")
                            self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "> ")
                            valid_command = False

                except IndexError:
                    self.cli.insert(tk.END, "\nIncomplete Command\n")
                    self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "> ")
                    valid_command = False

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
                if 'dhcp' in command:
                    self.class_object.send_dhcp_discover(self.working_interface)
                    self.cli_text = self.class_object.get_host_name() + "(int-config)> "
                    self.cli.insert(tk.END, "\n" + self.cli_text)
                else:
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

            elif command.startswith('ip helper-address '):
                try:
                    destination_dhcp = command.split('ip helper-address ')[1]
                    self.class_object.set_relay_agent(True, destination_dhcp)
                except IndexError:
                    pass

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
                    valid_command = False

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
                    valid_command = False

            elif command == 'exit':
                self.sub_interface_configuration = False
                self.cli_text = self.class_object.get_host_name() + "> "
                self.cli.insert(tk.END, "\n" + self.cli_text)

            else:
                self.cli.insert(tk.END, "\nUnknown Command\n" + "\n" + self.cli_text)
                valid_command = False

        elif self.dhcp_configuration:

            if command.startswith('network'):
                try:
                    ip = command.split('network ')[1].split(' ')[0]
                    subnet_or_prefix = command.split('network ')[1].split(' ')[1]

                    if '/' in subnet_or_prefix:
                        prefix = int(subnet_or_prefix.strip('/'))
                        if not hf.check_ipv4(ip):
                            self.cli.insert(tk.END, "\nInvalid Network Address\n" + "\n" + self.cli_text)
                            valid_command = False
                        elif not hf.check_subnet_mask(hf.get_subnet_from_prefix_length(prefix)):
                            self.cli.insert(tk.END, "\nInvalid Prefix Length\n" + "\n" + self.cli_text)
                            valid_command = False
                        else:
                            self.working_dhcp_pool.set_pool(ip, prefix, is_prefix=True)
                            self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "(dhcp-config)> ")
                    else:
                        subnet = subnet_or_prefix
                        if not hf.check_ipv4(ip):
                            self.cli.insert(tk.END, "\nInvalid Network Address\n" + "\n" + self.cli_text)
                            valid_command = False
                        elif not hf.check_subnet_mask(subnet):
                            self.cli.insert(tk.END, "\nInvalid Subnet Mask\n" + "\n" + self.cli_text)
                            valid_command = False
                        else:
                            self.working_dhcp_pool.set_pool(ip, subnet, is_prefix=False)
                            self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "(dhcp-config)> ")

                except IndexError:
                    self.cli.insert(tk.END, "\nIncomplete Command\n")
                    self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "(dhcp-config)> ")
                    valid_command = False

            elif command.startswith('dns-server'):
                try:
                    dns_server = command.split('dns-server ')[1]
                    if not dns_server:
                        raise IndexError
                    if hf.check_ipv4(dns_server):
                        self.working_dhcp_pool.add_dns_server(dns_server)
                        self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "(dhcp-config)> ")
                    else:
                        self.cli.insert(tk.END, "\nInvalid IP Address\n")
                        self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "(dhcp-config)> ")
                        valid_command = False
                except IndexError:
                    self.cli.insert(tk.END, "\nIncomplete Command\n")
                    self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "(dhcp-config)> ")
                    valid_command = False

            elif command.startswith('domain-name'):
                try:
                    domain_name = command.split('domain-name ')[1]
                    if all(i == ' ' for i in domain_name) or not domain_name:
                        raise IndexError
                    domain_name = domain_name.strip()  # Remove trailing and leading spaces
                    self.working_dhcp_pool.set_domain_name(domain_name)
                    self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "(dhcp-config)> ")
                except IndexError:
                    self.cli.insert(tk.END, "\nIncomplete Command\n")
                    self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "(dhcp-config)> ")
                    valid_command = False

            elif command.startswith('default-router'):
                try:
                    default_router = command.split('default-router ')[1]
                    if not default_router:
                        raise IndexError
                    if hf.check_ipv4(default_router):
                        self.working_dhcp_pool.set_default_router(default_router)
                        self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "(dhcp-config)> ")
                    else:
                        self.cli.insert(tk.END, "\nInvalid IP Address\n")
                        self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "(dhcp-config)> ")
                        valid_command = False
                except IndexError:
                    self.cli.insert(tk.END, "\nIncomplete Command\n")
                    self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "(dhcp-config)> ")
                    valid_command = False

            elif command.startswith('lease'):
                try:
                    time = command.split('lease ')[1]
                    if not time:
                        raise IndexError

                    days = time.split(' ')[0]

                    if days == 'infinite':
                        days, hours, minutes = 0, 0, 0
                        self.working_dhcp_pool.set_lease(days, hours, minutes)
                        self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "(dhcp-config)> ")
                    elif days.isnumeric():
                        days = int(days)
                        hours, minutes = 0, 0
                        try:
                            hours = int(time.split(' ')[1])
                            try:
                                minutes = int(time.split(' ')[2])
                            except IndexError:
                                pass
                        except IndexError:
                            pass
                        self.working_dhcp_pool.set_lease(days, hours, minutes)
                        self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "(dhcp-config)> ")
                    else:
                        self.cli.insert(tk.END, "\nInvalid Lease Time\n")
                        self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "(dhcp-config)> ")
                        valid_command = False

                except IndexError:
                    self.cli.insert(tk.END, "\nIncomplete Command\n")
                    self.cli.insert(tk.END, "\n" + self.class_object.get_host_name() + "(dhcp-config)> ")
                    valid_command = False

            elif command == "exit":
                self.dhcp_configuration = False
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
