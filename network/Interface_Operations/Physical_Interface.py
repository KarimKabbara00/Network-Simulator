class PhysicalInterface:

    def __init__(self, name, speed, device):
        self.speed = speed
        self.bandwidth = speed
        self.name = PhysicalInterface.set_name(speed) + name
        self.host = device
        self.host_mac_address = device.get_mac_address()
        self.is_connected = False
        self.connected_to = None
        self.connected_to_MAC = None
        self.cable = None
        self.operational = False
        self.administratively_down = False
        self.canvas_cable = None

        if self.host.get_model() == "R94X" or self.host.get_model() == "RTSA1000X":
            self.ipv4_address = None
            self.netmask = None
            self.sub_interfaces = []
            self.preferred_ipv4_address = None
            self.dhcp_transaction_id = None
            self.dhcp_server_ip = None
            self.dhcp_server_mac = None

        if self.host.get_model() == "TSA1000X" or self.host.get_model() == "RTSA1000X":
            self.switchport_type = 'Access'  # If none, then all vlan traffic is allowed
            self.access_vlan_id = 1
            self.trunk_vlan_ids = []
            self.native_vlan = 1

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
        if self.operational:
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

        m1 = self.cable.get_rj45_side_1().get_host_mac_address()
        m2 = self.cable.get_rj45_side_2().get_host_mac_address()

        self.connected_to_MAC = m1
        if self.connected_to_MAC == self.get_host_mac_address():
            self.connected_to_MAC = m2

    def set_canvas_object(self, obj):
        if obj:
            self.canvas_cable = obj

    def set_operational(self, state):
        self.operational = state
        if self.operational:
            self.canvas_cable.set_light("Green", self.host.get_canvas_object().get_block_name())
        else:
            self.canvas_cable.set_light("Red", self.host.get_canvas_object().get_block_name())

    def set_administratively_down(self, is_down):
        self.administratively_down = is_down

        try:  # Won't error if cable is connected
            if is_down:
                self.set_operational(False)

            elif not is_down and self.is_connected:
                self.set_operational(True)

            elif not is_down and not self.is_connected:
                self.set_operational(False)
        except AttributeError:
            pass

    # ------ Switch only ------ #
    def set_access_vlan_id(self, v_id):
        if self.host.get_model() == "TSA1000X" or self.host.get_model() == "RTSA1000X":
            self.access_vlan_id = v_id
            self.host.update_cam_table_vid(self, v_id)
        else:
            raise Exception("What you doin bruh")

    def set_switchport_type(self, sw_type):
        self.switchport_type = sw_type

    def set_allowed_trunk_vlan(self, vlan_ids):
        self.trunk_vlan_ids = vlan_ids

    def add_allowed_trunk_vlan(self, vlan_ids):
        for i in vlan_ids:
            self.trunk_vlan_ids.append(i)

    def remove_allowed_trunk_vlan(self, vlan_ids):
        try:
            for i in vlan_ids:
                self.trunk_vlan_ids.remove(i)
        except ValueError:  # Not in list
            pass

    def get_native_vlan(self):
        return self.native_vlan

    def set_native_vlan(self, native):
        self.native_vlan = native
    # ------ Switch only ------ #

    # ------ Router only ------ #
    def add_sub_interface(self, sub):
        self.sub_interfaces.append(sub)

    def get_sub_interfaces(self):
        return self.sub_interfaces

    def get_ipv4_address(self):
        if self.host.get_model() == "R94X" or self.host.get_model() == "RTSA1000X":
            if not self.ipv4_address:
                # return "   ----"
                return None
            return self.ipv4_address
        else:
            raise Exception("What you doin bruh")

    def get_netmask(self):
        if self.host.get_model() == "R94X" or self.host.get_model() == "RTSA1000X":
            return self.netmask
        else:
            raise Exception("What you doin bruh")

    def set_ipv4_address(self, address):
        self.ipv4_address = address

    def set_netmask(self, netmask):
        self.netmask = netmask

    def get_preferred_ipv4_address(self):
        return self.preferred_ipv4_address

    def get_dhcp_transaction_id(self):
        return self.dhcp_transaction_id

    def set_dhcp_transaction_id(self, t_id):
        self.dhcp_transaction_id = t_id

    def get_sub_interface_by_name(self, name):
        for i in self.sub_interfaces:
            if i.get_shortened_name() == name:
                return name

    def configure_interface_from_dhcp(self, data, dhcp_server_mac):
        self.dhcp_server_ip = data.get_si_address()
        self.dhcp_server_mac = dhcp_server_mac
        self.ipv4_address = self.preferred_ipv4_address = data.get_yi_address()
        options = data.get_options()
        self.netmask = options['REQUEST_SUBNET_MASK']

    def get_ip_assignment_method(self):
        if not self.dhcp_server_ip and self.ipv4_address:
            return "NVRAM"
        elif self.dhcp_server_ip and self.ipv4_address:
            return "DHCP"
        else:
            return "Unset"
    # ------ Router only ------ #

    # -------------------------- Save & Load Methods -------------------------- #
    def get_save_info(self):
        if self.host.get_model() == "R94X" or self.host.get_model() == "RTSA1000X":

            sub_interfaces = []
            for i in self.sub_interfaces:
                sub_interfaces.append(i.get_save_info())

            return [self.speed, self.bandwidth, self.name, self.host_mac_address, self.is_connected, self.connected_to_MAC,
                    self.operational, self.administratively_down, self.ipv4_address, self.netmask, sub_interfaces]

        elif self.host.get_model() == "TSA1000X" or self.host.get_model() == "RTSA1000X":
            return [self.speed, self.bandwidth, self.name, self.host_mac_address, self.is_connected, self.connected_to_MAC,
                    self.operational, self.administratively_down, self.switchport_type, self.access_vlan_id, self.trunk_vlan_ids,
                    self.native_vlan]

        else:
            return [self.speed, self.bandwidth, self.name, self.host_mac_address, self.is_connected, self.connected_to_MAC,
                    self.operational, self.administratively_down]

    def set_allowed_trunk_vlans(self, vlans):
        self.trunk_vlan_ids = vlans
    # -------------------------- Save & Load Methods -------------------------- #
