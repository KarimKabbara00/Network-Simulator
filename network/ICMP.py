class ICMP:

    def __init__(self, icmp_type, icmp_code, data="00000000000000000000000000000000"):
        self.type = icmp_type
        self.code = icmp_code
        self.checksum = None
        self.rest_of_header = None
        self.data = data
        self.protocol_id = 1
        if self.type == 0b00001000 and self.code == 0b000000000:
            self.segment_identifier = "ICMP ECHO REQUEST"
        elif self.type == 0b00000000 and self.code == 0b00000000:
            self.segment_identifier = "ICMP ECHO REPLY"
        self.size = 8  # Only for non error messages

    def get_icmp_type(self):
        return self.type

    def get_icmp_code(self):
        return self.code

    def get_icmp_roh(self):
        return self.rest_of_header

    def get_icmp_data(self):
        return self.data

    def get_protocol_id(self):
        return self.protocol_id

    def get_size(self):
        return self.size + len(self.data.encode('utf-8'))

    def get_data(self):
        return self.data

    def get_segment_identifier(self):
        return self.segment_identifier
