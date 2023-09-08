class SubInterface:

    def __init__(self, parent_interface, sub_name):
        self.parent_interface = parent_interface
        self.name = self.parent_interface.get_shortened_name() + sub_name
        self.ipv4_address = None
        self.subnet_mask = None
        self.vlan_id = None
        self.native_vlan = None

    def __str__(self):
        return self.name + " @ " + str(self.parent_interface.get_speed()) + " mbps"

    def send(self, frame):
        self.parent_interface.send(frame)

    def get_parent_interface(self):
        return self.parent_interface

    def get_ipv4_address(self):
        return self.ipv4_address

    def set_ipv4_address(self, address):
        self.ipv4_address = address

    def get_netmask(self):
        return self.subnet_mask

    def set_netmask(self, mask):
        self.subnet_mask = mask

    def get_vlan_id(self):
        return self.vlan_id

    def set_vlan_id(self, vid):
        self.vlan_id = vid

    def get_native_vlan(self):
        return self.native_vlan

    def set_native_vlan(self, n_vlan):
        self.native_vlan = n_vlan

    def get_shortened_name(self):
        return self.name

    def get_save_info(self):
        return [self.parent_interface.get_shortened_name(), self.name, self.ipv4_address, self.subnet_mask,
                self.vlan_id, self.native_vlan]
