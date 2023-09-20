from datetime import datetime, timedelta


class InternalTime:

    def __init__(self):
        self.time = 0
        self.pcs = []
        self.switches = []
        self.routers = []
        self.start_date = datetime.today().strftime('%A, %B %d, %Y %I:%M:%S %p')

    def get_time(self):
        return self.time

    def get_start_date(self):
        return self.start_date

    @staticmethod
    def get_current_date(format_date=False):
        if format_date:
            return datetime.today().strftime('%A, %B %d, %Y %I:%M:%S %p')
        return datetime.now()

    @staticmethod
    def add_seconds_to_date(seconds, format_date=False):
        if format_date:
            return (datetime.now() + timedelta(seconds=seconds)).strftime('%A, %B %d, %Y %I:%M:%S %p')
        else:
            return datetime.now() + timedelta(seconds=seconds)

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

    def clear_all(self):
        self.pcs = []
        self.switches = []
        self.routers = []
