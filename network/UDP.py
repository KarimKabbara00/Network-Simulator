def set_port(port):
    if 0 <= port <= 65535:
        return bin(port)[2:].zfill(16)
    else:
        raise Exception("Invalid Source Port")


def calculate_checksum():
    return bin(0)[2:].zfill(16)


class UDP:

    def __init__(self, source_port, dest_port, data):
        self.source_port = set_port(source_port)
        self.dest_port = set_port(dest_port)
        self.data = data
        self.length = self.__calculate_length()
        self.checksum = calculate_checksum()
        self.protocol_id = 17
        self.segment_identifier = "UDP"

    def __calculate_length(self):
        size = 8 + len(self.data.encode('utf-8'))
        return bin(size)[2:].zfill(16)

    def get_size(self):
        return 8 + len(self.data.encode('utf-8'))

    def get_data(self):
        return self.data

    def get_protocol_id(self):
        return self.protocol_id

    def get_segment_identifier(self):
        return self.segment_identifier

    def __str__(self):
        return "Source Port: " + str(self.source_port) + "\n" + \
               "Destination Port: " + str(self.dest_port) + "\n" + \
               "Length: " + str(self.length) + "\n" + \
               "Checksum: " + str(self.checksum)
