import UI.helper_functions as hf
class DHCP:

    def __init__(self, class_object, name):
        self.class_object = class_object
        self.pool_name = name
        self.ip_pool = []
        self.pool_subnet = None
        self.dns_server = None
        self.domain_name = None
        self.default_gateway = None
        self.lease_time = [1, 0, 0]  # Days, Minutes, Seconds. Infinite = [0, 0, 0]

    def set_pool(self, ip, subnet, is_prefix):
        try:
            self.pool_subnet = hf.get_subnet_from_prefix_length(subnet)
        except ValueError:
            self.pool_subnet = subnet

        self.ip_pool = hf.get_ip_range(ip, subnet, is_prefix)

    def set_dns_server(self, dns_server):
        self.dns_server = dns_server
        print(self.dns_server)

    def set_domain_name(self, domain_name):
        self.domain_name = domain_name
        print(self.domain_name)

    def set_default_router(self, default_router):
        self.default_gateway = default_router
        print(self.default_gateway)

    def set_lease(self, days, hours, minutes):
        self.lease_time = [days, hours, minutes]

    def get_name(self):
        return self.pool_name
