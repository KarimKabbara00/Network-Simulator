class Dot1q:
    def __init__(self, vlan_id):
        self.tag_protocol_id = 0b1000000100000000  # 0x8100
        self.tag_control_information = []
        self.PCP = 0b000
        self.DEI = 0b0
        self.VID = vlan_id
        self.tag_control_information.append(self.PCP)
        self.tag_control_information.append(self.DEI)
        self.tag_control_information.append(self.VID)

    def get_tag_protocol_id(self):
        return self.tag_protocol_id

    def get_PCP(self):
        return self.PCP

    def get_DEI(self):
        return self.DEI

    def get_VID(self):
        return self.VID
