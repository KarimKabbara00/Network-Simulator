def interfaces(interface_list):
    header = "{:<16} {:<15} {:<15} {:<15}".format('Interface', 'IP Address', 'Connected', 'Operational')
    header += '\n------------------------------------------------------------\n'
    entries = ''
    for interface in interface_list:
        int_co = "False"
        int_op = "False"
        if interface.get_is_connected():
            int_co = "True"
        if interface.get_is_operational():
            int_op = "True"

        ipv4 = interface.get_ipv4_address()
        if not ipv4:
            ipv4 = "   ----"

        entries += "{:<16} {:<15} {:<15} {:<15}".format(interface.get_shortened_name(), ipv4, int_co,
                                                        int_op) + '\n'

        for sub_intf in interface.get_sub_interfaces():
            entries += '--> ' + ("{:<12} {:<15}".format(sub_intf.get_shortened_name(),
                                                        sub_intf.get_ipv4_address()) + '\n')

    return header + entries


def routing_table(rt_table):
    header = "{:<10} {:<20} {:<15}".format('Type', 'Destination Network', 'Next Hop/Exit Interface')
    header += '\n--------------------------------------------------------\n'

    entries = ''
    for route in rt_table:
        flag = True
        for i in rt_table[route]:
            if flag:
                entries += "{:<10} {:<20} {:<15}".format(i[0], i[1], i[2])
                flag = False
            else:
                entries += "{:<10} {:<20} {:<15}".format(i[0], i[1], i[2])

            entries += "\n"
    return header + entries


def arp_table(table):
    header = "{:<25} {:<25} {:<15}".format('Internet Address', 'Physical Address', 'Type')
    header += '\n-----------------------------------------------------------\n'
    entries = ''
    for ip in table:
        entries += "{:<25} {:<25} {:<15}".format(ip, table[ip][0], table[ip][1])
        entries += "\n"
    return header + entries
