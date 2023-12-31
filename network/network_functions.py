import UI.helper_functions as hf
from network.ICMP import ICMP
from network.PDUs.ipv4_packet import ipv4_packet
from network.PDUs.Ethernet_Frame import EthernetFrame
from network.Arp import Arp
from network.Switch.Dot1q import Dot1q
import time
from network.PDUs.UDP import UDP
from network.Application_Protocols.DHCP import (DhcpDiscover, DhcpOffer, DhcpRequest, DhcpAcknowledge, DhcpRelease,
                                                DhcpRenew, DhcpDecline, DhcpNak)


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
        destination_host_unreachable = False
        broadcast_ping = False

        if same_subnet:

            if hf.get_broadcast_ipv4(dest_ip, source_netmask) == dest_ip:
                dst_mac = 'FF:FF:FF:FF:FF:FF'
                broadcast_ping = True

            else:
                if dest_ip not in host.get_arp_table():
                    host.arp_request(dest_ip)
                try:
                    dst_mac = host.get_arp_table()[dest_ip][0]
                except KeyError:
                    destination_host_unreachable = True

        # if the host is in another network, get (or learn) the mac address of the default route
        elif not same_subnet:
            if not default_gateway:
                destination_host_unreachable = True
            elif default_gateway not in host.get_arp_table():
                host.arp_request(default_gateway)
                # PROXY ARP REQUEST. Should the router send a reply without the PC having to send this?
                # if original_sender_ipv4 not in host.get_arp_table_actual():
                #     host.arp_request(original_sender_ipv4)
            try:
                dst_mac = host.get_arp_table()[default_gateway][0]
            except KeyError:
                destination_host_unreachable = True

        if destination_host_unreachable:
            canvas.get_info(info="Reply from " + source_ip + ": Destination Host Unreachable",
                            linebreak=True, last=False)
        else:
            icmp_segment = create_icmp_echo_segment()
            packet = create_ipv4_packet(icmp_segment, source_ip, dest_ip)
            frame = create_ethernet_frame(dst_mac, source_mac, None, packet, None)
            interface.send(frame)

        if _ != count - 1:
            time.sleep(time_between_pings)

        if host.get_received_ping_count() != _ + 1 and not destination_host_unreachable and not broadcast_ping:
            canvas.get_info(info="Request timed out.", linebreak=True, last=False)


def icmp_echo_reply(source_mac, source_ip, original_sender_ipv4, netmask, arp_table, host, default_gateway=None, dot1q=None):

    same_subnet = hf.is_same_subnet(source_ip, netmask, original_sender_ipv4)
    host_not_found = False
    dst_mac = ''

    if same_subnet:
        if original_sender_ipv4 not in host.get_arp_table():
            host.arp_request(original_sender_ipv4)
        try:
            dst_mac = arp_table[original_sender_ipv4][0]
        except KeyError:
            host_not_found = True

    else:
        if default_gateway not in host.get_arp_table():
            host.arp_request(default_gateway)
            # PROXY ARP REQUEST. Should the router send a reply without the PC having to send this?
            # if original_sender_ipv4 not in host.get_arp_table_actual():
            #     host.arp_request(original_sender_ipv4)
        try:
            dst_mac = host.get_arp_table()[default_gateway][0]
        except KeyError:
            host_not_found = True

    # dst_mac = arp_table[original_sender_ipv4][0]

    if not host_not_found:
        # Type 0 and code 0 indicate Echo Reply
        icmp_segment = create_icmp_reply_segment()
        packet = ipv4_packet(icmp_segment, dscp='000000', ecn='00', identification='0000000000000000', flags='000',
                             f_offset='0000000000000', ttl='10000000',
                             src_ip=source_ip, dst_ip=original_sender_ipv4, options='')
        frame = EthernetFrame(dst_mac=dst_mac, src_mac=source_mac, dot1q=dot1q, packet=packet, FCS=None)

        return frame


def create_arp_request(source_mac, source_ipv4, dest_ipv4, dot1q=None):
    # see ARP class definition for what these codes are
    # 4th arg, 0x0001, identifies an arp request
    # destination MAC is ignored, hence the empty arg
    arp_packet = Arp(0x0001, 0x0800, 0x06, 0x04, 0x0001, source_mac, source_ipv4, "", dest_ipv4)

    # ARP requests are always broadcast ethernet frames
    frame = EthernetFrame("FF:FF:FF:FF:FF:FF", source_mac, dot1q, arp_packet, None)

    return frame


def create_arp_reply(source_mac, source_ip, dest_mac, dest_ip, dot1q=None):
    # see ARP class definition for what these codes are
    # 4th arg, 0x0002, identifies an arp reply
    arp_packet = Arp(0x0001, 0x0800, 0x06, 0x04, 0x0002, source_mac, source_ip, dest_mac, dest_ip)

    # ARP requests are always broadcast ethernet frames
    frame = EthernetFrame(dest_mac, source_mac, dot1q, arp_packet, None)

    return frame


