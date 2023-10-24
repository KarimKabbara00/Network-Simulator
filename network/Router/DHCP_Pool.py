from datetime import datetime

import UI.helper_functions as hf
from operations import globalVars


class DHCPpool:

    def __init__(self, class_object, name):
        self.class_object = class_object
        self.pool_name = name

        self.ip_pool = []  # Available IPs
        self.leased_ip_pool = {}  # Leased IPs
        self.offered_ips = []  # IPs waiting for DORA -> Request
        self.unknown_ip_assignments = []  # If server receives a DECLINE due to ARP Request check

        self.example_ip = None  # Used to check for same subnet

        self.pool_subnet = None
        self.dns_servers = []
        self.domain_name = None
        self.default_gateway = None
        self.lease_time = [1, 0, 0]  # Days, Minutes, Seconds. Infinite = [0, 0, 0]

    def create_pool(self, ip, subnet, is_prefix):
        try:
            self.pool_subnet = hf.get_subnet_from_prefix_length(subnet)
        except ValueError:
            self.pool_subnet = subnet

        # Get IP Range
        self.ip_pool = hf.get_ip_range(ip, subnet, is_prefix)

        # Remove reserved network address
        self.ip_pool.pop(0)

        # Remove Excluded addresses
        excluded_addresses = self.class_object.get_dhcp_server().get_excluded_addresses()
        self.ip_pool = [ip for ip in self.ip_pool if ip not in excluded_addresses]

        # Used to check same subnet
        self.example_ip = self.ip_pool[0]

    def add_dns_server(self, dns_server):
        self.dns_servers.append(dns_server)

    def set_domain_name(self, domain_name):
        self.domain_name = domain_name

    def set_default_router(self, default_router):
        self.default_gateway = default_router

    def set_lease(self, days, hours, minutes):
        self.lease_time = [days, hours, minutes]

    def get_name(self):
        return self.pool_name

    def get_ip_pool(self):
        return self.ip_pool

    def get_ip_from_pool(self, ip):
        if ip and ip in self.ip_pool:
            ip_address = ip
            self.ip_pool.remove(ip_address)         # Remove from pool
        else:
            try:
                ip_address = self.ip_pool.pop(0)    # Remove from pool
            except IndexError:
                return None

        self.offered_ips.append(ip_address)     # Place it on hold until Request is received.

        return ip_address

    def remove_ip_from_hold(self, ip_address, assigned=True):
        if assigned:
            self.leased_ip_pool[ip_address] = globalVars.internal_clock.now()
        else:
            self.ip_pool.append(ip_address)

        self.offered_ips.remove(ip_address)

    def release_ip_assignment(self, ip):
        self.leased_ip_pool.pop(ip)
        self.ip_pool.append(ip)

    def unknown_ip_assignment(self, ip_address):
        self.unknown_ip_assignments.append(ip_address)
        self.offered_ips.remove(ip_address)
        # TODO: Syslog entry

    def get_subnet(self):
        return self.pool_subnet

    def get_default_gateway(self):
        return self.default_gateway

    def get_dns_servers(self):
        return self.dns_servers

    def get_domain_name(self):
        return self.domain_name

    def get_lease_time(self, as_list=False):
        if not as_list:
            if all(i == 0 for i in self.lease_time):
                return None
            else:
                return hf.get_lease_time(self.lease_time)
        else: # for saving
            return self.lease_time

    def get_leased_ip_pool(self):
        return self.leased_ip_pool

    def set_leased_ip_pool(self, leased_pool):
        for lease in leased_pool:
            self.leased_ip_pool[lease] = datetime.strptime(leased_pool[lease], '%A, %B %d, %Y %I:%M:%S %p')

    def get_example_ip(self):
        return self.example_ip

    def get_offered_ips(self):
        return self.offered_ips

    def get_unknown_ip_assignments(self):
        return self.unknown_ip_assignments

    def set_pool(self, pool):
        self.ip_pool = pool

    def set_offered_ips(self, offered_ips):
        self.offered_ips = offered_ips

    def set_unknown_assignments(self, unknown_ip_assignments):
        self.unknown_ip_assignments = unknown_ip_assignments

    def set_example_ip(self, ex_ip):
        self.example_ip = ex_ip

    def set_subnet(self, subnet):
        self.pool_subnet = subnet

    def set_dns_servers(self, dns_servers):
        self.dns_servers = dns_servers