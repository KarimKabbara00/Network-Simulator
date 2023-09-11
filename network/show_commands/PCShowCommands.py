def arp_table(table):
    header = "{:<25} {:<25} {:<15}".format('Internet Address', 'Physical Address', 'Type')
    header += '\n-----------------------------------------------------------\n'
    entries = ''
    for ip in table:
        entries += "{:<25} {:<25} {:<15}".format(ip, table[ip][0], table[ip][1])
        entries += "\n"
    return header + entries


def configuration(host):

    config = ''

    h = "{:<18} {:<18}".format("Hostname:",  host.get_host_name())
    m = "{:<18} {:<18}".format("MAC Address:",  host.get_mac_address())
    i = "{:<18} {:<18}".format("IPv4 Address:",  host.get_ipv4_address())
    n = "{:<18} {:<18}".format("Subnet Mask:",  host.get_netmask())
    d = "{:<18} {:<18}".format("Default Gateway:",  host.get_default_gateway())
    i6 = "{:<18} {:<18}".format("IPv6 Address:",  host.get_ipv6_address() + ' / ' + host.get_prefix())

    config += ('\n' + h + '\n' + m + '\n' + i + '\n' + n + '\n' + d + '\n' + i6)

    return config
