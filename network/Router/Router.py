import random
import UI.helper_functions as hf
import network.Router.DHCP_Server
import network.network_functions as nf
from network.Interface_Operations.Physical_Interface import PhysicalInterface
from operations import globalVars
from network.Router.DHCP_Server import DHCP_Server
# from network.Application_Protocols.DHCP import DhcpDiscover
# from network.PDUs.UDP import UDP

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
        self.rt_count = 0
        self.ARP_table = {}

        # -- DHCP -- #
        self.dhcp_server = None
        self.sent_dhcp_discover = False     # DHCP Client
        # self.destination_dhcp_server = None # Relay
        # -- DHCP -- #

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

        # Get information from frame and packet
        packet = frame.get_packet()
        packet_identifier = packet.get_identifier()
        original_sender_ipv4 = packet.get_src_ip()
        original_sender_mac = hf.bin_to_hex(frame.get_src_mac())
        original_dest_ipv4 = packet.get_dest_ip()
        original_dest_mac = hf.bin_to_hex(frame.get_dst_mac())

        # Second and Third values are False and next hop IP if routing table specifies next hop, otherwise, True, None
        forwarding_interface, destination_directly_attached, next_hop_ip = self.decide_route(packet)

        # Adjust for sub-interfaces, if necessary
        receiving_interface, dot1q_header = nf.interface_or_sub_interface(receiving_interface, forwarding_interface,
                                                                          original_sender_ipv4, packet_identifier,
                                                                          frame)

        # Only deal with the packet if the receiving interface is operational
        if receiving_interface.get_is_operational():


            # # Check if the dest is in the router's ARP table, and the packet is not an ARP packet
            if (forwarding_interface and original_dest_ipv4 not in self.ARP_table and packet_identifier != 'ARP' and
                    original_dest_ipv4 != forwarding_interface.get_ipv4_address()):
                self.arp_request(original_dest_ipv4, forwarding_interface, dot1q_header)

            # If an ARP packet, use receiving interface to reply so that ARP isn't routed.
            if packet_identifier == "ARP":

                if packet.get_operation_id() == 0x001:
                    # If destined to me, reply with the receiving interface to the sender
                    if original_dest_ipv4 == receiving_interface.get_ipv4_address():
                        self.arp_reply(receiving_interface, receiving_interface.get_ipv4_address(), original_sender_mac,
                                       original_sender_ipv4, dot1q_header)

                    # If destined to someone on another subnet
                    elif not hf.is_same_subnet(receiving_interface.get_ipv4_address(),
                                               receiving_interface.get_netmask(),
                                               original_dest_ipv4):

                        # If not in ARP table, but in routing table (forwarding interface not None), send an ARP request
                        # to discover the original intended destination
                        if (original_dest_ipv4 not in self.ARP_table and forwarding_interface and
                                hf.is_same_subnet(forwarding_interface.get_ipv4_address(),
                                                  forwarding_interface.get_netmask(), original_dest_ipv4)):
                            self.arp_request(original_dest_ipv4, forwarding_interface, dot1q_header)

                        # If in ARP table, send a reply to the original destination
                        if original_dest_ipv4 in self.ARP_table:
                            # Goes to original dest
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
                            if destination_directly_attached:  # Is this going to another router? If not,
                                self.arp_request(original_dest_ipv4, forwarding_interface, dot1q_header)
                            else:  # If yes, forward it
                                frame = nf.create_ethernet_frame(self.ARP_table[next_hop_ip][0],
                                                                 self.MAC_Address, dot1q_header, packet, None)
                                forwarding_interface.send(frame)

                elif segment_identifier == "ICMP ECHO REPLY":
                    if original_dest_ipv4 == forwarding_interface.get_ipv4_address():
                        pass  # destined to me
                    else:
                        # If routing an ICMP reply, ICMP already reached its dest, therefore ARP entry exists already
                        if destination_directly_attached:
                            frame = nf.create_ethernet_frame(self.ARP_table[original_dest_ipv4][0], self.MAC_Address,
                                                             dot1q_header, packet, None)
                            forwarding_interface.send(frame)
                        else:
                            frame = nf.create_ethernet_frame(self.ARP_table[next_hop_ip][0],
                                                             self.MAC_Address, dot1q_header, packet, None)
                            forwarding_interface.send(frame)

                elif segment_identifier == "UDP":

                    data = segment.get_data()
                    application_identifier = data.get_application_identifier()

                    match application_identifier:
                        case "DHCP":
                            # ---- DHCP Client ---- #
                            if data.get_dhcp_identifier() == 'DHCP_OFFER' and self.sent_dhcp_discover:
                                self.send_dhcp_request(receiving_interface, data)

                            elif data.get_dhcp_identifier() == 'DHCP_ACK' and self.sent_dhcp_discover:
                                receiving_interface.configure_interface_from_dhcp(data, dhcp_server_mac=hf.bin_to_hex(frame.get_src_mac()))
                            # ---- DHCP Client ---- #

                            # # ---- DHCP Relay Agent ---- #
                            # if not self.dhcp_server and self.destination_dhcp_server:
                            #
                            #     if data.get_dhcp_identifier() == 'DHCP_DISCOVER':
                            #
                            #         gi_address = receiving_interface.get_ipv4_address()
                            #         try:
                            #             preferred_ip = data.get_options()['PREFERRED_IP']
                            #         except KeyError:
                            #             preferred_ip = ''
                            #
                            #         application_data = DhcpDiscover(False, preferred_ip, data.get_transaction_id(), gi_address)
                            #         segment = UDP(67, 67, application_data)
                            #
                            #         # Create intermediary packet using remote DHCP to learn forwarding interface
                            #         intermediary_packet = nf.create_ipv4_packet(segment, original_sender_ipv4, self.destination_dhcp_server)
                            #
                            #         # Get the forwarding interface using the intermediary packet
                            #         forwarding_interface, destination_directly_attached, next_hop_ip = self.decide_route(intermediary_packet)
                            #
                            #         # Check if remote DHCP is in ARP table
                            #         if self.destination_dhcp_server not in self.ARP_table:
                            #             self.arp_request(self.destination_dhcp_server, forwarding_interface)
                            #
                            #         # Recreate the packet again with the forwarding interface ipv4
                            #         modified_packet = nf.create_ipv4_packet(segment, forwarding_interface.get_ipv4_address(),
                            #                                                 self.destination_dhcp_server)
                            #
                            #         # Recreate the frame
                            #         frame = nf.create_ethernet_frame(self.ARP_table[self.destination_dhcp_server][0], self.MAC_Address,
                            #                                          dot1q_header, modified_packet, None)
                            #
                            #         forwarding_interface.send(frame)
                            #
                            #     elif data.get_dhcp_identifier() == 'DHCP_OFFER':
                            #         print('received DHCP_OFFER!')
                            #     elif data.get_dhcp_identifier() == 'DHCP_REQUEST':
                            #         print('received DHCP_REQUEST!')
                            #     elif data.get_dhcp_identifier() == 'DHCP_ACK':
                            #         print('received DHCP_ACK!')

                            # ---- DHCP Relay Agent ---- #

                            # ---- DHCP Server ---- #
                            if self.dhcp_server:

                                if data.get_dhcp_identifier() == 'DHCP_DISCOVER':
                                    print('received discover')
                                    frame = self.dhcp_server.create_offer(receiving_interface, data, original_sender_mac, self.MAC_Address)
                                    if frame:
                                        receiving_interface.send(frame)

                                elif data.get_dhcp_identifier() == 'DHCP_REQUEST':
                                    # Request destined to this DHCP server
                                    if data.get_si_address() == receiving_interface.get_ipv4_address():
                                        frame = self.dhcp_server.create_ack(receiving_interface, self.MAC_Address, data,
                                                                            original_sender_mac, dhcp_renew=False)
                                        if frame:
                                            receiving_interface.send(frame)
                                    # Request destined to another DHCP server -> revoke offer
                                    else:
                                        self.dhcp_server.revoke_offer(receiving_interface, data)

                                elif data.get_dhcp_identifier() == 'DHCP_RENEW':
                                    frame = self.dhcp_server.create_ack(receiving_interface, self.MAC_Address, data,
                                                                        original_sender_mac, dhcp_renew=True)
                                    if frame:
                                        receiving_interface.send(frame)

                                elif data.get_dhcp_identifier() == 'DHCP_RELEASE':
                                    self.dhcp_server.release_ip_assignment(receiving_interface, data)

                                elif data.get_dhcp_identifier() == 'DHCP_DECLINE':
                                    self.dhcp_server.process_dhcp_decline(receiving_interface, data)
                            # ---- DHCP Server ---- #

                        case _:
                            pass

        globalVars.prompt_save = True

    def icmp_echo_reply(self, original_sender_ipv4, interface, dot1q=None):
        if original_sender_ipv4 not in self.ARP_table:
            self.arp_request(original_sender_ipv4, interface, dot1q)

        frame = nf.icmp_echo_reply(self.MAC_Address, interface.get_ipv4_address(), original_sender_ipv4,
                                   interface.get_netmask(), self.ARP_table, self, dot1q)
        interface.send(frame)
        globalVars.prompt_save = True

    def arp_request(self, dst_ipv4_address, forwarding_interface, dot1q=None):
        arp_frame = nf.create_arp_request(self.MAC_Address, forwarding_interface.get_ipv4_address(), dst_ipv4_address,
                                          dot1q)
        forwarding_interface.send(arp_frame)
        globalVars.prompt_save = True

    def arp_reply(self, forwarding_interface, fwd_int_ip, dest_mac, dest_ip, dot1q=None):
        frame = nf.create_arp_reply(self.MAC_Address, fwd_int_ip, dest_mac, dest_ip, dot1q)
        forwarding_interface.send(frame)
        globalVars.prompt_save = True

    def update_routing_table(self, interface, ip, netmask, route_type='DEFAULT', next_hop_or_exit_interface=None):

        try:
            self.routing_table[self.rt_count]
        except KeyError:
            self.routing_table[self.rt_count] = []

        prefix = "/" + hf.get_ipv4_prefix_length(netmask)

        if route_type == 'DEFAULT':
            self.routing_table[self.rt_count].append(["Connected", hf.get_network_portion_ipv4(ip, netmask) + prefix,
                                                      interface.get_shortened_name()])
            self.routing_table[self.rt_count].append(["Local", ip + "/32", interface.get_shortened_name()])

        elif route_type == 'STATIC':
            self.routing_table[self.rt_count].append(
                ['Static', hf.get_network_portion_ipv4(ip, netmask) + prefix, next_hop_or_exit_interface])

        globalVars.prompt_save = True

    def decide_route(self, packet):
        destination_ip = packet.get_dest_ip()
        routes = []
        for i in self.routing_table:
            for j in self.routing_table[i]:
                routes.append(j[1])

        most_specific_route = hf.match_dest_ip_to_route(destination_ip, routes)

        next_hop_ip = None  # Only assigned if routing table specifies next hop instead of exit interface
        need_arp = False  # Only true if routing table specifies next hop instead of exit interface
        destination_directly_attached = True  # Changes to false if ^
        forwarding_interface = None
        for i in self.routing_table:
            for j in self.routing_table[i]:
                if j[1] == most_specific_route:
                    forwarding_interface, need_arp = self.get_interface(j[2])
                    if need_arp:
                        next_hop_ip = j[2]
                        destination_directly_attached = False
                    break

        if need_arp:
            # most_specific_route returns A.B.C.D/#. Split at / and pass in # to be converted to subnet mask
            forwarding_interface = hf.same_subnet_interface(self.interfaces,
                                                            most_specific_route.split('/')[1], next_hop_ip)
            if next_hop_ip not in self.ARP_table:
                self.arp_request(next_hop_ip, forwarding_interface)

        return forwarding_interface, destination_directly_attached, next_hop_ip

    def add_arp_entry(self, ipv4, mac_address, address_type):
        self.ARP_table[ipv4] = [mac_address, address_type, self.internal_clock.now()]

    def get_interfaces(self):
        return self.interfaces

    def get_interface(self, next_hop_or_exit_interface):
        if '/' in next_hop_or_exit_interface:
            return self.get_interface_by_name(next_hop_or_exit_interface), False
        else:
            return self.get_interface_by_next_hop(next_hop_or_exit_interface), True

    def get_host_name(self):
        return self.Host_Name

    def get_mac_address(self):
        return self.MAC_Address

    def get_routing_table(self):
        return self.routing_table

    def get_interface_by_name(self, name):

        for i in self.interfaces:
            if name.lower() == i.get_shortened_name().lower():
                return i

        for intf in self.interfaces:
            for sub_intf in intf.get_sub_interfaces():
                if name.lower() == sub_intf.get_shortened_name().lower():
                    return sub_intf

        return None

    def get_interface_by_next_hop(self, next_hop):
        for i in self.interfaces:
            if i.get_ipv4_address() == next_hop:
                return next_hop

    def get_canvas_object(self):
        return self.canvas_object

    def set_canvas_object(self, obj):
        self.canvas_object = obj

    def set_internal_clock(self, clock):
        self.internal_clock = clock

    def get_model(self):
        return self.Model_Number

    def get_arp_table(self):
        return self.ARP_table

    def get_dhcp_server(self, bg_process=False):
        if not self.dhcp_server and not bg_process:
            self.dhcp_server: network.Router.DHCP_Server.DHCP_Server = DHCP_Server(self)
        return self.dhcp_server

    def set_dhcp_server(self, server):
        self.dhcp_server = server

    def send_dhcp_discover(self, working_interface: PhysicalInterface):
        t_id = working_interface.get_dhcp_transaction_id()
        if not t_id:
            t_id = random.getrandbits(16)
            working_interface.set_dhcp_transaction_id(t_id)  # Random 16-bit number (stored as int)

        frame = nf.create_dhcp_discover(self.MAC_Address, working_interface.get_ipv4_address(), t_id)
        self.sent_dhcp_discover = True
        working_interface.send(frame)
        globalVars.prompt_save = True

    def send_dhcp_request(self, working_interface: PhysicalInterface, data):
        dhcp_server_ip_address = data.get_si_address()
        provided_ip = data.get_yi_address()
        flags = data.get_flags()

        frame = nf.create_dhcp_request(self.MAC_Address, dhcp_server_ip_address, provided_ip, working_interface.get_dhcp_transaction_id(), flags)
        working_interface.send(frame)
        globalVars.prompt_save = True

    # Relay stuff.
    # def set_destination_dhcp_for_relay_agent(self, dhcp_ip):
    #     self.destination_dhcp_server = dhcp_ip

    # -------------------------- Save & Load Methods -------------------------- #
    def get_save_info(self):
        interfaces = []
        for interface in self.interfaces:
            interfaces.append(interface.get_save_info())

        return [self.Host_Name, self.MAC_Address, self.save_arp_table(), self.save_routing_table(), interfaces, self.save_dhcp_server()]

    def save_routing_table(self):
        routing_table = {}
        count = 0
        for interface in self.routing_table:  # For every interface
            for route in self.routing_table[interface]:  # For every route associated with the interface
                try:
                    routing_table[count]
                except KeyError:
                    routing_table[count] = []
                routing_table[count].append([route[0], route[1], route[2]])  # Append
                count += 1
        return routing_table

    def save_arp_table(self):
        arp_table = {}
        for entry in self.ARP_table:
            arp_table[entry] = [self.ARP_table[entry][0], self.ARP_table[entry][1],
                                self.ARP_table[entry][2].strftime('%A, %B %d, %Y %I:%M:%S %p')]
        print(self.ARP_table)
        print(arp_table)
        return arp_table

    def save_dhcp_server(self):
        if self.dhcp_server:
            dhcp_excluded_ip_ranges = self.dhcp_server.get_excluded_addresses()
            t_ids = self.dhcp_server.get_transaction_ids()
            pools = self.dhcp_server.save_dhcp_pools()
            return [dhcp_excluded_ip_ranges, t_ids, pools]
        return []

    def set_arp_table(self, arp):
        self.ARP_table = arp

    def set_routing_table(self, rt_table, count):
        self.routing_table = rt_table
        self.rt_count = count

    def set_interfaces_on_load(self, interface):
        self.interfaces.append(interface)
    # -------------------------- Save & Load Methods -------------------------- #
