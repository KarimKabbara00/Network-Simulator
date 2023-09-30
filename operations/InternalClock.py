from datetime import datetime, timedelta
import UI.helper_functions as hf

class InternalTime:

    def __init__(self):
        self.pcs = []
        self.switches = []
        self.routers = []
        self.start_date = datetime.today()

    @staticmethod
    def now(format_date=False):
        if format_date:
            return datetime.today().strftime('%A, %B %d, %Y %I:%M:%S %p')
        return datetime.now()

    @staticmethod
    def add_seconds_to_date(seconds, format_date=False):
        if format_date:
            return (datetime.now() + timedelta(seconds=seconds)).strftime('%A, %B %d, %Y %I:%M:%S %p')
        else:
            return datetime.now() + timedelta(seconds=seconds)

    def get_start_date(self):
        return self.start_date

    def set_start_date(self, t):
        self.start_date = hf.str_time_to_datetime(t)

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
