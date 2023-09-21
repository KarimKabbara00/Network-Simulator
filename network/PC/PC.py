import random as random
import time as time
import UI.helper_functions as hf
import network.network_functions as nf
from network.Interface_Operations.Physical_Interface import PhysicalInterface
from operations import globalVars


def generate_ip_address():
    random.seed(random.randint(0, 99999999))
    return "192.168.1." + str(random.randint(1, 254))


class PC:

    def __init__(self, model="SecondGen", host_name="PC"):

        self.Host_Name = host_name
        self.MAC_Address = hf.generate_mac_address()
        self.Model_Number = model
        self.interface = self.set_interface()

        self.ipv4_address = None  # generate_ip_address()  # TODO: REMOVE RANDOM IP
        self.netmask = None  # "255.255.255.0"  # TODO: REMOVE PRESET NETMASK
        self.ipv6_address = None
        self.ipv6_link_local = None  # TODO: GENERATE LINK LOCAL
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

        # DHCP
        self.dhcp_server = None
        self.autoconfiguration_enabled = False
        self.preferred_ipv4_address = None
        self.received_dhcp_offer = False
        self.ip_lease_time = None
        self.lease_start = None
        self.lease_end = None
        self.dns_servers = None  # assigned by dhcp, not dhcp related.
        self.domain_name = None  # ^
        self.dhcp_transaction_id = None
        # DHCP

        self.internal_clock = None

    def set_interface(self):
        return [PhysicalInterface('0/0', 1000, self)]

    def icmp_echo_request(self, dest_ipv4_address, count):
        nf.icmp_echo_request(self.ipv4_address, self.MAC_Address, self.netmask, self.default_gateway, dest_ipv4_address,
                             count, self.canvas_object, self, self.time_between_pings, self.interface[0])

        hf.compute_ping_stats(self.ping_rtt_times, dest_ipv4_address, count, self.received_ping_count,
                              self.canvas_object, self)
        globalVars.prompt_save = True

    def icmp_echo_reply(self, original_sender_ipv4):
        frame = nf.icmp_echo_reply(self.MAC_Address, self.ipv4_address, original_sender_ipv4, self.netmask,
                                   self.ARP_table, self, default_gateway=self.default_gateway)
        self.interface[0].send(frame)
        globalVars.prompt_save = True

    def arp_request(self, dst_ipv4_address):
        arp_frame = nf.create_arp_request(self.MAC_Address, self.ipv4_address, dst_ipv4_address)
        self.interface[0].send(arp_frame)
        globalVars.prompt_save = True

    def arp_reply(self, dest_mac, dest_ip):
        frame = nf.create_arp_reply(self.MAC_Address, self.ipv4_address, dest_mac, dest_ip)
        self.interface[0].send(frame)
        globalVars.prompt_save = True

    def send_dhcp_discover(self):
        self.dhcp_transaction_id = random.getrandbits(16)  # Random 16-bit number (stored as int)
        frame = nf.create_dhcp_discover(self.MAC_Address, self.preferred_ipv4_address, self.dhcp_transaction_id)
        self.interface[0].send(frame)
        globalVars.prompt_save = True

    def send_dhcp_request(self, dhcp_server_ip_address, provided_ip, transaction_id, flags):
        frame = nf.create_dhcp_request(self.MAC_Address, dhcp_server_ip_address, provided_ip, transaction_id, flags)
        self.interface[0].send(frame)
        globalVars.prompt_save = True

    def renew_nic_configuration(self):
        if not self.dhcp_server and self.autoconfiguration_enabled:
            self.send_dhcp_discover()
        elif self.dhcp_server and self.autoconfiguration_enabled:
            # TODO: dhcp renew packet
            # TODO: self.send_dhcp_renew()
            pass
        elif not self.autoconfiguration_enabled:
            pass

        self.autoconfiguration_enabled = True
        self.received_dhcp_offer = False

    def set_auto_configure(self, is_auto_config):
        self.autoconfiguration_enabled = is_auto_config
        if self.autoconfiguration_enabled:
            # TODO: if a dhcp server is already known, send a Request directly
            self.send_dhcp_discover()

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

            elif segment_identifier == "UDP":
                data = segment.get_data()
                application_identifier = data.get_application_identifier()
                match application_identifier:

                    case "DHCP":
                        if data.get_dhcp_identifier() == 'DHCP_OFFER' and not self.received_dhcp_offer:
                            # TODO: RFC requires ARP here to ensure address is not taken
                            self.received_dhcp_offer = True
                            dhcp_server_ip_address = data.get_si_address()
                            provided_ip = data.get_yi_address()
                            flags = data.get_flags()
                            self.send_dhcp_request(dhcp_server_ip_address, provided_ip, self.dhcp_transaction_id, flags)

                        elif data.get_dhcp_identifier() == "DHCP_ACK":
                            self.configure_nic_from_dhcp(data)
                            self.canvas_object.set_fields_from_dhcp(self.ipv4_address, self.netmask,
                                                                    self.default_gateway)

                    case _:
                        pass

        globalVars.prompt_save = True

    def add_arp_entry(self, ipv4, mac_address, address_type):
        self.ARP_table[ipv4] = [mac_address, address_type, self.internal_clock.now()]

    def get_interfaces(self):
        return self.interface

    def get_interface_by_name(self, ignored):
        return self.interface[0]  # does the same as the function above it. Needed in EthCableCanvas

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

    def get_ipv6_link_local(self):
        if not self.ipv6_link_local:
            return ""
        return self.ipv6_link_local

    def get_prefix(self):
        if not self.prefix:
            return ""
        return self.prefix

    def get_domain_name(self):
        if not self.domain_name:
            return ''
        return self.domain_name

    def get_dns_servers(self, as_list=False):
        if not self.dns_servers:
            return ''
        elif as_list:
            dns_servers = self.dns_servers[0]
            try:
                for i in range(1, len(self.dns_servers)):
                    dns_servers += '\n' + 39 * ' ' + self.dns_servers[i]
            except IndexError:
                pass
            return dns_servers
        else:
            return self.dns_servers

    def get_dhcp_server(self):
        if not self.dhcp_server:
            return ''
        return self.dhcp_server

    def get_lease_time(self):
        if not self.ip_lease_time:
            return ''
        return self.ip_lease_time

    def get_lease_start(self, format_date=False):
        if not self.lease_start:
            return ''
        elif not format_date:
            return self.lease_start
        else:
            return self.lease_start.strftime('%A, %B %d, %Y %I:%M:%S %p')

    def get_lease_end(self):
        if not self.lease_end:
            return ''
        return self.lease_end

    def expire_ip_lease(self):
        self.dhcp_server = None
        self.autoconfiguration_enabled = False
        self.ipv4_address = None
        self.netmask = None
        self.received_dhcp_offer = False
        self.ip_lease_time = None
        self.lease_start = None
        self.lease_end = None
        self.dns_servers = None
        self.domain_name = None
        self.dhcp_transaction_id = None

    def configure_nic_from_dhcp(self, data):
        self.dhcp_server = data.get_si_address()
        self.ipv4_address = self.preferred_ipv4_address = data.get_yi_address()
        options = data.get_options()
        self.netmask = options['REQUEST_SUBNET_MASK']
        self.default_gateway = options['REQUEST_ROUTER']
        self.ip_lease_time = options['LEASE_TIME']
        self.dns_servers = options['REQUEST_DNS_SERVER']
        self.domain_name = options['REQUEST_DOMAIN_NAME']
        self.lease_start = globalVars.internal_clock.now()
        self.lease_end = globalVars.internal_clock.add_seconds_to_date(self.ip_lease_time, format_date=True)

    def get_auto_config(self, as_str=False):
        if as_str:
            return "Yes" if self.autoconfiguration_enabled else "No"
        else:
            return self.autoconfiguration_enabled

    def get_arp_table(self):
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

    def set_ipv4_address(self, ip, is_preferred=True):
        self.ipv4_address = ip
        if is_preferred:
            self.preferred_ipv4_address = self.ipv4_address

    def get_preferred_ip(self):
        return self.preferred_ipv4_address

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

    def set_internal_clock(self, clock):
        self.internal_clock = clock

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
