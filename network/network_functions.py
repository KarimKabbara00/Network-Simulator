import UI.helper_functions as hf
from network.ICMP import ICMP
from network.ipv4_packet import ipv4_packet
from network.Ethernet_Frame import EthernetFrame
from network.Arp import Arp
from network.Dot1q import Dot1q
import time
import copy


def create_icmp_echo_segment():
    # Type 8 and code 0 indicate Echo Request
    return ICMP(icmp_type=0b00001000, icmp_code=0b00000000)


def create_icmp_reply_segment():
    return ICMP(icmp_type=0b00000000, icmp_code=0b00000000)


def create_ipv4_packet(segment, source_ip, destination_ip):
    return ipv4_packet(segment, dscp='000000', ecn='00', identification='0000000000000000', flags='000',
                       f_offset='0000000000000', ttl='10000000', src_ip=source_ip, dst_ip=destination_ip, options='')


def create_ethernet_frame(destination_mac, source_mac, dot1q, packet, FCS):
    return EthernetFrame(dst_mac=destination_mac, src_mac=source_mac, dot1q=dot1q, packet=packet, FCS=FCS)


def create_dot1q_header(vlan_id):
    return Dot1q(vlan_id)


def icmp_echo_request(source_ip, source_mac, source_netmask, default_gateway, dest_ip, count, canvas, host,
                      time_between_pings, interface):
    same_subnet = hf.is_same_subnet(source_ip, source_netmask, dest_ip)

    canvas.toggle_cli_busy()

    for _ in range(count):
        host.set_start_time(time.time())

        # if the host is in the same network, get (or learn) the mac address of the destination host
        dst_mac = ""
        host_not_found = False
        if same_subnet:
            if dest_ip not in host.get_arp_table_actual():
                host.arp_request(dest_ip)
            try:
                dst_mac = host.get_arp_table_actual()[dest_ip][0]
            except KeyError:
                host_not_found = True

        # if the host is in another network, get (or learn) the mac address of the default route
        elif not same_subnet:
            if not default_gateway:
                host_not_found = True
            elif default_gateway not in host.get_arp_table_actual():
                host.arp_request(default_gateway)
            try:
                dst_mac = host.get_arp_table_actual()[default_gateway][0]
            except KeyError:
                host_not_found = True

        if host_not_found:
            canvas.get_info(info="Reply from " + source_ip + ": Destination Host Unreachable",
                            linebreak=True, last=False)
        else:
            icmp_segment = create_icmp_echo_segment()
            packet = create_ipv4_packet(icmp_segment, source_ip, dest_ip)
            frame = create_ethernet_frame(dst_mac, source_mac, None, packet, None)
            interface.send(frame)

        if _ != count - 1:
            time.sleep(time_between_pings)

        if host.get_received_ping_count() != _ + 1 and not host_not_found:
            canvas.get_info(info="Reply from " + source_ip + ": Destination Host Unreachable",
                            linebreak=True, last=False)


def icmp_echo_reply(source_mac, source_ip, original_sender_ipv4, arp_table):
    dst_mac = arp_table[original_sender_ipv4][0]

    # Type 0 and code 0 indicate Echo Reply
    icmp_segment = create_icmp_reply_segment()
    packet = ipv4_packet(icmp_segment, dscp='000000', ecn='00', identification='0000000000000000', flags='000',
                         f_offset='0000000000000', ttl='10000000',
                         src_ip=source_ip, dst_ip=original_sender_ipv4, options='')
    frame = EthernetFrame(dst_mac=dst_mac, src_mac=source_mac, dot1q=None, packet=packet, FCS=None)

    return frame


def create_arp_request(source_mac, source_ipv4, dest_ipv4):
    # see ARP class definition for what these codes are
    # 4th arg, 0x0001, identifies an arp request
    # destination MAC is ignored, hence the empty arg
    arp_packet = Arp(0x0001, 0x0800, 0x06, 0x04, 0x0001, source_mac, source_ipv4, "", dest_ipv4)

    # ARP requests are always broadcast ethernet frames
    frame = EthernetFrame("FF:FF:FF:FF:FF:FF", source_mac, None, arp_packet, None)

    return frame


def create_arp_reply(source_mac, source_ip, dest_mac, dest_ip):
    # see ARP class definition for what these codes are
    # 4th arg, 0x0002, identifies an arp reply
    arp_packet = Arp(0x0001, 0x0800, 0x06, 0x04, 0x0002, source_mac, source_ip, dest_mac, dest_ip)

    # ARP requests are always broadcast ethernet frames
    frame = EthernetFrame(dest_mac, source_mac, None, arp_packet, None)

    return frame


def get_arp_table(arp_table):
    header = "{:<25} {:<25} {:<15}".format('Internet Address', 'Physical Address', 'Type')
    header += '\n-----------------------------------------------------------\n'
    entries = ''
    for ip in arp_table:
        entries += "{:<25} {:<25} {:<15}".format(ip, arp_table[ip][0], arp_table[ip][1])
        entries += "\n"
    return header + entries


def background_processes(internal_clock):

    # Dynamic MAC Address Aging = 5 minutes
    # Dynamic ARP Entry Aging = 2 minutes

    pcs = internal_clock.get_pcs()
    sws = internal_clock.get_switches()
    ros = internal_clock.get_routers()

    while True:
        print(pcs, sws, ros)

        # PCs and routers have ARP tables
        for i in pcs + ros:
            node = i.get_class_object()
            arp_table = node.get_arp_table_actual()

            for ip in copy.copy(arp_table):
                if arp_table[ip][1] == 'DYNAMIC' and internal_clock.get_time() > arp_table[ip][2] + 120:
                    arp_table.pop(ip)
                    node.set_arp_table(arp_table)

        # Switches have MAC tables:
        # for i in globalVars.sw_objects:
        #     i.get_class_object.get_CAM_table()

        time.sleep(5)
