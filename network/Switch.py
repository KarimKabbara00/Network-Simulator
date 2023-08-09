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

        # If the frame originated from the Native VLAN, the frame should be untagged
        try:
            src_dot1q = frame.get_dot1q().get_VID()
        except AttributeError:
            src_dot1q = None

        packet = frame.get_packet()

        # Get the interface and broadcast domain (vlan_id) to forward this frame
        interface, broadcast_domain = self.check_cam_table(original_src_mac, original_dst_mac, receiving_interface,
                                                           src_dot1q)

        # If the vlan ID is 1, don't tag the ethernet header
        if broadcast_domain != 1:
            dot1q_header = nf.create_dot1q_header(broadcast_domain)
        else:
            dot1q_header = None

        # if CAM table entry exists
        if interface:
            if broadcast_domain == interface[1]:  # if equal to dst vlan
                new_frame = self.encapsulate(hf.bin_to_hex(original_src_mac), hf.bin_to_hex(original_dst_mac),
                                             dot1q_header, packet, receiving_interface)
                # pass in src_mac so that we don't forward it back to sender
                self.unicast(new_frame)

            # # If an interface is a trunk port, and vlan is allowed on it
            # elif interface[3].get_switchport_type() == "Trunk" and broadcast_domain in interface[3].get_trunk_vlan_ids():
            #     new_frame = self.encapsulate(hf.bin_to_hex(original_src_mac), hf.bin_to_hex(original_dst_mac),
            #                                  dot1q_header, packet, receiving_interface)
            #     # pass in src_mac so that we don't forward it back to sender
            #     self.unicast(new_frame)

        # if not, broadcast it
        else:
            new_frame = self.encapsulate(hf.bin_to_hex(original_src_mac), 'FF:FF:FF:FF:FF:FF', dot1q_header, packet,
                                         receiving_interface)
            # pass in src_mac so that we don't forward it back to sender
            self.broadcast(new_frame, original_src_mac, src_dot1q)  # Only broadcast it in the host's vlan

    def check_cam_table(self, src_mac, dst_mac, receiving_interface, src_dot1q):

        count = len(self.CAM_table)

        # change binary mac to hex mac
        src_mac = hf.bin_to_hex(src_mac)
        dst_mac = hf.bin_to_hex(dst_mac)

        # If the sender is a host, dot1q will be None, correct it by setting vlan_id to the port's
        if not src_dot1q:
            src_dot1q = receiving_interface.get_access_vlan_id()

        # Check if the sender MAC and interface combo is in the CAM table
        exists = False
        for i in self.CAM_table:
            if self.CAM_table[i][0] == src_mac and self.CAM_table[i][3] == receiving_interface:
                exists = True
                break

        # If the sender MAC does not exist in the CAM table, add it
        if not exists:
            self.CAM_table[count] = [src_mac, src_dot1q, 'DYNAMIC', receiving_interface]

        # If a broadcast frame, return no specific cam table entry, and the corrected dot1q
        if dst_mac == "FF:FF:FF:FF:FF:FF":
            return None, src_dot1q

        # Return the cam table entry, and the corrected source_dot1q
        for i in self.CAM_table:
            if self.CAM_table[i][0] == dst_mac and self.CAM_table[i][1] == src_dot1q:
                return self.CAM_table[i], src_dot1q

        # Unknown Unicast
        return None, src_dot1q

    def unicast(self, frame):
        for i in self.CAM_table:
            if self.CAM_table[i][0] == hf.bin_to_hex(frame.get_dst_mac()):
                if self.CAM_table[i][3].get_is_operational():
                    self.CAM_table[i][3].send(frame)
                break

    def broadcast(self, frame, original_src_mac, broadcast_domain):

        # all interfaces except where the frame was received
        all_except = []

        # get all connected interfaces
        for i in self.interfaces:
            if i.get_is_connected():
                all_except.append(i)

        # keep only the interfaces in the same broadcast domain
        for i in self.interfaces:
            try:
                if i.get_access_vlan_id() != broadcast_domain:
                    all_except.remove(self.CAM_table[i][3])
            except KeyError:  # If the destination is not in the MAC table
                pass

        # keep all connected interfaces except where the frame was received
        for i in self.CAM_table:
            if self.CAM_table[i][0] == hf.bin_to_hex(original_src_mac):
                all_except.remove(self.CAM_table[i][3])
                break

        for i in all_except:
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
