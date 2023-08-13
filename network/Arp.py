class Arp:
    def __init__(self, link_layer_protocol_id, protocol_type, h_len, p_len, operation_id, sender_mac, sender_ip, dest_mac, dest_ip):
        self.hardware_type = link_layer_protocol_id     # Will be encapsulated in what? Ethernet frame is 0x0001
        self.protocol_type = protocol_type              # Address being used to learn the mac address (0x0800 for ipv4)
        self.h_len = h_len                              # 0x06 bytes for mac address size
        self.p_len = p_len                              # 0x04 bytes for ipv4 address size
        self.operation = operation_id                   # 0x0001 for ARP request, 0x0002 for ARP Reply
        self.sender_mac = sender_mac                    # sender mac address
        self.sender_ip = sender_ip                      # sender ip address
        self.dest_ip = dest_ip                          # dest ip address
        self.size = bin(26)
        if self.operation == 0x0001:
            self.dest_mac = "00:00:00:00:00:00"
        elif self.operation == 0x0002:
            self.dest_mac = dest_mac

        self.identifier = "ARP"

    def get_identifier(self):
        return self.identifier

    def get_operation_id(self):
        return self.operation

    def get_sender_mac(self):
        return self.sender_mac

    def get_src_ip(self):
        return self.sender_ip

    def get_dest_ip(self):
        return self.dest_ip

    def get_size(self):
        return self.size
