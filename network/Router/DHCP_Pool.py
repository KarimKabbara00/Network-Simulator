import UI.helper_functions as hf
class DHCPpool:

    def __init__(self, class_object, name):
        self.class_object = class_object
        self.pool_name = name

        self.ip_pool = []           # Available IPs
        self.leased_ip_pool = []    # Leased IPs
        self.offered_ips = []       # IPs waiting for DORA -> Request

        self.pool_subnet = None
        self.dns_servers = []
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
        self.dns_servers.append(dns_server)

    def set_domain_name(self, domain_name):
        self.domain_name = domain_name

    def set_default_router(self, default_router):
        self.default_gateway = default_router

    def set_lease(self, days, hours, minutes):
        self.lease_time = [days, hours, minutes]

    def get_name(self):
        return self.pool_name

    def get_pool(self):
        return self.ip_pool

    def get_ip_from_pool(self, ip):

        if ip and ip in self.ip_pool:
            ip_address = ip

        else:
            ip_address = next(iter(self.ip_pool))

        self.ip_pool.remove(ip_address)         # Remove from pool
        self.offered_ips.append(ip_address)     # Place it in limbo until Request is received.
        return ip_address

    def get_subnet(self):
        return self.pool_subnet

    def get_default_gateway(self):
        return self.default_gateway

    def get_dns_servers(self):
        return self.dns_servers

    def get_domain_name(self):
        return self.domain_name

    def get_lease_time(self):
        if all(i == 0 for i in self.lease_time):
            return None
        else:
            return hf.get_lease_time(self.lease_time)