def create_dhcp_discover(source_mac, preferred_ip, transaction_id, dot1q=None):
    application_data = DhcpDiscover(True, preferred_ip, transaction_id)
    udp_segment = UDP(source_port=68, dest_port=67, data=application_data)
    packet = create_ipv4_packet(udp_segment, '0.0.0.0', '255.255.255.255')
    frame = create_ethernet_frame('FF:FF:FF:FF:FF:FF', source_mac, dot1q, packet, None)

    return frame


def create_dhcp_offer(source_ip, source_mac, flags, ci_address, yi_address, si_address, gi_address, ch_address, transaction_id, dot1q=None):
    application_data = DhcpOffer(flags, ci_address, yi_address, si_address, gi_address, ch_address, transaction_id)
    udp_segment = UDP(source_port=67, dest_port=68, data=application_data)
    packet = create_ipv4_packet(udp_segment, source_ip, '255.255.255.255')
    frame = create_ethernet_frame(ch_address, source_mac, dot1q, packet, None)
    return frame


def create_dhcp_request(source_mac, si_address, provided_ip, transaction_id, flags, dot1q=None):
    application_data = DhcpRequest(si_address, source_mac, provided_ip, transaction_id, flags)
    udp_segment = UDP(source_port=68, dest_port=67, data=application_data)
    packet = create_ipv4_packet(udp_segment, "0.0.0.0", '255.255.255.255')
    frame = create_ethernet_frame("FF:FF:FF:FF:FF:FF", source_mac, dot1q, packet, None)
    return frame


def create_dhcp_ack(source_ip, source_mac, flags, ci_address, yi_address, si_address, gi_address, ch_address, dest_ip,
                    transaction_id, options, dot1q=None):
    application_data = DhcpAcknowledge(flags, ci_address, yi_address, si_address, gi_address, ch_address, transaction_id
                                       , options)
    udp_segment = UDP(source_port=67, dest_port=68, data=application_data)
    packet = create_ipv4_packet(udp_segment, source_ip, dest_ip)
    frame = create_ethernet_frame(ch_address, source_mac, dot1q, packet, None)
    return frame


def create_dhcp_renew(ci_address, si_address, ch_address, dhcp_mac_address, flags, is_t1, transaction_id, dot1q=None):
    application_data = DhcpRenew(ci_address, si_address, ch_address, flags, is_t1, transaction_id)
    udp_segment = UDP(source_port=68, dest_port=67, data=application_data)
    packet = create_ipv4_packet(udp_segment, ci_address, si_address)
    frame = create_ethernet_frame(dhcp_mac_address, ch_address, dot1q, packet, None)
    return frame


def create_dhcp_release(source_mac, preferred_ipv4_address, dhcp_server_mac, dhcp_server_ip, dhcp_transaction_id,
                        dot1q=None):
    application_data = DhcpRelease(source_mac, preferred_ipv4_address, dhcp_server_ip, dhcp_transaction_id)
    udp_segment = UDP(source_port=68, dest_port=67, data=application_data)
    packet = create_ipv4_packet(udp_segment, preferred_ipv4_address, dhcp_server_ip)
    frame = create_ethernet_frame(dhcp_server_mac, source_mac, dot1q, packet, None)
    return frame


def create_dhcp_decline(source_mac, dhcp_server_ip_address, provided_ip, dhcp_transaction_id, flags, dot1q=None):
    application_data = DhcpDecline(source_mac, provided_ip, dhcp_server_ip_address, dhcp_transaction_id)
    udp_segment = UDP(source_port=68, dest_port=67, data=application_data)
    packet = create_ipv4_packet(udp_segment, '0.0.0.0', '255.255.255.255')
    frame = create_ethernet_frame('FF:FF:FF:FF:FF:FF', source_mac, dot1q, packet, None)
    return frame


def create_dhcp_nak(si_address, ch_address, transaction_id, source_mac, source_ip, dest_ip='255.255.255.255', dot1q=None):
    application_data = DhcpNak(si_address, ch_address, transaction_id)
    udp_segment = UDP(source_port=67, dest_port=68, data=application_data)
    packet = create_ipv4_packet(udp_segment, source_ip, dest_ip)
    frame = create_ethernet_frame(ch_address, source_mac, dot1q, packet, None)
    return frame


def interface_or_sub_interface(receiving_interface, forwarding_interface, original_sender_ipv4, packet_identifier, frame):
    dot1q_header = None
    if not receiving_interface.get_netmask():
        for x in receiving_interface.get_sub_interfaces():
            if hf.is_same_subnet(x.get_ipv4_address(), x.get_netmask(), original_sender_ipv4):
                receiving_interface = x
                if frame.get_dot1q():  # Check if the frame had a dot1q header
                    if packet_identifier == 'ipv4':
                        dot1q_header = create_dot1q_header(forwarding_interface.get_vlan_id())
                    elif packet_identifier == 'ARP':
                        dot1q_header = create_dot1q_header(receiving_interface.get_vlan_id())
    else:
        dot1q_header = frame.get_dot1q()

    return receiving_interface, dot1q_header
