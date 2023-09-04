import random as random
import time as time
import UI.helper_functions as hf
import network.network_functions as nf
from network.Ethernet_Frame import EthernetFrame
from network.Physical_Interface import PhysicalInterface
from network.UDP import UDP
from network.ipv4_packet import ipv4_packet


def generate_ip_address():
    random.seed(random.randint(0, 99999999))
    return "192.168.1." + str(random.randint(1, 254))


class PC:

    def __init__(self, model="SecondGen", host_name="PC"):

        self.Host_Name = host_name
        self.MAC_Address = hf.generate_mac_address()
        self.Model_Number = model
        self.interface = self.set_interface()

        self.ipv4_address = generate_ip_address()  # TODO: REMOVE RANDOM IP
        self.netmask = "255.255.255.0"  # TODO: REMOVE PRESET NETMASK
        self.ipv6_address = None
        self.prefix = None
        self.default_gateway = None

        self.ARP_table = {}
        self.canvas_object = None

        # ICMP Control
        self.cli_busy = False
        self.start_time = 0
        self.time_between_pings = 1.5
        self.received_ping_count = 0
        self.ping_rtt_times = []
        # ICMP Control

    def set_interface(self):
        return [PhysicalInterface('0/0', 1000, self)]

    def send_message(self, message, destination_mac):

        segment = UDP(50000, 80, message)
        packet = ipv4_packet(segment, '000000', '00', '0000000000000000', '000', '0000000000000', '01000000',
                             self.ipv4_address, '192.168.1.1', '')
        frame = EthernetFrame(destination_mac, self.MAC_Address, None, packet, None)
        self.interface[0].send(frame)

    def icmp_echo_request(self, dest_ipv4_address, count):

        nf.icmp_echo_request(self.ipv4_address, self.MAC_Address, self.netmask, self.default_gateway, dest_ipv4_address,
                             count, self.canvas_object, self, self.time_between_pings, self.interface[0])

        hf.compute_ping_stats(self.ping_rtt_times, dest_ipv4_address, count, self.received_ping_count,
                              self.canvas_object, self)

    def icmp_echo_reply(self, original_sender_ipv4):
        if original_sender_ipv4 not in self.ARP_table:
            self.arp_request(original_sender_ipv4)
        frame = nf.icmp_echo_reply(self.MAC_Address, self.ipv4_address, original_sender_ipv4, self.ARP_table)
        self.interface[0].send(frame)

    def arp_request(self, dst_ipv4_address):
        arp_frame = nf.create_arp_request(self.MAC_Address, self.ipv4_address, dst_ipv4_address)
        self.interface[0].send(arp_frame)

    def arp_reply(self, dest_mac, dest_ip):
        frame = nf.create_arp_reply(self.MAC_Address, self.ipv4_address, dest_mac, dest_ip)
        self.interface[0].send(frame)

    def de_encapsulate(self, frame, receiving_interface):
        packet = frame.get_packet()
        packet_identifier = packet.get_identifier()

        if packet_identifier == "ARP":
            if packet.get_dest_ip() == self.ipv4_address:  # if ARP request is destined to this host
                if packet.get_operation_id() == 0x001:
                    dest_mac = packet.get_sender_mac()
                    dest_ipv4 = packet.get_src_ip()
                    self.arp_reply(dest_mac, dest_ipv4)
                    self.add_arp_entry(dest_ipv4, dest_mac, "DYNAMIC")
                elif packet.get_operation_id() == 0x002:
                    ipv4 = packet.get_src_ip()
                    mac_address = packet.get_sender_mac()
                    print(ipv4, mac_address)
                    self.add_arp_entry(ipv4, mac_address, "DYNAMIC")

        elif packet_identifier == "ipv4":
            segment = packet.get_segment()
            segment_identifier = segment.get_segment_identifier()
            data = segment.get_data()

            original_sender_ipv4 = packet.get_src_ip()

            if segment_identifier == "ICMP ECHO REQUEST":
                self.icmp_echo_reply(original_sender_ipv4=original_sender_ipv4)

            elif segment_identifier == "ICMP ECHO REPLY":
                time_taken = time.time() - self.start_time
                self.ping_rtt_times.append(time_taken)
                self.received_ping_count += 1

                time_taken = round(time_taken, 3)

                if time_taken <= 0.001:
                    time_taken = "<1ms"
                else:
                    time_taken = str(int(str(time_taken)[2:5])) + "ms"

                self.canvas_object.get_info(
                    info="Reply from " + original_sender_ipv4 + ": bytes=" + str(
                        segment.get_size()) + " time=" + time_taken + " TTL=" + str(int(packet.get_ttl(), 2)),
                    linebreak=True, last=False)

    def add_arp_entry(self, ipv4, mac_address, address_type):
        self.ARP_table[ipv4] = [mac_address, address_type]

    def get_interfaces(self):
        return self.interface

    def get_host_name(self):
        return self.Host_Name

    def get_mac_address(self):
        return self.MAC_Address

    def get_ipv4_address(self):
        if not self.ipv4_address:
            return ""
        return self.ipv4_address

    def get_netmask(self):
        if not self.netmask:
            return ""
        return self.netmask

    def get_ipv6_address(self):
        if not self.ipv6_address:
            return ""
        return self.ipv6_address

    def get_prefix(self):
        if not self.prefix:
            return ""
        return self.prefix

    def get_configurations(self):
        return {"Hostname: ": self.Host_Name, "MAC Address ": self.MAC_Address,
                "IPv4 Address: ": self.get_ipv4_address(),
                "Subnet Mask: ": self.get_netmask(),
                "IPv6 Address: ": self.get_ipv6_address() + " /" + self.get_prefix()}

    def get_arp_table(self):
        return nf.get_arp_table(self.ARP_table)

    def get_arp_table_actual(self):
        return self.ARP_table

    def get_cli_busy(self):
        return self.cli_busy

    def get_icmp_start_time(self):
        return self.start_time

    def get_canvas_object(self):
        return self.canvas_object

    def get_model(self):
        return self.Model_Number

    def get_default_gateway(self):
        if not self.default_gateway:
            return ""
        return self.default_gateway

    def get_received_ping_count(self):
        return self.received_ping_count

    def set_ipv4_address(self, ip):
        self.ipv4_address = ip

    def set_ipv6_address(self, ip):
        self.ipv6_address = ip

    def set_netmask(self, netmask):
        self.netmask = netmask

    def set_prefix(self, prefix):
        self.prefix = prefix

    def set_host_name(self, hostname):
        self.Host_Name = hostname

    def set_mac_address(self, mac_address):
        self.MAC_Address = mac_address

    def set_canvas_object(self, obj):
        self.canvas_object = obj

    def set_default_gateway(self, gateway):
        self.default_gateway = gateway

    def set_start_time(self, s_time):
        self.start_time = s_time

    def reset_ping_count(self, n):
        self.received_ping_count = n
        self.ping_rtt_times.clear()

    # -------------------------- Save & Load Methods -------------------------- #
    def get_save_info(self):
        return [self.Host_Name, self.MAC_Address, self.Model_Number, self.ipv4_address,
                self.netmask, self.ipv6_address, self.prefix, self.default_gateway, self.ARP_table,
                self.interface[0].get_save_info()]

    def set_arp_table(self, arp):
        self.ARP_table = arp

    def set_interfaces_on_load(self, interfaces):
        self.interface = [interfaces]
    # -------------------------- Save & Load Methods -------------------------- #
