def cam_table(mac_table):
    header = "{:<8} {:<25} {:<15} {:<20}".format('VLAN', 'MAC Address', 'Type', 'Local Port')
    header += '\n-------------------------------------------------------------\n'
    entries = ''
    for entry in mac_table:
        entries += "{:<8} {:<25} {:<15} {:<20}".format(mac_table[entry][1], mac_table[entry][0],
                                                       mac_table[entry][2],
                                                       mac_table[entry][3].__str__().split(" @")[0])
        entries += "\n"
    return header + entries


def interfaces(interface_list):
    header = "{:<15} {:<15} {:<15} {:<15} {:<15}".format('Interface', 'Connected', 'Operational', 'Speed',
                                                         'Bandwidth')
    header += '\n-------------------------------------------------------------------------\n'
    entries = ''
    for interface in interface_list:
        int_co = "False"
        int_op = "False"
        if interface.get_is_connected():
            int_co = "True"
        if interface.get_is_operational():
            int_op = "True"

        entries += "{:<15} {:<15} {:<15} {:<15} {:<15}".format(interface.get_name(), int_co, int_op,
                                                               interface.get_speed(), interface.get_bandwidth())
        entries += "\n"
    return header + entries


def interfaces_trunk(interface_list):
    header = "{:<11} {:<12} {:<14} {:<9} {:<12} {:<12}".format('Interface', 'Operational', 'Encapsulation',
                                                               'Status', 'Native VLAN', 'Allowed VLANs')
    header += '\n----------------------------------------------------------------------------\n'
    for interface in interface_list:
        if interface.get_switchport_type() == 'Trunk':
            entries = ''

            int_op = "False"
            if interface.get_is_operational():
                int_op = "True"

            allowed_vlans = ','.join(str(e) for e in interface.get_trunk_vlan_ids())

            entries += ("{:<11} {:<12} {:<14} {:<9} {:<12} {:<12}".format(interface.get_name(), int_op,
                                                                          '802.1q', 'Trunking',
                                                                          interface.get_native_vlan(), allowed_vlans)
                        + '\n')
            header += entries
    return header


def vlans(vlan_list):
    header = "{:<4} {:<12} {:<14} {:<14}".format('ID', 'VLAN Name', 'Status', 'Ports')
    header += '\n--------------------------------------\n'
    entries = ''
    for vlan in vlan_list:

        name = vlan.get_name()
        if not name:
            name = '  -----'

        interfaces_on_vlan = ' '.join([i.get_shortened_name() for i in vlan.get_interfaces()])
        entries += "{:<4} {:<12} {:<14} {:<14}".format(vlan.get_id(), name, vlan.get_status(),
                                                       interfaces_on_vlan) + '\n'
        header += entries
        entries = ''

    return header + entries
