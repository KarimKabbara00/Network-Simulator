import UI.helper_functions as hf


def set_ip(ip):
    x = ip.split('.')
    ip_address = ''

    if len(x) != 4:
        raise Exception("Invalid IP Address", ip)

    for i in x:
        if 0 <= int(i) <= 255:
            ip_address += bin(int(i))[2:].zfill(8)
        else:
            raise Exception("Invalid IP Address")

    return ip_address


def set_dscp(dscp):
    if any(c not in '01' for c in dscp) or len(dscp) != 6:
        raise Exception("Invalid DSCP")
    return dscp


def set_ecn(ecn):
    if any(c not in '01' for c in ecn) or len(ecn) != 2:
        raise Exception("Invalid ECN")
    return ecn


def set_options(options):
    if any(c not in '01' for c in options) or len(options) < 0 or len(options) > 320:
        raise Exception("Invalid Options")
    return options


def set_identification(identification):
    if any(c not in '01' for c in identification) or len(identification) != 16:
        raise Exception("Invalid Identification")
    return identification


def set_flags(flags):
    if any(c not in '01' for c in flags) or len(flags) != 3 or flags[0] != '0':
        raise Exception("Invalid Flags")
    return flags


def set_offset(offset):
    if any(c not in '01' for c in offset) or len(offset) != 13:
        raise Exception("Invalid Fragment Offset")
    return offset


def set_ttl(ttl):
    if any(c not in '01' for c in ttl) or len(ttl) != 8:
        raise Exception("Invalid Time to Live")
    return ttl


class ipv4_packet:

    def __init__(self, segment, dscp, ecn, identification, flags, f_offset, ttl, src_ip, dst_ip, options):
        self.segment = segment
        self.version = bin(4)[2:].zfill(4)
        self.DSCP = set_dscp(dscp)
        self.ECN = set_ecn(ecn)
        self.identification = set_identification(identification)
        self.flags = set_flags(flags)
        self.fragment_offset = f_offset
        self.ttl = set_ttl(ttl)
        self.protocol = bin(segment.get_protocol_id())[2:].zfill(8)
        self.src_ip = set_ip(src_ip)
        self.dst_ip = set_ip(dst_ip)
        self.options = set_options(options)

        self.IHL = self.__set_ihl()
        self.total_length = self.__set_total_length()
        self.checksum = None

        self.identifier = "ipv4"

    def __set_ihl(self):
        # calculate bytes used by options field
        # reserve 4 bytes at a time for the options field
        option_size = str(self.options)

        if len(option_size) % 32 != 0:
            option_size = ((len(option_size) // 32) + 1) * 4
        else:
            option_size = (len(option_size) // 32) * 4

        return bin(5 + option_size // 4)[2:].zfill(4)  # four byte increments

    def __set_total_length(self):
        return bin(self.segment.get_size() + (int(self.IHL, 2) * 4))[2:].zfill(16)

    def decrement_ttl(self):
        ttl_as_int = int(self.ttl, 2)
        ttl_as_int -= 1
        self.ttl = bin(ttl_as_int)[2:].zfill(8)

    def __calculate_checksum(self):
        pass

    def get_size(self):
        return self.total_length

    def get_segment(self):
        return self.segment

    def get_ttl(self):
        return self.ttl

    def __str__(self):
        return "Version: " + str(self.version) + "\n" + \
               "IHL: " + str(self.IHL) + "\n" + \
               "DSCP: " + str(self.DSCP) + "\n" + \
               "ECN: " + str(self.ECN) + "\n" + \
               "Total Length: " + str(self.total_length) + "\n" + \
               "Identification: " + str(self.identification) + "\n" + \
               "Flags: " + str(self.flags) + "\n" + \
               "Fragment Offset: " + str(self.fragment_offset) + "\n" + \
               "TTL: " + str(self.ttl) + "\n" + \
               "Protocol: " + str(self.protocol) + "\n" + \
               "Header Checksum: " + str(self.checksum) + "\n" + \
               "Source IP: " + str(self.src_ip) + "\n" + \
               "Destination IP: " + str(self.dst_ip) + "\n" + \
               "Options: " + str(self.options) + "\n"

    def get_identifier(self):
        return self.identifier

    def get_src_ip(self):
        return hf.bin_to_ipv4(self.src_ip)

    def get_dest_ip(self):
        return hf.bin_to_ipv4(self.dst_ip)
