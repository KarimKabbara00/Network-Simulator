import UI.helper_functions as hf
import network.Router.DHCP_Pool
import network.network_functions as nf
from network.Application_Protocols import DHCP

option_50 = ["PREFERRED_IP", ""]
option_51 = "LEASE_TIME"
option_54 = "DHCP_IP_ADDRESS"

option_53_1 = "DHCP_DISCOVER"
option_53_2 = "DHCP_OFFER"
option_53_3 = "DHCP_REQUEST"
option_53_4 = "DHCP_DECLINE"
option_53_5 = "DHCP_ACK"
option_53_6 = "DHCP_NAK"
option_53_7 = "DHCP_RELEASE"
option_53_9 = "DHCP_FORCE_RENEW"

option_55_1 = "REQUEST_SUBNET_MASK"
option_55_3 = "REQUEST_ROUTER"
option_55_6 = "REQUEST_DNS_SERVER"
option_55_15 = "REQUEST_DOMAIN_NAME"


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
        working_dhcp_pool:network.Router.DHCP_Pool.DHCPpool = self.get_dhcp_pool_by_network_address(receiving_interface)
        flags = data.get_flags()
        options = data.get_options()

        # global option_50, option_55_1

        ci_address = None
        yi_address = None
        si_address = receiving_interface.get_ipv4_address()
        gi_address = None
        ch_address = source_mac
        transaction_id = data.get_transaction_id()

        subnet_mask = None
        default_gateway = None
        lease_time = None
        lease_time = working_dhcp_pool.get_lease_time()  # TODO: convert lease list to seconds
        dhcp_server_ip = None
        dns_servers = []
        domain_name = None

        for option in options:
            if option ==  option_50:
                if option_50[1]:
                    yi_address = working_dhcp_pool.get_ip_from_pool(option_50[1])
                else:
                    yi_address = working_dhcp_pool.get_ip_from_pool(None)

            elif option == option_55_1:
                subnet_mask = working_dhcp_pool.get_subnet()

            elif option == option_55_3:
                default_gateway = working_dhcp_pool.get_default_gateway()

            elif option == option_55_6:
                dns_servers = working_dhcp_pool.get_dns_servers()

            elif option == option_55_15:
                domain_name = working_dhcp_pool.get_domain_name()

        # TODO: May have to convert options to dictionaries, so that they contain the value associated with the option
        new_options = [option_53_2, subnet_mask, ]

        nf.create_dhcp_offer()






















