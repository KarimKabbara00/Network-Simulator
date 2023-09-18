import UI.helper_functions as hf
import network.Router.DHCP_Pool
import network.network_functions as nf
from network.Application_Protocols import DHCP
from network.Application_Protocols.DHCP import DhcpOffer


class DHCP_Server:
    def __init__(self, class_object):
        self.class_object = class_object
        self.dhcp_pools = []
        self.dhcp_excluded_ip_ranges = []

    def add_dhcp_pool(self, pool):
        for i in self.dhcp_pools:
            if pool.get_name() == i.get_name():
                return

        self.dhcp_pools.append(pool)

    def exclude_ip_range_from_dhcp_pools(self, start_ip, end_ip, is_range):
        if is_range:
            for ip in hf.get_ip_range_from_to(start_ip, end_ip):
                if ip not in self.dhcp_excluded_ip_ranges:
                    self.dhcp_excluded_ip_ranges.append(ip)
        else:
            if start_ip not in self.dhcp_excluded_ip_ranges:
                self.dhcp_excluded_ip_ranges.append(start_ip)

    def get_dhcp_pool_by_network_address(self, receiving_interface):

        receiving_interface_ip_address = receiving_interface.get_ipv4_address()
        receiving_interface_netmask = receiving_interface.get_netmask()

        for pool in self.dhcp_pools:
            try:
                if hf.is_same_subnet(receiving_interface_ip_address, receiving_interface_netmask, pool.get_pool()[0]):
                    return pool
            except IndexError:
                pass
            return None

    def create_offer(self, receiving_interface, data: DHCP.Dhcp, source_mac):

        working_dhcp_pool: network.Router.DHCP_Pool.DHCPpool = self.get_dhcp_pool_by_network_address(
            receiving_interface)

        flags = data.get_flags()
        options = data.get_options()

        ci_address = None
        yi_address, preferred = None, False
        si_address = receiving_interface.get_ipv4_address()
        gi_address = None
        ch_address = source_mac
        transaction_id = data.get_transaction_id()

        # ---------------------------- DHCP OPTIONS ---------------------------- #
        subnet_mask = None
        default_gateway = None
        lease_time = working_dhcp_pool.get_lease_time()
        dhcp_server_ip = receiving_interface.get_ipv4_address()
        dns_servers = []
        domain_name = None

        for option in options.items():
            if option == "PREFERRED_IP":
                if option["PREFERRED_IP"]:
                    yi_address = working_dhcp_pool.get_ip_from_pool(option["PREFERRED_IP"])
                    preferred = True
                else:
                    yi_address = working_dhcp_pool.get_ip_from_pool(None)

            elif option == "REQUEST_SUBNET_MASK":
                subnet_mask = working_dhcp_pool.get_subnet()

            elif option == "REQUEST_ROUTER":
                default_gateway = working_dhcp_pool.get_default_gateway()

            elif option == "REQUEST_DNS_SERVER":
                dns_servers = working_dhcp_pool.get_dns_servers()

            elif option == "REQUEST_DOMAIN_NAME":
                domain_name = working_dhcp_pool.get_domain_name()

        dhcp_options = DHCP.DHCP_options
        if preferred:
            dhcp_options['PREFERRED_IP'] = yi_address

        dhcp_options['DHCP_OFFER'] = True
        dhcp_options['REQUEST_SUBNET_MASK'] = subnet_mask
        dhcp_options['REQUEST_ROUTER'] = default_gateway
        dhcp_options['LEASE_TIME'] = lease_time
        dhcp_options['DHCP_IP_ADDRESS'] = dhcp_server_ip
        dhcp_options['REQUEST_DNS_SERVER'] = dns_servers
        dhcp_options['REQUEST_DOMAIN_NAME'] = domain_name
        # ---------------------------- DHCP OPTIONS ---------------------------- #

        nf.create_dhcp_offer(receiving_interface.get_ipv4_address(), source_mac, flags, ci_address, yi_address,
                             si_address, gi_address, ch_address, transaction_id, dhcp_options)
