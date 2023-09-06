class InternalTime:

    def __init__(self):
        self.time = 0
        self.pcs = []
        self.switches = []
        self.routers = []

    def get_time(self):
        return self.time

    def set_time(self, t):
        self.time = t

    def increment_time(self):
        self.time += 1

    def add_pc(self, pc):
        self.pcs.append(pc)

    def remove_pc(self, pc):
        self.pcs.remove(pc)

    def get_pcs(self):
        return self.pcs

    def add_switch(self, switch):
        self.switches.append(switch)

    def remove_switch(self, switch):
        self.switches.remove(switch)

    def get_switches(self):
        return self.switches

    def add_router(self, router):
        self.routers.append(router)

    def remove_router(self, router):
        self.routers.remove(router)

    def get_routers(self):
        return self.routers
