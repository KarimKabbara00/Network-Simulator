import UI.helper_functions as hf
from network.PC.PC import PC

def arp_table(table):
    header = "{:<25} {:<25} {:<15}".format('Internet Address', 'Physical Address', 'Type')
    header += '\n-----------------------------------------------------------\n'
    entries = ''
    for ip in table:
        entries += "{:<25} {:<25} {:<15}".format(ip, table[ip][0], table[ip][1])
        entries += "\n"
    return header + entries


def ip_config(host):

    header = "\nPC IP Configuration\n\n\nEthernet adapter Ethernet 1:"
    dns = '   ' + hf.build_ip_config_line("Connection-specific DNS Suffix", host.get_domain_name())
    ll_ipv6 = '   ' + hf.build_ip_config_line("Link-local IPv6 Address", host.get_ipv6_link_local())
    ipv4 = '   ' + hf.build_ip_config_line("IPv4 Address", host.get_ipv4_address())
    subnet = '   ' + hf.build_ip_config_line("Subnet Mask", host.get_netmask())
    def_gw = '   ' + hf.build_ip_config_line("Default Gateway", host.get_default_gateway())

    return header + '\n' + dns + '\n' + ll_ipv6 + '\n' + ipv4 + '\n' + subnet + '\n' + def_gw + '\n'


def ip_config_all(host: PC):

    information = ''
    header = "\nPC IP Configuration\n\n"

    hostname = '   ' + hf.build_ip_config_line("Host Name", host.get_host_name()) + '\n'
    primary_dns = '   ' + hf.build_ip_config_line("Primary DNS Suffix", host.get_domain_name()) + '\n'
    node_type = '   ' + hf.build_ip_config_line("Node Type", 'Hybrid') + '\n'
    ip_routing = '   ' + hf.build_ip_config_line("IP Routing Enabled", 'No') + '\n'
    # wins_proxy = '   ' + hf.build_ip_config_line("WINS Proxy Enabled", 'No') + '\n'
    dns_search = '   ' + hf.build_ip_config_line("DNS Suffix Search List", host.get_domain_name()) + '\n'

    information += header + hostname + primary_dns + node_type + ip_routing + dns_search

    header_2 = "\nEthernet adapter Ethernet 1:\n\n"

    dns = '   ' + hf.build_ip_config_line("Connection-specific DNS Suffix", host.get_domain_name()) + '\n'
    description = '   ' + hf.build_ip_config_line("Description", "Standard PC NIC") + '\n'
    physical_addr = '   ' + hf.build_ip_config_line("Physical Address", host.get_mac_address()) + '\n'

    is_dhcp_enabled = "No"
    if host.get_dhcp_server():
        is_dhcp_enabled = "Yes"
    dhcp_enabled = '   ' + hf.build_ip_config_line("DHCP Enabled", is_dhcp_enabled) + '\n'

    auto_config = '   ' + hf.build_ip_config_line("Autoconfiguration Enabled",
                                                  host.get_auto_config(as_str=True)) + '\n'
    ll_ipv6 = '   ' + hf.build_ip_config_line("Link-local IPv6 Address", host.get_ipv6_link_local()) + '\n'

    is_preferred = ''
    if host.get_preferred_ip():
        is_preferred = '(Preferred)'
    ipv4 = '   ' + hf.build_ip_config_line("IPv4 Address", host.get_ipv4_address() + is_preferred) + '\n'

    subnet = '   ' + hf.build_ip_config_line("Subnet Mask", host.get_netmask()) + '\n'
    lease_start = '   ' + hf.build_ip_config_line("Lease Obtained", host.get_lease_start()) + '\n'
    lease_end = '   ' + hf.build_ip_config_line("Lease Expires", host.get_lease_end()) + '\n'
    def_gw = '   ' + hf.build_ip_config_line("Default Gateway", host.get_default_gateway()) + '\n'
    dhcp_server = '   ' + hf.build_ip_config_line("DHCP Server", host.get_dhcp_server()) + '\n'
    # dhcp_v6_iaid = '   ' + hf.build_ip_config_line("DHCP IAID", "") + '\n'
    # dhcp_v6_client_duid = '   ' + hf.build_ip_config_line("DHCP Client DUID", "") + '\n'
    dns_servers = '   ' + hf.build_ip_config_line("DNS Servers", host.get_dns_servers(as_list=True)) + '\n'
    # prim_wins_server = '   ' + hf.build_ip_config_line("Primary WINS Server", "") + '\n'
    # netbios_over_tcpip = '   ' + hf.build_ip_config_line("NetBIOS over Tcpip", "") + '\n'

    information += (header_2 + dns + description + physical_addr + dhcp_enabled + auto_config + ll_ipv6 + ipv4 + subnet
                    + lease_start + lease_end + def_gw + dhcp_server + dns_servers)
    return information
