import threading


class EthernetCable:

    def __init__(self):
        self.rj45_side_1 = None
        self.rj45_side_2 = None
        self.model = '1000BASE-T'
        self.canvas_object = None

    def connect(self, device_1, interface_1, device_2, interface_2):

        if self.rj45_side_1 is not None or self.rj45_side_2 is not None:
            raise Exception("Cable in Use")

        for i in device_1.get_interfaces():
            if i.__str__() == interface_1.__str__():

                # Check if the interface is already in use
                if i.get_is_connected():
                    raise Exception(device_1.get_host_name() + "'s interface in Use")

                i.set_is_connected(True)
                i.set_connected_to(device_2.get_host_name())
                i.set_cable(self)
                self.rj45_side_1 = i

        for i in device_2.get_interfaces():
            if i.__str__() == interface_2.__str__():

                # Check if the interface is already in use
                if i.get_is_connected():
                    raise Exception(device_2.get_host_name() + "'s interface in Use")

                i.set_is_connected(True)
                i.set_connected_to(device_1.get_host_name())
                i.set_cable(self)
                self.rj45_side_2 = i

        if not self.rj45_side_1 or not self.rj45_side_2:
            self.rj45_side_1 = None
            self.rj45_side_2 = None
            raise Exception("Error Connecting Devices")

    def send(self, source_interface, frame):
        if source_interface == self.rj45_side_1:
            self.rj45_side_2.get_host().de_encapsulate(frame, self.rj45_side_2)
        elif source_interface == self.rj45_side_2:
            self.rj45_side_1.get_host().de_encapsulate(frame, self.rj45_side_1)
        else:
            raise Exception("Interface Not Found")

    def set_canvas_object(self, obj):
        self.canvas_object = obj

    def get_rj45_side_1(self):
        return self.rj45_side_1

    def get_rj45_side_2(self):
        return self.rj45_side_2
