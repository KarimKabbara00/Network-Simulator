class VLAN:

    def __init__(self, v_id, name=''):
        self.name = name
        self.id = v_id
        self.status = 'Active'
        self.interfaces = []

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_id(self):
        return self.id

    def set_id(self, v_id):
        self.id = v_id

    def get_status(self):
        return self.status

    def set_status(self, status):
        self.status = status

    def get_interfaces(self):
        return self.interfaces

    def add_interface(self, interface):
        self.interfaces.append(interface)

    def get_save_info(self):
        return [self.name, self.id, self.status, [i.get_shortened_name() for i in self.interfaces]]
