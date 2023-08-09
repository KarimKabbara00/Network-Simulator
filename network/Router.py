import time

import UI.helper_functions as hf
import network.network_functions as nf
from network.Physical_Interface import PhysicalInterface


class Router:
    def __init__(self, host_name="Router"):
        self.MAC_Address = hf.generate_mac_address()
        self.Model_Number = "R94X"
        self.Host_Name = host_name

        self.serial_interfaces = []
        self.interfaces = self.set_interfaces()

        self.routing_table = {}  # TYPE (STATIC, Connected, Local)   DEST NETWORK    Exit Interface/Next hop
        self.ARP_table = {}

        self.canvas_object = None

    def set_interfaces(self):
        interfaces = []
        for i in range(8):
            interfaces.append(PhysicalInterface('0/' + str(i), 1000, self))
        for i in range(3):
            self.serial_interfaces.append(PhysicalInterface('0/' + str(i), 1000, self))
        return interfaces

    def de_encapsulate(self, frame, receiving_interface):

        packet = frame.get_packet()
        packet_identifier = packet.get_identifier()
        forwarding_interface = self.decide_route(packet)

        # if packet is destined to this device
        if packet.get_dest_ip() == forwarding_interface.get_ipv4_address():

            if packet_identifier == "ARP":

                # Receiving an ARP request
                if packet.get_operation_id() == 0x001:
                    dest_mac = packet.get_sender_mac()
                    dest_ipv4 = packet.get_sender_ip()
                    self.arp_reply(dest_mac, dest_ipv4, receiving_interface, receiving_interface.get_ipv4_address())
                    self.add_arp_entry(dest_ipv4, dest_mac, "DYNAMIC")

                # Receiving an ARP Reply
                elif packet.get_operation_id() == 0x002:
                    ipv4 = packet.get_sender_ip()
                    mac_address = packet.get_sender_mac()
                    self.add_arp_entry(ipv4, mac_address, "DYNAMIC")

            elif packet_identifier == "ipv4":
                segment = packet.get_segment()
                segment_identifier = segment.get_segment_identifier()

                original_sender_ipv4 = packet.get_src_ip()

                if segment_identifier == "ICMP ECHO REQUEST":
                    self.icmp_echo_reply(original_sender_ipv4, forwarding_interface)

        # Route the packet
        else:

            # Only route ipv4 packets
            if packet_identifier == "ipv4":
                try:
                    # Does the dest_ip exist in the ARP table?
                    dest_mac = self.ARP_table[packet.get_dest_ip()][0]

                    # Is there a dot1q header?
                    if frame.get_dot1q():
                        dot1q = frame.get_dot1q()
                    else:
                        dot1q = None

                    # Send the frame if dest_ip exists
                    new_frame = nf.create_ethernet_frame(dest_mac, self.MAC_Address, dot1q, packet, None)
                    forwarding_interface.send(new_frame)

                except KeyError:
                    # if the dest_ip does not exist, send an arp request out of the forwarding interface
                    self.arp_request(packet.get_dest_ip(), forwarding_interface)

    def icmp_echo_reply(self, original_sender_ipv4, interface):
        if original_sender_ipv4 not in self.ARP_table:
            self.arp_request(original_sender_ipv4, interface)
        frame = nf.icmp_echo_reply(self.MAC_Address, interface.get_ipv4_address(), original_sender_ipv4, self.ARP_table)
        interface.send(frame)

    def arp_request(self, dst_ipv4_address, forwarding_interface):
        arp_frame = nf.create_arp_request(self.MAC_Address, forwarding_interface.get_ipv4_address(), dst_ipv4_address)
        forwarding_interface.send(arp_frame)

    def arp_reply(self, dest_mac, dest_ip, receiving_interface, interface_ip_address):
        frame = nf.create_arp_reply(self.MAC_Address, interface_ip_address, dest_mac, dest_ip)
        receiving_interface.send(frame)

    def show_interfaces(self):
        header = "{:<12} {:<15} {:<15} {:<15}".format('Interface', 'IP Address', 'Connected', 'Operational')
        header += '\n--------------------------------------------------------\n'
        entries = ''
        for interface in self.interfaces:
            int_co = "False"
            int_op = "False"
            if interface.get_is_connected():
                int_co = "True"
            if interface.get_is_operational():
                int_op = "True"

            entries += "{:<12} {:<15} {:<15} {:<15}".format(interface.get_shortened_name(),
                                                            interface.get_ipv4_address(), int_co, int_op)
            entries += "\n"

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
        self.ARP_table[ipv4] = [mac_address, address_type]

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
        return None

    def get_canvas_object(self):
        return self.canvas_object

    def set_canvas_object(self, obj):
        self.canvas_object = obj

    def get_model(self):
        return self.Model_Number

    def get_arp_table(self):
        return nf.get_arp_table(self.ARP_table)
