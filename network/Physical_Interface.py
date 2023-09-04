class PhysicalInterface:

    def __init__(self, name, speed, device):
        self.speed = speed
        self.bandwidth = speed
        self.name = PhysicalInterface.set_name(speed) + name
        self.host = device
        self.host_mac_address = device.get_mac_address()
        self.is_connected = False
        self.connected_to = None
        self.cable = None
        self.operational = False
        self.administratively_down = False
        self.canvas_cable = None

        if self.host.get_model() == "R94X" or self.host.get_model() == "RTSA1000X":
            self.ip_address = None
            self.netmask = None

        if self.host.get_model() == "TSA1000X" or self.host.get_model() == "RTSA1000X":
            self.switchport_type = None  # If none, then all vlan traffic is allowed
            self.access_vlan_id = 1
            self.trunk_vlan_ids = []

    @staticmethod
    def set_name(speed):
        if speed == 10:
            return 'Eth'
        elif speed == 100:
            return 'Fa'
        elif speed == 1000:
            return 'G'
        elif speed == 10000:
            return '10G'
        else:
            raise Exception("Invalid Speed")

    def send(self, frame):
        self.cable.send(self, frame)

    def disconnect(self):
        self.canvas_cable = None
        self.is_connected = False
        self.connected_to = None
        self.cable = None
        self.operational = False

    def __str__(self):
        return self.name + " @ " + str(self.speed) + " mbps"

    def get_host(self):
        return self.host

    def get_host_mac_address(self):
        return self.host_mac_address

    def get_speed(self):
        return self.speed

    def get_bandwidth(self):
        return self.bandwidth

    def get_is_connected(self):
        return self.is_connected

    def get_connected_to(self):
        return self.connected_to

    def get_name(self):
        return self.name

    def get_shortened_name(self):
        return self.name.split(" @")[0]

    def get_is_operational(self):
        return self.operational

    def get_canvas_cable(self):
        return self.canvas_cable

    def get_administratively_down(self):
        return self.administratively_down

    def get_switchport_type(self):
        if self.host.get_model() == "TSA1000X" or self.host.get_model() == "RTSA1000X":
            return self.switchport_type
        else:
            raise Exception("What you doin bruh")

    def get_access_vlan_id(self):
        if self.host.get_model() == "TSA1000X" or self.host.get_model() == "RTSA1000X":
            return self.access_vlan_id
        else:
            raise Exception("What you doin bruh")

    def get_trunk_vlan_ids(self):
        if self.host.get_model() == "TSA1000X" or self.host.get_model() == "RTSA1000X":
            return self.trunk_vlan_ids
        else:
            raise Exception("What you doin bruh")

    def get_ipv4_address(self):
        if self.host.get_model() == "R94X" or self.host.get_model() == "RTSA1000X":
            if not self.ip_address:
                return "   ----"
            return self.ip_address
        else:
            raise Exception("What you doin bruh")

    def get_netmask(self):
        if self.host.get_model() == "R94X" or self.host.get_model() == "RTSA1000X":
            return self.netmask
        else:
            raise Exception("What you doin bruh")

    def set_ipv4_address(self, address):
        self.ip_address = address

    def set_netmask(self, netmask):
        self.netmask = netmask

    def set_speed(self, speed):
        self.speed = speed

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth

    def set_is_connected(self, is_connected):
        self.is_connected = is_connected

    def set_connected_to(self, connected_to):
        self.connected_to = connected_to

    def set_cable(self, cable):
        self.cable = cable

    def set_canvas_object(self, obj):
        self.canvas_cable = obj

    def set_operational(self, state, load=False):
        self.operational = state
        if not load:
            if self.operational:
                self.canvas_cable.set_light("Green", self.host.get_canvas_object().get_block_name())
            else:
                self.canvas_cable.set_light("Red", self.host.get_canvas_object().get_block_name())

    def set_administratively_down(self, is_down, load=False):
        self.administratively_down = is_down
        if not load:
            if is_down:
                self.set_operational(False)

            elif not is_down and self.is_connected:
                self.set_operational(True)

            elif not is_down and not self.is_connected:
                self.set_operational(False)

    def set_access_vlan_id(self, v_id):
        if self.host.get_model() == "TSA1000X" or self.host.get_model() == "RTSA1000X":
            self.access_vlan_id = v_id
            self.host.update_cam_table_vid(self, v_id)
        else:
            raise Exception("What you doin bruh")

    def set_switchport_type(self, sw_type):
        self.switchport_type = sw_type

    def add_allowed_trunk_vlan(self, vlan_id):
        self.trunk_vlan_ids.append(vlan_id)

    def get_save_info(self):
        return [self.speed, self.bandwidth, self.name, self.host_mac_address, self.is_connected, self.connected_to,
                self.operational, self.administratively_down]
