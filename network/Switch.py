import UI.helper_functions as hf
import network.network_functions as nf
from network.Physical_Interface import PhysicalInterface


class Switch:

    def __init__(self, host_name="Switch"):
        self.MAC_Address = hf.generate_mac_address()
        self.Model_Number = "TSA1000X"
        self.Host_Name = host_name
        self.interfaces = self.set_interfaces()
        self.CAM_table = {}
        self.canvas_object = None

    def set_interfaces(self):
        interfaces = []
        for i in range(2):
            interfaces.append(PhysicalInterface('0/' + str(i), 100, self))
        for i in range(18):
            interfaces.append(PhysicalInterface('0/' + str(i), 1000, self))
        for i in range(4):
            interfaces.append(PhysicalInterface('0/' + str(i), 10000, self))
        return interfaces

    def encapsulate(self, src_mac, dst_mac, dot1q, packet, receiving_interface):
        if receiving_interface.get_access_vlan_id() > 1:
            dot1q = nf.create_dot1q_header(receiving_interface.get_access_vlan_id())
        frame = nf.create_ethernet_frame(dst_mac, src_mac, dot1q, packet, None)
        return frame

    def de_encapsulate(self, frame, receiving_interface):
        original_src_mac = frame.get_src_mac()
        original_dst_mac = frame.get_dst_mac()
        src_dot1q = frame.get_dot1q()

        forwarding_interface, vlan_id = self.check_cam_table(original_src_mac, original_dst_mac, receiving_interface,
                                                             src_dot1q)

        # Unicast
        if forwarding_interface and forwarding_interface.get_is_operational():
            forwarding_interface.send(frame)

        # Unicast but interface is down
        elif forwarding_interface and not forwarding_interface.get_is_operational():
            pass

        # Broadcast
        elif not forwarding_interface:
            self.broadcast(frame, receiving_interface, vlan_id)

    def check_cam_table(self, src_mac, dst_mac, receiving_interface, src_dot1q):

        count = len(self.CAM_table)

        # change binary mac to hex mac
        src_mac = hf.bin_to_hex(src_mac)
        dst_mac = hf.bin_to_hex(dst_mac)

        if not src_dot1q:
            src_dot1q = receiving_interface.get_access_vlan_id()

        # Check if the source mac exists in the cam table
        exists = False
        for i in self.CAM_table:
            if self.CAM_table[i][0] == src_mac and self.CAM_table[i][3] == receiving_interface:
                exists = True
                break

        # if it doesn't, add it
        if not exists:
            self.CAM_table[count] = [src_mac, src_dot1q, 'DYNAMIC', receiving_interface]

        # Get the forwarding interface
        for i in self.CAM_table:
            if self.CAM_table[i][0] == dst_mac and self.CAM_table[i][1] == src_dot1q:
                return self.CAM_table[i][3], self.CAM_table[i][1]

        # If a broadcast frame, or unknown unicast
        return None, src_dot1q

    def broadcast(self, frame, receiving_interface, broadcast_domain):

        forwarding_interfaces = []

        for i in self.interfaces:
            if i.get_is_operational() and i.get_access_vlan_id() == broadcast_domain and i != receiving_interface:
                forwarding_interfaces.append(i)

        for i in forwarding_interfaces:
            i.send(frame)

    def show_cam_table(self):
        header = "{:<8} {:<25} {:<15} {:<20}".format('VLAN', 'MAC Address', 'Type', 'Local Port')
        header += '\n-------------------------------------------------------------\n'
        entries = ''
        for entry in self.CAM_table:
            entries += "{:<8} {:<25} {:<15} {:<20}".format(self.CAM_table[entry][1], self.CAM_table[entry][0],
                                                           self.CAM_table[entry][2],
                                                           self.CAM_table[entry][3].__str__().split(" @")[0])
            entries += "\n"
        return header + entries

    def show_interfaces(self):
        header = "{:<15} {:<15} {:<15} {:<15} {:<15}".format('Interface', 'Connected', 'Operational', 'Speed',
                                                             'Bandwidth')
        header += '\n--------------------------------------------\n'
        entries = ''
        for interface in self.interfaces:
            int_co = "False"
            int_op = "False"
            if interface.get_is_connected():
                int_co = "True"
            if interface.get_is_operational():
                int_op = "True"

            entries += "{:<15} {:<15} {:<15}".format(interface.get_name(), int_co, int_op, interface.get_speed(),
                                                     interface.get_bandwidth())
            entries += "\n"
        return header + entries

    def disable_interface(self, interface):
        for i in self.interfaces:
            if i == interface:
                i.set_operational(False)
                break

    def get_interface_by_name(self, name):
        for i in self.interfaces:
            if name.lower() == i.get_shortened_name().lower():
                return i
        return None

    def get_canvas_object(self):
        return self.canvas_object

    def get_model(self):
        return self.Model_Number

    def get_interfaces(self):
        return self.interfaces

    def get_host_name(self):
        return self.Host_Name

    def get_mac_address(self):
        return self.MAC_Address

    def set_canvas_object(self, obj):
        self.canvas_object = obj

    def update_cam_table_vid(self, interface, vid):
        for i in self.CAM_table:
            if self.CAM_table[i][3] == interface:
                self.CAM_table[i][1] = vid

    def at_least_one_connected_interface(self):
        return any(i.get_is_connected() for i in self.interfaces)

    # -------------------------- Save & Load Methods -------------------------- #
    def get_save_info(self):

        interfaces = []
        for interface in self.interfaces:
            interfaces.append(interface.get_save_info())

        return [self.Host_Name, self.MAC_Address, self.Model_Number, self.CAM_table, interfaces]

    def set_cam_table(self, cam):
        self.CAM_table = cam

    def set_interfaces_on_load(self, interfaces):
        self.interfaces = interfaces
    # -------------------------- Save & Load Methods -------------------------- #
