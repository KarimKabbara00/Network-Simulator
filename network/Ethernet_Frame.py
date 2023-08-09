def set_mac(mac):
    mac_address = mac.split(':')
    big_mac = ''
    for m in mac_address:
        if any(c not in '0123456789ABCDEFabcdef' for c in m) or len(m) != 2:
            raise Exception("Invalid MAC Address")
        big_mac += bin(int(m, 16))[2:].zfill(8)
    return big_mac


class EthernetFrame:

    def __init__(self, dst_mac, src_mac, dot1q, packet, FCS):
        self.preamble = '1010101010101010101010101010101010101010101010101010101010101010'
        self.SFD = '10101011'
        self.dst_mac = set_mac(dst_mac)
        self.src_mac = set_mac(src_mac)
        self.dot1q = dot1q

        self.FCS = FCS
        self.packet = packet

        self.type_or_length = self.set_t_l()

    def set_t_l(self):
        return bin(26 + int(self.packet.get_size(), 2))[2:].zfill(16)

    def get_src_mac(self):
        return self.src_mac

    def get_dst_mac(self):
        return self.dst_mac

    def get_dot1q(self):
        return self.dot1q

    def get_packet(self):
        return self.packet

    def __str__(self):
        return "Source MAC Address: " + str(self.src_mac) + "\n" + \
               "Destination MAC Address: " + str(self.dst_mac) + "\n" + \
               "Dot1Q: " + str(self.dot1q is not None) + "\n" + \
               "Type/Length: " + str(self.type_or_length) + "\n" + \
               "FCS: " + str(self.FCS)
