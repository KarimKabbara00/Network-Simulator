import UI.helper_functions as hf
import network.network_functions as nf
from network.Physical_Interface import PhysicalInterface
from network.Dot1q import Dot1q
from operations import globalVars


class Switch:

    def __init__(self, host_name="Switch", load=False):
        self.MAC_Address = hf.generate_mac_address()
        self.Model_Number = "TSA1000X"
        self.Host_Name = host_name

        self.CAM_table = {}
        self.VLANS = []
        self.interfaces = []
        if not load:
            self.interfaces = self.set_interfaces()

        self.canvas_object = None
        self.internal_clock = None

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

        do_not_tag = False

        # If received on a trunk port, check if it is allowed on the trunk
        if receiving_interface.get_switchport_type() == 'Trunk':

            if not src_dot1q:   # If trunk receives an untagged frame, set it to native vlan
                src_dot1q = receiving_interface.get_native_vlan()
                forwarding_interface, vlan_id = self.check_cam_table(original_src_mac, original_dst_mac,
                                                                     receiving_interface, src_dot1q)

            elif src_dot1q.get_VID() in receiving_interface.get_trunk_vlan_ids():
                src_dot1q = frame.get_dot1q().get_VID()
                forwarding_interface, vlan_id = self.check_cam_table(original_src_mac, original_dst_mac,
                                                                     receiving_interface, src_dot1q)
            else:
                forwarding_interface, vlan_id = None, None

            # If the forwarding interface's vlan matches the source vlan id, do not tag the frame
            if forwarding_interface and vlan_id != forwarding_interface.get_native_vlan():
                do_not_tag = True

        # If received on an access port, get the receiving interface's vlan id
        else:
            src_dot1q = receiving_interface.get_access_vlan_id()
            forwarding_interface, vlan_id = self.check_cam_table(original_src_mac, original_dst_mac,
                                                                 receiving_interface, src_dot1q)

        # If dot1q header exists, and its equal to the native vlan, tag the frame
        if vlan_id and not do_not_tag:
            frame.set_dot1q(Dot1q(vlan_id))
        else:
            frame.set_dot1q(None)

        print('SWITCH', forwarding_interface, hf.bin_to_hex(frame.get_dst_mac()), hf.bin_to_hex(frame.get_src_mac()),
              frame.get_packet().get_identifier(), src_dot1q, vlan_id)

        if forwarding_interface:  # Unicast
            self.unicast(frame, forwarding_interface, vlan_id)

        else:  # Broadcast
            self.broadcast(frame, receiving_interface, vlan_id)

        globalVars.prompt_save = True

    def check_cam_table(self, src_mac, dst_mac, receiving_interface, src_dot1q):

        count = len(self.CAM_table)

        # change binary mac to hex mac
        src_mac = hf.bin_to_hex(src_mac)
        dst_mac = hf.bin_to_hex(dst_mac)

        # Check if the source mac exists in the cam table
        exists = False
        for i in self.CAM_table:
            if (self.CAM_table[i][0] == src_mac and self.CAM_table[i][3] == receiving_interface and
                    self.CAM_table[i][1] == src_dot1q):
                exists = True
                break

        # if it doesn't, add it
        if not exists:
            self.CAM_table[count] = [src_mac, src_dot1q, 'DYNAMIC', receiving_interface, self.internal_clock.get_time()]

        # Get the forwarding interface
        for i in self.CAM_table:
            if self.CAM_table[i][0] == dst_mac and self.CAM_table[i][1] == src_dot1q:
                return self.CAM_table[i][3], self.CAM_table[i][1]

        # If a broadcast frame, or unknown unicast
        return None, src_dot1q

    def unicast(self, frame, forwarding_interface, vlan_id):

        # Unicast
        if forwarding_interface.get_switchport_type() == 'Access':
            if forwarding_interface and forwarding_interface.get_is_operational():
                forwarding_interface.send(frame)

            # Unicast but interface is down
            elif forwarding_interface and not forwarding_interface.get_is_operational():
                pass

        elif forwarding_interface.get_switchport_type() == 'Trunk':
            if any(v_id == vlan_id for v_id in forwarding_interface.get_trunk_vlan_ids()):
                forwarding_interface.send(frame)

    def broadcast(self, frame, receiving_interface, broadcast_domain):

        forwarding_interfaces = []

        for i in self.interfaces:
            if i.get_switchport_type() == 'Access':
                if i.get_is_operational() and i.get_access_vlan_id() == broadcast_domain and i != receiving_interface:
                    forwarding_interfaces.append(i)
            elif i.get_switchport_type() == 'Trunk':
                if (i.get_is_operational() and any(x == broadcast_domain for x in i.get_trunk_vlan_ids())
                        and i != receiving_interface):
                    forwarding_interfaces.append(i)

        # Remove duplicates
        forwarding_interfaces = list(set(forwarding_interfaces))

        for i in forwarding_interfaces:
            print(i.get_shortened_name())
            i.send(frame)

        print()

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

    def set_mac_address(self, mac):
        self.MAC_Address = mac

    def set_canvas_object(self, obj):
        self.canvas_object = obj

    def set_internal_clock(self, clock):
        self.internal_clock = clock

    def set_cam_table(self, cam):
        self.CAM_table = cam

    def get_cam_table(self):
        return self.CAM_table

    def update_cam_table_vid(self, interface, vid):
        for i in self.CAM_table:
            if self.CAM_table[i][3] == interface:
                self.CAM_table[i][1] = vid

    def add_vlan(self, vlan, interface=None):

        # Interface = None when being called from load_save.py
        if not interface:
            self.VLANS.append(vlan)

        else:
            exists = False
            for v in self.VLANS:
                if v.get_id() == vlan.get_id():
                    v.add_interface(interface)
                    exists = True
                    break

            if not exists:
                vlan.add_interface(interface)
                self.VLANS.append(vlan)

            globalVars.prompt_save = True

    def get_vlans(self):
        return self.VLANS

    # -------------------------- Save & Load Methods -------------------------- #
    def get_save_info(self):

        interfaces = []
        for interface in self.interfaces:
            interfaces.append(interface.get_save_info())

        vlans = []
        for vlan in self.VLANS:
            vlans.append(vlan.get_save_info())

        return [self.Host_Name, self.MAC_Address, self.save_cam_table(), interfaces, vlans]

    def save_cam_table(self):
        cam_table = {}
        for entry in self.CAM_table:
            cam_table[entry] = [self.CAM_table[entry][0], self.CAM_table[entry][1],
                                self.CAM_table[entry][2], self.CAM_table[entry][3].get_shortened_name(),
                                self.CAM_table[entry][4]]
        return cam_table

    def set_interfaces_on_load(self, interface):
        self.interfaces.append(interface)
    # -------------------------- Save & Load Methods -------------------------- #
