class SubInterface:

    def __init__(self, parent_interface, sub_name):
        self.parent_interface = parent_interface
        self.name = self.parent_interface.get_shortened_name() + sub_name
        self.ipv4_address = None
        self.subnet_mask = None
        self.vlan_id = None
        self.native_vlan = None

    def get_parent_interface(self):
        return self.parent_interface

    def get_ipv4_address(self):
        return self.ipv4_address

    def set_ipv4_address(self, address):
        self.ipv4_address = address

    def get_subnet_mask(self):
        return self.subnet_mask

    def set_subnet_mask(self, mask):
        self.subnet_mask = mask

    def get_vlan_id(self):
        return self.vlan_id

    def set_vlan_id(self, vid):
        self.vlan_id = vid

    def get_native_vlan(self):
        return self.native_vlan

    def set_native_vlan(self, n_vlan):
        self.native_vlan = n_vlan

    def get_name(self):
        return self.name
