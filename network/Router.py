import UI.helper_functions as hf
import network.network_functions as nf
from network.Physical_Interface import PhysicalInterface
from network.Dot1q import Dot1q


class Router:
    def __init__(self, host_name="Router", load=False):
        self.MAC_Address = hf.generate_mac_address()
        self.Model_Number = "R94X"
        self.Host_Name = host_name

        self.interfaces = []
        self.serial_interfaces = []
        if not load:
            self.serial_interfaces = []
            self.interfaces = self.set_interfaces()

        self.routing_table = {}
        self.ARP_table = {}

        self.canvas_object = None
        self.internal_clock = None

    def set_interfaces(self):
        interfaces = []
        for i in range(8):
            intf = PhysicalInterface('0/' + str(i), 1000, self)
            intf.set_administratively_down(True)
            interfaces.append(intf)
        for i in range(3):
            intf = PhysicalInterface('0/' + str(i), 1000, self)
            intf.set_administratively_down(True)
            self.serial_interfaces.append(intf)
        return interfaces

    def set_mac_address(self, address):
        self.MAC_Address = address

    def de_encapsulate(self, frame, receiving_interface):

        packet = frame.get_packet()
        packet_identifier = packet.get_identifier()
        forwarding_interface = self.decide_route(packet)

        original_sender_ipv4 = packet.get_src_ip()
        original_sender_mac = hf.bin_to_hex(frame.get_src_mac())

        original_dest_ipv4 = packet.get_dest_ip()

        # TODO: CLEAN!!!!!!!!!
        # Adjust for sub-interfaces
        dot1q_header = None
        if not receiving_interface.get_netmask():
            for x in receiving_interface.get_sub_interfaces():
                if hf.is_same_subnet(x.get_ipv4_address(), x.get_netmask(), original_sender_ipv4):
                    receiving_interface = x
                    if frame.get_dot1q():  # Check if the frame had a dot1q header
                        if packet_identifier == 'ipv4':
                            dot1q_header = Dot1q(forwarding_interface.get_vlan_id())
                        elif packet_identifier == 'ARP':
                            dot1q_header = Dot1q(receiving_interface.get_vlan_id())

        # Check if the dest is in the router's ARP table
        if original_dest_ipv4 not in self.ARP_table:
            self.arp_request(original_dest_ipv4, forwarding_interface, dot1q_header)

        # TODO: MAKE THIS CLEANER: nf.process_request(packet_identifier, packet, ...)
        # Do not route ARP
        # If an ARP packet, use receiving interface to reply so that ARP isn't routed.
        if packet_identifier == "ARP":

            if packet.get_operation_id() == 0x001:
                # If destined to me, reply with the receiving interface to the sender

                if original_dest_ipv4 == receiving_interface.get_ipv4_address():
                    self.arp_reply(receiving_interface, receiving_interface.get_ipv4_address(), original_sender_mac,
                                   original_sender_ipv4, dot1q_header)

                # If destined to someone on another subnet
                elif not hf.is_same_subnet(receiving_interface.get_ipv4_address(), receiving_interface.get_netmask(),
                                           original_dest_ipv4):

                    print('ROUTER', receiving_interface, receiving_interface.get_ipv4_address(), original_sender_mac,
                          original_sender_ipv4, original_dest_ipv4, dot1q_header.get_VID())
                    print()

                    # If not in ARP table, but in routing table (forwarding interface not None), send an ARP request
                    # to discover the original intended destination
                    if original_dest_ipv4 not in self.ARP_table and forwarding_interface:
                        self.arp_request(original_dest_ipv4, forwarding_interface, dot1q_header)

                    # TODO: This is needed, and mostly works. Sender does not create an ARP entry but receiver does????
                    # If in ARP table, send a reply to the original sender
                    if original_dest_ipv4 in self.ARP_table:
                        self.arp_reply(receiving_interface, original_dest_ipv4, original_sender_mac,
                                       original_sender_ipv4, dot1q_header)

                self.add_arp_entry(original_sender_ipv4, original_sender_mac, "DYNAMIC")

            elif packet.get_operation_id() == 0x002:
                self.add_arp_entry(original_sender_ipv4, original_sender_mac, "DYNAMIC")

        elif packet_identifier == "ipv4":

            segment = packet.get_segment()
            segment_identifier = segment.get_segment_identifier()

            if segment_identifier == "ICMP ECHO REQUEST":
                if original_dest_ipv4 == forwarding_interface.get_ipv4_address():  # Is this ICMP destined to me?
                    self.icmp_echo_reply(original_sender_ipv4, forwarding_interface, dot1q_header)
                else:  # If not
                    if original_dest_ipv4 in self.ARP_table:  # Does ARP table have a record
                        frame = nf.create_ethernet_frame(self.ARP_table[original_dest_ipv4][0], self.MAC_Address,
                                                         dot1q_header, packet, None)
                        forwarding_interface.send(frame)
                    else:  # If not, send one
                        self.arp_request(original_dest_ipv4, forwarding_interface, dot1q_header)

            elif segment_identifier == "ICMP ECHO REPLY":
                if original_dest_ipv4 == forwarding_interface.get_ipv4_address():
                    pass  # destined to me
                else:
                    # If routing an ICMP reply, the request must have gone through, therefore ARP entry exists already
                    frame = nf.create_ethernet_frame(self.ARP_table[original_dest_ipv4][0], self.MAC_Address,
                                                     dot1q_header, packet, None)
                    forwarding_interface.send(frame)

    def icmp_echo_reply(self, original_sender_ipv4, interface, dot1q=None):
        if original_sender_ipv4 not in self.ARP_table:
            self.arp_request(original_sender_ipv4, interface, dot1q)
        frame = nf.icmp_echo_reply(self.MAC_Address, interface.get_ipv4_address(), original_sender_ipv4, self.ARP_table,
                                   dot1q)
        interface.send(frame)

    def arp_request(self, dst_ipv4_address, forwarding_interface, dot1q=None):
        arp_frame = nf.create_arp_request(self.MAC_Address, forwarding_interface.get_ipv4_address(), dst_ipv4_address,
                                          dot1q)
        forwarding_interface.send(arp_frame)

    def arp_reply(self, forwarding_interface, fwd_int_ip, dest_mac, dest_ip, dot1q=None):
        frame = nf.create_arp_reply(self.MAC_Address, fwd_int_ip, dest_mac, dest_ip, dot1q)
        forwarding_interface.send(frame)

    def show_interfaces(self):
        header = "{:<16} {:<15} {:<15} {:<15}".format('Interface', 'IP Address', 'Connected', 'Operational')
        header += '\n------------------------------------------------------------\n'
        entries = ''
        for interface in self.interfaces:
            int_co = "False"
            int_op = "False"
            if interface.get_is_connected():
                int_co = "True"
            if interface.get_is_operational():
                int_op = "True"

            entries += "{:<16} {:<15} {:<15} {:<15}".format(interface.get_shortened_name(),
                                                            interface.get_ipv4_address(), int_co, int_op) + '\n'

            for sub_intf in interface.get_sub_interfaces():
                entries += '--> ' + ("{:<12} {:<15}".format(sub_intf.get_shortened_name(),
                                                            sub_intf.get_ipv4_address()) + '\n')

        return header + entries

    def update_routing_table(self, interface, ip, netmask):

        try:
            del self.routing_table[interface]
        except KeyError:
            pass

        prefix = "/" + hf.get_ipv4_prefix_length(netmask)
        self.routing_table[interface] = [["Connected", hf.get_network_portion_ipv4(ip, netmask) + prefix, ip],
                                         ["Local", ip + "/32", "----"]]

    def show_routing_table(self):
        header = "{:<14} {:<10} {:<20} {:<15}".format('At Interface', 'Type', 'Destination Network',
                                                      'Next Hop/Exit Interface')
        header += '\n----------------------------------------------------------------------\n'

        entries = ''
        for route in self.routing_table:
            flag = True
            for i in self.routing_table[route]:
                if flag:
                    entries += "{:<14} {:<10} {:<20} {:<15}".format(route.get_shortened_name(), i[0], i[1], i[2])
                    flag = False
                else:
                    entries += "{:<14} {:<10} {:<20} {:<15}".format("", i[0], i[1], i[2])

                entries += "\n"
        return header + entries

    def decide_route(self, packet):
        destination_ip = packet.get_dest_ip()
        routes = []
        for i in self.routing_table:
            for j in self.routing_table[i]:
                routes.append(j[1])

        most_specific_route = hf.match_dest_ip_to_route(destination_ip, routes)

        forwarding_interface = None
        for i in self.routing_table:
            for j in self.routing_table[i]:
                if j[1] == most_specific_route:
                    forwarding_interface = i
                    break

        return forwarding_interface

    def add_arp_entry(self, ipv4, mac_address, address_type):
        self.ARP_table[ipv4] = [mac_address, address_type, self.internal_clock.get_time()]

    def get_interfaces(self):
        return self.interfaces

    def get_host_name(self):
        return self.Host_Name

    def get_mac_address(self):
        return self.MAC_Address

    def get_interface_by_name(self, name):

        for i in self.interfaces:
            if name.lower() == i.get_shortened_name().lower():
                return i

        for intf in self.interfaces:
            for sub_intf in intf.get_sub_interfaces():
                if name.lower() == sub_intf.get_shortened_name().lower():
                    return sub_intf

        return None

    def get_canvas_object(self):
        return self.canvas_object

    def set_canvas_object(self, obj):
        self.canvas_object = obj

    def set_internal_clock(self, clock):
        self.internal_clock = clock

    def get_model(self):
        return self.Model_Number

    def get_arp_table(self):
        return nf.get_arp_table(self.ARP_table)

    def get_arp_table_actual(self):
        return self.ARP_table

    # -------------------------- Save & Load Methods -------------------------- #
    def get_save_info(self):
        interfaces = []
        for interface in self.interfaces:
            interfaces.append(interface.get_save_info())

        return [self.Host_Name, self.MAC_Address, self.ARP_table, self.save_routing_table(), interfaces]

    def save_routing_table(self):
        routing_table = {}
        for interface in self.routing_table:  # For every interface
            routing_table[interface.get_shortened_name()] = []  # Create a dict entry with the interface's name
            for route in self.routing_table[interface]:  # For every route associated with the interface
                routing_table[interface.get_shortened_name()].append([route[0], route[1], route[2]])  # Append
        return routing_table

    def set_arp_table(self, arp):
        self.ARP_table = arp

    def set_routing_table(self, rt_table):
        self.routing_table = rt_table

    def set_interfaces_on_load(self, interface):
        self.interfaces.append(interface)
    # -------------------------- Save & Load Methods -------------------------- #
